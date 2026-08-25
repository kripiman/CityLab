#!/usr/bin/env python3
"""attacker/tests/test_attack_honeypot_touch.py — Tests para Escenario 16: Interacción con Deception Technology"""
from __future__ import annotations

import unittest
from attacker.attack_honeypot_touch import HoneypotTouch, main as honeypot_main
from plc.tests._emulator_harness import running_honeypot_server


class TestHoneypotTouch(unittest.TestCase):

    def test_honeypot_touch_live_socket_triggers_siem(self) -> None:
        """Verifica que la conexión socket real al Honeypot dispare la alerta en el pipeline SIEM."""
        with running_honeypot_server(port=15025) as server:
            touch = HoneypotTouch(target_host='127.0.0.1', target_port=15025)
            res = touch.run_honeypot_interaction()

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertTrue(res['honeypot_triggered'])
            self.assertTrue(res['socket_connected'])

            # Mutación observable en el SIEM del daemon honeypot
            events = [e for e in server.siem.events_buffer if e.event_category == 'honeypot']
            self.assertGreaterEqual(len(events), 1)
            self.assertEqual(events[-1].severity, 'HIGH')

    def test_honeypot_touch_fallback_mode(self) -> None:
        """Verifica que si el honeypot está inalcanzable caiga en TABLETOP_FALLBACK."""
        touch = HoneypotTouch(target_host='127.0.0.1', target_port=59997)
        res = touch.run_honeypot_interaction()

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')
        self.assertFalse(res['socket_connected'])
        self.assertTrue(res['honeypot_triggered'])

    def test_honeypot_touch_cli(self) -> None:
        """Verifica la invocación CLI."""
        with running_honeypot_server(port=15026):
            rc = honeypot_main(['--host', '127.0.0.1', '--port', '15026'])
            self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
