#!/usr/bin/env python3
"""attacker/tests/test_attack_ransomware.py — Pruebas unitarias para ataque Ransomware IT/OT Impact"""
from __future__ import annotations

import unittest
from attacker.attack_ransomware_ot_impact import RansomwareOtImpactAttack


class TestRansomwareAttack(unittest.TestCase):

    def test_ransomware_ot_impact_execution(self) -> None:
        attacker = RansomwareOtImpactAttack()
        res = attacker.execute_precautionary_ot_shutdown()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['ot_precautionary_shutdown'])


if __name__ == '__main__':
    unittest.main()
