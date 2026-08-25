#!/usr/bin/env python3
"""attacker/tests/test_attack_bacnet_ntcip.py — Tests para scripts de ataque Categoría B OT (BACnet & NTCIP)"""
from __future__ import annotations

import unittest
from attacker.attack_bacnet import BacnetAttacker, main as bacnet_main
from attacker.attack_ntcip import NtcipAttacker, main as ntcip_main
from plc.tests._emulator_harness import running_bacnet_server, running_ntcip_server


class TestBacnetNtcipAttacks(unittest.TestCase):

    def test_bacnet_attack_live_socket_mutates_state(self) -> None:
        """Verifica que el ataque BACnet mute el estado de alarma del listener real a ALARM."""
        with running_bacnet_server(port=14780) as listener:
            self.assertEqual(listener.status, 'NORMAL')

            attacker = BacnetAttacker(target_host='127.0.0.1', target_port=14780)
            res1 = attacker.send_whois()
            self.assertEqual(res1['status'], 'SUCCESS')
            self.assertEqual(res1['mode'], 'SOCKET_LIVE')
            self.assertTrue(res1['bvlc'])

            res2 = attacker.inject_alarm_override()
            self.assertEqual(res2['status'], 'SUCCESS')
            self.assertEqual(res2['mode'], 'SOCKET_LIVE')
            self.assertTrue(res2['alarm_set'])

            # Mutación observable en el listener del dispositivo
            self.assertEqual(listener.status, 'ALARM')

    def test_bacnet_fallback_mode(self) -> None:
        """Verifica fallback ante puerto BACnet cerrado."""
        attacker = BacnetAttacker(target_host='127.0.0.1', target_port=59997)
        res = attacker.inject_alarm_override()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')

    def test_bacnet_cli(self) -> None:
        """Verifica CLI BACnet."""
        with running_bacnet_server(port=14781):
            rc = bacnet_main(['--host', '127.0.0.1', '--port', '14781'])
            self.assertEqual(rc, 0)

    def test_ntcip_attack_live_socket_mutates_phase(self) -> None:
        """Verifica que el ataque NTCIP 1202 altere la fase del semáforo a FLASHING_YELLOW."""
        with running_ntcip_server(port=14161) as listener:
            self.assertEqual(listener.phase, 'NS_GREEN')
            self.assertEqual(listener.coord, 'ON')

            attacker = NtcipAttacker(target_host='127.0.0.1', target_port=14161)
            res1 = attacker.inject_flash_override()
            self.assertEqual(res1['status'], 'SUCCESS')
            self.assertEqual(res1['mode'], 'SOCKET_LIVE')
            self.assertTrue(res1['flashing'])

            # Mutación observable en el estado del controlador
            self.assertEqual(listener.phase, 'FLASHING_YELLOW')
            self.assertEqual(listener.coord, 'OFF')

            res2 = attacker.clear_override()
            self.assertEqual(res2['status'], 'SUCCESS')
            self.assertEqual(res2['mode'], 'SOCKET_LIVE')
            self.assertTrue(res2['cleared'])
            self.assertEqual(listener.phase, 'NS_GREEN')

    def test_ntcip_fallback_mode(self) -> None:
        """Verifica fallback ante puerto NTCIP cerrado."""
        attacker = NtcipAttacker(target_host='127.0.0.1', target_port=59997)
        res = attacker.inject_flash_override()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')

    def test_ntcip_cli(self) -> None:
        """Verifica CLI NTCIP."""
        with running_ntcip_server(port=14162):
            rc = ntcip_main(['--host', '127.0.0.1', '--port', '14162'])
            self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
