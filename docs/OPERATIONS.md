# 🛠️ CityLab — Guía de Operaciones y Validación (Runbook Integral)

Manual operativo para despliegue, ejecución, pruebas automatizadas y validación de seguridad en el Cyber Range CityLab.

---

## 1. Comandos de Ciclo de Vida del Cyber Range (`./citylab.sh`)

`./citylab.sh` es el punto de entrada unificado para administrar el laboratorio.

### 🚀 Despliegue Completo (Co-Simulación HELICS + Red Mininet)

```bash
# Despliegue interactivo completo (Fase 3: 7 federados + Mininet + DMZ + OT + AD DC)
sudo ./citylab.sh up

# Despliegue por fases específicas
sudo ./citylab.sh up --phase 1   # Nodo mínimo viable (Water SWaT)
sudo ./citylab.sh up --phase 2   # Co-simulación multisectorial
sudo ./citylab.sh up --phase 3   # Ciudad completa (por defecto)
```

### 🔍 Inspección de Estado
```bash
./citylab.sh status
```
Muestra todos los procesos activos (HELICS broker, federados físicos, emuladores Modbus/DNP3/IEC61850/OPCUA, SCADA, HMI, SIEM y proxy).

### 🛑 Detención y Limpieza Completa
```bash
sudo ./citylab.sh down
```
Detiene de forma limpia todos los procesos huérfanos (SIGTERM/SIGKILL) y desmonta switches, enlaces e interfaces virtuales de Mininet (`mn -c`).

---

## 2. Acceso a Servicios y Dashboards de Supervisión

| Servicio | URL / Socket | Método / Protocolo | Autenticación (`STRICT_AUTH=1`) |
|---|---|---|---|
| **SCADA REST API** | `http://10.0.2.20:8080/api/telemetry` | `GET` | `Authorization: Bearer operator:OP_TOKEN_2026` |
| **Control SCADA** | `http://10.0.2.20:8080/api/control` | `POST` JSON | `Authorization: Bearer engineer:ENG_TOKEN_2026` |
| **Cluster HA Status**| `http://10.0.2.20:8080/api/ha/status` | `GET` | Libre / Consulta de estado |
| **HMI Web Dashboard** | `http://10.0.2.20:8085` | `GET` HTTP | Interfaz visual P&ID integrada |
| **Visualizador 2D SVG**| `http://10.0.2.20:8090` | `GET` HTTP / SVG | Dashboard ciberfísico interactivo airgapped (8 sectores) |
| **Viz API Telemetría** | `http://10.0.2.20:8090/api/viz/frame` | `GET` JSON | Frame en vivo para visualizador y herramientas externas |
| **SIEM HTTP Ingest** | `http://10.0.2.20:8514` | `POST` JSON | Endpoint de ingesta de eventos |
| **Flag & Scoreboard**| `http://10.0.2.20:8570` | `GET`/`POST` REST | Flags dinámicas HMAC + Scoreboard MTTD/MTTR |
| **Modbus DPI Proxy** | `10.0.2.20:15020` | Modbus TCP | Demuxing transparente por Unit ID |

### Ejemplos de Interacción por Consola

```bash
# Consultar telemetría consolidada de sectores en SCADA
curl -s http://10.0.2.20:8080/api/telemetry | jq .

# Consultar cuadro de estado en tiempo real del visualizador 2D (8 sectores)
curl -s http://10.0.2.20:8090/api/viz/frame | jq .

# Ejecutar conmutación de actuador con token de ingeniero
curl -s -X POST http://10.0.2.20:8080/api/control \
  -H "Authorization: Bearer engineer:ENG_TOKEN_2026" \
  -H "Content-Type: application/json" \
  -d '{"sector": "water", "action": "set_pump", "value": 1}' | jq .

# Lanzar puente de telemetría en modo Standalone (SCADA Poller con Bearer Token)
python3 helics_sim/fed_viz_bridge.py --standalone --viz-url http://127.0.0.1:8090
```

