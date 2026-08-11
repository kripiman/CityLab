#!/usr/bin/env python3
"""network/historian.py — Historian TSDB embebido (Fase 1)

Implementación de Time-Series Database industrial usando SQLite3 con Write-Ahead
Logging (WAL) para alta concurrencia de escrituras. Actúa como capa de persistencia
para el SCADA Server, sustituyendo el almacenamiento JSON en memoria.

Intercambiable con InfluxDB / TimescaleDB mediante la misma interfaz pública:
    historian = HistorianTSDB()
    historian.write(sector, field, value, timestamp)
    historian.query(sector, field, since_ts, limit)
    historian.last(sector)

La interfaz está diseñada para ser drop-in reemplazada por influxdb-client o
psycopg2+TimescaleDB sin cambiar scada_server.py.

Fase 1 / IEC 62443 RF-11: no modifica hallazgos CTF (F-03/F-05/F-06/F-07).
"""
from __future__ import annotations

import sqlite3
import threading
import time
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOGGER = logging.getLogger('historian')

# Ruta por defecto del archivo de base de datos. Sobreescribible vía variable de entorno.
_DEFAULT_DB_PATH = Path(os.getenv('HISTORIAN_DB_PATH', '/tmp/citylab_historian.db'))

# Retención máxima de puntos por sector (evita crecimiento ilimitado sin SIEM externo).
_MAX_RETENTION_POINTS = int(os.getenv('HISTORIAN_MAX_POINTS', '10000'))


