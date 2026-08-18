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
import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
    'hospital': (3.0, 2.0), # cargas hospitalarias y HVAC UCI
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


class NtcipListener:
    """Listener NTCIP 1202 de baja fidelidad en el mismo host que el PLC de transporte.

    Handshake fijo sobre TCP (no SNMP real). OVERRIDE FLASH emite evento SIEM.
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 161) -> None:
        self.host = host
        self.port = port
        self.phase = 'NS_GREEN'
        self.coord = 'ON'
        self._running = False
        self._sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self.siem = None
        try:
            from network.siem_pipeline import SiemCorrelationEngine
            self.siem = SiemCorrelationEngine()
        except Exception:
            self.siem = None

    def start(self) -> None:
        self._running = True
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(5)
        logging.getLogger('modbus_emulator.ntcip').info(
            'NTCIP listener on %s:%d', self.host, self.port)
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def handle_command(self, raw: str) -> str:
        cmd = raw.strip().upper()
        if cmd.startswith('OVERRIDE FLASH'):
            self.phase = 'FLASHING_YELLOW'
            self.coord = 'OFF'
            if self.siem is not None:
                self.siem.ingest_raw_event(
                    event_category='process_control',
                    event_type='alert',
                    severity='HIGH',
                    source_ip='local',
                    destination_ip=self.host,
                    service_name='ntcip_1202',
                    message='NTCIP phase override FLASHING_YELLOW',
                )
            return 'NTCIP 1202 PHASE=FLASHING_YELLOW COORD=OFF'
        if cmd.startswith('OVERRIDE CLEAR'):
            self.phase = 'NS_GREEN'
            self.coord = 'ON'
            return 'NTCIP 1202 PHASE=NS_GREEN COORD=ON'
        return f'NTCIP 1202 PHASE={self.phase} COORD={self.coord}'

    def _listen_loop(self) -> None:
        if not self._sock:
            return
        while self._running:
            try:
                self._sock.settimeout(1.0)
                client, _addr = self._sock.accept()
                with client:
                    client.settimeout(1.0)
                    try:
                        data = client.recv(1024)
                        if data:
                            resp = self.handle_command(data.decode('utf-8', errors='replace'))
                            client.sendall((resp + '\n').encode('ascii'))
                    except OSError:
                        pass
            except socket.timeout:
                continue
            except Exception as exc:
                if self._running:
                    logging.getLogger('modbus_emulator.ntcip').debug('NTCIP loop exception: %s', exc)
                    time.sleep(0.5)

    def stop(self) -> None:
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass


class BacnetListener:
    """Listener BACnet/IP (UDP 47808) de baja fidelidad para automatización de edificios/hospital.

    Responde con I-Am APDU ante cabecera BVLC (0x81) y maneja comandos de control/alarma.
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 47808) -> None:
        self.host = host
        self.port = port
        self.device_id = 1001
        self.status = 'NORMAL'
        self._running = False
        self._sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self.siem = None
        try:
            from network.siem_pipeline import SiemCorrelationEngine
            self.siem = SiemCorrelationEngine()
        except Exception:
            self.siem = None

    def start(self) -> None:
        self._running = True
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        logging.getLogger('modbus_emulator.bacnet').info(
            'BACnet/IP listener on %s:%d (UDP)', self.host, self.port)
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def handle_datagram(self, raw: bytes) -> bytes:
        # Check if BACnet BVLC header (0x81)
        if len(raw) >= 4 and raw[0] == 0x81:
            # BVLC Type 0x81 (BACnet/IP), Function 0x0A (Original-Unicast) or 0x0B (Original-Broadcast)
            # Respond with BVLC Original-Unicast I-Am (APDU 0x10)
            reply = bytearray([0x81, 0x0a, 0x00, 0x0c, 0x01, 0x00, 0x10, 0x08, 0x00, 0x03, 0xe9, 0x37])
            return bytes(reply)

        text = raw.decode('utf-8', errors='replace').strip().upper()
        if text.startswith('OVERRIDE BACNET') or text.startswith('ALARM'):
            self.status = 'ALARM'
            if self.siem is not None:
                self.siem.ingest_raw_event(
                    event_category='process_control',
                    event_type='alert',
                    severity='HIGH',
                    source_ip='local',
                    destination_ip=self.host,
                    service_name='bacnet_ip',
                    message='BACnet building management alarm override',
                )
            return f'BACNET/IP DEVICE_ID={self.device_id} STATUS=ALARM HVAC=EMERGENCY_STOP\n'.encode('ascii')
        if text.startswith('RESET'):
            self.status = 'NORMAL'
            return f'BACNET/IP DEVICE_ID={self.device_id} STATUS=NORMAL HVAC=RUNNING\n'.encode('ascii')

        return f'BACNET/IP DEVICE_ID={self.device_id} STATUS={self.status} TEMP_ANALOG=21.5C\n'.encode('ascii')

    def _listen_loop(self) -> None:
        if not self._sock:
            return
        while self._running:
            try:
                self._sock.settimeout(1.0)
                data, addr = self._sock.recvfrom(2048)
                if data:
                    resp = self.handle_datagram(data)
                    self._sock.sendto(resp, addr)
            except socket.timeout:
                continue
            except Exception as exc:
                if self._running:
                    logging.getLogger('modbus_emulator.bacnet').debug('BACnet loop exception: %s', exc)
                    time.sleep(0.5)

    def stop(self) -> None:
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass


