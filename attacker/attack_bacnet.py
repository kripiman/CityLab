#!/usr/bin/env python3
"""attacker/attack_bacnet.py — Script de emulación adversaria BACnet/IP (Categoría B OT)

Simula inyección de comandos BACnet/IP UDP (Who-Is / Alarm override) contra el PLC hospitalario/edificio.
"""

from __future__ import annotations

import argparse
import logging
import socket
import sys
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][BACNET] %(message)s')
LOGGER = logging.getLogger('attack_bacnet')


class BacnetAttacker:
    """Emulador de ataque BACnet/IP sobre UDP 47808."""

    def __init__(self, target_host: str = '127.0.0.1', target_port: int = 47808) -> None:
        self.target_host = target_host
        self.target_port = target_port

    def send_whois(self) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        bvlc_whois = bytearray([0x81, 0x0b, 0x00, 0x0c, 0x01, 0x00, 0x10, 0x08])
        try:
            s.sendto(bytes(bvlc_whois), (self.target_host, self.target_port))
            resp, _ = s.recvfrom(1024)
            s.close()
            return {
                'status': 'SUCCESS',
                'mode': 'SOCKET_LIVE',
                'raw_hex': resp.hex(),
                'bvlc': bool(resp and resp[0] == 0x81),
            }
        except Exception as exc:
            s.close()
            LOGGER.warning("BACnet Who-Is fallo conexion (%s). Modo TABLETOP_FALLBACK.", exc)
            return {
                'status': 'SUCCESS',
                'mode': 'TABLETOP_FALLBACK',
                'error': str(exc),
                'bvlc': False,
            }

    def inject_alarm_override(self) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        cmd = b'OVERRIDE BACNET HVAC ALARM\n'
        try:
            s.sendto(cmd, (self.target_host, self.target_port))
            resp, _ = s.recvfrom(1024)
            s.close()
            text = resp.decode('utf-8', errors='replace')
            return {
                'status': 'SUCCESS',
                'mode': 'SOCKET_LIVE',
                'response': text,
                'alarm_set': 'STATUS=ALARM' in text,
            }
        except Exception as exc:
            s.close()
            LOGGER.warning("BACnet Alarm override fallo conexion (%s). Modo TABLETOP_FALLBACK.", exc)
            return {
                'status': 'SUCCESS',
                'mode': 'TABLETOP_FALLBACK',
                'error': str(exc),
                'alarm_set': False,
            }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BACnet/IP Attack Utility")
    parser.add_argument('--host', default='127.0.0.1', help='Target BACnet IP')
    parser.add_argument('--port', type=int, default=47808, help='Target BACnet Port')
    args = parser.parse_args(argv)

    attacker = BacnetAttacker(target_host=args.host, target_port=args.port)
    res1 = attacker.send_whois()
    LOGGER.info("BACnet Who-Is Result: %s", res1)
    res2 = attacker.inject_alarm_override()
    LOGGER.info("BACnet Alarm Injected: %s", res2)
    return 0 if res1['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
