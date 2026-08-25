#!/usr/bin/env python3
"""attacker/tests/test_attack_kerberoast.py — Tests para ataque Kerberoasting Active Directory"""
from __future__ import annotations

import unittest
from attacker.attack_kerberoast_ad import KerberoastAttack, main as krb_main
from plc.tests._emulator_harness import running_ad_dc


class TestKerberoastAttack(unittest.TestCase):

    def test_kerberoast_live_socket_kdc(self) -> None:
        """Verifica que el ataque solicite y reciba un ticket TGS vía socket real TCP al KDC."""
        with running_ad_dc(kerberos_port=14088, ldap_port=14389):
            attacker = KerberoastAttack(kdc_host='127.0.0.1', kdc_port=14088, scada_url='')
            res = attacker.execute_kerberoast_escalation(account='krbe_ews')

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertTrue(res['kdc_reachable'])
            self.assertTrue(res['ticket_received'])
            self.assertTrue(res['is_engineer'])
            self.assertEqual(res['extracted_role'], 'engineer')

    def test_kerberoast_fallback_mode(self) -> None:
        """Verifica que si el KDC está inaccesible caiga en TABLETOP_FALLBACK sin romper."""
        attacker = KerberoastAttack(kdc_host='127.0.0.1', kdc_port=59997, scada_url='')
        res = attacker.execute_kerberoast_escalation(account='krbe_ews')

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')
        self.assertFalse(res['kdc_reachable'])
        self.assertTrue(res['is_engineer'])

    def test_kerberoast_cli(self) -> None:
        """Verifica la invocación por CLI."""
        with running_ad_dc(kerberos_port=14088, ldap_port=14389):
            rc = krb_main(['--kdc-host', '127.0.0.1', '--kdc-port', '14088', '--scada-url', ''])
            self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
