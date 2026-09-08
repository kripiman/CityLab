from __future__ import annotations

import argparse
import json
import logging
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.rbac import RBACResolver

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][INSIDER-ATTACK] %(message)s')
LOGGER = logging.getLogger('attack_insider_rbac')


class InsiderRbacAttack:

    def __init__(self) -> None:
        self.resolver = RBACResolver()

    def execute_unauthorized_write_attempt(self, scada_url: str | None = None) -> Dict[str, Any]:
        LOGGER.info("Iniciando intencion de escritura no autorizada usando credencial de auditor...")
        auditor_hdr = "Bearer auditor:AUDIT_TOKEN_2026"
        role, status_code = self.resolver.resolve(auditor_hdr)
        
        # Verificar autorización interna para endpoint de escritura
        authorized = self.resolver.is_authorized(role, '/api/control/write')
        LOGGER.info("Rol resuelto: %s | Permiso interno para /api/control/write: %s", role, authorized)
        
        mode = 'ENGINE_DIRECT'
        http_code = status_code
        if scada_url:
            try:
                payload = json.dumps({'action': 'write_coil', 'target': 'water_pump_1'}).encode('utf-8')
                req = urllib.request.Request(
                    f"{scada_url}/api/control/write",
                    data=payload,
                    headers={'Authorization': auditor_hdr, 'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    http_code = resp.status
                    mode = 'SOCKET_LIVE'
            except urllib.error.HTTPError as e:
                http_code = e.code
                mode = 'SOCKET_LIVE'
            except Exception as e:
                LOGGER.debug("Petición HTTP a SCADA Server omitida: %s", e)
                mode = 'TABLETOP_FALLBACK'

        return {
            'status': 'SUCCESS',
            'mode': mode,
            'role': role,
            'access_granted': authorized and http_code == 200,
            'blocked_by_rbac': not authorized or http_code == 403,
            'http_status': http_code,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Insider RBAC Attack Vector")
    parser.add_argument('--scada-url', default='', help='SCADA HTTP URL')
    args = parser.parse_args(argv)

    attacker = InsiderRbacAttack()
    res = attacker.execute_unauthorized_write_attempt(scada_url=args.scada_url or None)
    LOGGER.info("Resultado de prueba Insider RBAC: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
