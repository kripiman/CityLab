#!/usr/bin/env python3
"""physical/gas/plant_gas.py — Modelo Físico de Gasoducto y Compresión de Gas

Simula la dinámica de presión (bar) y flujo volumétrico (m³/h) en el sector gas.
Ecuaciones de estado:
  dP/dt = (Q_in * P_in - Q_out * P_out) / V_pipe - k_leak * P
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

LOGGER = logging.getLogger('plant_gas')


@dataclass
class GasPipelineParams:
    pipe_volume_m3: float = 500.0
    nominal_pressure_bar: float = 40.0
    compressor_flow_m3h: float = 1200.0
    consumption_flow_m3h: float = 1000.0
    leak_coeff: float = 0.05


class GasPipelinePlant:
    """Modelo físico dinámico de gasoducto con estación compresora."""

    def __init__(self, params: GasPipelineParams = GasPipelineParams()) -> None:
        self.params = params
        self.pressure_bar = params.nominal_pressure_bar
        self.compressor_running = True
        self.valve_open = True
        self.leak_detected = False

    def step(self, dt_s: float = 1.0) -> float:
        """Avanza la simulación física de gas dt_s segundos."""
        q_in = self.params.compressor_flow_m3h / 3600.0 if self.compressor_running else 0.0
        q_out = self.params.consumption_flow_m3h / 3600.0 if self.valve_open else 0.0
        k_leak = self.params.leak_coeff * 2.0 if self.leak_detected else self.params.leak_coeff

        dp_dt = ((q_in - q_out) * 0.1) - (k_leak * (self.pressure_bar - 1.0) * 0.01)
        self.pressure_bar = max(0.0, self.pressure_bar + dp_dt * dt_s)
        return self.pressure_bar
