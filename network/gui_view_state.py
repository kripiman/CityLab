#!/usr/bin/env python3
"""network/gui_view_state.py — Derivación pura de estado de vista (CAPA 2).

Extraída de citylab_gui.py: funciones sin I/O, unit-testables. Replican la lógica
JS de hmi_server.py (updateHmi) y viz_server.py (render).
"""
from __future__ import annotations

from typing import Any, Dict


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
