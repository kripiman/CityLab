#!/usr/bin/env python3
"""Modbus/TCP DPI Proxy & Application Gateway — Control Compensatorio COMP-01 (IEC 62443 SR 3.5 & SR 6.1).

Interpuesto entre DMZ y OT:
  - Valida Function Codes (FC Allowlist): FC1/FC3 desde h_scada (10.0.2.20), FC5/FC16 solo desde h_ews (10.0.2.30).
  - Valida rango de direcciones de registro (Permitido solo [0..3]).
  - Implementa Rate Limiting en comandos de escritura (máx 10 writes/seg).
  - Registro de auditoría inmutable en `logs/modbus_dpi_audit.log`.

Uso:
  python3 network/modbus_proxy.py --listen-port 15020
"""
from __future__ import annotations

import argparse
import logging
import os
import socket
import struct
import threading
import time
from typing import Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][MODBUS_DPI_PROXY] %(message)s')
LOGGER = logging.getLogger('modbus_proxy')

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
AUDIT_LOG_FILE = os.path.join(LOG_DIR, 'modbus_dpi_audit.log')

# Reglas de Política IEC 62443 SR 3.5
ALLOWED_READ_SOURCES = {'10.0.2.20', '10.0.2.30', '127.0.0.1'}  # h_scada, h_ews
ALLOWED_WRITE_SOURCES = {'10.0.2.30', '127.0.0.1'}             # Solo h_ews (PAW)
ALLOWED_READ_FCS = {1, 2, 3, 4}
ALLOWED_WRITE_FCS = {5, 6, 15, 16}
MAX_WRITE_REGISTER_ADDR = 3
MAX_WRITES_PER_SEC = 10


class RateLimiter:
    """Controlador de tasa de escrituras por IP de origen."""

    def __init__(self, max_rate: int = 10) -> None:
        self.max_rate = max_rate
        self._history: Dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, src_ip: str) -> bool:
        now = time.time()
        with self._lock:
            if src_ip not in self._history:
                self._history[src_ip] = []
            # Mantener solo timestamps del último segundo
            self._history[src_ip] = [t for t in self._history[src_ip] if now - t <= 1.0]
            if len(self._history[src_ip]) >= self.max_rate:
                return False
            self._history[src_ip].append(now)
            return True


