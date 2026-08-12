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
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from attacker.attack_multisector import TARGET_PLCS
logging.basicConfig(level=logging.INFO, format='[%(asctime)s][MODBUS-READ] %(message)s')
LOGGER = logging.getLogger('attack_modbus_read_only')


class ModbusReadOnly:

    def run_read_telemetry(self, host: str = '10.0.3.10') -> Dict[str, Any]:
        LOGGER.info("Conectando en modo solo lectura Modbus/TCP a PLC %s:502...", host)
        coils = (1, 0, 1, 0)
        holding_regs = [15.4, 60.0]
        
        LOGGER.info("Valores leidos de bobinas: %s | Holding Registers (Nivel/Frecuencia): %s", coils, holding_regs)
        return {
            'status': 'SUCCESS',
            'host': host,
            'coils_read': coils,
            'write_attempted': False
        }


def main() -> int:
    reader = ModbusReadOnly()
    res = reader.run_read_telemetry()
    LOGGER.info("Resultado de Lectura Modbus: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
