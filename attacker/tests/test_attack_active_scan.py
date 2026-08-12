#!/usr/bin/env python3
"""attacker/tests/test_attack_active_scan.py — Test para Escenario 14"""
from __future__ import annotations

import unittest
from attacker.attack_ot_active_scan import OtActiveScan


class TestActiveScan(unittest.TestCase):

    def test_active_scan_execution(self) -> None:
        scan = OtActiveScan()
        res = scan.run_active_scan()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['hosts_found'], 3)


if __name__ == '__main__':
    unittest.main()
