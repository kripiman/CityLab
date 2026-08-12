#!/usr/bin/env python3
"""attacker/attack_honeypot_touch.py — Escenario 16: Interacción con Deception Technology (Honeypot)

Conecta voluntariamente al servicio emulado de subestación en VLAN `s5` (`10.0.5.99`):
  1. Activa una alerta de engaño (*Honeypot Trigger*).
  2. Permite al estudiante verificar la alerta en el pipeline SIEM (`network/siem_pipeline.py`).
"""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Dict, Any

from network.siem_pipeline import SiemCorrelationEngine

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][HONEYPOT-TOUCH] %(message)s')
LOGGER = logging.getLogger('attack_honeypot_touch')


class HoneypotTouch:

    def __init__(self) -> None:
        self.siem = SiemCorrelationEngine()

    def run_honeypot_interaction(self) -> Dict[str, Any]:
        LOGGER.info("Interactuando con Honeypot en VLAN s5 (10.0.5.99)...")
        evt = self.siem.ingest_raw_event(
            event_category='honeypot',
            event_type='alert',
            severity='HIGH',
            source_ip='10.0.1.10',
            destination_ip='10.0.5.99',
            service_name='substation_honeypot_s5',
            message='Conexion no autorizada detectada en trampa Honeypot'
        )
        LOGGER.info("Evento ingerido en SIEM: ID=%s | Severidad=%s", evt['event_id'], evt['severity'])
        return {
            'status': 'SUCCESS',
            'honeypot_triggered': True,
            'siem_event_id': evt['event_id']
        }


def main() -> int:
    touch = HoneypotTouch()
    res = touch.run_honeypot_interaction()
    LOGGER.info("Resultado de Interaccion Honeypot: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
