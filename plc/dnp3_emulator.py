#!/usr/bin/env python3
"""DNP3 Outstation (IEEE 1815) Emulator — Emulador de PLC Eléctrico para CityLab.

Proporciona un Outstation DNP3 sobre TCP (puerto por defecto: 20000).
Expone telemetría DNP3 estándar para subestaciones / generación eléctrica:

Objetos DNP3:
  - Binary Inputs (Group 1):
      Index 0: breaker_closed   (1 = cerrado/normal, 0 = abierto/tripped)
      Index 1: grid_healthy     (1 = tensión OK >=0.85pu, 0 = subvoltaje)
  - Binary Outputs / CROB (Group 12):
      Index 0: trip_breaker     (Operación Latch-On / Pulse-On abre el disyuntor)
      Index 1: close_breaker    (Operación Latch-On / Pulse-On cierra el disyuntor)
  - Analog Inputs (Group 30):
      Index 0: voltage_pu_x100  (Voltaje en % pu * 100, ej. 100 = 1.00 pu)
      Index 1: frequency_cHz    (Frecuencia en cHz, ej. 6000 = 60.00 Hz)
      Index 2: power_kw         (Potencia activa generada en kW)

Uso:
  python3 plc/dnp3_emulator.py --host 0.0.0.0 --port 20000
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import logging
import socket
import struct
import threading
import time
from typing import Tuple, Optional, Dict, Any

POLL_INTERVAL = 0.5
DNP3_MAGIC = b'\x05\x64'  # DNP3 Link Layer Header bytes 0-1

logging.basicConfig(level=logging.INFO, format='[%(levelname)s][DNP3-Outstation] %(message)s')
LOGGER = logging.getLogger('dnp3_emulator')


def crc16_dnp(data: bytes) -> int:
    """Calcula el CRC-16 especificado por DNP3 (invertido / complemento a unos)."""
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA66B
            else:
                crc >>= 1
    return (~crc) & 0xFFFF


class Dnp3OutstationState:
    """Mantiene el estado interno de la subestación eléctrica emulada."""

    def __init__(self) -> None:
        self.breaker_closed: bool = True
        self.grid_healthy: bool = True
        self.voltage_pu: float = 1.00
        self.frequency_hz: float = 60.00
        self.power_kw: float = 500.00
        self.fault_active: bool = False
        self._lock = threading.Lock()

    def trip_breaker(self) -> None:
        with self._lock:
            self.breaker_closed = False
            self.power_kw = 0.0
            LOGGER.info("DNP3 CROB Command Executed: BREAKER TRIPPED")

    def close_breaker(self) -> None:
        with self._lock:
            self.breaker_closed = True
            self.power_kw = 500.0 if self.grid_healthy else 0.0
            LOGGER.info("DNP3 CROB Command Executed: BREAKER CLOSED")

    def get_binary_input(self, index: int) -> bool:
        with self._lock:
            if index == 0:
                return self.breaker_closed
            elif index == 1:
                return self.grid_healthy
            return False

    def get_analog_input(self, index: int) -> int:
        with self._lock:
            if index == 0:
                return int(self.voltage_pu * 100)
            elif index == 1:
                return int(self.frequency_hz * 100)
            elif index == 2:
                return int(self.power_kw)
            return 0


class Dnp3ProtocolHandler:
    """Decodifica tramas DNP3 TCP/IP y genera respuestas de Outstation DNP3 validas."""

    def __init__(self, state: Dnp3OutstationState) -> None:
        self.state = state

    def handle_frame(self, frame: bytes) -> bytes:
        """Procesa una trama DNP3 entrante y devuelve el paquete de respuesta DNP3."""
        if len(frame) < 10 or frame[0:2] != DNP3_MAGIC:
            # Petición minimalista / ping simple para verificación de conectividad
            return self._build_simple_response(function_code=0x81)

        # Analizar cabecera del enlace DNP3
        length = frame[2]
        control = frame[3]
        dest_addr = struct.unpack('<H', frame[4:6])[0]
        src_addr = struct.unpack('<H', frame[6:8])[0]

        # Extraer capa de aplicación DNP3 si está presente
        # Formato DNP3 App Header: [App Control (1B)] [Function Code (1B)] ...
        func_code = 0x01  # Default READ
        if len(frame) >= 12:
            func_code = frame[11]

        if func_code == 0x01:  # READ request
            return self._build_read_response(dest_addr=src_addr, src_addr=dest_addr)
        elif func_code in (0x03, 0x04, 0x05):  # SELECT / OPERATE / DIRECT OPERATE (CROB)
            # DNP3 Secure Authentication (SA Level 1 IEEE 1815-2012 §7)
            # Si sa_required está activo, exige HMAC-SHA256 válido al final de la trama
            if getattr(self, 'sa_required', False):
                secret = b'CITYLAB_DNP3_SA_KEY_2026'
                if len(frame) < 23:
                    LOGGER.warning("DNP3 SA Error: CROB rechazado por falta de HMAC (SA Required)")
                    return self._build_simple_response(function_code=0x83)  # Auth Failed
                expected_hmac = hmac.new(secret, frame[:19], hashlib.sha256).digest()[:4]
                received_hmac = frame[19:23]
                if not hmac.compare_digest(expected_hmac, received_hmac):
                    LOGGER.warning("DNP3 SA Error: Firma HMAC inválida en comando CROB")
                    return self._build_simple_response(function_code=0x83)

            if len(frame) >= 19:
                crob_index = frame[17]
                crob_code = frame[18]
                if crob_code == 0x41 or crob_index == 0:
                    self.state.trip_breaker()
                elif crob_code == 0x01 or crob_index == 1:
                    self.state.close_breaker()
                else:
                    self.state.trip_breaker()
            else:
                self.state.trip_breaker()
            return self._build_crob_response(dest_addr=src_addr, src_addr=dest_addr)

        return self._build_read_response(dest_addr=src_addr, src_addr=dest_addr)

    def _build_read_response(self, dest_addr: int, src_addr: int) -> bytes:
        """Construye un paquete de respuesta DNP3 READ conteniendo BI (0,1) y AI (0,1,2)."""
        bi0 = 1 if self.state.get_binary_input(0) else 0
        bi1 = 1 if self.state.get_binary_input(1) else 0

        ai0 = self.state.get_analog_input(0)
        ai1 = self.state.get_analog_input(1)
        ai2 = self.state.get_analog_input(2)

        # App Layer Payload: [AppCtrl=0xc0] [Func=0x81 (RESPONSE)] [IIN1=0x00] [IIN2=0x00]
        # Group 1 (BI): [Grp=1, Var=2, Qual=0x00, Count=2] [bi0_flags] [bi1_flags]
        # Group 30 (AI 16-bit): [Grp=30, Var=1, Qual=0x00, Count=3] [ai0] [ai1] [ai2]
        bi_flags0 = 0x80 if bi0 else 0x00
        bi_flags1 = 0x80 if bi1 else 0x00

        app_payload = (
            b'\xc0\x81\x00\x00'  # App Control (FIR+FIN), Response (0x81), Internal Indications (0x0000)
            b'\x01\x02\x00\x02'  # Group 1 Var 2 (BI with status), 2 items
            + bytes([bi_flags0, bi_flags1])
            + b'\x1e\x01\x00\x03'  # Group 30 Var 1 (32-bit AI) or Group 30 Var 2 (16-bit AI), 3 items
            + struct.pack('<hhh', ai0, ai1, ai2)
        )

        return self._wrap_link_layer(dest_addr, src_addr, app_payload)

    def _build_crob_response(self, dest_addr: int, src_addr: int) -> bytes:
        """Construye respuesta DNP3 CROB ACK (Success)."""
        app_payload = b'\xc0\x81\x00\x00\x0c\x01\x00\x01\x01\x00\x00\x00'  # Success ACK
        return self._wrap_link_layer(dest_addr, src_addr, app_payload)

    def _build_simple_response(self, function_code: int = 0x81) -> bytes:
        app_payload = bytes([0xc0, function_code, 0x00, 0x00]) + struct.pack(
            '<hh', self.state.get_analog_input(0), self.state.get_analog_input(2)
        )
        return self._wrap_link_layer(dest_addr=1, src_addr=10, payload=app_payload)

    def _wrap_link_layer(self, dest_addr: int, src_addr: int, payload: bytes) -> bytes:
        """Envuelve la carga útil en la trama Link Layer de DNP3 con CRCs."""
        len_byte = len(payload) + 5  # Length excludes magic bytes & len byte itself
        header_raw = DNP3_MAGIC + bytes([len_byte, 0x44]) + struct.pack('<HH', dest_addr, src_addr)
        header_crc = crc16_dnp(header_raw)
        header_complete = header_raw + struct.pack('<H', header_crc)

        payload_crc = crc16_dnp(payload)
        return header_complete + payload + struct.pack('<H', payload_crc)


class Dnp3Server:
    """Servidor TCP Outstation DNP3 para la subestación eléctrica."""

    def __init__(self, host: str = '0.0.0.0', port: int = 20000) -> None:
        self.host = host
        self.port = port
        self.state = Dnp3OutstationState()
        self.handler = Dnp3ProtocolHandler(self.state)
        self._running = False
        self._sock: Optional[socket.socket] = None

    def start(self) -> None:
        self._running = True
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(5)
        LOGGER.info("Servidor DNP3 Outstation escuchando en %s:%d", self.host, self.port)

        while self._running:
            try:
                self._sock.settimeout(1.0)
                client, addr = self._sock.accept()
                LOGGER.info("Conexión DNP3 entrante desde %s", addr)
                t = threading.Thread(target=self._handle_client, args=(client, addr), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception as exc:
                if self._running:
                    LOGGER.error("Error en accept() DNP3: %s", exc)

    def _handle_client(self, client: socket.socket, addr: Tuple[str, int]) -> None:
        with client:
            client.settimeout(2.0)
            while self._running:
                try:
                    data = client.recv(1024)
                    if not data:
                        break
                    resp = self.handler.handle_frame(data)
                    client.sendall(resp)
                except (socket.timeout, ConnectionResetError, BrokenPipeError):
                    break
                except Exception as exc:
                    LOGGER.warning("Error procesando trama DNP3 desde %s: %s", addr, exc)
                    break
        LOGGER.info("Conexión DNP3 cerrada desde %s", addr)

    def stop(self) -> None:
        self._running = False
        if self._sock:
            self._sock.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Emulador DNP3 Outstation IEEE 1815 (PLC Eléctrico)")
    parser.add_argument("--host", default="0.0.0.0", help="Dirección IP de bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=20000, help="Puerto DNP3 TCP (default: 20000)")
    args = parser.parse_args()

    server = Dnp3Server(args.host, args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        LOGGER.info("Deteniendo DNP3 Outstation...")
        server.stop()


if __name__ == "__main__":
    main()
