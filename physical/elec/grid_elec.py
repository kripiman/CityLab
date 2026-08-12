#!/usr/bin/env python3
"""physical/elec/grid_elec.py — Modelo Físico de Subestación Eléctrica

Simula la frecuencia de red (Hz), voltaje de barra (kV) y estado del interruptor de potencia (Breaker XCBR1).
Ecuaciones de inercia y balance de potencia:
  df/dt = (P_gen - P_load) / (2 * H)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

LOGGER = logging.getLogger('grid_elec')


@dataclass
class GridParams:
    nominal_freq_hz: float = 50.0
    nominal_voltage_kv: float = 110.0
    inertia_h: float = 4.0
    generation_mw: float = 50.0
    load_mw: float = 48.0


class ElectricalSubstationGrid:
    """Modelo físico de subestación de transmisión / distribución eléctrica."""

    def __init__(self, params: GridParams = GridParams()) -> None:
        self.params = params
        self.frequency_hz = params.nominal_freq_hz
        self.bus_voltage_kv = params.nominal_voltage_kv
        self.breaker_closed = True

    def step(self, dt_s: float = 1.0) -> float:
        """Avanza la simulación dinámica de la red eléctrica dt_s segundos."""
        if not self.breaker_closed:
            # Breaker tripped -> caida acelerada de voltaje y desviacion de frecuencia
            self.bus_voltage_kv = max(0.0, self.bus_voltage_kv - 15.0 * dt_s)
            self.frequency_hz = max(45.0, self.frequency_hz - 0.5 * dt_s)
        else:
            p_gen = self.params.generation_mw
            p_load = self.params.load_mw
            df_dt = (p_gen - p_load) / (2.0 * self.params.inertia_h)
            self.frequency_hz = max(45.0, min(55.0, self.frequency_hz + df_dt * 0.05 * dt_s))
            self.bus_voltage_kv = self.params.nominal_voltage_kv
        return self.frequency_hz
