#!/usr/bin/env python3
"""attacker/tests/test_attack_goose.py — Pruebas unitarias y E2E para ataque GOOSE Spoofing"""
from __future__ import annotations

import socket
import time
import unittest

from attacker.attack_goose_spoofing import spoof_goose_trip, main as goose_main
from plc.iec61850_emulator import Iec61850GooseEncoder, Iec61850Server


class TestGooseSpoofingAttack(unittest.TestCase):

    _goose_port = 15102
    _sv_port = 15103

    def setUp(self) -> None:
        self.server = Iec61850Server(host='127.0.0.1', goose_port=self._goose_port, sv_port=self._sv_port)
        self.server.start()
        time.sleep(0.05)

    def tearDown(self) -> None:
        self.server.stop()

    def test_goose_spoofing_payload_encoding_decoding(self) -> None:
        """Verifica la codificación y decodificación binaria del PDU GOOSE."""
        pdu = spoof_goose_trip(
            target_host='127.0.0.1',
            target_port=self._goose_port,
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

    def test_goose_spoofing_socket_e2e_trip(self) -> None:
        """Ataque real vía socket UDP provoca mutación de estado observable en el IED."""
        # Estado inicial del interruptor: CERRADO (True)
        self.assertTrue(self.server.dataset.get('XCBR1.Pos.stVal'))

        # Envío de frame malicioso GOOSE de disparo vía socket UDP real
        spoof_goose_trip(
            target_host='127.0.0.1',
            target_port=self._goose_port,
            ied_name='CITYLAB_IED1',
            st_num=200,
            breaker_pos=False
        )

        # Sondeo activo anti-flaky con timeout (máx 0.8s, resolución 20ms)
        received = False
        for _ in range(40):
            if self.server.dataset.get('XCBR1.Pos.stVal') is False:
                received = True
                break
            time.sleep(0.02)

        self.assertTrue(received, "No se procesó el paquete UDP GOOSE dentro de la ventana de espera")
        # El servidor procesa el paquete UDP real y muta el estado a DISPARADO (False)
        pos = self.server.dataset.get('XCBR1.Pos.stVal')
        self.assertFalse(pos)

    def test_goose_spoofing_malformed_packet_negative(self) -> None:
        """Paquetes UDP malformados no deben mutar el estado del interruptor."""
        self.assertTrue(self.server.dataset.get('XCBR1.Pos.stVal'))

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(b'MALFORMED_GARBAGE_PAYLOAD_12345', ('127.0.0.1', self._goose_port))
        finally:
            sock.close()

        time.sleep(0.1)
        # El interruptor debe permanecer CERRADO (True)
        self.assertTrue(self.server.dataset.get('XCBR1.Pos.stVal'))

    def test_goose_spoofing_main_cli_execution(self) -> None:
        """El entrypoint CLI main() ejecuta ráfagas de spoofing sobre el puerto de test sin errores."""
        ret = goose_main(['--port', str(self._goose_port), '--burst', '2'])
        self.assertEqual(ret, 0)
        self.assertFalse(self.server.dataset.get('XCBR1.Pos.stVal'))


if __name__ == '__main__':
    unittest.main()
