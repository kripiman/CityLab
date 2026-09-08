from __future__ import annotations

import argparse
import json
import logging
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.hmi_server import IndustrialHmiEngine

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][SCADA-TOUR] %(message)s')
LOGGER = logging.getLogger('attack_scada_tour')


class ScadaTour:

    def run_scada_exploration(
        self,
        hmi_url: Optional[str] = None,
        engine: Optional[IndustrialHmiEngine] = None,
    ) -> Dict[str, Any]:
        """Explora la API REST y estado HMI SCADA vía HTTP o motor directo."""
        LOGGER.info("Iniciando tour guiado por la API REST y HMI SCADA...")
        
        # Intentar consultar vía HTTP si se provee URL o por defecto
        target_url = hmi_url if hmi_url is not None else "http://127.0.0.1:8085"
        try:
            req = urllib.request.Request(f"{target_url}/api/hmi/overview")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode('utf-8'))
                    LOGGER.info("Respuesta HTTP /api/hmi/overview: %s", payload)
                    return {
                        'status': 'SUCCESS',
                        'mode': 'SOCKET_LIVE',
                        'target_url': target_url,
                        'overview_retrieved': True,
                        'system_health': payload.get('system_health', 'UNKNOWN'),
                        'active_alarms_count': payload.get('active_alarms_count', 0),
                        'sectors': list(payload.get('process_diagram', {}).keys()),
                    }
        except Exception as e:
            LOGGER.debug("Servidor HMI HTTP no alcanzable en %s (%s). Usando motor HMI local.", target_url, e)

        # Fallback a motor HMI industrial directo
        hmi_engine = engine if engine is not None else IndustrialHmiEngine()
        state = hmi_engine.get_overview()
        LOGGER.info("Respuesta de IndustrialHmiEngine overview: %s", state)

        return {
            'status': 'SUCCESS',
            'mode': 'ENGINE_DIRECT',
            'target_url': target_url,
            'overview_retrieved': True,
            'system_health': state.get('system_health', 'ALARM_CRITICAL'),
            'active_alarms_count': state.get('active_alarms_count', 0),
            'sectors': list(state.get('process_diagram', {}).keys()),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab SCADA HMI API Tour")
    parser.add_argument('--url', default='http://127.0.0.1:8085', help='Target HMI URL')
    args = parser.parse_args(argv)

    tour = ScadaTour()
    res = tour.run_scada_exploration(hmi_url=args.url)
    LOGGER.info("Resultado de Tour SCADA API: %s", res)
    return 0 if res['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
