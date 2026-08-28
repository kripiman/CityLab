"""
Tests unitarios y de integración para network/flag_service.py (Fase 1 - Roadmap)
"""

import json
import sqlite3
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path
import pytest

from network.flag_service import (
    ConditionChecker,
    RateLimiter,
    ThreadedFlagServer,
    generate_flag_hmac,
    verify_flag_hmac,
    load_scenario_manifest,
)
from network.historian import HistorianTSDB


@pytest.fixture
def temp_historian(tmp_path):
    db_file = tmp_path / "test_flag_historian.db"
    return HistorianTSDB(db_path=db_file)


def test_hmac_determinism_and_uniqueness():
    """Verifica que el HMAC sea determinista con la misma semilla y distinto con otra."""
    seed_a = "seed_alpha_2026"
    seed_b = "seed_beta_2026"

    flag_1_a = generate_flag_hmac(seed_a, "FLAG_1", "01")
    flag_1_a_repeat = generate_flag_hmac(seed_a, "FLAG_1", "01")
    flag_1_b = generate_flag_hmac(seed_b, "FLAG_1", "01")
    flag_2_a = generate_flag_hmac(seed_a, "FLAG_2", "01")

    # Deterministic
    assert flag_1_a == flag_1_a_repeat
    assert flag_1_a.startswith("FLAG_1{")
    assert flag_1_a.endswith("}")

    # Unique across seeds
    assert flag_1_a != flag_1_b

    # Unique across objectives
    assert flag_1_a != flag_2_a

    # Verification
    assert verify_flag_hmac(seed_a, "FLAG_1", flag_1_a, "01") is True
    assert verify_flag_hmac(seed_a, "FLAG_1", "FLAG_1{fake12345678}", "01") is False
    assert verify_flag_hmac(seed_b, "FLAG_1", flag_1_a, "01") is False


def test_rate_limiter():
    """Verifica que el limitador de tasa bloquee intentos excesivos."""
    limiter = RateLimiter(max_requests=3, window_seconds=2.0)
    client_ip = "127.0.0.1"

    assert limiter.is_allowed(client_ip) is True
    assert limiter.is_allowed(client_ip) is True
    assert limiter.is_allowed(client_ip) is True
    # 4th request in window should be blocked
    assert limiter.is_allowed(client_ip) is False

    # Another IP is allowed
    assert limiter.is_allowed("192.168.1.100") is True


def test_checker_historian_condition(temp_historian):
    """Verifica la evaluación del oráculo de estado físico sobre el Historian TSDB."""
    checker = ConditionChecker(historian=temp_historian)

    # 1. Sin datos -> debe fallar (negativo)
    check_freq = {
        "type": "historian_condition",
        "query": "grid_freq_hz < 58.0",
        "sector": "elec",
        "window_s": 30.0,
    }
    passed, msg = checker.evaluate(check_freq)
    assert passed is False
    assert "No hay registros recientes" in msg or "Ningún registro" in msg

    # 2. Con dato en rango normal (60.0 Hz) -> debe fallar
    temp_historian.write("elec", "grid_freq_hz", 60.0, timestamp=time.time())
    passed, msg = checker.evaluate(check_freq)
    assert passed is False

    # 3. Con dato de ataque (57.4 Hz) -> debe pasar (positivo)
    temp_historian.write("elec", "grid_freq_hz", 57.4, timestamp=time.time())
    passed, msg = checker.evaluate(check_freq)
    assert passed is True
    assert "cumplida" in msg


def test_checker_scada_sector_status(temp_historian):
    """Verifica la evaluación del oráculo de estado de sector SCADA."""
    checker = ConditionChecker(historian=temp_historian)

    # Simula estado en reposo
    temp_historian.write_snapshot("water", {"status": "NORMAL", "pumps": [1, 0]})
    check_status = {
        "type": "scada_sector_status",
        "sector": "water",
        "expect": "LOSS_OF_VIEW",
    }
    passed, msg = checker.evaluate(check_status)
    assert passed is False

    # Simula pérdida de visión por ataque
    temp_historian.write_snapshot("water", {"status": "LOSS_OF_VIEW", "pumps": [0, 0]})
    passed, msg = checker.evaluate(check_status)
    assert passed is True


@pytest.fixture
def test_flag_server(tmp_path):
    """Inicia un ThreadedFlagServer en un puerto efímero de test."""
    db_file = tmp_path / "server_historian.db"
    historian = HistorianTSDB(db_path=db_file)
    # Escribe telemetría de prueba para scenario_01
    historian.write("elec", "grid_freq_hz", 56.5, timestamp=time.time())
    historian.write_snapshot("water", {"status": "LOSS_OF_VIEW"})

    # Bind to port 0 to get OS-assigned ephemeral port
    server = ThreadedFlagServer(
        ("127.0.0.1", 0),
        session_seed="test_server_seed_999",
        historian=historian,
    )
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    yield server, f"http://127.0.0.1:{port}"

    server.shutdown()
    server.server_close()


def test_flag_server_endpoints(test_flag_server):
    """Prueba los endpoints HTTP /health, /api/flag/mint, /api/flag/submit y /api/scoreboard."""
    _, base_url = test_flag_server

    # 1. GET /health
    with urllib.request.urlopen(f"{base_url}/health", timeout=2.0) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data["status"] == "ok"
        assert data["service"] == "flag_service"

    # 2. GET /api/flag/mint/01/FLAG_2 (grid_freq_hz < 58.0 -> pasa porque escribimos 56.5)
    with urllib.request.urlopen(f"{base_url}/api/flag/mint/01/FLAG_2", timeout=2.0) as resp:
        assert resp.status == 200
        mint_data = json.loads(resp.read().decode('utf-8'))
        assert mint_data["success"] is True
        assert mint_data["flag"].startswith("FLAG_2{")
        flag_val = mint_data["flag"]

    # 3. POST /api/flag/submit (flag correcta)
    submit_body = json.dumps({
        "scenario": "01",
        "flag": flag_val,
        "team": "red_team_alpha"
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/flag/submit", data=submit_body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=2.0) as resp:
        assert resp.status == 200
        sub_res = json.loads(resp.read().decode('utf-8'))
        assert sub_res["valid"] is True
        assert sub_res["points"] == 200

    # 4. POST /api/flag/submit (flag incorrecta)
    bad_body = json.dumps({
        "scenario": "01",
        "flag": "FLAG_2{000000000000}",
        "team": "red_team_alpha"
    }).encode('utf-8')
    req_bad = urllib.request.Request(f"{base_url}/api/flag/submit", data=bad_body, headers={'Content-Type': 'application/json'})
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req_bad, timeout=2.0)
    assert exc_info.value.code == 400

    # 5. GET /api/scoreboard
    with urllib.request.urlopen(f"{base_url}/api/scoreboard", timeout=2.0) as resp:
        assert resp.status == 200
        board = json.loads(resp.read().decode('utf-8'))
        assert "red_team_alpha" in board["teams"]
        assert board["teams"]["red_team_alpha"]["score"] == 200
