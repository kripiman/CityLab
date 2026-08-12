#!/usr/bin/env python3
"""attacker/tests/test_scenario_20_strict_auth.py — Test para Escenario 20"""
from __future__ import annotations

import unittest
from network.rbac import RBACResolver


class TestScenario20StrictAuth(unittest.TestCase):

    def test_strict_auth_toggle(self) -> None:
        import os
        orig = os.environ.get('SCADA_TOKEN_OPERATOR')
        os.environ['SCADA_TOKEN_OPERATOR'] = 'SCADA_TOKEN_2026'
        try:
            resolver = RBACResolver()
            resolver.reload()
            role, status = resolver.resolve("Bearer operator:SCADA_TOKEN_2026")
            self.assertEqual(role, 'operator')
            self.assertEqual(status, 200)
        finally:
            if orig is None:
                os.environ.pop('SCADA_TOKEN_OPERATOR', None)
            else:
                os.environ['SCADA_TOKEN_OPERATOR'] = orig


if __name__ == '__main__':
    unittest.main()
