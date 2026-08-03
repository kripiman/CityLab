#!/usr/bin/env python3
"""Simple Modbus/TCP emulator for PoC PLC (fallback when OpenPLC not present).
Exposes coils:
 - coil 0 -> pump_start (command)
 - coil 1 -> pump_stop
 - coil 2 -> pump_running (state, output)
 - coil 3 -> pump_fault

Behaviour mimics the ST program: start has 5s on-delay, stop has 3s on-delay.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import List

from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock

LOGGER = logging.getLogger('modbus_emulator')
logging.basicConfig(level=logging.INFO)

START_DELAY = 5.0
STOP_DELAY = 3.0
POLL_INTERVAL = 0.5


class PumpEmulator:
    def __init__(self, context: ModbusServerContext):
        self.context = context
        self._lock = threading.Lock()
        self._pending_start_ts = 0.0
        self._pending_stop_ts = 0.0
        self._pump_running = False
        self._pump_fault = False
        self._stopped = threading.Event()

    def read_coils(self, count: int = 4) -> List[int]:
        slave_id = 0x00
        vals = self.context[slave_id].getValues(1, 0, count)
        return vals

    def write_coil(self, addr: int, value: int) -> None:
        slave_id = 0x00
        self.context[slave_id].setValues(1, addr, [int(value)])

    def loop(self) -> None:
        LOGGER.info('Pump emulator loop starting')
        while not self._stopped.is_set():
            coils = self.read_coils(4)
            start_cmd = bool(coils[0])
            stop_cmd = bool(coils[1])

            # Fault: start and stop simultaneously
            self._pump_fault = start_cmd and stop_cmd

            now = time.time()
            if start_cmd and not self._pump_running:
                if self._pending_start_ts == 0.0:
                    self._pending_start_ts = now + START_DELAY
                    LOGGER.info('Start command seen, will start at %s', self._pending_start_ts)
            else:
                self._pending_start_ts = 0.0

            if stop_cmd and self._pump_running:
                if self._pending_stop_ts == 0.0:
                    self._pending_stop_ts = now + STOP_DELAY
                    LOGGER.info('Stop command seen, will stop at %s', self._pending_stop_ts)
            else:
                self._pending_stop_ts = 0.0

            if self._pending_start_ts and now >= self._pending_start_ts and not self._pump_running:
                self._pump_running = True
                LOGGER.info('Pump transitioned to RUNNING')
                self.write_coil(2, 1)

            if self._pending_stop_ts and now >= self._pending_stop_ts and self._pump_running:
                self._pump_running = False
                LOGGER.info('Pump transitioned to STOPPED')
                self.write_coil(2, 0)

            # Update fault coil
            self.write_coil(3, 1 if self._pump_fault else 0)

            time.sleep(POLL_INTERVAL)

        LOGGER.info('Pump emulator loop stopped')

    def stop(self) -> None:
        self._stopped.set()


def run_server() -> None:
    # 100 coils available
    store = ModbusSlaveContext(co=ModbusSequentialDataBlock(0, [0] * 100))
    context = ModbusServerContext(slaves=store, single=True)

    pump = PumpEmulator(context)
    t = threading.Thread(target=pump.loop, daemon=True)
    t.start()

    LOGGER.info('Starting Modbus TCP server on 0.0.0.0:502')
    try:
        StartTcpServer(context, address=("0.0.0.0", 502))
    except Exception:
        LOGGER.exception('Modbus server terminated')
    finally:
        pump.stop()


if __name__ == '__main__':
    run_server()
