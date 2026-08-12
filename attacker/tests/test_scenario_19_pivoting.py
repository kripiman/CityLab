#!/usr/bin/env python3
"""attacker/tests/test_scenario_19_pivoting.py — Test para Escenario 19"""
from __future__ import annotations

import unittest
from attacker.attack_multisector import TARGET_PLCS


class TestScenario19Pivoting(unittest.TestCase):

    def test_pivoting_target_matrix(self) -> None:
        self.assertIn('water', TARGET_PLCS)
        self.assertEqual(TARGET_PLCS['water'], '10.0.3.10')


if __name__ == '__main__':
    unittest.main()
