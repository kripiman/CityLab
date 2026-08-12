#!/usr/bin/env python3
"""physical/hospital/hospital_load.py — Modelo Físico de Carga Crítica Hospitalaria

Simula el suministro de energía ininterrumpida (UPS / Generadores diésel de emergencia)
para la unidad de cuidados intensivos (UCI).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

LOGGER = logging.getLogger('hospital_load')


@dataclass
class HospitalPowerParams:
    critical_load_kw: float = 250.0
    ups_battery_capacity_kwh: float = 100.0
    generator_capacity_kw: float = 300.0


class HospitalPowerSystem:
    """Modelo físico de sistema de respaldo crítico hospitalario."""

    def __init__(self, params: HospitalPowerParams = HospitalPowerParams()) -> None:
        self.params = params
        self.grid_available = True
        self.ups_soc_percent = 100.0
        self.generator_running = False

    def step(self, dt_s: float = 1.0) -> float:
        """Avanza la simulación del sistema eléctrico hospitalario dt_s segundos."""
        if not self.grid_available:
            if not self.generator_running:
                # Descarga de UPS mientras entra el generador diésel
                drain_rate = (self.params.critical_load_kw / self.params.ups_battery_capacity_kwh) * (dt_s / 3600.0) * 100.0
                self.ups_soc_percent = max(0.0, self.ups_soc_percent - drain_rate)
            else:
                # Generador diésel activo recarga UPS gradualmente
                self.ups_soc_percent = min(100.0, self.ups_soc_percent + 0.1 * dt_s)
        else:
            self.ups_soc_percent = 100.0
        return self.ups_soc_percent
