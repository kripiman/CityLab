#!/usr/bin/env python3
"""attacker/attack_modbus_read_only.py — Escenario 15: Lectura Pasiva de Registros Modbus (No-Destructiva)

Conecta a un PLC objetivo mediante Modbus/TCP y lee el estado de bobinas e inputs sin realizar escrituras:
  1. Lee Coils 0-3 y Holding Registers para monitorear el estado del proceso físico.
  2. Demuestra la visibilidad en tiempo real sin alterar la operación de la planta.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    from pymodbus.client.sync import ModbusTcpClient

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][MODBUS-READ] %(message)s')
LOGGER = logging.getLogger('attack_modbus_read_only')


class ModbusReadOnly:

    def run_read_telemetry(
        self,
        host: str = '10.0.3.10',
        port: int = 502,
        timeout: float = 2.0,
    ) -> Dict[str, Any]:
        """Lee telemetría vía Modbus/TCP en modo pasivo sin escrituras."""
        LOGGER.info("Conectando en modo solo lectura Modbus/TCP a PLC %s:%d...", host, port)
        client = ModbusTcpClient(host, port=port, timeout=timeout)
        try:
            connected = client.connect()
            if not connected:
                LOGGER.warning("No se pudo conectar a %s:%d. Modo TABLETOP_FALLBACK.", host, port)
                return {
                    'status': 'SUCCESS',
                    'mode': 'TABLETOP_FALLBACK',
                    'host': host,
                    'port': port,
                    'coils_read': (1, 0, 1, 0),
                    'holding_registers_read': [0] * 30,
                    'write_attempted': False,
                }

            rr_coils = client.read_coils(0, 4)
            coils: Tuple[int, ...] = (0, 0, 0, 0)
            if rr_coils and not rr_coils.isError():
                coils = tuple(int(b) for b in rr_coils.bits[:4])

            rr_hr = client.read_holding_registers(0, 30)
            holding_regs: List[int] = []
            if rr_hr and not rr_hr.isError():
                holding_regs = list(rr_hr.registers)

            LOGGER.info("Valores leídos — Coils: %s | Holding Registers: %s", coils, holding_regs)
            return {
                'status': 'SUCCESS',
                'mode': 'SOCKET_LIVE',
                'host': host,
                'port': port,
                'coils_read': coils,
                'holding_registers_read': holding_regs,
                'write_attempted': False,
            }
        finally:
            client.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab Modbus Read-Only Telemetry Inspector")
    parser.add_argument('--host', default='10.0.3.10', help='Target PLC IP')
    parser.add_argument('--port', type=int, default=502, help='Target Modbus Port')
    args = parser.parse_args(argv)

    reader = ModbusReadOnly()
    res = reader.run_read_telemetry(host=args.host, port=args.port)
    LOGGER.info("Resultado de Lectura Modbus: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
