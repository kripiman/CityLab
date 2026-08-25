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

    def __init__(self, siem: SiemCorrelationEngine | None = None) -> None:
        self.siem = siem or SiemCorrelationEngine()

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
            'mode': 'ENGINE_DIRECT',
            'evasion_successful': alerts_triggered == 0,
            'alerts_triggered': alerts_triggered,
            'events_ingested': len(ips),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SIEM Multi-IP Rule Evasion Script")
    _ = parser.parse_args(argv)

    evasion = SiemRuleEvasion()
    res = evasion.run_multi_ip_evasion()
    LOGGER.info("Resultado de Evasion SIEM: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
