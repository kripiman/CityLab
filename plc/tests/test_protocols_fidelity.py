#!/usr/bin/env python3
"""plc/tests/test_protocols_fidelity.py — Tests de fidelidad y cobertura unificada para protocolos OT (Fase 3)

Cubre:
  - OPC UA Binary Write/Read payload exchange.
  - IEC 61850 GOOSE/SV Sequence State (st_num / sq_num) and Dataset Updates.
  - DNP3 Outstation Secure Authentication (SA L1) and CROB control.
"""

import threading
import time
import unittest
from plc.opcua_emulator import OpcUaServer, OpcUaClient, OpcUaNodeSpace
from plc.iec61850_emulator import IEC61850DataSet, Iec61850GooseEncoder, Iec61850SvEncoder
from plc.dnp3_emulator import Dnp3Server
from plc.dnp3_client import Dnp3MasterClient


class TestProtocolFidelityPhase3(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.opcua_port = 14841
        cls.dnp3_port = 20006

        # OPC UA Server
        cls.ns = OpcUaNodeSpace()
        cls.opcua_server = OpcUaServer('127.0.0.1', cls.opcua_port, node_space=cls.ns)
        cls.opcua_thread = threading.Thread(target=cls.opcua_server.start, daemon=True)
        cls.opcua_thread.start()

        # DNP3 Server
        cls.dnp3_server = Dnp3Server('127.0.0.1', cls.dnp3_port)
        cls.dnp3_thread = threading.Thread(target=cls.dnp3_server.start, daemon=True)
        cls.dnp3_thread.start()

        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.opcua_server.stop()
        cls.dnp3_server.stop()
        if hasattr(cls, 'opcua_thread'):
            cls.opcua_thread.join(timeout=2.0)
        if hasattr(cls, 'dnp3_thread'):
            cls.dnp3_thread.join(timeout=2.0)

    def test_opcua_write_node_over_network(self) -> None:
        client = OpcUaClient('127.0.0.1', self.opcua_port)
        self.assertTrue(client.connect(timeout=2.0))
        try:
            # Write via OPC UA Binary payload
            written = client.write_node(1001, 88.5)
            self.assertTrue(written)
            # Read back
            val = client.read_node(1001)
            self.assertAlmostEqual(val, 88.5, places=1)
        finally:
            client.close()

    def test_iec61850_dataset_fidelity(self) -> None:
        ds = IEC61850DataSet('CITYLAB_IED1')
        st_initial = ds.get_state()['st_num']

        # Quality flags test
        ds.set_quality('XCBR1.Pos.stVal', 0x0004)  # Test mode quality flag
        self.assertEqual(ds.get_quality('XCBR1.Pos.stVal'), 0x0004)

        # Update MMXU voltage
        ds.set('MMXU1.PhV.phsA.cVal.mag', 240.0)
        self.assertEqual(ds.get('MMXU1.PhV.phsA.cVal.mag'), 240.0)

        # GOOSE PDU encode/decode with conf_rev and test_mode
        goose_bin = Iec61850GooseEncoder.encode(
            gcb_ref='CITYLAB_IED1/LLN0$GO$gcb01',
            datset_ref='CITYLAB_IED1/LLN0$ds01',
            st_num=st_initial + 1,
            sq_num=1,
            breaker_pos=False,
            conf_rev=2,
            test_mode=True
        )
        decoded = Iec61850GooseEncoder.decode(goose_bin)
        self.assertFalse(decoded['breaker_pos'])
        self.assertEqual(decoded['st_num'], st_initial + 1)
        self.assertEqual(decoded['conf_rev'], 2)
        self.assertTrue(decoded['test_mode'])

    def test_dnp3_sa_level1_crob_fidelity(self) -> None:
        import hashlib, hmac
        client = Dnp3MasterClient('127.0.0.1', self.dnp3_port)
        telem = client.read_telemetry()
        self.assertEqual(telem['status'], 'SUCCESS')
        self.assertGreater(telem['raw_response_bytes'], 0)

        # Test DNP3 SA Challenge-Response HMAC verification (positive & negative)
        challenge = b'DNP3_RANDOM_CHALLENGE_12345678'
        key = b'CITYLAB_DNP3_SA'
        expected_hmac = hmac.new(key, challenge, hashlib.sha256).digest()
        sa_valid = self.dnp3_server.state.verify_sa_challenge_hmac(challenge, expected_hmac, secret_key=key)
        self.assertTrue(sa_valid)

        invalid_hmac = b'\x00' * 32
        sa_invalid = self.dnp3_server.state.verify_sa_challenge_hmac(challenge, invalid_hmac, secret_key=key)
        self.assertFalse(sa_invalid)
        self.assertEqual(self.dnp3_server.state.sa_challenge_count, 2)

        ok_trip = client.send_crob('TRIP')
        self.assertTrue(ok_trip)
        self.assertFalse(self.dnp3_server.state.breaker_closed)


if __name__ == '__main__':
    unittest.main()
