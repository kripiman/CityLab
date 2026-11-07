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

import logging
import os
import sys
import threading
import time
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

# CAPA 1 (clientes HTTP) y CAPA 2 (derivación de estado de vista) viven ahora en
# módulos propios; se re-exportan para que `from network.citylab_gui import ...`
# siga funcionando (tests y lanzadores dependen de estos nombres).
from network.gui_clients import (
    DEFAULT_HMI_URL,
    DEFAULT_VIZ_URL,
    HmiClient,
    VizClient,
    _http_get_json,
    _http_post_json,
)
from network.gui_view_state import derive_hmi_view_state, derive_viz_view_state


# CAPA 3: Aplicación de Escritorio Nativa (Tkinter / Dark SCADA Theme)

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

    # Construcción Panel Izquierdo: HMI Industrial

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

        # Resultado del ultimo mando enviado (exito real vs. rechazo del Proxy DPI/PLC)
        self.lbl_control_result = tk.Label(
            parent,
            text="Sin comandos enviados todavia.",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            justify=tk.LEFT,
            anchor=tk.W,
            wraplength=520,
            padx=8,
            pady=6
        )
        self.lbl_control_result.pack(fill=tk.X, pady=(6, 0))

    # Construcción Panel Derecho: Visualizador 2D Multisectorial & Blue Team

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

    # Hilos Daemon de Consulta en Segundo Plano

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
            # Tkinter no es thread-safe: marshaling del resultado al hilo principal via .after().
            self.root.after(0, lambda: self._show_control_result(action, target, res))

        threading.Thread(target=worker, daemon=True).start()

    def _show_control_result(self, action: str, target: str, res: Dict[str, Any]) -> None:
        if res.get('success'):
            self.lbl_control_result.config(
                text=f"✅ {action} -> {target}: ejecutado en el PLC.",
                fg=ACCENT_GREEN
            )
        else:
            self.lbl_control_result.config(
                text=f"⛔ {action} -> {target}: {res.get('error', 'rechazado')}",
                fg=ACCENT_RED
            )

    # Bucle Principal de Renderizado GUI (Hilos seguros)

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
