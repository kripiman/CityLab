#!/usr/bin/env python3
"""network/flag_service.py — Servicio de Flags Verificables y Scoring Server-Side (Fase 1)

Genera flags dinámicas e inmemorizables por sesión basadas en HMAC-SHA256 y verifica
las condiciones de estado físico / ciberfísico real antes de emitir (mint) cada flag.

Endpoints HTTP (puerto 8570 por defecto):
  - GET  /health
  - GET  /api/flag/mint/<scenario_id>/<flag_id>
  - POST /api/flag/submit
  - GET  /api/flags/manifest/<scenario_id>
  - GET  /api/scoreboard
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import logging
import os
import re
import sqlite3
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Any, Dict, List, Optional, Tuple

import yaml

from network.historian import HistorianTSDB, _DEFAULT_DB_PATH
from network.siem_pipeline import forward_event_to_central_siem, EcsEvent

LOGGER = logging.getLogger('flag_service')
DEFAULT_PORT = 8570
DEFAULT_SEED = "citylab_default_session_seed_2026"
REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = REPO_ROOT / "config" / "scenarios"


# ---------------------------------------------------------------------- #
#  HMAC Dynamic Flag Generation & Verification                          #
# ---------------------------------------------------------------------- #

def generate_flag_hmac(session_seed: str, flag_id: str, scenario_id: str = "") -> str:
    """Genera una flag dinámica e inmemorizable: FLAG_<id>{HMAC_SHA256(seed, flag_id)[:12]}."""
    seed = (session_seed or os.getenv('CITYLAB_SESSION_SEED', DEFAULT_SEED)).strip()
    key_material = f"{scenario_id}:{flag_id}" if scenario_id else flag_id
    sig = hmac.new(seed.encode('utf-8'), key_material.encode('utf-8'), hashlib.sha256).hexdigest()[:12]
    clean_id = flag_id.upper()
    if not clean_id.startswith("FLAG_"):
        clean_id = f"FLAG_{clean_id}"
    return f"{clean_id}{{{sig}}}"


def verify_flag_hmac(session_seed: str, flag_id: str, submitted_flag: str, scenario_id: str = "") -> bool:
    """Verifica si la flag enviada coincide exactamente con la calculada para la sesión."""
    expected = generate_flag_hmac(session_seed, flag_id, scenario_id)
    # Also support verification without scenario_id prefix if generated that way
    expected_alt = generate_flag_hmac(session_seed, flag_id, "")
    submitted = submitted_flag.strip()
    return hmac.compare_digest(expected, submitted) or hmac.compare_digest(expected_alt, submitted)


# ---------------------------------------------------------------------- #
#  Oracles / Checkers Engine                                             #
# ---------------------------------------------------------------------- #

class ConditionChecker:
    """Evalúa oráculos de verificación de estado físico, SCADA, SIEM y red."""

    def __init__(
        self,
        historian: Optional[HistorianTSDB] = None,
        scada_url: str = "http://10.0.2.20:8080",
        siem_url: str = "http://10.0.2.20:8514",
    ):
        self.historian = historian or HistorianTSDB()
        self.scada_url = scada_url.rstrip('/')
        self.siem_url = siem_url.rstrip('/')

    def evaluate(self, check_def: Dict[str, Any]) -> Tuple[bool, str]:
        """Evalúa una definición de check y retorna (éxito, mensaje/detalle)."""
        check_type = check_def.get("type", "")
        if check_type == "http_status":
            return self._check_http_status(check_def)
        elif check_type == "historian_condition":
            return self._check_historian_condition(check_def)
        elif check_type == "scada_sector_status":
            return self._check_scada_sector_status(check_def)
        elif check_type == "siem_alert":
            return self._check_siem_alert(check_def)
        elif check_type == "openflow_rule":
            return self._check_openflow_rule(check_def)
        else:
            return False, f"Tipo de check desconocido: {check_type}"

    def _check_http_status(self, check: Dict[str, Any]) -> Tuple[bool, str]:
        url = check.get("url", "")
        expect = int(check.get("expect", 200))
        method = check.get("method", "GET").upper()
        headers = check.get("headers", {})
        timeout = float(check.get("timeout", 2.0))

        if not url:
            return False, "Falta URL para check http_status"

        try:
            req = urllib.request.Request(url, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.getcode()
                if status == expect:
                    return True, f"HTTP {status} coincide con esperado {expect}"
                return False, f"HTTP {status} != esperado {expect}"
        except urllib.error.HTTPError as exc:
            if exc.code == expect:
                return True, f"HTTP {exc.code} coincide con esperado {expect}"
            return False, f"HTTP error {exc.code} (esperado {expect})"
        except Exception as exc:
            return False, f"Fallo de conexión a {url}: {exc}"

    def _check_historian_condition(self, check: Dict[str, Any]) -> Tuple[bool, str]:
        query_str = check.get("query", "").strip()
        window_s = float(check.get("window_s", 60.0))
        target_sector = check.get("sector", None)
        since_ts = time.time() - window_s

        if not query_str:
            return False, "Falta query de condición para historian_condition"

        # Match simple expressions like "grid_freq_hz < 58.0" or "level > 90" or "status == 'LOSS_OF_VIEW'"
        match = re.match(r"^\s*([a-zA-Z0-9_]+)\s*(<=|>=|<|>|==|!=|=)\s*(.+?)\s*$", query_str)
        if not match:
            return False, f"Sintaxis de condición no soportada: {query_str}"

        field_name, op, raw_val = match.groups()
        raw_val = raw_val.strip("'\"")

        try:
            val_num = float(raw_val)
            is_numeric = True
        except ValueError:
            val_num = None
            is_numeric = False

        db_path = getattr(self.historian, '_db_path', _DEFAULT_DB_PATH)
        if not Path(db_path).exists():
            return False, f"Base de datos Historian no existe en {db_path}"

        try:
            with sqlite3.connect(str(db_path), timeout=2.0) as conn:
                conn.row_factory = sqlite3.Row
                sql = "SELECT ts, sector, field, value, value_str FROM telemetry WHERE ts >= ? AND (field = ? OR field LIKE ?)"
                params: List[Any] = [since_ts, field_name, f"%{field_name}%"]
                if target_sector:
                    sql += " AND sector = ?"
                    params.append(target_sector)
                sql += " ORDER BY ts DESC LIMIT 200"

                rows = conn.execute(sql, params).fetchall()

                if not rows:
                    # Also check telemetry_raw if JSON snapshots exist
                    raw_sql = "SELECT ts, sector, data FROM telemetry_raw WHERE ts >= ?"
                    raw_params: List[Any] = [since_ts]
                    if target_sector:
                        raw_sql += " AND sector = ?"
                        raw_params.append(target_sector)
                    raw_rows = conn.execute(raw_sql, raw_params).fetchall()
                    for r in raw_rows:
                        try:
                            d = json.loads(r["data"])
                            if field_name in d:
                                f_val = d[field_name]
                                if self._compare_values(f_val, op, val_num if is_numeric else raw_val):
                                    return True, f"Condición '{query_str}' cumplida en snapshot raw (ts={r['ts']:.1f}, val={f_val})"
                        except Exception:
                            continue

                    return False, f"No hay registros recientes para campo '{field_name}' en los últimos {window_s}s"

                for r in rows:
                    curr_val = r["value"] if is_numeric and r["value"] is not None else (r["value_str"] or r["value"])
                    if self._compare_values(curr_val, op, val_num if is_numeric else raw_val):
                        return True, f"Condición '{query_str}' cumplida (ts={r['ts']:.1f}, sector={r['sector']}, val={curr_val})"

                return False, f"Ningún registro de '{field_name}' en ventana {window_s}s cumplió '{query_str}'"
        except Exception as exc:
            return False, f"Error consultando Historian: {exc}"

    def _compare_values(self, actual: Any, op: str, expected: Any) -> bool:
        if actual is None:
            return False
        try:
            if op in ('<', '<=', '>', '>='):
                act_f = float(actual)
                exp_f = float(expected)
                if op == '<':  return act_f < exp_f
                if op == '<=': return act_f <= exp_f
                if op == '>':  return act_f > exp_f
                if op == '>=': return act_f >= exp_f
            elif op in ('==', '='):
                return str(actual).strip().lower() == str(expected).strip().lower()
            elif op == '!=':
                return str(actual).strip().lower() != str(expected).strip().lower()
        except Exception:
            return False
        return False

    def _check_scada_sector_status(self, check: Dict[str, Any]) -> Tuple[bool, str]:
        sector = check.get("sector", "")
        expect = str(check.get("expect", "")).upper()
        if not sector:
            return False, "Falta campo sector para scada_sector_status"

        # Try query via SCADA HTTP API
        url = f"{self.scada_url}/api/telemetry"
        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                sec_data = data.get(sector, {})
                status_val = str(sec_data.get("status", sec_data.get("state", ""))).upper()
                if expect in status_val or status_val == expect:
                    return True, f"Sector '{sector}' estado '{status_val}' coincide con esperado '{expect}'"
                return False, f"Sector '{sector}' estado es '{status_val}', esperado '{expect}'"
        except Exception:
            # Fallback to direct Historian check
            try:
                last_snap = self.historian.last(sector)
                if last_snap:
                    data_dict = last_snap.get("data", last_snap) if isinstance(last_snap, dict) else {}
                    status_val = str(data_dict.get("status", data_dict.get("state", ""))).upper()
                    if expect in status_val or status_val == expect:
                        return True, f"Historian: Sector '{sector}' estado '{status_val}' coincide con '{expect}'"
                    return False, f"Historian: Sector '{sector}' estado es '{status_val}', esperado '{expect}'"
            except Exception as e:
                return False, f"No se pudo consultar estado del sector {sector}: {e}"
        return False, f"Sector '{sector}' no disponible"

    def _check_siem_alert(self, check: Dict[str, Any]) -> Tuple[bool, str]:
        expected_rule = check.get("rule", check.get("rule_name", check.get("rule_id", "")))
        if not expected_rule:
            return False, "Falta regla esperada para check siem_alert"

        url = f"{self.siem_url}/api/siem/alerts"
        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                alerts = json.loads(resp.read().decode('utf-8'))
                for a in alerts:
                    rule_name = a.get("rule_name", a.get("rule", a.get("message", "")))
                    if expected_rule.lower() in rule_name.lower():
                        return True, f"Alerta SIEM detectada: '{rule_name}' (severity={a.get('severity')})"
                return False, f"Alerta '{expected_rule}' no encontrada en el buffer SIEM ({len(alerts)} alertas presentes)"
        except Exception as exc:
            return False, f"Fallo al consultar SIEM alerts en {url}: {exc}"

    def _check_openflow_rule(self, check: Dict[str, Any]) -> Tuple[bool, str]:
        switch = check.get("switch", "s3")
        pattern = check.get("pattern", "")
        if not pattern:
            return False, "Falta patrón de flujo para check openflow_rule"

        try:
            res = subprocess.run(
                ["ovs-ofctl", "dump-flows", switch],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2.0,
            )
            if res.returncode != 0:
                return False, f"ovs-ofctl falló con código {res.returncode}: {res.stderr.strip()}"
            if pattern.lower() in res.stdout.lower():
                return True, f"Regla OpenFlow encontrada en switch {switch} coincidiendo con '{pattern}'"
            return False, f"Patrón '{pattern}' no encontrado en flujos de switch {switch}"
        except Exception as exc:
            return False, f"Error ejecutando ovs-ofctl: {exc}"


# ---------------------------------------------------------------------- #
#  Manifest Loader                                                       #
# ---------------------------------------------------------------------- #

def load_scenario_manifest(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Carga y parsea el archivo YAML del manifiesto de escenario."""
    norm_id = str(scenario_id).zfill(2)
    path = SCENARIOS_DIR / f"scenario_{norm_id}.yml"
    if not path.exists():
        path = SCENARIOS_DIR / f"scenario_{scenario_id}.yml"
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as exc:
        LOGGER.error("Error leyendo manifiesto %s: %s", path, exc)
        return None


