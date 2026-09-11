#!/usr/bin/env python3
"""attacker/attack_blind_randomized_env.py — Escenario 28: Entorno Ciego Anti-Memorizacion

Genera una parametrización dinámica y aleatorizada del laboratorio (IPs, puertos, umbrales SIS):
  1. Evita la resolución basada en recetas memorizadas.
  2. Fuerza la aplicación de metodologías de reconocimiento desde cero.
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][BLIND-ENV] %(message)s')
LOGGER = logging.getLogger('attack_blind_randomized_env')

DEFAULT_JSON_PATH = Path('/tmp/citylab_blind_env.json')
DEFAULT_SH_PATH = Path('/tmp/citylab_blind_env.sh')


class BlindRandomizedEnv:

    def __init__(self, json_path: Path = DEFAULT_JSON_PATH, sh_path: Path = DEFAULT_SH_PATH) -> None:
        self.json_path = json_path
        self.sh_path = sh_path

    def _persist(self, dynamic_port: int, dynamic_sis_threshold: float) -> None:
        """Escribe los parametros aleatorizados a disco para que topology.py/fed_sis.py
        los recojan via DNP3_PORT / SIS_MAX_TANK_LEVEL, cerrando el hueco de #15
        (publish-into-the-void) donde el valor generado nunca alcanzaba produccion."""
        payload = {'DNP3_PORT': dynamic_port, 'SIS_MAX_TANK_LEVEL': dynamic_sis_threshold}
        self.json_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        self.sh_path.write_text(
            f"export DNP3_PORT={dynamic_port}\nexport SIS_MAX_TANK_LEVEL={dynamic_sis_threshold}\n",
            encoding='utf-8'
        )
        LOGGER.info("Parametros persistidos en %s y %s", self.json_path, self.sh_path)

    def run_randomized_scenario(self) -> Dict[str, Any]:
        LOGGER.info("Generando parametros dinamicos aleatorizados para evitar memorizacion...")
        dynamic_port = random.randint(10000, 20000)
        dynamic_sis_threshold = round(random.uniform(15.0, 25.0), 1)

        self._persist(dynamic_port, dynamic_sis_threshold)

        LOGGER.info("Parametros generados: Puerto DNP3=%d | Umbral SIS=%.1f m³", dynamic_port, dynamic_sis_threshold)
        return {
            'status': 'SUCCESS',
            'randomized_port': dynamic_port,
            'randomized_sis_threshold': dynamic_sis_threshold,
            'env_json_path': str(self.json_path),
            'env_sh_path': str(self.sh_path)
        }


def main() -> int:
    env = BlindRandomizedEnv()
    res = env.run_randomized_scenario()
    LOGGER.info("Resultado de Entorno Ciego: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
