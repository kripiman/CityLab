#!/usr/bin/env python3
"""attacker/tests/test_attack_anti_forensics.py — Pruebas unitarias para ataque Historian Anti-Forensics"""
from __future__ import annotations

import unittest
from attacker.attack_historian_anti_forensics import HistorianAntiForensicsAttack


class TestAntiForensicsAttack(unittest.TestCase):

    def test_anti_forensics_execution(self) -> None:
        attacker = HistorianAntiForensicsAttack('/tmp/anti_forensics_test_db.db')
        res = attacker.execute_log_tampering()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['historian_cleared'])


if __name__ == '__main__':
    unittest.main()
