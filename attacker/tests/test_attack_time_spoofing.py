#!/usr/bin/env python3
"""attacker/tests/test_attack_time_spoofing.py — Pruebas unitarias para ataque NTP Time Spoofing"""
from __future__ import annotations

import unittest
from attacker.attack_ntp_time_spoofing import NtpTimeSpoofingAttack


class TestTimeSpoofingAttack(unittest.TestCase):

    def test_ntp_time_spoofing_execution(self) -> None:
        attacker = NtpTimeSpoofingAttack()
        res = attacker.execute_time_desync_attack(offset_seconds=3600.0)
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['siem_blinded'])


if __name__ == '__main__':
    unittest.main()
