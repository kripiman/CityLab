#!/usr/bin/env python3
"""Prueba unitaria e integración para SDN Controller y DNP3 SA Level 1 HMAC Authentication."""

import hashlib
import hmac
import unittest

from network.sdn_controller import apply_circuit_breaker, run_ovs_cmd
from plc.dnp3_emulator import Dnp3ProtocolHandler, Dnp3OutstationState


class TestSdnAndDnp3Sa(unittest.TestCase):

    def test_dnp3_sa_level1_authentication(self) -> None:
        state = Dnp3OutstationState()
        handler = Dnp3ProtocolHandler(state)
        handler.sa_required = True  # Enforce DNP3 SA Level 1

        # Frame 1: DNP3 CROB Direct Operate without SA HMAC -> Must be REJECTED (Func 0x83 Auth Failed)
        # Header (10B) + App Header (2B: \xc0\x05) + CROB Data (7B) = 19B
        crob_frame = (
            b'\x05\x64\x12\x44\x01\x00\x0a\x00\x00\x00'  # Header 10B
            b'\xc0\x05'                                  # App Control + Direct Operate
            b'\x0c\x01\x28\x01\x00'                      # Group 12 Var 1
            b'\x00\x41'                                  # Index 0, Code 0x41 (Trip)
        )
        resp = handler.handle_frame(crob_frame)
        # Verify Auth Failed Func Code 0x83 returned
        self.assertIn(b'\x83', resp)
        # Breaker should remain closed
        self.assertTrue(state.breaker_closed)

        # Frame 2: DNP3 CROB with valid HMAC-SHA256 signature suffix (23B total)
        secret = b'CITYLAB_DNP3_SA_KEY_2026'
        valid_hmac = hmac.new(secret, crob_frame[:19], hashlib.sha256).digest()[:4]
        authenticated_crob_frame = crob_frame[:19] + valid_hmac

        resp_auth = handler.handle_frame(authenticated_crob_frame)
        # Breaker should now be TRIPPED (breaker_closed = False)
        self.assertFalse(state.breaker_closed)

    def test_sdn_circuit_breaker_helper(self) -> None:
        # Dry run circuit breaker execution helper
        apply_circuit_breaker('10.0.1.99')


if __name__ == '__main__':
    unittest.main()
