#!/usr/bin/env python3
"""Tests de integración para el Historian TSDB embebido — Fase 1.

Valida:
  - Escritura y consulta de puntos de telemetría individuales.
  - Escritura y consulta de snapshots completos de sector.
  - API HTTP /api/history y /api/history/snapshot en scada_server.
  - Persistencia: los datos sobreviven a una nueva instancia de HistorianTSDB.
  - Retención: prune() elimina puntos excedentes manteniendo los más recientes.
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path

from network.historian import HistorianTSDB
from network.scada_server import SCADAAPIHandler, _historian, scada_state


class TestHistorianTSDB(unittest.TestCase):
    """Tests unitarios del módulo historian.py (HistorianTSDB)."""

    def setUp(self) -> None:
        # DB temporal aislada por test
        self._db_fd, self._db_path = tempfile.mkstemp(suffix='.db', prefix='historian_test_')
        os.close(self._db_fd)
        self.h = HistorianTSDB(db_path=Path(self._db_path))

    def tearDown(self) -> None:
        self.h.close()
        try:
            os.unlink(self._db_path)
            # SQLite WAL puede dejar archivos .db-wal y .db-shm
            for ext in ('-wal', '-shm'):
                p = self._db_path + ext
                if os.path.exists(p):
                    os.unlink(p)
        except OSError:
            pass

    def test_write_and_query_field(self) -> None:
        """write() persiste puntos individuales y query() los recupera correctamente."""
        t0 = time.time() - 10
        self.h.write('water', 'status', 'ONLINE', timestamp=t0)
        self.h.write('water', 'status', 'UNREACHABLE', timestamp=t0 + 1)
        self.h.write('water', 'coil_0', 1.0, timestamp=t0 + 2)

        rows = self.h.query('water', field='status', limit=10)
        self.assertEqual(len(rows), 2, "Debe haber 2 puntos de campo 'status'")
        # ORDER BY ts DESC — el más reciente primero
        self.assertEqual(rows[0]['value'], 'UNREACHABLE')
        self.assertEqual(rows[1]['value'], 'ONLINE')

    def test_write_snapshot_and_query_snapshot(self) -> None:
        """write_snapshot() persiste el estado completo y query_snapshots() lo recupera."""
        t0 = time.time()
        data = {'status': 'ONLINE', 'coils': [True, False, True, False], 'fault': False}
        self.h.write_snapshot('elec', data, timestamp=t0)

        snaps = self.h.query_snapshots('elec', limit=5)
        self.assertEqual(len(snaps), 1, "Debe existir exactamente 1 snapshot")
        self.assertEqual(snaps[0]['sector'], 'elec')
        self.assertEqual(snaps[0]['data']['status'], 'ONLINE')
        self.assertEqual(snaps[0]['ts'], t0)

    def test_last_returns_most_recent_snapshot(self) -> None:
        """last() devuelve el snapshot más reciente de un sector."""
        t0 = time.time()
        self.h.write_snapshot('gas', {'status': 'ONLINE'}, timestamp=t0 - 5)
        self.h.write_snapshot('gas', {'status': 'ERROR_READ'}, timestamp=t0)

        last = self.h.last('gas')
        self.assertIsNotNone(last)
        self.assertEqual(last['data']['status'], 'ERROR_READ')

    def test_last_returns_none_for_unknown_sector(self) -> None:
        """last() devuelve None cuando el sector no tiene datos."""
        result = self.h.last('nonexistent_sector')
        self.assertIsNone(result)

    def test_sectors_list(self) -> None:
        """sectors() lista exactamente los sectores con datos registrados."""
        self.h.write_snapshot('water', {'status': 'ONLINE'})
        self.h.write_snapshot('transport', {'status': 'ONLINE'})
        sectors = self.h.sectors()
        self.assertIn('water', sectors)
        self.assertIn('transport', sectors)
        self.assertNotIn('gas', sectors)

    def test_persistence_across_instances(self) -> None:
        """Datos persisten al cerrar y reabrir HistorianTSDB (same DB file)."""
        t0 = time.time()
        self.h.write_snapshot('transport', {'status': 'ONLINE', 'fault': False}, timestamp=t0)
        self.h.close()

        # Nueva instancia apuntando al mismo archivo
        h2 = HistorianTSDB(db_path=Path(self._db_path))
        snaps = h2.query_snapshots('transport', limit=5)
        h2.close()

        self.assertEqual(len(snaps), 1, "Snapshot debe persistir tras nueva instancia")
        self.assertEqual(snaps[0]['data']['status'], 'ONLINE')

    def test_prune_keeps_most_recent(self) -> None:
        """prune() elimina puntos más antiguos manteniendo los más recientes."""
        import os as _os
        original_max = _os.getenv('HISTORIAN_MAX_POINTS', '10000')
        # Forzar retención de solo 3 puntos para el test
        import network.historian as hist_mod
        original_limit = hist_mod._MAX_RETENTION_POINTS
        hist_mod._MAX_RETENTION_POINTS = 3

        try:
            t0 = time.time()
            for i in range(5):
                self.h.write('water', 'status', f'STATUS_{i}', timestamp=t0 + i)
            deleted = self.h.prune()
            self.assertEqual(deleted, 2, "Debe eliminar 2 puntos (5 - 3 = 2)")
            rows = self.h.query('water', field='status', limit=10)
            self.assertEqual(len(rows), 3)
            # Los 3 más recientes (STATUS_2, STATUS_3, STATUS_4) deben permanecer
            values = {r['value'] for r in rows}
            self.assertIn('STATUS_4', values)
            self.assertIn('STATUS_3', values)
            self.assertIn('STATUS_2', values)
        finally:
            hist_mod._MAX_RETENTION_POINTS = original_limit

    def test_query_since_filter(self) -> None:
        """query() con parámetro `since` filtra por timestamp correctamente."""
        t0 = time.time() - 100
        self.h.write('gas', 'pressure', 5.0, timestamp=t0)
        self.h.write('gas', 'pressure', 6.0, timestamp=t0 + 50)
        self.h.write('gas', 'pressure', 7.0, timestamp=t0 + 100)

        rows = self.h.query('gas', field='pressure', since=t0 + 40, limit=10)
        self.assertEqual(len(rows), 2, "Debe retornar solo puntos desde t0+40")
        pressures = {r['value'] for r in rows}
        self.assertIn(6.0, pressures)
        self.assertIn(7.0, pressures)
        self.assertNotIn(5.0, pressures)


class TestScadaHistorianHTTPEndpoints(unittest.TestCase):
    """Tests de integración HTTP para los endpoints /api/history del SCADA Server."""

    _server_port = 18081

    @classmethod
    def setUpClass(cls) -> None:
        """Arrancar un servidor HTTP de test con el handler real del SCADA."""
        from http.server import HTTPServer
        import network.rbac as rbac_mod

        # Configurar tokens de test para que el resolver RBAC los reconozca
        os.environ['SCADA_API_TOKEN']      = 'TEST_TOKEN_2026'
        os.environ['SCADA_TOKEN_OPERATOR'] = 'TEST_TOKEN_2026'
        os.environ['SCADA_TOKEN_ENGINEER'] = 'ENG_TOKEN_2026'
        os.environ['SCADA_TOKEN_AUDITOR']  = 'AUDIT_TOKEN_2026'
        os.environ['STRICT_AUTH'] = '0'
        os.environ['SCADA_AD_AUTH'] = '0'
        rbac_mod._rbac.reload()

        # Pre-poblar el historian global con datos sintéticos
        t0 = time.time() - 30
        _historian.write_snapshot('water', {'status': 'ONLINE', 'fault': False, 'coils': [True, False, False, False]}, timestamp=t0)
        _historian.write_snapshot('water', {'status': 'ONLINE', 'fault': False, 'coils': [True, True, False, False]}, timestamp=t0 + 10)
        _historian.write('water', 'pressure', 3.5, timestamp=t0)
        _historian.write('water', 'pressure', 4.0, timestamp=t0 + 10)

        cls._server = HTTPServer(('127.0.0.1', cls._server_port), SCADAAPIHandler)
        cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
        cls._thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._server.shutdown()

    def _get(self, path: str, token: str = 'TEST_TOKEN_2026') -> tuple[int, dict]:
        """Helper: realiza GET con Bearer token y retorna (status_code, json_body)."""
        url = f'http://127.0.0.1:{self._server_port}{path}'
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, {}

    def test_api_history_returns_field_rows(self) -> None:
        """GET /api/history?sector=water retorna filas históricas del sector."""
        status, body = self._get('/api/history?sector=water')
        self.assertEqual(status, 200)
        self.assertIn('rows', body)
        self.assertIsInstance(body['rows'], list)
        self.assertGreater(len(body['rows']), 0, "Debe haber al menos 1 fila histórica")

    def test_api_history_field_filter(self) -> None:
        """GET /api/history?sector=water&field=pressure filtra por campo."""
        status, body = self._get('/api/history?sector=water&field=pressure')
        self.assertEqual(status, 200)
        for row in body['rows']:
            self.assertEqual(row['field'], 'pressure', f"Campo inesperado: {row['field']}")

    def test_api_history_missing_sector_returns_400(self) -> None:
        """GET /api/history sin sector retorna 400."""
        url = f'http://127.0.0.1:{self._server_port}/api/history'
        req = urllib.request.Request(url, headers={'Authorization': 'Bearer TEST_TOKEN_2026'})
        try:
            urllib.request.urlopen(req, timeout=3)
            self.fail("Debe retornar error 400")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_api_history_snapshot_returns_data(self) -> None:
        """GET /api/history/snapshot?sector=water retorna snapshots del sector."""
        status, body = self._get('/api/history/snapshot?sector=water')
        self.assertEqual(status, 200)
        self.assertIsInstance(body, list)
        self.assertGreater(len(body), 0, "Debe haber al menos 1 snapshot")
        self.assertIn('data', body[0])
        self.assertIn('ts', body[0])


if __name__ == '__main__':
    unittest.main()
