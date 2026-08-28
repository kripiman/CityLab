#!/usr/bin/env python3
"""network/scoreboard.py — Scoreboard de Sesión y Métricas SOC Automatizadas (MTTD / MTTR) (Fase 4)

Calcula automáticamente métricas clave de operaciones de seguridad (SOC) y evaluación pedagógica:
  - MTTD (Mean Time to Detect): Tiempo desde el primer evento anómalo/ataque hasta la primera alerta correlacionada.
  - MTTR (Mean Time to Respond/Remediate): Tiempo desde la alerta hasta la acción defensiva / mitigación.
  - Scorecard de Sesión: Integración de objetivos cumplidos, timeline de eventos ECS y puntuación CTF.
"""
from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOGGER = logging.getLogger('scoreboard')
REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_iso_or_epoch(val: Any) -> Optional[float]:
    """Convierte un timestamp (ISO 8601 string o epoch float) a segundos epoch float."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val = val.strip()
        # Try numeric string
        try:
            return float(val)
        except ValueError:
            pass
        # Try ISO 8601
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.datetime.strptime(val, fmt)
                return dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            except ValueError:
                continue
    return None


@dataclass
class SocMetrics:
    """Métricas SOC calculadas."""
    mttd_seconds: Optional[float] = None
    mttr_seconds: Optional[float] = None
    total_events: int = 0
    attack_events_count: int = 0
    alert_events_count: int = 0
    defense_events_count: int = 0
    first_attack_ts: Optional[float] = None
    first_alert_ts: Optional[float] = None
    first_defense_ts: Optional[float] = None


class ScoreboardEngine:
    """Motor de análisis de eventos SIEM y cálculo de scorecard de ciberdefensa."""

    def __init__(self, siem_url: str = "http://10.0.2.20:8514"):
        self.siem_url = siem_url.rstrip('/')

    def fetch_siem_events(self) -> List[Dict[str, Any]]:
        """Recupera los eventos ECS del buffer del SIEM central."""
        url = f"{self.siem_url}/api/siem/events"
        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as exc:
            LOGGER.debug("No se pudieron recuperar eventos SIEM desde %s: %s", url, exc)
            return []

    def compute_soc_metrics(self, events: List[Dict[str, Any]]) -> SocMetrics:
        """Calcula MTTD y MTTR analizando la secuencia temporal de eventos ECS."""
        metrics = SocMetrics(total_events=len(events))
        if not events:
            return metrics

        attack_timestamps: List[float] = []
        alert_timestamps: List[float] = []
        defense_timestamps: List[float] = []

        for ev in events:
            raw_ts = ev.get("timestamp")
            ts = parse_iso_or_epoch(raw_ts)
            if ts is None:
                continue

            category = str(ev.get("event_category", "")).lower()
            ev_type = str(ev.get("event_type", "")).lower()
            severity = str(ev.get("severity", "")).upper()
            msg = str(ev.get("message", "")).lower()
            service_name = str(ev.get("service_name", "")).lower()

            # 1. Defensive action / SDN mitigation
            if (
                category in ("defense", "mitigation", "sdn")
                or ev_type in ("mitigation", "isolation")
                or "circuit_breaker" in msg
                or "isolated" in msg
                or "remediated" in msg
                or "mitigated" in msg
            ):
                defense_timestamps.append(ts)

            # 2. Correlated Security Alert
            elif (
                ev_type == "alert"
                or category == "alert"
                or ev_type == "system_trip"
                or "correlated alert" in msg
                or (service_name in ("siem_pipeline", "siem", "soc") and severity in ("HIGH", "CRITICAL"))
            ):
                alert_timestamps.append(ts)

            # 3. Attack activity / raw honeypot hit / anomaly
            elif (
                category in ("honeypot", "attack", "exploit", "ctf")
                or ev_type in ("intrusion", "malicious_write", "denial")
                or "ataque" in msg
                or "attack" in msg
                or "spoof" in msg
                or "recon" in msg
                or "honeypot" in msg
            ):
                attack_timestamps.append(ts)

        metrics.attack_events_count = len(attack_timestamps)
        metrics.alert_events_count = len(alert_timestamps)
        metrics.defense_events_count = len(defense_timestamps)

        if attack_timestamps:
            metrics.first_attack_ts = min(attack_timestamps)
        if alert_timestamps:
            metrics.first_alert_ts = min(alert_timestamps)
        if defense_timestamps:
            metrics.first_defense_ts = min(defense_timestamps)

        # MTTD = First Attack -> First Alert
        if metrics.first_attack_ts is not None and metrics.first_alert_ts is not None:
            if metrics.first_alert_ts >= metrics.first_attack_ts:
                metrics.mttd_seconds = round(metrics.first_alert_ts - metrics.first_attack_ts, 3)
            else:
                # If alert happened right at attack onset
                metrics.mttd_seconds = 0.0

        # MTTR = First Alert -> First Defense
        if metrics.first_alert_ts is not None and metrics.first_defense_ts is not None:
            if metrics.first_defense_ts >= metrics.first_alert_ts:
                metrics.mttr_seconds = round(metrics.first_defense_ts - metrics.first_alert_ts, 3)
            else:
                metrics.mttr_seconds = 0.0

        return metrics

    def generate_scorecard(
        self,
        scenario_id: Optional[str] = None,
        events: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Genera un reporte completo de Scorecard y métricas SOC."""
        if events is None:
            events = self.fetch_siem_events()

        soc = self.compute_soc_metrics(events)

        card = {
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "scenario_id": scenario_id,
            "total_events_analyzed": soc.total_events,
            "soc_metrics": {
                "mttd_seconds": soc.mttd_seconds,
                "mttd_formatted": f"{soc.mttd_seconds:.2f}s" if soc.mttd_seconds is not None else "N/A (sin alertas)",
                "mttr_seconds": soc.mttr_seconds,
                "mttr_formatted": f"{soc.mttr_seconds:.2f}s" if soc.mttr_seconds is not None else "N/A (sin mitigación)",
                "attacks_detected": soc.attack_events_count,
                "alerts_generated": soc.alert_events_count,
                "defense_actions": soc.defense_events_count,
            },
            "timeline_summary": [
                {
                    "ts": ev.get("timestamp"),
                    "service": ev.get("service_name"),
                    "severity": ev.get("severity"),
                    "msg": ev.get("message"),
                }
                for ev in events[-15:]
            ]
        }
        return card


