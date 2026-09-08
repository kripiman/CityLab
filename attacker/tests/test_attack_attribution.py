#!/usr/bin/env python3
"""attacker/tests/test_attack_attribution.py — Pruebas unitarias para ataque Heatwave Incident Attribution"""
from __future__ import annotations

import unittest
from attacker.attack_grid_heatwave_attribution import GridHeatwaveAttributionAttack


class TestAttributionAttack(unittest.TestCase):

    def test_attribution_attack_execution(self) -> None:
        attacker = GridHeatwaveAttributionAttack()
        res = attacker.execute_hybrid_attack()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['cyber_disruption_injected'])


if __name__ == '__main__':
    unittest.main()
