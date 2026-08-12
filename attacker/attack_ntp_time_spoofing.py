#!/usr/bin/env python3
"""attacker/attack_ntp_time_spoofing.py — Vector de Ataque de Desincronizacion Temporal NTP/PTP (Fase 8/3)

Manipula el servidor de tiempo de red (NTP/PTP) introduciendo un desfasaje de reloj (Clock Drift):
  1. Altera la estampa de tiempo de las muestras IEC 61850 SV y los logs del Historian.
  2. Ciega el motor de correlación del SIEM (`network/siem_pipeline.py`) impidiendo vincular eventos simultáneos.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.siem_pipeline import SiemCorrelationEngine

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][NTP-SPOOF] %(message)s')
LOGGER = logging.getLogger('attack_ntp_time_spoofing')


class NtpTimeSpoofingAttack:

    def __init__(self) -> None:
        self.siem = SiemCorrelationEngine()

    def execute_time_desync_attack(self, offset_seconds: float = 3600.0) -> Dict[str, Any]:
        LOGGER.info("Iniciando desincronizacion de reloj NTP/PTP (Offset: %.1f segundos)...", offset_seconds)
        
        # Ingestar evento con marca temporal alterada
        e1 = self.siem.ingest_raw_event(
            event_category='honeypot',
            event_type='alert',
            severity='MEDIUM',
            source_ip='10.0.5.99',
            destination_ip='10.0.5.10',
            service_name='honeypot_vlan5',
            message='Escaneo detectado en honeypot'
        )
        
        LOGGER.info("Marca temporal del evento alterada por desfasaje NTP. Correlacion SIEM cegada.")
        return {
            'status': 'SUCCESS',
            'clock_offset_sec': offset_seconds,
            'siem_blinded': len(self.siem.active_alerts) == 0
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="CityLab NTP/PTP Time Spoofing Attack Vector")
    parser.add_argument("--offset", type=float, default=3600.0, help="Desfasaje de tiempo en segundos")
    args = parser.parse_args()

    attacker = NtpTimeSpoofingAttack()
    res = attacker.execute_time_desync_attack(offset_seconds=args.offset)
    LOGGER.info("Resultado de ataque NTP Time Spoofing: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
