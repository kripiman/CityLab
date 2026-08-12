#!/usr/bin/env python3
"""attacker/tests/test_attack_goose.py — Pruebas unitarias para script de ataque GOOSE Spoofing"""
from __future__ import annotations

import unittest
from attacker.attack_goose_spoofing import spoof_goose_trip
from plc.iec61850_emulator import Iec61850GooseEncoder, Iec61850Server


class TestGooseSpoofingAttack(unittest.TestCase):

    def setUp(self) -> None:
        self.server = Iec61850Server(host='127.0.0.1', goose_port=10105, sv_port=10106)
        self.server.start()

    def tearDown(self) -> None:
        self.server.stop()

    def test_goose_spoofing_payload(self) -> None:
        pdu = spoof_goose_trip(
            target_host='127.0.0.1',
            target_port=10105,
            ied_name='TEST_IED',
            st_num=99,
            sq_num=1,
            breaker_pos=False
        )
        self.assertIsNotNone(pdu)
        
        decoded = Iec61850GooseEncoder.decode(pdu)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded['gcb_ref'], 'TEST_IED/LLN0$GO$gcb01')
        self.assertEqual(decoded['st_num'], 99)
        self.assertFalse(decoded['breaker_pos'])


if __name__ == '__main__':
    unittest.main()
