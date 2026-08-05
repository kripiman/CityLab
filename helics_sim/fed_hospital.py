#!/usr/bin/env python3
"""HELICS federate: Hospital — carga crítica con UPS/generador de respaldo.

Física modelada:
  - Carga base: 150 kW (quirófanos, UCI, refrigeración, iluminación crítica)
  - UPS: 30 min de autonomía a carga completa (energía = 75 kWh)
  - Generador diésel: activa en < 10 s tras detección de fallo de red

Lógica de failover:
  - NORMAL   : grid/voltage_pu >= 0.85 AND grid/frequency >= 58.0 Hz
  - UPS      : tensión o frecuencia fuera de rango → UPS activo, generador arrancando
  - GENERATOR: generador en línea, UPS descargando → hospital autónomo

Publicaciones HELICS:
  hospital/load_kw   (double) — demanda actual sobre la red (0 si en generador)
  hospital/on_ups    (int)    — 0=red normal, 1=UPS/generador activo

Suscripciones HELICS:
  grid/voltage_pu    (double) — tensión en pu en el nodo hospital
  grid/frequency     (double) — frecuencia de la red
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum

import helics as h

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('fed_hospital')

POLL_INTERVAL = 1.0
FED_NAME = os.environ.get('HELICS_FED_NAME', 'HOSPITAL_fed')
BROKER_ADDRESS = os.environ.get('HELICS_BROKER_ADDRESS', '127.0.0.1')
BROKER_PORT = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
MAX_STEPS = int(os.environ.get('HELICS_MAX_STEPS', '0'))

# Umbrales de protección (IEEE 1159 / NERC)
VOLTAGE_LOW_PU = 0.85    # bajo este valor → fallo de tensión
FREQ_LOW_HZ = 58.0       # bajo este valor → subfrecuencia


class PowerState(Enum):
    GRID_NORMAL = 'GRID_NORMAL'
    UPS_ACTIVE = 'UPS_ACTIVE'
    GENERATOR_ONLINE = 'GENERATOR_ONLINE'


@dataclass
class HospitalPlant:
    base_load_kw: float = 150.0          # carga base del hospital
    ups_capacity_kwh: float = 75.0       # 30 min a 150 kW
    ups_energy_kwh: float = 75.0         # energía actual del UPS
    generator_start_delay_s: float = 10.0
    state: PowerState = PowerState.GRID_NORMAL
    _gen_start_ts: float = field(default=float('inf'), repr=False)

    def update(self, voltage_pu: float, freq_hz: float, dt: float) -> tuple[float, int]:
        """Actualiza estado del hospital. Retorna (load_kw_on_grid, on_ups_flag)."""
        grid_ok = voltage_pu >= VOLTAGE_LOW_PU and freq_hz >= FREQ_LOW_HZ

        if self.state == PowerState.GRID_NORMAL:
            if not grid_ok:
                LOGGER.warning('Grid fault detected (V=%.3fpu f=%.2fHz) → activating UPS', voltage_pu, freq_hz)
                self.state = PowerState.UPS_ACTIVE
                self._gen_start_ts = time.monotonic() + self.generator_start_delay_s

        elif self.state == PowerState.UPS_ACTIVE:
            # Descargar UPS
            self.ups_energy_kwh -= (self.base_load_kw * dt) / 3600.0
            self.ups_energy_kwh = max(0.0, self.ups_energy_kwh)

            if time.monotonic() >= self._gen_start_ts:
                LOGGER.warning('Generator online → hospital autonomous')
                self.state = PowerState.GENERATOR_ONLINE

            if self.ups_energy_kwh <= 0.0:
                LOGGER.error('UPS depleted before generator online — critical failure')

            if grid_ok:
                LOGGER.info('Grid restored → returning to GRID_NORMAL')
                self.state = PowerState.GRID_NORMAL

        elif self.state == PowerState.GENERATOR_ONLINE:
            if grid_ok:
                LOGGER.info('Grid restored → switching back from generator')
                self.state = PowerState.GRID_NORMAL
                self.ups_energy_kwh = min(self.ups_capacity_kwh,
                                          self.ups_energy_kwh + (self.base_load_kw * dt) / 3600.0)

        on_ups = 0 if self.state == PowerState.GRID_NORMAL else 1
        # Cuando está en generador/UPS no consume de la red
        load_on_grid = self.base_load_kw if self.state == PowerState.GRID_NORMAL else 0.0
        return load_on_grid, on_ups


def create_federate() -> tuple[h.helics_federate, h.helics_publication, h.helics_publication,
                                h.helics_input, h.helics_input]:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, 'zmq')
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f'--federates=1 --broker_address={BROKER_ADDRESS} --brokerport={BROKER_PORT}',
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate(FED_NAME, fi)

    pub_load = h.helicsFederateRegisterGlobalPublication(fed, 'hospital/load_kw', h.HELICS_DATA_TYPE_DOUBLE, '')
    pub_ups = h.helicsFederateRegisterGlobalPublication(fed, 'hospital/on_ups', h.HELICS_DATA_TYPE_INT, '')

    sub_voltage = h.helicsFederateRegisterSubscription(fed, 'grid/voltage_pu', '')
    sub_freq = h.helicsFederateRegisterSubscription(fed, 'grid/frequency', '')

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info('HOSPITAL federate ready (broker=%s:%d)', BROKER_ADDRESS, BROKER_PORT)
    return fed, pub_load, pub_ups, sub_voltage, sub_freq


def main() -> int:
    fed, pub_load, pub_ups, sub_voltage, sub_freq = create_federate()
    plant = HospitalPlant()

    try:
        current_time = 0.0
        steps = 0
        while True:
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)

            voltage_pu = h.helicsInputGetDouble(sub_voltage)
            freq_hz = h.helicsInputGetDouble(sub_freq)

            # Valores por defecto si el federado eléctrico aún no publicó
            if voltage_pu == 0.0:
                voltage_pu = 1.0
            if freq_hz == 0.0:
                freq_hz = 60.0

            load_kw, on_ups = plant.update(voltage_pu, freq_hz, POLL_INTERVAL)

            h.helicsPublicationPublishDouble(pub_load, float(load_kw))
            h.helicsPublicationPublishInteger(pub_ups, int(on_ups))

            LOGGER.info('t=%.1f V=%.3fpu f=%.2fHz state=%s load=%.1fkW ups_kwh=%.2f',
                        current_time, voltage_pu, freq_hz,
                        plant.state.value, load_kw, plant.ups_energy_kwh)

            steps += 1
            if MAX_STEPS > 0 and steps >= MAX_STEPS:
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        LOGGER.info('Shutdown requested')
    finally:
        h.helicsFederateFinalize(fed)
        LOGGER.info('HOSPITAL federate finalized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
