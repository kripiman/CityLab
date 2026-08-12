#!/usr/bin/env python3
"""network/hmi_server.py — Dashboard HMI Industrial OpenSCADA / Ignition Edge (Fase 5)

Servidor HTTP / Dashboard HMI industrial que proporciona:
  - Diagrama de proceso P&ID (Water, Gas, Electric, Transport).
  - Telemetría en tiempo real desde `scada_server.py` y `historian.py`.
  - Mandos de control manual (START / STOP / TRIP / CLOSE) para operadores OT.
  - Consola de alarmas industriales (Loss of View, Loss of Control, Trip en Cascada).

Endpoints API HMI:
  - `GET  /api/hmi/overview`  — Estado consolidado P&ID de todos los sectores.
  - `GET  /api/hmi/alarms`    — Registro activo de alarmas de proceso.
  - `POST /api/hmi/control`   — Envío de mandos operacionales al SCADA Server.
"""
from __future__ import annotations

import json
import logging
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger('hmi_server')

DEFAULT_HMI_PORT = 8085
DEFAULT_SCADA_URL = 'http://127.0.0.1:8080'


class IndustrialHmiEngine:
    """Motor de estado HMI para consolidación P&ID y gestión de alarmas."""

    def __init__(self, scada_url: str = DEFAULT_SCADA_URL) -> None:
        self.scada_url = scada_url
        self.alarms: List[Dict[str, Any]] = []

    def fetch_scada_status(self) -> Dict[str, Any]:
        """Consulta el estado actual del servidor SCADA."""
        try:
            req = urllib.request.Request(f"{self.scada_url}/api/telemetry")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            LOGGER.debug('Error consultando SCADA server: %s', e)
        return {'status': 'OFFLINE', 'error': 'No se pudo conectar al SCADA Server'}

    def get_overview(self) -> Dict[str, Any]:
        scada_data = self.fetch_scada_status()
        sectors = scada_data.get('sectors', scada_data)

        self.alarms = []
        is_loss_of_view = False

        for sector_name in ['water', 'gas', 'elec', 'transport']:
            sec_info = sectors.get(sector_name, {}) if isinstance(sectors, dict) else {}
            if isinstance(sec_info, dict) and sec_info.get('status') == 'LOSS_OF_VIEW':
                is_loss_of_view = True
                self.alarms.append({
                    'alarm_id': f'ALM-LOV-{sector_name.upper()}',
                    'sector': sector_name,
                    'severity': 'CRITICAL',
                    'message': f'Pérdida de Visibilidad SCADA (Loss-of-View) en sector {sector_name}'
                })

        scada_connected = scada_data.get('status') != 'OFFLINE'
        has_critical_alarm = (not scada_connected) or is_loss_of_view

        return {
            'hmi_brand': 'CityLab OpenSCADA / Ignition Edge Emulator',
            'scada_connected': scada_connected,
            'process_diagram': {
                'water_sector': sectors.get('water', {'t1_level': 10.0, 't2_level': 15.0, 'p1_state': True}),
                'gas_sector': sectors.get('gas', {'pressure_psi': 145.0, 'valve_open': True}),
                'elec_sector': sectors.get('elec', {'grid_voltage': 230.0, 'breaker_closed': True}),
                'transport_sector': sectors.get('transport', {'traffic_light': 2, 'gate_open': True}),
            },
            'alarms': self.alarms,
            'active_alarms_count': len(self.alarms),
            'system_health': 'ALARM_CRITICAL' if has_critical_alarm else 'NORMAL'
        }

    def trigger_control_action(self, action: str, target: str, role_token: str = 'engineer:secret') -> Dict[str, Any]:
        """Envía una acción de control al SCADA Server."""
        try:
            payload = json.dumps({'action': action, 'target': target}).encode('utf-8')
            req = urllib.request.Request(
                f"{self.scada_url}/api/control",
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {role_token}'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                body = json.loads(resp.read().decode('utf-8'))
                return {'success': True, 'scada_response': body}
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class HmiRequestHandler(BaseHTTPRequestHandler):

    engine = IndustrialHmiEngine()

    def do_GET(self) -> None:
        if self.path == '/api/hmi/overview':
            self._send_json(self.engine.get_overview())
        elif self.path == '/api/hmi/alarms':
            self._send_json({'alarms': self.engine.alarms})
        elif self.path == '/' or self.path == '/index.html':
            html = """<!DOCTYPE html>
<html>
<head><title>CityLab Industrial HMI</title></head>
<body style="font-family: sans-serif; background: #121212; color: #00ffcc; padding: 20px;">
  <h1>🏭 CityLab OpenSCADA / Ignition Edge HMI</h1>
  <p>Status: <span id="status">CONNECTING...</span></p>
  <pre id="data"></pre>
  <script>
    fetch('/api/hmi/overview')
      .then(r => r.json())
      .then(d => {
        document.getElementById('status').innerText = d.system_health;
        document.getElementById('data').innerText = JSON.stringify(d, null, 2);
      });
  </script>
</body>
</html>"""
            self._send_html(html)
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self) -> None:
        if self.path == '/api/hmi/control':
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length)
            try:
                data = json.loads(body_bytes.decode('utf-8'))
                auth_hdr = self.headers.get('Authorization', 'Bearer engineer:secret')
                token = auth_hdr.replace('Bearer ', '').strip()
                res = self.engine.trigger_control_action(
                    action=data.get('action', ''),
                    target=data.get('target', ''),
                    role_token=token
                )
                self._send_json(res)
            except Exception as e:
                self._send_json({'success': False, 'error': str(e)}, status=400)
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
        pass  # Quiet logging for server requests


class ThreadedHmiServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
