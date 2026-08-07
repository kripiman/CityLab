#!/usr/bin/env python3
"""Active Directory Domain Controller (Samba AD DC Emulator) — Corporate Zone DC para CityLab.

Servicio emulado de Domain Controller `h_dc.citylab.local` @ 10.0.1.20.
Proporciona puertos estándar de infraestructura Active Directory:
  - LDAP (:389 TCP): Enumeración de usuarios, grupos y SPNs (Service Principal Names).
  - Kerberos (:88 TCP): Autenticación Kerberos (Soporta AS-REP Roasting & Kerberoasting).
  - SMB (:445 TCP): Recursos compartidos del dominio (SYSVOL, NETLOGON, GPO).

Cuentas de Dominio Emuladas:
  - Administrator (Domain Admin, SPN: LDAP/h_dc.citylab.local)
  - jdoe_eng (Ingeniero OT, AS-REP Roastable - DONT_REQ_PREAUTH habilitado)
  - krbe_ews (Cuenta de servicio EWS, SPN: HTTP/h_ews.citylab.local, Kerberoastable)
  - plc_operator (Operador SCADA)

Uso:
  python3 network/ad_dc_emulator.py --host 0.0.0.0
"""
from __future__ import annotations

import argparse
import logging
import socket
import threading
import time
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='[%(levelname)s][Samba-AD-DC] %(message)s')
LOGGER = logging.getLogger('ad_dc_emulator')

# Hashes Kerberos de demostración (formato Hashcat / John The Ripper para laboratorios CTF)
KERBEROAST_TGS_HASH = (
    "$krb5tgs$23$*krbe_ews$CITYLAB.LOCAL$HTTP/h_ews.citylab.local*"
    "a1b2c3d4e5f60718293a4b5c6d7e8f90$11223344556677889900aabbccddeeff"
)
ASREP_ROAST_HASH = (
    "$krb5asrep$23$jdoe_eng@CITYLAB.LOCAL:99887766554433221100aabbccddeeff$"
    "fedcba98765432100123456789abcdef0123456789abcdef"
)


class LdapServerThread(threading.Thread):
    """Escuchador LDAP en puerto 389."""

    def __init__(self, host: str, port: int = 389) -> None:
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.running = True

    def run(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
            sock.listen(5)
            LOGGER.info("LDAP AD Server escuchando en %s:%d (DC: h_dc.citylab.local)", self.host, self.port)
            while self.running:
                sock.settimeout(1.0)
                try:
                    conn, addr = sock.accept()
                    LOGGER.info("Conexión LDAP recibida desde %s", addr)
                    t = threading.Thread(target=self._handle_ldap, args=(conn,), daemon=True)
                    t.start()
                except socket.timeout:
                    continue
        except Exception as exc:
            LOGGER.error("Falló inicio de servidor LDAP: %s", exc)
        finally:
            sock.close()

    def _handle_ldap(self, conn: socket.socket) -> None:
        with conn:
            conn.settimeout(2.0)
            try:
                data = conn.recv(1024)
                if data:
                    # Respuesta básica LDAP SearchResultEntry / BindResponse (BER encoded representation)
                    ldap_resp = (
                        b'0\x84\x00\x00\x00.\x02\x01\x01c\x84\x00\x00\x00%'
                        b'\x0a\x01\x00\x04\x00\x04\x1aDC=citylab,DC=local LDAP OK'
                    )
                    conn.sendall(ldap_resp)
            except Exception:
                pass


class KerberosServerThread(threading.Thread):
    """Escuchador Kerberos KDC en puerto 88."""

    def __init__(self, host: str, port: int = 88) -> None:
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.running = True

    def run(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
            sock.listen(5)
            LOGGER.info("Kerberos KDC Server escuchando en %s:%d (Realm: CITYLAB.LOCAL)", self.host, self.port)
            while self.running:
                sock.settimeout(1.0)
                try:
                    conn, addr = sock.accept()
                    LOGGER.info("Petición Kerberos AS-REQ / TGS-REQ desde %s", addr)
                    t = threading.Thread(target=self._handle_kerberos, args=(conn,), daemon=True)
                    t.start()
                except socket.timeout:
                    continue
        except Exception as exc:
            LOGGER.error("Falló inicio KDC Kerberos: %s", exc)
        finally:
            sock.close()

    def _handle_kerberos(self, conn: socket.socket) -> None:
        with conn:
            conn.settimeout(2.0)
            try:
                data = conn.recv(2048)
                if data:
                    # Devuelve Ticket TGS / AS-REP para demostración de Kerberoasting
                    resp = (
                        b'\x76\x82\x01\x00'  # KDC AS-REP / TGS-REP ASN.1 tag
                        + KERBEROAST_TGS_HASH.encode('utf-8')
                    )
                    conn.sendall(resp)
            except Exception:
                pass


class SmbServerThread(threading.Thread):
    """Escuchador SMB v2/v3 en puerto 445."""

    def __init__(self, host: str, port: int = 445) -> None:
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.running = True

    def run(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
            sock.listen(5)
            LOGGER.info("SMB Domain Share Server escuchando en %s:%d (Shares: SYSVOL, NETLOGON)", self.host, self.port)
            while self.running:
                sock.settimeout(1.0)
                try:
                    conn, addr = sock.accept()
                    LOGGER.info("Conexión SMB recibida desde %s", addr)
                    t = threading.Thread(target=self._handle_smb, args=(conn,), daemon=True)
                    t.start()
                except socket.timeout:
                    continue
        except Exception as exc:
            LOGGER.error("Falló inicio de servidor SMB: %s", exc)
        finally:
            sock.close()

    def _handle_smb(self, conn: socket.socket) -> None:
        with conn:
            conn.settimeout(2.0)
            try:
                data = conn.recv(1024)
                if data:
                    # Respuesta de negociación SMB2 Header magic: \xfeSMB
                    smb_header = b'\xfeSMB\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00'
                    conn.sendall(smb_header)
            except Exception:
                pass


class DomainControllerEmulator:
    """Orquestador completo del controlador de dominio h_dc."""

    def __init__(self, host: str = '0.0.0.0') -> None:
        self.host = host
        self.ldap_thread = LdapServerThread(host, 389)
        self.kerberos_thread = KerberosServerThread(host, 88)
        self.smb_thread = SmbServerThread(host, 445)

    def start(self) -> None:
        LOGGER.info("Iniciando Samba Active Directory Domain Controller [h_dc.citylab.local]...")
        self.ldap_thread.start()
        self.kerberos_thread.start()
        self.smb_thread.start()

        while True:
            time.sleep(1.0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Emulador de Samba AD DC (h_dc.citylab.local)")
    parser.add_argument("--host", default="0.0.0.0", help="Host bind IP (default: 0.0.0.0)")
    args = parser.parse_args()

    dc = DomainControllerEmulator(args.host)
    try:
        dc.start()
    except KeyboardInterrupt:
        LOGGER.info("Deteniendo Domain Controller h_dc...")


if __name__ == "__main__":
    main()
