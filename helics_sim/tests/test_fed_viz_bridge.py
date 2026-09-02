#!/usr/bin/env python3
"""helics_sim/tests/test_fed_viz_bridge.py — Pruebas unitarias para fed_viz_bridge (Fase 9)."""
from __future__ import annotations

import json
import threading
import time
import unittest
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

from helics_sim.fed_viz_bridge import (
    VizBridgeEngine,
    format_bearer_header,
    poll_scada_once,
)
from network.viz_server import CityVisualizerStateEngine, ThreadedVizServer, VizRequestHandler


class MockScadaHandler(BaseHTTPRequestHandler):
    """Servidor mock para verificar autenticación RBAC Bearer en fallback SCADA."""

    received_auth: str = ""

    def do_GET(self) -> None:
        MockScadaHandler.received_auth = self.headers.get("Authorization", "")
        if self.path == "/api/telemetry":
            if "Bearer auditor:AUDIT_TOKEN_2026" in MockScadaHandler.received_auth:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                payload = {
                    "last_update": time.time(),
                    "sectors": {
                        "water": {"status": "ONLINE", "actuator_running": True, "fault": False, "coils": [True, False, True, False]},
                        "gas": {"status": "ONLINE", "actuator_running": True, "fault": False, "coils": [True, False, True, False]},
                        "elec": {"status": "ONLINE", "actuator_running": True, "fault": False, "coils": [True, False, True, False]},
                        "transport": {"status": "ONLINE", "actuator_running": True, "fault": False, "coils": [True, False, True, False]},
                        "hospital": {"status": "ONLINE", "actuator_running": True, "fault": False, "coils": [True, False, True, False]}
                    }
                }
                self.wfile.write(json.dumps(payload).encode("utf-8"))
            else:
                self.send_response(401)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


class ThreadedMockScadaServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class TestFedVizBridge(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = VizBridgeEngine(viz_url="http://127.0.0.1:18090", throttle_sec=1.0)

    def test_format_bearer_header(self) -> None:
        self.assertEqual(format_bearer_header("auditor:AUDIT_TOKEN_2026"), "Bearer auditor:AUDIT_TOKEN_2026")
        self.assertEqual(format_bearer_header("Bearer operator:TOKEN"), "Bearer operator:TOKEN")

    def test_helics_metrics_mapping_all_sectors(self) -> None:
        raw_data = {
            "water/t2_level": 14.5,
            "water/t1_level": 8.2,
            "breaker/trip": 0,
            "gas/pressure": 152.3,
            "gas/trip": 0,
            "grid/voltage_pu": 1.02,
            "grid/frequency": 60.05,
            "grid/trip": 0,
            "transport/congestion": 0.45,
            "transport/trip": 0,
            "hospital/load_kw": 850.0,
            "hospital/on_ups": 0,
            "desal/pump_trip": 0,
            "desal/power_kw": 48.5,
            "desal/tank_level_pct": 82.0,
            "lighting/power_kw": 115.0,
            "sis/trip": 0,
        }

        sectors = self.engine.update_metrics_from_helics(raw_data)

        # Verificación de los 8 sectores esperados (Enmiendas 1 y 5)
        self.assertIn("water", sectors)
        self.assertEqual(sectors["water"]["tank_level"], 14.5)
        self.assertTrue(sectors["water"]["pump_running"])

        self.assertIn("gas", sectors)
        self.assertEqual(sectors["gas"]["pressure_psi"], 152.3)

        self.assertIn("elec", sectors)
        self.assertAlmostEqual(sectors["elec"]["grid_voltage"], 1.02 * 230.0, places=1)

        self.assertIn("transport", sectors)
        self.assertEqual(sectors["transport"]["traffic_light"], "GREEN")

        self.assertIn("hospital", sectors)
        self.assertEqual(sectors["hospital"]["load_kw"], 850.0)

        self.assertIn("desal", sectors)
        self.assertFalse(sectors["desal"]["pump_trip"])
        self.assertEqual(sectors["desal"]["power_kw"], 48.5)
        self.assertEqual(sectors["desal"]["tank_level_pct"], 82.0)

        self.assertIn("lighting", sectors)
        self.assertEqual(sectors["lighting"]["power_kw"], 115.0)

        self.assertIn("safety", sectors)
        self.assertFalse(sectors["safety"]["sis_trip"])

    def test_scada_metrics_mapping(self) -> None:
        scada_data = {
            "sectors": {
                "water": {"status": "ONLINE", "actuator_running": True, "fault": False},
                "gas": {"status": "LOSS_OF_VIEW", "actuator_running": False, "fault": True},
            }
        }
        sectors = self.engine.update_metrics_from_scada(scada_data)
        self.assertIn("water", sectors)
        self.assertTrue(sectors["water"]["pump_running"])
        self.assertIn("gas", sectors)
        self.assertTrue(sectors["gas"]["alert"])

    def test_throttling_rate_limiting(self) -> None:
        self.engine.state_buffer = {"water": {"tank_level": 12.0}}
        self.engine.last_dispatch_time = time.time()
        # Sin force y dentro del throttle_sec debe ser rechazado
        dispatched = self.engine.dispatch(force=False)
        self.assertFalse(dispatched)

    def test_http_resilience_when_viz_down(self) -> None:
        engine = VizBridgeEngine(viz_url="http://127.0.0.1:59999")  # Puerto no existente
        engine.state_buffer = {"water": {"tank_level": 12.0}}
        # No debe lanzar excepción no controlada
        dispatched = engine.dispatch(force=True)
        self.assertFalse(dispatched)

    def test_live_dispatch_to_viz_server(self) -> None:
        # Iniciar viz server real en puerto efímero
        state_engine = CityVisualizerStateEngine()
        VizRequestHandler.engine = state_engine
        server = ThreadedVizServer(("127.0.0.1", 0), VizRequestHandler)
        port = server.server_address[1]
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()

        try:
            bridge = VizBridgeEngine(viz_url=f"http://127.0.0.1:{port}")
            raw = {
                "water/t2_level": 19.8,
                "breaker/trip": 1,
                "desal/pump_trip": 1,
                "desal/power_kw": 55.0,
                "desal/tank_level_pct": 91.0,
                "safety/sis_trip": 1,
                "sis/trip": 1,
            }
            bridge.update_metrics_from_helics(raw)
            dispatched = bridge.dispatch(force=True)
            self.assertTrue(dispatched)

            # Verificar que el servidor visualizador actualizó su frame
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/viz/frame")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                sectors = data["city_sectors"]
                self.assertEqual(sectors["water"]["tank_level"], 19.8)
                self.assertTrue(sectors["water"]["alert"])
                self.assertTrue(sectors["desal"]["pump_trip"])
                self.assertEqual(sectors["desal"]["power_kw"], 55.0)
                self.assertTrue(sectors["safety"]["sis_trip"])
        finally:
            server.shutdown()
            server.server_close()

    def test_scada_poll_with_bearer_token(self) -> None:
        mock_scada = ThreadedMockScadaServer(("127.0.0.1", 0), MockScadaHandler)
        scada_port = mock_scada.server_address[1]
        t = threading.Thread(target=mock_scada.serve_forever, daemon=True)
        t.start()

        try:
            # 1. Con token correcto
            data = poll_scada_once(f"http://127.0.0.1:{scada_port}", "auditor:AUDIT_TOKEN_2026")
            self.assertIsNotNone(data)
            self.assertIn("sectors", data)

            # 2. Con token inválido
            data_bad = poll_scada_once(f"http://127.0.0.1:{scada_port}", "invalid_token")
            self.assertIsNone(data_bad)
        finally:
            mock_scada.shutdown()
            mock_scada.server_close()


if __name__ == "__main__":
    unittest.main()
