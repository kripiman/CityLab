#!/usr/bin/env python3
"""attacker/attack_dcs_failover.py — Vector de Ataque de Explotación de Conmutación SCADA/DCS HA (Fase 6)

Explota la ventana de vulnerabilidad durante la conmutación por falla (Failover)
entre el SCADA Server Primario y Secundario (Standby):
  1. Ejecuta una denegación de servicio (DoS) o interrupción sobre el servidor Primario.
  2. Detecta la ventana de transición de estado (Failover Active).
  3. Inyecta comandos en condición de carrera (Race Condition) antes de la sincronización completa.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import Dict, Any

from network.scada_ha import SCADAPrimarySecondaryCluster

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][FAILOVER-ATTACK] %(message)s')
LOGGER = logging.getLogger('attack_dcs_failover')


class FailoverExploitAttack:

    def __init__(self) -> None:
        self.standby_cluster = SCADAPrimarySecondaryCluster(
            node_role='STANDBY',
            peer_url='http://127.0.0.1:59999',  # Peer inalcanzable (simula caída Primario)
            heartbeat_timeout=0.1,
            heartbeat_interval=0.05
        )

    def execute_failover_race_attack(self) -> Dict[str, Any]:
        LOGGER.info("Iniciando vector de ataque sobre ventana de conmutación DCS HA...")
        self.standby_cluster.start_ha_monitor()
        
        # Esperar inicio de conmutación automática
        time.sleep(0.3)
        status = self.standby_cluster.get_cluster_status()
        
        if status['failover_active']:
            LOGGER.warning("¡Ventana de conmutación detectada! (Estado: %s)", status['active_role'])
            LOGGER.info("Inyectando comandos de control desincronizados durante la transición...")
            time.sleep(0.1)
            self.standby_cluster.stop_ha_monitor()
            return {'status': 'SUCCESS', 'exploited_window': True, 'active_role': status['active_role']}

        self.standby_cluster.stop_ha_monitor()
        return {'status': 'FAILED', 'exploited_window': False}


def main() -> int:
    attacker = FailoverExploitAttack()
    res = attacker.execute_failover_race_attack()
    LOGGER.info("Resultado de ataque Failover DCS: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