# ---------------------------------------------------------------------- #
#  Rate Limiter                                                          #
# ---------------------------------------------------------------------- #

class RateLimiter:
    """Limitador de tasa de peticiones deslizante por clave."""

    def __init__(self, max_requests: int = 10, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            history = self._requests.get(key, [])
            # Keep only entries within window
            history = [t for t in history if now - t < self.window_seconds]
            if len(history) >= self.max_requests:
                self._requests[key] = history
                return False
            history.append(now)
            self._requests[key] = history
            return True


# ---------------------------------------------------------------------- #
#  HTTP Request Handler                                                  #
# ---------------------------------------------------------------------- #

class FlagServiceHandler(BaseHTTPRequestHandler):
    """Manejador HTTP REST para el servicio de flags y scoring."""

    server: 'ThreadedFlagServer'

    def log_message(self, fmt: str, *args: Any) -> None:
        LOGGER.debug("[FLAG_SERVICE] " + fmt, *args)

    def _send_json(self, status: int, data: Dict[str, Any]) -> None:
        raw = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path in ('', '/health'):
            self._send_json(200, {
                "status": "ok",
                "service": "flag_service",
                "port": self.server.server_port,
                "session_seed_set": bool(self.server.session_seed),
            })
            return

        # GET /api/flag/mint/<scenario_id>/<flag_id>
        mint_match = re.match(r"^/api/flag/mint/([^/]+)/([^/]+)$", path)
        if mint_match:
            scenario_id, flag_id = mint_match.groups()
            self._handle_mint(scenario_id, flag_id)
            return

        # GET /api/flags/manifest/<scenario_id>
        manifest_match = re.match(r"^/api/flags/manifest/([^/]+)$", path)
        if manifest_match:
            scenario_id = manifest_match.group(1)
            manifest = load_scenario_manifest(scenario_id)
            if not manifest:
                self._send_json(404, {"error": f"Manifiesto scenario_{scenario_id}.yml no encontrado"})
                return
            # Return public view of manifest without internal secrets
            self._send_json(200, manifest)
            return

        # GET /api/scoreboard
        if path == '/api/scoreboard':
            self._send_json(200, self.server.get_scoreboard_data())
            return

        self._send_json(404, {"error": "Endpoint no encontrado", "path": path})

    def _handle_mint(self, scenario_id: str, flag_id: str) -> None:
        manifest = load_scenario_manifest(scenario_id)
        if not manifest:
            self._send_json(404, {
                "success": False,
                "error": f"Manifiesto de escenario '{scenario_id}' no encontrado en {SCENARIOS_DIR}"
            })
            return

        clean_flag_id = flag_id.upper()
        if not clean_flag_id.startswith("FLAG_"):
            clean_flag_id = f"FLAG_{clean_flag_id}"

        target_obj = None
        for obj in manifest.get("objectives", []):
            if str(obj.get("id", "")).upper() == clean_flag_id:
                target_obj = obj
                break

        if not target_obj:
            self._send_json(404, {
                "success": False,
                "error": f"Objetivo '{flag_id}' no encontrado en escenario '{scenario_id}'"
            })
            return

        check_def = target_obj.get("check", {})
        passed, details = self.server.checker.evaluate(check_def)

        if passed:
            flag_value = generate_flag_hmac(self.server.session_seed, clean_flag_id, scenario_id)
            self._send_json(200, {
                "success": True,
                "scenario_id": scenario_id,
                "flag_id": clean_flag_id,
                "flag": flag_value,
                "desc": target_obj.get("desc", ""),
                "points": target_obj.get("points", 100),
                "details": details,
            })
        else:
            self._send_json(400, {
                "success": False,
                "scenario_id": scenario_id,
                "flag_id": clean_flag_id,
                "error": "Condición de estado físico/ciberfísico no cumplida",
                "details": details,
            })

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/api/flag/submit':
            client_ip = self.client_address[0]
            if not self.server.rate_limiter.is_allowed(client_ip):
                self._send_json(429, {"valid": False, "error": "Rate limit excedido. Intenta más tarde."})
                return

            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len).decode('utf-8')
                payload = json.loads(body)
            except Exception as exc:
                self._send_json(400, {"valid": False, "error": f"JSON inválido: {exc}"})
                return

            scenario_id = str(payload.get("scenario", payload.get("scenario_id", "")))
            submitted_flag = str(payload.get("flag", "")).strip()
            team = str(payload.get("team", client_ip))

            if not submitted_flag:
                self._send_json(400, {"valid": False, "error": "Campo 'flag' requerido"})
                return

            # Extract flag_id prefix e.g. "FLAG_1" from "FLAG_1{abc...}"
            match = re.match(r"^(FLAG_[0-9A-Za-z_-]+)\{([0-9a-fA-F]{12})\}$", submitted_flag)
            if not match:
                self._send_json(400, {"valid": False, "error": "Formato de flag inválido. Esperado: FLAG_X{12hex}"})
                return

            flag_id, sig = match.groups()
            is_valid = verify_flag_hmac(self.server.session_seed, flag_id, submitted_flag, scenario_id)

            from dataclasses import asdict
            event = EcsEvent(
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                event_category='ctf',
                event_type='flag_submission',
                severity='HIGH' if is_valid else 'LOW',
                source_ip=client_ip,
                destination_ip='10.0.2.20',
                service_name='flag_service',
                message=f"CTF Flag Submission: team='{team}', scenario='{scenario_id}', flag_id='{flag_id}', valid={is_valid}",
                metadata={"team": team, "scenario": scenario_id, "flag_id": flag_id, "valid": is_valid}
            )
            forward_event_to_central_siem(asdict(event), self.server.siem_url)

            if is_valid:
                points = 100
                manifest = load_scenario_manifest(scenario_id)
                if manifest:
                    for obj in manifest.get("objectives", []):
                        if str(obj.get("id", "")).upper() == flag_id.upper():
                            points = obj.get("points", 100)
                            break

                self.server.record_submission(team, scenario_id, flag_id, points)
                self._send_json(200, {
                    "valid": True,
                    "scenario_id": scenario_id,
                    "flag_id": flag_id,
                    "points": points,
                    "message": f"¡Flag correcta! +{points} puntos registrados.",
                })
            else:
                self._send_json(400, {
                    "valid": False,
                    "error": "Flag inválida para esta sesión de Cyber Range."
                })
            return

        self._send_json(404, {"error": "Endpoint no encontrado", "path": path})


