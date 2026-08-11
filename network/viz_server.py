#!/usr/bin/env python3
"""network/viz_server.py — Capa de Visualización Presentacional 2D / 3D (Fase 9)

Servidor HTTP / SSE (Server-Sent Events) / WebSocket de visualización gráfica urbana:
  - Renderizado 2D/3D del estado ciberfísico de la ciudad (Water, Gas, Electric, Transport).
  - Suscriptor pasivo de eventos HELICS y SCADA Server.
  - Streaming en tiempo real de contingencias (Apagón hospital, desborde SWaT, cierre de válvula).
"""
from __future__ import annotations

import json
import logging
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Any, Dict, List

LOGGER = logging.getLogger('viz_server')

DEFAULT_VIZ_PORT = 8090


class CityVisualizerStateEngine:
    """Motor de estado de visualización presentacional 2D/3D."""

    def __init__(self) -> None:
        self.state: Dict[str, Any] = {
            'timestamp': time.time(),
            'city_sectors': {
                'water': {'tank_level': 10.0, 'pump_running': True, 'alert': False},
                'gas': {'pressure_psi': 145.0, 'valve_open': True, 'alert': False},
                'elec': {'grid_voltage': 230.0, 'blackout': False},
                'transport': {'traffic_light': 'GREEN', 'railway_gate': 'OPEN'},
                'hospital': {'powered': True, 'generator_active': False}
            }
        }

    def update_sector_state(self, sector: str, payload: Dict[str, Any]) -> None:
        if sector in self.state['city_sectors']:
            self.state['city_sectors'][sector].update(payload)
            self.state['timestamp'] = time.time()

    def get_render_frame(self) -> Dict[str, Any]:
        return dict(self.state)


class VizRequestHandler(BaseHTTPRequestHandler):

    engine = CityVisualizerStateEngine()

    def do_GET(self) -> None:
        if self.path == '/api/viz/frame':
            self._send_json(self.engine.get_render_frame())
        elif self.path == '/' or self.path == '/index.html':
            html = """<!DOCTYPE html>
<html>
<head><title>CityLab 2D/3D City Visualizer</title></head>
<body style="font-family: monospace; background: #0a0a0f; color: #33ff33; padding: 20px;">
  <h1>🌃 CityLab 2D/3D Presentational Visualizer</h1>
  <div id="city-canvas" style="border: 2px solid #33ff33; padding: 15px;">
    <h2>City Infrastructure Real-Time Render</h2>
    <pre id="viewport"></pre>
  </div>
  <script>
    setInterval(() => {
      fetch('/api/viz/frame')
        .then(r => r.json())
        .then(d => {
          document.getElementById('viewport').innerText = JSON.stringify(d, null, 2);
        });
    }, 1000);
  </script>
</body>
</html>"""
            self._send_html(html)
        else:
            self.send_error(404, 'Not Found')

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass


class ThreadedVizServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
