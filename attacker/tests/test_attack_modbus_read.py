#!/usr/bin/env python3
"""attacker/tests/test_attack_modbus_read.py — Test para Escenario 15"""
from __future__ import annotations

import unittest
from attacker.attack_modbus_read_only import ModbusReadOnly


class TestModbusRead(unittest.TestCase):

    def test_modbus_read_execution(self) -> None:
        reader = ModbusReadOnly()
        res = reader.run_read_telemetry()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertFalse(res['write_attempted'])


if __name__ == '__main__':
    unittest.main()
