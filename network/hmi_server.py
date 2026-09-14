#!/usr/bin/env python3
"""network/hmi_server.py — Dashboard HMI Industrial OpenSCADA / Ignition Edge (Fase 5)

Servidor HTTP / Dashboard HMI industrial que proporciona:
  - Diagrama de proceso P&ID (Water, Gas, Electric, Transport).
  - Telemetría en tiempo real desde `scada_server.py` y `historian.py`.
  - Mandos de control manual (START / STOP / TRIP / CLOSE) para operadores OT.
  - Consola de alarmas industriales (Loss of View, Loss of Control, Trip en Cascada).

Alcance de Supervisión y Contexto Pedagógico (ERS RF-06.2 / CTF F-06):
  Supervisa exclusivamente los 4 sectores industriales primarios (water, gas,
  elec, transport). Los activos secundarios de campo (hospital, desal, lighting,
  safety) operan desacoplados del loop SCADA primario para preservar el hallazgo
  pedagógico CTF F-06 (Loss of Primary SCADA Visibility) conforme a ERS RF-06.2.

Endpoints API HMI:
  - `GET  /api/hmi/overview`  — Estado consolidado P&ID de todos los sectores.
  - `GET  /api/hmi/alarms`    — Registro activo de alarmas de proceso.
  - `POST /api/hmi/control`   — Envío de mandos operacionales al SCADA Server.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Any, Dict, List, Optional, Sequence

from network.historian import HistorianTSDB

LOGGER = logging.getLogger('hmi_server')

DEFAULT_HMI_PORT = 8085
DEFAULT_SCADA_URL = 'http://127.0.0.1:8080'

# NOTA DE DISEÑO PEDAGÓGICO / AUDITORÍA (ERS RF-06.2 / CTF F-06):
# El servidor HMI supervisa intencionalmente sólo los 4 sectores primarios
# (water, gas, elec, transport) alineado con scada_server.py (PLC_CONFIGS).
# Los activos secundarios de campo (hospital, desal, lighting, safety) operan
# desacoplados del loop SCADA primario para preservar el hallazgo pedagógico
# CTF F-06 (Loss of Primary SCADA Visibility) conforme a ERS RF-06.2.


def format_rbac_token(token: Optional[str], default_role: str = 'engineer') -> str:
    """Asegura que el token posea el formato <role>:<token> para compatibilidad STRICT_AUTH=1."""
    raw = (token or '').strip()
    if raw.startswith('Bearer '):
        raw = raw[len('Bearer '):].strip()
    if not raw:
        raw = 'ENG_TOKEN_2026'
    if ':' not in raw:
        raw = f"{default_role}:{raw}"
    return raw


class IndustrialHmiEngine:
    """Motor de estado HMI para consolidación P&ID, tendencias históricas y gestión de alarmas.

    Supervisa los 4 sectores primarios (water, gas, elec, transport) según ERS RF-06.2.
    """

    def __init__(
        self,
        scada_url: str = DEFAULT_SCADA_URL,
        historian: Optional[HistorianTSDB] = None,
        auth_token: Optional[str] = None
    ) -> None:
        self.scada_url = scada_url
        self.historian = historian if historian is not None else HistorianTSDB()
        raw_token = auth_token or os.getenv('SCADA_API_TOKEN', os.getenv('SCADA_TOKEN_ENGINEER', 'ENG_TOKEN_2026'))
        self.auth_token = format_rbac_token(raw_token, default_role='engineer')
        self.alarms: List[Dict[str, Any]] = []

    def fetch_scada_status(self) -> Dict[str, Any]:
        """Consulta el estado actual del servidor SCADA con cabecera de autenticación RBAC."""
        try:
            req = urllib.request.Request(
                f"{self.scada_url}/api/telemetry",
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            LOGGER.debug('Error consultando SCADA server: %s', e)
        return {'status': 'OFFLINE', 'error': 'No se pudo conectar al SCADA Server'}

    def get_overview(self) -> Dict[str, Any]:
        scada_data = self.fetch_scada_status()
        sectors = scada_data.get('sectors', scada_data)

        self.alarms = []
        is_loss_of_view = False

        for sector_name in ['water', 'gas', 'elec', 'transport']:
            sec_info = sectors.get(sector_name, {}) if isinstance(sectors, dict) else {}
            if isinstance(sec_info, dict) and sec_info.get('status') == 'LOSS_OF_VIEW':
                is_loss_of_view = True
                self.alarms.append({
                    'alarm_id': f'ALM-LOV-{sector_name.upper()}',
                    'sector': sector_name,
                    'severity': 'CRITICAL',
                    'message': f'Pérdida de Visibilidad SCADA (Loss-of-View) en sector {sector_name}'
                })

        scada_connected = scada_data.get('status') != 'OFFLINE'
        has_critical_alarm = (not scada_connected) or is_loss_of_view

        water_sec = {'t1_level': 10.0, 't2_level': 15.0, 'p1_state': True}
        if isinstance(sectors.get('water'), dict):
            water_sec.update(sectors['water'])
            if 'actuator_running' in sectors['water']:
                water_sec['p1_state'] = sectors['water']['actuator_running']

        gas_sec = {'pressure_psi': 145.0, 'valve_open': True}
        if isinstance(sectors.get('gas'), dict):
            gas_sec.update(sectors['gas'])
            if 'actuator_running' in sectors['gas']:
                gas_sec['valve_open'] = sectors['gas']['actuator_running']

        elec_sec = {'grid_voltage': 230.0, 'breaker_closed': True}
        if isinstance(sectors.get('elec'), dict):
            elec_sec.update(sectors['elec'])
            if 'actuator_running' in sectors['elec']:
                elec_sec['breaker_closed'] = sectors['elec']['actuator_running']

        transport_sec = {'traffic_light': 2, 'gate_open': True}
        if isinstance(sectors.get('transport'), dict):
            transport_sec.update(sectors['transport'])
            if 'actuator_running' in sectors['transport']:
                transport_sec['gate_open'] = sectors['transport']['actuator_running']

        return {
            'hmi_brand': 'CityLab OpenSCADA / Ignition Edge Emulator',
            'scada_connected': scada_connected,
            'process_diagram': {
                'water_sector': water_sec,
                'gas_sector': gas_sec,
                'elec_sector': elec_sec,
                'transport_sector': transport_sec,
            },
            'alarms': self.alarms,
            'active_alarms_count': len(self.alarms),
            'system_health': 'ALARM_CRITICAL' if has_critical_alarm else 'NORMAL'
        }

    def get_history(
        self,
        sector: str = 'water',
        field: Optional[str] = None,
        since: Optional[float] = None,
        limit: int = 200
    ) -> Dict[str, Any]:
        """Consulta series de tiempo históricas directamente a HistorianTSDB en SQLite WAL."""
        history_points = self.historian.query(sector=sector, field=field, since=since, limit=limit)
        return {
            'sector': sector,
            'field': field,
            'count': len(history_points),
            'history': history_points
        }

    def trigger_control_action(self, action: str, target: str, role_token: Optional[str] = None) -> Dict[str, Any]:
        """Envía una acción de control al SCADA Server con token RBAC."""
        token = format_rbac_token(role_token or self.auth_token, default_role='engineer')
        try:
            payload = json.dumps({'action': action, 'target': target}).encode('utf-8')
            req = urllib.request.Request(
                f"{self.scada_url}/api/control",
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                body = json.loads(resp.read().decode('utf-8'))
                return {'success': True, 'scada_response': body}
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class HmiRequestHandler(BaseHTTPRequestHandler):

    engine = IndustrialHmiEngine()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == '/api/hmi/overview':
            self._send_json(self.engine.get_overview())
        elif path == '/api/hmi/alarms':
            self._send_json({'alarms': self.engine.alarms})
        elif path in ('/api/history', '/api/hmi/history'):
            sector = params.get('sector', ['water'])[0]
            field = params.get('field', [None])[0]
            since_val = float(params['since'][0]) if 'since' in params else None
            limit_val = int(params['limit'][0]) if 'limit' in params else 200
            self._send_json(self.engine.get_history(sector=sector, field=field, since=since_val, limit=limit_val))
        elif path == '/' or path == '/index.html':
            html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>CityLab Industrial HMI — OpenSCADA / Ignition Edge</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #090d14;
      color: #cfd8dc;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      padding: 16px;
      line-height: 1.4;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #1c2538;
      padding-bottom: 12px;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 10px;
    }
    h1 {
      font-size: 1.3rem;
      color: #00e5ff;
      letter-spacing: 0.5px;
    }
    .sub {
      color: #78909c;
      font-size: 0.78rem;
    }
    .badge-bar {
      display: flex;
      gap: 10px;
      align-items: center;
    }
    .badge {
      padding: 4px 10px;
      border-radius: 4px;
      font-weight: bold;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .badge-ok { background: #003314; color: #00e676; border: 1px solid #00e676; }
    .badge-warn { background: #332600; color: #ffab00; border: 1px solid #ffab00; }
    .badge-crit { background: #330009; color: #ff1744; border: 1px solid #ff1744; animation: blink 1s infinite; }
    @keyframes blink { 50% { opacity: 0.4; } }
    .btn {
      background: #141b29;
      color: #00e5ff;
      border: 1px solid #00e5ff;
      padding: 4px 10px;
      border-radius: 4px;
      cursor: pointer;
      font-family: inherit;
      font-size: 0.75rem;
      transition: all 0.2s;
    }
    .btn:hover { background: #00e5ff; color: #080a10; }
    .btn-danger { color: #ff5252; border-color: #ff5252; }
    .btn-danger:hover { background: #ff5252; color: #080a10; }
    .btn-success { color: #00e676; border-color: #00e676; }
    .btn-success:hover { background: #00e676; color: #080a10; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 14px;
      margin-bottom: 16px;
    }
    .card {
      background: #0f1522;
      border: 1px solid #1a233a;
      border-radius: 6px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .card:hover { border-color: #00e5ff; }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      border-bottom: 1px solid #192236;
      padding-bottom: 6px;
    }
    .card-title {
      font-size: 0.88rem;
      font-weight: 600;
      color: #90caf9;
    }
    .pid-wrap {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 125px;
      margin: 6px 0;
      background: #080c14;
      border: 1px solid #151d30;
      border-radius: 4px;
    }
    .telemetry-table {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 5px;
      background: #0b101c;
      padding: 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      margin-bottom: 8px;
    }
    .lbl { color: #78909c; }
    .val { color: #eceff1; font-weight: bold; text-align: right; }
    .ctl-bar {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
      padding-top: 6px;
      border-top: 1px dashed #1c273e;
    }
    .alarm-panel {
      background: #0f1522;
      border: 1px solid #1a233a;
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 16px;
    }
    .alarm-panel h3 {
      font-size: 0.88rem;
      color: #ffab00;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    table.alarm-tbl {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.75rem;
    }
    table.alarm-tbl th, table.alarm-tbl td {
      padding: 6px 8px;
      text-align: left;
      border-bottom: 1px solid #192236;
    }
    table.alarm-tbl th { color: #78909c; background: #0b101c; }
    .sev-critical { color: #ff1744; font-weight: bold; }
    .sev-warning { color: #ffab00; font-weight: bold; }
    #toast {
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #192236;
      border: 1px solid #00e5ff;
      color: #00e5ff;
      padding: 10px 16px;
      border-radius: 4px;
      font-size: 0.8rem;
      display: none;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
      z-index: 1000;
    }
    #raw-data {
      display: none;
      background: #06090f;
      border: 1px solid #1a233a;
      border-radius: 4px;
      padding: 10px;
      color: #00e676;
      font-size: 0.72rem;
      max-height: 220px;
      overflow-y: auto;
      margin-top: 10px;
    }
    .notice-box {
      font-size: 0.72rem;
      color: #90a4ae;
      background: #0d1320;
      border-left: 3px solid #00e5ff;
      padding: 6px 10px;
      margin-bottom: 14px;
      border-radius: 0 4px 4px 0;
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>🏭 CityLab Industrial HMI — OpenSCADA / Ignition Edge</h1>
      <div class="sub">Diagrama de Proceso P&ID y Mando Operacional OT (IEC 62443 DMZ :8085)</div>
    </div>
    <div class="badge-bar">
      <span id="badge-scada" class="badge badge-ok">SCADA ONLINE</span>
      <span id="badge-health" class="badge badge-ok">NORMAL</span>
      <button class="btn" onclick="toggleRaw()">JSON</button>
    </div>
  </header>

  <div class="notice-box">
    ℹ️ <strong>Alcance de Supervisión Primaria (ERS RF-06.2 / CTF F-06):</strong> Este HMI supervisa directamente los 4 sectores industriales primarios de la red OT (Water, Gas, Elec, Transport). Los activos secundarios de campo (Hospital, Desal, Lighting, Safety) operan de forma desacoplada y son visualizados de forma complementaria por el Visualizador 2D.
  </div>

  <div class="grid">
    <!-- SECTOR 1: AGUA P&ID -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">💧 P&ID Proceso de Agua (SWaT)</span>
        <span id="badge-water" class="badge badge-ok">OK</span>
      </div>
      <div class="pid-wrap">
        <svg width="300" height="115" viewBox="0 0 300 115">
          <!-- Tuberías -->
          <path d="M70 65 L120 65 L120 45 L150 45" fill="none" stroke="#2a3b5c" stroke-width="4"/>
          <path d="M210 65 L260 65" fill="none" stroke="#2a3b5c" stroke-width="4"/>
          <!-- Tanque T1 -->
          <rect x="15" y="25" width="55" height="65" rx="3" fill="#101826" stroke="#455a64" stroke-width="2"/>
          <rect id="pid-water-t1-fill" x="17" y="55" width="51" height="33" rx="1" fill="#00b0ff" opacity="0.8"/>
          <text x="42" y="20" fill="#90a4ae" font-size="9" text-anchor="middle">TK-101</text>
          <!-- Bomba P101 -->
          <circle id="pid-pump-body" cx="135" cy="65" r="14" fill="#132035" stroke="#00e676" stroke-width="2"/>
          <path id="pid-pump-rotor" d="M135 55 L135 75 M125 65 L145 65" stroke="#00e676" stroke-width="2"/>
          <text x="135" y="90" fill="#90a4ae" font-size="8" text-anchor="middle">P-101</text>
          <!-- Tanque T2 -->
          <rect x="155" y="25" width="55" height="65" rx="3" fill="#101826" stroke="#455a64" stroke-width="2"/>
          <rect id="pid-water-t2-fill" x="157" y="50" width="51" height="38" rx="1" fill="#00e5ff" opacity="0.8"/>
          <text x="182" y="20" fill="#90a4ae" font-size="9" text-anchor="middle">TK-102</text>
          <!-- Transmisor Nivel LIT-101 -->
          <circle cx="250" cy="40" r="11" fill="#101826" stroke="#00e5ff" stroke-width="1.5"/>
          <text x="250" y="43" fill="#00e5ff" font-size="7" text-anchor="middle">LT</text>
        </svg>
      </div>
      <div class="telemetry-table">
        <span class="lbl">Nivel TK-101:</span><span id="hmi-water-t1" class="val">10.0 m³</span>
        <span class="lbl">Nivel TK-102:</span><span id="hmi-water-t2" class="val">15.0 m³</span>
        <span class="lbl">Bomba P-101:</span><span id="hmi-water-p1" class="val">RUNNING</span>
        <span class="lbl">Estado PLC:</span><span id="hmi-water-status" class="val">ONLINE</span>
      </div>
      <div class="ctl-bar">
        <button class="btn btn-success" onclick="sendCommand('START', 'water')">ARRANCAR P-101</button>
        <button class="btn btn-danger" onclick="sendCommand('STOP', 'water')">PARAR P-101</button>
      </div>
    </div>

    <!-- SECTOR 2: GAS P&ID -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">🔥 P&ID Distribución de Gas</span>
        <span id="badge-gas" class="badge badge-ok">OK</span>
      </div>
      <div class="pid-wrap">
        <svg width="300" height="115" viewBox="0 0 300 115">
          <!-- Tubería principal -->
          <line x1="20" y1="60" x2="280" y2="60" stroke="#37474f" stroke-width="6"/>
          <line x1="20" y1="60" x2="280" y2="60" stroke="#ffab00" stroke-width="2" stroke-dasharray="6,4"/>
          <!-- Manómetro de presión PT-201 -->
          <circle cx="85" cy="50" r="28" fill="#101826" stroke="#455a64" stroke-width="2"/>
          <circle cx="85" cy="50" r="23" fill="#080c14"/>
          <path d="M68 62 A18 18 0 1 1 102 62" fill="none" stroke="#263238" stroke-width="4"/>
          <line id="pid-gas-needle" x1="85" y1="50" x2="85" y2="33" stroke="#ff5252" stroke-width="2" stroke-linecap="round"/>
          <circle cx="85" cy="50" r="3" fill="#fff"/>
          <text x="85" y="90" fill="#90a4ae" font-size="8" text-anchor="middle">PT-201 (PSI)</text>
          <!-- Válvula de control solenoide XV-201 -->
          <g transform="translate(195, 45)">
            <polygon id="pid-valve-l" points="0,5 20,15 0,25" fill="#00e676"/>
            <polygon id="pid-valve-r" points="40,5 20,15 40,25" fill="#00e676"/>
            <rect x="17" y="0" width="6" height="15" fill="#78909c"/>
            <circle cx="20" cy="0" r="4" fill="#00e676"/>
          </g>
          <text x="215" y="90" fill="#90a4ae" font-size="8" text-anchor="middle">XV-201</text>
        </svg>
      </div>
      <div class="telemetry-table">
        <span class="lbl">Presión Línea:</span><span id="hmi-gas-press" class="val">145.0 PSI</span>
        <span class="lbl">Válvula XV-201:</span><span id="hmi-gas-valve" class="val">ABIERTA</span>
        <span class="lbl">Límite Alta:</span><span class="val">180.0 PSI</span>
        <span class="lbl">Estado PLC:</span><span id="hmi-gas-status" class="val">ONLINE</span>
      </div>
      <div class="ctl-bar">
        <button class="btn btn-success" onclick="sendCommand('OPEN', 'gas')">ABRIR XV-201</button>
        <button class="btn btn-danger" onclick="sendCommand('CLOSE', 'gas')">CERRAR XV-201</button>
      </div>
    </div>

    <!-- SECTOR 3: ELEC P&ID -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">⚡ P&ID Subestación Eléctrica</span>
        <span id="badge-elec" class="badge badge-ok">OK</span>
      </div>
      <div class="pid-wrap">
        <svg width="300" height="115" viewBox="0 0 300 115">
          <!-- Barra de Distribución Busbar 13.8kV -->
          <line x1="30" y1="35" x2="270" y2="35" stroke="#ffeb3b" stroke-width="4"/>
          <text x="150" y="25" fill="#ffeb3b" font-size="8" text-anchor="middle">BUSBAR 13.8 kV</text>
          <!-- Transformador T1 -->
          <circle cx="80" cy="65" r="14" fill="none" stroke="#00e5ff" stroke-width="2"/>
          <circle cx="80" cy="80" r="14" fill="none" stroke="#00e5ff" stroke-width="2"/>
          <line x1="80" y1="35" x2="80" y2="51" stroke="#ffeb3b" stroke-width="2"/>
          <text x="80" y="105" fill="#90a4ae" font-size="8" text-anchor="middle">XFMR-1</text>
          <!-- Interruptor de Potencia CB-52 -->
          <g id="pid-elec-cb-grp" transform="translate(190, 48)">
            <rect x="0" y="0" width="36" height="32" rx="3" fill="#101826" stroke="#455a64" stroke-width="2"/>
            <line id="pid-elec-cb-line" x1="18" y1="5" x2="18" y2="27" stroke="#00e676" stroke-width="3"/>
            <circle cx="18" cy="5" r="3" fill="#00e676"/>
            <circle cx="18" cy="27" r="3" fill="#00e676"/>
          </g>
          <text x="208" y="95" fill="#90a4ae" font-size="8" text-anchor="middle">CB-52 (FEEDER)</text>
        </svg>
      </div>
      <div class="telemetry-table">
        <span class="lbl">Tensión Red:</span><span id="hmi-elec-volt" class="val">230.0 V</span>
        <span class="lbl">Interruptor CB-52:</span><span id="hmi-elec-breaker" class="val">CERRADO</span>
        <span class="lbl">Frecuencia:</span><span class="val">60.0 Hz</span>
        <span class="lbl">Estado PLC:</span><span id="hmi-elec-status" class="val">ONLINE</span>
      </div>
      <div class="ctl-bar">
        <button class="btn btn-success" onclick="sendCommand('CLOSE', 'elec')">CERRAR CB-52</button>
        <button class="btn btn-danger" onclick="sendCommand('TRIP', 'elec')">DISPARAR CB-52</button>
      </div>
    </div>

    <!-- SECTOR 4: TRANSPORTE P&ID -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">🚦 P&ID Control de Tráfico Urbano</span>
        <span id="badge-trans" class="badge badge-ok">OK</span>
      </div>
      <div class="pid-wrap">
        <svg width="300" height="115" viewBox="0 0 300 115">
          <!-- Vía de tren y cruce peatonal -->
          <line x1="20" y1="75" x2="280" y2="75" stroke="#37474f" stroke-width="4"/>
          <line x1="20" y1="85" x2="280" y2="85" stroke="#37474f" stroke-width="4"/>
          <!-- Durmientes -->
          <line x1="60" y1="70" x2="60" y2="90" stroke="#455a64" stroke-width="2"/>
          <line x1="120" y1="70" x2="120" y2="90" stroke="#455a64" stroke-width="2"/>
          <line x1="180" y1="70" x2="180" y2="90" stroke="#455a64" stroke-width="2"/>
          <line x1="240" y1="70" x2="240" y2="90" stroke="#455a64" stroke-width="2"/>
          <!-- Semáforo Semafórico -->
          <rect x="70" y="20" width="22" height="48" rx="4" fill="#080c14" stroke="#455a64" stroke-width="2"/>
          <circle id="hmi-tl-red" cx="81" cy="28" r="6" fill="#330009"/>
          <circle id="hmi-tl-amber" cx="81" cy="44" r="6" fill="#332600"/>
          <circle id="hmi-tl-green" cx="81" cy="60" r="6" fill="#00e676"/>
          <text x="81" y="80" fill="#90a4ae" font-size="8" text-anchor="middle">S-101</text>
          <!-- Barrera de paso a nivel -->
          <circle cx="210" cy="65" r="7" fill="#455a64"/>
          <line id="hmi-gate-bar" x1="210" y1="65" x2="250" y2="35" stroke="#ff1744" stroke-width="3" stroke-linecap="round"/>
          <text x="210" y="85" fill="#90a4ae" font-size="8" text-anchor="middle">BARRERA</text>
        </svg>
      </div>
      <div class="telemetry-table">
        <span class="lbl">Fase Semáforo:</span><span id="hmi-trans-light" class="val">VERDE</span>
        <span class="lbl">Paso a Nivel:</span><span id="hmi-trans-gate" class="val">ABIERTO</span>
        <span class="lbl">Modo Mando:</span><span class="val">NTCIP / MODBUS</span>
        <span class="lbl">Estado PLC:</span><span id="hmi-trans-status" class="val">ONLINE</span>
      </div>
      <div class="ctl-bar">
        <button class="btn btn-danger" onclick="sendCommand('CLOSE_GATE', 'transport')">BAJAR BARRERA</button>
        <button class="btn btn-success" onclick="sendCommand('OPEN_GATE', 'transport')">SUBIR BARRERA</button>
      </div>
    </div>
  </div>

  <!-- CONSOLA DE ALARMAS INDUSTRIALES -->
  <div class="alarm-panel">
    <h3>
      <span>🚨 Consola de Alarmas de Proceso e Incidentes SCADA</span>
      <span id="alarm-count-badge" class="badge badge-ok">0 ACTIVAS</span>
    </h3>
    <table class="alarm-tbl">
      <thead>
        <tr>
          <th>ID Alarma</th>
          <th>Sector</th>
          <th>Severidad</th>
          <th>Mensaje / Evento de Proceso</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody id="alarm-tbody">
        <tr><td colspan="5" style="color: #78909c; text-align: center;">Sin alarmas activas en el proceso.</td></tr>
      </tbody>
    </table>
  </div>

  <div id="toast">Comando enviado al SCADA Server...</div>
  <pre id="raw-data"></pre>

  <script>
    function toggleRaw() {
      const el = document.getElementById('raw-data');
      el.style.display = el.style.display === 'block' ? 'none' : 'block';
    }

    function showToast(msg, isError) {
      const toast = document.getElementById('toast');
      toast.innerText = msg;
      toast.style.borderColor = isError ? '#ff1744' : '#00e5ff';
      toast.style.color = isError ? '#ff1744' : '#00e5ff';
      toast.style.display = 'block';
      setTimeout(() => { toast.style.display = 'none'; }, 3000);
    }

    function sendCommand(action, target) {
      showToast(`Enviando mando ${action} a sector ${target}...`, false);
      fetch('/api/hmi/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action, target: target })
      })
      .then(r => r.json())
      .then(res => {
        if (res.success) {
          showToast(`✅ Mando ${action} ejecutado con éxito`, false);
          updateHmi();
        } else {
          showToast(`❌ Fallo: ${res.error || 'No autorizado'}`, true);
        }
      })
      .catch(err => {
        showToast(`❌ Error de conexión: ${err}`, true);
      });
    }

    function updateHmi() {
      fetch('/api/hmi/overview')
        .then(r => r.json())
        .then(data => {
          document.getElementById('raw-data').innerText = JSON.stringify(data, null, 2);

          // Estado global y salud
          const scadaBadge = document.getElementById('badge-scada');
          const healthBadge = document.getElementById('badge-health');
          if (data.scada_connected) {
            scadaBadge.className = 'badge badge-ok';
            scadaBadge.innerText = 'SCADA ONLINE';
          } else {
            scadaBadge.className = 'badge badge-crit';
            scadaBadge.innerText = 'SCADA OFFLINE';
          }

          if (data.system_health === 'ALARM_CRITICAL') {
            healthBadge.className = 'badge badge-crit';
            healthBadge.innerText = 'ALARMA CRÍTICA';
          } else {
            healthBadge.className = 'badge badge-ok';
            healthBadge.innerText = 'NORMAL';
          }

          const proc = data.process_diagram || {};

          // 1. Agua
          const w = proc.water_sector || {};
          const wLov = w.status === 'LOSS_OF_VIEW';
          const t1Val = Number(w.t1_level !== undefined ? w.t1_level : 10.0);
          const t2Val = Number(w.t2_level !== undefined ? w.t2_level : 15.0);
          document.getElementById('hmi-water-t1').innerText = t1Val.toFixed(1) + ' m³';
          document.getElementById('hmi-water-t2').innerText = t2Val.toFixed(1) + ' m³';
          const fill1 = Math.min(60, Math.max(5, (t1Val / 20.0) * 60));
          const fill2 = Math.min(60, Math.max(5, (t2Val / 20.0) * 60));
          const t1Fill = document.getElementById('pid-water-t1-fill');
          const t2Fill = document.getElementById('pid-water-t2-fill');
          if (t1Fill) { t1Fill.setAttribute('height', fill1); t1Fill.setAttribute('y', 25 + (65 - fill1)); }
          if (t2Fill) { t2Fill.setAttribute('height', fill2); t2Fill.setAttribute('y', 25 + (65 - fill2)); }
          const pRunning = Boolean(w.p1_state || w.actuator_running);
          document.getElementById('hmi-water-p1').innerText = pRunning ? 'RUNNING' : 'STOPPED';
          document.getElementById('hmi-water-status').innerText = w.status || 'ONLINE';
          const bWater = document.getElementById('badge-water');
          bWater.className = wLov ? 'badge badge-crit' : (pRunning ? 'badge badge-ok' : 'badge badge-warn');
          bWater.innerText = wLov ? 'LOSS OF VIEW' : (pRunning ? 'OK' : 'STOP');
          const rotor = document.getElementById('pid-pump-rotor');
          if (rotor) rotor.setAttribute('stroke', pRunning ? '#00e676' : '#ff5252');

          // 2. Gas
          const g = proc.gas_sector || {};
          const gLov = g.status === 'LOSS_OF_VIEW';
          const press = Number(g.pressure_psi || 145.0);
          document.getElementById('hmi-gas-press').innerText = press.toFixed(1) + ' PSI';
          const vOpen = Boolean(g.valve_open || g.actuator_running);
          document.getElementById('hmi-gas-valve').innerText = vOpen ? 'ABIERTA' : 'CERRADA';
          document.getElementById('hmi-gas-status').innerText = g.status || 'ONLINE';
          const bGas = document.getElementById('badge-gas');
          bGas.className = gLov ? 'badge badge-crit' : (press > 180 ? 'badge badge-crit' : 'badge badge-ok');
          bGas.innerText = gLov ? 'LOSS OF VIEW' : (press > 180 ? 'ALTA PRESIÓN' : 'OK');
          const gNeedle = document.getElementById('pid-gas-needle');
          if (gNeedle) {
            const deg = -60 + (Math.min(220, Math.max(0, press)) / 220.0) * 120;
            gNeedle.setAttribute('transform', `rotate(${deg}, 85, 50)`);
          }
          const vl = document.getElementById('pid-valve-l');
          const vr = document.getElementById('pid-valve-r');
          if (vl && vr) {
            const vCol = vOpen ? '#00e676' : '#ff5252';
            vl.setAttribute('fill', vCol);
            vr.setAttribute('fill', vCol);
          }

          // 3. Electric
          const e = proc.elec_sector || {};
          const eLov = e.status === 'LOSS_OF_VIEW';
          const volt = Number(e.grid_voltage || 230.0);
          document.getElementById('hmi-elec-volt').innerText = volt.toFixed(1) + ' V';
          const cbClosed = Boolean(e.breaker_closed !== undefined ? e.breaker_closed : !e.blackout);
          document.getElementById('hmi-elec-breaker').innerText = cbClosed ? 'CERRADO' : 'DISPARADO';
          document.getElementById('hmi-elec-status').innerText = e.status || 'ONLINE';
          const bElec = document.getElementById('badge-elec');
          bElec.className = eLov ? 'badge badge-crit' : (cbClosed ? 'badge badge-ok' : 'badge badge-crit');
          bElec.innerText = eLov ? 'LOSS OF VIEW' : (cbClosed ? 'OK' : 'TRIPPED');
          const cbLine = document.getElementById('pid-elec-cb-line');
          if (cbLine) cbLine.setAttribute('stroke', cbClosed ? '#00e676' : '#ff5252');

          // 4. Transport
          const t = proc.transport_sector || {};
          const tLov = t.status === 'LOSS_OF_VIEW';
          const tlRaw = t.traffic_light;
          const tlFmt = typeof tlRaw === 'number' ? (tlRaw === 2 ? 'VERDE' : (tlRaw === 1 ? 'ÁMBAR' : 'ROJO')) : (tlRaw || 'VERDE');
          document.getElementById('hmi-trans-light').innerText = tlFmt;
          const tlRed = document.getElementById('hmi-tl-red');
          const tlAmb = document.getElementById('hmi-tl-amber');
          const tlGrn = document.getElementById('hmi-tl-green');
          const isRed = tlFmt === 'ROJO' || tlRaw === 0 || tlRaw === 'RED';
          const isAmb = tlFmt === 'ÁMBAR' || tlRaw === 1 || tlRaw === 'AMBER';
          const isGrn = !isRed && !isAmb;
          if (tlRed) tlRed.setAttribute('fill', isRed ? '#ff1744' : '#330009');
          if (tlAmb) tlAmb.setAttribute('fill', isAmb ? '#ffab00' : '#332600');
          if (tlGrn) tlGrn.setAttribute('fill', isGrn ? '#00e676' : '#003314');
          const gateOpen = Boolean(t.gate_open !== undefined ? t.gate_open : (t.railway_gate === 'OPEN'));
          document.getElementById('hmi-trans-gate').innerText = gateOpen ? 'ABIERTO' : 'CERRADO';
          document.getElementById('hmi-trans-status').innerText = t.status || 'ONLINE';
          const bTrans = document.getElementById('badge-trans');
          bTrans.className = tLov ? 'badge badge-crit' : 'badge badge-ok';
          bTrans.innerText = tLov ? 'LOSS OF VIEW' : 'OK';
          const gateBar = document.getElementById('hmi-gate-bar');
          if (gateBar) {
            if (gateOpen) {
              gateBar.setAttribute('x2', '250'); gateBar.setAttribute('y2', '35');
            } else {
              gateBar.setAttribute('x2', '250'); gateBar.setAttribute('y2', '65');
            }
          }

          // Alarmas activas
          const alarms = data.alarms || [];
          const countBadge = document.getElementById('alarm-count-badge');
          countBadge.innerText = alarms.length + ' ACTIVAS';
          countBadge.className = alarms.length > 0 ? 'badge badge-crit' : 'badge badge-ok';

          const tbody = document.getElementById('alarm-tbody');
          if (alarms.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="color: #78909c; text-align: center;">Sin alarmas activas en el proceso.</td></tr>';
          } else {
            tbody.innerHTML = alarms.map(a => `
              <tr>
                <td><strong>${a.alarm_id || 'ALM'}</strong></td>
                <td>${a.sector ? a.sector.toUpperCase() : 'SISTEMA'}</td>
                <td class="${a.severity === 'CRITICAL' ? 'sev-critical' : 'sev-warning'}">${a.severity}</td>
                <td>${a.message}</td>
                <td><span class="badge badge-crit">ACTIVA</span></td>
              </tr>
            `).join('');
          }
        })
        .catch(err => {
          console.error("HMI polling error:", err);
          document.getElementById('badge-health').className = 'badge badge-crit';
          document.getElementById('badge-health').innerText = 'ERROR CONEXIÓN';
        });
    }

    setInterval(updateHmi, 2000);
    updateHmi();
  </script>
</body>
</html>"""
            self._send_html(html)
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self) -> None:
        if self.path == '/api/hmi/control':
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length)
            try:
                data = json.loads(body_bytes.decode('utf-8'))
                auth_hdr = self.headers.get('Authorization', f'Bearer {self.engine.auth_token}')
                token = format_rbac_token(auth_hdr, default_role='engineer')
                res = self.engine.trigger_control_action(
                    action=data.get('action', ''),
                    target=data.get('target', ''),
                    role_token=token
                )
                self._send_json(res)
            except Exception as e:
                self._send_json({'success': False, 'error': str(e)}, status=400)
        else:
            self.send_error(404, 'Not Found')

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass  # Quiet logging for server requests


class ThreadedHmiServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="CityLab Industrial HMI Server (OpenSCADA / Ignition Edge)")
    parser.add_argument("--host", default="0.0.0.0", help="Host / IP de escucha (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_HMI_PORT, help=f"Puerto HTTP (default: {DEFAULT_HMI_PORT})")
    parser.add_argument("--scada-url", default=DEFAULT_SCADA_URL, help=f"URL del SCADA Server (default: {DEFAULT_SCADA_URL})")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][HMI] %(message)s')
    engine = IndustrialHmiEngine(scada_url=args.scada_url)
    HmiRequestHandler.engine = engine
    server = ThreadedHmiServer((args.host, args.port), HmiRequestHandler)
    LOGGER.info("Servidor HMI Industrial escuchando en http://%s:%d (SCADA: %s)", args.host, args.port, args.scada_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Apagando Servidor HMI...")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
