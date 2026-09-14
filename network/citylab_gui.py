#!/usr/bin/env python3
"""network/citylab_gui.py — Dashboard Nativo de Escritorio para CityLab Cyber Range.

Aplicación de escritorio nativa (Tkinter / ttk) con diseño en panel dividido:
  - Panel Izquierdo: HMI Industrial (OpenSCADA / Ignition Edge Emulator) con 4 sectores
    primarios (water, gas, elec, transport), mandos manuales y consola de alarmas.
  - Panel Derecho: Visualizador Urbano Ciberfísico 2D con los 8 sectores y telemetría
    Blue Team SOC / SDN Mitigations.

Diseñado en 3 capas desacopladas:
  1. Clientes HTTP de transporte (HmiClient, VizClient) con resiliencia total y timeouts cortos.
  2. Funciones puras de derivación de estado de vista (derive_hmi_view_state, derive_viz_view_state).
  3. Aplicación gráfica (CityLabDashboardApp) con sondeo en hilos daemon en segundo plano.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    tk = None  # type: ignore
    ttk = None  # type: ignore
    messagebox = None  # type: ignore

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][GUI] %(message)s')
LOGGER = logging.getLogger('citylab_gui')

DEFAULT_HMI_URL = os.getenv('HMI_HTTP_URL', os.getenv('HMI_URL', 'http://10.0.2.20:8085'))
DEFAULT_VIZ_URL = os.getenv('VIZ_HTTP_URL', os.getenv('VIZ_URL', 'http://10.0.2.20:8090'))


# ============================================================================
# CAPA 1: Clientes HTTP de Transporte (No-crash, Safe Defaults)
# ============================================================================

def _http_get_json(url: str, timeout: float = 2.0) -> Optional[Dict[str, Any]]:
    """Consulta HTTP GET con timeout estricto; retorna dict o None ante error."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CityLab-Native-GUI/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = resp.read().decode('utf-8')
                return json.loads(data)
    except Exception as exc:
        LOGGER.debug("GET %s falló: %s", url, exc)
    return None


def _http_post_json(url: str, payload: Dict[str, Any], timeout: float = 2.0) -> Optional[Dict[str, Any]]:
    """Envío HTTP POST con payload JSON y timeout estricto; retorna dict o None."""
    try:
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'CityLab-Native-GUI/1.0',
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                body = resp.read().decode('utf-8')
                return json.loads(body)
    except Exception as exc:
        LOGGER.debug("POST %s falló: %s", url, exc)
    return None


class HmiClient:
    """Cliente para la API REST del HMI Server (:8085)."""

    def __init__(self, base_url: str = DEFAULT_HMI_URL) -> None:
        self.base_url = base_url.rstrip('/')

    def get_overview(self) -> Dict[str, Any]:
        """Obtiene el estado consolidado P&ID y alarmas."""
        url = f"{self.base_url}/api/hmi/overview"
        data = _http_get_json(url)
        if data is not None and isinstance(data, dict):
            return data
        return {
            'scada_connected': False,
            'system_health': 'ALARM_CRITICAL',
            'process_diagram': {},
            'alarms': [],
            'error': 'OFFLINE'
        }

    def send_control(self, action: str, target: str) -> Dict[str, Any]:
        """Envía un comando de control de operador al HMI Server."""
        url = f"{self.base_url}/api/hmi/control"
        res = _http_post_json(url, {'action': action, 'target': target})
        if res is not None and isinstance(res, dict):
            return res
        return {'success': False, 'error': 'No se pudo contactar al servidor HMI'}


class VizClient:
    """Cliente para la API REST del Visualizador Urbano 2D (:8090)."""

    def __init__(self, base_url: str = DEFAULT_VIZ_URL) -> None:
        self.base_url = base_url.rstrip('/')

    def get_frame(self) -> Dict[str, Any]:
        """Obtiene el fotograma actual de los 8 sectores urbanos y Blue Team."""
        url = f"{self.base_url}/api/viz/frame"
        data = _http_get_json(url)
        if data is not None and isinstance(data, dict):
            return data
        return {
            'city_sectors': {},
            'soc_alerts': [],
            'sdn_mitigations': [],
            'offline': True
        }


# ============================================================================
# CAPA 2: Derivación Pura de Estado de Vista (Unit-testable, Sin I/O)
# ============================================================================

