#!/usr/bin/env python3
"""plc/tests/_emulator_harness.py — Context managers para pruebas con emuladores OT en puertos altos."""
from __future__ import annotations

import contextlib
import threading
import time
from typing import Iterator, Any

from plc.iec61850_emulator import Iec61850Server
from plc.opcua_emulator import OpcUaServer, OpcUaNodeSpace
from plc.dnp3_emulator import Dnp3Server
from plc.modbus_emulator import build_server, ModbusServerContext


@contextlib.contextmanager
def running_iec61850_server(
    host: str = '127.0.0.1',
    goose_port: int = 15102,
    sv_port: int = 15103
) -> Iterator[Iec61850Server]:
    """Inicia un Iec61850Server en puerto alto y asegura stop() en finally."""
    server = Iec61850Server(host=host, goose_port=goose_port, sv_port=sv_port)
    server.start()
    time.sleep(0.05)
    try:
        yield server
    finally:
        server.stop()


@contextlib.contextmanager
def running_opcua_server(
    host: str = '127.0.0.1',
    port: int = 14840,
    node_space: OpcUaNodeSpace | None = None
) -> Iterator[OpcUaServer]:
    """Inicia un OpcUaServer en puerto alto y asegura stop() en finally."""
    ns = node_space or OpcUaNodeSpace()
    server = OpcUaServer(host=host, port=port, node_space=ns)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.1)
    try:
        yield server
    finally:
        server.stop()
        thread.join(timeout=1.0)


@contextlib.contextmanager
def running_dnp3_server(
    host: str = '127.0.0.1',
    port: int = 15200
) -> Iterator[Dnp3Server]:
    """Inicia un Dnp3Server en puerto alto y asegura stop() en finally."""
    server = Dnp3Server(host=host, port=port)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.1)
    try:
        yield server
    finally:
        server.stop()
        thread.join(timeout=1.0)


@contextlib.contextmanager
def running_modbus_server(
    host: str = '127.0.0.1',
    port: int = 15020,
    plant_type: str = 'water'
) -> Iterator[tuple[Any, ModbusServerContext]]:
    """Inicia un ModbusTcpServer en puerto alto y asegura shutdown/server_close en finally."""
    server, context, actuator, ntcip, bacnet = build_server(host, port, plant_type)
    actuator_thread = threading.Thread(target=actuator.loop, daemon=True)
    actuator_thread.start()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.08)
    try:
        yield server, context
    finally:
        try:
            server.shutdown()
            server.server_close()
        except Exception:
            pass
        actuator.stop()
        if ntcip:
            ntcip.stop()
        if bacnet:
            bacnet.stop()
        thread.join(timeout=1.0)


@contextlib.contextmanager
def running_bacnet_server(
    host: str = '127.0.0.1',
    port: int = 14780
) -> Iterator[Any]:
    """Inicia un BacnetListener en puerto alto y asegura stop() en finally."""
    from plc.modbus_emulator import BacnetListener
    listener = BacnetListener(host=host, port=port)
    listener.start()
    time.sleep(0.05)
    try:
        yield listener
    finally:
        listener.stop()


@contextlib.contextmanager
def running_ntcip_server(
    host: str = '127.0.0.1',
    port: int = 14161
) -> Iterator[Any]:
    """Inicia un NtcipListener en puerto alto y asegura stop() en finally."""
    from plc.modbus_emulator import NtcipListener
    listener = NtcipListener(host=host, port=port)
    listener.start()
    time.sleep(0.05)
    try:
        yield listener
    finally:
        listener.stop()


@contextlib.contextmanager
def running_ad_dc(
    host: str = '127.0.0.1',
    kerberos_port: int = 14088,
    ldap_port: int = 14389
) -> Iterator[Any]:
    """Inicia emulador AD DC con Kerberos y LDAP en puertos altos."""
    from network.ad_dc_emulator import KerberosServerThread, LdapServerThread
    krb_thread = KerberosServerThread(host=host, port=kerberos_port)
    ldap_thread = LdapServerThread(host=host, port=ldap_port)
    krb_thread.start()
    ldap_thread.start()
    time.sleep(0.08)
    try:
        yield krb_thread, ldap_thread
    finally:
        krb_thread.running = False
        ldap_thread.running = False

