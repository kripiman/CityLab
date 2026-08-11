#!/usr/bin/env python3
"""Prueba unitaria e integración para DNP3 Outstation y Samba AD DC Emulator."""

import socket
import threading
import time
import unittest

from plc.dnp3_emulator import Dnp3Server
from plc.dnp3_client import Dnp3MasterClient
from network.ad_dc_emulator import LdapServerThread, KerberosServerThread, SmbServerThread


class TestDnp3AndAdDcEmulators(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.dnp3_port = 20005
        cls.ldap_port = 10389
        cls.kdc_port = 10088
        cls.smb_port = 10445

        # Start DNP3 Outstation on localhost:20005
        cls.dnp3_server = Dnp3Server('127.0.0.1', cls.dnp3_port)
        cls.dnp3_thread = threading.Thread(target=cls.dnp3_server.start, daemon=True)
        cls.dnp3_thread.start()

        # Start AD DC emulators on custom ports
        cls.ldap_thread = LdapServerThread('127.0.0.1', cls.ldap_port)
        cls.kdc_thread = KerberosServerThread('127.0.0.1', cls.kdc_port)
        cls.smb_thread = SmbServerThread('127.0.0.1', cls.smb_port)

        cls.ldap_thread.start()
        cls.kdc_thread.start()
        cls.smb_thread.start()

        time.sleep(0.4)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.dnp3_server.stop()
        cls.ldap_thread.running = False
        cls.kdc_thread.running = False
        cls.smb_thread.running = False

    def test_dnp3_telemetry_and_crob(self) -> None:
        client = Dnp3MasterClient('127.0.0.1', self.dnp3_port)
        
        # Test DNP3 Read
        telemetry = client.read_telemetry()
        self.assertEqual(telemetry['status'], 'SUCCESS')
        self.assertTrue(telemetry['breaker_closed'])

        # Test DNP3 CROB Trip
        trip_ok = client.send_crob('TRIP')
        self.assertTrue(trip_ok)

        # Verify breaker opened state
        self.assertFalse(self.dnp3_server.state.breaker_closed)

        # Test DNP3 CROB Close
        close_ok = client.send_crob('CLOSE')
        self.assertTrue(close_ok)
        self.assertTrue(self.dnp3_server.state.breaker_closed)

    def test_ad_dc_ports(self) -> None:
        # Test LDAP
        with socket.create_connection(('127.0.0.1', self.ldap_port), timeout=2.0) as s:
            s.sendall(b'ldap_ping')
            resp = s.recv(1024)
            self.assertIn(b'LDAP OK', resp)

        # Test Kerberos KDC
        with socket.create_connection(('127.0.0.1', self.kdc_port), timeout=2.0) as s:
            s.sendall(b'as_req')
            resp = s.recv(1024)
            self.assertIn(b'krb5tgs', resp)

        # Test SMB
        with socket.create_connection(('127.0.0.1', self.smb_port), timeout=2.0) as s:
            s.sendall(b'smb_neg')
            resp = s.recv(1024)
            self.assertIn(b'SMB', resp)


if __name__ == '__main__':
    unittest.main()
