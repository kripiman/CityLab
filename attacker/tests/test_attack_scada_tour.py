#!/usr/bin/env python3
"""attacker/tests/test_attack_scada_tour.py — Test para Escenario 17"""
from __future__ import annotations

import unittest
from attacker.attack_scada_tour import ScadaTour


class TestScadaTour(unittest.TestCase):

    def test_scada_tour_execution(self) -> None:
        tour = ScadaTour()
        res = tour.run_scada_exploration()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['overview_retrieved'])


if __name__ == '__main__':
    unittest.main()
