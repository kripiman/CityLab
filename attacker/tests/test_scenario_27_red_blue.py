#!/usr/bin/env python3
"""attacker/tests/test_scenario_27_red_blue.py — Test para Escenario 27"""
from __future__ import annotations

import unittest
from attacker.attack_red_vs_blue_match import RedVsBlueMatch


class TestScenario27RedBlue(unittest.TestCase):

    def test_red_blue_match_execution(self) -> None:
        rvb = RedVsBlueMatch()
        res = rvb.run_adjudicated_match()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['match_completed'])


if __name__ == '__main__':
    unittest.main()
