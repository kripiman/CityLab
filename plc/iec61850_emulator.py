#!/usr/bin/env python3
"""plc/iec61850_emulator.py — Emulador de Protocolos Subestación IEC 61850 GOOSE y SV (Fase 3)

Implementación de IEC 61850 Substation Automation (GOOSE + Sampled Values):
  - GOOSE (Generic Object Oriented Substation Events): Eventos en tiempo real sobre Ethernet/UDP Multicast.
  - SV (Sampled Values): Transmisión de mediciones instantáneas (Voltaje/Corriente).
  - IED Emulado (Intelligent Electronic Device): Nodo de subestación eléctrica con dataset IEC 61850.

Scope pedagógico:
  - Permite simular mensajes GOOSE de disparo (Trip) y actualización de estado de interruptores (XCBR).
  - Permite simular flujo de Sampled Values (MMXU) para monitoreo de corriente/voltaje en subestación.
  - Soporta modo UDP Multicast / Unicast autónomo para ejecución en espacio de usuario sin permisos root.

Integración:
  - Subestación Eléctrica CityLab (zona OT 10.0.3.x).
  - Interopera con `fed_gridmock.py` y `gridlabd_federate.py`.
"""
from __future__ import annotations

import logging
import os
import socket
import struct
import threading
import time
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger('iec61850_emulator')

# ------------------------------------------------------------------ #
#  Constantes IEC 61850                                               #
# ------------------------------------------------------------------ #
ETHERTYPE_GOOSE = 0x88B8
ETHERTYPE_SV    = 0x88BA

DEFAULT_GOOSE_PORT = 10102
DEFAULT_SV_PORT    = 10103

MULTICAST_GOOSE_ADDR = '239.0.0.1'
MULTICAST_SV_ADDR    = '239.0.0.2'


class IEC61850DataSet:
    """Dataset IEC 61850 con modelos LNode standard (XCBR, MMXU, CSWI)."""

    def __init__(self, ied_name: str = 'CITYLAB_IED1') -> None:
        self.ied_name = ied_name
        self._lock = threading.Lock()
        self._st_num = 1
        self._sq_num = 0
        self._data: Dict[str, Any] = {
            # Logical Node XCBR (Circuit Breaker)
            'XCBR1.Pos.stVal': True,       # True = Closed, False = Tripped/Open
            'XCBR1.Loc.stVal': False,      # False = Remote, True = Local
            'XCBR1.OpCnt.stVal': 42,       # Operation Counter
            # Logical Node MMXU (Measurements)
            'MMXU1.PhV.phsA.cVal.mag': 230.0,
            'MMXU1.PhV.phsB.cVal.mag': 230.0,
            'MMXU1.PhV.phsC.cVal.mag': 230.0,
            'MMXU1.Amp.phsA.cVal.mag': 15.5,
            'MMXU1.Hz.stVal': 60.0,
            # Logical Node CSWI (Switch Controller)
            'CSWI1.Pos.stVal': True,
        }
        self._quality_flags: Dict[str, int] = {
            'XCBR1.Pos.stVal': 0x0000,     # 0x0000 = GOOD, 0x0001 = INVALID, 0x0004 = TEST
            'MMXU1.PhV.phsA.cVal.mag': 0x0000,
        }

    def get(self, key: str) -> Any:
        with self._lock:
            return self._data.get(key)

    def get_quality(self, key: str) -> int:
        with self._lock:
            return self._quality_flags.get(key, 0x0000)

    def set_quality(self, key: str, q_flags: int) -> None:
        with self._lock:
            self._quality_flags[key] = q_flags

    def set(self, key: str, value: Any) -> bool:
        with self._lock:
            if key not in self._data:
                self._data[key] = value
                return True
            if self._data[key] != value:
                self._data[key] = value
                self._st_num += 1  # Increment state number on value change
                self._sq_num = 0
                return True
            return False

    def increment_seq(self) -> int:
        with self._lock:
            self._sq_num += 1
            return self._sq_num

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'ied_name': self.ied_name,
                'st_num': self._st_num,
                'sq_num': self._sq_num,
                'data': dict(self._data),
                'quality': dict(self._quality_flags)
            }


