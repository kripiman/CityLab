#!/usr/bin/env python3
"""network/scada_server.py — Servidor SCADA Central / Historian en DMZ (10.0.2.20)

Funcionalidad:
  - Polling periódico por Modbus/TCP hacia los 4 PLCs OT (Water, Gas, Elec, Transport).
  - Persiste telemetría en historian TSDB embebido (SQLite WAL) — Fase 1.
  - RBAC / PAM por roles (auditor / operator / engineer) — Fase 2.
  - Expone un servidor HTTP / API JSON en puerto 8080 para monitoreo y ataque (DMZ).
  - Endpoints:
      GET /                     — telemetría en tiempo real (JSON)
      GET /api/telemetry         — alias del anterior
      GET /api/history           — histórico de campos (?sector=water&field=status&limit=200)
      GET /api/history/snapshot  — snapshots completos (?sector=water&limit=50)
      GET /api/whoami            — identidad y rol del token presentado
      GET /health                — liveness probe (sin auth)
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Tuple, Optional, List
from urllib.parse import urlparse, parse_qs

from network.historian import HistorianTSDB
from network.rbac import _rbac
from network.scada_ha import SCADAPrimarySecondaryCluster

try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    from pymodbus.client.sync import ModbusTcpClient

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][SCADA_SERVER] %(message)s')
LOGGER = logging.getLogger('scada_server')

# Configuración de sondeo de infraestructura crítica primaria (IEC 62443 Nivel 2).
# Alcance estricto (ERS RF-06.2): 'water', 'gas', 'elec', 'transport'.
# NOTA DE DISEÑO PEDAGÓGICO / AUDITORÍA:
# Los activos secundarios de campo (h_plc_hosp 10.0.3.15, h_desal 10.0.3.16, h_lighting 10.0.3.17)
# disponen de daemons Modbus reales en la Celda OT y son monitoreados de forma desacoplada
# por el Visualizador 2D (viz_server.py + fed_viz_bridge.py). Su omisión en el loop de polling
# primario de SCADA es un diseño educativo intencional (Loss of Primary SCADA Visibility)
# conforme a la especificación ERS RF-06.2 y escenario CTF F-06.
PLC_CONFIGS = {
    'water':     (os.getenv('PLC_WATER_HOST', '10.0.3.10'), int(os.getenv('PLC_WATER_PORT', '502'))),
    'gas':       (os.getenv('PLC_GAS_HOST', '10.0.3.12'), int(os.getenv('PLC_GAS_PORT', '502'))),
    'elec':      (os.getenv('PLC_ELEC_HOST', '10.0.3.13'), int(os.getenv('PLC_ELEC_PORT', '502'))),
    'transport': (os.getenv('PLC_TRANSPORT_HOST', '10.0.3.14'), int(os.getenv('PLC_TRANSPORT_PORT', '502'))),
}

# Activos secundarios de campo atacables / controlables
SECONDARY_PLC_CONFIGS = {
    'hospital':  (os.getenv('PLC_HOSP_HOST', '10.0.3.15'), int(os.getenv('PLC_HOSP_PORT', '502'))),
    'desal':     (os.getenv('PLC_DESAL_HOST', '10.0.3.16'), int(os.getenv('PLC_DESAL_PORT', '502'))),
    'lighting':  (os.getenv('PLC_LIGHTING_HOST', '10.0.3.17'), int(os.getenv('PLC_LIGHTING_PORT', '502'))),
}

# Estado global SCADA (telemetría en tiempo real)
scada_state: Dict[str, Any] = {
    'last_update': 0.0,
    'sectors': {}
}

# Historian TSDB embebido (Fase 1) — persiste cada snapshot de polling
_historian: HistorianTSDB = HistorianTSDB()

# Cluster de Alta Disponibilidad DCS HA (Fase 6)
_ha_cluster: SCADAPrimarySecondaryCluster = SCADAPrimarySecondaryCluster(
    node_role=os.getenv('HA_ROLE', 'PRIMARY'),
    peer_url=os.getenv('HA_PEER_URL', 'http://127.0.0.1:8081' if os.getenv('ENABLE_HA_PEER', '0') == '1' else '')
)

LOSS_OF_VIEW_THRESHOLD = 3
_consecutive_failures: Dict[str, int] = {sector: 0 for sector in PLC_CONFIGS}

SECTOR_UNIT_IDS: Dict[str, int] = {
    'water':     1,
    'gas':       2,
    'elec':      3,
    'transport': 4,
    'hospital':  5,
    'desal':     1,
    'lighting':  1,
}

USE_MODBUS_PROXY = os.getenv('USE_MODBUS_PROXY', '0') == '1'
MODBUS_PROXY_HOST = os.getenv('MODBUS_PROXY_HOST', '10.0.2.20')
MODBUS_PROXY_PORT = int(os.getenv('MODBUS_PROXY_PORT', '15020'))


def poll_plcs_once() -> Dict[str, Any]:
    """Ejecuta una ronda individual de consulta a los PLCs OT (directo o vía DPI proxy)."""
    timestamp = time.time()
    sector_data = {}

    for sector, (direct_ip, direct_port) in PLC_CONFIGS.items():
        ip = MODBUS_PROXY_HOST if USE_MODBUS_PROXY else direct_ip
        port = MODBUS_PROXY_PORT if USE_MODBUS_PROXY else direct_port
        unit_id = SECTOR_UNIT_IDS.get(sector, 1)
        client = ModbusTcpClient(ip, port=port, timeout=1.0)
        try:
            if client.connect():
                try:
                    rr = client.read_coils(0, 4, unit=unit_id)
                except TypeError:
                    rr = client.read_coils(0, 4, slave=unit_id)
                if rr and not rr.isError():
                    _consecutive_failures[sector] = 0
                    sector_data[sector] = {
                        'status': 'ONLINE',
                        'coils': [bool(b) for b in rr.bits[:4]],
                        'start_cmd': bool(rr.bits[0]),
                        'stop_cmd': bool(rr.bits[1]),
                        'actuator_running': bool(rr.bits[2]),
                        'fault': bool(rr.bits[3]),
                        'consecutive_failures': 0
                    }
                else:
                    _consecutive_failures[sector] += 1
                    status = 'LOSS_OF_VIEW' if _consecutive_failures[sector] >= LOSS_OF_VIEW_THRESHOLD else 'ERROR_READ'
                    sector_data[sector] = {'status': status, 'consecutive_failures': _consecutive_failures[sector]}
                client.close()
            else:
                _consecutive_failures[sector] += 1
                status = 'LOSS_OF_VIEW' if _consecutive_failures[sector] >= LOSS_OF_VIEW_THRESHOLD else 'UNREACHABLE'
                sector_data[sector] = {'status': status, 'consecutive_failures': _consecutive_failures[sector]}
        except Exception as exc:
            _consecutive_failures[sector] += 1
            status = 'LOSS_OF_VIEW' if _consecutive_failures[sector] >= LOSS_OF_VIEW_THRESHOLD else 'EXCEPTION'
            sector_data[sector] = {'status': status, 'detail': str(exc), 'consecutive_failures': _consecutive_failures[sector]}

    scada_state['last_update'] = timestamp
    scada_state['sectors'] = sector_data

    # Fase 1 — Persistir snapshots en historian TSDB
    for sector, data in sector_data.items():
        try:
            _historian.write_snapshot(sector, data, timestamp)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning('[Historian] Error al escribir snapshot %s: %s', sector, exc)
    return sector_data


def poll_plcs() -> None:
    """Hilo de fondo que consulta periódicamente los PLCs OT."""
    while True:
        poll_plcs_once()
        time.sleep(2.0)


def _modbus_write_coil(client: ModbusTcpClient, addr: int, value: bool, unit_id: int) -> Any:
    try:
        return client.write_coil(addr, bool(value), unit=unit_id)
    except TypeError:
        return client.write_coil(addr, bool(value), slave=unit_id)


def _modbus_write_register(client: ModbusTcpClient, addr: int, value: int, unit_id: int) -> Any:
    try:
        return client.write_register(addr, int(value), unit=unit_id)
    except TypeError:
        return client.write_register(addr, int(value), slave=unit_id)


def _normalize_target(target_raw: str) -> List[str]:
    raw = (target_raw or 'all').strip().lower()
    if raw.startswith('sector_'):
        raw = raw[7:]
    if raw in ('power', 'electricity'):
        raw = 'elec'
    if raw == 'all':
        return list(PLC_CONFIGS.keys())
    if raw in PLC_CONFIGS or raw in SECONDARY_PLC_CONFIGS:
        return [raw]
    for key in list(PLC_CONFIGS.keys()) + list(SECONDARY_PLC_CONFIGS.keys()):
        if key in raw:
            return [key]
    return [raw]


def _determine_control_coils(sector: str, action: str, body: Dict[str, Any]) -> Tuple[Dict[int, bool], Dict[int, int]]:
    """Determina los coils y registros a escribir según el sector y la acción.

    Retorna:
      (coils_to_write: Dict[int, bool], registers_to_write: Dict[int, int])
    """
    coils: Dict[int, bool] = {}
    regs: Dict[int, int] = {}

    # 1. Soporte explícito para escrituras de bajo nivel
    if 'coils' in body and isinstance(body['coils'], list):
        for idx, val in enumerate(body['coils']):
            coils[idx] = bool(val)
        return coils, regs
    if 'coil' in body and 'value' in body:
        coils[int(body['coil'])] = bool(body['value'])
        return coils, regs
    if 'address' in body and 'value' in body:
        addr = int(body['address'])
        val = body['value']
        act_lower = str(action).lower()
        if 'register' in act_lower or 'hr' in act_lower or 'holding' in act_lower:
            regs[addr] = int(val)
        else:
            coils[addr] = bool(val)
        return coils, regs

    # 2. Acciones semánticas de alto nivel
    act = str(action).strip().upper()

    # Emergencia o parada general
    if act in ('EMERGENCY_SHUTDOWN', 'SHUTDOWN', 'TRIP_ALL'):
        coils[0] = False
        coils[1] = True
        return coils, regs

    if act in ('RESET', 'FAULT_RESET', 'CLEAR'):
        coils[0] = False
        coils[1] = False
        return coils, regs

    if act in ('FAULT', 'INJECT_FAULT'):
        coils[0] = True
        coils[1] = True
        return coils, regs

    # Sector: Water (bomba P-101)
    if sector == 'water':
        if act in ('START', 'START_PUMP', 'RUN', 'ON', 'ENABLE', '1', 'TRUE'):
            coils[0] = True
            coils[1] = False
        elif act in ('STOP', 'STOP_PUMP', 'OFF', 'DISABLE', '0', 'FALSE', 'TRIP'):
            coils[0] = False
            coils[1] = True

    # Sector: Gas (válvula XV-201: OPEN = gas fluye, CLOSE = corte)
    elif sector == 'gas':
        if act in ('OPEN', 'OPEN_VALVE', 'START', 'RUN', 'ON', 'ENABLE', '1', 'TRUE'):
            coils[0] = True
            coils[1] = False
        elif act in ('CLOSE', 'CLOSE_VALVE', 'STOP', 'OFF', 'DISABLE', '0', 'FALSE', 'TRIP'):
            coils[0] = False
            coils[1] = True

    # Sector: Elec (disyuntor CB-52: CLOSE = circuito cerrado/energizado, TRIP/OPEN = desconexión)
    elif sector == 'elec':
        if act in ('CLOSE', 'CLOSE_BREAKER', 'START', 'RUN', 'ON', 'ENABLE', '1', 'TRUE'):
            coils[0] = True
            coils[1] = False
        elif act in ('TRIP', 'OPEN', 'OPEN_BREAKER', 'STOP', 'OFF', 'DISABLE', '0', 'FALSE'):
            coils[0] = False
            coils[1] = True

    # Sector: Transport (barrera/semáforo: OPEN_GATE = paso abierto, CLOSE_GATE = paso cerrado)
    elif sector == 'transport':
        if act in ('OPEN_GATE', 'OPEN', 'START', 'RUN', 'ON', 'ENABLE', '1', 'TRUE'):
            coils[0] = True
            coils[1] = False
        elif act in ('CLOSE_GATE', 'CLOSE', 'STOP', 'OFF', 'DISABLE', '0', 'FALSE', 'TRIP'):
            coils[0] = False
            coils[1] = True

    # Sectores secundarios (hospital, desal, lighting, etc.) o genéricos
    else:
        if act in ('START', 'OPEN', 'CLOSE_BREAKER', 'RUN', 'ON', 'ENABLE', '1', 'TRUE'):
            coils[0] = True
            coils[1] = False
        elif act in ('STOP', 'CLOSE', 'TRIP', 'OPEN_BREAKER', 'OFF', 'DISABLE', '0', 'FALSE'):
            coils[0] = False
            coils[1] = True

    if not coils and not regs and act == 'WRITE_COIL':
        coils[0] = True
        coils[1] = False

    return coils, regs


def execute_modbus_control(
    action: str,
    target: str = 'all',
    body_extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Ejecuta una acción de control escribiendo directamente sobre los coils Modbus del PLC correspondiente."""
    body = body_extra or {}
    targets = _normalize_target(target)
    results: Dict[str, Any] = {}
    all_configs = dict(PLC_CONFIGS)
    all_configs.update(SECONDARY_PLC_CONFIGS)
    timestamp = time.time()

    any_connected = False

    for sec in targets:
        coils_to_write, regs_to_write = _determine_control_coils(sec, action, body)
        if not coils_to_write and not regs_to_write:
            results[sec] = {'status': 'SKIPPED', 'reason': f"Unrecognized action '{action}' for sector '{sec}'"}
            continue

        cfg = all_configs.get(sec)
        if not cfg:
            results[sec] = {'status': 'UNKNOWN_TARGET', 'reason': f"No PLC config for sector '{sec}'"}
            continue

        direct_ip, direct_port = cfg
        ip = MODBUS_PROXY_HOST if USE_MODBUS_PROXY else direct_ip
        port = MODBUS_PROXY_PORT if USE_MODBUS_PROXY else direct_port
        unit_id = SECTOR_UNIT_IDS.get(sec, 1)

        client = ModbusTcpClient(ip, port=port, timeout=0.25)
        connected = False
        try:
            connected = bool(client.connect())
        except Exception as exc:
            LOGGER.debug("Error conectando a PLC %s (%s:%d): %s", sec, ip, port, exc)
            connected = False

        if connected:
            any_connected = True
            sec_res: Dict[str, Any] = {'connected': True, 'coils_written': {}, 'registers_written': {}}
            try:
                for addr, val in coils_to_write.items():
                    rr = _modbus_write_coil(client, addr, val, unit_id)
                    sec_res['coils_written'][addr] = not (rr and rr.isError())
                for addr, val in regs_to_write.items():
                    rr = _modbus_write_register(client, addr, val, unit_id)
                    sec_res['registers_written'][addr] = not (rr and rr.isError())
                sec_res['status'] = 'SUCCESS'
                LOGGER.info("Control ejecutado en PLC %s (%s:%d): %s -> coils=%s regs=%s",
                            sec, ip, port, action, coils_to_write, regs_to_write)
            except Exception as exc:
                LOGGER.warning("Error escribiendo en PLC %s: %s", sec, exc)
                sec_res['status'] = 'WRITE_ERROR'
                sec_res['error'] = str(exc)
            finally:
                try:
                    client.close()
                except Exception:
                    pass
            results[sec] = sec_res
        else:
            LOGGER.warning("PLC %s inalcanzable en %s:%d (actualizando estado local)", sec, ip, port)
            results[sec] = {
                'status': 'PLC_UNREACHABLE',
                'ip': ip,
                'port': port,
                'coils_intended': coils_to_write,
                'registers_intended': regs_to_write
            }

        # Actualizar telemetría local de forma inmediata
        if sec in scada_state['sectors'] and isinstance(scada_state['sectors'][sec], dict):
            sec_state = scada_state['sectors'][sec]
            if 0 in coils_to_write:
                sec_state['start_cmd'] = coils_to_write[0]
            if 1 in coils_to_write:
                sec_state['stop_cmd'] = coils_to_write[1]
            if 0 in coils_to_write and 1 in coils_to_write:
                sec_state['fault'] = bool(coils_to_write[0] and coils_to_write[1])
            if 'coils' in sec_state and isinstance(sec_state['coils'], list):
                while len(sec_state['coils']) < 4:
                    sec_state['coils'].append(False)
                for c_addr, c_val in coils_to_write.items():
                    if c_addr < len(sec_state['coils']):
                        sec_state['coils'][c_addr] = c_val
            # Si el PLC no está conectado (modo test/simulación), reflejar actuator_running optimista
            if not connected:
                if coils_to_write.get(0) and not coils_to_write.get(1):
                    sec_state['actuator_running'] = True
                elif coils_to_write.get(1) and not coils_to_write.get(0):
                    sec_state['actuator_running'] = False
        else:
            scada_state['sectors'][sec] = {
                'status': 'ONLINE' if connected else 'SIMULATED',
                'coils': [coils_to_write.get(0, False), coils_to_write.get(1, False),
                          coils_to_write.get(0, False) and not coils_to_write.get(1, False),
                          bool(coils_to_write.get(0) and coils_to_write.get(1))],
                'start_cmd': coils_to_write.get(0, False),
                'stop_cmd': coils_to_write.get(1, False),
                'actuator_running': coils_to_write.get(0, False) and not coils_to_write.get(1, False),
                'fault': bool(coils_to_write.get(0) and coils_to_write.get(1)),
                'consecutive_failures': 0 if connected else 1
            }

        # Registrar evento en Historian
        try:
            _historian.write(sec, 'control_action', action, timestamp)
        except Exception:
            pass

    scada_state['last_update'] = timestamp

    # Si conectamos a algún PLC real, lanzar sondeo rápido para refrescar coils
    if any_connected:
        try:
            threading.Thread(target=poll_plcs_once, daemon=True).start()
        except Exception:
            pass

    return {
        'status': 'SUCCESS',
        'action_executed': action,
        'target': target,
        'results': results
    }


class SCADAAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass  # Suppress per-request HTTP access log noise

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        # --- Fase 2: RBAC auth (preserva STRICT_AUTH toggle para CTF) ---
        if parsed.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return

        auth_header = self.headers.get('Authorization')
        role, http_code = _rbac.resolve(auth_header)
        if role is None:
            self.send_response(http_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'unauthorized', 'code': http_code}).encode())
            return

        if not _rbac.is_authorized(role, parsed.path):
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'forbidden', 'role': role, 'path': parsed.path}).encode())
            return

        # --- Routing con rol verificado ---

        if parsed.path in ('/', '/api/telemetry'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-SCADA-Role', role)  # Fase 2: informar rol al cliente
            self.end_headers()
            response = json.dumps(scada_state, indent=2)
            self.wfile.write(response.encode('utf-8'))

        elif parsed.path == '/api/history':
            # Fase 1: Consulta histórica de campos individuales.
            # Params: ?sector=<name>&field=<field>&limit=<int>&since=<epoch>
            sector = qs.get('sector', [None])[0]
            field = qs.get('field', [None])[0]
            limit = int(qs.get('limit', ['200'])[0])
            since = float(qs.get('since', ['0'])[0]) or None
            if not sector:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "sector param required"}')
                return
            rows = _historian.query(sector=sector, field=field, since=since, limit=limit)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'sector': sector, 'field': field, 'rows': rows}, indent=2).encode('utf-8'))

        elif parsed.path == '/api/history/snapshot':
            # Fase 1: Snapshots completos por sector (útil para HMI y análisis forense).
            # Params: ?sector=<name>&limit=<int>&since=<epoch>
            sector = qs.get('sector', [None])[0]
            limit = int(qs.get('limit', ['50'])[0])
            since = float(qs.get('since', ['0'])[0]) or None
            if not sector:
                # Sin sector: retorna último snapshot de todos los sectores
                result = {s: _historian.last(s) for s in _historian.sectors()}
            else:
                result = _historian.query_snapshots(sector=sector, since=since, limit=limit)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))

        elif parsed.path in ('/api/control', '/api/control/read', '/api/control/write'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-SCADA-Role', role)
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'SUCCESS', 'role': role, 'path': parsed.path}).encode('utf-8'))

        elif parsed.path == '/api/whoami':
            # Fase 2: introspección de identidad y rol del token
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'role': role, 'strict_auth': os.getenv('STRICT_AUTH', '0') == '1'}).encode())

        elif parsed.path == '/api/ha/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(_ha_cluster.get_cluster_status()).encode('utf-8'))

        elif parsed.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b'{}'
        try:
            body_json = json.loads(post_body.decode('utf-8'))
        except Exception:
            body_json = {}

        if parsed.path == '/api/ha/heartbeat':
            sender_role = body_json.get('role', 'UNKNOWN')
            resp = _ha_cluster.receive_heartbeat(sender_role=sender_role)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return
        elif parsed.path == '/api/ha/sync':
            state_snapshot = body_json.get('state', {})
            if state_snapshot:
                scada_state['sectors'].update(state_snapshot)
                scada_state['last_update'] = time.time()
                _ha_cluster.sync_state(state_snapshot)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'SYNC_OK'}).encode('utf-8'))
            return

        auth_header = self.headers.get('Authorization')
        role, http_code = _rbac.resolve(auth_header)
        if role is None:
            self.send_response(http_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'unauthorized', 'code': http_code}).encode())
            return

        if not _rbac.is_authorized(role, parsed.path):
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'forbidden', 'role': role, 'path': parsed.path}).encode())
            return

        if parsed.path in ('/api/control', '/api/control/write'):
            action = body_json.get('action', 'write')
            target = body_json.get('target', 'all')
            ctrl_result = execute_modbus_control(action=action, target=target, body_extra=body_json)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-SCADA-Role', role)
            self.end_headers()
            resp_payload = {
                'status': 'SUCCESS',
                'action_executed': action,
                'target': target,
                'role': role,
                'details': ctrl_result.get('results', {})
            }
            self.wfile.write(json.dumps(resp_payload).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def run_http_server(port: int = 8080) -> None:
    host = '0.0.0.0'
    server = HTTPServer((host, port), SCADAAPIHandler)
    LOGGER.info('Servidor SCADA Central listo en http://%s:%d', host, port)
    server.serve_forever()


def main() -> int:
    LOGGER.info('Iniciando Servidor SCADA Central / Historian (DMZ)...')
    t = threading.Thread(target=poll_plcs, daemon=True)
    t.start()
    _ha_cluster.start_ha_monitor()
    try:
        run_http_server(8080)
    except KeyboardInterrupt:
        LOGGER.info('Apagando Servidor SCADA Central...')
        _ha_cluster.stop_ha_monitor()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
