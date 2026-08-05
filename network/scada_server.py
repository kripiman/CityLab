#!/usr/bin/env python3
"""network/scada_server.py — Servidor SCADA Central / Historian en DMZ (10.0.2.20)

Funcionalidad:
  - Polling periódico por Modbus/TCP hacia los 4 PLCs OT (Water, Gas, Elec, Transport).
  - Almacena telemetría en tiempo real de la infraestructura crítica de la ciudad.
  - Expone un servidor HTTP / API JSON en puerto 8080 para monitoreo y ataque (DMZ).
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

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

# Estado global SCADA
scada_state: Dict[str, Any] = {
    'last_update': 0.0,
    'sectors': {}
}


def poll_plcs() -> None:
    """Hilo de fondo que consulta periódicamente los PLCs OT."""
    while True:
        timestamp = time.time()
        sector_data = {}

        for sector, (ip, port) in PLC_CONFIGS.items():
            client = ModbusTcpClient(ip, port=port, timeout=1.0)
            try:
                if client.connect():
                    rr = client.read_coils(0, 4)
                    if rr and not rr.isError():
                        sector_data[sector] = {
                            'status': 'ONLINE',
                            'coils': [bool(b) for b in rr.bits[:4]],
                            'start_cmd': bool(rr.bits[0]),
                            'stop_cmd': bool(rr.bits[1]),
                            'actuator_running': bool(rr.bits[2]),
                            'fault': bool(rr.bits[3]),
                        }
                    else:
                        sector_data[sector] = {'status': 'ERROR_READ'}
                    client.close()
                else:
                    sector_data[sector] = {'status': 'UNREACHABLE'}
            except Exception as exc:
                sector_data[sector] = {'status': 'EXCEPTION', 'detail': str(exc)}

        scada_state['last_update'] = timestamp
        scada_state['sectors'] = sector_data
        time.sleep(2.0)


class SCADAAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass  # Suppress per-request HTTP access log noise

    def do_GET(self) -> None:
        if self.path in ('/', '/api/telemetry'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps(scada_state, indent=2)
            self.wfile.write(response.encode('utf-8'))
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()


def run_http_server(port: int = 8080) -> None:
    server = HTTPServer(('0.0.0.0', port), SCADAAPIHandler)
    LOGGER.info('Servidor SCADA Central listo en http://0.0.0.0:%d', port)
    server.serve_forever()


def main() -> int:
    LOGGER.info('Iniciando Servidor SCADA Central / Historian (DMZ)...')
    t = threading.Thread(target=poll_plcs, daemon=True)
    t.start()
    try:
        run_http_server(8080)
    except KeyboardInterrupt:
        LOGGER.info('Apagando Servidor SCADA Central...')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