class Iec61850GooseEncoder:
    """Codificador/Decodificador binario simplificado para PDU GOOSE IEC 61850."""

    @staticmethod
    def encode(gcb_ref: str, datset_ref: str, st_num: int, sq_num: int, breaker_pos: bool, conf_rev: int = 1, test_mode: bool = False) -> bytes:
        """Codifica un PDU GOOSE binario en formato TLV / APDU con ConfRev y Test mode."""
        gcb_bytes = gcb_ref.encode('utf-8')
        ds_bytes = datset_ref.encode('utf-8')
        
        payload = struct.pack(
            '>HH H%ds H%ds II I??' % (len(gcb_bytes), len(ds_bytes)),
            ETHERTYPE_GOOSE,
            len(gcb_bytes) + len(ds_bytes) + 20,
            len(gcb_bytes), gcb_bytes,
            len(ds_bytes), ds_bytes,
            st_num,
            sq_num,
            conf_rev,
            test_mode,
            breaker_pos
        )
        return payload

    @staticmethod
    def decode(data: bytes) -> Optional[Dict[str, Any]]:
        """Decodifica un PDU GOOSE binario."""
        if len(data) < 14:
            return None
        try:
            ethertype, length = struct.unpack_from('>HH', data, 0)
            if ethertype != ETHERTYPE_GOOSE:
                return None
            gcb_len = struct.unpack_from('>H', data, 4)[0]
            offset = 6
            gcb_ref = data[offset:offset+gcb_len].decode('utf-8')
            offset += gcb_len
            
            ds_len = struct.unpack_from('>H', data, offset)[0]
            offset += 2
            datset_ref = data[offset:offset+ds_len].decode('utf-8')
            offset += ds_len
            
            if len(data) >= offset + 14:
                st_num, sq_num, conf_rev, test_mode, breaker_pos = struct.unpack_from('>III??', data, offset)
            else:
                st_num, sq_num, breaker_pos = struct.unpack_from('>II?', data, offset)
                conf_rev, test_mode = 1, False

            return {
                'ethertype': hex(ethertype),
                'gcb_ref': gcb_ref,
                'datset_ref': datset_ref,
                'st_num': st_num,
                'sq_num': sq_num,
                'conf_rev': conf_rev,
                'test_mode': test_mode,
                'breaker_pos': breaker_pos
            }
        except Exception as e:
            LOGGER.debug('Error decodificando GOOSE: %s', e)
            return None


class Iec61850SvEncoder:
    """Codificador/Decodificador binario para Sampled Values (SV)."""

    @staticmethod
    def encode(sv_id: str, smp_cnt: int, v_a: float, i_a: float) -> bytes:
        sv_bytes = sv_id.encode('utf-8')
        payload = struct.pack(
            '>HH H%ds I ff' % len(sv_bytes),
            ETHERTYPE_SV,
            len(sv_bytes) + 14,
            len(sv_bytes), sv_bytes,
            smp_cnt,
            v_a,
            i_a
        )
        return payload

    @staticmethod
    def decode(data: bytes) -> Optional[Dict[str, Any]]:
        if len(data) < 14:
            return None
        try:
            ethertype, length = struct.unpack_from('>HH', data, 0)
            if ethertype != ETHERTYPE_SV:
                return None
            sv_len = struct.unpack_from('>H', data, 4)[0]
            offset = 6
            sv_id = data[offset:offset+sv_len].decode('utf-8')
            offset += sv_len
            smp_cnt, v_a, i_a = struct.unpack_from('>Iff', data, offset)
            return {
                'ethertype': hex(ethertype),
                'sv_id': sv_id,
                'smp_cnt': smp_cnt,
                'v_a': v_a,
                'i_a': i_a
            }
        except Exception as e:
            LOGGER.debug('Error decodificando SV: %s', e)
            return None


