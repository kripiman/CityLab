#!/usr/bin/env python3
"""network/siem_pipeline.py — SOC / SIEM Enterprise Pipeline (ELK / Graylog Integration) (Fase 8)

Pipeline de recolección, normalización y correlación de eventos de seguridad IT/OT:
  - Formato estandarizado ECS (Elastic Common Schema) / Syslog RFC 5424.
  - Recolección de fuentes multi-sector:
    * Modbus DPI Proxy (`network/modbus_proxy.py` — F-05, anomalías Modbus).
    * SDN Circuit Breaker (`network/sdn_controller.py` — aislamiento host s3/s5).
    * Active Directory DC (`network/ad_dc_emulator.py` — autenticación Kerberos/LDAP).
    * SCADA Watchdog (`network/scada_server.py` — Loss of View / Loss of Control).
    * Honeypot OT (`VLAN s5` — escaneos y pivoteo en F-11).
  - Motor de Reglas de Correlación SOC para detección de ataques ciberfísicos en cascada.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger('siem_pipeline')


@dataclass
class EcsEvent:
    timestamp: str
    event_category: str       # 'network', 'authentication', 'process_control', 'honeypot'
    event_type: str           # 'alert', 'denial', 'allowed', 'system_trip'
    severity: str             # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    source_ip: str
    destination_ip: str
    service_name: str
    message: str
    metadata: Dict[str, Any]


class SiemCorrelationEngine:
    """Motor de correlación SIEM para alertas de seguridad ciberfísica."""

    def __init__(self) -> None:
        self.events_buffer: List[EcsEvent] = []
        self.active_alerts: List[Dict[str, Any]] = []

    def ingest_raw_event(
        self,
        event_category: str,
        event_type: str,
        severity: str,
        source_ip: str,
        destination_ip: str,
        service_name: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EcsEvent:
        event = EcsEvent(
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            event_category=event_category,
            event_type=event_type,
            severity=severity.upper(),
            source_ip=source_ip,
            destination_ip=destination_ip,
            service_name=service_name,
            message=message,
            metadata=metadata or {}
        )
        self.events_buffer.append(event)
        self._evaluate_correlation_rules(event)
        return event

    def _evaluate_correlation_rules(self, event: EcsEvent) -> None:
        """Aplica reglas de correlación SOC sobre los eventos ingresados."""
        # Regla 1: Detección de Ataque en Cascada IT->OT
        # (Escaneo Honeypot en s5 seguido inmediatamente de inyección Modbus/DNP3)
        honeypot_events = [
            e for e in self.events_buffer[-10:]
            if e.event_category == 'honeypot' and e.source_ip == event.source_ip
        ]
        modbus_dpi_alerts = [
            e for e in self.events_buffer[-10:]
            if e.event_category == 'process_control' and e.severity in ('HIGH', 'CRITICAL')
        ]

        if honeypot_events and modbus_dpi_alerts:
            alert = {
                'alert_id': f"SOC-ALT-{len(self.active_alerts)+1:04d}",
                'name': 'Ataque Ciberfísico en Cascada Detectado (IT Pivoting -> OT Injection)',
                'severity': 'CRITICAL',
                'attacker_ip': event.source_ip,
                'evidence': [asdict(e) for e in honeypot_events + modbus_dpi_alerts],
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
            if not any(a['name'] == alert['name'] and a['attacker_ip'] == alert['attacker_ip'] for a in self.active_alerts):
                self.active_alerts.append(alert)
                LOGGER.critical('[SIEM-CORRELATION] ¡ALERTA SOC CRÍTICA! %s desde IP %s', alert['name'], event.source_ip)

        # Regla 2: Inyección / Spoofing GOOSE IEC 61850 (Industroyer2 Pattern)
        if event.event_category == 'process_control' and ('GOOSE' in event.message.upper() or event.service_name == 'iec61850_emulator'):
            alert = {
                'alert_id': f"SOC-ALT-{len(self.active_alerts)+1:04d}",
                'name': 'Ataque por Inyección / Spoofing de Mensajes GOOSE IEC 61850 (Industroyer2 Pattern)',
                'severity': 'CRITICAL',
                'attacker_ip': event.source_ip,
                'evidence': [asdict(event)],
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
            if not any(a['name'] == alert['name'] and a['attacker_ip'] == alert['attacker_ip'] for a in self.active_alerts):
                self.active_alerts.append(alert)
                LOGGER.critical('[SIEM-CORRELATION] ¡ALERTA SOC CRÍTICA! %s desde IP %s', alert['name'], event.source_ip)

    def export_elk_json(self) -> str:
        """Exporta buffer de eventos en formato JSON compatible con Logstash / Elasticsearch."""
        return json.dumps([asdict(e) for e in self.events_buffer], indent=2)
