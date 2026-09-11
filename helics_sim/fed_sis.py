"""helics_sim/fed_sis.py — Safety Instrumented System (SIS / ESD Independiente) (Fase 7)

Federado HELICS independiente que ejecuta la lógica de Parada de Emergencia (ESD / SIS):
  - SIL-3 Safety Integrity Level.
  - Separación lógica y física respecto del sistema de control básico de proceso (BPCS).
  - Monitorea variables críticas (nivel de tanque SWaT, presión de gas, frecuencia red eléctrica).
  - Interlocks de seguridad física indiscutibles (Emergency Trip / Interlock Action).
  - Anula cualquier comando del BPCS que comprometa la integridad física de la planta.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional

try:
    import helics as h
    HAS_HELICS = True
except ImportError:
    HAS_HELICS = False

LOGGER = logging.getLogger('fed_sis')
BROKER_ADDRESS = os.environ.get('HELICS_BROKER_ADDRESS', '127.0.0.1')
BROKER_PORT = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
POLL_INTERVAL = 1.0


@dataclass
class SafetyInterlockLimits:
    # SIS_MAX_TANK_LEVEL permite la randomizacion pedagogica del Escenario 28 (Entorno Ciego
    # Anti-Memorizacion); en ausencia de la env var conserva el valor de diseño 19.0 (95% de 20m³ SWaT T1).
    max_tank_level_m3: float = float(os.getenv('SIS_MAX_TANK_LEVEL', '19.0'))
    min_tank_level_m3: float = 0.5        # 0.5m³ SWaT T1
    max_gas_pressure_psi: float = 180.0   # Presión máxima admisible tubería gas
    max_grid_freq_hz: float = 62.5        # Frecuencia máxima admisible red eléctrica (SIL-3 threshold sobre 60Hz nominal)


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


def create_federate() -> tuple[Any, Any, Any, Any, Any]:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f"--federates=1 --broker_address={BROKER_ADDRESS} --brokerport={BROKER_PORT}",
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate("SIS_fed", fi)

    pub_sis_trip = h.helicsFederateRegisterGlobalPublication(fed, "sis/trip", h.HELICS_DATA_TYPE_INT, "")
    pub_desal_trip = h.helicsFederateRegisterGlobalPublication(fed, "desal/pump_trip", h.HELICS_DATA_TYPE_INT, "")
    sub_t1 = h.helicsFederateRegisterSubscription(fed, "water/t1_level", "")
    sub_gas = h.helicsFederateRegisterSubscription(fed, "gas/pressure", "")
    sub_freq = h.helicsFederateRegisterSubscription(fed, "grid/frequency", "")

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info("HELICS federate SIS_fed ready (broker=%s:%d)", BROKER_ADDRESS, BROKER_PORT)
    return fed, pub_sis_trip, pub_desal_trip, sub_t1, sub_gas, sub_freq


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][SIS] %(message)s')
    LOGGER.info('Iniciando Safety Instrumented System (SIS) / ESD Federate...')
    logic = SafetyInstrumentedLogic()

    standalone = os.environ.get('HELICS_STANDALONE', '0') == '1' or not HAS_HELICS
    if standalone:
        LOGGER.warning('[SIS] HELICS no disponible o modo standalone activo.')
        demo_state = {'water_t1_level': 19.5, 'gas_pressure': 145.0, 'grid_freq': 60.0}
        cmd, tripped, reason = logic.enforce_safety_override(bpcs_command=True, process_data=demo_state)
        LOGGER.info('Evaluación SIS demo: cmd=%s, tripped=%s, reason=%s', cmd, tripped, reason)
        return 0

    try:
        fed, pub_sis_trip, pub_desal_trip, sub_t1, sub_gas, sub_freq = create_federate()
        current_time = 0.0
        max_steps = int(os.environ.get('HELICS_MAX_STEPS', '0'))
        steps = 0

        while True:
            steps += 1
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)

            t1_val = h.helicsInputGetDouble(sub_t1)
            gas_val = h.helicsInputGetDouble(sub_gas)
            freq_val = h.helicsInputGetDouble(sub_freq)

            process_data = {
                'water_t1_level': 10.0 if t1_val < -1e20 else t1_val,
                'gas_pressure': 90.0 if gas_val < -1e20 else gas_val,
                'grid_freq': 60.0 if (freq_val < -1e20 or freq_val > 70.0) else freq_val,
            }

            must_trip, reason = logic.evaluate_safety_state(process_data)
            trip_val = 1 if must_trip else 0
            h.helicsPublicationPublishInteger(pub_sis_trip, trip_val)
            h.helicsPublicationPublishInteger(pub_desal_trip, trip_val)
            LOGGER.info('[SIS] t=%.1f trip=%d reason=%s', current_time, trip_val, reason or 'NORMAL')

            if max_steps > 0 and steps >= max_steps:
                break
            time.sleep(POLL_INTERVAL)
    except Exception as exc:
        LOGGER.warning('[SIS] Error en ciclo HELICS: %s', exc)
    finally:
        if 'fed' in locals():
            h.helicsFederateFinalize(fed)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