def derive_hmi_view_state(overview: Dict[str, Any]) -> Dict[str, Any]:
    """Deriva el estado visual de la HMI a partir del JSON de /api/hmi/overview.

    Replica exactamente la lógica del JavaScript `updateHmi()` en hmi_server.py.
    """
    scada_connected = bool(overview.get('scada_connected', False))
    system_health = overview.get('system_health', 'ALARM_CRITICAL' if not scada_connected else 'NORMAL')

    scada_badge = ('SCADA ONLINE', '#00e676') if scada_connected else ('SCADA OFFLINE', '#ff1744')
    health_badge = ('ALARMA CRÍTICA', '#ff1744') if system_health == 'ALARM_CRITICAL' else ('NORMAL', '#00e676')

    proc = overview.get('process_diagram', {})
    if not isinstance(proc, dict):
        proc = {}

    # 1. Agua
    w = proc.get('water_sector', {})
    w_lov = w.get('status') == 'LOSS_OF_VIEW'
    w_t1 = float(w.get('t1_level') if w.get('t1_level') is not None else 10.0)
    w_t2 = float(w.get('t2_level') if w.get('t2_level') is not None else 15.0)
    w_running = bool(w.get('p1_state') or w.get('actuator_running'))
    if w_lov:
        w_badge = ('LOSS OF VIEW', '#ff1744')
    elif w_running:
        w_badge = ('OK', '#00e676')
    else:
        w_badge = ('STOP', '#ffab00')

    # 2. Gas
    g = proc.get('gas_sector', {})
    g_lov = g.get('status') == 'LOSS_OF_VIEW'
    g_press = float(g.get('pressure_psi') if g.get('pressure_psi') is not None else 145.0)
    g_open = bool(g.get('valve_open') or g.get('actuator_running'))
    if g_lov:
        g_badge = ('LOSS OF VIEW', '#ff1744')
    elif g_press > 180.0:
        g_badge = ('ALTA PRESIÓN', '#ff1744')
    else:
        g_badge = ('OK', '#00e676')

    # 3. Eléctrico
    e = proc.get('elec_sector', {})
    e_lov = e.get('status') == 'LOSS_OF_VIEW'
    e_volt = float(e.get('grid_voltage') if e.get('grid_voltage') is not None else 230.0)
    e_closed = bool(e.get('breaker_closed') if e.get('breaker_closed') is not None else (not e.get('blackout', False)))
    if e_lov:
        e_badge = ('LOSS OF VIEW', '#ff1744')
    elif e_closed:
        e_badge = ('OK', '#00e676')
    else:
        e_badge = ('TRIPPED', '#ff1744')

    # 4. Transporte
    t = proc.get('transport_sector', {})
    t_lov = t.get('status') == 'LOSS_OF_VIEW'
    tl_raw = t.get('traffic_light')
    if isinstance(tl_raw, (int, float)):
        tl_str = 'VERDE' if tl_raw == 2 else ('ÁMBAR' if tl_raw == 1 else 'ROJO')
    else:
        tl_str = str(tl_raw or 'VERDE').upper()
    t_gate_open = bool(t.get('gate_open') if t.get('gate_open') is not None else (t.get('railway_gate') == 'OPEN'))
    if t_lov:
        t_badge = ('LOSS OF VIEW', '#ff1744')
    else:
        t_badge = ('OK', '#00e676')

    alarms = overview.get('alarms', [])
    if not isinstance(alarms, list):
        alarms = []

    return {
        'scada_connected': scada_connected,
        'scada_badge': scada_badge,
        'health_badge': health_badge,
        'sectors': {
            'water': {
                'badge': w_badge,
                't1_level': w_t1,
                't2_level': w_t2,
                'pump_running': w_running,
                'status': w.get('status', 'ONLINE'),
            },
            'gas': {
                'badge': g_badge,
                'pressure_psi': g_press,
                'valve_open': g_open,
                'status': g.get('status', 'ONLINE'),
            },
            'elec': {
                'badge': e_badge,
                'grid_voltage': e_volt,
                'breaker_closed': e_closed,
                'status': e.get('status', 'ONLINE'),
            },
            'transport': {
                'badge': t_badge,
                'traffic_light': tl_str,
                'gate_open': t_gate_open,
                'status': t.get('status', 'ONLINE'),
            }
        },
        'alarms': alarms,
        'alarms_count': len(alarms)
    }


