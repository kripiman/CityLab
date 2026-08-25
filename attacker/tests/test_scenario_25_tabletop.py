#!/usr/bin/env python3
"""attacker/tests/test_scenario_25_tabletop.py — Test para Escenario 25"""
from __future__ import annotations

import unittest
from attacker.attack_ransomware_tabletop import RansomwareTabletop


class TestScenario25Tabletop(unittest.TestCase):

    def test_tabletop_execution(self) -> None:
        tt = RansomwareTabletop()
        res = tt.run_crisis_simulation()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['tabletop_completed'])
        self.assertIn('decisions', res)
        self.assertTrue(res['decisions']['isolate_ot'])
        self.assertTrue(res['decisions']['refuse_ransom'])


if __name__ == '__main__':
    unittest.main()
