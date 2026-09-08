#!/usr/bin/env python3
"""network/viz_server.py — Capa de Visualización Presentacional 2D / 3D (Fase 9)

Servidor HTTP / SSE (Server-Sent Events) / WebSocket de visualización gráfica urbana:
  - Renderizado 2D/3D del estado ciberfísico de la ciudad (Water, Gas, Electric, Transport).
  - Suscriptor pasivo de eventos HELICS y SCADA Server.
  - Streaming en tiempo real de contingencias (Apagón hospital, desborde SWaT, cierre de válvula).
"""
from __future__ import annotations

import json
import logging
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Any, Dict, List, Optional, Sequence

LOGGER = logging.getLogger('viz_server')

DEFAULT_VIZ_PORT = 8090


class CityVisualizerStateEngine:
    """Motor de estado de visualización presentacional 2D/3D."""

    def __init__(self) -> None:
        self.state: Dict[str, Any] = {
            'timestamp': time.time(),
            'city_sectors': {
                'water': {'tank_level': 10.0, 'pump_running': True, 'alert': False},
                'gas': {'pressure_psi': 145.0, 'valve_open': True, 'alert': False},
                'elec': {'grid_voltage': 230.0, 'blackout': False},
                'transport': {'traffic_light': 'GREEN', 'railway_gate': 'OPEN'},
                'hospital': {'powered': True, 'generator_active': False},
                'desal': {'power_kw': 45.0, 'tank_level_pct': 75.0, 'pump_trip': False},
                'lighting': {'power_kw': 120.0},
                'safety': {'sis_trip': False}
            }
        }
        self.frame_history: List[Dict[str, Any]] = []

    def update_sector_state(self, sector: str, payload: Dict[str, Any]) -> bool:
        if sector in self.state['city_sectors']:
            self.state['city_sectors'][sector].update(payload)
            self.state['timestamp'] = time.time()
            frame_copy = json.loads(json.dumps(self.state))
            self.frame_history.append(frame_copy)
            if len(self.frame_history) > 100:
                self.frame_history.pop(0)
            return True
        LOGGER.warning("[VIZ] Sector desconocido rechazado: %s", sector)
        return False

    def get_render_frame(self) -> Dict[str, Any]:
        return dict(self.state)

    def get_history_frames(self) -> List[Dict[str, Any]]:
        return list(self.frame_history)


