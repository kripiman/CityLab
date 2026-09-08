#!/usr/bin/env python3
"""Tests de integración para el módulo RBAC / PAM del SCADA Server — Fase 2.

Valida:
  - Resolución de roles desde token plano (modo CTF, STRICT_AUTH=0).
  - Resolución de roles desde token RBAC (Bearer <role>:<token>).
  - Rechazo con 401 sin token.
  - Rechazo con 403 en STRICT_AUTH=1 con token plano.
  - Verificación de permisos por rol y endpoint.
  - Endpoints HTTP /api/whoami y cabecera X-SCADA-Role.
  - Toggle STRICT_AUTH sin romper compatibilidad CTF.
"""
from __future__ import annotations

import json
import os
import threading
import time
import unittest
import urllib.request
import urllib.error
from http.server import HTTPServer
from unittest.mock import patch

from network.rbac import RBACResolver, ROLE_PERMISSIONS
from network.scada_server import SCADAAPIHandler


class TestRBACResolver(unittest.TestCase):
    """Tests unitarios del RBACResolver (network/rbac.py)."""

    def setUp(self) -> None:
        # Guarda env original y configura tokens deterministas para este test
        self._orig_env = {
            k: os.environ.get(k)
            for k in ('SCADA_API_TOKEN', 'SCADA_TOKEN_OPERATOR', 'SCADA_TOKEN_ENGINEER',
                      'SCADA_TOKEN_AUDITOR', 'STRICT_AUTH', 'SCADA_AD_AUTH')
        }
        os.environ['SCADA_API_TOKEN']      = 'SCADA_TOKEN_2026'
        os.environ['SCADA_TOKEN_OPERATOR'] = 'SCADA_TOKEN_2026'
        os.environ['SCADA_TOKEN_ENGINEER'] = 'ENG_TOKEN_2026'
        os.environ['SCADA_TOKEN_AUDITOR']  = 'AUDIT_TOKEN_2026'
        os.environ['STRICT_AUTH'] = '0'
        os.environ['SCADA_AD_AUTH'] = '0'
        self.rbac = RBACResolver()  # Instancia fresca con el env actual

    def tearDown(self) -> None:
        # Restaura env original
        for k, v in self._orig_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_legacy_token_resolves_operator_in_ctf_mode(self) -> None:
        """Bearer <token> plano → rol operator en STRICT_AUTH=0 (modo CTF)."""
        role, code = self.rbac.resolve('Bearer SCADA_TOKEN_2026')
        self.assertEqual(code, 200)
        self.assertEqual(role, 'operator')

    def test_rbac_format_operator_token(self) -> None:
        """Bearer operator:<token> → rol operator."""
        role, code = self.rbac.resolve('Bearer operator:SCADA_TOKEN_2026')
        self.assertEqual(code, 200)
        self.assertEqual(role, 'operator')

    def test_rbac_format_engineer_token(self) -> None:
        """Bearer engineer:<token> → rol engineer."""
        role, code = self.rbac.resolve('Bearer engineer:ENG_TOKEN_2026')
        self.assertEqual(code, 200)
        self.assertEqual(role, 'engineer')

    def test_rbac_format_auditor_token(self) -> None:
        """Bearer auditor:<token> → rol auditor."""
        role, code = self.rbac.resolve('Bearer auditor:AUDIT_TOKEN_2026')
        self.assertEqual(code, 200)
        self.assertEqual(role, 'auditor')

    def test_no_auth_header_returns_401(self) -> None:
        """Sin Authorization header → 401."""
        role, code = self.rbac.resolve(None)
        self.assertIsNone(role)
        self.assertEqual(code, 401)

    def test_invalid_token_returns_401(self) -> None:
        """Token inválido → 401 en modo CTF."""
        role, code = self.rbac.resolve('Bearer INVALID_TOKEN')
        self.assertIsNone(role)
        self.assertEqual(code, 401)

    def test_plain_token_rejected_in_strict_mode(self) -> None:
        """Bearer <token> plano → 403 en STRICT_AUTH=1."""
        os.environ['STRICT_AUTH'] = '1'
        try:
            role, code = self.rbac.resolve('Bearer SCADA_TOKEN_2026')
            self.assertIsNone(role)
            self.assertEqual(code, 403)
        finally:
            os.environ['STRICT_AUTH'] = '0'

    def test_wrong_role_prefix_returns_403(self) -> None:
        """Bearer auditor:<operator_token> → 403 (rol incorrecto para token)."""
        role, code = self.rbac.resolve('Bearer auditor:SCADA_TOKEN_2026')
        self.assertIsNone(role)
        self.assertEqual(code, 403)

    def test_is_authorized_auditor_read_only(self) -> None:
        """Rol auditor puede leer telemetría pero no /api/control/write."""
        self.assertTrue(self.rbac.is_authorized('auditor', '/api/telemetry'))
        self.assertTrue(self.rbac.is_authorized('auditor', '/api/history'))
        self.assertFalse(self.rbac.is_authorized('auditor', '/api/control/write'))

    def test_is_authorized_operator_control_read(self) -> None:
        """Rol operator puede acceder a /api/control/read pero no /api/control/write."""
        self.assertTrue(self.rbac.is_authorized('operator', '/api/control/read'))
        self.assertFalse(self.rbac.is_authorized('operator', '/api/control/write'))

    def test_is_authorized_engineer_full_access(self) -> None:
        """Rol engineer tiene acceso completo (wildcard)."""
        self.assertTrue(self.rbac.is_authorized('engineer', '/api/control/write'))
        self.assertTrue(self.rbac.is_authorized('engineer', '/api/any/endpoint'))

    def test_is_authorized_none_role_returns_false(self) -> None:
        """Rol None (no autenticado) → siempre False."""
        self.assertFalse(self.rbac.is_authorized(None, '/api/telemetry'))

    def test_reload_picks_up_new_tokens(self) -> None:
        """reload() recarga almacén de tokens con cambios de env var."""
        os.environ['SCADA_TOKEN_OPERATOR'] = 'NEW_TOKEN_XYZ'
        self.rbac.reload()
        role, code = self.rbac.resolve('Bearer operator:NEW_TOKEN_XYZ')
        self.assertEqual(code, 200)
        self.assertEqual(role, 'operator')


