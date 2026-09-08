#!/usr/bin/env python3
"""attacker/tests/test_scenario_18_modbus_write.py — Test para Escenario 18: Modbus Write Injection"""
from __future__ import annotations

import unittest
from attacker.attack_modbus import run_modbus_attack, main as attack_main
from plc.tests._emulator_harness import running_modbus_server


class TestScenario18ModbusWrite(unittest.TestCase):

    def test_modbus_start_live_socket_mutates_coil(self) -> None:
        """Verifica que el ataque force_start active Coil 0 en el datastore del emulador."""
        with running_modbus_server(port=15020, plant_type='water') as (server, context):
            # Estado inicial Coil 0 es 0
            self.assertEqual(context[0x00].getValues(1, 0, 1), [0])

            res = run_modbus_attack(host='127.0.0.1', port=15020, mode='start')
            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertEqual(res['attack_mode'], 'start')

            # Mutación observable en el datastore real del emulador
            self.assertEqual(context[0x00].getValues(1, 0, 1), [1])

    def test_modbus_stop_live_socket_mutates_coil(self) -> None:
        """Verifica que el ataque force_stop active Coil 1 en el datastore del emulador."""
        with running_modbus_server(port=15020, plant_type='water') as (server, context):
            self.assertEqual(context[0x00].getValues(1, 1, 1), [0])

            res = run_modbus_attack(host='127.0.0.1', port=15020, mode='stop')
            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertEqual(res['attack_mode'], 'stop')

            # Mutación observable en el datastore real del emulador
            self.assertEqual(context[0x00].getValues(1, 1, 1), [1])

    def test_modbus_fault_live_socket(self) -> None:
        """Verifica que el ataque fault active START y STOP vía socket real."""
        with running_modbus_server(port=15020, plant_type='water') as (server, context):
            res = run_modbus_attack(host='127.0.0.1', port=15020, mode='fault')
            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')

    def test_modbus_unreachable_fallback(self) -> None:
        """Verifica que ante un host no disponible el ataque caiga en TABLETOP_FALLBACK."""
        res = run_modbus_attack(host='127.0.0.1', port=59997, mode='start', timeout=0.2)
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')

    def test_modbus_cli_execution(self) -> None:
        """Verifica ejecución por CLI."""
        with running_modbus_server(port=15020, plant_type='water'):
            rc = attack_main(['--host', '127.0.0.1', '--port', '15020', '--mode', 'start'])
            self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
