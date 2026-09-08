#!/usr/bin/env python3
"""attacker/tests/test_attack_dosing.py — Pruebas unitarias y E2E para ataque Chemical Dosing"""
from __future__ import annotations

import unittest
from attacker.attack_chemical_dosing import ChemicalDosingAttack, main as dosing_main
from plc.tests._emulator_harness import running_modbus_server


class TestChemicalDosingAttack(unittest.TestCase):

    _modbus_port = 15020

    def test_dosing_attack_socket_e2e_overdosing(self) -> None:
        """Ataque real vía Modbus/TCP muta el Holding Register 10 en el PLC y confirma contaminación."""
        with running_modbus_server(port=self._modbus_port, plant_type='water') as (server, context):
            attacker = ChemicalDosingAttack(host='127.0.0.1', port=self._modbus_port)
            res = attacker.execute_overdosing_attack(target_ppm=8.5)

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertEqual(res['baseline_ppm'], 1.5)
            self.assertEqual(res['altered_ppm'], 8.5)
            self.assertTrue(res['contamination_achieved'])

            # Verificación directa sobre el datastore del emulador PLC
            stored_val = context[0x00].getValues(3, 10, 1)
            self.assertEqual(stored_val, [85])

    def test_dosing_attack_socket_e2e_safe_negative(self) -> None:
        """Dosificación dentro de rango seguro muta el registro pero no marca contaminación."""
        with running_modbus_server(port=self._modbus_port, plant_type='water') as (server, context):
            attacker = ChemicalDosingAttack(host='127.0.0.1', port=self._modbus_port)
            res = attacker.execute_overdosing_attack(target_ppm=2.0)

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertEqual(res['altered_ppm'], 2.0)
            self.assertFalse(res['contamination_achieved'])

            stored_val = context[0x00].getValues(3, 10, 1)
            self.assertEqual(stored_val, [20])

    def test_dosing_attack_tabletop_fallback(self) -> None:
        """Si el PLC no está disponible, el ataque activa el modo TABLETOP_FALLBACK documentado."""
        attacker = ChemicalDosingAttack(host='127.0.0.1', port=59998)
        res = attacker.execute_overdosing_attack(target_ppm=8.5)

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')
        self.assertEqual(res['altered_ppm'], 8.5)
        self.assertTrue(res['contamination_achieved'])

    def test_dosing_attack_main_cli(self) -> None:
        """El entrypoint CLI main() ejecuta la sobre-dosificación contra el puerto de test sin errores."""
        with running_modbus_server(port=self._modbus_port, plant_type='water'):
            ret = dosing_main(['--port', str(self._modbus_port), '--ppm', '7.5'])
            self.assertEqual(ret, 0)


if __name__ == '__main__':
    unittest.main()
