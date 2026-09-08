#!/usr/bin/env python3
"""attacker/tests/test_attack_stuxnet.py — Pruebas unitarias y E2E para ataque Stuxnet Telemetry Replay"""
from __future__ import annotations

import os
import unittest
from attacker.attack_stuxnet_replay import StuxnetReplayAttack, main as stuxnet_main
from network.historian import HistorianTSDB
from plc.tests._emulator_harness import running_modbus_server


class TestStuxnetAttack(unittest.TestCase):

    _modbus_port = 15020

    def test_stuxnet_replay_socket_divergence_e2e(self) -> None:
        """Verifica que el ataque sabotee el PLC vía Modbus mientras el Historian recibe replay normal (Divergencia)."""
        db_path = '/tmp/stuxnet_test_db.db'
        self.addCleanup(self._cleanup, db_path)
        historian = HistorianTSDB(db_path)

        with running_modbus_server(port=self._modbus_port, plant_type='water'):
            attacker = StuxnetReplayAttack()
            attacker.record_normal_baseline(samples=3)

            res = attacker.execute_replay_and_sabotage(
                historian,
                sabotage_duration=3,
                host='127.0.0.1',
                port=self._modbus_port,
                sabotage_value=0.1
            )

            self.assertEqual(res['status'], 'SUCCESS')
            self.assertEqual(res['mode'], 'SOCKET_LIVE')
            self.assertEqual(res['replayed_samples'], 3)
            self.assertEqual(res['real_process_val'], 0.1)
            self.assertNotEqual(res['real_process_val'], res['historian_last_val'])
            self.assertTrue(res['divergence_detected'])
            self.assertTrue(res['real_process_sabotaged'])

    def test_stuxnet_replay_tabletop_fallback(self) -> None:
        """Si el PLC no está activo, el ataque activa el modo TABLETOP_FALLBACK documentado."""
        db_path = '/tmp/stuxnet_fallback_db.db'
        self.addCleanup(self._cleanup, db_path)
        historian = HistorianTSDB(db_path)

        attacker = StuxnetReplayAttack()
        attacker.record_normal_baseline(samples=3)

        res = attacker.execute_replay_and_sabotage(
            historian,
            sabotage_duration=3,
            host='127.0.0.1',
            port=59998,
            sabotage_value=0.1
        )

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'TABLETOP_FALLBACK')
        self.assertTrue(res['divergence_detected'])
        self.assertTrue(res['real_process_sabotaged'])

    def test_stuxnet_main_cli(self) -> None:
        """El entrypoint CLI main() ejecuta el vector replay contra el puerto de test sin errores."""
        db_path = '/tmp/stuxnet_cli_db.db'
        self.addCleanup(self._cleanup, db_path)

        with running_modbus_server(port=self._modbus_port, plant_type='water'):
            ret = stuxnet_main(['--port', str(self._modbus_port), '--duration', '2', '--db', db_path])
            self.assertEqual(ret, 0)

    @staticmethod
    def _cleanup(path: str) -> None:
        for ext in ['', '-wal', '-shm']:
            p = path + ext
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


if __name__ == '__main__':
    unittest.main()
