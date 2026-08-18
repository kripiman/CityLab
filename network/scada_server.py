#!/usr/bin/env python3
"""network/scada_server.py — Servidor SCADA Central / Historian en DMZ (10.0.2.20)

Funcionalidad:
  - Polling periódico por Modbus/TCP hacia los 4 PLCs OT (Water, Gas, Elec, Transport).
  - Persiste telemetría en historian TSDB embebido (SQLite WAL) — Fase 1.
  - RBAC / PAM por roles (auditor / operator / engineer) — Fase 2.
  - Expone un servidor HTTP / API JSON en puerto 8080 para monitoreo y ataque (DMZ).
  - Endpoints:
      GET /                     — telemetría en tiempo real (JSON)
      GET /api/telemetry         — alias del anterior
      GET /api/history           — histórico de campos (?sector=water&field=status&limit=200)
      GET /api/history/snapshot  — snapshots completos (?sector=water&limit=50)
      GET /api/whoami            — identidad y rol del token presentado
      GET /health                — liveness probe (sin auth)
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs

from network.historian import HistorianTSDB
from network.rbac import _rbac
from network.scada_ha import SCADAPrimarySecondaryCluster

try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    from pymodbus.client.sync import ModbusTcpClient

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][SCADA_SERVER] %(message)s')
LOGGER = logging.getLogger('scada_server')

PLC_CONFIGS = {
    'water':     ('10.0.3.10', 502),
    'gas':       ('10.0.3.12', 502),
    'elec':      ('10.0.3.13', 502),
    'transport': ('10.0.3.14', 502),
}

# Estado global SCADA (telemetría en tiempo real)
scada_state: Dict[str, Any] = {
    'last_update': 0.0,
    'sectors': {}
}

# Historian TSDB embebido (Fase 1) — persiste cada snapshot de polling
_historian: HistorianTSDB = HistorianTSDB()

# Cluster de Alta Disponibilidad DCS HA (Fase 6)
_ha_cluster: SCADAPrimarySecondaryCluster = SCADAPrimarySecondaryCluster(
    node_role=os.getenv('HA_ROLE', 'PRIMARY'),
    peer_url=os.getenv('HA_PEER_URL', 'http://127.0.0.1:8081')
)

LOSS_OF_VIEW_THRESHOLD = 3
_consecutive_failures: Dict[str, int] = {sector: 0 for sector in PLC_CONFIGS}

def poll_plcs_once() -> Dict[str, Any]:
    """Ejecuta una ronda individual de consulta a los PLCs OT."""
    timestamp = time.time()
    sector_data = {}

    for sector, (ip, port) in PLC_CONFIGS.items():
        client = ModbusTcpClient(ip, port=port, timeout=1.0)
        try:
            if client.connect():
                rr = client.read_coils(0, 4)
                if rr and not rr.isError():
                    _consecutive_failures[sector] = 0
                    sector_data[sector] = {
                        'status': 'ONLINE',
                        'coils': [bool(b) for b in rr.bits[:4]],
                        'start_cmd': bool(rr.bits[0]),
                        'stop_cmd': bool(rr.bits[1]),
                        'actuator_running': bool(rr.bits[2]),
                        'fault': bool(rr.bits[3]),
                        'consecutive_failures': 0
                    }
                else:
                    _consecutive_failures[sector] += 1
                    status = 'LOSS_OF_VIEW' if _consecutive_failures[sector] >= LOSS_OF_VIEW_THRESHOLD else 'ERROR_READ'
                    sector_data[sector] = {'status': status, 'consecutive_failures': _consecutive_failures[sector]}
                client.close()
            else:
                _consecutive_failures[sector] += 1
                status = 'LOSS_OF_VIEW' if _consecutive_failures[sector] >= LOSS_OF_VIEW_THRESHOLD else 'UNREACHABLE'
                sector_data[sector] = {'status': status, 'consecutive_failures': _consecutive_failures[sector]}
        except Exception as exc:
            _consecutive_failures[sector] += 1
            status = 'LOSS_OF_VIEW' if _consecutive_failures[sector] >= LOSS_OF_VIEW_THRESHOLD else 'EXCEPTION'
            sector_data[sector] = {'status': status, 'detail': str(exc), 'consecutive_failures': _consecutive_failures[sector]}

    scada_state['last_update'] = timestamp
    scada_state['sectors'] = sector_data

    # Fase 1 — Persistir snapshots en historian TSDB
    for sector, data in sector_data.items():
        try:
            _historian.write_snapshot(sector, data, timestamp)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning('[Historian] Error al escribir snapshot %s: %s', sector, exc)
    return sector_data


def poll_plcs() -> None:
    """Hilo de fondo que consulta periódicamente los PLCs OT."""
    while True:
        poll_plcs_once()
        time.sleep(2.0)


class SCADAAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass  # Suppress per-request HTTP access log noise

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        # --- Fase 2: RBAC auth (preserva STRICT_AUTH toggle para CTF) ---
        if parsed.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return

        auth_header = self.headers.get('Authorization')
        role, http_code = _rbac.resolve(auth_header)
        if role is None:
            self.send_response(http_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'unauthorized', 'code': http_code}).encode())
            return

        if not _rbac.is_authorized(role, parsed.path):
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'forbidden', 'role': role, 'path': parsed.path}).encode())
            return

        # --- Routing con rol verificado ---

        if parsed.path in ('/', '/api/telemetry'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-SCADA-Role', role)  # Fase 2: informar rol al cliente
            self.end_headers()
            response = json.dumps(scada_state, indent=2)
            self.wfile.write(response.encode('utf-8'))

        elif parsed.path == '/api/history':
            # Fase 1: Consulta histórica de campos individuales.
            # Params: ?sector=<name>&field=<field>&limit=<int>&since=<epoch>
            sector = qs.get('sector', [None])[0]
            field = qs.get('field', [None])[0]
            limit = int(qs.get('limit', ['200'])[0])
            since = float(qs.get('since', ['0'])[0]) or None
            if not sector:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "sector param required"}')
                return
            rows = _historian.query(sector=sector, field=field, since=since, limit=limit)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'sector': sector, 'field': field, 'rows': rows}, indent=2).encode('utf-8'))

        elif parsed.path == '/api/history/snapshot':
            # Fase 1: Snapshots completos por sector (útil para HMI y análisis forense).
            # Params: ?sector=<name>&limit=<int>&since=<epoch>
            sector = qs.get('sector', [None])[0]
            limit = int(qs.get('limit', ['50'])[0])
            since = float(qs.get('since', ['0'])[0]) or None
            if not sector:
                # Sin sector: retorna último snapshot de todos los sectores
                result = {s: _historian.last(s) for s in _historian.sectors()}
            else:
                result = _historian.query_snapshots(sector=sector, since=since, limit=limit)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))

        elif parsed.path in ('/api/control', '/api/control/read', '/api/control/write'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-SCADA-Role', role)
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'SUCCESS', 'role': role, 'path': parsed.path}).encode('utf-8'))

        elif parsed.path == '/api/whoami':
            # Fase 2: introspección de identidad y rol del token
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'role': role, 'strict_auth': os.getenv('STRICT_AUTH', '0') == '1'}).encode())

        elif parsed.path == '/api/ha/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(_ha_cluster.get_cluster_status()).encode('utf-8'))

        elif parsed.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b'{}'
        try:
            body_json = json.loads(post_body.decode('utf-8'))
        except Exception:
            body_json = {}

        if parsed.path == '/api/ha/heartbeat':
            sender_role = body_json.get('role', 'UNKNOWN')
            resp = _ha_cluster.receive_heartbeat(sender_role=sender_role)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return
        elif parsed.path == '/api/ha/sync':
            state_snapshot = body_json.get('state', {})
            if state_snapshot:
                scada_state['sectors'].update(state_snapshot)
                scada_state['last_update'] = time.time()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'SYNC_OK'}).encode('utf-8'))
            return

        auth_header = self.headers.get('Authorization')
        role, http_code = _rbac.resolve(auth_header)
        if role is None:
            self.send_response(http_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'unauthorized', 'code': http_code}).encode())
            return

        if not _rbac.is_authorized(role, parsed.path):
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'forbidden', 'role': role, 'path': parsed.path}).encode())
            return

        if parsed.path in ('/api/control', '/api/control/write'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-SCADA-Role', role)
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'SUCCESS',
                'action_executed': body_json.get('action', 'write'),
                'target': body_json.get('target', 'all'),
                'role': role
            }).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def run_http_server(port: int = 8080) -> None:
    host = '0.0.0.0'
    server = HTTPServer((host, port), SCADAAPIHandler)
    LOGGER.info('Servidor SCADA Central listo en http://%s:%d', host, port)
    server.serve_forever()


def main() -> int:
    LOGGER.info('Iniciando Servidor SCADA Central / Historian (DMZ)...')
    t = threading.Thread(target=poll_plcs, daemon=True)
    t.start()
    _ha_cluster.start_ha_monitor()
    try:
        run_http_server(8080)
    except KeyboardInterrupt:
        LOGGER.info('Apagando Servidor SCADA Central...')
        _ha_cluster.stop_ha_monitor()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
