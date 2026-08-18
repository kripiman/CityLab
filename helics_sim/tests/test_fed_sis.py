#!/usr/bin/env python3
"""helics_sim/tests/test_fed_sis.py — Unit tests for Phase 7 SIS federate."""

import os
import unittest
from helics_sim.fed_sis import SafetyInstrumentedLogic, SafetyInterlockLimits, main


class TestSisFederate(unittest.TestCase):

    def setUp(self) -> None:
        self.logic = SafetyInstrumentedLogic()

    def tearDown(self) -> None:
        if 'HELICS_STANDALONE' in os.environ:
            del os.environ['HELICS_STANDALONE']

    def test_normal_process_data_no_trip(self) -> None:
        normal_data = {'water_t1_level': 10.0, 'gas_pressure': 145.0, 'grid_freq': 60.0}
        must_trip, reason = self.logic.evaluate_safety_state(normal_data)
        self.assertFalse(must_trip)
        self.assertEqual(reason, '')

        cmd, tripped, reason = self.logic.enforce_safety_override(bpcs_command=True, process_data=normal_data)
        self.assertTrue(cmd)
        self.assertFalse(tripped)
        self.assertEqual(reason, 'NORMAL')

    def test_over_tank_level_interlock(self) -> None:
        high_water = {'water_t1_level': 19.5, 'gas_pressure': 145.0, 'grid_freq': 60.0}
        must_trip, reason = self.logic.evaluate_safety_state(high_water)
        self.assertTrue(must_trip)
        self.assertIn('sobre-nivel peligroso', reason)

        cmd, tripped, reason = self.logic.enforce_safety_override(bpcs_command=True, process_data=high_water)
        self.assertFalse(cmd)
        self.assertTrue(tripped)

    def test_low_tank_level_interlock(self) -> None:
        low_water = {'water_t1_level': 0.2, 'gas_pressure': 145.0, 'grid_freq': 60.0}
        must_trip, reason = self.logic.evaluate_safety_state(low_water)
        self.assertTrue(must_trip)
        self.assertIn('bajo-nivel crítico', reason)

    def test_over_gas_pressure_interlock(self) -> None:
        high_gas = {'water_t1_level': 10.0, 'gas_pressure': 185.0, 'grid_freq': 60.0}
        must_trip, reason = self.logic.evaluate_safety_state(high_gas)
        self.assertTrue(must_trip)
        self.assertIn('Sobre-presión crítica', reason)

    def test_over_grid_freq_interlock(self) -> None:
        high_freq = {'water_t1_level': 10.0, 'gas_pressure': 145.0, 'grid_freq': 63.5}
        must_trip, reason = self.logic.evaluate_safety_state(high_freq)
        self.assertTrue(must_trip)
        self.assertIn('Sobre-frecuencia eléctrica crítica', reason)

    def test_standalone_execution(self) -> None:
        os.environ['HELICS_STANDALONE'] = '1'
        ret = main()
        self.assertEqual(ret, 0)


if __name__ == '__main__':
    unittest.main()
