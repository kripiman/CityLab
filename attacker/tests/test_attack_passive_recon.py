#!/usr/bin/env python3
"""attacker/tests/test_attack_passive_recon.py — Test para Escenario 13"""
from __future__ import annotations

import unittest
from attacker.attack_ot_passive_recon import OtPassiveRecon


class TestPassiveRecon(unittest.TestCase):

    def test_passive_recon_execution(self) -> None:
        recon = OtPassiveRecon()
        res = recon.run_passive_sniff()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['devices_mapped'], 5)


if __name__ == '__main__':
    unittest.main()
