#!/usr/bin/env python3
"""physical/elec/smart_lighting.py — Modelo físico de Alumbrado Público Inteligente (Fase 4)

Simula la red de alumbrado LED urbano conectado:
  - 500 luminarias LED de 150W en 5 circuitos de distribución.
  - Sensor de fotocélula de luz ambiental (ambient_lux: 0 - 100,000 lux).
  - Regulación de intensidad dimmer inteligente (0% a 100%).
  - Cálculo de potencia activa total (`kW`) y detección de lámparas defectuosas.
"""
from __future__ import annotations

import logging
import math
import threading
from typing import Dict, Any

LOGGER = logging.getLogger('smart_lighting')


class SmartLightingSystem:
    """Modelo físico determinista de Red de Alumbrado Público Inteligente."""

    def __init__(self, total_fixtures: int = 500, nominal_fixture_watt: float = 150.0) -> None:
        self.total_fixtures = total_fixtures
        self.nominal_fixture_watt = nominal_fixture_watt

        # RLock (reentrante) y no Lock: `step()` mantiene el cerrojo y llama a `get_state()`,
        # que vuelve a tomarlo. Con un Lock simple eso es un autodeadlock permanente.
        self._lock = threading.RLock()
        self.ambient_lux: float = 50.0  # Atardecer/Noche inicial
        self.manual_override: bool = False
        self.dimming_pct: float = 100.0  # 100% potencia nominal
        self.failed_fixtures: int = 2
        self.active_power_kw: float = 0.0

    def step(self, dt_seconds: float = 1.0, ambient_lux: float = 50.0) -> Dict[str, Any]:
        """Avanza el modelo de alumbrado ajustando fotocélulas o dimmer."""
        with self._lock:
            dt_seconds = 1.0 if (math.isnan(dt_seconds) or math.isinf(dt_seconds) or dt_seconds < 0) else dt_seconds
            ambient_lux = 50.0 if (math.isnan(ambient_lux) or math.isinf(ambient_lux)) else max(0.0, float(ambient_lux))
            self.ambient_lux = ambient_lux

            # Control automático por fotocélula si no hay override manual
            if not self.manual_override:
                if self.ambient_lux > 300.0:  # Día pleno
                    self.dimming_pct = 0.0
                elif self.ambient_lux > 50.0:  # Crepúsculo
                    self.dimming_pct = 50.0
                else:  # Noche cerrada
                    self.dimming_pct = 100.0

            # Cálculo de potencia total consumida
            working_fixtures = max(0, self.total_fixtures - self.failed_fixtures)
            power_per_fixture_w = self.nominal_fixture_watt * (self.dimming_pct / 100.0)
            self.active_power_kw = (working_fixtures * power_per_fixture_w) / 1000.0

            return self.get_state()

    def set_dimming(self, dimming_pct: float, override: bool = True) -> None:
        with self._lock:
            self.dimming_pct = max(0.0, min(100.0, dimming_pct))
            self.manual_override = override
            LOGGER.info("[LIGHTING] Regulación dimmer ajustada a %.1f%% (Override=%s)", self.dimming_pct, override)

    def set_manual_override(self, state: bool) -> None:
        with self._lock:
            self.manual_override = state

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'total_fixtures': self.total_fixtures,
                'failed_fixtures': self.failed_fixtures,
                'ambient_lux': self.ambient_lux,
                'dimming_pct': self.dimming_pct,
                'manual_override': self.manual_override,
                'active_power_kw': self.active_power_kw
            }
