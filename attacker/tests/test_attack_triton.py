#!/usr/bin/env python3
"""attacker/tests/test_attack_triton.py — Pruebas unitarias y E2E para ataque Triton Low-and-Slow"""
from __future__ import annotations

import unittest
from attacker.attack_triton_low_slow import TritonLowSlowAttack, main as triton_main
from plc.tests._emulator_harness import running_modbus_server


class TestTritonAttack(unittest.TestCase):

    _modbus_port = 15020

    def test_triton_stealth_socket_e2e(self) -> None:
        """Verifica manipulación de proceso vía Modbus manteniendo valores bajo umbral SIS (Sigilo)."""
        with running_modbus_server(port=self._modbus_port, plant_type='water') as (server, context):
            attacker = TritonLowSlowAttack(target_sector='water', port=self._modbus_port)
            res = attacker.execute_stealth_manipulation(cycles=2, port=self._modbus_port, force_trip=False)

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertEqual(res['observed_val'], 18.8)
            self.assertFalse(res['sis_tripped'])
            self.assertTrue(res['stealth_maintained'])

            # Verificación directa en el datastore del emulador PLC
            stored_val = context[0x00].getValues(3, 20, 1)
            self.assertEqual(stored_val, [188])

    def test_triton_trip_negative_socket_e2e(self) -> None:
        """Manipulación sobre el umbral de seguridad provoca disparo inmediato del SIS (Pérdida de sigilo)."""
        with running_modbus_server(port=self._modbus_port, plant_type='water') as (server, context):
            attacker = TritonLowSlowAttack(target_sector='water', port=self._modbus_port)
            res = attacker.execute_stealth_manipulation(cycles=2, port=self._modbus_port, force_trip=True)

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertEqual(res['observed_val'], 21.0)
            self.assertTrue(res['sis_tripped'])
            self.assertFalse(res['stealth_maintained'])

            stored_val = context[0x00].getValues(3, 20, 1)
            self.assertEqual(stored_val, [210])

    def test_triton_tabletop_fallback(self) -> None:
        """Si el PLC no está activo, el ataque activa el modo TABLETOP_FALLBACK documentado."""
        attacker = TritonLowSlowAttack(target_sector='water', port=59998)
        res = attacker.execute_stealth_manipulation(cycles=2, port=59998, force_trip=False)

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')
        self.assertTrue(res['stealth_maintained'])

    def test_triton_main_cli(self) -> None:
        """El entrypoint CLI main() ejecuta la manipulación Triton sobre el puerto de test sin errores."""
        with running_modbus_server(port=self._modbus_port, plant_type='water'):
            ret = triton_main(['--port', str(self._modbus_port), '--sector', 'water', '--cycles', '2'])
            self.assertEqual(ret, 0)


if __name__ == '__main__':
    unittest.main()