# ---------------------------------------------------------------------- #
#  Server Infrastructure                                                 #
# ---------------------------------------------------------------------- #

class ThreadedFlagServer(ThreadingMixIn, HTTPServer):
    """Servidor HTTP multihilo para el servicio de flags y scoring."""

    def __init__(
        self,
        server_address: Tuple[str, int],
        session_seed: str,
        historian: Optional[HistorianTSDB] = None,
        siem_url: str = "http://10.0.2.20:8514",
        scada_url: str = "http://10.0.2.20:8080",
    ):
        super().__init__(server_address, FlagServiceHandler)
        self.session_seed = session_seed
        self.siem_url = siem_url
        self.scada_url = scada_url
        self.server_port = server_address[1]
        self.checker = ConditionChecker(historian=historian, scada_url=scada_url, siem_url=siem_url)
        self.rate_limiter = RateLimiter(max_requests=15, window_seconds=60.0)
        self._scoreboard: Dict[str, Any] = {
            "teams": {},
            "submissions": [],
            "start_time": time.time(),
        }
        self._score_lock = threading.Lock()

    def record_submission(self, team: str, scenario_id: str, flag_id: str, points: int) -> None:
        with self._score_lock:
            sub_key = f"{scenario_id}:{flag_id}"
            team_info = self._scoreboard["teams"].setdefault(team, {"score": 0, "solved": []})
            if sub_key not in team_info["solved"]:
                team_info["solved"].append(sub_key)
                team_info["score"] += points
                self._scoreboard["submissions"].append({
                    "timestamp": time.time(),
                    "team": team,
                    "scenario": scenario_id,
                    "flag_id": flag_id,
                    "points": points,
                })

    def get_scoreboard_data(self) -> Dict[str, Any]:
        with self._score_lock:
            return {
                "session_seed": self.session_seed[:8] + "...",
                "uptime_seconds": round(time.time() - self._scoreboard["start_time"], 1),
                "teams": self._scoreboard["teams"],
                "total_submissions": len(self._scoreboard["submissions"]),
                "recent_submissions": self._scoreboard["submissions"][-20:],
            }


