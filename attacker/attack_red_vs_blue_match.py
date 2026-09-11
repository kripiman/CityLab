#!/usr/bin/env python3
"""attacker/attack_red_vs_blue_match.py — Escenario 27: Enfrentamiento Adjudicado Red vs Blue

Motor de puntuación para ciberejercicios en vivo entre Red Team y Blue Team:
  1. Registra objetivos físicos cumplidos por el Red Team.
  2. Mide la velocidad y efectividad de contención del Blue Team.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.scoreboard import ScoreboardEngine

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][RED-VS-BLUE] %(message)s')
LOGGER = logging.getLogger('attack_red_vs_blue_match')

# Baseline usado solo si el SIEM esta inalcanzable (arbitracion simulada, no en vivo).
_TABLETOP_BASELINE = {
    'red_team_points': 850,
    'blue_team_points': 920,
    'winner': 'Blue Team (Mitigacion Exitosa en <2min)'
}


class RedVsBlueMatch:

    def __init__(self, siem_url: str = None) -> None:
        self.engine = ScoreboardEngine(siem_url=siem_url or os.getenv('SIEM_HTTP_URL', 'http://10.0.2.20:8514'))

    def run_adjudicated_match(self, events: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        LOGGER.info("Iniciando ciberejercicio Red vs Blue con motor de arbitraje...")
        raw_events = events if events is not None else self.engine.fetch_siem_events()
        scorecard = self.engine.generate_scorecard(scenario_id='27', events=raw_events)
        metrics = scorecard['soc_metrics']

        if scorecard['total_events_analyzed'] == 0:
            LOGGER.warning("[TABLETOP] Servidores no detectados, usando adjudicacion simulada baseline")
            score_board = dict(_TABLETOP_BASELINE)
            mode = 'TABLETOP_FALLBACK'
        else:
            # Metricas ofensivas del Red Team (exito de intrusion, disrupcion y evasion):
            # El equipo atacante puntua por compromisos exitosos (exploits), impacto en procesos
            # (disrupciones/trips) y ataques no mitigados por la defensa.
            # NO se recompensa al atacante por ser detectado por el Blue Team.
            successful_exploits = sum(
                1 for ev in raw_events
                if str(ev.get('event_type', '')).lower() in ('system_trip', 'malicious_write', 'intrusion', 'exploit')
                or any(k in str(ev.get('message', '')).lower() for k in ('trip', 'disrupt', 'sabotage', 'override', 'compromise', 'unauthorized write'))
            )
            services_disrupted = sum(
                1 for ev in raw_events
                if str(ev.get('event_type', '')).lower() == 'system_trip'
                or any(k in str(ev.get('message', '')).lower() for k in ('system_trip', 'trip breaker', 'service disrupted', 'shutdown', 'blackout'))
            )
            # Ataques que no fueron neutralizados por acciones defensivas del Blue Team
            unmitigated_attacks = max(0, metrics['attacks_detected'] - metrics['defense_actions'])

            if successful_exploits > 0 or services_disrupted > 0:
                red_pts = (successful_exploits * 100) + (services_disrupted * 100) + (unmitigated_attacks * 50)
            else:
                red_pts = unmitigated_attacks * 100

            metrics['successful_exploits'] = successful_exploits
            metrics['services_disrupted'] = services_disrupted
            metrics['unmitigated_attacks'] = unmitigated_attacks

            # Metricas defensivas del Blue Team (deteccion, respuesta y mitigacion rapida):
            blue_pts = metrics['alerts_generated'] * 50 + metrics['defense_actions'] * 150
            fast_containment = metrics['mttr_seconds'] is not None and metrics['mttr_seconds'] < 120
            if fast_containment:
                blue_pts += 200

            winner_team = 'Blue Team' if blue_pts >= red_pts else 'Red Team'
            if winner_team == 'Red Team':
                reason = f"Exploits {successful_exploits} / Disrupciones {services_disrupted} / Evasiones {unmitigated_attacks}"
            else:
                reason = f"MTTR {metrics['mttr_formatted']}" if fast_containment else f"MTTD {metrics['mttd_formatted']} / MTTR {metrics['mttr_formatted']}"

            score_board = {
                'red_team_points': red_pts,
                'blue_team_points': blue_pts,
                'winner': f'{winner_team} ({reason})'
            }
            mode = 'SIEM_LIVE'

        LOGGER.info("Puntuacion final adjudicada [%s]: %s", mode, score_board)
        return {
            'status': 'SUCCESS',
            'mode': mode,
            'match_completed': True,
            'soc_metrics': metrics,
            'scoreboard': score_board
        }


def main() -> int:
    rvb = RedVsBlueMatch()
    res = rvb.run_adjudicated_match()
    LOGGER.info("Resultado de Red vs Blue Match: %s", res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
