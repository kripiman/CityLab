#!/usr/bin/env python3
"""network/tests/test_siem.py — Pruebas unitarias para SOC/SIEM Pipeline (Fase 8)"""
from __future__ import annotations

import json
import unittest
from network.siem_pipeline import SiemCorrelationEngine, EcsEvent


class TestSiemPipeline(unittest.TestCase):

    def setUp(self) -> None:
        self.siem = SiemCorrelationEngine()

    def test_event_ingestion_and_ecs_format(self) -> None:
        event = self.siem.ingest_raw_event(
            event_category='authentication',
            event_type='allowed',
            severity='LOW',
            source_ip='10.0.1.50',
            destination_ip='10.0.2.10',
            service_name='ad_dc_emulator',
            message='Kerberos AS-REQ authentication successful'
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.severity, 'LOW')
        self.assertEqual(event.event_category, 'authentication')

    def test_cascading_attack_correlation_rule(self) -> None:
        # Ingest Honeypot scan event
        self.siem.ingest_raw_event(
            event_category='honeypot',
            event_type='alert',
            severity='MEDIUM',
            source_ip='10.0.5.99',
            destination_ip='10.0.5.10',
            service_name='honeypot_vlan5',
            message='Port scan detected on honeypot interface'
        )
        
        # Ingest malicious Modbus DPI injection event from same source IP
        self.siem.ingest_raw_event(
            event_category='process_control',
            event_type='denial',
            severity='CRITICAL',
            source_ip='10.0.5.99',
            destination_ip='10.0.3.20',
            service_name='modbus_proxy',
            message='Unauthorized Write Single Coil 0x05 blocked by DPI Proxy'
        )
        
        self.assertEqual(len(self.siem.active_alerts), 1)
        alert = self.siem.active_alerts[0]
        self.assertEqual(alert['severity'], 'CRITICAL')
        self.assertEqual(alert['attacker_ip'], '10.0.5.99')

    def test_elk_json_export(self) -> None:
        self.siem.ingest_raw_event(
            event_category='network',
            event_type='alert',
            severity='HIGH',
            source_ip='10.0.1.99',
            destination_ip='10.0.3.1',
            service_name='sdn_controller',
            message='Rate limiting flow installed for offending host'
        )
        export_str = self.siem.export_elk_json()
        parsed = json.loads(export_str)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 1)


if __name__ == '__main__':
    unittest.main()
