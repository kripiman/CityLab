#!/usr/bin/env python3
"""attacker/tests/test_attack_failover.py — Tests para ataque DCS Failover Exploitation"""
from __future__ import annotations

import unittest
from attacker.attack_dcs_failover import FailoverExploitAttack, main as failover_main
from network.scada_ha import SCADAPrimarySecondaryCluster


class TestFailoverAttack(unittest.TestCase):

    def test_dcs_failover_attack_execution_triggers_primary(self) -> None:
        """Verifica que la ausencia de heartbeat fuerce la conmutación a PRIMARY."""
        cluster = SCADAPrimarySecondaryCluster(
            node_role='STANDBY',
            peer_url='http://127.0.0.1:59999',
            heartbeat_timeout=0.08,
            heartbeat_interval=0.03
        )
        attacker = FailoverExploitAttack(cluster=cluster)
        res = attacker.execute_failover_race_attack()

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'ENGINE_DIRECT')
        self.assertTrue(res['exploited_window'])
        self.assertEqual(res['active_role'], 'ACTIVE_STANDBY')

    def test_dcs_failover_cli(self) -> None:
        """Verifica ejecución CLI."""
        rc = failover_main([])
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
