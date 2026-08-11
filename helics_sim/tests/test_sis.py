#!/usr/bin/env python3
"""helics_sim/tests/test_sis.py — Pruebas unitarias para Safety Instrumented System SIS (Fase 7)"""
from __future__ import annotations

import unittest
from helics_sim.fed_sis import SafetyInstrumentedLogic, SafetyInterlockLimits


class TestSafetyInstrumentedSystem(unittest.TestCase):

    def setUp(self) -> None:
        self.logic = SafetyInstrumentedLogic()

    def test_normal_operation(self) -> None:
        normal_state = {'water_t1_level': 10.0, 'gas_pressure': 145.0, 'grid_freq': 60.0}
        cmd, tripped, reason = self.logic.enforce_safety_override(bpcs_command=True, process_data=normal_state)
        
        self.assertTrue(cmd)
        self.assertFalse(tripped)
        self.assertEqual(reason, 'NORMAL')

    def test_water_tank_overfill_trip(self) -> None:
        overfill_state = {'water_t1_level': 19.5, 'gas_pressure': 145.0, 'grid_freq': 60.0}
        cmd, tripped, reason = self.logic.enforce_safety_override(bpcs_command=True, process_data=overfill_state)
        
        self.assertFalse(cmd)  # BPCS command overridden to False
        self.assertTrue(tripped)
        self.assertIn('sobre-nivel', reason)

    def test_gas_overpressure_trip(self) -> None:
        high_press_state = {'water_t1_level': 10.0, 'gas_pressure': 195.0, 'grid_freq': 60.0}
        cmd, tripped, reason = self.logic.enforce_safety_override(bpcs_command=True, process_data=high_press_state)
        
        self.assertFalse(cmd)
        self.assertTrue(tripped)
        self.assertIn('Sobre-presión', reason)

    def test_electrical_overfrequency_trip(self) -> None:
        high_freq_state = {'water_t1_level': 10.0, 'gas_pressure': 145.0, 'grid_freq': 64.0}
        cmd, tripped, reason = self.logic.enforce_safety_override(bpcs_command=True, process_data=high_freq_state)
        
        self.assertFalse(cmd)
        self.assertTrue(tripped)
        self.assertIn('Sobre-frecuencia', reason)


if __name__ == '__main__':
    unittest.main()
