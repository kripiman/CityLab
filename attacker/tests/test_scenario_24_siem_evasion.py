#!/usr/bin/env python3
"""attacker/tests/test_scenario_24_siem_evasion.py — Test para Escenario 24"""
from __future__ import annotations

import unittest
from attacker.attack_siem_rule_evasion import SiemRuleEvasion


class TestScenario24SiemEvasion(unittest.TestCase):

    def test_siem_evasion_execution(self) -> None:
        evasion = SiemRuleEvasion()
        res = evasion.run_multi_ip_evasion()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['evasion_successful'])


if __name__ == '__main__':
    unittest.main()
