#!/usr/bin/env python3
"""physical/water/desal_plant.py — Modelo físico de Planta Desalinizadora por Ósmosis Inversa (RO) (Fase 4)

Simula la física de una planta industrial de desalinización de agua de mar:
  - Captación de agua de mar (Seawater Intake: ~35,000 ppm TDS).
  - Bomba de alta presión (High-Pressure RO Pump): 55-70 bar.
  - Filtración por membrana de ósmosis inversa (Permeado < 500 ppm, Salmuera/Rechazo ~65,000 ppm).
  - Sistema de Recuperación de Energía (ERD - Energy Recovery Device: 90% eficiencia).
  - Tanque de almacenamiento de agua potable (% nivel).
"""
from __future__ import annotations

import logging
import threading
from typing import Dict, Any

LOGGER = logging.getLogger('desal_plant')


class DesalinationPlant:
    """Modelo físico determinista de Planta de Desalinización por Ósmosis Inversa."""

    def __init__(
        self,
        capacity_m3h: float = 500.0,
        tank_capacity_m3: float = 2000.0,
        intake_tds_ppm: float = 35000.0
    ) -> None:
        self.capacity_m3h = capacity_m3h
        self.tank_capacity_m3 = tank_capacity_m3
        self.intake_tds_ppm = intake_tds_ppm

        # RLock (reentrante): step() mantiene el cerrojo y llama a get_state(), que vuelve a
        # tomarlo. Con un Lock simple sería un autodeadlock permanente.
        self._lock = threading.RLock()
        self.hp_pump_on: bool = True
        self.intake_valve_open: bool = True
        self.tank_level_m3: float = 1200.0  # 60% nivel inicial
        self.permeate_tds_ppm: float = 280.0
        self.brine_tds_ppm: float = 67000.0
        self.power_kw: float = 650.0  # Consumo energético con ERD
        self.recovery_rate: float = 0.45  # 45% conversión a agua dulce

    def step(self, dt_seconds: float = 1.0, city_demand_m3h: float = 180.0) -> Dict[str, Any]:
        """Avanza la simulación física de la planta dt_seconds segundos."""
        with self._lock:
            if self.hp_pump_on and self.intake_valve_open:
                production_rate_m3h = self.capacity_m3h * self.recovery_rate
                self.power_kw = 650.0
                self.permeate_tds_ppm = 280.0
            else:
                production_rate_m3h = 0.0
                self.power_kw = 20.0  # Carga auxiliar mínima
                self.permeate_tds_ppm = 0.0

            # Balance hídrico en tanque de permeado
            net_flow_m3s = (production_rate_m3h - city_demand_m3h) / 3600.0
            self.tank_level_m3 = max(0.0, min(self.tank_capacity_m3, self.tank_level_m3 + net_flow_m3s * dt_seconds))

            return self.get_state()

    def set_hp_pump(self, state: bool) -> None:
        with self._lock:
            self.hp_pump_on = state
            LOGGER.info("[DESAL] Bomba de alta presión RO: %s", "ON" if state else "TRIPPED/OFF")

    def set_intake_valve(self, state: bool) -> None:
        with self._lock:
            self.intake_valve_open = state
            LOGGER.info("[DESAL] Válvula de captación: %s", "ABIERTA" if state else "CERRADA")

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            tank_pct = (self.tank_level_m3 / self.tank_capacity_m3) * 100.0
            return {
                'hp_pump_on': self.hp_pump_on,
                'intake_valve_open': self.intake_valve_open,
                'tank_level_m3': self.tank_level_m3,
                'tank_level_pct': tank_pct,
                'permeate_tds_ppm': self.permeate_tds_ppm,
                'brine_tds_ppm': self.brine_tds_ppm,
                'power_kw': self.power_kw,
                'recovery_rate': self.recovery_rate
            }
