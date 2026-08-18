#!/usr/bin/env python3
"""network/tests/test_hmi_historian.py — Unit tests for Phase 5 HMI Historian integration."""

import json
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path
from http.server import HTTPServer

from network.historian import HistorianTSDB
from network.hmi_server import IndustrialHmiEngine, HmiRequestHandler, ThreadedHmiServer


class TestHmiHistorianIntegration(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)
        self.historian = HistorianTSDB(db_path=self.db_path)

        # Seed sample time-series data
        self.now = time.time()
        self.historian.write(sector='water', field='t1_level', value=12.5, timestamp=self.now - 10)
        self.historian.write(sector='water', field='t2_level', value=18.0, timestamp=self.now - 5)
        self.historian.write(sector='gas', field='pressure_psi', value=142.3, timestamp=self.now - 2)

        self.engine = IndustrialHmiEngine(historian=self.historian)

    def tearDown(self) -> None:
        self.historian.close()
        if self.db_path.exists():
            try:
                self.db_path.unlink()
            except OSError:
                pass

    def test_engine_get_history(self) -> None:
        res_water = self.engine.get_history(sector='water')
        self.assertEqual(res_water['sector'], 'water')
        self.assertEqual(res_water['count'], 2)
        self.assertEqual(len(res_water['history']), 2)

        res_gas = self.engine.get_history(sector='gas', field='pressure_psi')
        self.assertEqual(res_gas['sector'], 'gas')
        self.assertEqual(res_gas['field'], 'pressure_psi')
        self.assertEqual(res_gas['count'], 1)
        self.assertAlmostEqual(res_gas['history'][0]['value'], 142.3)

    def test_hmi_server_api_history_endpoint(self) -> None:
        # Assign temporary engine to HmiRequestHandler
        HmiRequestHandler.engine = self.engine

        server = ThreadedHmiServer(('127.0.0.1', 0), HmiRequestHandler)
        port = server.server_address[1]

        import threading
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        try:
            url = f"http://127.0.0.1:{port}/api/history?sector=water"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode('utf-8'))
                self.assertEqual(data['sector'], 'water')
                self.assertEqual(data['count'], 2)
                self.assertEqual(len(data['history']), 2)

            url_hmi = f"http://127.0.0.1:{port}/api/hmi/history?sector=gas&field=pressure_psi"
            req_hmi = urllib.request.Request(url_hmi)
            with urllib.request.urlopen(req_hmi, timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                data_hmi = json.loads(resp.read().decode('utf-8'))
                self.assertEqual(data_hmi['sector'], 'gas')
                self.assertEqual(data_hmi['field'], 'pressure_psi')
                self.assertEqual(data_hmi['count'], 1)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
