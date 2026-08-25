#!/usr/bin/env python3
"""attacker/tests/test_attack_multisector.py — Test para Ataque Multi-Sectorial Modbus"""
from __future__ import annotations

import unittest
from attacker.attack_multisector import execute_cascading_attack, main as multisector_main
from plc.tests._emulator_harness import running_modbus_server


class TestAttackMultisector(unittest.TestCase):

    def test_multisector_attack_live_socket_start(self) -> None:
        """Verifica que el ataque multi-sectorial ejecute writes reales vía Modbus/TCP."""
        with running_modbus_server(port=15020, plant_type='water') as (server, context):
            self.assertEqual(context[0x00].getValues(1, 0, 1), [0])

            res = execute_cascading_attack(
                target_sector='water',
                mode='start',
                targets_override={'water': ('127.0.0.1', 15020)},
            )

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertEqual(res['live_targets_count'], 1)
            self.assertTrue(res['sector_results']['water']['success'])
            # Mutación observable en el datastore del emulador
            self.assertEqual(context[0x00].getValues(1, 0, 1), [1])

    def test_multisector_attack_fallback(self) -> None:
        """Verifica que si ningún objetivo está disponible caiga en TABLETOP_FALLBACK."""
        res = execute_cascading_attack(
            target_sector='gas',
            mode='fault',
            targets_override={'gas': ('127.0.0.1', 59997)},
        )
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')
        self.assertEqual(res['live_targets_count'], 0)
        self.assertFalse(res['sector_results']['gas']['success'])

    def test_multisector_cli(self) -> None:
        """Verifica la ejecución CLI en modo fallback sin romper."""
        rc = multisector_main(['--sector', 'water', '--mode', 'start'])
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
