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
