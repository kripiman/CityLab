"""physical/water/plant_water.py — Modelo físico de tratamiento de agua en 2 etapas (SWaT-inspired).

Etapa 1: Reservorio Crudo → Bomba P1 → Tanque Sedimentador T1
Etapa 2: Tanque T1 → Bomba P2 → Tanque Distribución T2 → Demanda Ciudadana

Interdependencia Eléctrica:
  Ambas bombas (P1 y P2) requieren alimentación eléctrica (power_available=True).
  Si la red sufre un blackout o caída de tensión (voltage_pu < 0.85), ambas bombas
  se detienen aunque el PLC ordene arrancar.

  P1: controlada por PLC vía Modbus (coil 2 = actuator_running).
  P2: sin PLC propio en Fase 2 — activa automáticamente si hay energía y T1 > 0.5 m³.
      Decisión de diseño explícita: P2 comparte alimentación eléctrica con P1.
"""
from __future__ import annotations

from dataclasses import dataclass
from physical.water.epanet_solver import EpanetHydraulicSolver


@dataclass
class TwoStageWaterPlant:
    # Tanque T1 (Sedimentación)
    t1_level_m3: float = 10.0
    t1_capacity_m3: float = 20.0
    p1_flow_m3_s: float = 1.0        # Flujo bomba P1 (Reservorio → T1)

    # Tanque T2 (Distribución a la ciudad)
    t2_level_m3: float = 15.0
    t2_capacity_m3: float = 30.0
    p2_flow_m3_s: float = 0.8        # Flujo bomba P2 (T1 → T2)
    city_demand_m3_s: float = 0.5    # Demanda constante de agua de la ciudad
    epanet_solver: EpanetHydraulicSolver = None  # type: ignore

    def __post_init__(self) -> None:
        if self.epanet_solver is None:
            self.epanet_solver = EpanetHydraulicSolver()

    def step(self, p1_cmd: bool, p2_cmd: bool, power_available: bool = True, dt: float = 1.0) -> tuple[float, float]:
        """Avanza el estado de la planta 2 etapas con motor EPANET.
        
        Retorna (t1_level_m3, t2_level_m3).
        """
        p1_active = p1_cmd and power_available
        p2_active = p2_cmd and power_available and (self.t1_level_m3 > 0.5)

        # Resuelve hidráulica EPANET para P1 y P2
        flow_p1, press_p1, _ = self.epanet_solver.solve_network(p1_active, self.p1_flow_m3_s)
        flow_p2, press_p2, _ = self.epanet_solver.solve_network(p2_active, self.p2_flow_m3_s)

        t1_in = flow_p1
        t1_out = flow_p2
        self.t1_level_m3 += (t1_in - t1_out) * dt

        t2_in = t1_out
        t2_out = self.city_demand_m3_s
        self.t2_level_m3 += (t2_in - t2_out) * dt

        # Clamping de seguridad física
        self.t1_level_m3 = max(0.0, min(self.t1_capacity_m3, self.t1_level_m3))
        self.t2_level_m3 = max(0.0, min(self.t2_capacity_m3, self.t2_level_m3))

        return self.t1_level_m3, self.t2_level_m3

    def needs_trip(self) -> bool:
        """Regla de disparo de protección de planta:
        - T1 desborde (>95%) o seco (<0.5m³)
        - T2 bajo nivel crítico de distribución (<2.0m³)
        """
        if self.t1_level_m3 >= 0.95 * self.t1_capacity_m3 or self.t1_level_m3 < 0.5:
            return True
        if self.t2_level_m3 < 2.0:
            return True
        return False
