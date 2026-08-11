#!/usr/bin/env python3
"""network/tests/test_scada_ha.py — Pruebas unitarias para Redundancia SCADA HA (Fase 6)"""
from __future__ import annotations

import time
import unittest
from network.scada_ha import SCADAPrimarySecondaryCluster


class TestSCADAHighAvailability(unittest.TestCase):

    def test_cluster_initial_state(self) -> None:
        primary = SCADAPrimarySecondaryCluster(node_role='PRIMARY')
        standby = SCADAPrimarySecondaryCluster(node_role='STANDBY')
        
        self.assertEqual(primary.node_role, 'PRIMARY')
        self.assertEqual(standby.node_role, 'STANDBY')
        self.assertFalse(standby.is_failover_active)

    def test_heartbeat_processing(self) -> None:
        primary = SCADAPrimarySecondaryCluster(node_role='PRIMARY')
        resp = primary.receive_heartbeat(sender_role='STANDBY')
        
        self.assertEqual(resp['status'], 'OK')
        self.assertEqual(resp['my_role'], 'PRIMARY')

    def test_automatic_failover_trigger(self) -> None:
        # Configurar timeout muy corto para la prueba (0.2s)
        standby = SCADAPrimarySecondaryCluster(
            node_role='STANDBY',
            peer_url='http://127.0.0.1:59999',  # Unreachable peer
            heartbeat_timeout=0.1,
            heartbeat_interval=0.05
        )
        standby.start_ha_monitor()
        time.sleep(0.5)
        
        status = standby.get_cluster_status()
        standby.stop_ha_monitor()
        
        self.assertTrue(status['failover_active'])
        self.assertEqual(status['active_role'], 'ACTIVE_STANDBY')

    def test_failback_upon_primary_recovery(self) -> None:
        standby = SCADAPrimarySecondaryCluster(node_role='STANDBY')
        standby.is_failover_active = True
        standby.active_role = 'ACTIVE_STANDBY'
        
        # Recibir heartbeat de Primario recuperado
        resp = standby.receive_heartbeat(sender_role='PRIMARY')
        self.assertFalse(standby.is_failover_active)
        self.assertEqual(standby.active_role, 'STANDBY')


if __name__ == '__main__':
    unittest.main()
