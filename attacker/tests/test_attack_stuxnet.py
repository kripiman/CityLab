#!/usr/bin/env python3
"""attacker/tests/test_attack_stuxnet.py — Pruebas unitarias para ataque Stuxnet Telemetry Replay"""
from __future__ import annotations

import unittest
from attacker.attack_stuxnet_replay import StuxnetReplayAttack
from network.historian import HistorianTSDB


class TestStuxnetAttack(unittest.TestCase):

    def test_stuxnet_replay_execution(self) -> None:
        historian = HistorianTSDB('/tmp/stuxnet_test_db.db')
        attacker = StuxnetReplayAttack()
        attacker.record_normal_baseline(samples=3)
        
        res = attacker.execute_replay_and_sabotage(historian, sabotage_duration=3)
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['replayed_samples'], 3)
        self.assertTrue(res['real_process_sabotaged'])


if __name__ == '__main__':
    unittest.main()