> **Nota — escritura Modbus real requiere origen EWS**: con `USE_MODBUS_PROXY=1` (default bajo `sudo ./citylab.sh up`), el Proxy DPI Modbus solo acepta escrituras (FC5/6/15/16) desde `h_ews` (`10.0.4.30`) — `h_scada` (de donde salen la HMI web y la app de escritorio) puede leer pero no escribir (control COMP-01, IEC 62443 SR 3.5). Un botón de control rechazado por esto lo indica explícitamente en pantalla. Ver **[Guía de Pivote a EWS](EWS_PIVOT_GUIDE.md)** para operar desde EWS.

### Shell Interactiva Completa por Host (`clear`, `nano`, `vim`, tab-completion, Ctrl+C)

El prompt `mininet>` en sí **no** sirve para esto: cada `mininet> h_X <comando>` es un relay de un solo comando (`Node.cmd()` espera un sentinel de fin y recién ahí devuelve la salida) — no hay un pty interactivo recibiendo tus teclas en vivo, así que programas de pantalla completa (`nano`, `vim`, `htop`, `less`) fallan o cuelgan ahí. Para una terminal de verdad, dos métodos nativos de Mininet, sin código nuevo:

**Opción 1 — `xterm` desde el prompt** (requiere X11; ya es prerrequisito del proyecto vía `xhost +SI:localuser:root`):
```
mininet> xterm h_ews
```
Abre una ventana de terminal real adjunta al namespace de red de `h_ews` (o cualquier host). Todo funciona como en tu terminal normal: `clear`, `nano`, `vim`, historial, tab-completion, Ctrl+C.

**Opción 2 — adjuntar tu terminal actual** (desde un shell real, fuera del prompt `mininet>`):
```bash
sudo mnexec -a $(pgrep -f 'mininet:h_ews') bash
```
`mnexec -a <pid>` (ver `mnexec -h`) adjunta al namespace de red y mount del pid dado y ejecuta el comando directo sobre tu stdin/stdout/stderr reales — sin relay, sin pty intermedio. Los hosts de Mininet en este proyecto no tienen filesystem propio (`network/topology.py` no usa `privateDirs` ni `chroot` ni `cls=` en ningún host) — comparten el filesystem real de la máquina, solo cambia el namespace de red, así que cualquier shell/binario instalado en el sistema (`bash`, `nano`, `vim` — confirmado presentes; `zsh`/`htop` no vienen instalados por defecto) funciona igual ahí adentro. `exit` o Ctrl+D te devuelve a tu terminal normal sin afectar la red ni el host.

Reemplazá `h_ews` por cualquier otro host (`h_scada`, `h_attacker`, `h_plc`, etc.) según lo que necesites inspeccionar o editar.

---

## 3. Pruebas y Validación Automatizada

### 🧪 1. Suite de Pruebas Unitarias e Integración (Pytest)
Ejecuta la suite completa de 265 pruebas unitarias y de integración (con `PYTHONPATH=.` obligatorio):
```bash
PYTHONPATH=. pytest network/tests plc/tests physical helics_sim attacker/tests -q
# Salida esperada: 265 passed in ~50s
```

### 💨 2. Smoke Tests de Co-Simulación HELICS (Sin necesidad de root)
Verifica la física acoplada y la sincronización de mensajes entre federados con temporizador global de 120 segundos:
```bash
# Smoke test Fase 4 (9 federados)
./citylab.sh smoke --phase 4     # 9/9 federates EXIT=0 (~7s)

# Smoke test Fase 7 (10 federados, incluye SIS SIL-3 y Desalinizadora)
./citylab.sh smoke --phase 7     # 10/10 federates EXIT=0 (~6s)
```

### 🌐 3. Arnés de Validación End-to-End en Mininet Real (Requiere sudo)
Ejecuta el ciclo de vida completo: firewall OVS, sockets OT reales, ataque GOOSE, alerta SIEM y mitigación SDN Circuit Breaker:
```bash
sudo ./scripts/validate_e2e.sh
```

