#!/usr/bin/env python3
"""attacker/tests/test_scenario_26_apt.py — Test para Escenario 26"""
from __future__ import annotations

import unittest
from attacker.attack_apt_sandworm_campaign import AptSandwormCampaign


class TestScenario26Apt(unittest.TestCase):

    def test_apt_campaign_execution(self) -> None:
        apt = AptSandwormCampaign()
        res = apt.run_full_apt_campaign()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['total_phases'], 5)


if __name__ == '__main__':
    unittest.main()
