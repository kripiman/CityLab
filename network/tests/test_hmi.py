#!/usr/bin/env python3
"""network/tests/test_hmi.py — Pruebas unitarias para HMI Industrial (Fase 5)"""
from __future__ import annotations

import json
import threading
import urllib.request
import unittest
from network.hmi_server import IndustrialHmiEngine, HmiRequestHandler, ThreadedHmiServer, DEFAULT_HMI_PORT


class TestHmiServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadedHmiServer(('127.0.0.1', 18085), HmiRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def test_hmi_overview_endpoint(self) -> None:
        url = 'http://127.0.0.1:18085/api/hmi/overview'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode('utf-8'))
            self.assertIn('hmi_brand', data)
            self.assertIn('process_diagram', data)
            self.assertIn('water_sector', data['process_diagram'])

    def test_hmi_alarms_endpoint(self) -> None:
        url = 'http://127.0.0.1:18085/api/hmi/alarms'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode('utf-8'))
            self.assertIn('alarms', data)

    def test_hmi_html_rendering(self) -> None:
        url = 'http://127.0.0.1:18085/'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            content = resp.read().decode('utf-8')
            self.assertIn('CityLab Industrial HMI', content)

    def test_hmi_control_action_with_auth(self) -> None:
        engine = IndustrialHmiEngine(scada_url='http://127.0.0.1:18080', auth_token='ENG_TOKEN_2026')
        self.assertEqual(engine.auth_token, 'engineer:ENG_TOKEN_2026')
        # Control action against offline endpoint returns structured error without exception
        res = engine.trigger_control_action(action='TRIP', target='water')
        self.assertFalse(res['success'])
        self.assertIn('error', res)

    def test_hmi_with_live_scada_strict_auth_integration(self) -> None:
        """Verifica que IndustrialHmiEngine y HmiRequestHandler autentiquen exitosamente con SCADA en STRICT_AUTH=1."""
        import os
        from http.server import HTTPServer
        from network.scada_server import SCADAAPIHandler, scada_state
        import network.rbac as rbac_mod

        old_strict = os.environ.get('STRICT_AUTH')
        os.environ['STRICT_AUTH'] = '1'
        rbac_mod._rbac.reload()

        scada_server = HTTPServer(('127.0.0.1', 0), SCADAAPIHandler)
        scada_port = scada_server.server_address[1]
        scada_thread = threading.Thread(target=scada_server.serve_forever, daemon=True)
        scada_thread.start()

        try:
            scada_url = f"http://127.0.0.1:{scada_port}"
            engine = IndustrialHmiEngine(scada_url=scada_url, auth_token='ENG_TOKEN_2026')
            
            # 1. Telemetry query succeeds under STRICT_AUTH=1
            status = engine.fetch_scada_status()
            self.assertNotEqual(status.get('status'), 'OFFLINE')
            self.assertIn('sectors', status)

            # 2. Control action POST succeeds with role 'engineer' under STRICT_AUTH=1
            res = engine.trigger_control_action(action='START', target='water', role_token='ENG_TOKEN_2026')
            self.assertTrue(res.get('success'))
            self.assertEqual(res['scada_response']['status'], 'SUCCESS')
            self.assertEqual(res['scada_response']['role'], 'engineer')
        finally:
            scada_server.shutdown()
            scada_server.server_close()
            if old_strict is None:
                os.environ.pop('STRICT_AUTH', None)
            else:
                os.environ['STRICT_AUTH'] = old_strict
            rbac_mod._rbac.reload()


if __name__ == '__main__':
    unittest.main()
