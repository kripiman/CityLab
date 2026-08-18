#!/usr/bin/env python3
"""attacker/tests/test_attack_bacnet_ntcip.py — Unit tests for Category B OT attack scripts"""

import socket
import unittest
from attacker.attack_bacnet import BacnetAttacker
from attacker.attack_ntcip import NtcipAttacker
from plc.modbus_emulator import BacnetListener, NtcipListener


class TestBacnetNtcipAttacks(unittest.TestCase):
    def test_bacnet_attack_execution(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()

        listener = BacnetListener(host='127.0.0.1', port=port)
        listener.start()
        try:
            attacker = BacnetAttacker(target_host='127.0.0.1', target_port=port)
            res1 = attacker.send_whois()
            self.assertEqual(res1['status'], 'SUCCESS')
            self.assertTrue(res1['bvlc'])

            res2 = attacker.inject_alarm_override()
            self.assertEqual(res2['status'], 'SUCCESS')
            self.assertTrue(res2['alarm_set'])
        finally:
            listener.stop()

    def test_ntcip_attack_execution(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()

        listener = NtcipListener(host='127.0.0.1', port=port)
        listener.start()
        try:
            attacker = NtcipAttacker(target_host='127.0.0.1', target_port=port)
            res1 = attacker.inject_flash_override()
            self.assertEqual(res1['status'], 'SUCCESS')
            self.assertTrue(res1['flashing'])

            res2 = attacker.clear_override()
            self.assertEqual(res2['status'], 'SUCCESS')
            self.assertTrue(res2['cleared'])
        finally:
            listener.stop()


if __name__ == '__main__':
    unittest.main()
