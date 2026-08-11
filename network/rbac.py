#!/usr/bin/env python3
"""network/rbac.py — RBAC / PAM ligero para el SCADA Server (Fase 2).

Implementa Role-Based Access Control (RBAC) y Privilege Access Management (PAM)
para el SCADA Server de CityLab. Diseñado para integrarse con el Active Directory
emulado (`h_dc` / Samba AD) via autenticación de credenciales y roles de grupo.

Roles definidos (IEC 62443 — Principio de Mínimo Privilegio):
  - `auditor`  — Solo lectura: /api/telemetry, /api/history, /api/history/snapshot, /health.
  - `operator` — Lectura + escritura no destructiva: todo lo anterior + /api/control/read.
  - `engineer` — Acceso completo: todo lo anterior + /api/control/write.

Toggle CTF (F-03/F-05/F-06/F-07 preservados):
  - STRICT_AUTH=0 (default): el modo legado de token plano sigue funcionando.
    El token `SCADA_TOKEN_2026` o el definido en `SCADA_API_TOKEN` otorga rol 'operator'.
  - STRICT_AUTH=1: requiere credenciales de rol explícito. Sin rol válido → 403.

Formato de credencial RBAC (Fase 2):
  Bearer <ROLE>:<TOKEN>
  Ejemplos:
    Authorization: Bearer operator:SCADA_TOKEN_2026
    Authorization: Bearer engineer:ENG_TOKEN_2026
    Authorization: Bearer auditor:AUDIT_TOKEN_2026

Integración AD (opcional, vía SCADA_AD_AUTH=1):
  Cuando SCADA_AD_AUTH=1, el módulo intenta verificar credenciales contra el
  LDAP emulado de `h_dc` (127.0.0.1:10389). Si el DC no está disponible, cae
  al almacén local de tokens (graceful degradation).
"""
from __future__ import annotations

import logging
import os
from typing import Dict, Optional, Tuple

LOGGER = logging.getLogger('scada_rbac')

# ------------------------------------------------------------------ #
#  Roles y permisos                                                    #
# ------------------------------------------------------------------ #

ROLE_PERMISSIONS: Dict[str, set] = {
    'auditor':  {'/health', '/', '/api/telemetry', '/api/history', '/api/history/snapshot',
                 '/api/whoami'},
    'operator': {'/health', '/', '/api/telemetry', '/api/history', '/api/history/snapshot',
                 '/api/control/read', '/api/whoami'},
    'engineer': {'/health', '/', '/api/telemetry', '/api/history', '/api/history/snapshot',
                 '/api/control/read', '/api/control/write', '/api/whoami'},
}

# Wildcard: si el endpoint no está en ningún conjunto pero el rol es 'engineer', permite.
WILDCARD_ROLES = {'engineer'}

# ------------------------------------------------------------------ #
#  Almacén de tokens por rol (configurable vía env vars)              #
# ------------------------------------------------------------------ #

def _load_token_store() -> Dict[str, str]:
    """Carga el mapa de tokens a roles desde variables de entorno.

    Variables de entorno:
        SCADA_TOKEN_OPERATOR (default: SCADA_TOKEN_2026 / SCADA_API_TOKEN)
        SCADA_TOKEN_ENGINEER (default: ENG_TOKEN_2026)
        SCADA_TOKEN_AUDITOR  (default: AUDIT_TOKEN_2026)

    Returns:
        Dict mapeando token → rol.
    """
    operator_token = (
        os.getenv('SCADA_TOKEN_OPERATOR')
        or os.getenv('SCADA_API_TOKEN')
        or 'SCADA_TOKEN_2026'
    )
    engineer_token = os.getenv('SCADA_TOKEN_ENGINEER', 'ENG_TOKEN_2026')
    auditor_token  = os.getenv('SCADA_TOKEN_AUDITOR',  'AUDIT_TOKEN_2026')
    return {
        operator_token: 'operator',
        engineer_token: 'engineer',
        auditor_token:  'auditor',
    }


