#!/usr/bin/env python3
"""Tests de integración para el emulador OPC UA — Fase 3.

Valida:
  - Handshake UA/TCP: HEL → ACK → OpenSecureChannel.
  - Lectura de nodos individuales (Float, Boolean, Int32).
  - Browse del espacio de nodos.
  - GetEndpoints.
  - Escritura de valores y lectura posterior.
  - Snapshot completo por sector.
  - Ausencia de autenticación (SecurityMode=None, endpoint anónimo — CTF F-05 análogo).
"""
from __future__ import annotations

import struct
import threading
import time
import unittest

from plc.opcua_emulator import (
    OpcUaServer, OpcUaClient, OpcUaNodeSpace,
    OPCUA_DEFAULT_PORT, MSG_HELLO, MSG_ACK, MSG_OPEN, MSG_MSG,
)


class TestOpcUaNodeSpace(unittest.TestCase):
    """Tests unitarios del espacio de nodos OpcUaNodeSpace."""

    def setUp(self) -> None:
        self.ns = OpcUaNodeSpace()

    def test_read_existing_node(self) -> None:
        """read() retorna datos correctos para un nodo existente."""
        node = self.ns.read(1001)
        self.assertIsNotNone(node)
        self.assertEqual(node['name'], 'WaterTank_Level')
        self.assertEqual(node['type'], 'Float')
        self.assertAlmostEqual(node['value'], 75.0, places=1)

    def test_read_nonexistent_node_returns_none(self) -> None:
        """read() retorna None para un NodeId desconocido."""
        result = self.ns.read(9999)
        self.assertIsNone(result)

    def test_write_and_read_back(self) -> None:
        """write() actualiza el valor y read() lo refleja."""
        ok = self.ns.write(1004, 4.5)
        self.assertTrue(ok)
        node = self.ns.read(1004)
        self.assertAlmostEqual(node['value'], 4.5, places=2)

    def test_write_nonexistent_returns_false(self) -> None:
        """write() retorna False para NodeId desconocido."""
        ok = self.ns.write(9999, 42.0)
        self.assertFalse(ok)

    def test_browse_returns_all_nodes(self) -> None:
        """browse() lista todos los nodos del espacio."""
        nodes = self.ns.browse()
        self.assertGreater(len(nodes), 0)
        names = [n['name'] for n in nodes]
        self.assertIn('WaterTank_Level', names)
        self.assertIn('GasPressure_PSI', names)
        self.assertIn('Breaker_Main_State', names)

    def test_all_values_grouped_by_sector(self) -> None:
        """all_values() agrupa datos por sector correctamente."""
        snapshot = self.ns.all_values()
        self.assertIn('water', snapshot)
        self.assertIn('gas', snapshot)
        self.assertIn('elec', snapshot)
        self.assertIn('transport', snapshot)
        self.assertIn('WaterTank_Level', snapshot['water'])


class TestOpcUaServerClient(unittest.TestCase):
    """Tests de integración del servidor y cliente OPC UA."""

    _server_port = 14840

    @classmethod
    def setUpClass(cls) -> None:
        cls.node_space = OpcUaNodeSpace()
        cls.server = OpcUaServer(host='127.0.0.1', port=cls._server_port,
                                 node_space=cls.node_space)
        cls.server_thread = threading.Thread(target=cls.server.start, daemon=True)
        cls.server_thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.stop()

    def _make_client(self) -> OpcUaClient:
        """Crea y conecta un cliente para el test."""
        client = OpcUaClient(host='127.0.0.1', port=self._server_port)
        self.assertTrue(client.connect(timeout=3.0), "Cliente OPC UA debe conectar y completar handshake")
        return client

    def test_handshake_hello_ack(self) -> None:
        """El servidor responde ACK al HEL correctamente (UA/TCP handshake)."""
        client = self._make_client()
        # Si connect() retorna True, el handshake HEL→ACK+OPN fue exitoso
        self.assertIsNotNone(client._sock)
        client.close()

    def test_read_float_node(self) -> None:
        """Lectura de nodo Float (WaterTank_Level, NodeId=1001) retorna valor numérico."""
        client = self._make_client()
        value = client.read_node(1001)
        client.close()
        self.assertIsNotNone(value, "Debe retornar un valor Float")
        self.assertAlmostEqual(value, 75.0, places=0)

    def test_read_boolean_node(self) -> None:
        """Lectura de nodo Boolean (WaterPump_State, NodeId=1002)."""
        client = self._make_client()
        value = client.read_node(1002)
        client.close()
        self.assertIsNotNone(value)
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_read_int32_node(self) -> None:
        """Lectura de nodo Int32 (Traffic_Light_State, NodeId=4001)."""
        client = self._make_client()
        value = client.read_node(4001)
        client.close()
        self.assertIsNotNone(value)
        self.assertIsInstance(value, int)

    def test_read_unknown_node_returns_none(self) -> None:
        """Lectura de NodeId desconocido retorna None (BadNodeIdUnknown)."""
        client = self._make_client()
        value = client.read_node(9999)
        client.close()
        self.assertIsNone(value)

    def test_write_and_read_back_via_client(self) -> None:
        """Escritura directa al NodeSpace y lectura confirmada vía cliente."""
        # Escribir nuevo valor directamente al NodeSpace (como haría HELICS federate)
        self.node_space.write(1004, 5.5)
        client = self._make_client()
        value = client.read_node(1004)
        client.close()
        self.assertIsNotNone(value)
        self.assertAlmostEqual(value, 5.5, places=1)

    def test_browse_returns_node_count(self) -> None:
        """Browse retorna lista con conteo correcto de nodos."""
        client = self._make_client()
        nodes = client.browse()
        client.close()
        self.assertGreater(len(nodes), 0)

    def test_get_endpoints_succeeds(self) -> None:
        """GetEndpoints responde con 200 de servicio (SecurityMode=None)."""
        client = self._make_client()
        ok = client.get_endpoints()
        client.close()
        self.assertTrue(ok)

    def test_no_auth_required_ctf(self) -> None:
        """Conexión exitosa sin credenciales — endpoint anónimo CTF (F-05 análogo)."""
        # Si connect() tiene éxito sin usuario/contraseña, el endpoint es anónimo
        client = OpcUaClient(host='127.0.0.1', port=self._server_port)
        connected = client.connect(timeout=3.0)
        client.close()
        self.assertTrue(connected, "Servidor OPC UA debe aceptar conexiones anónimas (CTF diseño pedagógico)")

    def test_multiple_concurrent_clients(self) -> None:
        """El servidor maneja múltiples clientes concurrentes correctamente."""
        results = []

        def read_client():
            c = OpcUaClient(host='127.0.0.1', port=self._server_port)
            if c.connect(timeout=3.0):
                v = c.read_node(1001)
                results.append(v)
                c.close()

        threads = [threading.Thread(target=read_client) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        self.assertEqual(len(results), 3, "Los 3 clientes concurrentes deben conectar y leer")
        for v in results:
            self.assertIsNotNone(v)


if __name__ == '__main__':
    unittest.main()
