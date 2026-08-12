#!/usr/bin/env python3
"""attacker/tests/test_attack_dosing.py — Pruebas unitarias para ataque Chemical Dosing"""
from __future__ import annotations

import unittest
from attacker.attack_chemical_dosing import ChemicalDosingAttack


class TestChemicalDosingAttack(unittest.TestCase):

    def test_dosing_attack_execution(self) -> None:
        attacker = ChemicalDosingAttack()
        res = attacker.execute_overdosing_attack(target_ppm=8.5)
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['contamination_achieved'])


if __name__ == '__main__':
    unittest.main()
