#!/usr/bin/env python3
"""physical/water/epanet_solver.py — Motor Hidráulico EPANET (Fase 4)

Simulador de dinámica de fluidos hidráulica basado en ecuaciones de Hazen-Williams
y curvas de operación de bombas de presión de agua.

Ecuaciones físicas implementadas:
  1. Pérdida de carga Hazen-Williams:
     h_f = 10.67 * L * Q^1.852 / (C^1.852 * D^4.87)
  2. Curva de Bomba de Agua (Head vs Flow):
     H_pump = H_0 - A * Q^B
  3. Presión en nodos (Junction Head):
     P_node = (H_head - Z_elevation - h_f) * gamma

Integración:
  - Acoplado a `TwoStageWaterPlant` en `physical/water/plant_water.py`.
  - Proporciona telemetría de presión en bar/PSI y tasa de flujo m³/h real.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class PipeConfig:
    length_m: float = 100.0      # L (m)
    diameter_m: float = 0.5     # D (m) - 500mm industrial pipe
    c_factor: float = 130.0     # C (Hazen-Williams roughness: PVC/Ductile Iron)


@dataclass
class PumpConfig:
    h0_head_m: float = 50.0      # Shutoff head (m)
    a_coeff: float = 15.0       # Coefficient A
    b_exp: float = 2.0          # Exponent B (Quadratic pump curve)


class EpanetHydraulicSolver:
    """Solver hidráulico de red de distribución de agua (Modelo didáctico Hazen-Williams / EPANET)."""

    def __init__(
        self,
        pipe: PipeConfig = PipeConfig(),
        pump: PumpConfig = PumpConfig(),
        reservoir_head_m: float = 10.0,
        node_elevation_m: float = 2.0
    ) -> None:
        self.pipe = pipe
        self.pump = pump
        self.reservoir_head = reservoir_head_m
        self.node_elevation = node_elevation_m

    def compute_head_loss(self, flow_m3_s: float) -> float:
        """Calcula la pérdida de fricción en la tubería usando Hazen-Williams."""
        if flow_m3_s <= 0.0:
            return 0.0
        q = abs(flow_m3_s)
        hf = 10.67 * self.pipe.length_m * (q ** 1.852) / (
            (self.pipe.c_factor ** 1.852) * (self.pipe.diameter_m ** 4.87)
        )
        return hf

    def compute_pump_head(self, flow_m3_s: float) -> float:
        """Calcula la presión generada por la bomba según su curva TDH."""
        if flow_m3_s <= 0.0:
            return self.pump.h0_head_m
        head = self.pump.h0_head_m - self.pump.a_coeff * (flow_m3_s ** self.pump.b_exp)
        return max(0.0, head)

    def solve_network(self, pump_active: bool, requested_flow_m3_s: float) -> Tuple[float, float, float]:
        """Calcula el estado hidráulico de la red.
        
        Retorna (flow_m3_s, pressure_bar, friction_loss_m).
        """
        if not pump_active:
            # Presión estática únicamente por gravedad de reservorio
            head = max(0.0, self.reservoir_head - self.node_elevation)
            pressure_bar = (head * 9.81 * 1000.0) / 100000.0  # P = rho * g * h (bar)
            return 0.0, pressure_bar, 0.0

        flow = max(0.0, requested_flow_m3_s)
        pump_h = self.compute_pump_head(flow)
        hf = self.compute_head_loss(flow)

        total_head = self.reservoir_head + pump_h - hf - self.node_elevation
        total_head = max(0.0, total_head)

        # Conversión de Head (m) a Presión (bar): 1 m = ~0.0981 bar
        pressure_bar = (total_head * 9.81 * 1000.0) / 100000.0
        return flow, pressure_bar, hf


SimplifiedHydraulicModel = EpanetHydraulicSolver
