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


if __name__ == '__main__':
    unittest.main()
