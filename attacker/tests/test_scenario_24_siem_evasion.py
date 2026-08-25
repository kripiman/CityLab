#!/usr/bin/env python3
"""attacker/tests/test_scenario_24_siem_evasion.py — Tests para Escenario 24: Evasión de Reglas SIEM Multi-IP"""
from __future__ import annotations

import unittest
from attacker.attack_siem_rule_evasion import SiemRuleEvasion, main as evasion_main
from network.siem_pipeline import SiemCorrelationEngine


class TestScenario24SiemEvasion(unittest.TestCase):

    def test_siem_evasion_execution_avoids_alerts(self) -> None:
        """Verifica que el ataque distribuido multi-IP evada el umbral de disparo del SIEM."""
        engine = SiemCorrelationEngine()
        evasion = SiemRuleEvasion(siem=engine)
        res = evasion.run_multi_ip_evasion()

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'ENGINE_DIRECT')
        self.assertTrue(res['evasion_successful'])
        self.assertEqual(res['alerts_triggered'], 0)
        self.assertEqual(len(engine.active_alerts), 0)

    def test_siem_single_ip_baseline_triggers_alert(self) -> None:
        """Prueba negativa / anti-trampa: ráfaga de eventos desde una sola IP sí activa alerta correlacionada."""
        engine = SiemCorrelationEngine()
        # Inyectar eventos concentrados desde la misma IP
        engine.ingest_raw_event('honeypot', 'alert', 'HIGH', '10.0.1.10', '10.0.5.99', 'substation_honeypot_s5', 'Unauthorized scan')
        engine.ingest_raw_event('process_control', 'alert', 'CRITICAL', '10.0.1.10', '10.0.3.10', 'modbus_dpi', 'OT Injection')
        
        self.assertGreaterEqual(len(engine.active_alerts), 1)

    def test_siem_evasion_cli(self) -> None:
        """Verifica la ejecución CLI."""
        rc = evasion_main([])
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
