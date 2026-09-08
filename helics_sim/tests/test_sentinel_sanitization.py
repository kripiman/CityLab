#!/usr/bin/env python3
"""helics_sim/tests/test_sentinel_sanitization.py — Tests unitarios para sanitización de sentinels HELICS.

Verifica directamente contra el SUT (helics_sim/sentinel_utils.py) que las señales no inicializadas
retornadas por HELICS Core (INT64_MIN = -9223372036854775808 y HELICS_BIG_NUMBER = -9.99e48)
no generen falsos disparos ni contaminen telemetría analógica en producción.
"""
import unittest

from helics_sim.sentinel_utils import sanitize_trip_signal, sanitize_telemetry_double


class TestSentinelSanitization(unittest.TestCase):
    """Pruebas directas de las funciones del SUT (helics_sim.sentinel_utils)."""

    def test_integer_trip_sentinel_filtering(self):
        """Valores no inicializados (-9223372036854775808) deben ser normalizados a 0 por el SUT."""
        raw_trips = [0, -9223372036854775808, -9223372036854775808]
        sanitized_trips = [sanitize_trip_signal(t) for t in raw_trips]
        trip_state = any(t == 1 for t in sanitized_trips)
        
        self.assertEqual(sanitized_trips, [0, 0, 0])
        self.assertFalse(trip_state)

    def test_integer_trip_legitimate_activation(self):
        """Un valor explícito 1 debe ser preservado como 1 independientemente de otros canales centinela."""
        raw_trips = [1, -9223372036854775808, 0]
        sanitized_trips = [sanitize_trip_signal(t) for t in raw_trips]
        trip_state = any(t == 1 for t in sanitized_trips)
        
        self.assertEqual(sanitized_trips, [1, 0, 0])
        self.assertTrue(trip_state)

    def test_mock_federate_multisector_trip_logic(self):
        """Verifica la interacción de sanitización multi-sector con las funciones del SUT."""
        raw_w = 0
        raw_g = -9223372036854775808
        raw_e = -9223372036854775808
        raw_t = -9223372036854775808

        water_trip = sanitize_trip_signal(raw_w)
        gas_trip = sanitize_trip_signal(raw_g)
        grid_trip = sanitize_trip_signal(raw_e)
        trans_trip = sanitize_trip_signal(raw_t)

        any_trip = (water_trip == 1 or gas_trip == 1 or grid_trip == 1 or trans_trip == 1)
        self.assertFalse(any_trip)

        # Activando solo gas con valor legítimo
        raw_g = 1
        gas_trip = sanitize_trip_signal(raw_g)
        any_trip = (water_trip == 1 or gas_trip == 1 or grid_trip == 1 or trans_trip == 1)
        self.assertTrue(any_trip)

    def test_double_telemetry_sentinel_normalization(self):
        """Valores double pre-publicación (-9.99e48) deben normalizarse al default configurado."""
        raw_hospital_load = -9.999999999999999e+48
        hospital_load_kw = sanitize_telemetry_double(raw_hospital_load, default=0.0)
        self.assertEqual(hospital_load_kw, 0.0)

        # Valor legítimo
        valid_load = 550.5
        hospital_load_kw = sanitize_telemetry_double(valid_load, default=0.0)
        self.assertEqual(hospital_load_kw, 550.5)

    def test_double_telemetry_out_of_bounds_frequency(self):
        """Valores double con límite superior configurado deben normalizarse ante sobrepaso."""
        raw_freq_sentinel = 100.0
        e_val = sanitize_telemetry_double(raw_freq_sentinel, default=60.0, max_val=70.0)
        self.assertEqual(e_val, 60.0)

        raw_freq_normal = 59.98
        e_val = sanitize_telemetry_double(raw_freq_normal, default=60.0, max_val=70.0)
        self.assertEqual(e_val, 59.98)


if __name__ == '__main__':
    unittest.main()
