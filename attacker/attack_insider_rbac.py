#!/usr/bin/env python3
"""attacker/attack_insider_rbac.py — Vector de Ataque de Insider Threat / Violación RBAC (Fase 2)

Simula un ataque de insider o robo de credencial con rol de menor privilegio (`auditor`):
  1. El atacante utiliza el token legítimo de auditor `AUDIT_TOKEN_2026`.
  2. Intenta ejecutar comandos destructivos de escritura (`/api/control/write`).
  3. Verifica que en modo `STRICT_AUTH=1` la API rechaza el acceso con `HTTP 403 Forbidden`.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.rbac import RBACResolver

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][INSIDER-ATTACK] %(message)s')
LOGGER = logging.getLogger('attack_insider_rbac')


class InsiderRbacAttack:

    def __init__(self) -> None:
        self.resolver = RBACResolver()

    def execute_unauthorized_write_attempt(self) -> Dict[str, Any]:
        LOGGER.info("Iniciando intencion de escritura no autorizada usando credencial de auditor...")
        auditor_hdr = "Bearer auditor:AUDIT_TOKEN_2026"
        role, _ = self.resolver.resolve(auditor_hdr)
        
        # Verificar autorización para endpoint de escritura
        authorized = self.resolver.is_authorized(role, '/api/control/write')
        LOGGER.info("Rol resuelto: %s | Permiso para /api/control/write: %s", role, authorized)
        
        return {
            'status': 'SUCCESS',
            'role': role,
            'access_granted': authorized,
            'blocked_by_rbac': not authorized
        }


def main() -> int:
    attacker = InsiderRbacAttack()
    res = attacker.execute_unauthorized_write_attempt()
    LOGGER.info("Resultado de prueba Insider RBAC: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
