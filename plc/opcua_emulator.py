#!/usr/bin/env python3
"""plc/opcua_emulator.py — Emulador de servidor OPC UA sobre TCP (Fase 3)

Implementación mínima del protocolo OPC UA (UA Binary Transport Layer)
suficiente para:
  - Ser detectable como servidor OPC UA en escaneos de red.
  - Responder a Hello/Acknowledge handshake (OpenSecureChannel).
  - Exponer nodos de telemetría OT en un espacio de direcciones (NodeSpace).
  - Retornar valores de proceso (presión, temperatura, estado actuador).
  - Ser atacado en ejercicios CTF (sin autenticación, endpoint anónimo — F-05 análogo).

Puerto por defecto: 4840 (puerto estándar OPC UA TCP).

Scope pedagógico:
  Emula OPC UA Binary Protocol v1.04 (UA/TCP) con las siguientes restricciones
  de diseño pedagógico (RF-11):
  - Sin seguridad de mensaje (SecurityMode=None). Permite sniffing de sesión.
  - Endpoint anónimo sin autenticación de usuario. Permite inyección sin credenciales.
  - Sin firma ni cifrado de payload. Permite MITM a nivel OPC UA.

Integración:
  - Se integra en la topología Mininet como host `h_plc_proc` en zona OT (10.0.3.20).
  - Las lecturas de nodo son consumidas por el SCADA vía OPC UA en vez de Modbus/TCP.
  - Compatible con gridlabd_federate.py para actualizar valores desde HELICS.

Nota de fidelidad:
  Una implementación completa usaría `asyncua` (Python OPC UA async) o `opcua-asyncio`.
  Este emulador replica el comportamiento observable en red sin esa dependencia.
  Para reemplazarlo por una stack real: $ pip install asyncua
  y sustituir esta clase por asyncua.Server con el mismo espacio de nodos.
"""
from __future__ import annotations

import logging
import socket
import struct
import threading
import time
from typing import Any, Dict, Optional

LOGGER = logging.getLogger('opcua_emulator')

# ------------------------------------------------------------------ #
#  Constantes OPC UA Binary Protocol (UA/TCP)                         #
# ------------------------------------------------------------------ #

# Tipos de mensajes UA/TCP Header (4-byte magic code)
MSG_HELLO    = b'HEL'
MSG_ACK      = b'ACK'
MSG_ERROR    = b'ERR'
MSG_OPEN     = b'OPN'
MSG_CLOSE    = b'CLO'
MSG_MSG      = b'MSG'

# Opcodes de servicio OPC UA (RequestTypeId simplificado)
SVC_GET_ENDPOINTS_REQ  = 0x01
SVC_CREATE_SESSION_REQ = 0x02
SVC_READ_REQ           = 0x03
SVC_BROWSE_REQ         = 0x04

# Puerto OPC UA estándar
OPCUA_DEFAULT_PORT = 4840

# ------------------------------------------------------------------ #
#  Espacio de nodos (NodeSpace) — telemetría de proceso OT            #
# ------------------------------------------------------------------ #

# Cada nodo: NodeId -> (dataType, valor_inicial, descripción)
_DEFAULT_NODES: Dict[int, Dict[str, Any]] = {
    # Sector Agua (SWaT)
    1001: {'name': 'WaterTank_Level',    'type': 'Float',   'value': 75.0,  'unit': '%',   'sector': 'water'},
    1002: {'name': 'WaterPump_State',    'type': 'Boolean', 'value': True,  'unit': '',    'sector': 'water'},
    1003: {'name': 'InletValve_Open',    'type': 'Boolean', 'value': True,  'unit': '',    'sector': 'water'},
    1004: {'name': 'WaterPressure_Bar',  'type': 'Float',   'value': 3.2,   'unit': 'bar', 'sector': 'water'},
    # Sector Gas
    2001: {'name': 'GasPressure_PSI',    'type': 'Float',   'value': 145.0, 'unit': 'PSI', 'sector': 'gas'},
    2002: {'name': 'GasValve_State',     'type': 'Boolean', 'value': True,  'unit': '',    'sector': 'gas'},
    2003: {'name': 'GasFlowRate_m3h',   'type': 'Float',   'value': 22.5,  'unit': 'm3/h','sector': 'gas'},
    # Sector Eléctrico
    3001: {'name': 'Breaker_Main_State', 'type': 'Boolean', 'value': True,  'unit': '',    'sector': 'elec'},
    3002: {'name': 'Grid_Voltage_V',     'type': 'Float',   'value': 230.0, 'unit': 'V',   'sector': 'elec'},
    3003: {'name': 'Grid_FreqHz',        'type': 'Float',   'value': 60.0,  'unit': 'Hz',  'sector': 'elec'},
    # Sector Transporte
    4001: {'name': 'Traffic_Light_State','type': 'Int32',   'value': 2,     'unit': '',    'sector': 'transport'},
    4002: {'name': 'Railway_Gate_Open',  'type': 'Boolean', 'value': True,  'unit': '',    'sector': 'transport'},
}


