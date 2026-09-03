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
        event = parsed[0]
        self.assertEqual(event['source_ip'], '10.0.1.99')
        self.assertEqual(event['destination_ip'], '10.0.3.1')
        self.assertEqual(event['severity'], 'HIGH')
        self.assertEqual(event['event_category'], 'network')
        self.assertEqual(event['event_type'], 'alert')
        self.assertEqual(event['service_name'], 'sdn_controller')
        self.assertEqual(event['message'], 'Rate limiting flow installed for offending host')
        self.assertIn('timestamp', event)

    def test_syslog_rfc5424_export(self) -> None:
        self.siem.ingest_raw_event(
            event_category='network',
            event_type='alert',
            severity='HIGH',
            source_ip='10.0.1.99',
            destination_ip='10.0.3.1',
            service_name='sdn_controller',
            message='Rate limiting flow installed'
        )
        syslog_lines = self.siem.export_syslog_rfc5424()
        self.assertEqual(len(syslog_lines), 1)
        self.assertIn('<13>1', syslog_lines[0])
        self.assertIn('citylab-siem', syslog_lines[0])

    def test_export_file(self) -> None:
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            self.siem.ingest_raw_event('network', 'alert', 'LOW', '10.0.1.1', '10.0.1.2', 'test', 'msg')
            self.siem.export_file(tmp_path)
            self.assertTrue(os.path.exists(tmp_path))
            with open(tmp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.assertEqual(len(data), 1)
            event = data[0]
            self.assertEqual(event['source_ip'], '10.0.1.1')
            self.assertEqual(event['destination_ip'], '10.0.1.2')
            self.assertEqual(event['severity'], 'LOW')
            self.assertEqual(event['event_category'], 'network')
            self.assertEqual(event['event_type'], 'alert')
            self.assertEqual(event['service_name'], 'test')
            self.assertEqual(event['message'], 'msg')
            self.assertIn('timestamp', event)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    def test_goose_injection_correlation_rule(self) -> None:
        """Verifica que la Regla 2 (Industroyer2 GOOSE Spoofing) active alerta crítica."""
        self.siem.ingest_raw_event(
            event_category='process_control',
            event_type='alert',
            severity='CRITICAL',
            source_ip='10.0.1.10',
            destination_ip='10.0.3.20',
            service_name='iec61850_emulator',
            message='IEC 61850 GOOSE Anomaly Detected: Sequence Jump (stNum spoofing)'
        )
        self.assertGreaterEqual(len(self.siem.active_alerts), 1)
        alert = self.siem.active_alerts[-1]
        self.assertEqual(alert['severity'], 'CRITICAL')
        self.assertIn('GOOSE', alert['name'])
        self.assertEqual(alert['attacker_ip'], '10.0.1.10')


    def test_siem_http_server_endpoints(self) -> None:
        from network.siem_pipeline import SiemRequestHandler, ThreadedSiemServer
        import threading
        import urllib.request

        SiemRequestHandler.engine = self.siem
        server = ThreadedSiemServer(('127.0.0.1', 0), SiemRequestHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            # 1. GET /health
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode())
                self.assertEqual(data['status'], 'ONLINE')

            # 2. POST /api/siem/event
            payload = json.dumps({
                'event_category': 'network',
                'event_type': 'alert',
                'severity': 'HIGH',
                'source_ip': '10.0.1.5',
                'destination_ip': '10.0.3.10',
                'service_name': 'test_daemon',
                'message': 'Testing central daemon ingestion'
            }).encode()
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/api/siem/event',
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                res = json.loads(resp.read().decode())
                self.assertEqual(res['status'], 'INGESTED')

            # 3. GET /api/siem/events
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/siem/events', timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                events_data = json.loads(resp.read().decode())
                self.assertGreaterEqual(events_data['count'], 1)
        finally:
            server.shutdown()
            server.server_close()

    def test_siem_cross_source_forwarding_and_cascade_rule(self) -> None:
        """Verifica que el daemon central SIEM reciba eventos de honeypot y proxy, gatillando la Regla 1."""
        import os
        from network.siem_pipeline import SiemCorrelationEngine, SiemRequestHandler, ThreadedSiemServer
        import threading
        import time

        central_engine = SiemCorrelationEngine()
        SiemRequestHandler.engine = central_engine
        server = ThreadedSiemServer(('127.0.0.1', 0), SiemRequestHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        old_url = os.environ.get('SIEM_HTTP_URL')
        os.environ['SIEM_HTTP_URL'] = f'http://127.0.0.1:{port}'

        try:
            # 1. Honeypot touch from attacker 10.0.1.99
            local_honeypot_siem = SiemCorrelationEngine()
            local_honeypot_siem.ingest_raw_event(
                event_category='honeypot',
                event_type='alert',
                severity='HIGH',
                source_ip='10.0.1.99',
                destination_ip='10.0.5.99',
                service_name='ot_honeypot_s5',
                message='Honeypot hit from attacker'
            )

            # 2. Modbus proxy DPI block from same attacker 10.0.1.99
            local_proxy_siem = SiemCorrelationEngine()
            local_proxy_siem.ingest_raw_event(
                event_category='process_control',
                event_type='denial',
                severity='CRITICAL',
                source_ip='10.0.1.99',
                destination_ip='10.0.3.10',
                service_name='modbus_proxy',
                message='Unauthorized Modbus write attempt blocked'
            )

            time.sleep(0.3)

            # Central SIEM should have correlated both events into Rule 1 Critical Cascade Alert
            self.assertGreaterEqual(len(central_engine.active_alerts), 1)
            cascade_alert = [a for a in central_engine.active_alerts if a['attacker_ip'] == '10.0.1.99']
            self.assertEqual(len(cascade_alert), 1)
            self.assertEqual(cascade_alert[0]['severity'], 'CRITICAL')
            self.assertIn('Cascada', cascade_alert[0]['name'])
        finally:
            server.shutdown()
            server.server_close()
            if old_url is None:
                os.environ.pop('SIEM_HTTP_URL', None)
            else:
                os.environ['SIEM_HTTP_URL'] = old_url


if __name__ == '__main__':
    unittest.main()