def derive_viz_view_state(frame: Dict[str, Any]) -> Dict[str, Any]:
    """Deriva el estado visual del Visualizador 2D a partir de /api/viz/frame.

    Replica exactamente la lógica del JavaScript `render()` en viz_server.py.
    """
    sectors = frame.get('city_sectors', {})
    if not isinstance(sectors, dict):
        sectors = {}

    critical = False

    # 1. Water
    w = sectors.get('water', {})
    w_alert = bool(w.get('alert', False))
    if w_alert:
        w_badge = ('TRIP', '#ff1744')
        critical = True
    else:
        w_badge = ('OK', '#00e676')
    w_running = bool(w.get('pump_running', True))
    w_level = float(w.get('tank_level') if w.get('tank_level') is not None else 10.0)

    # 2. Gas
    g = sectors.get('gas', {})
    g_alert = bool(g.get('alert', False))
    g_press = float(g.get('pressure_psi') if g.get('pressure_psi') is not None else 145.0)
    g_valve = bool(g.get('valve_open', True))
    if g_alert or g_press > 180.0:
        g_badge = ('ALERTA', '#ff1744')
        critical = True
    else:
        g_badge = ('OK', '#00e676')

    # 3. Elec
    e = sectors.get('elec', {})
    e_blackout = bool(e.get('blackout', False))
    e_volt = float(e.get('grid_voltage') if e.get('grid_voltage') is not None else 230.0)
    if e_blackout:
        e_badge = ('APAGÓN', '#ff1744')
        critical = True
    else:
        e_badge = ('OK', '#00e676')

    # 4. Transport (badge estático OK en JS)
    t = sectors.get('transport', {})
    t_light = str(t.get('traffic_light') or 'VERDE')
    t_gate = str(t.get('railway_gate') or 'ABIERTA')
    t_cong = float(t.get('congestion_pct') if t.get('congestion_pct') is not None else (85.0 if t_light == 'RED' else 20.0))
    t_badge = ('OK', '#00e676')

    # 5. Hospital
    h = sectors.get('hospital', {})
    h_gen = bool(h.get('generator_active', False))
    h_decoupled = bool(h.get('standalone_decoupled', False))
    h_load = float(h.get('load_kw') if h.get('load_kw') is not None else 850.0)
    if h_gen:
        h_badge = ('ON UPS', '#ffab00')
    elif h_decoupled:
        h_badge = ('OK (STANDALONE)', '#00e676')
    else:
        h_badge = ('OK', '#00e676')

    # 6. Desal
    d = sectors.get('desal', {})
    d_trip = bool(d.get('pump_trip', False))
    d_decoupled = bool(d.get('standalone_decoupled', False))
    d_level = float(d.get('tank_level_pct') if d.get('tank_level_pct') is not None else 75.0)
    d_kw = float(d.get('power_kw') if d.get('power_kw') is not None else 45.0)
    if d_trip:
        d_badge = ('TRIP', '#ff1744')
        critical = True
    elif d_decoupled:
        d_badge = ('OK (STANDALONE)', '#00e676')
    else:
        d_badge = ('OK', '#00e676')

    # 7. Lighting
    l = sectors.get('lighting', {})
    l_kw = float(l.get('power_kw') if l.get('power_kw') is not None else 120.0)
    l_decoupled = bool(l.get('standalone_decoupled', False))
    l_blackout = bool(l.get('blackout', False)) or (l_kw == 0.0)
    if l_blackout:
        l_badge = ('APAGÓN', '#ff1744')
        critical = True
    elif l_decoupled:
        l_badge = ('OK (STANDALONE)', '#00e676')
    else:
        l_badge = ('OK', '#00e676')

    # 8. Safety / SIS
    s = sectors.get('safety', {})
    s_trip = bool(s.get('sis_trip', False))
    s_decoupled = bool(s.get('standalone_decoupled', False))
    if s_trip:
        s_badge = ('TRIPPED', '#ff1744')
        sis_header_badge = ('SIS: TRIP', '#ff1744')
        critical = True
    elif s_decoupled:
        s_badge = ('ARMED (STANDALONE)', '#00e676')
        sis_header_badge = ('SIS SIL-3: OK', '#00e676')
    else:
        s_badge = ('ARMED', '#00e676')
        sis_header_badge = ('SIS SIL-3: OK', '#00e676')

    # Blue Team SOC & SDN
    soc_alerts = frame.get('soc_alerts', [])
    if not isinstance(soc_alerts, list):
        soc_alerts = []
    sdn_mitigations = frame.get('sdn_mitigations', [])
    if not isinstance(sdn_mitigations, list):
        sdn_mitigations = []

    if soc_alerts:
        top_a = soc_alerts[0]
        soc_name = top_a.get('name', top_a.get('alert_id', 'ALERTA'))
        attacker_ip = top_a.get('attacker_ip', 'UNK')
        soc_badge = (f"SOC: {soc_name[:24]} [IP: {attacker_ip}]", '#ff1744')
    elif critical:
        soc_badge = ('INCIDENTE FÍSICO ACTIVO', '#ff1744')
    else:
        soc_badge = ('SISTEMA NORMAL', '#00e676')

    return {
        'critical': critical,
        'system_badge': soc_badge,
        'sis_badge': sis_header_badge,
        'sectors': {
            'water': {'badge': w_badge, 'pump_running': w_running, 'tank_level': w_level},
            'gas': {'badge': g_badge, 'pressure_psi': g_press, 'valve_open': g_valve},
            'elec': {'badge': e_badge, 'grid_voltage': e_volt, 'blackout': e_blackout},
            'transport': {'badge': t_badge, 'traffic_light': t_light, 'railway_gate': t_gate, 'congestion_pct': t_cong},
            'hospital': {'badge': h_badge, 'generator_active': h_gen, 'load_kw': h_load},
            'desal': {'badge': d_badge, 'tank_level_pct': d_level, 'power_kw': d_kw},
            'lighting': {'badge': l_badge, 'power_kw': l_kw, 'blackout': l_blackout},
            'safety': {'badge': s_badge, 'sis_trip': s_trip},
        },
        'soc_alerts': soc_alerts[:3],
        'sdn_mitigations': sdn_mitigations[:3],
    }


# ============================================================================
# CAPA 3: Aplicación de Escritorio Nativa (Tkinter / Dark SCADA Theme)
# ============================================================================

BG_MAIN = '#0a0d14'
BG_CARD = '#101522'
BG_HEADER = '#161c2e'
TEXT_COLOR = '#e2e8f0'
TEXT_MUTED = '#94a3b8'
ACCENT_CYAN = '#00e5ff'
ACCENT_GREEN = '#00e676'
ACCENT_RED = '#ff1744'
ACCENT_AMBER = '#ffab00'
BORDER_COLOR = '#1e293b'


