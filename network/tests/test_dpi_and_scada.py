#!/usr/bin/env python3
"""Prueba unitaria e integración para Modbus DPI Proxy y Watchdog Loss of View en SCADA Server."""

import socket
import threading
import time
import unittest

from network.modbus_proxy import ModbusDpiProxyServer, ModbusDpiEngine
from network.scada_server import scada_state, poll_plcs, _consecutive_failures, LOSS_OF_VIEW_THRESHOLD


class TestDpiProxyAndScadaWatchdog(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.proxy_port = 15025
        cls.proxy_server = ModbusDpiProxyServer('127.0.0.1', cls.proxy_port)
        cls.proxy_thread = threading.Thread(target=cls.proxy_server.start, daemon=True)
        cls.proxy_thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.proxy_server.stop()

    def test_modbus_dpi_filter_read_and_write(self) -> None:
        engine = ModbusDpiEngine()

        # FC1 (Read Coils) from h_scada (10.0.2.20) -> ALLOWED
        read_packet = b'\x00\x01\x00\x00\x00\x06\x01\x01\x00\x00\x00\x04'
        ok, reason = engine.inspect_and_filter('10.0.2.20', '10.0.3.10', read_packet)
        self.assertTrue(ok)
        self.assertEqual(reason, 'ALLOWED')

        # FC5 (Write Single Coil) from unauthorized h_dmz (10.0.2.10) -> DENIED
        write_packet = b'\x00\x02\x00\x00\x00\x06\x01\x05\x00\x00\xff\x00'
        ok, reason = engine.inspect_and_filter('10.0.2.10', '10.0.3.10', write_packet)
        self.assertFalse(ok)
        self.assertEqual(reason, 'UNAUTHORIZED_WRITE_SOURCE_NOT_EWS')

        # FC5 (Write Single Coil) from authorized h_ews (10.0.4.30) to addr 0 -> ALLOWED
        ok, reason = engine.inspect_and_filter('10.0.4.30', '10.0.3.10', write_packet)
        self.assertTrue(ok)
        self.assertEqual(reason, 'ALLOWED')

        # FC5 Write to out of range register addr 10 -> DENIED
        out_of_range_packet = b'\x00\x03\x00\x00\x00\x06\x01\x05\x00\x0a\xff\x00'
        ok, reason = engine.inspect_and_filter('10.0.4.30', '10.0.3.10', out_of_range_packet)
        self.assertFalse(ok)
        self.assertIn('REGISTER_OUT_OF_RANGE', reason)

    def test_multi_plc_unit_id_routing(self) -> None:
        engine = ModbusDpiEngine()
        # Unit ID 1 -> 10.0.3.10 (water)
        read_uid1 = b'\x00\x01\x00\x00\x00\x06\x01\x01\x00\x00\x00\x04'
        ok1, reason1 = engine.inspect_and_filter('10.0.2.20', '10.0.3.10', read_uid1)
        self.assertTrue(ok1)

        # Unit ID 4 -> 10.0.3.14 (transport)
        read_uid4 = b'\x00\x01\x00\x00\x00\x06\x04\x01\x00\x00\x00\x04'
        ok4, reason4 = engine.inspect_and_filter('10.0.2.20', '10.0.3.14', read_uid4)
        self.assertTrue(ok4)

    def test_scada_watchdog_loss_of_view(self) -> None:
        # Simulate 3 consecutive polling failures for a sector
        sector = 'water'
        _consecutive_failures[sector] = LOSS_OF_VIEW_THRESHOLD
        scada_state['sectors'][sector] = {'status': 'LOSS_OF_VIEW', 'coils': [False] * 4}
        self.assertEqual(scada_state['sectors'][sector]['status'], 'LOSS_OF_VIEW')


if __name__ == '__main__':
    unittest.main()
