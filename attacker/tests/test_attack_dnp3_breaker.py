#!/usr/bin/env python3
"""attacker/tests/test_attack_dnp3_breaker.py — Tests para ataque DNP3 CROB Breaker Trip"""
from __future__ import annotations

import unittest
from attacker.attack_dnp3_breaker import Dnp3BreakerAttack, main as dnp3_breaker_main
from plc.tests._emulator_harness import running_dnp3_server


class TestDnp3BreakerAttack(unittest.TestCase):

    def test_dnp3_breaker_live_socket_trip_mutates_state(self) -> None:
        """Verifica que el ataque DNP3 CROB TRIP abra el disyuntor real en el servidor DNP3."""
        with running_dnp3_server(port=15200) as server:
            # Estado inicial cerrado
            self.assertTrue(server.state.breaker_closed)

            attacker = Dnp3BreakerAttack(target_host='127.0.0.1', target_port=15200)
            res = attacker.execute_trip_attack(command='TRIP')

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertTrue(res['crob_executed'])

            # Mutación observable en el estado del outstation DNP3
            self.assertFalse(server.state.breaker_closed)

    def test_dnp3_breaker_live_socket_close_mutates_state(self) -> None:
        """Verifica que el ataque DNP3 CROB CLOSE cierre el disyuntor real."""
        with running_dnp3_server(port=15201) as server:
            server.state.breaker_closed = False

            attacker = Dnp3BreakerAttack(target_host='127.0.0.1', target_port=15201)
            res = attacker.execute_trip_attack(command='CLOSE')

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertTrue(res['crob_executed'])
            self.assertTrue(server.state.breaker_closed)

    def test_dnp3_breaker_fallback_mode(self) -> None:
        """Verifica que si el outstation DNP3 está inalcanzable caiga en TABLETOP_FALLBACK."""
        attacker = Dnp3BreakerAttack(target_host='127.0.0.1', target_port=59997)
        res = attacker.execute_trip_attack(command='TRIP')

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')
        self.assertFalse(res['crob_executed'])

    def test_dnp3_breaker_cli(self) -> None:
        """Verifica invocación CLI."""
        with running_dnp3_server(port=15202):
            rc = dnp3_breaker_main(['--host', '127.0.0.1', '--port', '15202', '--command', 'TRIP'])
            self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
