#!/usr/bin/env python3
"""attacker/tests/test_scenario_22_purple_team.py — Test para Escenario 22"""
from __future__ import annotations

import unittest
from attacker.attack_purple_team_mttd import PurpleTeamMttd


class TestScenario22PurpleTeam(unittest.TestCase):

    def test_mttd_measurement(self) -> None:
        mttd = PurpleTeamMttd()
        res = mttd.run_mttd_measurement()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['nist_report_generated'])


if __name__ == '__main__':
    unittest.main()