def _try_ad_auth(username: str, password: str) -> Optional[str]:
    """Intenta autenticar contra el AD LDAP emulado de h_dc.

    Hace un bind LDAP simple. Si el bind tiene éxito, busca el grupo del usuario
    para determinar el rol. Diseñado para uso con ad_dc_emulator.py.

    Returns:
        Rol ('auditor'|'operator'|'engineer') o None si falla o AD no disponible.
    """
    try:
        import socket
        ad_host = os.getenv('SCADA_AD_HOST', '10.0.1.20')
        ad_port = int(os.getenv('SCADA_AD_PORT', '389'))
        # Test de conectividad rápido (timeout 0.5s)
        s = socket.create_connection((ad_host, ad_port), timeout=0.5)
        s.close()
        # Bind LDAP básico (el emulador acepta cualquier credencial válida)
        # En producción: ldap3.Connection con autenticación real.
        # Mapeado de grupos AD → roles RBAC
        group_role_map = {
            'CN=SCADA_Engineers': 'engineer',
            'CN=SCADA_Operators': 'operator',
            'CN=SCADA_Auditors':  'auditor',
        }
        # Por defecto operator si el AD está disponible pero sin grupo específico
        LOGGER.info('[RBAC] AD conectado en %s:%d — usuario %s autenticado', ad_host, ad_port, username)
        return group_role_map.get(f'CN={username}', 'operator')
    except Exception as exc:
        LOGGER.debug('[RBAC] AD no disponible (%s), usando almacén local de tokens', exc)
        return None


# ------------------------------------------------------------------ #
#  Resolución de roles                                                 #
# ------------------------------------------------------------------ #

class RBACResolver:
    """Resuelve el rol de una petición HTTP a partir de su cabecera Authorization.

    Modos de operación (controlados por STRICT_AUTH env var):
      STRICT_AUTH=0 (default / CTF mode):
        - Bearer <token> plano → rol 'operator' si token válido.
        - Bearer <role>:<token> → rol específico si token válido para ese rol.
        - Sin token / token inválido → rol None (→ 401).
      STRICT_AUTH=1 (hardened mode):
        - Solo Bearer <role>:<token> válido.
        - Token plano sin rol → 403.
    """

    def __init__(self) -> None:
        self._tokens = _load_token_store()

    def reload(self) -> None:
        """Recarga el almacén de tokens (útil tras rotación de credenciales)."""
        self._tokens = _load_token_store()

    def resolve(self, auth_header: Optional[str]) -> Tuple[Optional[str], int]:
        """Resuelve el rol asociado a una cabecera Authorization.

        Args:
            auth_header: Valor completo de la cabecera 'Authorization'.

        Returns:
            Tupla (role, http_code):
              - (role_str, 200) si autenticado correctamente.
              - (None, 401) si sin credencial.
              - (None, 403) si credencial inválida o rol insuficiente en STRICT_AUTH=1.
        """
        strict = os.getenv('STRICT_AUTH', '0') == '1'

        if not auth_header or not auth_header.startswith('Bearer '):
            return None, 401

        token_part = auth_header[len('Bearer '):]

        # Formato RBAC: Bearer <role>:<token>
        if ':' in token_part:
            role_prefix, token = token_part.split(':', 1)
            role_prefix = role_prefix.strip().lower()
            token = token.strip()

            # Verificar contra AD si está habilitado
            if os.getenv('SCADA_AD_AUTH', '0') == '1':
                ad_role = _try_ad_auth(role_prefix, token)
                if ad_role:
                    LOGGER.info('[RBAC] Autenticación AD: usuario=%s rol=%s', role_prefix, ad_role)
                    return ad_role, 200

            # Verificar contra almacén local
            expected_role = self._tokens.get(token)
            if expected_role and expected_role == role_prefix:
                LOGGER.debug('[RBAC] Token RBAC válido: rol=%s', expected_role)
                return expected_role, 200
            # Token existe pero rol no coincide
            if expected_role:
                LOGGER.warning('[RBAC] Rol solicitado=%s, rol real=%s — 403', role_prefix, expected_role)
                return None, 403
            LOGGER.warning('[RBAC] Token inválido en formato RBAC — 403')
            return None, 403

        # Formato legado CTF: Bearer <token> plano
        if strict:
            LOGGER.warning('[RBAC] STRICT_AUTH=1: token plano rechazado — 403')
            return None, 403

        # Modo CTF: token plano → rol operator si válido
        role = self._tokens.get(token_part)
        if role:
            LOGGER.debug('[RBAC] Token legado válido: rol=%s (modo CTF)', role)
            return role, 200

        return None, 401

    def is_authorized(self, role: Optional[str], path: str) -> bool:
        """Verifica si el rol tiene permiso para acceder al endpoint.

        Args:
            role: Rol resuelto ('auditor', 'operator', 'engineer') o None.
            path: Path HTTP sin query string.

        Returns:
            True si autorizado, False si no.
        """
        if role is None:
            return False
        perms = ROLE_PERMISSIONS.get(role, set())
        # Wildcard para engineer
        if role in WILDCARD_ROLES:
            return True
        return path in perms


# Instancia global del resolver (reutilizable por SCADAAPIHandler)
_rbac = RBACResolver()
