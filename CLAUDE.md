# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

CityLab is a software-only **cyber-physical cyber range**: a Mininet-emulated IEC 62443 network of critical-infrastructure sectors (water, gas, electric, transport, hospital) that Red Team scripts attack and a Blue Team SIEM/SCADA stack defends. It ships 29 CTF scenarios. The code is a mix of protocol emulators, physics models, HELICS co-simulation, and attack scripts.

## Golden rule — intentional vulnerabilities

Findings **F-03, F-05, F-06, F-07 are deliberate CTF material.** Never "fix", close, or harden them. They are pedagogical and gated behind toggles (e.g. `STRICT_AUTH=0` is the default permissive mode; `STRICT_AUTH=1` is the hardened mode). When touching auth/RBAC/segmentation, preserve the toggle and both branches. Treat these as features, not bugs.

## Commands

**`./citylab.sh` is the single entrypoint.** It sets `PYTHONPATH` for you and wraps every operation:

```bash
sudo ./citylab.sh up [--phase N]   # deploy the lab (default phase 3; delegates to run_phase*.sh)
sudo ./citylab.sh down             # kill all federates/emulators/servers + `mn -c`
./citylab.sh smoke [--phase N]     # HELICS co-simulation, no root (phase 7 default = 10 federates)
./citylab.sh test [pytest args]    # unit-test suite
./citylab.sh profile               # REAL RSS/CPU measurement of live components
./citylab.sh status                # what is running right now
```

The `run_phase*.sh` scripts are now internal implementation invoked by `up`; do not document them as the entrypoint.

- **Run the unit tests** (no root needed — they use mocks, not Mininet). Prefer `./citylab.sh test`; the raw form is:
  ```bash
  PYTHONPATH=. python3 -m pytest network/tests plc/tests physical helics_sim attacker/tests -q
  ```
  `PYTHONPATH=.` is **mandatory** — there is no `pyproject.toml`/`setup.py`, and all imports are absolute package paths (`from network.x import ...`, `from plc.x import ...`). Running pytest without it fails to import.
- **Run a single test:**
  ```bash
  PYTHONPATH=. python3 -m pytest attacker/tests/test_scenario_21_loss_of_view.py::TestScenario21LossOfView::test_hmi_detects_loss_of_view_alarm
  ```
- **The five test suites** are `network/tests`, `plc/tests`, `physical`, `helics_sim`, `attacker/tests`.
- **Bring up the full lab** (requires root — Mininet + Open vSwitch): `sudo ./citylab.sh up`. Lower-level entry points, when you need them directly:
  ```bash
  sudo python3 network/topology.py          # interactive Mininet CLI
  sudo python3 network/topology.py --test    # automated firewall connectivity checks, then exit
  sudo ./citylab.sh down                     # cleanup, including `mn -c`, before a fresh run
  ```
- **End-to-end validation harness** (root only; exits 0 as a no-op if not root):
  ```bash
  sudo ./scripts/validate_e2e.sh
  ```
- **Install dependencies:** `./install_deps.sh`. It installs Python packages **system-wide on purpose** — Mininet host processes run under `sudo`, so `pip --user` packages are not visible inside the network namespaces. Mininet, Open vSwitch, and GridLAB-D are system packages, not pip; `pymodbus` is pinned to `2.5.3` (v3.x has an incompatible API — the code has fallback imports for both).
- **Resource figures:** every `~N MB` in the docs is a design estimate. The measured number comes from `./citylab.sh profile` (`scripts/profile_resources.py`), which samples RSS/CPU of live CityLab processes into `logs/resource_profile_summary.txt`. Never present an unmeasured figure as measured.
- **Knowledge graph:** `graphify-out/` holds a prebuilt graph. Prefer `graphify query "<question>"` for codebase questions, and run `graphify update .` after modifying code to keep it current.

## Architecture — the big picture

The system is three layers that only fully connect when the lab is running under root:

1. **Network emulation — `network/topology.py` is the spine.** It builds five IEC 62443 zones (Corporate `10.0.1.0/24`, DMZ `10.0.2.0/24`, OT cell `10.0.3.0/24`, EWS PAW `10.0.4.0/24`, Honeypot `10.0.5.0/24`) bridged by a single multi-homed firewall host `fw` that enforces segmentation with iptables (`FORWARD DROP` default). Only `h_scada` (10.0.2.20) and `h_ews` (10.0.4.30) may reach the OT zone; Corporate→OT is explicitly dropped. **GOOSE has no firewall rule by design** — L2 substation attacks require first pivoting into the OT segment. On `net.start()` the topology **auto-spawns every emulator into the correct host namespace** (guarded by `AUTO_START_PLC=1`), passing explicit `--host` values.

