#!/usr/bin/env python3
"""attacker/tests/test_scenario_27_red_blue.py — Test para Escenario 27"""
from __future__ import annotations

import unittest
from attacker.attack_red_vs_blue_match import RedVsBlueMatch


class TestScenario27RedBlue(unittest.TestCase):

    def test_red_blue_match_execution(self) -> None:
        rvb = RedVsBlueMatch()
        res = rvb.run_adjudicated_match()
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertTrue(res['match_completed'])
        self.assertIn('scoreboard', res)

    def test_red_team_offensive_scoring(self) -> None:
        """Verifica que el Red Team puntúa por exploits y disrupciones, no por detección."""
        events = [
            # Intrusión y exploit malicioso
            {
                "timestamp": "2026-09-11T12:00:00Z",
                "event_category": "exploit",
                "event_type": "malicious_write",
                "message": "Unauthorized register overwrite",
                "service_name": "modbus_plc"
            },
            # Disrupción física de servicio (trip)
            {
                "timestamp": "2026-09-11T12:00:10Z",
                "event_category": "attack",
                "event_type": "system_trip",
                "message": "Substation breaker trip command executed",
                "service_name": "scada_server"
            },
            # Alerta Blue Team
            {
                "timestamp": "2026-09-11T12:00:15Z",
                "event_category": "alert",
                "event_type": "alert",
                "message": "Correlated alert: anomalous breaker state",
                "service_name": "siem_pipeline"
            }
        ]
        rvb = RedVsBlueMatch()
        res = rvb.run_adjudicated_match(events=events)
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'SIEM_LIVE')

        soc = res['soc_metrics']
        self.assertEqual(soc['successful_exploits'], 2)  # malicious_write + system_trip
        self.assertEqual(soc['services_disrupted'], 1)   # system_trip
        # 1 ataque categorizado en SIEM, 0 defensas -> 1 ataque no mitigado
        self.assertEqual(soc['unmitigated_attacks'], 1)

        scoreboard = res['scoreboard']
        # red_pts = (2 * 100) + (1 * 100) + (1 * 50) = 350
        self.assertEqual(scoreboard['red_team_points'], 350)
        # blue_pts = 2 alerts (alerta + trip) * 50 = 100
        self.assertEqual(scoreboard['blue_team_points'], 100)
        self.assertIn('Red Team', scoreboard['winner'])

    def test_red_team_not_rewarded_when_fully_mitigated(self) -> None:
        """Si la defensa detecta y mitiga todos los escaneos/ataques sin exploits, Red Team no suma puntos."""
        events = [
            # Escaneo detectado
            {
                "timestamp": "2026-09-11T12:00:00Z",
                "event_category": "honeypot",
                "event_type": "honeypot",
                "message": "Port probe detected on honeypot",
                "service_name": "honeypot_server"
            },
            # Alerta SOC
            {
                "timestamp": "2026-09-11T12:00:05Z",
                "event_category": "alert",
                "event_type": "alert",
                "message": "correlated alert probe",
                "service_name": "siem_pipeline"
            },
            # Mitigación SDN inmediata
            {
                "timestamp": "2026-09-11T12:00:20Z",
                "event_category": "defense",
                "event_type": "isolation",
                "message": "Attacker IP isolated by SDN controller",
                "service_name": "sdn_controller"
            }
        ]
        rvb = RedVsBlueMatch()
        res = rvb.run_adjudicated_match(events=events)
        self.assertEqual(res['mode'], 'SIEM_LIVE')

        soc = res['soc_metrics']
        self.assertEqual(soc['successful_exploits'], 0)
        self.assertEqual(soc['services_disrupted'], 0)
        self.assertEqual(soc['unmitigated_attacks'], 0)

        scoreboard = res['scoreboard']
        # El Red Team NO recibe puntos por ser detectado
        self.assertEqual(scoreboard['red_team_points'], 0)
        # Blue Team recibe: 1 alerta * 50 + 1 mitigación * 150 + bono MTTR (15s < 120s) 200 = 400
        self.assertEqual(scoreboard['blue_team_points'], 400)
        self.assertIn('Blue Team', scoreboard['winner'])

    def test_red_team_evasion_fallback_scoring(self) -> None:
        """Verifica que si no hay exploits específicos pero hay ataques no mitigados, puntúa por evasión."""
        events = [
            {
                "timestamp": "2026-09-11T12:00:00Z",
                "event_category": "attack",
                "event_type": "recon",
                "message": "Port scan against substation network",
                "service_name": "scanner"
            },
            {
                "timestamp": "2026-09-11T12:00:05Z",
                "event_category": "attack",
                "event_type": "spoof",
                "message": "Arp spoofing attempt detected",
                "service_name": "network"
            }
        ]
        rvb = RedVsBlueMatch()
        res = rvb.run_adjudicated_match(events=events)
        self.assertEqual(res['mode'], 'SIEM_LIVE')

        soc = res['soc_metrics']
        self.assertEqual(soc['successful_exploits'], 0)
        self.assertEqual(soc['services_disrupted'], 0)
        self.assertEqual(soc['unmitigated_attacks'], 2)

        scoreboard = res['scoreboard']
        # 2 ataques no mitigados * 100 = 200
        self.assertEqual(scoreboard['red_team_points'], 200)
        self.assertEqual(scoreboard['blue_team_points'], 0)
        self.assertIn('Red Team', scoreboard['winner'])


if __name__ == '__main__':
    unittest.main()
