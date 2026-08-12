#!/usr/bin/env python3
"""attacker/attack_stuxnet_replay.py — Vector de Ataque Telemetry Replay (Stuxnet Pattern)

Inspirado en el ataque Stuxnet (2010).
Graba lecturas normales de la planta industrial y las reproduce continuamente
hacia la interfaz HMI y el Historian TSDB, mientras en segundo plano se manipula
el proceso físico real provocando daños en la infraestructura.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import Dict, List, Any

from network.historian import HistorianTSDB
from physical.water.plant_water import TwoStageWaterPlant

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][STUXNET-REPLAY] %(message)s')
LOGGER = logging.getLogger('attack_stuxnet_replay')


class StuxnetReplayAttack:

    def __init__(self) -> None:
        self.recorded_telemetry: List[Dict[str, Any]] = []

    def record_normal_baseline(self, samples: int = 5) -> None:
        LOGGER.info("Grabando baseline de telemetría normal (%d muestras)...", samples)
        plant = TwoStageWaterPlant()
        for i in range(samples):
            t1, t2 = plant.step(p1_cmd=True, p2_cmd=True, dt=0.5)
            self.recorded_telemetry.append({'water_t1': t1, 'water_t2': t2, 'status': 'NORMAL'})
        LOGGER.info("Baseline grabado exitosamente.")

    def execute_replay_and_sabotage(self, historian: HistorianTSDB, sabotage_duration: int = 3) -> Dict[str, Any]:
        LOGGER.info("Iniciando ataque Replay: Inyectando baseline grabado mientras se sabotea el proceso real...")
        
        # 1. Sabotaje real del proceso (vaciar o sobrecargar)
        plant = TwoStageWaterPlant()
        plant.t1_level_m3 = 0.1  # Nivel seco crítico real
        
        replay_count = 0
        for i in range(sabotage_duration):
            sample = self.recorded_telemetry[i % len(self.recorded_telemetry)]
            # Replay al Historian de valores normales grabados
            historian.write_snapshot('water', sample)
            replay_count += 1
            LOGGER.info(
                "Ciclo %d — Proceso Real T1: %.1f m³ (CRÍTICO) | Telemetría Replay enviada a HMI: %.1f m³ (NORMAL)",
                i+1, plant.t1_level_m3, sample['water_t1']
            )
            time.sleep(0.05)

        return {'status': 'SUCCESS', 'replayed_samples': replay_count, 'real_process_sabotaged': True}


def main() -> int:
    parser = argparse.ArgumentParser(description="CityLab Stuxnet Telemetry Replay Attack Vector")
    parser.add_argument("--duration", type=int, default=5, help="Duración del ataque replay en ciclos")
    args = parser.parse_args()

    historian = HistorianTSDB('/tmp/stuxnet_test_historian.db')
    attacker = StuxnetReplayAttack()
    attacker.record_normal_baseline(samples=5)
    res = attacker.execute_replay_and_sabotage(historian, sabotage_duration=args.duration)
    LOGGER.info("Resultado de ataque Stuxnet: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
