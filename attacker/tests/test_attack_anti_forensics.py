#!/usr/bin/env python3
"""attacker/tests/test_attack_anti_forensics.py — Tests para ataque Historian Anti-Forensics"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from attacker.attack_historian_anti_forensics import HistorianAntiForensicsAttack, main as anti_forensics_main
from network.historian import HistorianTSDB


class TestAntiForensicsAttack(unittest.TestCase):

    def test_anti_forensics_execution_wipes_records(self) -> None:
        """Verifica que el ataque purgue físicamente los registros de telemetría de la base de datos."""
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        db_path = Path(temp_db.name)
        self.addCleanup(self._cleanup, str(db_path))

        historian = HistorianTSDB(db_path=db_path)
        self.addCleanup(historian.close)

        attacker = HistorianAntiForensicsAttack(historian=historian)
        res = attacker.execute_log_tampering()

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'ENGINE_DIRECT')
        self.assertEqual(res['records_wiped'], 1)
        self.assertTrue(res['historian_cleared'])

        # Mutación observable en el datastore SQLite
        remaining = historian.query(sector='water')
        self.assertEqual(len(remaining), 0)

    def test_anti_forensics_cli(self) -> None:
        """Verifica ejecución CLI con DB temporal."""
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        db_path = Path(temp_db.name)
        self.addCleanup(self._cleanup, str(db_path))

        rc = anti_forensics_main(['--db-path', str(db_path)])
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