class VizRequestHandler(BaseHTTPRequestHandler):

    engine = CityVisualizerStateEngine()

    def do_GET(self) -> None:
        if self.path == '/api/viz/frame':
            self._send_json(self.engine.get_render_frame())
        elif self.path == '/api/viz/history':
            self._send_json({'frames': self.engine.get_history_frames()})
        elif self.path == '/' or self.path == '/index.html':
            html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>CityLab 2D/3D City Visualizer</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #080a10;
      color: #e0e6ed;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      padding: 16px;
      line-height: 1.4;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #1f293d;
      padding-bottom: 12px;
      margin-bottom: 16px;
    }
    h1 {
      font-size: 1.4rem;
      color: #00e5ff;
      letter-spacing: 0.5px;
    }
    .sub {
      color: #78909c;
      font-size: 0.8rem;
    }
    .status-bar {
      display: flex;
      gap: 12px;
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
      background: #161b26;
      color: #00e5ff;
      border: 1px solid #00e5ff;
      padding: 5px 12px;
      border-radius: 4px;
      cursor: pointer;
      font-family: inherit;
      font-size: 0.75rem;
    }
    .btn:hover { background: #00e5ff; color: #080a10; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
      margin-bottom: 16px;
    }
    .card {
      background: #0f131d;
      border: 1px solid #1c2436;
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
      border-bottom: 1px solid #161c2b;
      padding-bottom: 6px;
    }
    .card-title {
      font-size: 0.9rem;
      font-weight: 600;
      color: #90caf9;
    }
    .canvas-wrap {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 120px;
      margin: 6px 0;
    }
    .readouts {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      background: #090c14;
      padding: 6px;
      border-radius: 4px;
      font-size: 0.75rem;
    }
    .metric-label { color: #607d8b; }
    .metric-val { color: #cfd8dc; font-weight: bold; text-align: right; }
    #raw-container {
      display: none;
      margin-top: 12px;
      border: 1px solid #263238;
      border-radius: 6px;
      background: #05070a;
      padding: 12px;
    }
    #viewport {
      color: #00e676;
      font-size: 0.75rem;
      max-height: 250px;
      overflow-y: auto;
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>🌃 CityLab 2D/3D Presentational Visualizer</h1>
      <div class="sub">IEC 62443 DMZ Real-Time Cyber-Physical Urban Twin & Threat Operations</div>
    </div>
    <div class="status-bar">
      <div id="badge-soc" class="badge badge-ok">SISTEMA NORMAL</div>
      <div id="badge-sis" class="badge badge-ok">SIS SIL-3: OK</div>
      <button class="btn" onclick="toggleRaw()">JSON Telemetría</button>
    </div>
  </header>

  <div class="grid">
    <!-- 1. AGUA -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">💧 Tratamiento de Agua (SWaT)</span>
        <span id="badge-water" class="badge badge-ok">OK</span>
      </div>
      <div class="canvas-wrap">
        <svg width="220" height="110" viewBox="0 0 220 110">
          <rect x="20" y="20" width="60" height="70" rx="3" fill="#121a29" stroke="#37474f" stroke-width="2"/>
          <rect id="svg-water-fill-t1" x="22" y="55" width="56" height="33" rx="2" fill="#00b0ff" opacity="0.75"/>
          <text x="50" y="15" fill="#78909c" font-size="9" text-anchor="middle">Tanque T1</text>
          <rect x="110" y="20" width="60" height="70" rx="3" fill="#121a29" stroke="#37474f" stroke-width="2"/>
          <rect id="svg-water-fill-t2" x="112" y="45" width="56" height="43" rx="2" fill="#00e5ff" opacity="0.75"/>
          <text x="140" y="15" fill="#78909c" font-size="9" text-anchor="middle">Tanque T2</text>
          <circle id="svg-pump-body" cx="195" cy="55" r="14" fill="#162238" stroke="#00e676" stroke-width="2"/>
          <path id="svg-pump-rotor" d="M195 45 L195 65 M185 55 L205 55" stroke="#00e676" stroke-width="2"/>
          <text x="195" y="80" fill="#78909c" font-size="8" text-anchor="middle">P101</text>
        </svg>
      </div>
      <div class="readouts">
        <span class="metric-label">Nivel T2 (m³):</span><span id="val-water-t2" class="metric-val">10.0</span>
        <span class="metric-label">Bomba P101:</span><span id="val-water-pump" class="metric-val">ACTIVA</span>
      </div>
    </div>

    <!-- 2. GAS -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">🔥 Distribución de Gas</span>
        <span id="badge-gas" class="badge badge-ok">OK</span>
      </div>
      <div class="canvas-wrap">
        <svg width="220" height="110" viewBox="0 0 220 110">
          <circle cx="90" cy="55" r="40" fill="#121a29" stroke="#37474f" stroke-width="2"/>
          <circle cx="90" cy="55" r="34" fill="#090d14"/>
          <path d="M60 70 A30 30 0 1 1 120 70" fill="none" stroke="#263238" stroke-width="6"/>
          <path d="M60 70 A30 30 0 0 1 85 27" fill="none" stroke="#00e676" stroke-width="6"/>
          <path d="M85 27 A30 30 0 0 1 105 32" fill="none" stroke="#ffab00" stroke-width="6"/>
          <path d="M105 32 A30 30 0 0 1 120 70" fill="none" stroke="#ff1744" stroke-width="6"/>
          <line id="svg-gas-needle" x1="90" y1="55" x2="90" y2="28" stroke="#ff5252" stroke-width="2.5" stroke-linecap="round" transform="rotate(20, 90, 55)"/>
          <circle cx="90" cy="55" r="4" fill="#fff"/>
          <text x="90" y="80" fill="#78909c" font-size="8" text-anchor="middle">PSI x10</text>
          <g id="svg-gas-valve-grp" transform="translate(165, 40)">
            <polygon points="0,5 15,20 0,35" fill="#00e676"/>
            <polygon points="30,5 15,20 30,35" fill="#00e676"/>
            <rect x="13" y="0" width="4" height="20" fill="#00e676"/>
            <text x="15" y="48" fill="#78909c" font-size="8" text-anchor="middle">V-101</text>
          </g>
        </svg>
      </div>
      <div class="readouts">
        <span class="metric-label">Presión (PSI):</span><span id="val-gas-press" class="metric-val">145.0</span>
        <span class="metric-label">Válvula V-101:</span><span id="val-gas-valve" class="metric-val">ABIERTA</span>
      </div>
    </div>

    <!-- 3. ELECTRICO -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">⚡ Subestación Eléctrica</span>
        <span id="badge-elec" class="badge badge-ok">OK</span>
      </div>
      <div class="canvas-wrap">
        <svg width="220" height="110" viewBox="0 0 220 110">
          <line x1="20" y1="55" x2="65" y2="55" stroke="#00e5ff" stroke-width="3"/>
          <circle cx="65" cy="55" r="4" fill="#00e5ff"/>
          <g id="svg-breaker-state">
            <line id="svg-breaker-arm" x1="65" y1="55" x2="115" y2="55" stroke="#00e676" stroke-width="3"/>
          </g>
          <circle cx="115" cy="55" r="4" fill="#00e5ff"/>
          <line x1="115" y1="55" x2="160" y2="55" stroke="#00e5ff" stroke-width="3"/>
          <text x="90" y="30" fill="#78909c" font-size="9" text-anchor="middle">XCBR1</text>
          <path d="M175 40 L195 55 L175 70 Z" fill="#ffab00" opacity="0.8"/>
          <text x="185" y="90" fill="#78909c" font-size="8" text-anchor="middle">Carga</text>
        </svg>
      </div>
      <div class="readouts">
        <span class="metric-label">Tensión (V):</span><span id="val-elec-volt" class="metric-val">230.0</span>
        <span class="metric-label">Estado:</span><span id="val-elec-status" class="metric-val">CONECTADO</span>
      </div>
    </div>

    <!-- 4. TRANSPORTE -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">🚦 Red Vial y Tráfico</span>
        <span id="badge-trans" class="badge badge-ok">OK</span>
      </div>
      <div class="canvas-wrap">
        <svg width="220" height="110" viewBox="0 0 220 110">
          <rect x="30" y="10" width="30" height="85" rx="5" fill="#121a29" stroke="#37474f" stroke-width="2"/>
          <circle id="tl-red" cx="45" cy="25" r="9" fill="#330009"/>
          <circle id="tl-amber" cx="45" cy="52" r="9" fill="#332600"/>
          <circle id="tl-green" cx="45" cy="79" r="9" fill="#00e676"/>
          <rect x="90" y="45" width="110" height="15" rx="3" fill="#121a29" stroke="#37474f"/>
          <rect id="svg-cong-bar" x="92" y="47" width="20" height="11" rx="2" fill="#00e676"/>
          <text x="145" y="35" fill="#78909c" font-size="8" text-anchor="middle">Congestión</text>
          <text id="val-trans-gate" x="145" y="80" fill="#cfd8dc" font-size="9" text-anchor="middle">Barrera: ABIERTA</text>
        </svg>
      </div>
      <div class="readouts">
        <span class="metric-label">Luz Semáforo:</span><span id="val-trans-light" class="metric-val">VERDE</span>
        <span class="metric-label">Congestión (%):</span><span id="val-trans-cong" class="metric-val">15.0</span>
      </div>
    </div>

    <!-- 5. HOSPITAL -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">🏥 Hospital Municipal</span>
        <span id="badge-hosp" class="badge badge-ok">OK</span>
      </div>
      <div class="canvas-wrap">
        <svg width="220" height="110" viewBox="0 0 220 110">
          <rect x="75" y="25" width="70" height="60" rx="3" fill="#121a29" stroke="#37474f" stroke-width="2"/>
          <path d="M110 35 L110 55 M100 45 L120 45" stroke="#ff1744" stroke-width="4"/>
          <text x="110" y="75" fill="#78909c" font-size="8" text-anchor="middle">UCI / ATS</text>
          <g id="svg-hosp-source" transform="translate(160, 35)">
            <circle cx="20" cy="20" r="16" fill="#162238" stroke="#00e676" stroke-width="2"/>
            <text id="svg-hosp-src-txt" x="20" y="23" fill="#00e676" font-size="8" text-anchor="middle">RED</text>
          </g>
        </svg>
      </div>
      <div class="readouts">
        <span class="metric-label">Suministro:</span><span id="val-hosp-source" class="metric-val">RED NORMAL</span>
        <span class="metric-label">Carga Activa:</span><span id="val-hosp-load" class="metric-val">850 kW</span>
      </div>
    </div>

    <!-- 6. DESALINIZADORA -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">🌊 Planta Desalinizadora</span>
        <span id="badge-desal" class="badge badge-ok">OK</span>
      </div>
      <div class="canvas-wrap">
        <svg width="220" height="110" viewBox="0 0 220 110">
          <rect x="35" y="20" width="70" height="70" rx="3" fill="#121a29" stroke="#37474f" stroke-width="2"/>
          <rect id="svg-desal-fill" x="37" y="45" width="66" height="43" rx="2" fill="#00b4d8" opacity="0.75"/>
          <text x="70" y="15" fill="#78909c" font-size="8" text-anchor="middle">Tanque Osmosis</text>
          <circle id="svg-desal-pump" cx="155" cy="55" r="16" fill="#162238" stroke="#00e676" stroke-width="2"/>
          <path d="M155 42 L155 68 M142 55 L168 55" stroke="#00e676" stroke-width="2"/>
          <text x="155" y="85" fill="#78909c" font-size="8" text-anchor="middle">HP-Pump</text>
        </svg>
      </div>
      <div class="readouts">
        <span class="metric-label">Nivel Permeado:</span><span id="val-desal-level" class="metric-val">75.0%</span>
        <span class="metric-label">Potencia / Trip:</span><span id="val-desal-kw" class="metric-val">45 kW</span>
      </div>
    </div>

    <!-- 7. ALUMBRADO -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">💡 Alumbrado Inteligente</span>
        <span id="badge-light" class="badge badge-ok">OK</span>
      </div>
      <div class="canvas-wrap">
        <svg width="220" height="110" viewBox="0 0 220 110">
          <line x1="110" y1="90" x2="110" y2="30" stroke="#78909c" stroke-width="3"/>
          <path d="M110 30 Q110 15 130 20" fill="none" stroke="#78909c" stroke-width="3"/>
          <circle id="svg-lamp-glow" cx="130" cy="22" r="10" fill="#fff59d" opacity="0.85"/>
          <circle cx="130" cy="22" r="4" fill="#fff"/>
        </svg>
      </div>
      <div class="readouts">
        <span class="metric-label">Consumo Red:</span><span id="val-light-kw" class="metric-val">120 kW</span>
        <span class="metric-label">Modo:</span><span class="metric-val">AUTO DALI</span>
      </div>
    </div>

    <!-- 8. SEGURIDAD SIS SIL-3 -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">🛡️ Sistema SIS SIL-3</span>
        <span id="badge-sis-card" class="badge badge-ok">ARMED</span>
      </div>
      <div class="canvas-wrap">
        <svg width="220" height="110" viewBox="0 0 220 110">
          <polygon points="110,15 170,45 170,80 110,100 50,80 50,45" fill="#121a29" stroke="#00e676" stroke-width="2" id="svg-shield-border"/>
          <text id="svg-sis-center-txt" x="110" y="60" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">SIL-3</text>
          <text x="110" y="78" fill="#78909c" font-size="8" text-anchor="middle">INTERLOCKS</text>
        </svg>
      </div>
      <div class="readouts">
        <span class="metric-label">Disparo Emergencia:</span><span id="val-sis-trip" class="metric-val">NO ACTIVO</span>
        <span class="metric-label">Canales Votación:</span><span class="metric-val">1oo2D / 2oo3</span>
      </div>
    </div>
  </div>

  <div id="raw-container">
    <h3 style="font-size: 0.85rem; color: #78909c; margin-bottom: 6px;">Payload JSON de Telemetría (/api/viz/frame)</h3>
    <pre id="viewport"></pre>
  </div>

  <script>
    function toggleRaw() {
      const c = document.getElementById('raw-container');
      c.style.display = c.style.display === 'block' ? 'none' : 'block';
    }

    function render(data) {
      const sectors = data.city_sectors || {};
      let critical = false;

      // 1. Water
      if (sectors.water) {
        const w = sectors.water;
        document.getElementById('val-water-t2').innerText = Number(w.tank_level || 0).toFixed(1);
        const pumpTxt = w.pump_running ? 'ACTIVA' : (w.alert ? 'TRIP' : 'PARADA');
        document.getElementById('val-water-pump').innerText = pumpTxt;
        const b = document.getElementById('badge-water');
        if (w.alert) {
          b.className = 'badge badge-crit'; b.innerText = 'TRIP';
          critical = true;
        } else {
          b.className = 'badge badge-ok'; b.innerText = 'OK';
        }
        const t2H = Math.min(65, Math.max(5, (w.tank_level / 20) * 65));
        const svgT2 = document.getElementById('svg-water-fill-t2');
        svgT2.setAttribute('height', t2H);
        svgT2.setAttribute('y', 90 - t2H);
      }

      // 2. Gas
      if (sectors.gas) {
        const g = sectors.gas;
        document.getElementById('val-gas-press').innerText = Number(g.pressure_psi || 0).toFixed(1);
        document.getElementById('val-gas-valve').innerText = g.valve_open ? 'ABIERTA' : 'CERRADA';
        const b = document.getElementById('badge-gas');
        if (g.alert) {
          b.className = 'badge badge-crit'; b.innerText = 'ALERTA';
          critical = true;
        } else {
          b.className = 'badge badge-ok'; b.innerText = 'OK';
        }
        const rot = Math.min(120, Math.max(-120, ((g.pressure_psi - 100) / 100) * 120));
        document.getElementById('svg-gas-needle').setAttribute('transform', `rotate(${rot}, 90, 55)`);
      }

      // 3. Elec
      if (sectors.elec) {
        const e = sectors.elec;
        document.getElementById('val-elec-volt').innerText = Number(e.grid_voltage || 0).toFixed(1);
        document.getElementById('val-elec-status').innerText = e.blackout ? 'BLACKOUT' : 'NORMAL';
        const b = document.getElementById('badge-elec');
        const arm = document.getElementById('svg-breaker-arm');
        if (e.blackout) {
          b.className = 'badge badge-crit'; b.innerText = 'APAGÓN';
          arm.setAttribute('x2', '95'); arm.setAttribute('y2', '40'); arm.setAttribute('stroke', '#ff1744');
          critical = true;
        } else {
          b.className = 'badge badge-ok'; b.innerText = 'OK';
          arm.setAttribute('x2', '115'); arm.setAttribute('y2', '55'); arm.setAttribute('stroke', '#00e676');
        }
      }

      // 4. Transport
      if (sectors.transport) {
        const t = sectors.transport;
        document.getElementById('val-trans-light').innerText = t.traffic_light || 'VERDE';
        document.getElementById('val-trans-gate').innerText = 'Barrera: ' + (t.railway_gate || 'ABIERTA');
        const cVal = Number(t.congestion_pct || (t.traffic_light === 'RED' ? 85 : 20));
        document.getElementById('val-trans-cong').innerText = cVal.toFixed(1);
        document.getElementById('svg-cong-bar').setAttribute('width', Math.min(106, (cVal / 100) * 106));

        document.getElementById('tl-red').setAttribute('fill', t.traffic_light === 'RED' ? '#ff1744' : '#330009');
        document.getElementById('tl-amber').setAttribute('fill', t.traffic_light === 'AMBER' ? '#ffab00' : '#332600');
        document.getElementById('tl-green').setAttribute('fill', t.traffic_light === 'GREEN' ? '#00e676' : '#003314');
      }

      // 5. Hospital
      if (sectors.hospital) {
        const h = sectors.hospital;
        document.getElementById('val-hosp-source').innerText = h.generator_active ? 'GENERADOR / UPS' : 'RED NORMAL';
        document.getElementById('val-hosp-load').innerText = (h.load_kw || 850) + ' kW';
        const b = document.getElementById('badge-hosp');
        const srcTxt = document.getElementById('svg-hosp-src-txt');
        if (h.generator_active) {
          b.className = 'badge badge-warn'; b.innerText = 'ON UPS';
          srcTxt.innerText = 'UPS'; srcTxt.setAttribute('fill', '#ffab00');
        } else {
          b.className = 'badge badge-ok'; b.innerText = 'OK';
          srcTxt.innerText = 'RED'; srcTxt.setAttribute('fill', '#00e676');
        }
      }

      // 6. Desal
      if (sectors.desal) {
        const d = sectors.desal;
        document.getElementById('val-desal-level').innerText = Number(d.tank_level_pct || 75).toFixed(1) + '%';
        document.getElementById('val-desal-kw').innerText = Number(d.power_kw || 45).toFixed(0) + ' kW';
        const b = document.getElementById('badge-desal');
        if (d.pump_trip) {
          b.className = 'badge badge-crit'; b.innerText = 'TRIP';
          critical = true;
        } else {
          b.className = 'badge badge-ok'; b.innerText = 'OK';
        }
      }

      // 7. Lighting
      if (sectors.lighting) {
        const l = sectors.lighting;
        document.getElementById('val-light-kw').innerText = Number(l.power_kw || 120).toFixed(0) + ' kW';
      }

      // 8. Safety / SIS
      if (sectors.safety) {
        const s = sectors.safety;
        const b = document.getElementById('badge-sis-card');
        const bTop = document.getElementById('badge-sis');
        const border = document.getElementById('svg-shield-border');
        const centerTxt = document.getElementById('svg-sis-center-txt');
        if (s.sis_trip) {
          document.getElementById('val-sis-trip').innerText = '¡DISPARO SIL-3!';
          b.className = 'badge badge-crit'; b.innerText = 'TRIPPED';
          bTop.className = 'badge badge-crit'; bTop.innerText = 'SIS: TRIP';
          border.setAttribute('stroke', '#ff1744');
          centerTxt.setAttribute('fill', '#ff1744');
          critical = true;
        } else {
          document.getElementById('val-sis-trip').innerText = 'NO ACTIVO';
          b.className = 'badge badge-ok'; b.innerText = 'ARMED';
          bTop.className = 'badge badge-ok'; bTop.innerText = 'SIS SIL-3: OK';
          border.setAttribute('stroke', '#00e676');
          centerTxt.setAttribute('fill', '#00e676');
        }
      }

      // Banner Superior
      const socBadge = document.getElementById('badge-soc');
      if (critical) {
        socBadge.className = 'badge badge-crit';
        socBadge.innerText = 'INCIDENTE ACTIVO';
      } else {
        socBadge.className = 'badge badge-ok';
        socBadge.innerText = 'SISTEMA NORMAL';
      }

      // Actualizar viewport crudo
      document.getElementById('viewport').innerText = JSON.stringify(data, null, 2);
    }

    setInterval(() => {
      fetch('/api/viz/frame')
        .then(r => r.json())
        .then(render)
        .catch(err => console.debug('Polling viz frame:', err));
    }, 1000);
  </script>
</body>
</html>"""
            self._send_html(html)
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self) -> None:
        if self.path == '/api/viz/update':
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length)
            try:
                data = json.loads(body_bytes.decode('utf-8'))
                # Soporte para actualización por lotes {"sectors": {...}}
                if 'sectors' in data and isinstance(data['sectors'], dict):
                    unknown = [s for s in data['sectors'] if s not in self.engine.state['city_sectors']]
                    if unknown:
                        self._send_json({'status': 'ERROR', 'message': f'unknown sectors: {unknown}'}, status=400)
                        return
                    for s, p in data['sectors'].items():
                        if isinstance(p, dict):
                            self.engine.update_sector_state(s, p)
                    self._send_json({'status': 'UPDATED', 'sectors': list(data['sectors'].keys())})
                    return

                # Formato individual clásico {"sector": "...", "payload": {...}}
                sector = data.get('sector', '')
                payload = data.get('payload', {})
                if sector and isinstance(payload, dict):
                    if self.engine.update_sector_state(sector, payload):
                        self._send_json({'status': 'UPDATED', 'sector': sector})
                    else:
                        self._send_json({'status': 'ERROR', 'message': f'unknown sector: {sector}'}, status=400)
                else:
                    self._send_json({'status': 'ERROR', 'message': 'invalid sector or payload'}, status=400)
            except Exception as e:
                self._send_json({'status': 'ERROR', 'message': str(e)}, status=400)
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
        pass


class ThreadedVizServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="CityLab 2D/3D City Visualizer Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host / IP de escucha (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_VIZ_PORT, help=f"Puerto HTTP (default: {DEFAULT_VIZ_PORT})")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][VIZ] %(message)s')
    server = ThreadedVizServer((args.host, args.port), VizRequestHandler)
    LOGGER.info("Servidor Visualizador Urbano escuchando en http://%s:%d", args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Apagando Servidor Visualizador...")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
