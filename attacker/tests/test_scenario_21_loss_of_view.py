#!/usr/bin/env python3
"""attacker/tests/test_scenario_21_loss_of_view.py — Test para Escenario 21"""
from __future__ import annotations

import unittest


from unittest.mock import MagicMock, patch
from network.scada_server import LOSS_OF_VIEW_THRESHOLD, scada_state, poll_plcs_once, _consecutive_failures
from network.hmi_server import IndustrialHmiEngine


class TestScenario21LossOfView(unittest.TestCase):

    @patch('network.sdn_controller.apply_circuit_breaker')
    @patch('network.scada_server.ModbusTcpClient')
    def test_loss_of_view_behavioral_polling_accumulation(self, mock_modbus_client: MagicMock, mock_sdn: MagicMock) -> None:
        """Ejercita la lógica de producción poll_plcs_once() y verifica la transición real a LOSS_OF_VIEW."""
        mock_instance = MagicMock()
        mock_instance.connect.return_value = False
        mock_modbus_client.return_value = mock_instance

        for sector in _consecutive_failures:
            _consecutive_failures[sector] = 0

        # Ronda 1 y 2 (PLCs inalcanzables -> UNREACHABLE)
        poll_plcs_once()
        self.assertEqual(_consecutive_failures['water'], 1)
        self.assertEqual(scada_state['sectors']['water']['status'], 'UNREACHABLE')

        poll_plcs_once()
        self.assertEqual(_consecutive_failures['water'], 2)

        # Ronda 3 -> cruza LOSS_OF_VIEW_THRESHOLD (3)
        poll_plcs_once()
        self.assertGreaterEqual(_consecutive_failures['water'], LOSS_OF_VIEW_THRESHOLD)
        self.assertEqual(scada_state['sectors']['water']['status'], 'LOSS_OF_VIEW')

        # Control F-06: Verificación de vulnerabilidad F-06 (no hay auto-aislamiento ni mitigación automática)
        # 1. No se ejecuta regla SDN Circuit Breaker
        mock_sdn.assert_not_called()
        # 2. No se envían comandos Modbus de corte/escritura a las bobinas del PLC
        mock_instance.write_coils.assert_not_called()
        mock_instance.write_registers.assert_not_called()

    def test_hmi_detects_loss_of_view_alarm(self) -> None:
        """Verifica que el motor HMI registre alarma de LOSS_OF_VIEW y cambie a ALARM_CRITICAL."""
        hmi = IndustrialHmiEngine()
        hmi.fetch_scada_status = MagicMock(return_value={
            'status': 'ONLINE',
            'sectors': {
                'water': {'status': 'ONLINE', 'consecutive_failures': 0},
                'elec': {'status': 'LOSS_OF_VIEW', 'consecutive_failures': 3}
            }
        })

        overview = hmi.get_overview()
        self.assertEqual(overview['system_health'], 'ALARM_CRITICAL')
        self.assertGreaterEqual(overview['active_alarms_count'], 1)
        self.assertEqual(overview['alarms'][0]['sector'], 'elec')
        self.assertIn('Loss-of-View', overview['alarms'][0]['message'])


if __name__ == '__main__':
    unittest.main()
