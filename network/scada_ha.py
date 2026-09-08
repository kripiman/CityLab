#!/usr/bin/env python3
"""network/scada_ha.py — Redundancia DCS y High Availability Hot-Standby (Fase 6)

Arquitectura de Alta Disponibilidad SCADA (Primary / Secondary Active-Passive Cluster):
  - Heartbeat continuo entre SCADA Primario y SCADA Secundario (Standby).
  - Sincronización automática de estado y registros del proceso OT en tiempo real.
  - Failover automático a Standby ante timeout o caída del Primario.
  - Failback ordenado al recuperar la salud del servidor primario.

Endpoints / Métodos HA:
  - `GET  /api/ha/status`      — Estado del cluster (ROLE: PRIMARY / STANDBY, STATE: HEALTHY / DEGRADED / FAILOVER).
  - `POST /api/ha/sync`        — Endpoint de sincronización de estado de proceso desde Primario hacia Secundario.
  - `POST /api/ha/heartbeat`   — Canal de latido (Heartbeat) entre nodos del cluster.
"""
from __future__ import annotations

import json
import logging
import threading
import time
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

LOGGER = logging.getLogger('scada_ha')

DEFAULT_HEARTBEAT_INTERVAL = 1.0  # segundos
DEFAULT_HEARTBEAT_TIMEOUT  = 3.0  # segundos sin respuesta gatillan failover


class SCADAPrimarySecondaryCluster:
    """Administrador de cluster de Alta Disponibilidad SCADA."""

    def __init__(
        self,
        node_role: str = 'PRIMARY',  # 'PRIMARY' o 'STANDBY'
        peer_url: str = 'http://127.0.0.1:8081',
        heartbeat_timeout: float = DEFAULT_HEARTBEAT_TIMEOUT,
        heartbeat_interval: float = DEFAULT_HEARTBEAT_INTERVAL
    ) -> None:
        self.node_role = node_role.upper()
        self.peer_url = peer_url
        self.heartbeat_timeout = heartbeat_timeout
        self.heartbeat_interval = heartbeat_interval
        
        self.active_role = self.node_role  # 'PRIMARY', 'STANDBY', or 'ACTIVE_STANDBY'
        self.peer_status = 'UNKNOWN'
        self.last_peer_heartbeat = time.time()
        self.is_failover_active = False
        self.synced_state: Dict[str, Any] = {}
        self.last_state_sync: float = 0.0
        
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start_ha_monitor(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        LOGGER.info('[SCADA-HA] Monitor HA iniciado en modo %s (Peer: %s)', self.node_role, self.peer_url)

    def stop_ha_monitor(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def sync_state(self, state: Dict[str, Any]) -> None:
        """Registra y actualiza el snapshot sincronizado del cluster."""
        with self._lock:
            self.synced_state = dict(state)
            self.last_state_sync = time.time()

    def get_synced_state(self) -> Dict[str, Any]:
        """Obtiene el último estado sincronizado almacenado."""
        with self._lock:
            return dict(self.synced_state)

    def receive_heartbeat(self, sender_role: str, state_snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Procesa un heartbeat recibido del peer."""
        with self._lock:
            self.last_peer_heartbeat = time.time()
            self.peer_status = 'ONLINE'
            if state_snapshot:
                self.synced_state = dict(state_snapshot)
                self.last_state_sync = time.time()
            if self.node_role == 'STANDBY' and self.is_failover_active and sender_role == 'PRIMARY':
                # Primario recuperado — failback a modo standby pasivo
                LOGGER.info('[SCADA-HA] Primario recuperado — devolviendo control activo')
                self.is_failover_active = False
                self.active_role = 'STANDBY'
        
        return {
            'status': 'OK',
            'my_role': self.node_role,
            'active_role': self.active_role,
            'timestamp': time.time(),
            'synced_sectors_count': len(self.synced_state)
        }

    def _send_peer_heartbeat(self) -> bool:
        if not self.peer_url or self.node_role == 'STANDALONE':
            return False
        try:
            payload = json.dumps({'role': self.node_role, 'timestamp': time.time()}).encode('utf-8')
            req = urllib.request.Request(
                f"{self.peer_url}/api/ha/heartbeat",
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    with self._lock:
                        self.last_peer_heartbeat = time.time()
                        self.peer_status = 'ONLINE'
                    return True
        except Exception:
            with self._lock:
                self.peer_status = 'UNREACHABLE'
        return False

    def _monitor_loop(self) -> None:
        while self._running:
            self._send_peer_heartbeat()
            
            with self._lock:
                time_since_hb = time.time() - self.last_peer_heartbeat
                if self.node_role == 'STANDBY' and time_since_hb > self.heartbeat_timeout:
                    if not self.is_failover_active:
                        LOGGER.warning(
                            '[SCADA-HA] Primario no responde (%.1fs > %.1fs) — ¡INICIANDO FAILOVER AUTOMÁTICO!',
                            time_since_hb, self.heartbeat_timeout
                        )
                        self.is_failover_active = True
                        self.active_role = 'ACTIVE_STANDBY'
            
            time.sleep(self.heartbeat_interval)

    def get_cluster_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'configured_role': self.node_role,
                'active_role': self.active_role,
                'peer_status': self.peer_status,
                'failover_active': self.is_failover_active,
                'last_peer_heartbeat_ago': round(time.time() - self.last_peer_heartbeat, 2),
                'last_state_sync': self.last_state_sync,
                'synced_sectors_count': len(self.synced_state)
            }
