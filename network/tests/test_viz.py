#!/usr/bin/env python3
"""network/tests/test_viz.py — Pruebas unitarias para Visualizador 2D/3D (Fase 9)"""
from __future__ import annotations

import json
import threading
import urllib.request
import unittest
from network.viz_server import CityVisualizerStateEngine, VizRequestHandler, ThreadedVizServer


class TestCityVisualizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadedVizServer(('127.0.0.1', 18090), VizRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def test_state_engine_updates(self) -> None:
        engine = CityVisualizerStateEngine()
        frame1 = engine.get_render_frame()
        self.assertIn('city_sectors', frame1)
        
        engine.update_sector_state('water', {'tank_level': 18.5})
        frame2 = engine.get_render_frame()
        self.assertEqual(frame2['city_sectors']['water']['tank_level'], 18.5)

    def test_viz_frame_endpoint(self) -> None:
        url = 'http://127.0.0.1:18090/api/viz/frame'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode('utf-8'))
            self.assertIn('city_sectors', data)

    def test_viz_html_rendering(self) -> None:
        url = 'http://127.0.0.1:18090/'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            content = resp.read().decode('utf-8')
            self.assertIn('CityLab 2D/3D Presentational Visualizer', content)


if __name__ == '__main__':
    unittest.main()
