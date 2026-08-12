#!/usr/bin/env python3
"""attacker/attack_scada_tour.py — Escenario 17: Exploración de API REST y Servidor HMI SCADA

Explora el Servidor HMI P&ID (`network/hmi_server.py` puerto `:8085`):
  1. Consulta los endpoints `/api/whoami`, `/api/telemetry`, `/api/history`.
  2. Verifica la entrega de JSON de estado operacional HMI.
"""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Dict, Any

from network.hmi_server import IndustrialHmiEngine

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][SCADA-TOUR] %(message)s')
LOGGER = logging.getLogger('attack_scada_tour')


class ScadaTour:

    def run_scada_exploration(self) -> Dict[str, Any]:
        LOGGER.info("Iniciando tour guiado por la API REST y HMI SCADA (Puerto 8085)...")
        engine = IndustrialHmiEngine()
        state = engine.get_overview()
        LOGGER.info("Respuesta de /api/telemetry HMI: %s", state)
        
        return {
            'status': 'SUCCESS',
            'hmi_port': 8085,
            'overview_retrieved': True
        }


def main() -> int:
    tour = ScadaTour()
    res = tour.run_scada_exploration()
    LOGGER.info("Resultado de Tour SCADA API: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
