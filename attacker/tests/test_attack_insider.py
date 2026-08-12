#!/usr/bin/env python3
"""attacker/tests/test_attack_insider.py — Pruebas unitarias para ataque Insider RBAC"""
from __future__ import annotations

import unittest
from attacker.attack_insider_rbac import InsiderRbacAttack


class TestInsiderRbacAttack(unittest.TestCase):

    def test_insider_rbac_execution(self) -> None:
        attacker = InsiderRbacAttack()
        res = attacker.execute_unauthorized_write_attempt()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['blocked_by_rbac'])


if __name__ == '__main__':
    unittest.main()
