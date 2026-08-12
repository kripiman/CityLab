#!/usr/bin/env python3
"""attacker/tests/test_scenario_28_blind.py — Test para Escenario 28"""
from __future__ import annotations

import unittest
from attacker.attack_blind_randomized_env import BlindRandomizedEnv


class TestScenario28Blind(unittest.TestCase):

    def test_blind_env_execution(self) -> None:
        env = BlindRandomizedEnv()
        res = env.run_randomized_scenario()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertGreater(res['randomized_port'], 0)


if __name__ == '__main__':
    unittest.main()