def main() -> int:
    parser = argparse.ArgumentParser(description="CityLab Scoreboard & SOC Metrics Analyzer")
    parser.add_argument("--siem-url", default=os.getenv("SIEM_HTTP_URL", "http://10.0.2.20:8514"))
    parser.add_argument("--scenario", default=None, help="ID del escenario")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    args = parser.parse_args()

    engine = ScoreboardEngine(siem_url=args.siem_url)
    scorecard = engine.generate_scorecard(scenario_id=args.scenario)

    if args.json:
        print(json.dumps(scorecard, indent=2, ensure_ascii=False))
        return 0

    print("=" * 64)
    print("🛡️  CityLab Cyber Range — Métricas SOC y Scorecard Automatizado")
    print(f"   Escenario: {scorecard.get('scenario_id') or 'Sesión Global'}")
    print("=" * 64)
    metrics = scorecard["soc_metrics"]
    print(f"   ⏱️  MTTD (Tiempo Medio de Detección)   : {metrics['mttd_formatted']}")
    print(f"   🛠️  MTTR (Tiempo Medio de Respuesta)   : {metrics['mttr_formatted']}")
    print(f"   🔍  Eventos de Ataque Identificados     : {metrics['attacks_detected']}")
    print(f"   🚨  Alertas SOC Correlacionadas        : {metrics['alerts_generated']}")
    print(f"   🛡️  Acciones de Mitigación / SDN       : {metrics['defense_actions']}")
    print("=" * 64)

    return 0


if __name__ == '__main__':
    exit(main())