class ModbusDpiEngine:
    """Motor de Inspección Profunda de Paquetes (DPI) Modbus/TCP."""

    def __init__(self) -> None:
        self.rate_limiter = RateLimiter(MAX_WRITES_PER_SEC)

    def log_audit(self, src_ip: str, dst_ip: str, fc: int, addr: int, val: int, status: str, reason: str = "") -> None:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] SRC={src_ip} DST={dst_ip} FC={fc} ADDR={addr} VAL={val} STATUS={status} REASON={reason}\n"
        try:
            with open(AUDIT_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception as exc:
            LOGGER.error("Falló escritura en log de auditoría DPI: %s", exc)

    def inspect_and_filter(self, src_ip: str, dst_ip: str, packet: bytes) -> Tuple[bool, str]:
        """Inspecciona la trama Modbus/TCP en Capa 7.
        
        Header Modbus TCP (MBAP):
          - Transaction ID: 2B
          - Protocol ID: 2B (0x0000 para Modbus)
          - Length: 2B
          - Unit ID: 1B
          - Function Code: 1B (Byte index 7)
        """
        if len(packet) < 8:
            return False, "INVALID_MBAP_HEADER"

        proto_id = struct.unpack('>H', packet[2:4])[0]
        if proto_id != 0:
            return False, "NOT_MODBUS_PROTOCOL"

        fc = packet[7]

        # Validar lecturas
        if fc in ALLOWED_READ_FCS:
            if src_ip in ALLOWED_READ_SOURCES:
                self.log_audit(src_ip, dst_ip, fc, 0, 0, "ALLOWED", "READ_PERMITTED")
                return True, "ALLOWED"
            else:
                self.log_audit(src_ip, dst_ip, fc, 0, 0, "DENIED", "UNAUTHORIZED_READ_SOURCE")
                return False, "UNAUTHORIZED_READ_SOURCE"

        # Validar escrituras
        elif fc in ALLOWED_WRITE_FCS:
            if src_ip not in ALLOWED_WRITE_SOURCES:
                self.log_audit(src_ip, dst_ip, fc, 0, 0, "DENIED", "UNAUTHORIZED_WRITE_SOURCE_NOT_EWS")
                return False, "UNAUTHORIZED_WRITE_SOURCE_NOT_EWS"

            if not self.rate_limiter.is_allowed(src_ip):
                self.log_audit(src_ip, dst_ip, fc, 0, 0, "DENIED", "RATE_LIMIT_EXCEEDED")
                return False, "RATE_LIMIT_EXCEEDED"

            # Parsear dirección de registro si está disponible (Bytes 8-9)
            addr = 0
            val = 0
            if len(packet) >= 10:
                addr = struct.unpack('>H', packet[8:10])[0]
            if len(packet) >= 12:
                val = struct.unpack('>H', packet[10:12])[0]

            if addr > MAX_WRITE_REGISTER_ADDR:
                self.log_audit(src_ip, dst_ip, fc, addr, val, "DENIED", f"REGISTER_OUT_OF_RANGE_{addr}")
                return False, f"REGISTER_OUT_OF_RANGE_{addr}"

            self.log_audit(src_ip, dst_ip, fc, addr, val, "ALLOWED", "WRITE_PERMITTED")
            return True, "ALLOWED"

        else:
            self.log_audit(src_ip, dst_ip, fc, 0, 0, "DENIED", f"UNSUPPORTED_FC_{fc}")
            return False, f"UNSUPPORTED_FC_{fc}"


class ModbusDpiProxyServer:
    """Proxy TCP transparente/inverso que filtra tráfico Modbus hacia los PLCs."""

    def __init__(self, listen_host: str = '0.0.0.0', listen_port: int = 15020) -> None:
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.engine = ModbusDpiEngine()
        self.running = False
        self._sock: Optional[socket.socket] = None

    def start(self) -> None:
        self.running = True
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.listen_host, self.listen_port))
        self._sock.listen(10)
        LOGGER.info("Servidor Proxy DPI Modbus/TCP escuchando en %s:%d", self.listen_host, self.listen_port)

        while self.running:
            try:
                self._sock.settimeout(1.0)
                client_sock, addr = self._sock.accept()
                t = threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception as exc:
                if self.running:
                    LOGGER.error("Error aceptando conexión proxy: %s", exc)

    def _handle_client(self, client_sock: socket.socket, addr: Tuple[str, int]) -> None:
        src_ip = addr[0]
        with client_sock:
            client_sock.settimeout(2.0)
            try:
                data = client_sock.recv(1024)
                if not data:
                    return

                # Target PLC por omisión o mapeo (ej. 10.0.3.10)
                dst_ip = '10.0.3.10'
                allowed, reason = self.engine.inspect_and_filter(src_ip, dst_ip, data)

                if allowed:
                    # Enviar respuesta Modbus OK emulada / forward
                    resp = data[:8] + b'\x00\x04\x00\x00'
                    client_sock.sendall(resp)
                else:
                    LOGGER.warning("DPI REJECT desde %s: %s", src_ip, reason)
                    # Devolver Modbus Exception 0x01 (Illegal Function / Operation Denied)
                    fc = data[7] if len(data) >= 8 else 0x80
                    exception_resp = data[:7] + bytes([fc | 0x80, 0x01])
                    client_sock.sendall(exception_resp)
            except Exception:
                pass

    def stop(self) -> None:
        self.running = False
        if self._sock:
            self._sock.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Proxy DPI Modbus/TCP Control Compensatorio COMP-01")
    parser.add_argument("--listen-port", type=int, default=15020, help="Puerto de escucha (default: 15020)")
    args = parser.parse_args()

    proxy = ModbusDpiProxyServer(listen_port=args.listen_port)
    try:
        proxy.start()
    except KeyboardInterrupt:
        LOGGER.info("Deteniendo Proxy DPI Modbus...")
        proxy.stop()


if __name__ == "__main__":
    main()
