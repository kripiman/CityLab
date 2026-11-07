#!/usr/bin/env python3
"""network/gui_clients.py — Clientes HTTP de transporte del dashboard (CAPA 1).

Extraídos de citylab_gui.py: resiliencia total, timeouts cortos y safe defaults;
nunca propagan excepciones hacia la GUI.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from typing import Any, Dict, Optional

LOGGER = logging.getLogger('citylab_gui.clients')

DEFAULT_HMI_URL = os.getenv('HMI_HTTP_URL', os.getenv('HMI_URL', 'http://10.0.2.20:8085'))
DEFAULT_VIZ_URL = os.getenv('VIZ_HTTP_URL', os.getenv('VIZ_URL', 'http://10.0.2.20:8090'))


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
