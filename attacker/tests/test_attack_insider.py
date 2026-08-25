#!/usr/bin/env python3
"""attacker/tests/test_attack_insider.py — Tests para ataque Insider RBAC"""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from attacker.attack_insider_rbac import InsiderRbacAttack, main as insider_main


class TestInsiderRbacAttack(unittest.TestCase):

    def test_insider_rbac_strict_auth_enabled(self) -> None:
        """Verifica que con STRICT_AUTH=1 el rol auditor sea bloqueado para writes."""
        with patch.dict(os.environ, {'STRICT_AUTH': '1'}):
            attacker = InsiderRbacAttack()
            res = attacker.execute_unauthorized_write_attempt()
            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'ENGINE_DIRECT')
            self.assertEqual(res['role'], 'auditor')
            self.assertTrue(res['blocked_by_rbac'])
            self.assertFalse(res['access_granted'])

    def test_insider_rbac_strict_auth_disabled(self) -> None:
        """Verifica que con STRICT_AUTH=0 el rol auditor siga sin permiso de escritura en la matriz RBAC."""
        with patch.dict(os.environ, {'STRICT_AUTH': '0'}):
            attacker = InsiderRbacAttack()
            res = attacker.execute_unauthorized_write_attempt()
            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'ENGINE_DIRECT')
            self.assertEqual(res['role'], 'auditor')
            self.assertTrue(res['blocked_by_rbac'])

    def test_insider_rbac_cli(self) -> None:
        """Verifica invocación CLI."""
        rc = insider_main(['--scada-url', ''])
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
