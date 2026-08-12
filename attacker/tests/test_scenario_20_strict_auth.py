#!/usr/bin/env python3
"""attacker/tests/test_scenario_20_strict_auth.py — Test para Escenario 20"""
from __future__ import annotations

import unittest
from network.rbac import RBACResolver


class TestScenario20StrictAuth(unittest.TestCase):

    def test_strict_auth_toggle(self) -> None:
        resolver = RBACResolver()
        role, status = resolver.resolve("Bearer operator:SCADA_TOKEN_2026")
        self.assertEqual(role, 'operator')
        self.assertEqual(status, 200)


if __name__ == '__main__':
    unittest.main()
