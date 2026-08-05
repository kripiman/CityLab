"""Automated integration test for the PoC PLC Modbus interface.

Usage (from within Mininet host h_dmz):
  python3 plc/tests/poc_modbus_test.py --host 10.0.3.10

Tests performed:
 - Read initial coils
 - Issue START (coil 0) and expect coil 2 (pump_running) within 10s
 - Issue STOP (coil 1) and expect coil 2 cleared within 10s
 - Issue START+STOP simultaneously and expect fault coil 3 set

Requires pymodbus>=3.6
"""
from __future__ import annotations

import argparse
import time
from typing import Tuple



def read_coils(client: ModbusTcpClient, count: int = 4) -> Tuple[int, ...]:
    rr = client.read_coils(0, count)
    if not rr or rr.isError():
        raise RuntimeError('Failed to read coils')
    return tuple(int(b) for b in rr.bits)


def write_coil(client: ModbusTcpClient, addr: int, value: bool) -> None:
    rr = client.write_coil(addr, int(value))
    if rr.isError():
        raise RuntimeError(f'Failed to write coil {addr}')


def wait_for_coil(client: ModbusTcpClient, addr: int, expected: int, timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        coils = read_coils(client, addr + 1)
        if coils[addr] == expected:
            return True
        time.sleep(0.5)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='10.0.3.10', help='PLC IP address')
    parser.add_argument('--port', type=int, default=502, help='Modbus/TCP port')
    args = parser.parse_args()

    client = ModbusTcpClient(args.host, port=args.port)
    connected = client.connect()
    if not connected:
        print('[ERROR] Cannot connect to PLC Modbus server')
        return 2

    try:
        print('[*] Reading initial coils')
        coils = read_coils(client)
        print('  initial:', coils)

        print('[*] Test START -> expect pump_running (coil 2) in ~5s')
        write_coil(client, 0, True)
        ok = wait_for_coil(client, 2, 1, timeout=10.0)
        write_coil(client, 0, False)
        if not ok:
            print('[FAIL] pump did not start within timeout')
            return 3
        print('[PASS] pump started')

        print('[*] Test STOP -> expect pump_running cleared in ~3s')
        write_coil(client, 1, True)
        ok2 = wait_for_coil(client, 2, 0, timeout=10.0)
        write_coil(client, 1, False)
        if not ok2:
            print('[FAIL] pump did not stop within timeout')
            return 4
        print('[PASS] pump stopped')

        print('[*] Test FAULT -> set START and STOP simultaneously, expect coil 3')
        write_coil(client, 0, True)
        write_coil(client, 1, True)
        time.sleep(0.5)
        coils2 = read_coils(client)
        if coils2[3] != 1:
            print('[FAIL] fault coil not set')
            return 5
        print('[PASS] fault coil set')

        # Cleanup
        write_coil(client, 0, False)
        write_coil(client, 1, False)

        print('[*] All tests passed')
        return 0
    finally:
        client.close()


if __name__ == '__main__':
    raise SystemExit(main())
