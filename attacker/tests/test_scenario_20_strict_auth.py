#!/usr/bin/env python3
"""attacker/tests/test_scenario_20_strict_auth.py — Test para Escenario 20"""
from __future__ import annotations

import unittest
from network.rbac import RBACResolver


class TestScenario20StrictAuth(unittest.TestCase):

    def test_strict_auth_toggle(self) -> None:
        import os
        orig_token = os.environ.get('SCADA_TOKEN_OPERATOR')
        orig_strict = os.environ.get('STRICT_AUTH')
        os.environ['SCADA_TOKEN_OPERATOR'] = 'SCADA_TOKEN_2026'

        try:
            # 1. Modo CTF (STRICT_AUTH=0): token plano sin prefijo de rol es aceptado
            os.environ['STRICT_AUTH'] = '0'
            resolver_ctf = RBACResolver()
            role_ctf, status_ctf = resolver_ctf.resolve("Bearer SCADA_TOKEN_2026")
            self.assertEqual(role_ctf, 'operator')
            self.assertEqual(status_ctf, 200)

            # 2. Modo Estricto (STRICT_AUTH=1): token plano sin prefijo es rechazado con 403
            os.environ['STRICT_AUTH'] = '1'
            resolver_strict = RBACResolver()
            role_plain, status_plain = resolver_strict.resolve("Bearer SCADA_TOKEN_2026")
            self.assertIsNone(role_plain)
            self.assertEqual(status_plain, 403)

            # 3. Modo Estricto (STRICT_AUTH=1): token formateado Bearer operator:<token> es aceptado
            role_rbac, status_rbac = resolver_strict.resolve("Bearer operator:SCADA_TOKEN_2026")
            self.assertEqual(role_rbac, 'operator')
            self.assertEqual(status_rbac, 200)

        finally:
            if orig_token is None:
                os.environ.pop('SCADA_TOKEN_OPERATOR', None)
            else:
                os.environ['SCADA_TOKEN_OPERATOR'] = orig_token

            if orig_strict is None:
                os.environ.pop('STRICT_AUTH', None)
            else:
                os.environ['STRICT_AUTH'] = orig_strict


if __name__ == '__main__':
    unittest.main()