### 🛡️ 4. Test Rápido de Conduits de Red Mininet
Valida exclusivamente las 7 reglas de firewall y conduits de microsegmentación:
```bash
sudo python3 network/topology.py --test
```

### 📊 5. Profiling y Medición de Memoria / CPU
Mide el consumo real de RAM (RSS) y procesador:
```bash
./citylab.sh profile
cat logs/resource_profile_summary.txt
```

### 🧹 6. Verificación Estricta de Ausencia de Procesos Huérfanos
Tras cualquier prueba en Mininet o desmontaje con `./citylab.sh down`, verifica la ausencia total de procesos residuales:
```bash
ps -eo pid,args | grep -E "modbus_emulator|dnp3_emulator|iec61850_emulator|opcua_emulator|honeypot_server|ad_dc_emulator|scada_server|hmi_server|viz_server|siem_pipeline|modbus_proxy|flag_service|fed_|helics_broker" | grep -v grep | wc -l
# Salida obligatoria esperada: 0
```

---

## 4. Matriz de Escenarios CTF / Ataques Industriales

El Cyber Range incluye un currículo formativo completo de **29 escenarios CTF** documentados en [`docs/scenarios/`](file:///home/kripi/Documentos/GitHub/CityLab/docs/scenarios) (`scenario_01_*.md` a `scenario_29_*.md`). Destacan entre ellos:
- [⚡ **Escenario 01**: Apagón Urbano en Cascada](scenarios/scenario_01_cascading_blackout.md)
- [🛡️ **Escenario 02**: Inyección y Spoofing de Mensajes GOOSE IEC 61850](scenarios/scenario_02_goose_spoofing.md)
- [📉 **Escenario 03**: Ataque Low and Slow al Sistema SIS SIL-3](scenarios/scenario_03_triton_low_slow.md)
- [🔄 **Escenario 04**: Replay Attack Modbus Tipo Stuxnet](scenarios/scenario_04_stuxnet_replay.md)
- [🔄 **Escenario 05**: Conmutación y Failover en Cluster SCADA HA](scenarios/scenario_05_dcs_failover.md)
- [🔑 **Escenario 06**: Kerberoasting y Abuso de Samba Active Directory](scenarios/scenario_06_kerberoast_ad.md)
- [🌐 **Escenario 17**: Exploración y Tour de la API HMI/SCADA](scenarios/scenario_17_scada_tour_api.md)
- [🔀 **Escenario 19**: Cadena de Pivoteo Attacker $\to$ DMZ $\to$ OT](scenarios/scenario_19_guided_pivoting_chain.md)
- [👁️ **Escenario 21**: Pérdida de Visibilidad (*Loss of View*) y Aislamiento](scenarios/scenario_21_loss_of_view_manual_isolation.md)
- [🧱 **Escenario 23**: Defensa Dinámica con Controlador SDN y Circuit Breaker](scenarios/scenario_23_live_sdn_defense_under_fire.md)

---

## 5. Evaluación de Objetivos, Flags Dinámicas y Métricas SOC

CityLab utiliza un motor de evaluación server-side basado en manifiestos YAML (`config/scenarios/scenario_NN.yml`) y flags HMAC generadas dinámicamente a partir de la semilla de sesión `CITYLAB_SESSION_SEED`.

### 🏁 Evaluación y Emisión de Flags por Estado Real
```bash
# Validar el cumplimiento de objetivos de un escenario (ej. 01)
python3 scripts/run_scenario.py --id 01 --check

# Validar el manifiesto YAML contra schema.json
python3 scripts/run_scenario.py --id 01 --validate-manifest

# Enviar una flag para validación oficial
python3 scripts/run_scenario.py --id 01 --submit "FLAG_1{4f8a9b2c1d3e}" --team "estudiante_1"
```

### 🏆 Scoreboard y Métricas SOC Automatizadas (MTTD / MTTR)
```bash
# Consultar métricas de tiempo medio de detección y mitigación
python3 network/scoreboard.py

# Ver el Scoreboard consolidado de la sesión
python3 scripts/run_scenario.py --scorecard
```


