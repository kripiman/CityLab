#!/usr/bin/env python3
"""helics_sim/fed_sis.py — Safety Instrumented System (SIS / ESD Independiente) (Fase 7)

Federado HELICS independiente que ejecuta la lógica de Parada de Emergencia (ESD / SIS):
  - SIL-3 Safety Integrity Level.
  - Separación lógica y física respecto del sistema de control básico de proceso (BPCS).
  - Monitorea variables críticas (nivel de tanque SWaT, presión de gas, voltaje).
  - Interlocks de seguridad física indiscutibles (Emergency Trip / Interlock Action).
  - Anula cualquier comando del BPCS que comprometa la integridad física de la planta.
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional

LOGGER = logging.getLogger('fed_sis')


@dataclass
class SafetyInterlockLimits:
    max_tank_level_m3: float = 19.0       # 95% de 20m³ SWaT T1
    min_tank_level_m3: float = 0.5        # 0.5m³ SWaT T1
    max_gas_pressure_psi: float = 180.0   # Presión máxima admisible tubería gas
    max_grid_freq_hz: float = 62.5        # Frecuencia máxima red eléctrica


class SafetyInstrumentedLogic:
    """Lógica de interlocks SIL-3 independiente."""

    def __init__(self, limits: SafetyInterlockLimits = SafetyInterlockLimits()) -> None:
        self.limits = limits
        self.is_emergency_tripped = False
        self.trip_reason = ''

    def evaluate_safety_state(self, process_data: Dict[str, Any]) -> tuple[bool, str]:
        """Evalúa los interlocks de seguridad física.
        
        Retorna (must_trip, reason).
        """
        t1_level = float(process_data.get('water_t1_level', 10.0))
        gas_pressure = float(process_data.get('gas_pressure', 145.0))
        freq_hz = float(process_data.get('grid_freq', 60.0))

        if t1_level >= self.limits.max_tank_level_m3:
            return True, f"SIS TRIP: Tanque T1 sobre-nivel peligroso ({t1_level:.1f} m³ >= {self.limits.max_tank_level_m3} m³)"

        if t1_level < self.limits.min_tank_level_m3:
            return True, f"SIS TRIP: Tanque T1 bajo-nivel crítico ({t1_level:.1f} m³ < {self.limits.min_tank_level_m3} m³)"

        if gas_pressure >= self.limits.max_gas_pressure_psi:
            return True, f"SIS TRIP: Sobre-presión crítica en sector gas ({gas_pressure:.1f} PSI >= {self.limits.max_gas_pressure_psi} PSI)"

        if freq_hz >= self.limits.max_grid_freq_hz:
            return True, f"SIS TRIP: Sobre-frecuencia eléctrica crítica ({freq_hz:.1f} Hz >= {self.limits.max_grid_freq_hz} Hz)"

        return False, ''

    def enforce_safety_override(self, bpcs_command: bool, process_data: Dict[str, Any]) -> tuple[bool, bool, str]:
        """Aplica la regla de anulación SIS sobre comandos BPCS.
        
        Retorna (allowed_cmd, sis_tripped, reason).
        """
        must_trip, reason = self.evaluate_safety_state(process_data)
        if must_trip:
            self.is_emergency_tripped = True
            self.trip_reason = reason
            LOGGER.critical('[SIS/ESD] ¡INTERLOCK DE SEGURIDAD ACTIVADO! Comando BPCS anulado. Motivo: %s', reason)
            return False, True, reason

        return bpcs_command, False, 'NORMAL'


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][SIS] %(message)s')
    LOGGER.info('Iniciando Safety Instrumented System (SIS) / ESD Federate...')
    logic = SafetyInstrumentedLogic()
    
    # Standalone verification loop
    demo_state = {'water_t1_level': 19.5, 'gas_pressure': 145.0, 'grid_freq': 60.0}
    cmd, tripped, reason = logic.enforce_safety_override(bpcs_command=True, process_data=demo_state)
    LOGGER.info('Evaluación SIS demo: cmd=%s, tripped=%s, reason=%s', cmd, tripped, reason)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
