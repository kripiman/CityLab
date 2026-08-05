"""physical/transport/traffic.py — Modelo ciberfísico de intersección de semáforos urbanos.

Modelado:
  - Intersección de 4 fases (Norte-Sur / Este-Oeste).
  - Interdependencia Eléctrica: Requiere energía de la red (grid/voltage_pu >= 0.85).
    Si la subestación cae, pasa a modo destello de emergencia (FLASHING_YELLOW) y
    el índice de congestión urbana sube hacia 1.0 (bloqueo vehicular/ambulancias).
  - Control PLC Modbus:
    - Coil 0: auto_cycle (Ciclo automático normal).
    - Coil 1: emergency_corridor (Prioridad pasaje ambulancias hacia el Hospital).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LightPhase(Enum):
    GREEN_NS = "GREEN_NS_RED_EW"
    YELLOW_NS = "YELLOW_NS_RED_EW"
    GREEN_EW = "RED_NS_GREEN_EW"
    YELLOW_EW = "RED_NS_YELLOW_EW"
    FLASHING_EMERGENCY = "FLASHING_YELLOW_EMERGENCY"


@dataclass
class TrafficLightIntersection:
    phase_timer_s: float = 0.0
    phase_duration_s: float = 5.0
    current_phase: LightPhase = LightPhase.GREEN_NS
    congestion_index: float = 0.1  # 0.0 = Fluido, 1.0 = Emboteamiento total (Gridlock)

    def step(self, emergency_override: bool, power_available: bool = True, dt: float = 1.0) -> tuple[str, float]:
        """Avanza el estado de la intersección vehicular.
        
        Retorna (nombre_fase, índice_congestión).
        """
        if not power_available:
            self.current_phase = LightPhase.FLASHING_EMERGENCY
            # Sin semáforos la congestión escala continuamente
            self.congestion_index += 0.03 * dt
            self.congestion_index = min(1.0, self.congestion_index)
            return self.current_phase.value, self.congestion_index

        if emergency_override:
            # Corredor de emergencia forzado por PLC (prioridad al hospital)
            self.current_phase = LightPhase.GREEN_NS
            self.congestion_index = max(0.05, self.congestion_index - 0.02 * dt)
            return self.current_phase.value, self.congestion_index

        # Operación normal autorregulada
        self.phase_timer_s += dt
        if self.phase_timer_s >= self.phase_duration_s:
            self.phase_timer_s = 0.0
            if self.current_phase == LightPhase.GREEN_NS:
                self.current_phase = LightPhase.YELLOW_NS
            elif self.current_phase == LightPhase.YELLOW_NS:
                self.current_phase = LightPhase.GREEN_EW
            elif self.current_phase == LightPhase.GREEN_EW:
                self.current_phase = LightPhase.YELLOW_EW
            else:
                self.current_phase = LightPhase.GREEN_NS

        # En operación normal la congestión se mantiene baja
        self.congestion_index = max(0.05, self.congestion_index - 0.01 * dt)
        return self.current_phase.value, self.congestion_index

    def needs_trip(self) -> bool:
        """Alerta de colapso de tráfico urbano si el índice supera 0.80."""
        return self.congestion_index > 0.80
