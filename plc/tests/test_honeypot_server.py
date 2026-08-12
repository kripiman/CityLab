#!/usr/bin/env python3
"""plc/tests/test_honeypot_server.py — Test unitario para daemon honeypot OT"""
from __future__ import annotations

import socket
import time
import unittest
from plc.honeypot_server import OtHoneypotServer


class TestHoneypotServer(unittest.TestCase):

    def setUp(self) -> None:
        self.server = OtHoneypotServer(host='127.0.0.1', port=15099)
        self.server.start()
        time.sleep(0.2)

    def tearDown(self) -> None:
        self.server.stop()

    def test_honeypot_touch_detection(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(('127.0.0.1', 15099))
        s.sendall(b'\x00\x01\x00\x00\x00\x06\x01\x01\x00\x00\x00\x04')
        try:
            data = s.recv(1024)
            self.assertTrue(len(data) > 0)
        except OSError:
            pass
        s.close()
        time.sleep(0.2)

        events = self.server.siem.events_buffer
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0].event_category, 'honeypot')
        self.assertEqual(events[0].source_ip, '127.0.0.1')


if __name__ == '__main__':
    unittest.main()
