#!/usr/bin/env python3
"""attacker/tests/test_attack_active_scan.py — Pruebas unitarias y E2E para escaneo activo OT"""
from __future__ import annotations

import unittest
from attacker.attack_ot_active_scan import OtActiveScan, main as scan_main
from plc.tests._emulator_harness import running_modbus_server, running_opcua_server, running_dnp3_server


class TestActiveScan(unittest.TestCase):

    def test_active_scan_live_sockets_mixed_targets(self) -> None:
        """Verifica que el escáner detecte empíricamente puertos abiertos y cerrados usando sockets TCP reales."""
        with running_modbus_server(port=15020, plant_type='water'):
            with running_opcua_server(port=14840):
                with running_dnp3_server(port=15200):
                    targets = [
                        ('127.0.0.1', 15020),  # Modbus (Abierto)
                        ('127.0.0.1', 14840),  # OPC UA (Abierto)
                        ('127.0.0.1', 15200),  # DNP3 (Abierto)
                        ('127.0.0.1', 15999),  # Cerrado deliberado
                    ]
                    scan = OtActiveScan()
                    res = scan.run_active_scan(targets=targets, timeout=0.2)

                    self.assertEqual(res['status'], 'SUCCESS')
                    self.assertEqual(res['mode'], 'SOCKET_LIVE')
                    self.assertEqual(res['hosts_scanned'], 4)
                    self.assertEqual(len(res['open_ports']), 3)
                    self.assertIn(('127.0.0.1', 15020), res['open_ports'])
                    self.assertIn(('127.0.0.1', 14840), res['open_ports'])
                    self.assertIn(('127.0.0.1', 15200), res['open_ports'])
                    self.assertEqual(res['closed_ports'], [('127.0.0.1', 15999)])
                    self.assertEqual(res['hosts_found'], 1)

    def test_active_scan_tabletop_fallback(self) -> None:
        """Si no hay objetivos alcanzables en localhost, aplica fallback TABLETOP_FALLBACK documentado."""
        scan = OtActiveScan()
        res = scan.run_active_scan('10.0.3.0/24')

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')
        self.assertEqual(res['subnet'], '10.0.3.0/24')
        self.assertEqual(res['hosts_found'], 0)
        self.assertEqual(len(res['closed_ports']), 3)

    def test_active_scan_cli_execution(self) -> None:
        """El entrypoint CLI main() ejecuta el escaneo activo con flags sin errores."""
        with running_modbus_server(port=15020, plant_type='water'):
            ret = scan_main(['--target', '127.0.0.1:15020', '--target', '127.0.0.1:15999', '--timeout', '0.1'])
            self.assertEqual(ret, 0)


if __name__ == '__main__':
    unittest.main()
