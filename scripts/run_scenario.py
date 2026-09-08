#!/usr/bin/env python3
"""scripts/run_scenario.py — Evaluador de Escenarios CTF, Oráculo de Flags y Scorecard

Permite a los alumnos y al CI/auditor verificar el cumplimiento de objetivos pedagógicos
y obtener las flags verificables basadas en el estado real del Cyber Range.

Uso:
  python3 scripts/run_scenario.py --id 01 --check
  python3 scripts/run_scenario.py --id 01 --validate-manifest
  python3 scripts/run_scenario.py --id 01 --submit FLAG_1{...}
  python3 scripts/run_scenario.py --id 01 --scorecard
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from network.flag_service import (
    DEFAULT_PORT,
    DEFAULT_SEED,
    ConditionChecker,
    generate_flag_hmac,
    load_scenario_manifest,
    verify_flag_hmac,
)
from network.historian import HistorianTSDB


def validate_manifest(scenario_id: str) -> bool:
    """Valida el manifiesto del escenario contra schema.json."""
    schema_path = REPO_ROOT / "config" / "scenarios" / "schema.json"
    norm_id = str(scenario_id).zfill(2)
    manifest_path = REPO_ROOT / "config" / "scenarios" / f"scenario_{norm_id}.yml"

    if not manifest_path.exists():
        manifest_path = REPO_ROOT / "config" / "scenarios" / f"scenario_{scenario_id}.yml"

    if not manifest_path.exists():
        print(f"❌ Error: Manifiesto no encontrado para escenario {scenario_id} ({manifest_path})")
        return False

    if not schema_path.exists():
        print(f"❌ Error: Esquema no encontrado en {schema_path}")
        return False

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        try:
            import jsonschema
            jsonschema.validate(instance=data, schema=schema)
            print(f"✅ Manifiesto '{manifest_path.name}' válido contra schema.json")
            return True
        except ImportError:
            # Fallback check
            assert "id" in data and "title" in data and "objectives" in data
            print(f"✅ Manifiesto '{manifest_path.name}' tiene campos requeridos (jsonschema no instalado)")
            return True
        except Exception as err:
            print(f"❌ Error de validación en '{manifest_path.name}': {err}")
            return False
    except Exception as exc:
        print(f"❌ Error leyendo archivo: {exc}")
        return False


def run_checks(
    scenario_id: str,
    flag_service_url: Optional[str] = None,
    session_seed: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> int:
    """Ejecuta los checks del escenario y muestra el estado y las flags obtenidas."""
    manifest = load_scenario_manifest(scenario_id)
    if not manifest:
        print(f"❌ Escenario '{scenario_id}' no encontrado en config/scenarios/")
        return 2

    print("=" * 72)
    print(f"🎯 CityLab CTF — Evaluación de Escenario {manifest.get('id')}: {manifest.get('title')}")
    print(f"   Dificultad: {manifest.get('difficulty', 'N/A')} | Categoría: {manifest.get('category', 'N/A')}")
    print("=" * 72)

    seed = (session_seed or os.getenv('CITYLAB_SESSION_SEED', DEFAULT_SEED)).strip()
    checker = ConditionChecker(
        historian=HistorianTSDB(db_path=db_path),
        scada_url=os.getenv('SCADA_HTTP_URL', 'http://10.0.2.20:8080'),
        siem_url=os.getenv('SIEM_HTTP_URL', 'http://10.0.2.20:8514'),
    )

    objectives = manifest.get("objectives", [])
    if not objectives:
        print("⚠️ No hay objetivos definidos en este escenario.")
        return 1

    passed_count = 0
    total_count = len(objectives)
    total_points = 0
    earned_points = 0

    print(f"\n{'ID':<8} | {'Puntos':<6} | {'Estado':<8} | {'Descripción'}")
    print("-" * 72)

    results = []

    for obj in objectives:
        obj_id = obj.get("id", "FLAG_?")
        desc = obj.get("desc", "")
        pts = obj.get("points", 100)
        total_points += pts
        check_def = obj.get("check", {})

        # Try query through running flag service daemon first if available
        passed = False
        details = ""
        minted_flag = None

        if flag_service_url:
            norm_url = flag_service_url.rstrip('/')
            url = f"{norm_url}/api/flag/mint/{scenario_id}/{obj_id}"
            try:
                req = urllib.request.Request(url, headers={'Accept': 'application/json'})
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    passed = data.get("success", False)
                    minted_flag = data.get("flag")
                    details = data.get("details", "")
            except urllib.error.HTTPError as exc:
                try:
                    err_data = json.loads(exc.read().decode('utf-8'))
                    details = err_data.get("details", err_data.get("error", str(exc)))
                except Exception:
                    details = str(exc)
            except Exception as exc:
                details = f"Flag service no alcanzable: {exc}"

        if not flag_service_url or (not passed and "no alcanzable" in details):
            # Evaluate locally via Checker engine
            passed, details = checker.evaluate(check_def)
            if passed:
                minted_flag = generate_flag_hmac(seed, obj_id, str(manifest.get("id")))

        if passed:
            passed_count += 1
            earned_points += pts
            status_str = "✅ PASS"
        else:
            status_str = "❌ FAIL"

        results.append({
            "id": obj_id,
            "desc": desc,
            "points": pts,
            "passed": passed,
            "flag": minted_flag,
            "details": details,
        })

        print(f"{obj_id:<8} | {pts:<6} | {status_str:<8} | {desc}")

    print("-" * 72)
    print(f"📊 Resumen: {passed_count}/{total_count} objetivos cumplidos | {earned_points}/{total_points} puntos")

    if passed_count > 0:
        print("\n🚩 Flags Obtenidas (Minted Server-Side):")
        for res in results:
            if res["passed"] and res["flag"]:
                print(f"   - {res['id']}: \033[1;32m{res['flag']}\033[0m ({res['desc']})")

    failed_objs = [r for r in results if not r["passed"]]
    if failed_objs:
        print("\n💡 Diagnóstico de Objetivos Pendientes:")
        for res in failed_objs:
            print(f"   - {res['id']}: {res['details']}")

    print("=" * 72)
    return 0 if passed_count == total_count else 1


def submit_flag(
    scenario_id: str,
    flag_str: str,
    team: str = "student",
    flag_service_url: str = "http://10.0.2.20:8570",
    session_seed: Optional[str] = None,
) -> int:
    """Envía una flag para verificación."""
    seed = (session_seed or os.getenv('CITYLAB_SESSION_SEED', DEFAULT_SEED)).strip()
    norm_url = flag_service_url.rstrip('/')

    # Try HTTP POST to Flag Service
    try:
        data = json.dumps({
            "scenario": scenario_id,
            "flag": flag_str,
            "team": team,
        }).encode('utf-8')
        req = urllib.request.Request(
            f"{norm_url}/api/flag/submit",
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            if res.get("valid"):
                print(f"🎉 \033[1;32m{res.get('message', '¡Flag correcta!')}\033[0m (+{res.get('points')} pts)")
                return 0
            else:
                print(f"❌ \033[1;31m{res.get('error', 'Flag inválida')}\033[0m")
                return 1
    except urllib.error.HTTPError as exc:
        try:
            err = json.loads(exc.read().decode('utf-8'))
            print(f"❌ \033[1;31m{err.get('error', 'Error al verificar flag')}\033[0m")
        except Exception:
            print(f"❌ Error HTTP {exc.code}")
        return 1
    except Exception:
        # Fallback local verification
        match = re.match(r"^(FLAG_[0-9A-Za-z_-]+)\{([0-9a-fA-F]{12})\}$", flag_str.strip())
        if not match:
            print("❌ Formato de flag inválido. Esperado: FLAG_X{12hex}")
            return 1
        flag_id = match.group(1)
        if verify_flag_hmac(seed, flag_id, flag_str, scenario_id):
            print(f"🎉 \033[1;32m¡Flag verificada localmente con éxito!\033[0m (Sesión: {seed[:6]}...)")
            return 0
        else:
            print("❌ Flag inválida para esta sesión.")
            return 1


def show_scorecard(flag_service_url: str = "http://10.0.2.20:8570") -> int:
    """Consulta y muestra el Scoreboard y métricas."""
    norm_url = flag_service_url.rstrip('/')
    try:
        req = urllib.request.Request(f"{norm_url}/api/scoreboard", headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print("=" * 60)
            print("🏆 CityLab Cyber Range — Scoreboard de Sesión")
            print(f"   Uptime: {data.get('uptime_seconds', 0)}s | Semilla: {data.get('session_seed')}")
            print("=" * 60)
            teams = data.get("teams", {})
            if not teams:
                print("   (Sin envíos registrados aún)")
            for team, info in teams.items():
                print(f"   Team: {team:<20} | Puntos: {info.get('score', 0):<5} | Resueltos: {len(info.get('solved', []))}")
            print("=" * 60)
            return 0
    except Exception as exc:
        print(f"⚠️ No se pudo conectar al Scoreboard en {norm_url}: {exc}")
        return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CityLab Scenario Runner & Flag Verification")
    parser.add_argument("--id", default="01", help="ID del escenario (ej. 01, 02)")
    parser.add_argument("--check", action="store_true", help="Evaluar estado del laboratorio y emitir flags")
    parser.add_argument("--validate-manifest", action="store_true", help="Validar YAML contra schema.json")
    parser.add_argument("--submit", default=None, help="Enviar flag para validación")
    parser.add_argument("--scorecard", action="store_true", help="Mostrar resumen del scoreboard")
    parser.add_argument("--team", default="student", help="Nombre del equipo/alumno")
    parser.add_argument("--flag-service-url", default=os.getenv("FLAG_SERVICE_URL", "http://10.0.2.20:8570"))
    parser.add_argument("--seed", default=None, help="Semilla de sesión")
    parser.add_argument("--db-path", default=None, help="Ruta a base de datos Historian SQLite")

    args = parser.parse_args(argv)

    if args.validate_manifest:
        return 0 if validate_manifest(args.id) else 2

    if args.scorecard:
        return show_scorecard(args.flag_service_url)

    if args.submit:
        return submit_flag(
            scenario_id=args.id,
            flag_str=args.submit,
            team=args.team,
            flag_service_url=args.flag_service_url,
            session_seed=args.seed,
        )

    if args.check or len(sys.argv) == 1 or (len(sys.argv) == 3 and "--id" in sys.argv):
        return run_checks(
            scenario_id=args.id,
            flag_service_url=args.flag_service_url if os.getenv("FLAG_SERVICE_URL") else None,
            session_seed=args.seed,
            db_path=Path(args.db_path) if args.db_path else None,
        )

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