class HistorianTSDB:
    """Time-Series historian embebido sobre SQLite WAL.

    Interfaz pública idéntica a la que se usaría con InfluxDB-client o TimescaleDB,
    permitiendo migración sin cambios en scada_server.py.

    Thread-safe: cada hilo usa su propia conexión SQLite (check_same_thread=False).
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self._db_path = Path(db_path) if db_path else _DEFAULT_DB_PATH
        self._lock = threading.Lock()
        self._local = threading.local()
        self._init_db()

    # ------------------------------------------------------------------ #
    #  Conexión por hilo                                                   #
    # ------------------------------------------------------------------ #

    def _conn(self) -> sqlite3.Connection:
        """Retorna conexión SQLite local al hilo actual (lazy init)."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return self._local.conn

    # ------------------------------------------------------------------ #
    #  Inicialización de esquema                                           #
    # ------------------------------------------------------------------ #

    def _init_db(self) -> None:
        """Crea las tablas si no existen. Idempotente."""
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS telemetry (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts        REAL    NOT NULL,
                    sector    TEXT    NOT NULL,
                    field     TEXT    NOT NULL,
                    value     REAL,
                    value_str TEXT
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_telemetry_sector_ts
                ON telemetry (sector, ts DESC)
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS telemetry_raw (
                    id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts     REAL NOT NULL,
                    sector TEXT NOT NULL,
                    data   TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_raw_sector_ts
                ON telemetry_raw (sector, ts DESC)
            ''')
            conn.commit()
        LOGGER.info('[Historian] Base de datos inicializada en %s (SQLite WAL)', self._db_path)

    # ------------------------------------------------------------------ #
    #  Escritura                                                           #
    # ------------------------------------------------------------------ #

    def write(
        self,
        sector: str,
        field: str,
        value: Any,
        timestamp: Optional[float] = None,
    ) -> None:
        """Escribe un punto de telemetría.

        Args:
            sector:    Nombre del sector OT ('water', 'gas', 'elec', 'transport').
            field:     Nombre del campo ('status', 'coil_0', etc.).
            value:     Valor numérico o de cadena.
            timestamp: Epoch UNIX en segundos. Si None, usa time.time().
        """
        ts = timestamp if timestamp is not None else time.time()
        num_val: Optional[float] = None
        str_val: Optional[str] = None
        try:
            num_val = float(value)
        except (TypeError, ValueError):
            str_val = str(value)

        conn = self._conn()
        with self._lock:
            conn.execute(
                'INSERT INTO telemetry (ts, sector, field, value, value_str) VALUES (?,?,?,?,?)',
                (ts, sector, field, num_val, str_val),
            )
            conn.commit()

    def write_snapshot(self, sector: str, data: Dict[str, Any], timestamp: Optional[float] = None) -> None:
        """Escribe el snapshot JSON completo de un sector.

        Permite consultas de telemetría completa por sector y rango temporal.

        Args:
            sector:    Nombre del sector OT.
            data:      Diccionario de datos del sector (como los de scada_state['sectors']).
            timestamp: Epoch UNIX en segundos. Si None, usa time.time().
        """
        import json as _json
        ts = timestamp if timestamp is not None else time.time()
        conn = self._conn()
        with self._lock:
            conn.execute(
                'INSERT INTO telemetry_raw (ts, sector, data) VALUES (?,?,?)',
                (ts, sector, _json.dumps(data)),
            )
            conn.commit()
        # Escribir también campos individuales para queries granulares
        for key, val in data.items():
            if isinstance(val, bool):
                self.write(sector, key, int(val), ts)
            elif isinstance(val, (int, float, str)):
                self.write(sector, key, val, ts)

    # ------------------------------------------------------------------ #
    #  Lectura                                                             #
    # ------------------------------------------------------------------ #

    def query(
        self,
        sector: str,
        field: Optional[str] = None,
        since: Optional[float] = None,
        until: Optional[float] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """Consulta puntos de telemetría históricos.

        Args:
            sector: Sector OT a consultar.
            field:  Campo específico. Si None, devuelve todos los campos.
            since:  Epoch inicio (inclusive). Si None, sin límite inferior.
            until:  Epoch fin (inclusive). Si None, hasta el más reciente.
            limit:  Número máximo de filas devueltas.

        Returns:
            Lista de dicts con keys: ts, sector, field, value.
        """
        clauses = ['sector = ?']
        params: List[Any] = [sector]
        if field:
            clauses.append('field = ?')
            params.append(field)
        if since is not None:
            clauses.append('ts >= ?')
            params.append(since)
        if until is not None:
            clauses.append('ts <= ?')
            params.append(until)
        params.append(limit)
        sql = (
            f"SELECT ts, sector, field, value, value_str FROM telemetry "
            f"WHERE {' AND '.join(clauses)} ORDER BY ts DESC LIMIT ?"
        )
        conn = self._conn()
        rows = conn.execute(sql, params).fetchall()
        return [
            {
                'ts': r['ts'],
                'sector': r['sector'],
                'field': r['field'],
                'value': r['value'] if r['value'] is not None else r['value_str'],
            }
            for r in rows
        ]

    def query_snapshots(
        self,
        sector: str,
        since: Optional[float] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Consulta snapshots completos del sector.

        Returns:
            Lista de dicts con keys: ts, sector, data (dict del snapshot).
        """
        import json as _json
        clauses = ['sector = ?']
        params: List[Any] = [sector]
        if since is not None:
            clauses.append('ts >= ?')
            params.append(since)
        params.append(limit)
        sql = (
            f"SELECT ts, sector, data FROM telemetry_raw "
            f"WHERE {' AND '.join(clauses)} ORDER BY ts DESC LIMIT ?"
        )
        conn = self._conn()
        rows = conn.execute(sql, params).fetchall()
        return [
            {'ts': r['ts'], 'sector': r['sector'], 'data': _json.loads(r['data'])}
            for r in rows
        ]

    def last(self, sector: str) -> Optional[Dict[str, Any]]:
        """Retorna el snapshot más reciente de un sector, o None si no hay datos."""
        results = self.query_snapshots(sector, limit=1)
        return results[0] if results else None

    def sectors(self) -> List[str]:
        """Lista los sectores con datos en el historian."""
        conn = self._conn()
        rows = conn.execute('SELECT DISTINCT sector FROM telemetry_raw ORDER BY sector').fetchall()
        return [r['sector'] for r in rows]

    # ------------------------------------------------------------------ #
    #  Mantenimiento (retención)                                           #
    # ------------------------------------------------------------------ #

    def prune(self) -> int:
        """Elimina puntos excedentes para mantener retención máxima por sector.

        Returns:
            Número total de filas eliminadas.
        """
        deleted = 0
        conn = self._conn()
        with self._lock:
            for (sector,) in conn.execute(
                'SELECT DISTINCT sector FROM telemetry'
            ).fetchall():
                count = conn.execute(
                    'SELECT COUNT(*) FROM telemetry WHERE sector=?', (sector,)
                ).fetchone()[0]
                if count > _MAX_RETENTION_POINTS:
                    to_del = count - _MAX_RETENTION_POINTS
                    conn.execute(
                        '''DELETE FROM telemetry WHERE id IN (
                            SELECT id FROM telemetry WHERE sector=?
                            ORDER BY ts ASC LIMIT ?
                        )''',
                        (sector, to_del),
                    )
                    deleted += to_del
            conn.commit()
        return deleted

    def close(self) -> None:
        """Cierra la conexión del hilo actual."""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
