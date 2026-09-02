#!/usr/bin/env python3
"""network/tests/test_scada_http_strict_integration.py

Test de integración HTTP real para SCADA Server bajo STRICT_AUTH=1 (Fase 5).
Valida el ciclo de vida completo de peticiones HTTP, RBAC y control de acceso:
- 401 Unauthorized cuando falta credencial.
- 403 Forbidden cuando se usa token plano en modo estricto.
- 403 Forbidden cuando el rol es insuficiente ('operator' intentando control/write).
- 200 OK cuando el rol es 'engineer' con credencial RBAC válida.
- Restauración estricta de variables de entorno en tearDown (Defecto #3).
"""
from __future__ import annotations

import json
import os
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer

from network.scada_server import SCADAAPIHandler


class TestScadaHttpStrictIntegration(unittest.TestCase):

    def setUp(self) -> None:
        self._orig_strict_auth = os.environ.get('STRICT_AUTH')
        os.environ['STRICT_AUTH'] = '1'

        # Levantar HTTPServer en un puerto dinámico efímero del kernel (puerto 0)
        self.server = HTTPServer(('127.0.0.1', 0), SCADAAPIHandler)
        self.host, self.port = self.server.server_address
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

    def tearDown(self) -> None:
        # Apagar servidor HTTP y liberar sockets
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join(timeout=2.0)

        # Restauración obligatoria de variables de entorno para evitar contaminación cruzada
        if self._orig_strict_auth is None:
            os.environ.pop('STRICT_AUTH', None)
        else:
            os.environ['STRICT_AUTH'] = self._orig_strict_auth

    def _http_request(
        self,
        path: str,
        method: str = 'GET',
        headers: dict[str, str] | None = None,
        data: dict | None = None
    ) -> tuple[int, dict, dict]:
        url = f"http://{self.host}:{self.port}{path}"
        req_headers = headers or {}
        req_data = json.dumps(data).encode('utf-8') if data is not None else None

        req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.status
                body = resp.read().decode('utf-8')
                resp_headers = dict(resp.headers)
                return status, json.loads(body) if body else {}, resp_headers
        except urllib.error.HTTPError as err:
            body = err.read().decode('utf-8')
            resp_headers = dict(err.headers)
            try:
                parsed_body = json.loads(body) if body else {}
            except Exception:
                parsed_body = {'raw': body}
            return err.code, parsed_body, resp_headers

    def test_unauthenticated_request_returns_401(self) -> None:
        """Petición POST a /api/control/write sin header Authorization debe retornar 401."""
        status, body, _ = self._http_request(
            '/api/control/write',
            method='POST',
            data={'action': 'trip', 'target': 'sector_water'}
        )
        self.assertEqual(status, 401)
        self.assertEqual(body.get('error'), 'unauthorized')
        self.assertEqual(body.get('code'), 401)

    def test_flat_token_under_strict_auth_returns_403(self) -> None:
        """En STRICT_AUTH=1, un token legado plano sin prefijo de rol debe ser rechazado con 403."""
        status, body, _ = self._http_request(
            '/api/control/write',
            method='POST',
            headers={'Authorization': 'Bearer SCADA_TOKEN_2026', 'Content-Type': 'application/json'},
            data={'action': 'trip', 'target': 'sector_water'}
        )
        self.assertEqual(status, 403)
        self.assertEqual(body.get('error'), 'unauthorized')
        self.assertEqual(body.get('code'), 403)

    def test_operator_role_forbidden_on_control_write_returns_403(self) -> None:
        """Rol operator autenticado válidamente no tiene permiso para escribir control -> 403."""
        status, body, _ = self._http_request(
            '/api/control/write',
            method='POST',
            headers={'Authorization': 'Bearer operator:SCADA_TOKEN_2026', 'Content-Type': 'application/json'},
            data={'action': 'trip', 'target': 'sector_elec'}
        )
        self.assertEqual(status, 403)
        self.assertEqual(body.get('error'), 'forbidden')
        self.assertEqual(body.get('role'), 'operator')

    def test_engineer_role_allowed_on_control_write_returns_200(self) -> None:
        """Rol engineer autenticado tiene permiso para control/write -> 200 y confirmación."""
        status, body, resp_headers = self._http_request(
            '/api/control/write',
            method='POST',
            headers={'Authorization': 'Bearer engineer:ENG_TOKEN_2026', 'Content-Type': 'application/json'},
            data={'action': 'emergency_shutdown', 'target': 'sector_power'}
        )
        self.assertEqual(status, 200)
        self.assertEqual(body.get('status'), 'SUCCESS')
        self.assertEqual(body.get('role'), 'engineer')
        self.assertEqual(body.get('action_executed'), 'emergency_shutdown')
        self.assertEqual(body.get('target'), 'sector_power')
        self.assertEqual(resp_headers.get('X-SCADA-Role'), 'engineer')

    def test_whoami_endpoint_under_strict_auth(self) -> None:
        """Endpoint /api/whoami confirma identidad y bandera strict_auth."""
        status, body, _ = self._http_request(
            '/api/whoami',
            method='GET',
            headers={'Authorization': 'Bearer engineer:ENG_TOKEN_2026'}
        )
        self.assertEqual(status, 200)
        self.assertEqual(body.get('role'), 'engineer')
        self.assertTrue(body.get('strict_auth'))


if __name__ == '__main__':
    unittest.main()