2. **Protocol emulators run as daemons inside those namespaces.** `plc/modbus_emulator.py` (per-sector PLCs on :502), `plc/dnp3_emulator.py` (:20000), `plc/iec61850_emulator.py` (GOOSE/SV on :10102/:10103), `plc/opcua_emulator.py` (:4840), `plc/honeypot_server.py` (:502 decoy), and `network/ad_dc_emulator.py` (LDAP/Kerberos/SMB on :389/:88/:445). Each emulator's bind host defaults to `0.0.0.0` via a `BIND_HOST` / `<PROTO>_HOST` env chain; inside an isolated namespace this is safe, and `topology.py` passes `--host 0.0.0.0` explicitly. **Port 502 is privileged** — running a Modbus emulator standalone without root fails to bind.

3. **Cyber-physical cascade — `physical/` + `helics_sim/`.** Physics models (`physical/elec/grid_elec.py` swing equation, `physical/water/`, `physical/gas/`, `physical/transport/traffic.py`, `physical/hospital/`) are coordinated in real time by HELICS 3.x federates in `helics_sim/` (`fed_*.py`, one per sector plus a logger). This is how an OT attack propagates into a physical consequence (e.g. blackout). Note: the IEC 61850 breaker emulator and the electrical physics model each keep their own breaker state and are not directly wired together in code.

### Defensive stack (DMZ/Blue Team)

- `network/scada_server.py` — polls all sector PLCs over Modbus (`poll_plcs()` loop calling the extracted `poll_plcs_once()`), serves telemetry over HTTP :8080, and enforces RBAC via `network/rbac.py`. It carries the **Loss-of-View watchdog** (`_consecutive_failures`, threshold 3 → `LOSS_OF_VIEW`).
- `network/hmi_server.py` — derives an operator overview/alarms from the SCADA telemetry.
- `network/siem_pipeline.py` — SOC correlation engine. Rule 1 = cascading IT→OT (honeypot scan + Modbus injection); Rule 2 = GOOSE spoofing (Industroyer2 pattern). Correlation is driven by ingested events, not auto-hooked into the attack scripts.
- `network/sdn_controller.py` — OpenFlow circuit-breaker mitigation (`execute_sdn_mitigation`, `--isolate-ip`).

### Attack scripts & scenarios

`attacker/attack_*.py` implements the 29 scenarios, each mapped 1:1 to `docs/scenarios/scenario_NN_*.md`. **Most attack scripts are standalone simulations**: they self-report success (tabletop/onboarding value) without contacting a real device. A subset (cascading blackout, GOOSE spoofing, Modbus coil write, guided pivoting, live SDN defense) only exercise real behavior with the lab running under root. When auditing, verify a script actually reaches a device before treating its "SUCCESS" as end-to-end.

## Gotchas

- Unit tests never touch Mininet; the lab-dependent scenarios cannot be validated without `sudo` + Mininet + an OVS/HELICS runtime.
- Scenario docs sometimes describe higher-fidelity mechanisms than the code implements (real Kerberos vs. in-process RBAC, multicast GOOSE vs. loopback UDP). Check the code before trusting a doc step's ports/commands/endpoints.
- Deeper design docs live in `docs/ERS.md`, `docs/ARCHITECTURE.md`, and `docs/OPERATIONS.md`.

## Git Commits and SemVer Tagging Rule (MANDATORY)

- **Always tag every commit**: Whenever generating a git commit, **always** generate its respective annotated git tag on that exact commit.
- **Format**: `vX.Y.Z` adhering to Semantic Versioning (SemVerTag):
  - **X (Major)**: Breaking / incompatible changes or major architecture shifts.
  - **Y (Minor)**: New backward-compatible features, scenarios, federates, or enhancements.
  - **Z (Patch)**: Bug fixes, test stabilization, documentation fixes, anti-trampa corrections.
- **Command pattern**:
  ```bash
  git commit -m "<type>(<scope>): <clear description>"
  git tag -a vX.Y.Z -m "vX.Y.Z: <summary of changes>"
  ```

