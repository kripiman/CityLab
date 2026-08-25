#!/usr/bin/env python3
"""attacker/tests/test_attack_time_spoofing.py — Tests para ataque NTP Time Spoofing"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from attacker.attack_ntp_time_spoofing import NtpTimeSpoofingAttack, main as ntp_main
from network.historian import HistorianTSDB


class TestTimeSpoofingAttack(unittest.TestCase):

    def test_ntp_time_spoofing_execution_persists_offset(self) -> None:
        """Verifica que el ataque inyecte muestras con timestamp manipulado en el Historian TSDB."""
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        db_path = Path(temp_db.name)
        self.addCleanup(self._cleanup, str(db_path))

        historian = HistorianTSDB(db_path=db_path)
        self.addCleanup(historian.close)

        attacker = NtpTimeSpoofingAttack(historian=historian)
        offset = 7200.0  # +2 horas
        res = attacker.execute_time_desync_attack(offset_seconds=offset)

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'ENGINE_DIRECT')
        self.assertEqual(res['clock_offset_sec'], offset)
        self.assertEqual(res['records_written'], 1)
        self.assertTrue(res['siem_blinded'])

        # Mutación observable en la base de datos de telemetría SQLite
        rows = historian.query(sector='water', field='t1_level')
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]['ts'], res['spoofed_timestamp'], delta=0.5)

    def test_ntp_time_spoofing_cli(self) -> None:
        """Verifica ejecución CLI."""
        rc = ntp_main(['--offset', '3600'])
        self.assertEqual(rc, 0)

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
