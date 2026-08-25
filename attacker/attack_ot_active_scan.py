#!/usr/bin/env python3
"""attacker/attack_ot_active_scan.py — Escenario 14: Escaneo Activo de Red OT con Nmap / TCP Probes

Ejecuta escaneo activo controlado hacia objetivos OT:
  1. Realiza probes TCP connect (`socket.connect_ex`) con timeout corto.
  2. Mide la alcanzabilidad de puertos OT reales (Modbus 502, OPC UA 4840, DNP3 20000, etc.).
  3. Reporta puertos abiertos y cerrados observados empíricamente.
  4. Dispone de fallback documentado para modo tabletop / standalone sin red Mininet activa.
"""
from __future__ import annotations

import argparse
import logging
import socket
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][ACTIVE-SCAN] %(message)s')
LOGGER = logging.getLogger('attack_ot_active_scan')

# Objetivos por defecto en topología OT (zona 10.0.3.0/24)
DEFAULT_OT_TARGETS: List[Tuple[str, int]] = [
    ('10.0.3.10', 502),    # Water PLC (Modbus)
    ('10.0.3.12', 502),    # Gas PLC (Modbus)
    ('10.0.3.13', 502),    # Elec PLC (Modbus)
]


class OtActiveScan:
    """Escáner activo de servicios y puertos OT."""

    @staticmethod
    def scan_port(host: str, port: int, timeout: float = 0.2) -> bool:
        """Realiza un probe TCP connect a un endpoint host:port con timeout corto."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            res = sock.connect_ex((host, port))
            return res == 0
        except Exception:
            return False
        finally:
            sock.close()

    def run_active_scan(
        self,
        target_subnet: str = '10.0.3.0/24',
        targets: Optional[List[Tuple[str, int]]] = None,
        timeout: float = 0.2
    ) -> Dict[str, Any]:
        """Ejecuta el escaneo activo TCP sobre la lista de objetivos dada o los defaults."""
        scan_targets = targets if targets is not None else DEFAULT_OT_TARGETS
        LOGGER.info("Iniciando escaneo activo sobre subred %s (%d endpoints)...", target_subnet, len(scan_targets))

        open_ports: List[Tuple[str, int]] = []
        closed_ports: List[Tuple[str, int]] = []

        for host, port in scan_targets:
            is_open = self.scan_port(host, port, timeout=timeout)
            if is_open:
                open_ports.append((host, port))
                LOGGER.info("Puerto ABIERTO descubierto: %s:%d", host, port)
            else:
                closed_ports.append((host, port))
                LOGGER.debug("Puerto CERRADO / FILTRADO: %s:%d", host, port)

        # Si se especificaron targets explícitos o se descubrieron puertos vivos, reportar modo SOCKET_LIVE
        if targets is not None or len(open_ports) > 0:
            discovered_hosts = len({host for host, _ in open_ports})
            return {
                'status': 'SUCCESS',
                'mode': 'SOCKET_LIVE',
                'subnet': target_subnet,
                'hosts_scanned': len(scan_targets),
                'open_ports': open_ports,
                'closed_ports': closed_ports,
                'hosts_found': discovered_hosts
            }

        # Fallback documentado para modo tabletop si se ejecuta standalone sin emuladores ni Mininet
        LOGGER.warning("[TABLETOP-FALLBACK] Ningún host OT respondió al escaneo activo. Aplicando perfil simulado.")
        return {
            'status': 'SUCCESS',
            'mode': 'TABLETOP_FALLBACK',
            'subnet': target_subnet,
            'hosts_scanned': len(scan_targets),
            'open_ports': [],
            'closed_ports': scan_targets,
            'hosts_found': 0
        }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab OT Active Scan Vector")
    parser.add_argument("--subnet", default="10.0.3.0/24", help="Subred objetivo (default: 10.0.3.0/24)")
    parser.add_argument("--target", action="append", help="Target explícito en formato host:port (repetible)")
    parser.add_argument("--timeout", type=float, default=0.2, help="Timeout de conexión por puerto en segundos")
    args = parser.parse_args(argv)

    targets: Optional[List[Tuple[str, int]]] = None
    if args.target:
        targets = []
        for t in args.target:
            parts = t.split(':')
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 502
            targets.append((host, port))

    scan = OtActiveScan()
    res = scan.run_active_scan(target_subnet=args.subnet, targets=targets, timeout=args.timeout)
    LOGGER.info("Resultado de Escaneo Activo: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
