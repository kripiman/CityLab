#!/usr/bin/env python3
"""plc/honeypot_server.py — Daemon Honeypot OT en VLAN s5 (10.0.5.99)

Servidor trampa Modbus/TCP y puerto de observación para la celda s5:
  - Escucha conexiones de escaneo / recon no autorizadas en el puerto 502.
  - Ingiere automáticamente eventos de categoría 'honeypot' en el pipeline SIEM (`network/siem_pipeline.py`).
  - Alerta sobre la IP origen del atacante permitiendo la correlación SOC de intrusiones IT->OT.
"""
from __future__ import annotations

import argparse
import logging
import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.siem_pipeline import SiemCorrelationEngine

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][HONEYPOT-DAEMON] %(message)s')
LOGGER = logging.getLogger('honeypot_server')


class OtHoneypotServer:

    def __init__(self, host: str = '0.0.0.0', port: int = 502) -> None:
        self.host = host
        self.port = port
        self.siem = SiemCorrelationEngine()
        self._running = False
        self._sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._running = True
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(5)
        LOGGER.info("[HONEYPOT] Daemon activado escuchando en %s:%d (VLAN s5)", self.host, self.port)

        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def _listen_loop(self) -> None:
        if not self._sock:
            return
        while self._running:
            try:
                self._sock.settimeout(1.0)
                client, addr = self._sock.accept()
                attacker_ip = addr[0]
                LOGGER.warning("[HONEYPOT-TOUCH] ¡Conexión no autorizada detectada desde IP %s!", attacker_ip)
                
                # Ingestar evento en el SIEM
                self.siem.ingest_raw_event(
                    event_category='honeypot',
                    event_type='alert',
                    severity='HIGH',
                    source_ip=attacker_ip,
                    destination_ip=self.host,
                    service_name='ot_honeypot_s5',
                    message=f'Intrusión detectada en trampa Honeypot OT desde {attacker_ip}'
                )

                # Responder con paquete nulo y cerrar
                with client:
                    client.settimeout(0.5)
                    try:
                        data = client.recv(1024)
                        if data:
                            # Modbus/TCP dummy exception response
                            dummy_resp = b'\x00\x01\x00\x00\x00\x03\x01\x81\x01'
                            client.sendall(dummy_resp)
                    except OSError:
                        pass
            except socket.timeout:
                continue
            except Exception as exc:
                if self._running:
                    LOGGER.debug("[HONEYPOT] Excepción en listen_loop: %s", exc)

    def stop(self) -> None:
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Daemon Honeypot OT (VLAN s5)")
    default_host = os.getenv("HONEYPOT_HOST", os.getenv("BIND_HOST", "0.0.0.0"))
    parser.add_argument("--host", default=default_host, help=f"IP de escucha (default: {default_host})")
    parser.add_argument("--port", type=int, default=502, help="Puerto Modbus/TCP honeypot")
    args = parser.parse_args()

    server = OtHoneypotServer(host=args.host, port=args.port)
    server.start()
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        LOGGER.info("[HONEYPOT] Deteniendo daemon...")
        server.stop()


if __name__ == '__main__':
    main()
