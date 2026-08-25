from __future__ import annotations

import argparse
import logging
import socket
import sys
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.siem_pipeline import SiemCorrelationEngine

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][HONEYPOT-TOUCH] %(message)s')
LOGGER = logging.getLogger('attack_honeypot_touch')


class HoneypotTouch:

    def __init__(self, target_host: str = '10.0.5.99', target_port: int = 502) -> None:
        self.target_host = target_host
        self.target_port = target_port
        self.siem = SiemCorrelationEngine()

    def run_honeypot_interaction(self) -> Dict[str, Any]:
        LOGGER.info("Interactuando con Honeypot en %s:%d...", self.target_host, self.target_port)
        
        mode = 'TABLETOP_FALLBACK'
        socket_connected = False
        try:
            with socket.create_connection((self.target_host, self.target_port), timeout=1.0) as sock:
                socket_connected = True
                mode = 'SOCKET_LIVE'
                # Enviar probe Modbus/TCP a la trampa
                sock.sendall(b'\x00\x01\x00\x00\x00\x06\x01\x01\x00\x00\x00\x01')
                try:
                    sock.settimeout(0.5)
                    _ = sock.recv(1024)
                except Exception:
                    pass
                LOGGER.info("Conexión socket real establecida con el Honeypot en %s:%d", self.target_host, self.target_port)
        except Exception as exc:
            LOGGER.warning("Honeypot socket no disponible (%s). Modo TABLETOP_FALLBACK.", exc)
            evt = self.siem.ingest_raw_event(
                event_category='honeypot',
                event_type='alert',
                severity='HIGH',
                source_ip='10.0.1.10',
                destination_ip=self.target_host,
                service_name='substation_honeypot_s5',
                message='Conexion no autorizada detectada en trampa Honeypot'
            )
            LOGGER.info("Evento fallback ingerido en SIEM: Categoría=%s | Severidad=%s", evt.event_category, evt.severity)

        return {
            'status': 'SUCCESS',
            'mode': mode,
            'honeypot_triggered': True,
            'target_host': self.target_host,
            'target_port': self.target_port,
            'socket_connected': socket_connected,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Honeypot Touch Attack Script")
    parser.add_argument('--host', default='10.0.5.99', help='Honeypot Target IP')
    parser.add_argument('--port', type=int, default=502, help='Honeypot Target Port')
    args = parser.parse_args(argv)

    touch = HoneypotTouch(target_host=args.host, target_port=args.port)
    res = touch.run_honeypot_interaction()
    LOGGER.info("Resultado de Interaccion Honeypot: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
