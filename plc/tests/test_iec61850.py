#!/usr/bin/env python3
"""plc/tests/test_iec61850.py — Pruebas unitarias para emulador IEC 61850 GOOSE/SV (Fase 3)"""
from __future__ import annotations

import unittest
from plc.iec61850_emulator import (
    IEC61850DataSet,
    Iec61850GooseEncoder,
    Iec61850SvEncoder,
    Iec61850Server,
    ETHERTYPE_GOOSE,
    ETHERTYPE_SV
)


class TestIEC61850Emulator(unittest.TestCase):

    def setUp(self) -> None:
        self.dataset = IEC61850DataSet('TEST_IED')

    def test_dataset_operations(self) -> None:
        val = self.dataset.get('XCBR1.Pos.stVal')
        self.assertTrue(val)
        
        # State number increments on change
        st1 = self.dataset.get_state()['st_num']
        self.dataset.set('XCBR1.Pos.stVal', False)
        st2 = self.dataset.get_state()['st_num']
        self.assertEqual(st2, st1 + 1)
        self.assertFalse(self.dataset.get('XCBR1.Pos.stVal'))

    def test_goose_encode_decode(self) -> None:
        pdu = Iec61850GooseEncoder.encode(
            gcb_ref='TEST_IED/LLN0$GO$gcb01',
            datset_ref='TEST_IED/LLN0$ds01',
            st_num=5,
            sq_num=10,
            breaker_pos=True
        )
        self.assertIsNotNone(pdu)
        decoded = Iec61850GooseEncoder.decode(pdu)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded['gcb_ref'], 'TEST_IED/LLN0$GO$gcb01')
        self.assertEqual(decoded['st_num'], 5)
        self.assertEqual(decoded['sq_num'], 10)
        self.assertTrue(decoded['breaker_pos'])

    def test_sv_encode_decode(self) -> None:
        pdu = Iec61850SvEncoder.encode(
            sv_id='TEST_IED/LLN0$SV$sv01',
            smp_cnt=100,
            v_a=230.5,
            i_a=12.2
        )
        self.assertIsNotNone(pdu)
        decoded = Iec61850SvEncoder.decode(pdu)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded['sv_id'], 'TEST_IED/LLN0$SV$sv01')
        self.assertEqual(decoded['smp_cnt'], 100)
        self.assertAlmostEqual(decoded['v_a'], 230.5, places=1)
        self.assertAlmostEqual(decoded['i_a'], 12.2, places=1)

    def test_server_goose_and_sv_publishing(self) -> None:
        server = Iec61850Server(host='127.0.0.1', goose_port=10102, sv_port=10103)
        server.start()
        
        goose_pdu = server.publish_goose_event()
        sv_pdu = server.publish_sv_sample()
        
        server.stop()
        
        decoded_goose = Iec61850GooseEncoder.decode(goose_pdu)
        decoded_sv = Iec61850SvEncoder.decode(sv_pdu)
        
        self.assertIsNotNone(decoded_goose)
        self.assertIsNotNone(decoded_sv)


if __name__ == '__main__':
    unittest.main()
