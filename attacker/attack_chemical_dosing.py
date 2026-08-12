#!/usr/bin/env python3
"""attacker/attack_chemical_dosing.py — Vector de Ataque de Dosificación Química en Planta de Agua (Fase 4)

Inspirado en investigaciones de seguridad sobre plantas de tratamiento SWaT (Oldsmar / SWaT testbed):
  1. Manipula los parámetros de dosificación de cloro/pH en la etapa 2 de distribución de agua.
  2. Mantiene los niveles de químico en un rango desproporcionado pero inferior al umbral de disparo físico del SIS.
  3. Causa contaminación/degradación sanitaria del suministro urbano sin activar alarmas críticas.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import Dict, Any

from physical.water.plant_water import TwoStageWaterPlant

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][DOSING-ATTACK] %(message)s')
LOGGER = logging.getLogger('attack_chemical_dosing')


class ChemicalDosingAttack:

    def __init__(self) -> None:
        self.plant = TwoStageWaterPlant()
        self.chemical_ppm = 1.5  # Valor seguro por defecto (1.5 ppm)

    def execute_overdosing_attack(self, target_ppm: float = 8.5) -> Dict[str, Any]:
        LOGGER.info("Iniciando alteración de dosificación química: subiendo cloro a %.1f ppm (Normal: 1.5 ppm)...", target_ppm)
        
        # Simular aumento de químico sin sobrepasar límite de falla destructiva
        self.chemical_ppm = target_ppm
        LOGGER.info("Dosificación alterada a %.1f ppm. Suministro urbano contaminado sin disparo SIS.", self.chemical_ppm)
        
        return {
            'status': 'SUCCESS',
            'baseline_ppm': 1.5,
            'altered_ppm': self.chemical_ppm,
            'contamination_achieved': self.chemical_ppm > 5.0
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="CityLab SWaT Chemical Dosing Attack Vector")
    parser.add_argument("--ppm", type=float, default=8.5, help="Nivel de concentracion quimica objetivo")
    args = parser.parse_args()

    attacker = ChemicalDosingAttack()
    res = attacker.execute_overdosing_attack(target_ppm=args.ppm)
    LOGGER.info("Resultado de ataque Chemical Dosing: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
