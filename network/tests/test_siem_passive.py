#!/usr/bin/env python3
"""network/tests/test_siem_passive.py — Unit tests for Zeek and Suricata passive inspection bridge (Fase 2)"""

import unittest
from network.siem_pipeline import SiemCorrelationEngine


class TestSiemPassiveBridge(unittest.TestCase):
    def setUp(self) -> None:
        self.siem = SiemCorrelationEngine()

    def test_zeek_log_ingestion(self) -> None:
        zeek_notice = {
            'id.orig_h': '10.0.1.10',
            'id.resp_h': '10.0.3.10',
            'proto': 'tcp',
            'note': 'Modbus::Unauthorized_Write_Attempt',
            'msg': 'Modbus write coil attempt to water PLC'
        }
        event = self.siem.ingest_zeek_log(zeek_notice)
        self.assertEqual(event.source_ip, '10.0.1.10')
        self.assertEqual(event.destination_ip, '10.0.3.10')
        self.assertEqual(event.severity, 'HIGH')
        self.assertIn('zeek_tcp', event.service_name)
        self.assertTrue(len(self.siem.active_alerts) > 0)

    def test_suricata_eve_ingestion(self) -> None:
        eve_alert = {
            'event_type': 'alert',
            'src_ip': '10.0.1.10',
            'dest_ip': '10.0.3.13',
            'alert': {
                'signature': 'ET PRO MALWARE DNP3 Unauthorized Read Command',
                'severity': 1
            }
        }
        event = self.siem.ingest_suricata_eve(eve_alert)
        self.assertEqual(event.source_ip, '10.0.1.10')
        self.assertEqual(event.destination_ip, '10.0.3.13')
        self.assertEqual(event.severity, 'CRITICAL')
        self.assertEqual(event.service_name, 'suricata_eve')
        self.assertTrue(len(self.siem.active_alerts) > 0)


if __name__ == '__main__':
    unittest.main()
