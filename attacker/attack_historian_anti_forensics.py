from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.historian import HistorianTSDB

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][ANTI-FORENSICS] %(message)s')
LOGGER = logging.getLogger('attack_historian_anti_forensics')


class HistorianAntiForensicsAttack:

    def __init__(self, db_path: str = '/tmp/citylab_historian.db', historian: HistorianTSDB | None = None) -> None:
        self.historian = historian or HistorianTSDB(db_path)

    def execute_log_tampering(self) -> Dict[str, Any]:
        LOGGER.info("Iniciando manipulacion anti-forense sobre Historian TSDB...")
        
        # 1. Escribir evidencia previa
        self.historian.write('water', 't1_level', 19.5)
        count_before = len(self.historian.query(sector='water'))
        
        # 2. Purgar registros (Anti-forensics wiping)
        deleted_count = self.historian.prune(keep_records=0)
        count_after = len(self.historian.query(sector='water'))
        
        LOGGER.info("Registros previos: %d | Registros purgados: %d | Registros restantes: %d",
                    count_before, deleted_count, count_after)

        return {
            'status': 'SUCCESS',
            'mode': 'ENGINE_DIRECT',
            'records_wiped': deleted_count,
            'historian_cleared': count_after == 0
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Historian Anti-Forensics Attack Vector")
    parser.add_argument("--db-path", default="/tmp/citylab_historian.db", help="Ruta de la DB SQLite del Historian")
    args = parser.parse_args(argv)

    attacker = HistorianAntiForensicsAttack(db_path=args.db_path)
    res = attacker.execute_log_tampering()
    LOGGER.info("Resultado de ataque Anti-Forensics Historian: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
