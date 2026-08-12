#!/usr/bin/env python3
"""attacker/attack_ot_passive_recon.py — Escenario 13: Reconocimiento Pasivo OT (Sniffing)

Simula la captura pasiva de paquetes de red en celdas OT (Mininet s1/s2/s3):
  1. Escucha puertos de control industrial (Modbus 502, DNP3 20000, OPC UA 4840).
  2. Mapea la topología de red sin transmitir paquetes (cero impacto operacional).
"""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][PASSIVE-RECON] %(message)s')
LOGGER = logging.getLogger('attack_ot_passive_recon')


class OtPassiveRecon:

    def __init__(self) -> None:
        self.discovered_devices: List[Dict[str, Any]] = [
            {'ip': '10.0.3.10', 'port': 502, 'protocol': 'Modbus/TCP', 'sector': 'Water PLC'},
            {'ip': '10.0.3.12', 'port': 502, 'protocol': 'Modbus/TCP', 'sector': 'Gas PLC'},
            {'ip': '10.0.3.13', 'port': 502, 'protocol': 'Modbus/TCP', 'sector': 'Elec PLC'},
            {'ip': '10.0.3.20', 'port': 10102, 'protocol': 'IEC 61850 GOOSE', 'sector': 'Substation IED'},
            {'ip': '10.0.3.30', 'port': 4840, 'protocol': 'OPC UA', 'sector': 'Telemetry Gateway'},
        ]

    def run_passive_sniff(self) -> Dict[str, Any]:
        LOGGER.info("Iniciando captura pasiva de trafico en interfaz de red OT...")
        for dev in self.discovered_devices:
            LOGGER.info("Capturado paquete: %s:%d [%s] -> %s", dev['ip'], dev['port'], dev['protocol'], dev['sector'])
        
        return {
            'status': 'SUCCESS',
            'devices_mapped': len(self.discovered_devices),
            'stealth_maintained': True
        }


def main() -> int:
    recon = OtPassiveRecon()
    res = recon.run_passive_sniff()
    LOGGER.info("Resultado de Reconocimiento Pasivo: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
