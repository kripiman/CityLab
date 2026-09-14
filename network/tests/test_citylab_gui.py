#!/usr/bin/env python3
"""network/tests/test_citylab_gui.py — Pruebas unitarias para CityLab Native Desktop Dashboard."""
from __future__ import annotations

import threading
import unittest
from typing import Any, Dict

from network.citylab_gui import (
    HmiClient,
    VizClient,
    derive_hmi_view_state,
    derive_viz_view_state,
)
from network.hmi_server import HmiRequestHandler, ThreadedHmiServer
from network.viz_server import ThreadedVizServer, VizRequestHandler


class TestCityLabGuiClients(unittest.TestCase):
    """Pruebas de transporte HTTP para HmiClient y VizClient contra servidores reales."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.hmi_server = ThreadedHmiServer(('127.0.0.1', 0), HmiRequestHandler)
        cls.hmi_port = cls.hmi_server.server_address[1]
        cls.hmi_thread = threading.Thread(target=cls.hmi_server.serve_forever, daemon=True)
        cls.hmi_thread.start()

        cls.viz_server = ThreadedVizServer(('127.0.0.1', 0), VizRequestHandler)
        cls.viz_port = cls.viz_server.server_address[1]
        cls.viz_thread = threading.Thread(target=cls.viz_server.serve_forever, daemon=True)
        cls.viz_thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.hmi_server.shutdown()
        cls.hmi_server.server_close()
        cls.viz_server.shutdown()
        cls.viz_server.server_close()

    def test_hmi_client_get_overview(self) -> None:
        client = HmiClient(f"http://127.0.0.1:{self.hmi_port}")
        overview = client.get_overview()
        self.assertIsInstance(overview, dict)
        self.assertIn('process_diagram', overview)
        self.assertIn('alarms', overview)

    def test_hmi_client_send_control(self) -> None:
        client = HmiClient(f"http://127.0.0.1:{self.hmi_port}")
        res = client.send_control(action='START', target='water')
        self.assertIsInstance(res, dict)
        self.assertIn('success', res)

    def test_viz_client_get_frame(self) -> None:
        client = VizClient(f"http://127.0.0.1:{self.viz_port}")
        frame = client.get_frame()
        self.assertIsInstance(frame, dict)
        self.assertIn('city_sectors', frame)
        self.assertIn('soc_alerts', frame)
        self.assertIn('sdn_mitigations', frame)

    def test_clients_offline_resilience(self) -> None:
        # Clientes apuntando a puertos inalcanzables deben retornar defaults seguros sin lanzar excepciones
        offline_hmi = HmiClient("http://127.0.0.1:1")
        hmi_data = offline_hmi.get_overview()
        self.assertFalse(hmi_data.get('scada_connected'))
        self.assertEqual(hmi_data.get('system_health'), 'ALARM_CRITICAL')

        ctrl_res = offline_hmi.send_control('START', 'water')
        self.assertFalse(ctrl_res.get('success'))

        offline_viz = VizClient("http://127.0.0.1:1")
        viz_data = offline_viz.get_frame()
        self.assertTrue(viz_data.get('offline'))
        self.assertEqual(viz_data.get('city_sectors'), {})


class TestCityLabGuiDerivations(unittest.TestCase):
    """Pruebas unitarias de las funciones puras de derivación de estado de vista."""

    def test_derive_hmi_view_state_normal(self) -> None:
        fixture: Dict[str, Any] = {
            'scada_connected': True,
            'system_health': 'NORMAL',
            'process_diagram': {
                'water_sector': {'t1_level': 12.5, 't2_level': 18.0, 'p1_state': True, 'status': 'ONLINE'},
                'gas_sector': {'pressure_psi': 140.0, 'valve_open': True, 'status': 'ONLINE'},
                'elec_sector': {'grid_voltage': 228.0, 'breaker_closed': True, 'status': 'ONLINE'},
                'transport_sector': {'traffic_light': 2, 'gate_open': True, 'status': 'ONLINE'},
            },
            'alarms': []
        }
        view = derive_hmi_view_state(fixture)
        self.assertTrue(view['scada_connected'])
        self.assertEqual(view['scada_badge'][0], 'SCADA ONLINE')
        self.assertEqual(view['health_badge'][0], 'NORMAL')

        w = view['sectors']['water']
        self.assertEqual(w['badge'][0], 'OK')
        self.assertEqual(w['t1_level'], 12.5)
        self.assertTrue(w['pump_running'])

        g = view['sectors']['gas']
        self.assertEqual(g['badge'][0], 'OK')
        self.assertEqual(g['pressure_psi'], 140.0)
        self.assertTrue(g['valve_open'])

        e = view['sectors']['elec']
        self.assertEqual(e['badge'][0], 'OK')
        self.assertTrue(e['breaker_closed'])

        t = view['sectors']['transport']
        self.assertEqual(t['badge'][0], 'OK')
        self.assertEqual(t['traffic_light'], 'VERDE')
        self.assertTrue(t['gate_open'])
        self.assertEqual(view['alarms_count'], 0)

    def test_derive_hmi_view_state_critical_and_lov(self) -> None:
        fixture: Dict[str, Any] = {
            'scada_connected': False,
            'system_health': 'ALARM_CRITICAL',
            'process_diagram': {
                'water_sector': {'status': 'LOSS_OF_VIEW', 'p1_state': False},
                'gas_sector': {'status': 'ONLINE', 'pressure_psi': 195.0, 'valve_open': False},
                'elec_sector': {'status': 'ONLINE', 'breaker_closed': False},
                'transport_sector': {'status': 'LOSS_OF_VIEW', 'traffic_light': 0, 'gate_open': False},
            },
            'alarms': [{'alarm_id': 'ALM-01', 'sector': 'water', 'severity': 'CRITICAL', 'message': 'Loss of View'}]
        }
        view = derive_hmi_view_state(fixture)
        self.assertFalse(view['scada_connected'])
        self.assertEqual(view['scada_badge'][0], 'SCADA OFFLINE')
        self.assertEqual(view['health_badge'][0], 'ALARMA CRÍTICA')

        self.assertEqual(view['sectors']['water']['badge'][0], 'LOSS OF VIEW')
        self.assertEqual(view['sectors']['gas']['badge'][0], 'ALTA PRESIÓN')
        self.assertEqual(view['sectors']['elec']['badge'][0], 'TRIPPED')
        self.assertEqual(view['sectors']['transport']['badge'][0], 'LOSS OF VIEW')
        self.assertEqual(view['sectors']['transport']['traffic_light'], 'ROJO')
        self.assertEqual(view['alarms_count'], 1)

    def test_derive_viz_view_state_normal(self) -> None:
        fixture: Dict[str, Any] = {
            'city_sectors': {
                'water': {'alert': False, 'pump_running': True, 'tank_level': 14.0},
                'gas': {'alert': False, 'pressure_psi': 142.0, 'valve_open': True},
                'elec': {'blackout': False, 'grid_voltage': 230.0},
                'transport': {'traffic_light': 'GREEN', 'railway_gate': 'ABIERTA', 'congestion_pct': 25.0},
                'hospital': {'generator_active': False, 'standalone_decoupled': False, 'load_kw': 820.0},
                'desal': {'pump_trip': False, 'standalone_decoupled': False, 'tank_level_pct': 80.0, 'power_kw': 45.0},
                'lighting': {'blackout': False, 'standalone_decoupled': False, 'power_kw': 120.0},
                'safety': {'sis_trip': False, 'standalone_decoupled': False},
            },
            'soc_alerts': [],
            'sdn_mitigations': []
        }
        view = derive_viz_view_state(fixture)
        self.assertFalse(view['critical'])
        self.assertEqual(view['system_badge'][0], 'SISTEMA NORMAL')
        self.assertEqual(view['sis_badge'][0], 'SIS SIL-3: OK')
        self.assertEqual(view['sectors']['water']['badge'][0], 'OK')
        self.assertTrue(view['sectors']['water']['pump_running'])
        self.assertEqual(view['sectors']['water']['tank_level'], 14.0)
        self.assertEqual(view['sectors']['hospital']['badge'][0], 'OK')
        self.assertEqual(view['sectors']['desal']['badge'][0], 'OK')
        self.assertEqual(view['sectors']['lighting']['badge'][0], 'OK')
        self.assertEqual(view['sectors']['safety']['badge'][0], 'ARMED')

    def test_derive_viz_view_state_cascade_and_blue_team(self) -> None:
        fixture: Dict[str, Any] = {
            'city_sectors': {
                'water': {'alert': True, 'pump_running': False, 'tank_level': 10.0},
                'gas': {'alert': True, 'pressure_psi': 190.0, 'valve_open': True},
                'elec': {'blackout': True, 'grid_voltage': 0.0},
                'transport': {'traffic_light': 'RED', 'railway_gate': 'CERRADA', 'congestion_pct': 88.0},
                'hospital': {'generator_active': True, 'load_kw': 750.0},
                'desal': {'pump_trip': True, 'tank_level_pct': 70.0, 'power_kw': 0.0},
                'lighting': {'blackout': True, 'power_kw': 0.0},
                'safety': {'sis_trip': True},
            },
            'soc_alerts': [
                {'alert_id': 'SOC-001', 'name': 'Modbus Injection Attack', 'attacker_ip': '10.0.1.50'}
            ],
            'sdn_mitigations': [
                {'mechanism': 'OpenFlow Circuit Breaker', 'offending_ip': '10.0.1.50', 'switch': 's2', 'rule': 'Drop Flow'}
            ]
        }
        view = derive_viz_view_state(fixture)
        self.assertTrue(view['critical'])
        self.assertIn('SOC: Modbus Injection Attack', view['system_badge'][0])
        self.assertEqual(view['sis_badge'][0], 'SIS: TRIP')
        self.assertEqual(view['sectors']['water']['badge'][0], 'TRIP')
        self.assertFalse(view['sectors']['water']['pump_running'])
        self.assertEqual(view['sectors']['gas']['badge'][0], 'ALERTA')
        self.assertEqual(view['sectors']['elec']['badge'][0], 'APAGÓN')
        self.assertEqual(view['sectors']['hospital']['badge'][0], 'ON UPS')
        self.assertEqual(view['sectors']['desal']['badge'][0], 'TRIP')
        self.assertEqual(view['sectors']['lighting']['badge'][0], 'APAGÓN')
        self.assertEqual(view['sectors']['safety']['badge'][0], 'TRIPPED')
        self.assertEqual(len(view['soc_alerts']), 1)
        self.assertEqual(len(view['sdn_mitigations']), 1)

    def test_derive_viz_view_state_standalone_decoupled(self) -> None:
        fixture: Dict[str, Any] = {
            'city_sectors': {
                'hospital': {'generator_active': False, 'standalone_decoupled': True},
                'desal': {'pump_trip': False, 'standalone_decoupled': True},
                'lighting': {'blackout': False, 'power_kw': 120.0, 'standalone_decoupled': True},
                'safety': {'sis_trip': False, 'standalone_decoupled': True},
            }
        }
        view = derive_viz_view_state(fixture)
        self.assertEqual(view['sectors']['hospital']['badge'][0], 'OK (STANDALONE)')
        self.assertEqual(view['sectors']['desal']['badge'][0], 'OK (STANDALONE)')
        self.assertEqual(view['sectors']['lighting']['badge'][0], 'OK (STANDALONE)')
        self.assertEqual(view['sectors']['safety']['badge'][0], 'ARMED (STANDALONE)')


if __name__ == '__main__':
    unittest.main()