class CityLabDashboardApp:
    """Ventana principal de escritorio con diseño split-pane: HMI y Visualizador 2D."""

    def __init__(
        self,
        hmi_url: str = DEFAULT_HMI_URL,
        viz_url: str = DEFAULT_VIZ_URL,
        root: Optional[tk.Tk] = None
    ) -> None:
        if tk is None:
            raise RuntimeError("tkinter no está disponible en este entorno.")

        self.root = root or tk.Tk()
        self.root.title("CityLab Cyber Range — Dashboard Unificado (HMI & Visualizador 2D)")
        self.root.geometry("1400x880")
        self.root.configure(bg=BG_MAIN)

        self.hmi_client = HmiClient(hmi_url)
        self.viz_client = VizClient(viz_url)

        self._lock = threading.Lock()
        self._raw_hmi_data: Dict[str, Any] = {}
        self._raw_viz_data: Dict[str, Any] = {}
        self._stop_event = threading.Event()

        self._build_styles()
        self._build_layout()

        # Iniciar hilos daemon de sondeo en segundo plano
        self.hmi_thread = threading.Thread(target=self._poll_hmi_loop, daemon=True)
        self.viz_thread = threading.Thread(target=self._poll_viz_loop, daemon=True)
        self.hmi_thread.start()
        self.viz_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(200, self._refresh_ui)

    def _build_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('.', background=BG_MAIN, foreground=TEXT_COLOR, font=('Helvetica', 10))
        style.configure('TPanedwindow', background=BORDER_COLOR)
        style.configure('Treeview', background=BG_CARD, foreground=TEXT_COLOR, fieldbackground=BG_CARD, rowheight=24)
        style.configure('Treeview.Heading', background=BG_HEADER, foreground=ACCENT_CYAN, font=('Helvetica', 9, 'bold'))
        style.map('Treeview', background=[('selected', '#1e293b')], foreground=[('selected', ACCENT_CYAN)])

    def _build_layout(self) -> None:
        # Top Global Title Bar
        top_bar = tk.Frame(self.root, bg=BG_HEADER, height=50, bd=1, relief=tk.SOLID)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        lbl_title = tk.Label(
            top_bar,
            text="🏙️ CITYLAB CYBER RANGE — CONSOLA DE OPERACIONES",
            bg=BG_HEADER,
            fg=ACCENT_CYAN,
            font=('Helvetica', 13, 'bold'),
            padx=16,
            pady=8
        )
        lbl_title.pack(side=tk.LEFT)

        self.lbl_global_status = tk.Label(
            top_bar,
            text="CONECTANDO...",
            bg='#003314',
            fg=ACCENT_GREEN,
            font=('Helvetica', 10, 'bold'),
            padx=12,
            pady=4,
            relief=tk.RIDGE
        )
        self.lbl_global_status.pack(side=tk.RIGHT, padx=16, pady=8)

        # Main Paned Window (Split-Pane Horizontal)
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Left Pane: HMI Industrial (OpenSCADA / Ignition Edge)
        self.hmi_frame = tk.Frame(self.paned, bg=BG_MAIN)
        self.paned.add(self.hmi_frame, weight=1)
        self._build_hmi_pane(self.hmi_frame)

        # Right Pane: Visualizador 2D Multisectorial & Blue Team
        self.viz_frame = tk.Frame(self.paned, bg=BG_MAIN)
        self.paned.add(self.viz_frame, weight=1)
        self._build_viz_pane(self.viz_frame)

    # ------------------------------------------------------------------------
    # Construcción Panel Izquierdo: HMI Industrial
    # ------------------------------------------------------------------------

    def _build_hmi_pane(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=BG_CARD, bd=1, relief=tk.SOLID, padx=10, pady=8)
        header.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            header,
            text="🎛️ HMI INDUSTRIAL — OpenSCADA (:8085)",
            bg=BG_CARD,
            fg=ACCENT_CYAN,
            font=('Helvetica', 11, 'bold')
        ).pack(side=tk.LEFT)

        self.hmi_badge_scada = tk.Label(header, text="SCADA...", bg='#332600', fg=ACCENT_AMBER, font=('Helvetica', 9, 'bold'), padx=8)
        self.hmi_badge_scada.pack(side=tk.RIGHT, padx=4)

        self.hmi_badge_health = tk.Label(header, text="ESTADO...", bg='#332600', fg=ACCENT_AMBER, font=('Helvetica', 9, 'bold'), padx=8)
        self.hmi_badge_health.pack(side=tk.RIGHT, padx=4)

        # Tarjetas de 4 Sectores Primarios (Grid 2x2)
        grid_frame = tk.Frame(parent, bg=BG_MAIN)
        grid_frame.pack(fill=tk.BOTH, expand=False, pady=4)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # 1. Agua Card
        card_w = tk.LabelFrame(grid_frame, text=" 💧 Tratamiento de Agua (P-101 / T-101) ", bg=BG_CARD, fg=TEXT_COLOR, font=('Helvetica', 10, 'bold'), padx=10, pady=8)
        card_w.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        self.w_lbl_badge = tk.Label(card_w, text="OK", bg='#003314', fg=ACCENT_GREEN, font=('Helvetica', 8, 'bold'))
        self.w_lbl_badge.pack(anchor=tk.E)
        self.w_lbl_t1 = tk.Label(card_w, text="Tanque T1: -- m³", bg=BG_CARD, fg=TEXT_COLOR)
        self.w_lbl_t1.pack(anchor=tk.W)
        self.w_lbl_t2 = tk.Label(card_w, text="Tanque T2: -- m³", bg=BG_CARD, fg=TEXT_COLOR)
        self.w_lbl_t2.pack(anchor=tk.W)
        self.w_lbl_p1 = tk.Label(card_w, text="Bomba P1: --", bg=BG_CARD, fg=TEXT_COLOR)
        self.w_lbl_p1.pack(anchor=tk.W)
        btn_w_box = tk.Frame(card_w, bg=BG_CARD)
        btn_w_box.pack(fill=tk.X, pady=(6, 0))
        tk.Button(btn_w_box, text="ARRANCAR P-101", bg='#1e293b', fg=ACCENT_GREEN, command=lambda: self._async_control('START', 'water')).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_w_box, text="PARAR P-101", bg='#1e293b', fg=ACCENT_RED, command=lambda: self._async_control('STOP', 'water')).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # 2. Gas Card
        card_g = tk.LabelFrame(grid_frame, text=" ⚡ Distribución de Gas (XV-201) ", bg=BG_CARD, fg=TEXT_COLOR, font=('Helvetica', 10, 'bold'), padx=10, pady=8)
        card_g.grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        self.g_lbl_badge = tk.Label(card_g, text="OK", bg='#003314', fg=ACCENT_GREEN, font=('Helvetica', 8, 'bold'))
        self.g_lbl_badge.pack(anchor=tk.E)
        self.g_lbl_press = tk.Label(card_g, text="Presión Gasoducto: -- PSI", bg=BG_CARD, fg=TEXT_COLOR)
        self.g_lbl_press.pack(anchor=tk.W)
        self.g_lbl_valve = tk.Label(card_g, text="Válvula XV-201: --", bg=BG_CARD, fg=TEXT_COLOR)
        self.g_lbl_valve.pack(anchor=tk.W)
        btn_g_box = tk.Frame(card_g, bg=BG_CARD)
        btn_g_box.pack(fill=tk.X, pady=(6, 0))
        tk.Button(btn_g_box, text="ABRIR XV-201", bg='#1e293b', fg=ACCENT_GREEN, command=lambda: self._async_control('OPEN', 'gas')).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_g_box, text="CERRAR XV-201", bg='#1e293b', fg=ACCENT_RED, command=lambda: self._async_control('CLOSE', 'gas')).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # 3. Eléctrico Card
        card_e = tk.LabelFrame(grid_frame, text=" 💡 Red de Potencia (CB-52) ", bg=BG_CARD, fg=TEXT_COLOR, font=('Helvetica', 10, 'bold'), padx=10, pady=8)
        card_e.grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
        self.e_lbl_badge = tk.Label(card_e, text="OK", bg='#003314', fg=ACCENT_GREEN, font=('Helvetica', 8, 'bold'))
        self.e_lbl_badge.pack(anchor=tk.E)
        self.e_lbl_volt = tk.Label(card_e, text="Tensión Subestación: -- V", bg=BG_CARD, fg=TEXT_COLOR)
        self.e_lbl_volt.pack(anchor=tk.W)
        self.e_lbl_cb = tk.Label(card_e, text="Disyuntor CB-52: --", bg=BG_CARD, fg=TEXT_COLOR)
        self.e_lbl_cb.pack(anchor=tk.W)
        btn_e_box = tk.Frame(card_e, bg=BG_CARD)
        btn_e_box.pack(fill=tk.X, pady=(6, 0))
        tk.Button(btn_e_box, text="CERRAR CB-52", bg='#1e293b', fg=ACCENT_GREEN, command=lambda: self._async_control('CLOSE', 'elec')).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_e_box, text="DISPARAR CB-52", bg='#1e293b', fg=ACCENT_RED, command=lambda: self._async_control('TRIP', 'elec')).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # 4. Transporte Card
        card_t = tk.LabelFrame(grid_frame, text=" 🚦 Tráfico y Ferrocarril ", bg=BG_CARD, fg=TEXT_COLOR, font=('Helvetica', 10, 'bold'), padx=10, pady=8)
        card_t.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
        self.t_lbl_badge = tk.Label(card_t, text="OK", bg='#003314', fg=ACCENT_GREEN, font=('Helvetica', 8, 'bold'))
        self.t_lbl_badge.pack(anchor=tk.E)
        self.t_lbl_light = tk.Label(card_t, text="Semáforo NTCIP: --", bg=BG_CARD, fg=TEXT_COLOR)
        self.t_lbl_light.pack(anchor=tk.W)
        self.t_lbl_gate = tk.Label(card_t, text="Barrera Paso Nivel: --", bg=BG_CARD, fg=TEXT_COLOR)
        self.t_lbl_gate.pack(anchor=tk.W)
        btn_t_box = tk.Frame(card_t, bg=BG_CARD)
        btn_t_box.pack(fill=tk.X, pady=(6, 0))
        tk.Button(btn_t_box, text="SUBIR BARRERA", bg='#1e293b', fg=ACCENT_GREEN, command=lambda: self._async_control('OPEN_GATE', 'transport')).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_t_box, text="BAJAR BARRERA", bg='#1e293b', fg=ACCENT_RED, command=lambda: self._async_control('CLOSE_GATE', 'transport')).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # Consola de Alarmas de Proceso (Treeview)
        alarm_frame = tk.LabelFrame(parent, text=" 🚨 Consola de Alarmas Activas (IEC 62443 L2/L3) ", bg=BG_CARD, fg=TEXT_COLOR, font=('Helvetica', 10, 'bold'), padx=6, pady=6)
        alarm_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        cols = ('id', 'sector', 'sev', 'msg')
        self.alarm_tree = ttk.Treeview(alarm_frame, columns=cols, show='headings', height=7)
        self.alarm_tree.heading('id', text='ID Alarma')
        self.alarm_tree.heading('sector', text='Sector')
        self.alarm_tree.heading('sev', text='Severidad')
        self.alarm_tree.heading('msg', text='Mensaje de Operación')
        self.alarm_tree.column('id', width=110, stretch=False)
        self.alarm_tree.column('sector', width=90, stretch=False)
        self.alarm_tree.column('sev', width=90, stretch=False)
        self.alarm_tree.column('msg', width=260, stretch=True)
        self.alarm_tree.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------------
    # Construcción Panel Derecho: Visualizador 2D Multisectorial & Blue Team
    # ------------------------------------------------------------------------

    def _build_viz_pane(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=BG_CARD, bd=1, relief=tk.SOLID, padx=10, pady=8)
        header.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            header,
            text="🌐 VISUALIZADOR URBANO 2D (:8090)",
            bg=BG_CARD,
            fg=ACCENT_CYAN,
            font=('Helvetica', 11, 'bold')
        ).pack(side=tk.LEFT)

        self.viz_badge_sis = tk.Label(header, text="SIS...", bg='#003314', fg=ACCENT_GREEN, font=('Helvetica', 9, 'bold'), padx=8)
        self.viz_badge_sis.pack(side=tk.RIGHT, padx=4)

        self.viz_badge_sys = tk.Label(header, text="SISTEMA...", bg='#003314', fg=ACCENT_GREEN, font=('Helvetica', 9, 'bold'), padx=8)
        self.viz_badge_sys.pack(side=tk.RIGHT, padx=4)

        # 8 Tarjetas de Sectores Urbanos (Grid 4x2)
        grid_8 = tk.Frame(parent, bg=BG_MAIN)
        grid_8.pack(fill=tk.BOTH, expand=False, pady=4)
        grid_8.columnconfigure(0, weight=1)
        grid_8.columnconfigure(1, weight=1)

        self.viz_sec_labels: Dict[str, Tuple[tk.Label, tk.Label]] = {}
        sector_specs = [
            ('water', '1. 💧 Agua Potable', 0, 0),
            ('gas', '2. ⚡ Red Gas Natural', 0, 1),
            ('elec', '3. 💡 Red Eléctrica', 1, 0),
            ('transport', '4. 🚦 Movilidad Urbana', 1, 1),
            ('hospital', '5. 🏥 Hospital / UCI', 2, 0),
            ('desal', '6. 🌊 Desalinizadora', 2, 1),
            ('lighting', '7. 💡 Alumbrado DALI', 3, 0),
            ('safety', '8. 🛡️ Seguridad SIS SIL-3', 3, 1),
        ]

        for sec_key, sec_title, r, c in sector_specs:
            box = tk.LabelFrame(grid_8, text=f" {sec_title} ", bg=BG_CARD, fg=TEXT_COLOR, font=('Helvetica', 9, 'bold'), padx=8, pady=4)
            box.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            b_lbl = tk.Label(box, text="OK", bg='#003314', fg=ACCENT_GREEN, font=('Helvetica', 8, 'bold'))
            b_lbl.pack(anchor=tk.E)
            val_lbl = tk.Label(box, text="Iniciando...", bg=BG_CARD, fg=TEXT_MUTED, font=('Helvetica', 8))
            val_lbl.pack(anchor=tk.W)
            self.viz_sec_labels[sec_key] = (b_lbl, val_lbl)

        # Blue Team Panel (SOC Alerts & SDN Mitigations)
        bt_frame = tk.LabelFrame(parent, text=" 🛡️ Blue Team — Centro de Operaciones SOC & SDN Controller ", bg=BG_CARD, fg=ACCENT_CYAN, font=('Helvetica', 10, 'bold'), padx=8, pady=6)
        bt_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        tk.Label(bt_frame, text="Alertas de Seguridad Correlacionadas (SIEM Ingest):", bg=BG_CARD, fg=ACCENT_AMBER, font=('Helvetica', 9, 'bold')).pack(anchor=tk.W)
        self.lbl_soc_alerts = tk.Label(bt_frame, text="Sin incidentes de seguridad correlacionados.", bg=BG_CARD, fg=TEXT_MUTED, justify=tk.LEFT, anchor=tk.W)
        self.lbl_soc_alerts.pack(anchor=tk.W, fill=tk.X, padx=4, pady=(2, 6))

        tk.Label(bt_frame, text="Mitigaciones SDN en Ejecución (OpenFlow Circuit-Breaker):", bg=BG_CARD, fg=ACCENT_CYAN, font=('Helvetica', 9, 'bold')).pack(anchor=tk.W)
        self.lbl_sdn_mitigations = tk.Label(bt_frame, text="Red operando bajo flujos normales.", bg=BG_CARD, fg=TEXT_MUTED, justify=tk.LEFT, anchor=tk.W)
        self.lbl_sdn_mitigations.pack(anchor=tk.W, fill=tk.X, padx=4, pady=(2, 0))

    # ------------------------------------------------------------------------
    # Hilos Daemon de Consulta en Segundo Plano
    # ------------------------------------------------------------------------

    def _poll_hmi_loop(self) -> None:
        while not self._stop_event.is_set():
            data = self.hmi_client.get_overview()
            with self._lock:
                self._raw_hmi_data = data
            time.sleep(2.0)

    def _poll_viz_loop(self) -> None:
        while not self._stop_event.is_set():
            data = self.viz_client.get_frame()
            with self._lock:
                self._raw_viz_data = data
            time.sleep(1.0)

    def _async_control(self, action: str, target: str) -> None:
        def worker() -> None:
            LOGGER.info("Enviando mando HMI: %s -> %s", action, target)
            res = self.hmi_client.send_control(action, target)
            if not res.get('success'):
                LOGGER.warning("Comando %s/%s rechazado: %s", action, target, res.get('error'))

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------------
    # Bucle Principal de Renderizado GUI (Hilos seguros)
    # ------------------------------------------------------------------------

    def _refresh_ui(self) -> None:
        try:
            with self._lock:
                hmi_raw = dict(self._raw_hmi_data)
                viz_raw = dict(self._raw_viz_data)

            if hmi_raw:
                hmi_view = derive_hmi_view_state(hmi_raw)
                self._render_hmi_view(hmi_view)

            if viz_raw:
                viz_view = derive_viz_view_state(viz_raw)
                self._render_viz_view(viz_view)

        except Exception as exc:
            LOGGER.debug("Error en refresco de GUI: %s", exc)
        finally:
            if not self._stop_event.is_set():
                self.root.after(300, self._refresh_ui)

    def _render_hmi_view(self, view: Dict[str, Any]) -> None:
        s_txt, s_col = view['scada_badge']
        self.hmi_badge_scada.config(text=s_txt, fg=s_col, bg='#003314' if s_col == ACCENT_GREEN else '#330009')

        h_txt, h_col = view['health_badge']
        self.hmi_badge_health.config(text=h_txt, fg=h_col, bg='#003314' if h_col == ACCENT_GREEN else '#330009')

        secs = view['sectors']
        # Agua
        w = secs['water']
        wb_txt, wb_col = w['badge']
        self.w_lbl_badge.config(text=wb_txt, fg=wb_col, bg='#003314' if wb_col == ACCENT_GREEN else '#330009')
        self.w_lbl_t1.config(text=f"Tanque T1: {w['t1_level']:.1f} m³")
        self.w_lbl_t2.config(text=f"Tanque T2: {w['t2_level']:.1f} m³")
        self.w_lbl_p1.config(text=f"Bomba P1: {'RUNNING' if w['pump_running'] else 'STOPPED'}")

        # Gas
        g = secs['gas']
        gb_txt, gb_col = g['badge']
        self.g_lbl_badge.config(text=gb_txt, fg=gb_col, bg='#003314' if gb_col == ACCENT_GREEN else '#330009')
        self.g_lbl_press.config(text=f"Presión: {g['pressure_psi']:.1f} PSI")
        self.g_lbl_valve.config(text=f"Válvula XV-201: {'ABIERTA' if g['valve_open'] else 'CERRADA'}")

        # Elec
        e = secs['elec']
        eb_txt, eb_col = e['badge']
        self.e_lbl_badge.config(text=eb_txt, fg=eb_col, bg='#003314' if eb_col == ACCENT_GREEN else '#330009')
        self.e_lbl_volt.config(text=f"Tensión: {e['grid_voltage']:.1f} V")
        self.e_lbl_cb.config(text=f"Disyuntor CB-52: {'CERRADO' if e['breaker_closed'] else 'DISPARADO'}")

        # Transport
        t = secs['transport']
        tb_txt, tb_col = t['badge']
        self.t_lbl_badge.config(text=tb_txt, fg=tb_col, bg='#003314' if tb_col == ACCENT_GREEN else '#330009')
        self.t_lbl_light.config(text=f"Semáforo: {t['traffic_light']}")
        self.t_lbl_gate.config(text=f"Barrera: {'ABIERTA' if t['gate_open'] else 'CERRADA'}")

        # Alarmas
        self.alarm_tree.delete(*self.alarm_tree.get_children())
        for a in view['alarms']:
            self.alarm_tree.insert('', tk.END, values=(
                a.get('alarm_id', '-'),
                a.get('sector', '-'),
                a.get('severity', '-'),
                a.get('message', '-')
            ))

    def _render_viz_view(self, view: Dict[str, Any]) -> None:
        sys_txt, sys_col = view['system_badge']
        self.viz_badge_sys.config(text=sys_txt, fg=sys_col, bg='#003314' if sys_col == ACCENT_GREEN else '#330009')
        self.lbl_global_status.config(text=sys_txt, fg=sys_col, bg='#003314' if sys_col == ACCENT_GREEN else '#330009')

        sis_txt, sis_col = view['sis_badge']
        self.viz_badge_sis.config(text=sis_txt, fg=sis_col, bg='#003314' if sis_col == ACCENT_GREEN else '#330009')

        secs = view['sectors']
        # 1. Water
        w = secs['water']
        wb_txt, wb_col = w['badge']
        self.viz_sec_labels['water'][0].config(text=wb_txt, fg=wb_col, bg='#003314' if wb_col == ACCENT_GREEN else '#330009')
        pump_state_str = 'ACTIVA' if w['pump_running'] else ('TRIP' if wb_txt == 'TRIP' else 'PARADA')
        self.viz_sec_labels['water'][1].config(text=f"Bomba: {pump_state_str} | Nivel: {w['tank_level']:.1f} m³")

        # 2. Gas
        g = secs['gas']
        gb_txt, gb_col = g['badge']
        self.viz_sec_labels['gas'][0].config(text=gb_txt, fg=gb_col, bg='#003314' if gb_col == ACCENT_GREEN else '#330009')
        self.viz_sec_labels['gas'][1].config(text=f"Presión: {g['pressure_psi']:.1f} PSI | Válvula: {'ABIERTA' if g['valve_open'] else 'CERRADA'}")

        # 3. Elec
        e = secs['elec']
        eb_txt, eb_col = e['badge']
        self.viz_sec_labels['elec'][0].config(text=eb_txt, fg=eb_col, bg='#003314' if eb_col == ACCENT_GREEN else '#330009')
        self.viz_sec_labels['elec'][1].config(text=f"Tensión: {e['grid_voltage']:.1f} V | Estado: {'BLACKOUT' if e['blackout'] else 'NORMAL'}")

        # 4. Transport
        tr = secs['transport']
        tb_txt, tb_col = tr['badge']
        self.viz_sec_labels['transport'][0].config(text=tb_txt, fg=tb_col, bg='#003314' if tb_col == ACCENT_GREEN else '#330009')
        self.viz_sec_labels['transport'][1].config(text=f"Semáforo: {tr['traffic_light']} | Congestión: {tr['congestion_pct']:.1f}%")

        # 5. Hospital
        h = secs['hospital']
        hb_txt, hb_col = h['badge']
        self.viz_sec_labels['hospital'][0].config(text=hb_txt, fg=hb_col, bg='#003314' if hb_col == ACCENT_GREEN else '#330009')
        self.viz_sec_labels['hospital'][1].config(text=f"Fuente: {'UPS / GENERADOR' if h['generator_active'] else 'RED'} | Carga: {h['load_kw']:.0f} kW")

        # 6. Desal
        d = secs['desal']
        db_txt, db_col = d['badge']
        self.viz_sec_labels['desal'][0].config(text=db_txt, fg=db_col, bg='#003314' if db_col == ACCENT_GREEN else '#330009')
        self.viz_sec_labels['desal'][1].config(text=f"Nivel Tanque: {d['tank_level_pct']:.1f}% | Consumo: {d['power_kw']:.0f} kW")

        # 7. Lighting
        l = secs['lighting']
        lb_txt, lb_col = l['badge']
        self.viz_sec_labels['lighting'][0].config(text=lb_txt, fg=lb_col, bg='#003314' if lb_col == ACCENT_GREEN else '#330009')
        self.viz_sec_labels['lighting'][1].config(text=f"Potencia: {l['power_kw']:.0f} kW | Modo: DALI AUTO")

        # 8. Safety
        s = secs['safety']
        sb_txt, sb_col = s['badge']
        self.viz_sec_labels['safety'][0].config(text=sb_txt, fg=sb_col, bg='#003314' if sb_col == ACCENT_GREEN else '#330009')
        self.viz_sec_labels['safety'][1].config(text=f"SIS Interlock: {'¡DISPARO SIL-3!' if s['sis_trip'] else 'ARMADO OK'}")

        # Blue Team SOC
        soc = view['soc_alerts']
        if soc:
            lines = []
            for a in soc:
                lines.append(f"• [{a.get('alert_id', 'ALERTA')}] {a.get('name', 'Amenaza')} (IP Atacante: {a.get('attacker_ip', 'UNK')})")
            self.lbl_soc_alerts.config(text="\n".join(lines), fg=ACCENT_RED)
        else:
            self.lbl_soc_alerts.config(text="Sin incidentes de seguridad correlacionados.", fg=TEXT_MUTED)

        # Blue Team SDN
        sdn = view['sdn_mitigations']
        if sdn:
            lines = []
            for m in sdn:
                lines.append(f"• [{m.get('mechanism', 'SDN')}] Host {m.get('offending_ip', '-')} aislado en {m.get('switch', 's2')} ({m.get('rule', 'DoS')})")
            self.lbl_sdn_mitigations.config(text="\n".join(lines), fg=ACCENT_CYAN)
        else:
            self.lbl_sdn_mitigations.config(text="Red operando bajo flujos normales.", fg=TEXT_MUTED)

    def _on_close(self) -> None:
        self._stop_event.set()
        try:
            self.root.destroy()
        except Exception:
            pass


def main() -> None:
    """Punto de entrada de citylab_gui. Resistencia total ante entornos sin DISPLAY/X11."""
    try:
        app = CityLabDashboardApp()
        app.root.mainloop()
    except (tk.TclError if tk is not None else Exception, Exception) as exc:
        LOGGER.error("No se pudo iniciar la interfaz gráfica Tkinter (DISPLAY/X11): %s", exc)
        print(f"[citylab_gui] No se pudo inicializar entorno gráfico X11: {exc}", file=sys.stderr)
        print("[citylab_gui] Si ejecutas bajo sudo, ejecuta primero en tu terminal: xhost +SI:localuser:root", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