class TestScadaRBACHTTPEndpoints(unittest.TestCase):
    """Tests de integración HTTP para RBAC en scada_server."""

    _server_port = 18082

    @classmethod
    def setUpClass(cls) -> None:
        cls._orig_env = {
            k: os.environ.get(k)
            for k in ('SCADA_API_TOKEN', 'SCADA_TOKEN_OPERATOR', 'SCADA_TOKEN_ENGINEER',
                      'SCADA_TOKEN_AUDITOR', 'STRICT_AUTH', 'SCADA_AD_AUTH')
        }
        os.environ['SCADA_API_TOKEN']      = 'SCADA_TOKEN_2026'
        os.environ['SCADA_TOKEN_OPERATOR'] = 'SCADA_TOKEN_2026'
        os.environ['SCADA_TOKEN_ENGINEER'] = 'ENG_TOKEN_2026'
        os.environ['SCADA_TOKEN_AUDITOR']  = 'AUDIT_TOKEN_2026'
        os.environ['STRICT_AUTH'] = '0'
        os.environ['SCADA_AD_AUTH'] = '0'

        # Recargar resolver con tokens de test
        import network.rbac as rbac_mod
        rbac_mod._rbac.reload()

        cls._server = HTTPServer(('127.0.0.1', cls._server_port), SCADAAPIHandler)
        cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
        cls._thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._server.shutdown()
        cls._server.server_close()
        import network.rbac as rbac_mod
        for k, v in cls._orig_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        rbac_mod._rbac.reload()

    def _get(self, path: str, auth: str = 'Bearer SCADA_TOKEN_2026') -> tuple[int, dict | str]:
        url = f'http://127.0.0.1:{self._server_port}{path}'
        req = urllib.request.Request(url, headers={'Authorization': auth})
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                body = resp.read().decode()
                try:
                    return resp.status, json.loads(body)
                except json.JSONDecodeError:
                    return resp.status, body
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ''
            try:
                return e.code, json.loads(body)
            except Exception:
                return e.code, {}

    def test_health_no_auth_required(self) -> None:
        """/health responde 200 sin Authorization."""
        url = f'http://127.0.0.1:{self._server_port}/health'
        with urllib.request.urlopen(url, timeout=3) as resp:
            self.assertEqual(resp.status, 200)

    def test_telemetry_with_valid_token(self) -> None:
        """/api/telemetry con token válido → 200."""
        status, body = self._get('/api/telemetry')
        self.assertEqual(status, 200)
        self.assertIn('sectors', body)

    def test_telemetry_without_token_returns_401(self) -> None:
        """/api/telemetry sin token → 401."""
        status, _ = self._get('/api/telemetry', auth='')
        self.assertEqual(status, 401)

    def test_whoami_returns_role(self) -> None:
        """/api/whoami retorna el rol del token presentado."""
        status, body = self._get('/api/whoami', auth='Bearer auditor:AUDIT_TOKEN_2026')
        self.assertEqual(status, 200)
        self.assertEqual(body.get('role'), 'auditor')

    def test_whoami_operator_via_legacy_token(self) -> None:
        """/api/whoami con token legado → rol operator (modo CTF)."""
        status, body = self._get('/api/whoami')
        self.assertEqual(status, 200)
        self.assertEqual(body.get('role'), 'operator')

    def test_strict_auth_rejects_plain_token(self) -> None:
        """STRICT_AUTH=1 rechaza token plano legado con 403."""
        os.environ['STRICT_AUTH'] = '1'
        import network.rbac as rbac_mod
        rbac_mod._rbac.reload()
        try:
            status, body = self._get('/api/whoami', auth='Bearer SCADA_TOKEN_2026')
            self.assertEqual(status, 403)
        finally:
            os.environ['STRICT_AUTH'] = '0'
            rbac_mod._rbac.reload()

    def test_auditor_cannot_access_control_write(self) -> None:
        """Auditor recibe 403 en /api/control/write."""
        status, body = self._get('/api/control/write', auth='Bearer auditor:AUDIT_TOKEN_2026')
        self.assertEqual(status, 403)


if __name__ == '__main__':
    unittest.main()
