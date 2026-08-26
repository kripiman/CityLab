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
import os
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Any, Dict, List, Optional, Sequence

from network.historian import HistorianTSDB

LOGGER = logging.getLogger('hmi_server')

DEFAULT_HMI_PORT = 8085
DEFAULT_SCADA_URL = 'http://127.0.0.1:8080'


def format_rbac_token(token: Optional[str], default_role: str = 'engineer') -> str:
    """Asegura que el token posea el formato <role>:<token> para compatibilidad STRICT_AUTH=1."""
    raw = (token or '').strip()
    if raw.startswith('Bearer '):
        raw = raw[len('Bearer '):].strip()
    if not raw:
        raw = 'ENG_TOKEN_2026'
    if ':' not in raw:
        raw = f"{default_role}:{raw}"
    return raw


class IndustrialHmiEngine:
    """Motor de estado HMI para consolidación P&ID, tendencias históricas y gestión de alarmas."""

    def __init__(
        self,
        scada_url: str = DEFAULT_SCADA_URL,
        historian: Optional[HistorianTSDB] = None,
        auth_token: Optional[str] = None
    ) -> None:
        self.scada_url = scada_url
        self.historian = historian if historian is not None else HistorianTSDB()
        raw_token = auth_token or os.getenv('SCADA_API_TOKEN', os.getenv('SCADA_TOKEN_ENGINEER', 'ENG_TOKEN_2026'))
        self.auth_token = format_rbac_token(raw_token, default_role='engineer')
        self.alarms: List[Dict[str, Any]] = []

    def fetch_scada_status(self) -> Dict[str, Any]:
        """Consulta el estado actual del servidor SCADA con cabecera de autenticación RBAC."""
        try:
            req = urllib.request.Request(
                f"{self.scada_url}/api/telemetry",
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
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

    def get_history(
        self,
        sector: str = 'water',
        field: Optional[str] = None,
        since: Optional[float] = None,
        limit: int = 200
    ) -> Dict[str, Any]:
        """Consulta series de tiempo históricas directamente a HistorianTSDB en SQLite WAL."""
        history_points = self.historian.query(sector=sector, field=field, since=since, limit=limit)
        return {
            'sector': sector,
            'field': field,
            'count': len(history_points),
            'history': history_points
        }

    def trigger_control_action(self, action: str, target: str, role_token: Optional[str] = None) -> Dict[str, Any]:
        """Envía una acción de control al SCADA Server con token RBAC."""
        token = format_rbac_token(role_token or self.auth_token, default_role='engineer')
        try:
            payload = json.dumps({'action': action, 'target': target}).encode('utf-8')
            req = urllib.request.Request(
                f"{self.scada_url}/api/control",
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
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
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == '/api/hmi/overview':
            self._send_json(self.engine.get_overview())
        elif path == '/api/hmi/alarms':
            self._send_json({'alarms': self.engine.alarms})
        elif path in ('/api/history', '/api/hmi/history'):
            sector = params.get('sector', ['water'])[0]
            field = params.get('field', [None])[0]
            since_val = float(params['since'][0]) if 'since' in params else None
            limit_val = int(params['limit'][0]) if 'limit' in params else 200
            self._send_json(self.engine.get_history(sector=sector, field=field, since=since_val, limit=limit_val))
        elif path == '/' or path == '/index.html':
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
                auth_hdr = self.headers.get('Authorization', f'Bearer {self.engine.auth_token}')
                token = format_rbac_token(auth_hdr, default_role='engineer')
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


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="CityLab Industrial HMI Server (OpenSCADA / Ignition Edge)")
    parser.add_argument("--host", default="0.0.0.0", help="Host / IP de escucha (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_HMI_PORT, help=f"Puerto HTTP (default: {DEFAULT_HMI_PORT})")
    parser.add_argument("--scada-url", default=DEFAULT_SCADA_URL, help=f"URL del SCADA Server (default: {DEFAULT_SCADA_URL})")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][HMI] %(message)s')
    engine = IndustrialHmiEngine(scada_url=args.scada_url)
    HmiRequestHandler.engine = engine
    server = ThreadedHmiServer((args.host, args.port), HmiRequestHandler)
    LOGGER.info("Servidor HMI Industrial escuchando en http://%s:%d (SCADA: %s)", args.host, args.port, args.scada_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Apagando Servidor HMI...")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
