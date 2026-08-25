#!/usr/bin/env python3
"""attacker/tests/test_attack_anti_forensics.py — Pruebas unitarias para ataque Historian Anti-Forensics"""
from __future__ import annotations

import os
import unittest
from attacker.attack_historian_anti_forensics import HistorianAntiForensicsAttack


class TestAntiForensicsAttack(unittest.TestCase):

    def test_anti_forensics_execution(self) -> None:
        db_path = '/tmp/anti_forensics_test_db.db'
        attacker = HistorianAntiForensicsAttack(db_path)
        self.addCleanup(self._cleanup, db_path)
        res = attacker.execute_log_tampering()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['historian_cleared'])

    @staticmethod
    def _cleanup(path: str) -> None:
        for ext in ['', '-wal', '-shm']:
            p = path + ext
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


if __name__ == '__main__':
    unittest.main()
