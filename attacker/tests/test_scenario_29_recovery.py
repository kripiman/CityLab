#!/usr/bin/env python3
"""attacker/tests/test_scenario_29_recovery.py — Test para Escenario 29"""
from __future__ import annotations

import unittest
from attacker.attack_post_incident_recovery import PostIncidentRecovery


class TestScenario29Recovery(unittest.TestCase):

    def test_recovery_execution(self) -> None:
        rec = PostIncidentRecovery('/tmp/test_recovery_db.db')
        res = rec.run_recovery_procedure()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['recovery_completed'])


if __name__ == '__main__':
    unittest.main()
