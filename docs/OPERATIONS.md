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
| **Viz 2D/3D Server** | `http://10.0.2.20:8090/api/viz/frame` | `GET` HTTP | Telemetría para renderizado visual |
| **SIEM HTTP Ingest** | `http://10.0.2.20:8514` | `POST` JSON | Endpoint de ingesta de eventos |
| **Flag & Scoreboard**| `http://10.0.2.20:8570` | `GET`/`POST` REST | Flags dinámicas HMAC + Scoreboard MTTD/MTTR |
| **Modbus DPI Proxy** | `10.0.2.20:15020` | Modbus TCP | Demuxing transparente por Unit ID |

### Ejemplos de Interacción por Consola

```bash
# Consultar telemetría consolidada de sectores
curl -s http://10.0.2.20:8080/api/telemetry | jq .

# Ejecutar conmutación de actuador con token de ingeniero
curl -s -X POST http://10.0.2.20:8080/api/control \
  -H "Authorization: Bearer engineer:ENG_TOKEN_2026" \
  -H "Content-Type: application/json" \
  -d '{"sector": "water", "action": "set_pump", "value": 1}' | jq .
```

---

## 3. Pruebas y Validación Automatizada

### 🧪 1. Suite de Pruebas Unitarias e Integración (Pytest)
Ejecuta la suite completa de 200 pruebas unitarias y de integración:
```bash
pytest network/tests plc/tests physical helics_sim attacker/tests -q
# Salida esperada: 200 passed in ~42s
```

### 💨 2. Smoke Tests de Co-Simulación HELICS (Sin necesidad de root)
Verifica la física acoplada y la sincronización de mensajes entre federados:
```bash
# Smoke test Fase 4 (9 federados)
./citylab.sh smoke --phase 4     # 9/9 federates EXIT=0

# Smoke test Fase 7 (10 federados, incluye SIS SIL-3 y Desalinizadora)
./citylab.sh smoke --phase 7     # 10/10 federates EXIT=0
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


