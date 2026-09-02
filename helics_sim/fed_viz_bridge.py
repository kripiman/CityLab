#!/usr/bin/env python3
"""helics_sim/fed_viz_bridge.py — Puente de Telemetría HELICS / SCADA $\to$ Viz Server (Fase 9).

Suscribe métricas ciberfísicas del bus HELICS y las proyecta al Servidor Visualizador 2D:
  - Tópicos multisectoriales (water, gas, elec, transport, hospital, desal, lighting, safety).
  - Modo dual: co-simulación HELICS nativa o SCADA Poller con autenticación RBAC Bearer.
  - Throttling acumulado a 1 Hz y despacho por lotes (batch / individual).
  - Resiliente ante caídas de red o reinicios de viz_server (never-crash policy).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Sequence

try:
    import helics as h
    HAS_HELICS = True
except ImportError:
    h = None  # type: ignore
    HAS_HELICS = False

LOGGER = logging.getLogger('fed_viz_bridge')

# Configuración y valores por defecto
DEFAULT_VIZ_URL = os.environ.get('VIZ_URL', 'http://127.0.0.1:8090')
DEFAULT_SCADA_URL = os.environ.get('SCADA_URL', 'http://127.0.0.1:8080')
DEFAULT_SCADA_TOKEN = os.environ.get('SCADA_BEARER_TOKEN', 'auditor:AUDIT_TOKEN_2026')

POLL_INTERVAL = 1.0  # s
THROTTLE_INTERVAL = 1.0  # s (tasa máxima de despacho: 1 Hz)
FED_NAME = os.environ.get('HELICS_FED_NAME', 'VIZ_BRIDGE_fed')
BROKER_ADDRESS = os.environ.get('HELICS_BROKER_ADDRESS', '127.0.0.1')
BROKER_PORT = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
MAX_STEPS = int(os.environ.get('HELICS_MAX_STEPS', '0'))


def format_bearer_header(token: str) -> str:
    """Asegura formato RFC 6750 Bearer <token>."""
    raw = (token or '').strip()
    if raw.startswith('Bearer '):
        return raw
    return f"Bearer {raw}"


class VizBridgeEngine:
    """Motor desacoplado de normalización, acumulación y despacho de telemetría."""

    def __init__(self, viz_url: str = DEFAULT_VIZ_URL, throttle_sec: float = THROTTLE_INTERVAL) -> None:
        self.viz_url = viz_url.rstrip('/')
        self.throttle_sec = throttle_sec
        self.last_dispatch_time = 0.0
        self.state_buffer: Dict[str, Dict[str, Any]] = {}

    def update_metrics_from_helics(self, raw_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Mapea datos crudos HELICS a esquemas válidos para CityVisualizerStateEngine."""
        sectors: Dict[str, Dict[str, Any]] = {}

        # 1. Water
        w_t2 = raw_data.get('water/t2_level')
        w_t1 = raw_data.get('water/t1_level')
        w_trip = raw_data.get('breaker/trip')
        w_dict: Dict[str, Any] = {}
        if w_t2 is not None and w_t2 > -900:
            w_dict['tank_level'] = float(w_t2)
        if w_t1 is not None and w_t1 > -900:
            w_dict['t1_level'] = float(w_t1)
        if w_trip is not None and w_trip >= 0:
            w_dict['alert'] = bool(w_trip)
            w_dict['pump_running'] = not bool(w_trip)
        if w_dict:
            sectors['water'] = w_dict

        # 2. Gas
        g_press = raw_data.get('gas/pressure')
        g_trip = raw_data.get('gas/trip')
        g_dict: Dict[str, Any] = {}
        if g_press is not None and g_press > -900:
            g_dict['pressure_psi'] = float(g_press)
        if g_trip is not None and g_trip >= 0:
            g_dict['alert'] = bool(g_trip)
            g_dict['valve_open'] = not bool(g_trip)
        if g_dict:
            sectors['gas'] = g_dict

        # 3. Elec
        e_volt = raw_data.get('grid/voltage_pu')
        e_freq = raw_data.get('grid/frequency')
        e_trip = raw_data.get('grid/trip')
        e_dict: Dict[str, Any] = {}
        if e_volt is not None and e_volt > -900:
            e_dict['grid_voltage'] = float(e_volt) * 230.0
        if e_freq is not None and e_freq > -900:
            e_dict['frequency'] = float(e_freq)
        if e_trip is not None and e_trip >= 0:
            e_dict['blackout'] = bool(e_trip)
        if e_dict:
            sectors['elec'] = e_dict

        # 4. Transport
        t_cong = raw_data.get('transport/congestion')
        t_trip = raw_data.get('transport/trip')
        t_dict: Dict[str, Any] = {}
        if t_cong is not None and t_cong > -900:
            t_dict['congestion_pct'] = float(t_cong) * 100.0
            t_dict['traffic_light'] = 'RED' if t_cong > 0.8 else ('AMBER' if t_cong > 0.5 else 'GREEN')
        if t_trip is not None and t_trip >= 0:
            t_dict['railway_gate'] = 'CLOSED' if t_trip else 'OPEN'
        if t_dict:
            sectors['transport'] = t_dict

        # 5. Hospital
        h_load = raw_data.get('hospital/load_kw')
        h_ups = raw_data.get('hospital/on_ups')
        h_dict: Dict[str, Any] = {}
        if h_load is not None and h_load > -900:
            h_dict['load_kw'] = float(h_load)
        if h_ups is not None and h_ups >= 0:
            h_dict['powered'] = True
            h_dict['generator_active'] = bool(h_ups)
        if h_dict:
            sectors['hospital'] = h_dict

        # 6. Desal (Enmiendas 1 y 5)
        d_trip = raw_data.get('desal/pump_trip')
        d_kw = raw_data.get('desal/power_kw')
        d_level = raw_data.get('desal/tank_level_pct')
        d_dict: Dict[str, Any] = {}
        if d_trip is not None and d_trip >= 0:
            d_dict['pump_trip'] = bool(d_trip)
        if d_kw is not None and d_kw > -900:
            d_dict['power_kw'] = float(d_kw)
        if d_level is not None and d_level > -900:
            d_dict['tank_level_pct'] = float(d_level)
        if d_dict:
            sectors['desal'] = d_dict

        # 7. Lighting (Enmiendas 1 y 5)
        l_kw = raw_data.get('lighting/power_kw')
        l_dict: Dict[str, Any] = {}
        if l_kw is not None and l_kw > -900:
            l_dict['power_kw'] = float(l_kw)
        if l_dict:
            sectors['lighting'] = l_dict

        # 8. Safety / SIS (Enmiendas 1 y 5)
        s_trip = raw_data.get('sis/trip')
        s_dict: Dict[str, Any] = {}
        if s_trip is not None and s_trip >= 0:
            s_dict['sis_trip'] = bool(s_trip)
        if s_dict:
            sectors['safety'] = s_dict

        for sec, payload in sectors.items():
            if sec not in self.state_buffer:
                self.state_buffer[sec] = {}
            self.state_buffer[sec].update(payload)

        return sectors

    def update_metrics_from_scada(self, scada_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Mapea telemetría SCADA REST (/api/telemetry) a esquemas del visualizador."""
        sectors: Dict[str, Dict[str, Any]] = {}
        raw_sectors = scada_data.get('sectors', {})

        for sector, s_info in raw_sectors.items():
            if not isinstance(s_info, dict):
                continue
            status = s_info.get('status', 'OFFLINE')
            running = bool(s_info.get('actuator_running', False))
            fault = bool(s_info.get('fault', False))
            coils = s_info.get('coils', [False, False, False, False])

            if sector == 'water':
                sectors['water'] = {
                    'pump_running': running,
                    'alert': fault or (status == 'LOSS_OF_VIEW'),
                }
            elif sector == 'gas':
                sectors['gas'] = {
                    'valve_open': running,
                    'alert': fault or (status == 'LOSS_OF_VIEW'),
                }
            elif sector == 'elec':
                sectors['elec'] = {
                    'blackout': fault or (status == 'LOSS_OF_VIEW') or (len(coils) > 0 and not coils[0]),
                }
            elif sector == 'transport':
                sectors['transport'] = {
                    'railway_gate': 'OPEN' if running else 'CLOSED',
                    'traffic_light': 'RED' if fault else 'GREEN',
                }
            elif sector == 'hospital':
                sectors['hospital'] = {
                    'powered': status == 'ONLINE',
                    'generator_active': running or fault,
                }

        for sec, payload in sectors.items():
            if sec not in self.state_buffer:
                self.state_buffer[sec] = {}
            self.state_buffer[sec].update(payload)

        return sectors

    def dispatch(self, force: bool = False) -> bool:
        """Despacha estado acumulado a VIZ_URL respetando throttling 1 Hz."""
        now = time.time()
        if not force and (now - self.last_dispatch_time < self.throttle_sec):
            return False

        if not self.state_buffer:
            return False

        payload = json.dumps({'sectors': self.state_buffer}).encode('utf-8')
        endpoint = f"{self.viz_url}/api/viz/update"

        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    self.last_dispatch_time = now
                    self.state_buffer.clear()
                    return True
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            LOGGER.warning("[VIZ_BRIDGE] Despacho a %s fallido: %s", endpoint, exc)
            return False

        return False


def poll_scada_once(scada_url: str, token: str, timeout: float = 2.0) -> Optional[Dict[str, Any]]:
    """Consulta /api/telemetry de SCADA Server con cabecera Authorization: Bearer."""
    endpoint = f"{scada_url.rstrip('/')}/api/telemetry"
    req = urllib.request.Request(
        endpoint,
        headers={'Authorization': format_bearer_header(token)}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode('utf-8'))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        LOGGER.debug("[VIZ_BRIDGE] Consulta SCADA %s fallida: %s", endpoint, exc)
    return None


def run_standalone_loop(engine: VizBridgeEngine, scada_url: str, scada_token: str, max_steps: int = 0) -> int:
    """Bucle operativo en modo SCADA Poller (sin broker HELICS)."""
    LOGGER.info("[VIZ_BRIDGE] Iniciando modo standalone SCADA poller (SCADA=%s, VIZ=%s)", scada_url, engine.viz_url)
    steps = 0
    try:
        while True:
            data = poll_scada_once(scada_url, scada_token)
            if data:
                engine.update_metrics_from_scada(data)
                engine.dispatch(force=True)

            steps += 1
            if max_steps > 0 and steps >= max_steps:
                break
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        LOGGER.info("[VIZ_BRIDGE] Parada solicitada por operador.")
    return 0


def create_helics_subscriptions(fed: Any) -> Dict[str, Any]:
    """Registra suscripciones a todos los tópicos ciberfísicos verificados."""
    subs = {
        'water/t2_level': h.helicsFederateRegisterSubscription(fed, 'water/t2_level', ''),
        'water/t1_level': h.helicsFederateRegisterSubscription(fed, 'water/t1_level', ''),
        'breaker/trip': h.helicsFederateRegisterSubscription(fed, 'breaker/trip', ''),
        'gas/pressure': h.helicsFederateRegisterSubscription(fed, 'gas/pressure', ''),
        'gas/trip': h.helicsFederateRegisterSubscription(fed, 'gas/trip', ''),
        'grid/frequency': h.helicsFederateRegisterSubscription(fed, 'grid/frequency', ''),
        'grid/voltage_pu': h.helicsFederateRegisterSubscription(fed, 'grid/voltage_pu', ''),
        'grid/trip': h.helicsFederateRegisterSubscription(fed, 'grid/trip', ''),
        'transport/congestion': h.helicsFederateRegisterSubscription(fed, 'transport/congestion', ''),
        'transport/trip': h.helicsFederateRegisterSubscription(fed, 'transport/trip', ''),
        'hospital/load_kw': h.helicsFederateRegisterSubscription(fed, 'hospital/load_kw', ''),
        'hospital/on_ups': h.helicsFederateRegisterSubscription(fed, 'hospital/on_ups', ''),
        'desal/pump_trip': h.helicsFederateRegisterSubscription(fed, 'desal/pump_trip', ''),
        'desal/power_kw': h.helicsFederateRegisterSubscription(fed, 'desal/power_kw', ''),
        'desal/tank_level_pct': h.helicsFederateRegisterSubscription(fed, 'desal/tank_level_pct', ''),
        'lighting/power_kw': h.helicsFederateRegisterSubscription(fed, 'lighting/power_kw', ''),
        'sis/trip': h.helicsFederateRegisterSubscription(fed, 'sis/trip', ''),
    }
    return subs


def read_helics_metrics(subs: Dict[str, Any]) -> Dict[str, Any]:
    """Extrae valores actualizados de las suscripciones HELICS."""
    data: Dict[str, Any] = {}
    for topic, sub in subs.items():
        if not h.helicsInputIsValid(sub):
            continue
        try:
            if topic in ('breaker/trip', 'gas/trip', 'grid/trip', 'transport/trip', 'hospital/on_ups',
                         'desal/pump_trip', 'sis/trip'):
                data[topic] = h.helicsInputGetInteger(sub)
            else:
                data[topic] = h.helicsInputGetDouble(sub)
        except Exception as exc:
            LOGGER.debug("[VIZ_BRIDGE] Error leyendo tópico %s: %s", topic, exc)
    return data


def run_helics_loop(engine: VizBridgeEngine, broker_addr: str, broker_port: int, max_steps: int = 0) -> int:
    """Bucle operativo sincronizado con bus HELICS."""
    if not HAS_HELICS:
        LOGGER.error("[VIZ_BRIDGE] pyhelics no está instalado. Use modo --standalone.")
        return 1

    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, 'zmq')
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f'--federates=1 --broker_address={broker_addr} --brokerport={broker_port}'
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate(FED_NAME, fi)

    subs = create_helics_subscriptions(fed)
    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info("[VIZ_BRIDGE] Federado HELICS %s listo (broker=%s:%d, VIZ=%s)",
                FED_NAME, broker_addr, broker_port, engine.viz_url)

    current_time = 0.0
    steps = 0
    try:
        while True:
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)
            raw = read_helics_metrics(subs)
            engine.update_metrics_from_helics(raw)
            engine.dispatch(force=False)

            steps += 1
            if max_steps > 0 and steps >= max_steps:
                break
            time.sleep(0.05)
    except KeyboardInterrupt:
        LOGGER.info("[VIZ_BRIDGE] Cierre solicitado.")
    finally:
        try:
            h.helicsFederateFinalize(fed)
            h.helicsFederateFree(fed)
        except Exception:
            pass
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab HELICS / SCADA to Viz Server Bridge")
    parser.add_argument("--viz-url", default=DEFAULT_VIZ_URL, help=f"URL del servidor visualizador (default: {DEFAULT_VIZ_URL})")
    parser.add_argument("--scada-url", default=DEFAULT_SCADA_URL, help=f"URL del SCADA Server para fallback (default: {DEFAULT_SCADA_URL})")
    parser.add_argument("--scada-token", default=DEFAULT_SCADA_TOKEN, help="Token RBAC Bearer para consultas SCADA")
    parser.add_argument("--standalone", action="store_true", help="Forzar modo SCADA Poller sin broker HELICS")
    parser.add_argument("--broker-address", default=BROKER_ADDRESS, help=f"Host broker HELICS (default: {BROKER_ADDRESS})")
    parser.add_argument("--broker-port", type=int, default=BROKER_PORT, help=f"Puerto broker HELICS (default: {BROKER_PORT})")
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS, help="Límite de pasos (0 = infinito)")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][VIZ_BRIDGE] %(message)s')
    engine = VizBridgeEngine(viz_url=args.viz_url)

    is_standalone = args.standalone or os.environ.get('HELICS_STANDALONE', '0') == '1' or not HAS_HELICS

    if is_standalone:
        return run_standalone_loop(engine, args.scada_url, args.scada_token, max_steps=args.max_steps)
    else:
        return run_helics_loop(engine, args.broker_address, args.broker_port, max_steps=args.max_steps)


if __name__ == '__main__':
    sys.exit(main())
