#!/usr/bin/env python3
"""attacker/tests/test_scenario_23_sdn.py — Test para Escenario 23"""
from __future__ import annotations

import unittest
from attacker.attack_live_sdn_defense import LiveSdnDefense


class TestScenario23Sdn(unittest.TestCase):

    def test_sdn_defense_execution(self) -> None:
        sdn = LiveSdnDefense()
        res = sdn.run_sdn_mitigation()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['sdn_rule_applied'])


if __name__ == '__main__':
    unittest.main()