class Iec61850Server:
    """Servidor IED Subestación IEC 61850 con emisión GOOSE & SV y recepción de comandos."""

    def __init__(self, host: str = '127.0.0.1', goose_port: int = DEFAULT_GOOSE_PORT, sv_port: int = DEFAULT_SV_PORT) -> None:
        self.host = host
        self.goose_port = goose_port
        self.sv_port = sv_port
        self.dataset = IEC61850DataSet()
        self._running = False
        self._goose_sock: Optional[socket.socket] = None
        self._sv_sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._listen_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._goose_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._goose_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._listen_sock.bind((self.host, self.goose_port))
        except OSError:
            pass
            
        self._sv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._sv_sock.bind((self.host, self.sv_port))
        except OSError:
            pass
        self._running = True
        self._thread = threading.Thread(target=self._publish_loop, daemon=True)
        self._thread.start()
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()
        LOGGER.info('[IEC61850] Servidor IED subestación activo en %s (GOOSE:%d, SV:%d)', self.host, self.goose_port, self.sv_port)

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=1.0)
        if self._goose_sock:
            self._goose_sock.close()
        if self._sv_sock:
            self._sv_sock.close()

    def publish_goose_event(self) -> bytes:
        """Publica un paquete GOOSE inmediatamente."""
        state = self.dataset.get_state()
        breaker_pos = state['data']['XCBR1.Pos.stVal']
        pdu = Iec61850GooseEncoder.encode(
            f"{state['ied_name']}/LLN0$GO$gcb01",
            f"{state['ied_name']}/LLN0$ds01",
            state['st_num'],
            state['sq_num'],
            breaker_pos
        )
        if self._goose_sock:
            try:
                self._goose_sock.sendto(pdu, ('127.0.0.1', self.goose_port))
            except OSError:
                pass
        return pdu

    def publish_sv_sample(self) -> bytes:
        """Publica una muestra SV de voltaje y corriente."""
        state = self.dataset.get_state()
        v_a = float(state['data']['MMXU1.PhV.phsA.cVal.mag'])
        i_a = float(state['data']['MMXU1.Amp.phsA.cVal.mag'])
        smp_cnt = self.dataset.increment_seq()
        pdu = Iec61850SvEncoder.encode(
            f"{state['ied_name']}/LLN0$SV$sv01",
            smp_cnt,
            v_a,
            i_a
        )
        if self._sv_sock:
            try:
                self._sv_sock.sendto(pdu, ('127.0.0.1', self.sv_port))
            except OSError:
                pass
        return pdu

    def _listen_loop(self) -> None:
        """Hilo receptor de mensajes GOOSE entrantes en la subestación."""
        if not hasattr(self, '_listen_sock') or not self._listen_sock:
            return
        self._listen_sock.settimeout(0.5)
        while self._running:
            try:
                data, addr = self._listen_sock.recvfrom(2048)
                if not data:
                    continue
                decoded = Iec61850GooseEncoder.decode(data)
                if decoded and 'breaker_pos' in decoded:
                    new_pos = decoded['breaker_pos']
                    st_num = decoded.get('st_num', 0)
                    self.dataset.set('XCBR1.Pos.stVal', new_pos)
                    LOGGER.warning('[IEC61850] ¡Mensaje GOOSE recibido de %s! XCBR1.Pos.stVal=%s (stNum=%d)',
                                   addr[0], new_pos, st_num)
            except socket.timeout:
                continue
            except Exception as e:
                LOGGER.debug('[IEC61850] Excepción en receiver loop GOOSE: %s', e)

    def _publish_loop(self) -> None:
        while self._running:
            self.publish_goose_event()
            self.publish_sv_sample()
            time.sleep(0.5)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Emulador IED Subestación IEC 61850 GOOSE/SV")
    default_host = os.getenv("IEC61850_HOST", os.getenv("BIND_HOST", "0.0.0.0"))
    parser.add_argument("--host", default=default_host, help=f"Dirección IP de bind (default: {default_host})")
    parser.add_argument("--goose-port", type=int, default=DEFAULT_GOOSE_PORT, help="Puerto GOOSE UDP (default: 10102)")
    parser.add_argument("--sv-port", type=int, default=DEFAULT_SV_PORT, help="Puerto SV UDP (default: 10103)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='[%(levelname)s][%(name)s] %(message)s')

    server = Iec61850Server(host=args.host, goose_port=args.goose_port, sv_port=args.sv_port)
    server.start()
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        server.stop()


if __name__ == '__main__':
    main()
