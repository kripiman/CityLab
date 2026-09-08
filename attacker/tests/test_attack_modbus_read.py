#!/usr/bin/env python3
"""attacker/tests/test_attack_modbus_read.py — Test para Escenario 15: Lectura Pasiva Modbus"""
from __future__ import annotations

import unittest
from attacker.attack_modbus_read_only import ModbusReadOnly, main as read_main
from plc.tests._emulator_harness import running_modbus_server


class TestModbusRead(unittest.TestCase):

    def test_modbus_read_live_socket(self) -> None:
        """Verifica que la lectura pasiva lea correctamente valores reales del datastore del emulador."""
        with running_modbus_server(port=15020, plant_type='water') as (server, context):
            # Sembrar valores específicos en el datastore del emulador
            context[0x00].setValues(1, 0, [1, 0, 1, 0])
            context[0x00].setValues(3, 10, [85])
            context[0x00].setValues(3, 20, [188])

            reader = ModbusReadOnly()
            res = reader.run_read_telemetry(host='127.0.0.1', port=15020)

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertFalse(res['write_attempted'])
            self.assertEqual(res['coils_read'][:4], (1, 0, 1, 0))
            self.assertEqual(res['holding_registers_read'][10], 85)
            self.assertEqual(res['holding_registers_read'][20], 188)

    def test_modbus_read_fallback(self) -> None:
        """Verifica que ante un host no alcanzable caiga en TABLETOP_FALLBACK."""
        reader = ModbusReadOnly()
        res = reader.run_read_telemetry(host='127.0.0.1', port=59997, timeout=0.2)
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')
        self.assertFalse(res['write_attempted'])

    def test_modbus_read_cli(self) -> None:
        """Verifica ejecución de la CLI."""
        with running_modbus_server(port=15020, plant_type='water'):
            rc = read_main(['--host', '127.0.0.1', '--port', '15020'])
            self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
