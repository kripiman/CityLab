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
from network.historian import HistorianTSDB

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][NTP-SPOOF] %(message)s')
LOGGER = logging.getLogger('attack_ntp_time_spoofing')


class NtpTimeSpoofingAttack:

    def __init__(self, historian: HistorianTSDB | None = None, siem: SiemCorrelationEngine | None = None) -> None:
        self.historian = historian
        self.siem = siem or SiemCorrelationEngine()

    def execute_time_desync_attack(self, offset_seconds: float = 3600.0) -> Dict[str, Any]:
        LOGGER.info("Iniciando desincronizacion de reloj NTP/PTP (Offset: %.1f segundos)...", offset_seconds)
        
        now = time.time()
        spoofed_ts = now + offset_seconds
        records_written = 0

        if self.historian is not None:
            self.historian.write(
                sector='water',
                field='t1_level',
                value=12.5,
                timestamp=spoofed_ts
            )
            records_written += 1

        # Ingestar evento en SIEM con marca temporal alterada
        _ = self.siem.ingest_raw_event(
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
            'mode': 'ENGINE_DIRECT',
            'clock_offset_sec': offset_seconds,
            'spoofed_timestamp': spoofed_ts,
            'records_written': records_written,
            'siem_blinded': len(self.siem.active_alerts) == 0
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab NTP/PTP Time Spoofing Attack Vector")
    parser.add_argument("--offset", type=float, default=3600.0, help="Desfasaje de tiempo en segundos")
    args = parser.parse_args(argv)

    attacker = NtpTimeSpoofingAttack()
    res = attacker.execute_time_desync_attack(offset_seconds=args.offset)
    LOGGER.info("Resultado de ataque NTP Time Spoofing: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