class OpcUaNodeSpace:
    """Espacio de nodos OPC UA en memoria. Thread-safe."""

    def __init__(self) -> None:
        self._nodes: Dict[int, Dict[str, Any]] = {
            nid: dict(node) for nid, node in _DEFAULT_NODES.items()
        }
        self._lock = threading.Lock()

    def read(self, node_id: int) -> Optional[Dict[str, Any]]:
        """Lee el valor actual de un nodo."""
        with self._lock:
            node = self._nodes.get(node_id)
            if node is None:
                return None
            return {'node_id': node_id, 'value': node['value'],
                    'name': node['name'], 'type': node['type'],
                    'unit': node['unit'], 'timestamp': time.time()}

    def write(self, node_id: int, value: Any) -> bool:
        """Escribe el valor de un nodo. Retorna True si el nodo existe."""
        with self._lock:
            if node_id not in self._nodes:
                return False
            self._nodes[node_id]['value'] = value
            return True

    def browse(self) -> list:
        """Lista todos los nodos disponibles."""
        with self._lock:
            return [
                {'node_id': nid, 'name': n['name'], 'type': n['type'],
                 'sector': n['sector'], 'unit': n['unit']}
                for nid, n in self._nodes.items()
            ]

    def all_values(self) -> Dict[str, Any]:
        """Retorna snapshot completo del espacio de nodos por sector."""
        result: Dict[str, Any] = {}
        with self._lock:
            for node in self._nodes.values():
                sector = node['sector']
                result.setdefault(sector, {})[node['name']] = node['value']
        return result


# ------------------------------------------------------------------ #
#  Servidor OPC UA binario (UA/TCP stub)                              #
# ------------------------------------------------------------------ #

