#!/usr/bin/env python3
"""attacker/tests/test_attack_honeypot_touch.py — Test para Escenario 16"""
from __future__ import annotations

import unittest
from attacker.attack_honeypot_touch import HoneypotTouch


class TestHoneypotTouch(unittest.TestCase):

    def test_honeypot_touch_execution(self) -> None:
        touch = HoneypotTouch()
        res = touch.run_honeypot_interaction()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['honeypot_triggered'])


if __name__ == '__main__':
    unittest.main()
