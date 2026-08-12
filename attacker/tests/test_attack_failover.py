#!/usr/bin/env python3
"""attacker/tests/test_attack_failover.py — Pruebas unitarias para ataque DCS Failover"""
from __future__ import annotations

import unittest
from attacker.attack_dcs_failover import FailoverExploitAttack


class TestFailoverAttack(unittest.TestCase):

    def test_dcs_failover_attack_execution(self) -> None:
        attacker = FailoverExploitAttack()
        res = attacker.execute_failover_race_attack()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['exploited_window'])


if __name__ == '__main__':
    unittest.main()
