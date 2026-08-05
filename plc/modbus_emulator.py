#!/usr/bin/env python3
"""Modbus/TCP emulator — fallback PLC para PoC.

Coils (idénticos para todos los tipos de planta):
  0 -> actuator_start   (comando arranque)
  1 -> actuator_stop    (comando parada)
  2 -> actuator_running (estado, salida)
  3 -> actuator_fault   (fallo, salida)

Uso:
  python3 plc/modbus_emulator.py --plant-type water --port 502
  python3 plc/modbus_emulator.py --plant-type gas   --port 502
  python3 plc/modbus_emulator.py --plant-type elec  --port 502
"""
from __future__ import annotations

import argparse
import logging
import threading
import time
from typing import List

try:
    from pymodbus.server import StartTcpServer
except ImportError:
    from pymodbus.server.sync import StartTcpServer

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext, ModbusSlaveContext

# Parámetros de temporización por tipo de planta (start_delay, stop_delay) en segundos
_PLANT_TIMINGS = {
    'water': (5.0, 3.0),
    'gas':   (8.0, 5.0),  # válvulas de gas: delays más conservadores
    'elec':  (2.0, 1.0),  # disyuntores: respuesta rápida
    'transport': (1.0, 1.0), # semáforos: respuesta instantánea
}

POLL_INTERVAL = 0.5


class ActuatorEmulator:
    """Emula la lógica ST del PLC: TON arranque/parada y detección de fallo."""

    def __init__(self, context: ModbusServerContext, start_delay: float, stop_delay: float, name: str) -> None:
        self.context = context
        self.start_delay = start_delay
        self.stop_delay = stop_delay
        self._logger = logging.getLogger(f'modbus_emulator.{name}')
        self._pending_start_ts = 0.0
        self._pending_stop_ts = 0.0
        self._running = False
        self._stopped = threading.Event()

    def _read_coils(self, count: int = 4) -> List[int]:
        return self.context[0x00].getValues(1, 0, count)

    def _write_coil(self, addr: int, value: int) -> None:
        self.context[0x00].setValues(1, addr, [int(value)])

    def loop(self) -> None:
        self._logger.info('Actuator loop starting (start_delay=%.1fs stop_delay=%.1fs)',
                          self.start_delay, self.stop_delay)
        while not self._stopped.is_set():
            coils = self._read_coils(4)
            start_cmd, stop_cmd = bool(coils[0]), bool(coils[1])
            fault = start_cmd and stop_cmd
            now = time.time()

            if start_cmd and not self._running:
                if self._pending_start_ts == 0.0:
                    self._pending_start_ts = now + self.start_delay
            else:
                self._pending_start_ts = 0.0

            if stop_cmd and self._running:
                if self._pending_stop_ts == 0.0:
                    self._pending_stop_ts = now + self.stop_delay
            else:
                self._pending_stop_ts = 0.0

            if self._pending_start_ts and now >= self._pending_start_ts and not self._running:
                self._running = True
                self._logger.info('Actuator → RUNNING')
                self._write_coil(2, 1)

            if self._pending_stop_ts and now >= self._pending_stop_ts and self._running:
                self._running = False
                self._logger.info('Actuator → STOPPED')
                self._write_coil(2, 0)

            self._write_coil(3, 1 if fault else 0)
            time.sleep(POLL_INTERVAL)

    def stop(self) -> None:
        self._stopped.set()


def run_server(host: str, port: int, plant_type: str) -> None:
    start_delay, stop_delay = _PLANT_TIMINGS[plant_type]
    logger = logging.getLogger('modbus_emulator')

    store = ModbusSlaveContext(co=ModbusSequentialDataBlock(0, [0] * 100))
    context = ModbusServerContext(slaves=store, single=True)

    actuator = ActuatorEmulator(context, start_delay, stop_delay, plant_type)
    t = threading.Thread(target=actuator.loop, daemon=True)
    t.start()

    logger.info('Starting Modbus TCP server [%s] on %s:%d', plant_type, host, port)
    try:
        StartTcpServer(context, address=(host, port))
    except Exception:
        logger.exception('Modbus server terminated')
    finally:
        actuator.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description='Modbus/TCP PLC emulator')
    parser.add_argument('--plant-type', choices=list(_PLANT_TIMINGS), default='water',
                        help='Tipo de planta: water | gas | elec (default: water)')
    parser.add_argument('--host', default='0.0.0.0', help='Bind address (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=502, help='Modbus TCP port (default: 502)')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format=f'[%(levelname)s][{args.plant_type}] %(message)s')
    run_server(args.host, args.port, args.plant_type)


if __name__ == '__main__':
    main()
