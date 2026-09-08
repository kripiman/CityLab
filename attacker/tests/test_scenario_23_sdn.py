#!/usr/bin/env python3
"""attacker/tests/test_scenario_23_sdn.py — Test para Escenario 23"""
from __future__ import annotations

import unittest
from unittest.mock import patch
from attacker.attack_live_sdn_defense import LiveSdnDefense


class TestScenario23Sdn(unittest.TestCase):

    @patch('attacker.attack_live_sdn_defense.apply_sdn_flow_rules', return_value=True)
    def test_sdn_defense_execution_success(self, mock_apply) -> None:
        sdn = LiveSdnDefense()
        res = sdn.execute_sdn_mitigation()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['flow_rules_applied'])

    @patch('attacker.attack_live_sdn_defense.apply_sdn_flow_rules', return_value=False)
    def test_sdn_defense_execution_no_ovs(self, mock_apply) -> None:
        sdn = LiveSdnDefense()
        res = sdn.execute_sdn_mitigation()
        self.assertEqual(res['status'], 'SKIPPED_NO_OVS')
        self.assertFalse(res['flow_rules_applied'])


if __name__ == '__main__':
    unittest.main()