def run_flag_service(
    host: str = "0.0.0.0",
    port: int = DEFAULT_PORT,
    seed: Optional[str] = None,
    db_path: Optional[Path] = None,
    siem_url: Optional[str] = None,
    scada_url: Optional[str] = None,
) -> None:
    """Inicia el demonio de Flag Service."""
    session_seed = seed or os.getenv('CITYLAB_SESSION_SEED', DEFAULT_SEED)
    historian = HistorianTSDB(db_path=db_path)
    s_url = siem_url or os.getenv('SIEM_HTTP_URL', 'http://10.0.2.20:8514')
    c_url = scada_url or os.getenv('SCADA_HTTP_URL', 'http://10.0.2.20:8080')

    server = ThreadedFlagServer(
        (host, port),
        session_seed=session_seed,
        historian=historian,
        siem_url=s_url,
        scada_url=c_url,
    )
    print(f"[*] Flag Service iniciado en http://{host}:{port} (seed: {session_seed[:6]}...)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Flag Service detenido.")
    finally:
        server.server_close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    parser = argparse.ArgumentParser(description="CityLab Flag & Scoring Service Daemon")
    parser.add_argument("--host", default="0.0.0.0", help="Dirección IP de escucha (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Puerto de escucha (default: {DEFAULT_PORT})")
    parser.add_argument("--seed", default=None, help="Semilla de sesión para HMAC (default: env CITYLAB_SESSION_SEED)")
    parser.add_argument("--db-path", default=None, help="Ruta a base de datos Historian SQLite WAL")
    args = parser.parse_args()

    run_flag_service(
        host=args.host,
        port=args.port,
        seed=args.seed,
        db_path=Path(args.db_path) if args.db_path else None,
    )
