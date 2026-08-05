"""ICSSIM-like plant model for PoC: simple tank and pump.

This module implements a TankPlant class that can be stepped by fixed dt.
It is independent of HELICS and Modbus; the HELICS federate will use it.
"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class TankPlant:
    level_m3: float = 10.0        # initial volume (m^3)
    capacity_m3: float = 20.0     # tank capacity
    pump_flow_m3_s: float = 1.0   # pump flow when running (m^3/s) for fast PoC trip
    leak_flow_m3_s: float = 0.001 # small leak outflow

    def step(self, pump_running: bool, dt: float = 1.0) -> float:
        """Advance plant state by dt seconds. Returns new level."""
        inflow = self.pump_flow_m3_s if pump_running else 0.0
        outflow = self.leak_flow_m3_s
        self.level_m3 += (inflow - outflow) * dt
        # clamp
        if self.level_m3 < 0:
            self.level_m3 = 0.0
        if self.level_m3 > self.capacity_m3:
            self.level_m3 = self.capacity_m3
        return self.level_m3

    def needs_trip(self) -> bool:
        """Simple rule: if level below 1 m^3 or above 95% capacity, trip."""
        if self.level_m3 < 1.0:
            return True
        if self.level_m3 > 0.95 * self.capacity_m3:
            return True
        return False


@dataclass
class GasPlant:
    pressure_psi: float = 100.0
    min_pressure_psi: float = 0.0
    max_pressure_psi: float = 150.0
    flow_rate_psi_s: float = 5.0
    leak_rate_psi_s: float = 0.1

    def step(self, valve_open: bool, dt: float = 1.0) -> float:
        """Advance gas pipeline pressure state."""
        delta = (-self.flow_rate_psi_s if valve_open else self.flow_rate_psi_s) - self.leak_rate_psi_s
        self.pressure_psi += delta * dt
        if self.pressure_psi < self.min_pressure_psi:
            self.pressure_psi = self.min_pressure_psi
        if self.pressure_psi > self.max_pressure_psi:
            self.pressure_psi = self.max_pressure_psi
        return self.pressure_psi

    def needs_trip(self) -> bool:
        """Trip if pressure falls below 20 PSI or exceeds 140 PSI."""
        return self.pressure_psi < 20.0 or self.pressure_psi > 140.0


@dataclass
class ElecPlant:
    """Modelo de frecuencia de subestación usando ecuación de swing simplificada.

    df/dt = (P_gen - P_load) / (2 * H * f0)

    H  = constante de inercia del generador (s) — típico 3-6 s en distribución
    f0 = frecuencia nominal (60 Hz)
    P_gen, P_load en pu sobre base de 1 MVA

    Con carga nominal (P_load = P_gen) la frecuencia es estable.
    Un trip de carga reduce P_load → frecuencia sube (sobre-velocidad).
    Un trip de generación reduce P_gen → frecuencia cae (bajo-velocidad).
    """
    frequency_hz: float = 60.0
    p_gen_pu: float = 1.0       # generación activa en pu
    p_load_pu: float = 1.0      # carga activa en pu (actualizable desde hospital)
    inertia_h: float = 4.0      # constante de inercia H (s)
    f0: float = 60.0            # frecuencia nominal
    f_min: float = 45.0         # límite inferior absoluto (protección)
    f_max: float = 65.0         # límite superior absoluto

    def step(self, generation_trip: bool, dt: float = 1.0) -> float:
        """Avanza la frecuencia un paso dt.

        generation_trip=True simula pérdida súbita de generación (P_gen → 0).
        La carga p_load_pu puede actualizarse externamente antes de llamar step()
        para modelar el efecto del hospital activando su UPS (reduce demanda de red).
        """
        p_gen = 0.0 if generation_trip else self.p_gen_pu
        df_dt = (p_gen - self.p_load_pu) / (2.0 * self.inertia_h)
        self.frequency_hz += df_dt * dt
        self.frequency_hz = max(self.f_min, min(self.f_max, self.frequency_hz))
        return self.frequency_hz

    def needs_trip(self) -> bool:
        """Protección de subfrecuencia (UFLS): trip si f < 57 Hz (estándar NERC)."""
        return self.frequency_hz < 57.0

