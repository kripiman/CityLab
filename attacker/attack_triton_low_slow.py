#!/usr/bin/env python3
"""attacker/attack_triton_low_slow.py — Vector de Ataque Triton/Trisis (Low-and-Slow SIS Avoidance)

Inspirado en la amenaza ciberfísica Triton/Trisis (2017).
Manipula deliberadamente las variables de proceso (nivel de agua en tanque SWaT T1 o presión de gas)
manteniéndose exactamente un 1% por debajo de los umbrales de disparo del Safety Instrumented System (SIS):
  - Tanque SWaT T1: Mantiene nivel en 18.8 m³ (Límite SIS trip = 19.0 m³).
  - Presión de Gas: Mantiene presión en 178.5 PSI (Límite SIS trip = 180.0 PSI).

Resultado:
  Genera deterioro físico continuo e ineficiencia operacional sin activar los interlocks SIL-3 del SIS.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import Dict, Any

from helics_sim.fed_sis import SafetyInstrumentedLogic, SafetyInterlockLimits
from physical.water.plant_water import TwoStageWaterPlant

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][TRITON-ATTACK] %(message)s')
LOGGER = logging.getLogger('attack_triton_low_slow')


class TritonLowSlowAttack:

    def __init__(self, target_sector: str = 'water') -> None:
        self.target_sector = target_sector
        self.sis_limits = SafetyInterlockLimits()
        self.sis_logic = SafetyInstrumentedLogic(self.sis_limits)

    def execute_stealth_manipulation(self, cycles: int = 5) -> Dict[str, Any]:
        LOGGER.info("Iniciando ataque Triton Low-and-Slow en sector: %s", self.target_sector)
        plant = TwoStageWaterPlant()
        
        # Ajustar estado del proceso rozando el umbral SIS sin superarlo
        target_t1 = self.sis_limits.max_tank_level_m3 - 0.2  # 18.8 m³
        plant.t1_level_m3 = target_t1

        results = []
        for i in range(cycles):
            # Simular avance del proceso con pulso de bomba controlado
            plant.step(p1_cmd=True, p2_cmd=False, dt=0.1)
            # Evitar superar el umbral exacto
            plant.t1_level_m3 = min(plant.t1_level_m3, target_t1)
            
            state = {'water_t1_level': plant.t1_level_m3, 'gas_pressure': 178.5, 'grid_freq': 60.0}
            must_trip, reason = self.sis_logic.evaluate_safety_state(state)
            
            LOGGER.info(
                "Ciclo %d/%d — Nivel T1: %.2f m³ | Umbral SIS: %.1f m³ | SIS Tripped: %s",
                i+1, cycles, plant.t1_level_m3, self.sis_limits.max_tank_level_m3, must_trip
            )
            results.append({'cycle': i+1, 'level': plant.t1_level_m3, 'sis_tripped': must_trip})
            time.sleep(0.05)

        return {'status': 'SUCCESS', 'stealth_maintained': not any(r['sis_tripped'] for r in results)}


def main() -> int:
    parser = argparse.ArgumentParser(description="CityLab Triton/Trisis Low-and-Slow Attack Vector")
    parser.add_argument("--sector", choices=['water', 'gas'], default='water', help="Sector objetivo")
    parser.add_argument("--cycles", type=int, default=5, help="Número de ciclos de manipulación")
    args = parser.parse_args()

    attacker = TritonLowSlowAttack(target_sector=args.sector)
    res = attacker.execute_stealth_manipulation(cycles=args.cycles)
    LOGGER.info("Resultado de ataque Triton: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