def run_server(host: str, port: int, plant_type: str, ntcip_port: int = 0, bacnet_port: int = 0) -> None:
    start_delay, stop_delay = _PLANT_TIMINGS[plant_type]
    logger = logging.getLogger('modbus_emulator')

    store = ModbusSlaveContext(co=ModbusSequentialDataBlock(0, [0] * 100))
    context = ModbusServerContext(slaves=store, single=True)

    actuator = ActuatorEmulator(context, start_delay, stop_delay, plant_type)
    t = threading.Thread(target=actuator.loop, daemon=True)
    t.start()

    ntcip: Optional[NtcipListener] = None
    if ntcip_port:
        try:
            ntcip = NtcipListener(host, ntcip_port)
            ntcip.start()
        except Exception as exc:
            logger.warning('Failed to start NTCIP listener on %s:%d: %s', host, ntcip_port, exc)
            ntcip = None

    bacnet: Optional[BacnetListener] = None
    if bacnet_port:
        try:
            bacnet = BacnetListener(host, bacnet_port)
            bacnet.start()
        except Exception as exc:
            logger.warning('Failed to start BACnet listener on %s:%d: %s', host, bacnet_port, exc)
            bacnet = None

    logger.info('Starting Modbus TCP server [%s] on %s:%d', plant_type, host, port)
    try:
        StartTcpServer(context, address=(host, port))
    except Exception:
        logger.exception('Modbus server terminated')
    finally:
        actuator.stop()
        if ntcip:
            ntcip.stop()
        if bacnet:
            bacnet.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description='Modbus/TCP PLC emulator')
    parser.add_argument('--plant-type', choices=list(_PLANT_TIMINGS), default='water',
                        help='Tipo de planta: water | gas | elec (default: water)')
    default_host = os.getenv('MODBUS_HOST', os.getenv('BIND_HOST', '0.0.0.0'))
    parser.add_argument('--host', default=default_host, help=f'Bind address (default: {default_host})')
    parser.add_argument('--port', type=int, default=502, help='Modbus TCP port (default: 502)')
    parser.add_argument('--ntcip-port', type=int, default=None,
                        help='NTCIP TCP port (default 161 if plant-type=transport, 0 disables)')
    parser.add_argument('--bacnet-port', type=int, default=None,
                        help='BACnet UDP port (default 47808 if plant-type=hospital, 0 disables)')
    args = parser.parse_args()

    ntcip_port = args.ntcip_port
    if ntcip_port is None:
        ntcip_port = 161 if args.plant_type == 'transport' else 0

    bacnet_port = args.bacnet_port
    if bacnet_port is None:
        bacnet_port = 47808 if args.plant_type == 'hospital' else 0

    logging.basicConfig(level=logging.INFO,
                        format=f'[%(levelname)s][{args.plant_type}] %(message)s')
    run_server(args.host, args.port, args.plant_type, ntcip_port=ntcip_port, bacnet_port=bacnet_port)


if __name__ == '__main__':
    main()
