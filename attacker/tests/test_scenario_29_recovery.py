#!/usr/bin/env python3
"""attacker/tests/test_scenario_29_recovery.py — Test para Escenario 29"""
from __future__ import annotations

import os
import unittest
from attacker.attack_post_incident_recovery import PostIncidentRecovery


class TestScenario29Recovery(unittest.TestCase):

    def test_recovery_execution(self) -> None:
        db_path = '/tmp/test_recovery_db.db'
        self.addCleanup(self._cleanup, db_path)
        rec = PostIncidentRecovery(db_path)
        res = rec.run_recovery_procedure()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['recovery_completed'])

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
