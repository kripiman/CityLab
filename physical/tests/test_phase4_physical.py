#!/usr/bin/env python3
"""physical/tests/test_phase4_physical.py — Pruebas unitarias para modelos físicos de Fase 4 (Desal & Lighting)"""

import unittest
from physical.water.desal_plant import DesalinationPlant
from physical.elec.smart_lighting import SmartLightingSystem


class TestPhase4PhysicalModels(unittest.TestCase):
    def setUp(self) -> None:
        self.desal = DesalinationPlant()
        self.lighting = SmartLightingSystem()

    def test_desalination_plant_normal_operation(self) -> None:
        state = self.desal.step(dt_seconds=10.0, city_demand_m3h=180.0)
        self.assertTrue(state['hp_pump_on'])
        self.assertTrue(state['intake_valve_open'])
        self.assertEqual(state['power_kw'], 650.0)
        self.assertAlmostEqual(state['permeate_tds_ppm'], 280.0, places=1)
        self.assertGreater(state['tank_level_m3'], 1200.0)

    def test_desalination_plant_hp_pump_trip(self) -> None:
        self.desal.set_hp_pump(False)
        state = self.desal.step(dt_seconds=10.0, city_demand_m3h=180.0)
        self.assertFalse(state['hp_pump_on'])
        self.assertEqual(state['power_kw'], 20.0)
        self.assertEqual(state['permeate_tds_ppm'], 0.0)
        # Nivel cae por demanda de ciudad sin producción
        self.assertLess(state['tank_level_m3'], 1200.0)

    def test_smart_lighting_autocontrol_day_night(self) -> None:
        # Noche (50 lux) -> 100% dimmer
        state_night = self.lighting.step(dt_seconds=1.0, ambient_lux=10.0)
        self.assertEqual(state_night['dimming_pct'], 100.0)
        self.assertAlmostEqual(state_night['active_power_kw'], 74.7, places=1)

        # Día (500 lux) -> 0% dimmer (apagado)
        state_day = self.lighting.step(dt_seconds=1.0, ambient_lux=500.0)
        self.assertEqual(state_day['dimming_pct'], 0.0)
        self.assertEqual(state_day['active_power_kw'], 0.0)

    def test_smart_lighting_manual_override(self) -> None:
        self.lighting.set_dimming(30.0, override=True)
        state = self.lighting.step(dt_seconds=1.0, ambient_lux=10.0)
        self.assertEqual(state['dimming_pct'], 30.0)
        self.assertTrue(state['manual_override'])
        self.assertAlmostEqual(state['active_power_kw'], 22.41, places=1)


if __name__ == '__main__':
    unittest.main()