class OpcUaServer:
    """Servidor TCP que emula el protocolo UA/TCP de OPC UA.

    Suficiente para fingerprinting de red, handshake observable y lecturas
    de telemetría OT en ejercicios CTF y pruebas de integración.
    """

    def __init__(
        self,
        host: str = '0.0.0.0',
        port: int = OPCUA_DEFAULT_PORT,
        node_space: Optional[OpcUaNodeSpace] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.nodes = node_space or OpcUaNodeSpace()
        self._sock: Optional[socket.socket] = None
        self._running = False

    def start(self) -> None:
        """Arranca el servidor. Bloqueante — llamar desde un hilo."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(10)
        self._running = True
        LOGGER.info('[OPC UA] Servidor escuchando en %s:%d (SecurityMode=None)', self.host, self.port)
        while self._running:
            try:
                self._sock.settimeout(1.0)
                conn, addr = self._sock.accept()
                LOGGER.info('[OPC UA] Conexión entrante desde %s:%d', *addr)
                t = threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except OSError:
                break

    def stop(self) -> None:
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass

    # ---------------------------------------------------------------- #
    #  Manejo de cliente                                                 #
    # ---------------------------------------------------------------- #

    def _handle_client(self, conn: socket.socket, addr: tuple) -> None:
        """Maneja una conexión de cliente OPC UA."""
        try:
            conn.settimeout(5.0)
            while self._running:
                # Leer header UA/TCP: 3 bytes tipo + 1 byte 'F' (final chunk) + 4 bytes length
                header = self._recv_exactly(conn, 8)
                if not header:
                    break
                msg_type = header[:3]
                msg_len = struct.unpack_from('<I', header, 4)[0]
                body = self._recv_exactly(conn, msg_len - 8)
                if body is None:
                    break

                if msg_type == MSG_HELLO:
                    self._handle_hello(conn, body)
                elif msg_type == MSG_OPEN:
                    self._handle_open_channel(conn, body)
                elif msg_type == MSG_MSG:
                    self._handle_message(conn, body)
                elif msg_type == MSG_CLOSE:
                    LOGGER.info('[OPC UA] CloseSecureChannel desde %s:%d', *addr)
                    break
                else:
                    LOGGER.warning('[OPC UA] Tipo de mensaje desconocido: %r', msg_type)
                    break
        except (socket.timeout, ConnectionResetError, OSError):
            pass
        finally:
            conn.close()
            LOGGER.info('[OPC UA] Conexión cerrada desde %s:%d', *addr)

    def _recv_exactly(self, conn: socket.socket, n: int) -> Optional[bytes]:
        """Lee exactamente n bytes del socket."""
        data = b''
        while len(data) < n:
            try:
                chunk = conn.recv(n - len(data))
            except (socket.timeout, OSError):
                return None
            if not chunk:
                return None
            data += chunk
        return data

    def _send_msg(self, conn: socket.socket, msg_type: bytes, body: bytes) -> None:
        """Envía un mensaje UA/TCP."""
        length = 8 + len(body)
        header = msg_type + b'F' + struct.pack('<I', length)
        conn.sendall(header + body)

    def _handle_hello(self, conn: socket.socket, body: bytes) -> None:
        """Responde a HEL con ACK — primer paso del handshake UA/TCP."""
        # ACK: ProtocolVersion(4) + ReceiveBufferSize(4) + SendBufferSize(4) +
        #      MaxMessageSize(4) + MaxChunkCount(4) = 20 bytes
        protocol_version = struct.pack('<I', 0)
        recv_buffer  = struct.pack('<I', 65536)
        send_buffer  = struct.pack('<I', 65536)
        max_msg_size = struct.pack('<I', 0)
        max_chunks   = struct.pack('<I', 0)
        ack_body = protocol_version + recv_buffer + send_buffer + max_msg_size + max_chunks
        self._send_msg(conn, MSG_ACK, ack_body)
        LOGGER.debug('[OPC UA] HEL→ACK enviado')

    def _handle_open_channel(self, conn: socket.socket, body: bytes) -> None:
        """Maneja OpenSecureChannel con SecurityMode=None."""
        # Respuesta mínima: SecurityChannelId + TokenId + RevisedLifetime
        # En producción: negociaría claves, firmaría, etc.
        channel_id    = struct.pack('<I', 1001)
        token_id      = struct.pack('<I', 2001)
        revised_life  = struct.pack('<I', 600000)  # 10 minutos en ms
        opn_body = channel_id + token_id + revised_life
        self._send_msg(conn, MSG_OPEN, opn_body)
        LOGGER.debug('[OPC UA] OpenSecureChannel respondido (SecurityMode=None)')

    def _handle_message(self, conn: socket.socket, body: bytes) -> None:
        """Despacha servicios OPC UA: Read, Browse, GetEndpoints."""
        if len(body) < 1:
            return
        svc_code = body[0]

        if svc_code == SVC_GET_ENDPOINTS_REQ:
            self._svc_get_endpoints(conn)
        elif svc_code == SVC_READ_REQ:
            # Extraer NodeId del payload (offset 1, 4 bytes little-endian)
            if len(body) >= 5:
                node_id = struct.unpack_from('<I', body, 1)[0]
                self._svc_read(conn, node_id)
        elif svc_code == SVC_BROWSE_REQ:
            self._svc_browse(conn)
        else:
            LOGGER.debug('[OPC UA] Servicio desconocido: 0x%02x', svc_code)
            # Respuesta de error de servicio OPC UA (StatusCode Bad_ServiceUnsupported)
            self._send_msg(conn, MSG_MSG, struct.pack('<I', 0x803B0000))

    def _svc_get_endpoints(self, conn: socket.socket) -> None:
        """Retorna la lista de endpoints disponibles."""
        # Endpoint mínimo: URL + SecurityMode=None + AnonymousToken
        endpoint_url = b'opc.tcp://citylab-plc:4840'
        url_len = struct.pack('<I', len(endpoint_url))
        security_mode = struct.pack('<I', 1)  # None = 1
        response = b'\x00' + url_len + endpoint_url + security_mode
        self._send_msg(conn, MSG_MSG, response)

    def _svc_read(self, conn: socket.socket, node_id: int) -> None:
        """Lee el valor de un nodo del espacio OPC UA."""
        node = self.nodes.read(node_id)
        if node is None:
            # StatusCode Bad_NodeIdUnknown = 0x80340000
            self._send_msg(conn, MSG_MSG, struct.pack('<I', 0x80340000))
            return

        value = node['value']
        data_type = node['type']
        LOGGER.debug('[OPC UA] Read NodeId=%d Name=%s Value=%s', node_id, node['name'], value)

        # Serialización mínima: TypeCode(1) + Value
        if data_type == 'Float':
            payload = b'\x0A' + struct.pack('<f', float(value))
        elif data_type == 'Boolean':
            payload = b'\x01' + (b'\x01' if value else b'\x00')
        elif data_type == 'Int32':
            payload = b'\x06' + struct.pack('<i', int(value))
        else:
            payload = b'\x0C' + str(value).encode('utf-8')  # String fallback

        response = b'\x00' + struct.pack('<I', node_id) + payload
        self._send_msg(conn, MSG_MSG, response)

    def _svc_browse(self, conn: socket.socket) -> None:
        """Lista todos los nodos del espacio OPC UA."""
        nodes = self.nodes.browse()
        count = struct.pack('<I', len(nodes))
        node_data = b''
        for n in nodes:
            name_bytes = n['name'].encode('utf-8')
            node_data += struct.pack('<I', n['node_id'])
            node_data += struct.pack('<H', len(name_bytes)) + name_bytes
        response = b'\x00' + count + node_data
        self._send_msg(conn, MSG_MSG, response)


# ------------------------------------------------------------------ #
#  Cliente OPC UA mínimo (para tests)                                 #
# ------------------------------------------------------------------ #

class OpcUaClient:
    """Cliente OPC UA TCP mínimo para pruebas de integración.

    Replica exactamente el protocolo implementado en OpcUaServer para
    permitir tests de integración sin dependencias externas.
    """

    def __init__(self, host: str = '127.0.0.1', port: int = OPCUA_DEFAULT_PORT) -> None:
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None

    def connect(self, timeout: float = 3.0) -> bool:
        """Establece conexión y realiza handshake HEL/ACK + OpenSecureChannel."""
        try:
            self._sock = socket.create_connection((self.host, self.port), timeout=timeout)
            self._sock.settimeout(timeout)
            # Enviar HEL
            hel_body = struct.pack('<IIIII', 0, 65536, 65536, 0, 0)
            self._send_msg(MSG_HELLO, hel_body)
            # Esperar ACK
            resp = self._recv_msg()
            if not resp or resp[0] != MSG_ACK:
                return False
            # OpenSecureChannel (vacío — el servidor responde con SecurityMode=None)
            self._send_msg(MSG_OPEN, b'\x00' * 4)
            resp = self._recv_msg()
            if not resp or resp[0] != MSG_OPEN:
                return False
            return True
        except (socket.error, OSError):
            return False

    def read_node(self, node_id: int) -> Optional[Any]:
        """Lee el valor de un nodo OPC UA."""
        if not self._sock:
            return None
        body = bytes([SVC_READ_REQ]) + struct.pack('<I', node_id)
        self._send_msg(MSG_MSG, body)
        resp = self._recv_msg()
        if not resp or resp[0] != MSG_MSG or not resp[1]:
            return None
        data = resp[1]
        if len(data) < 6 or data[0] != 0:
            return None
        # Skip: status(1) + node_id(4) = offset 5, type_code(1), value
        if len(data) < 6:
            return None
        type_code = data[5]
        payload = data[6:]
        if type_code == 0x0A and len(payload) >= 4:   # Float
            return struct.unpack_from('<f', payload)[0]
        elif type_code == 0x01 and len(payload) >= 1:  # Boolean
            return bool(payload[0])
        elif type_code == 0x06 and len(payload) >= 4:  # Int32
            return struct.unpack_from('<i', payload)[0]
        return None

    def browse(self) -> list:
        """Lista nodos disponibles en el servidor."""
        if not self._sock:
            return []
        self._send_msg(MSG_MSG, bytes([SVC_BROWSE_REQ]))
        resp = self._recv_msg()
        if not resp or resp[0] != MSG_MSG or not resp[1]:
            return []
        data = resp[1]
        if len(data) < 5 or data[0] != 0:
            return []
        count = struct.unpack_from('<I', data, 1)[0]
        return list(range(count))  # Retorna conteo de nodos como lista

    def get_endpoints(self) -> bool:
        """Consulta los endpoints disponibles (GetEndpoints)."""
        if not self._sock:
            return False
        self._send_msg(MSG_MSG, bytes([SVC_GET_ENDPOINTS_REQ]))
        resp = self._recv_msg()
        return resp is not None and resp[0] == MSG_MSG

    def close(self) -> None:
        if self._sock:
            try:
                self._send_msg(MSG_CLOSE, b'')
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def _send_msg(self, msg_type: bytes, body: bytes) -> None:
        length = 8 + len(body)
        header = msg_type + b'F' + struct.pack('<I', length)
        self._sock.sendall(header + body)  # type: ignore[union-attr]

    def _recv_msg(self) -> Optional[tuple]:
        """Recibe un mensaje UA/TCP. Retorna (tipo, body) o None."""
        header = self._recv_exactly(8)
        if not header:
            return None
        msg_type = header[:3]
        length = struct.unpack_from('<I', header, 4)[0]
        body = self._recv_exactly(length - 8)
        return (msg_type, body)

    def _recv_exactly(self, n: int) -> Optional[bytes]:
        data = b''
        while len(data) < n:
            try:
                chunk = self._sock.recv(n - len(data))  # type: ignore[union-attr]
            except (socket.timeout, OSError):
                return None
            if not chunk:
                return None
            data += chunk
        return data


def main() -> int:
    """Punto de entrada standalone del emulador OPC UA."""
    import os
    host = os.getenv('OPCUA_HOST', '10.0.3.20')
    port = int(os.getenv('OPCUA_PORT', str(OPCUA_DEFAULT_PORT)))
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][OPC_UA] %(message)s')
    server = OpcUaServer(host=host, port=port)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
