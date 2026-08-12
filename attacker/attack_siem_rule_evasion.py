#!/usr/bin/env python3
"""attacker/attack_siem_rule_evasion.py — Escenario 24: Evasion de Reglas SIEM Multi-IP

Diseña una inyección distribuida multi-IP para evitar la regla de correlación fija del SIEM (`network/siem_pipeline.py`):
  1. Divide los escaneos y comandos Modbus entre múltiples direcciones origen.
  2. Logra la manipulación del proceso evitando el umbral de disparo por firma.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.siem_pipeline import SiemCorrelationEngine

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][SIEM-EVASION] %(message)s')
LOGGER = logging.getLogger('attack_siem_rule_evasion')


class SiemRuleEvasion:

    def __init__(self) -> None:
        self.siem = SiemCorrelationEngine()

    def run_multi_ip_evasion(self) -> Dict[str, Any]:
        LOGGER.info("Iniciando ataque distribuido multi-IP para evadir reglas fijas del SIEM...")
        ips = ['10.0.5.101', '10.0.5.102', '10.0.5.103']
        
        for ip in ips:
            self.siem.ingest_raw_event(
                event_category='process_control',
                event_type='alert',
                severity='LOW',
                source_ip=ip,
                destination_ip='10.0.3.10',
                service_name='modbus_dpi',
                message='Peticion aislada Modbus'
            )
            
        alerts_triggered = len(self.siem.active_alerts)
        LOGGER.info("Alertas criticas correlacionadas en SIEM: %d", alerts_triggered)
        return {
            'status': 'SUCCESS',
            'evasion_successful': alerts_triggered == 0
        }


def main() -> int:
    evasion = SiemRuleEvasion()
    res = evasion.run_multi_ip_evasion()
    LOGGER.info("Resultado de Evasion SIEM: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
