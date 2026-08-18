#!/usr/bin/env python3
"""plc/tests/test_bacnet.py — Unit tests for BacnetListener in plc/modbus_emulator.py"""

import socket
import unittest
from plc.modbus_emulator import BacnetListener


class TestBacnetListener(unittest.TestCase):
    def test_bacnet_datagram_handling(self) -> None:
        listener = BacnetListener(host='127.0.0.1', port=0)
        # Test BVLC Who-Is header handling
        bvlc_whois = bytearray([0x81, 0x0b, 0x00, 0x0c, 0x01, 0x00, 0x10, 0x08])
        res_bvlc = listener.handle_datagram(bytes(bvlc_whois))
        self.assertEqual(res_bvlc[0], 0x81)
        self.assertEqual(res_bvlc[1], 0x0a)  # Original-Unicast I-Am

        # Test ASCII command
        res_default = listener.handle_datagram(b'STATUS')
        self.assertIn(b'DEVICE_ID=1001', res_default)

        res_alarm = listener.handle_datagram(b'ALARM HVAC')
        self.assertIn(b'STATUS=ALARM', res_alarm)
        self.assertEqual(listener.status, 'ALARM')

        res_reset = listener.handle_datagram(b'RESET')
        self.assertIn(b'STATUS=NORMAL', res_reset)
        self.assertEqual(listener.status, 'NORMAL')

    def test_bacnet_socket_communication(self) -> None:
        # Use ephemeral UDP port
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()

        listener = BacnetListener(host='127.0.0.1', port=port)
        listener.start()
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(2.0)
            client.sendto(b'STATUS', ('127.0.0.1', port))
            data, _ = client.recvfrom(1024)
            client.close()
            self.assertIn(b'DEVICE_ID=1001', data)
        finally:
            listener.stop()


if __name__ == '__main__':
    unittest.main()
