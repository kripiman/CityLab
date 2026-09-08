#!/usr/bin/env python3
"""plc/tests/test_modbus_ntcip.py — Unit tests for NtcipListener in plc/modbus_emulator.py"""

import socket
import unittest
from plc.modbus_emulator import NtcipListener


class TestNtcipListener(unittest.TestCase):
    def test_ntcip_listener_commands(self) -> None:
        listener = NtcipListener(host='127.0.0.1', port=0)
        # Test command handling without binding socket
        res_default = listener.handle_command('STATUS')
        self.assertIn('NS_GREEN', res_default)

        res_override = listener.handle_command('OVERRIDE FLASH')
        self.assertIn('FLASHING_YELLOW', res_override)
        self.assertEqual(listener.phase, 'FLASHING_YELLOW')

        res_clear = listener.handle_command('OVERRIDE CLEAR')
        self.assertIn('NS_GREEN', res_clear)
        self.assertEqual(listener.phase, 'NS_GREEN')

    def test_ntcip_listener_socket_communication(self) -> None:
        # Use ephemeral port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()

        listener = NtcipListener(host='127.0.0.1', port=port)
        listener.start()
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(2.0)
            client.connect(('127.0.0.1', port))
            client.sendall(b'OVERRIDE FLASH\n')
            data = client.recv(1024).decode('utf-8')
            client.close()
            self.assertIn('FLASHING_YELLOW', data)
        finally:
            listener.stop()


if __name__ == '__main__':
    unittest.main()
