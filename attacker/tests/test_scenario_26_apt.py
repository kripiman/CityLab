#!/usr/bin/env python3
"""attacker/tests/test_scenario_26_apt.py — Test para Escenario 26"""
from __future__ import annotations

import os
import unittest
from attacker.attack_apt_sandworm_campaign import AptSandwormCampaign


class TestScenario26Apt(unittest.TestCase):

    def test_apt_campaign_execution(self) -> None:
        self.addCleanup(self._cleanup, '/tmp/apt_sandworm_historian.db')
        self.addCleanup(self._cleanup, '/tmp/apt_sandworm_recovery.db')

        apt = AptSandwormCampaign()
        res = apt.run_full_apt_campaign()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['total_phases'], 5)
        self.assertTrue(res['phase_details']['phase3_goose']['breaker_tripped'])
        self.assertEqual(res['phase_details']['phase4_anti_forensics']['records_wiped'], 1)
        self.assertTrue(res['phase_details']['phase5_recovery']['recovery_completed'])

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
