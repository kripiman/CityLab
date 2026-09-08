"""
Tests unitarios para network/scoreboard.py (Fase 4 - Métricas SOC MTTD/MTTR)
"""

import json
import pytest
from network.scoreboard import ScoreboardEngine, parse_iso_or_epoch


def test_parse_iso_or_epoch():
    """Verifica la conversión de timestamps variados a float epoch."""
    # Epoch float
    assert parse_iso_or_epoch(1700000000.5) == 1700000000.5
    # Numeric string
    assert parse_iso_or_epoch("1700000000.0") == 1700000000.0
    # ISO 8601 UTC
    ts_iso = "2026-08-28T12:00:00Z"
    epoch = parse_iso_or_epoch(ts_iso)
    assert epoch is not None
    assert epoch > 1700000000
    # None
    assert parse_iso_or_epoch(None) is None


def test_scoreboard_empty_events():
    """Verifica que un buffer vacío no cause excepciones y reporte métricas vacías."""
    engine = ScoreboardEngine()
    scorecard = engine.generate_scorecard(scenario_id="01", events=[])

    assert scorecard["scenario_id"] == "01"
    assert scorecard["total_events_analyzed"] == 0
    metrics = scorecard["soc_metrics"]
    assert metrics["mttd_seconds"] is None
    assert metrics["mttr_seconds"] is None
    assert metrics["attacks_detected"] == 0
    assert metrics["alerts_generated"] == 0


def test_soc_metrics_mttd_mttr_exact():
    """Calcula MTTD y MTTR exactos a partir de eventos sintéticos con timestamps conocidos."""
    engine = ScoreboardEngine()

    t0 = 1756400000.0  # Attack begins
    t_alert = t0 + 4.25  # SIEM Alert 4.25s later
    t_defense = t_alert + 2.5  # SDN Circuit Breaker mitigation 2.5s after alert

    synthetic_events = [
        {
            "timestamp": t0,
            "event_category": "honeypot",
            "event_type": "intrusion",
            "severity": "MEDIUM",
            "source_ip": "10.0.1.10",
            "destination_ip": "10.0.5.99",
            "service_name": "modbus_honeypot",
            "message": "Ataque Modbus write detectado sobre honeypot",
        },
        {
            "timestamp": t_alert,
            "event_category": "alert",
            "event_type": "alert",
            "severity": "CRITICAL",
            "source_ip": "10.0.2.20",
            "destination_ip": "10.0.2.20",
            "service_name": "siem_pipeline",
            "message": "SIEM Correlated Alert: Industroyer2 GOOSE Spoofing detected",
        },
        {
            "timestamp": t_defense,
            "event_category": "defense",
            "event_type": "mitigation",
            "severity": "HIGH",
            "source_ip": "10.0.2.20",
            "destination_ip": "10.0.3.20",
            "service_name": "sdn_controller",
            "message": "SDN circuit_breaker triggered: isolating compromised host s3",
        },
    ]

    metrics = engine.compute_soc_metrics(synthetic_events)

    assert metrics.total_events == 3
    assert metrics.attack_events_count == 1
    assert metrics.alert_events_count == 1
    assert metrics.defense_events_count == 1

    assert metrics.mttd_seconds == 4.25
    assert metrics.mttr_seconds == 2.5

    scorecard = engine.generate_scorecard(scenario_id="02", events=synthetic_events)
    assert scorecard["soc_metrics"]["mttd_formatted"] == "4.25s"
    assert scorecard["soc_metrics"]["mttr_formatted"] == "2.50s"
