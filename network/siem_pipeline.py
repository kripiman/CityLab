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

        # Regla 3: Alerta de Inspección Pasiva Zeek / Suricata Coincidente
        if 'zeek' in event.service_name or 'suricata' in event.service_name:
            if event.severity in ('HIGH', 'CRITICAL'):
                alert = {
                    'alert_id': f"SOC-ALT-{len(self.active_alerts)+1:04d}",
                    'name': f"Alerta de Inspección Pasiva Network Bridge ({event.service_name})",
                    'severity': event.severity,
                    'attacker_ip': event.source_ip,
                    'evidence': [asdict(event)],
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                }
                if not any(a['name'] == alert['name'] and a['attacker_ip'] == alert['attacker_ip'] for a in self.active_alerts):
                    self.active_alerts.append(alert)
                    LOGGER.info('[SIEM-PASSIVE] Alerta SOC inspección pasiva desde IP %s', event.source_ip)

    def ingest_zeek_log(self, raw_entry: Dict[str, Any] | str) -> EcsEvent:
        """Ingiere y normaliza un registro de log Zeek (conn.log, notice.log, modbus.log)."""
        data: Dict[str, Any] = json.loads(raw_entry) if isinstance(raw_entry, str) else raw_entry
        src_ip = data.get('id.orig_h') or data.get('id_orig_h') or data.get('src_ip') or '0.0.0.0'
        dst_ip = data.get('id.resp_h') or data.get('id_resp_h') or data.get('dst_ip') or '0.0.0.0'
        proto = data.get('proto') or data.get('service') or 'zeek'
        note = str(data.get('note') or data.get('msg') or data.get('history') or 'Zeek passive traffic record')
        action = data.get('action') or ('alert' if 'notice' in note.lower() or 'unauthorized' in note.lower() else 'allowed')
        severity = 'HIGH' if action == 'alert' or 'unauthorized' in note.lower() or 'attack' in note.lower() else 'LOW'

        return self.ingest_raw_event(
            event_category='network' if 'modbus' not in str(proto).lower() else 'process_control',
            event_type=action,
            severity=severity,
            source_ip=src_ip,
            destination_ip=dst_ip,
            service_name=f'zeek_{proto}',
            message=f"Zeek Event [{proto}]: {note}",
            metadata=data
        )

    def ingest_suricata_eve(self, raw_entry: Dict[str, Any] | str) -> EcsEvent:
        """Ingiere y normaliza un registro de alerta Suricata Eve JSON (eve.json)."""
        data: Dict[str, Any] = json.loads(raw_entry) if isinstance(raw_entry, str) else raw_entry
        src_ip = data.get('src_ip') or '0.0.0.0'
        dst_ip = data.get('dest_ip') or '0.0.0.0'
        event_type = data.get('event_type') or 'alert'
        
        alert_info = data.get('alert') or {}
        sig = alert_info.get('signature') or data.get('message') or 'Suricata alert signature'
        suricata_sev = alert_info.get('severity', 3)
        severity_map = {1: 'CRITICAL', 2: 'HIGH', 3: 'MEDIUM', 4: 'LOW'}
        severity = severity_map.get(suricata_sev, 'MEDIUM')

        return self.ingest_raw_event(
            event_category='network',
            event_type=event_type,
            severity=severity,
            source_ip=src_ip,
            destination_ip=dst_ip,
            service_name='suricata_eve',
            message=f"Suricata Eve Alert: {sig}",
            metadata=data
        )

    def export_elk_json(self) -> str:
        """Exporta buffer de eventos en formato JSON compatible con Logstash / Elasticsearch."""
        return json.dumps([asdict(e) for e in self.events_buffer], indent=2)

    def export_file(self, filepath: str) -> None:
        """Guarda buffer de eventos ECS en un archivo JSON en disco."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.export_elk_json())

    def export_syslog_rfc5424(self) -> List[str]:
        """Exporta eventos en formato Syslog estandarizado RFC 5424."""
        lines = []
        for e in self.events_buffer:
            pri = 13 if e.severity in ('HIGH', 'CRITICAL') else 14  # Notice / Informational
            line = f"<{pri}>1 {e.timestamp} citylab-siem {e.service_name} - - - [{e.event_category} src={e.source_ip} dst={e.destination_ip}] {e.message}"
            lines.append(line)
        return lines
