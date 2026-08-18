#!/usr/bin/env python3
"""network/tests/test_viz_server.py — Unit tests for Phase 9 presentational visualizer server."""

import json
import threading
import unittest
import urllib.request
import urllib.error

from network.viz_server import CityVisualizerStateEngine, VizRequestHandler, ThreadedVizServer


class TestVizServer(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = CityVisualizerStateEngine()

    def test_engine_state_update_and_history(self) -> None:
        initial = self.engine.get_render_frame()
        self.assertEqual(initial['city_sectors']['water']['tank_level'], 10.0)

        self.engine.update_sector_state('water', {'tank_level': 18.5, 'alert': True})
        updated = self.engine.get_render_frame()
        self.assertEqual(updated['city_sectors']['water']['tank_level'], 18.5)
        self.assertTrue(updated['city_sectors']['water']['alert'])

        history = self.engine.get_history_frames()
        self.assertEqual(len(history), 1)

    def test_viz_server_http_endpoints(self) -> None:
        VizRequestHandler.engine = self.engine
        server = ThreadedVizServer(('127.0.0.1', 0), VizRequestHandler)
        port = server.server_address[1]

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        try:
            # 1. GET /api/viz/frame
            req_frame = urllib.request.Request(f"http://127.0.0.1:{port}/api/viz/frame")
            with urllib.request.urlopen(req_frame, timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                frame = json.loads(resp.read().decode('utf-8'))
                self.assertIn('city_sectors', frame)

            # 2. POST /api/viz/update
            payload = json.dumps({'sector': 'elec', 'payload': {'grid_voltage': 0.0, 'blackout': True}}).encode('utf-8')
            req_update = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/viz/update",
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req_update, timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                update_res = json.loads(resp.read().decode('utf-8'))
                self.assertEqual(update_res['status'], 'UPDATED')

            # 3. GET /api/viz/history
            req_hist = urllib.request.Request(f"http://127.0.0.1:{port}/api/viz/history")
            with urllib.request.urlopen(req_hist, timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                hist = json.loads(resp.read().decode('utf-8'))
                self.assertIn('frames', hist)
                self.assertGreaterEqual(len(hist['frames']), 1)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
