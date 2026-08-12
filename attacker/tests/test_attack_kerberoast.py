#!/usr/bin/env python3
"""attacker/tests/test_attack_kerberoast.py — Pruebas unitarias para ataque Kerberoasting"""
from __future__ import annotations

import unittest
from attacker.attack_kerberoast_ad import KerberoastAttack


class TestKerberoastAttack(unittest.TestCase):

    def test_kerberoast_execution(self) -> None:
        attacker = KerberoastAttack()
        res = attacker.execute_kerberoast_escalation()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['is_engineer'])


if __name__ == '__main__':
    unittest.main()
