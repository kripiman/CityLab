#!/usr/bin/env python3
"""Verificación E2E de la UI ISA-101 (banda de alarmas L1 y reserva de color) con Playwright.

Ejercita el camino de polling en vivo: el estado cambia en el servidor y el `fetch` de la
propia página lo recoge, transicionando la banda L1 gris -> rojo/ámbar -> gris. Cubre el
Visualizador 2D (`viz_server`) y el HMI Industrial (`hmi_server`).

Los servidores corren bajo este mismo intérprete (solo usan la stdlib más el paquete local
`network`, vía PYTHONPATH); el driver Playwright corre en el entorno `uv`. Un stub SCADA
embebido (hilo HTTP en el propio proceso) alimenta al HMI y se conmuta a LOSS_OF_VIEW para
probar la transición, sin depender del laboratorio Mininet ni de root.

Requisitos (una sola vez, requiere red):
    uv run --with playwright -- playwright install chromium

Uso:
    uv run --with playwright -- python scripts/ui_e2e_test.py              # corre las aserciones
    uv run --with playwright -- python scripts/ui_e2e_test.py --screenshots docs/img

Sale con código 1 si alguna aserción falla. No forma parte de `./citylab.sh test` (la suite
unitaria se mantiene sin dependencias de navegador); es una verificación de UI opcional.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIZ_PORT, HMI_PORT, STUB_PORT = 18190, 18191, 18192

# Stub SCADA en proceso: sirve telemetría normal, o LOSS_OF_VIEW en el sector de agua cuando
# el test conmuta el modo. Deja al HMI mostrar SCADA ONLINE sin el laboratorio real.
_STUB_MODE = {"mode": "normal"}
_NORMAL_TELEMETRY = {
    "status": "ONLINE",
    "sectors": {
        "water": {"status": "ONLINE", "t1_level": 10.0, "t2_level": 15.0, "actuator_running": True},
        "gas": {"status": "ONLINE", "pressure_psi": 145.0, "actuator_running": True},
        "elec": {"status": "ONLINE", "grid_voltage": 230.0, "actuator_running": True},
        "transport": {"status": "ONLINE", "traffic_light": 2, "actuator_running": True},
    },
}


class _StubHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        data = json.loads(json.dumps(_NORMAL_TELEMETRY))
        if _STUB_MODE["mode"] == "lov":
            data["sectors"]["water"]["status"] = "LOSS_OF_VIEW"
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:
        pass


def _start_stub() -> HTTPServer:
    srv = HTTPServer(("127.0.0.1", STUB_PORT), _StubHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _wait_http(url: str, tries: int = 200) -> bool:
    for _ in range(tries):
        try:
            urllib.request.urlopen(url, timeout=0.5)
            return True
        except Exception:
            time.sleep(0.05)
    return False


def _post(url: str, payload: dict) -> None:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=2).close()


def _shot(page, path: str) -> None:
    """Captura ajustada al contenido: mide el alto real con un viewport corto (scrollHeight
    queda clampeado al viewport si el contenido es más bajo) y lo fija antes de capturar, así
    no queda lienzo muerto al pie. La rejilla reflota por ancho, no por alto."""
    page.set_viewport_size({"width": 1460, "height": 200})
    height = page.evaluate("Math.ceil(document.documentElement.scrollHeight)")
    page.set_viewport_size({"width": 1460, "height": height})
    page.screenshot(path=path)


def _spawn(script: str, *args: str) -> subprocess.Popen:
    cmd = [sys.executable, str(ROOT / "network" / script), "--host", "127.0.0.1", *args]
    return subprocess.Popen(cmd, cwd=str(ROOT), env=dict(os.environ, PYTHONPATH=str(ROOT)),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# Cascada IT->OT usada tanto por las aserciones como por la captura de alarma.
_CASCADE = {"sectors": {"water": {"alert": True, "pump_running": False, "tank_level": 2.0},
                        "gas": {"alert": True, "pressure_psi": 205.0, "valve_open": False},
                        "elec": {"blackout": True, "grid_voltage": 0.0},
                        "hospital": {"generator_active": True},
                        "desal": {"pump_trip": True, "tank_level_pct": 12.0, "power_kw": 0},
                        "lighting": {"power_kw": 0, "blackout": True},
                        "safety": {"sis_trip": True}}}
_SOC = {"alert_id": "SOC-ITOT-01", "name": "Cascada IT->OT: escaneo honeypot + inyeccion Modbus",
        "attacker_ip": "10.0.1.66", "severity": "CRITICAL"}
_SDN = {"mechanism": "SDN Circuit Breaker", "offending_ip": "10.0.1.66",
        "action": "ISOLATE", "rule": "Modbus write flood"}
_NORMAL = {"sectors": {"water": {"alert": False, "pump_running": True},
                       "gas": {"alert": False, "pressure_psi": 145.0, "valve_open": True},
                       "elec": {"blackout": False, "grid_voltage": 230.0},
                       "hospital": {"generator_active": False},
                       "desal": {"pump_trip": False, "tank_level_pct": 75.0, "power_kw": 45},
                       "lighting": {"power_kw": 120, "blackout": False},
                       "safety": {"sis_trip": False}}}


def run(screenshots_dir: str | None) -> int:
    results: list[tuple[str, bool]] = []

    def check(name: str, cond: bool) -> None:
        results.append((name, bool(cond)))
        print(("PASS " if cond else "FAIL ") + name)

    stub = _start_stub()
    procs = [
        _spawn("viz_server.py", "--port", str(VIZ_PORT)),
        _spawn("hmi_server.py", "--port", str(HMI_PORT), "--scada-url", f"http://127.0.0.1:{STUB_PORT}"),
    ]
    viz_url = f"http://127.0.0.1:{VIZ_PORT}"
    hmi_url = f"http://127.0.0.1:{HMI_PORT}"
    try:
        assert _wait_http(viz_url + "/"), "viz_server no levantó"
        assert _wait_http(hmi_url + "/"), "hmi_server no levantó"

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1460, "height": 900})

            # ---------------- Visualizador 2D ----------------
            page.goto(viz_url + "/")
            page.wait_for_load_state("networkidle")

            if screenshots_dir:
                _shot(page, str(Path(screenshots_dir) / "viz-normal.png"))

            check("viz banda normal = gris (alarm-band-ok)",
                  "alarm-band-ok" in (page.locator("#alarm-band").get_attribute("class") or ""))
            check("viz banda normal = SIN ALARMAS ACTIVAS",
                  page.locator("#alarm-band-count").inner_text().strip() == "SIN ALARMAS ACTIVAS")
            check("viz aguja de gas muteada (#d7dce1)",
                  page.eval_on_selector("#svg-gas-needle", "e => e.getAttribute('stroke')") == "#d7dce1")
            check("viz manómetro de gas sin arcos de semáforo",
                  page.eval_on_selector_all("path[stroke='#00e676'], path[stroke='#ff1744'][stroke-width='6']",
                                            "els => els.length") == 0)
            check("viz carga/busbar muteado (#96a1ae)",
                  page.eval_on_selector("path[d='M175 40 L195 55 L175 70 Z']",
                                        "e => e.getAttribute('fill')") == "#96a1ae")
            check("viz verde semántico del semáforo preservado (#00e676)",
                  page.eval_on_selector("#tl-green", "e => e.getAttribute('fill')") == "#00e676")

            _post(viz_url + "/api/viz/update", _CASCADE)
            _post(viz_url + "/api/viz/soc", _SOC)
            _post(viz_url + "/api/viz/sdn", _SDN)
            page.wait_for_selector("#alarm-band.alarm-band-crit", timeout=6000)
            if screenshots_dir:
                page.wait_for_timeout(200)
                _shot(page, str(Path(screenshots_dir) / "viz-alarm.png"))
            count_txt = page.locator("#alarm-band-count").inner_text()
            check("viz banda -> crítica en cascada en vivo", "CRÍTICA" in count_txt)
            check("viz banda cuenta 6 críticas + 1 advertencia",
                  "6 CRÍTICAS" in count_txt and "1 ADVERTENCIA" in count_txt)
            check("viz banda nombra el área afectada (Agua)",
                  "Agua" in page.locator("#alarm-band-areas").inner_text())

            _post(viz_url + "/api/viz/update", _NORMAL)
            page.wait_for_selector("#alarm-band.alarm-band-ok", timeout=6000)
            check("viz banda -> gris de nuevo al despejar",
                  "alarm-band-ok" in (page.locator("#alarm-band").get_attribute("class") or ""))

            # ---------------- HMI Industrial ----------------
            _STUB_MODE["mode"] = "normal"
            page.goto(hmi_url + "/")
            page.wait_for_load_state("networkidle")
            page.wait_for_selector("#badge-scada.badge-ok", timeout=6000)

            if screenshots_dir:
                _shot(page, str(Path(screenshots_dir) / "hmi.png"))

            check("hmi banda normal = gris",
                  "alarm-band-ok" in (page.locator("#alarm-band").get_attribute("class") or ""))
            check("hmi busbar ya no es ámbar (#ffeb3b ausente)",
                  page.eval_on_selector_all("[stroke='#ffeb3b']", "els => els.length") == 0)
            check("hmi título de consola no es ámbar fijo",
                  page.eval_on_selector(".alarm-panel h3", "e => getComputedStyle(e).color") != "rgb(240, 160, 0)")

            _STUB_MODE["mode"] = "lov"
            page.wait_for_selector("#alarm-band.alarm-band-crit", timeout=8000)
            check("hmi banda -> crítica en loss-of-view en vivo",
                  "CRÍTICA" in page.locator("#alarm-band-count").inner_text())
            check("hmi banda nombra el área WATER",
                  "WATER" in page.locator("#alarm-band-areas").inner_text())

            _STUB_MODE["mode"] = "normal"
            page.wait_for_selector("#alarm-band.alarm-band-ok", timeout=8000)
            check("hmi banda -> gris de nuevo tras recuperación",
                  "alarm-band-ok" in (page.locator("#alarm-band").get_attribute("class") or ""))

            browser.close()
    finally:
        stub.shutdown()
        for pr in procs:
            pr.terminate()
        for pr in procs:
            try:
                pr.wait(timeout=5)
            except Exception:
                pr.kill()

    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n==== {passed}/{total} verificaciones OK ====")
    if screenshots_dir:
        print(f"Capturas escritas en {screenshots_dir}/ (viz-normal.png, viz-alarm.png, hmi.png)")
    if passed != total:
        print("FALLOS:", [n for n, ok in results if not ok])
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="E2E Playwright de la UI ISA-101 (banda de alarmas + reserva de color).")
    parser.add_argument("--screenshots", metavar="DIR",
                        help="Además de verificar, regenera viz-normal/viz-alarm/hmi .png en DIR.")
    args = parser.parse_args()
    if args.screenshots:
        Path(args.screenshots).mkdir(parents=True, exist_ok=True)
    return run(args.screenshots)


if __name__ == "__main__":
    sys.exit(main())
