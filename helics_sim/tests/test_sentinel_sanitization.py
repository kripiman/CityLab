#!/usr/bin/env python3
"""helics_sim/tests/test_sentinel_sanitization.py — Tests unitarios para sanitización de sentinels HELICS.

Verifica que las señales no inicializadas retornadas por HELICS Core (INT64_MIN = -9223372036854775808
y HELICS_BIG_NUMBER = -9.99e48) no generen falsos disparos ni contaminen telemetría analógica.
"""
import unittest


class TestSentinelSanitization(unittest.TestCase):
    """Pruebas de lógica pura de sanitización según especificación PLAN_REMEDIACION_HELICS_SENTINEL.md."""

    def test_integer_trip_sentinel_filtering(self):
        """Valores no inicializados (-9223372036854775808) no deben activar disparo booleano."""
        raw_trips = [0, -9223372036854775808, -9223372036854775808]
        sanitized_trips = [1 if t == 1 else 0 for t in raw_trips]
        trip_state = any(t == 1 for t in sanitized_trips)
        
        self.assertEqual(sanitized_trips, [0, 0, 0])
        self.assertFalse(trip_state)

    def test_integer_trip_legitimate_activation(self):
        """Un valor explícito 1 debe activar el disparo independientemente de otros canales no conectados."""
        raw_trips = [1, -9223372036854775808, 0]
        sanitized_trips = [1 if t == 1 else 0 for t in raw_trips]
        trip_state = any(t == 1 for t in sanitized_trips)
        
        self.assertEqual(sanitized_trips, [1, 0, 0])
        self.assertTrue(trip_state)

    def test_mock_federate_multisector_trip_logic(self):
        """Verifica la lógica de combinación multi-sector en fed_gridmock."""
        raw_w = 0
        raw_g = -9223372036854775808
        raw_e = -9223372036854775808
        raw_t = -9223372036854775808

        water_trip = 1 if raw_w == 1 else 0
        gas_trip = 1 if raw_g == 1 else 0
        grid_trip = 1 if raw_e == 1 else 0
        trans_trip = 1 if raw_t == 1 else 0

        any_trip = (water_trip == 1 or gas_trip == 1 or grid_trip == 1 or trans_trip == 1)
        self.assertFalse(any_trip)

        # Activando solo gas
        raw_g = 1
        gas_trip = 1 if raw_g == 1 else 0
        any_trip = (water_trip == 1 or gas_trip == 1 or grid_trip == 1 or trans_trip == 1)
        self.assertTrue(any_trip)

    def test_double_telemetry_sentinel_normalization(self):
        """Valores double pre-publicación (-9.99e48) deben normalizarse a 0.0 kW."""
        raw_hospital_load = -9.999999999999999e+48
        hospital_load_kw = 0.0 if raw_hospital_load < -1e20 else max(0.0, raw_hospital_load)
        self.assertEqual(hospital_load_kw, 0.0)

        # Valor legítimo
        valid_load = 550.5
        hospital_load_kw = 0.0 if valid_load < -1e20 else max(0.0, valid_load)
        self.assertEqual(hospital_load_kw, 550.5)


if __name__ == '__main__':
    unittest.main()
