# 🏙️ CityLab — Cyber Range Ciberfísico Multisectorial (Fase 9 Ciudad Completa)

[![Standard](https://img.shields.io/badge/Standard-IEC%2062443%20%7C%20NIST%20800--82r3-blue.svg)](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa62443)
[![Purdue Model](https://img.shields.io/badge/Architecture-Purdue%20PERA%20(L0--L4)-orange.svg)](#-arquitectura-de-red-iec-62443)
[![Tests](https://img.shields.io/badge/Tests-272%20PASS%20(100%25)-brightgreen.svg)](#-pruebas)
[![Stack](https://img.shields.io/badge/Stack-Mininet%20%7C%20OVS%20%7C%20Python-purple.svg)](#-arquitectura-de-red-iec-62443)
[![Co-Simulation](https://img.shields.io/badge/Co--Simulation-HELICS%203.x%20(11%20Feds)-red.svg)](https://helics.org/)
[![Memory](https://img.shields.io/badge/RAM%20Footprint-%3C1.5%20GB-success.svg)](#6-medir-el-consumo-real-de-recursos)

**CityLab** es un entorno de entrenamiento ciberfísico (*Cyber Range*) 100% basado en software, diseñado para simular ataques ofensivos (Red Team / Hacking Ético) y monitoreo defensivo (Blue Team) sobre infraestructuras críticas urbanas e interdependencias ciberfísicas en cascada.

- **0% Sobrecarga de Máquinas Virtuales**: Ejecución nativa en Linux mediante Mininet y procesos distribuidos.
- **Eficiencia de Recursos**: Consumo de memoria RAM total $<1.5\text{ GB}$ base ($<8.0\text{ GB}$ con ciudad completa en estrés).
- **Co-Simulación Multisectorial**: Coordinación temporal a tiempo real vía **HELICS 3.x** (hasta 11 federados).
- **Estándar Industrial**: Segmentación de red alineada con **IEC 62443** (Zonas Corporate, DMZ, Celda OT, PAW EWS y Decoy Honeypot).
- **Visualizador 2D Airgapped**: Dashboard interactivo vectorial SVG/CSS en tiempo real (puerto `:8090`), 100% offline sin dependencias externas.
- **Fiabilidad y Calidad de Código**: **272 tests unitarios e integración PASS** y 0 procesos huérfanos garantizados tras teardown.

---

## ✅ Requisitos Previos

- **Sistema Operativo**: Linux. `install_deps.sh` da soporte nativo a Fedora/Nobara/RHEL (`dnf`), Ubuntu/Debian/Mint (`apt`) y Arch/Manjaro (`pacman`).
- **Python 3** con `pip`.
- **Mininet** y **Open vSwitch** — paquetes de sistema (no se instalan vía `pip`); los instala `install_deps.sh`.
- **Acceso `sudo`/root** — solo necesario para `sudo ./citylab.sh up` y `sudo ./citylab.sh down` (Mininet + Open vSwitch crean namespaces de red reales). `./citylab.sh test`, `./citylab.sh smoke` y `./citylab.sh profile` **no** requieren root.
- **GridLAB-D** *(opcional, instalación manual)*: habilita el flujo de potencia eléctrico real de alta fidelidad (`helics_sim/gridlabd_federate.py` + `gridlabd/*.glm`). `install_deps.sh` **no** lo instala — sin él, el sector eléctrico sigue operando con la ecuación de swing simulada.
- **HELICS 3.x** — se instala vía `pip` como parte de `install_deps.sh` / `requirements.txt`.

---

## 🔧 Instalación

```bash
git clone <url-del-repositorio> CityLab
cd CityLab
./install_deps.sh
```

`install_deps.sh` detecta la distribución automáticamente e instala los paquetes Python **a nivel de sistema** (no `pip --user`) a propósito: los procesos de Mininet corren bajo `sudo`, y los paquetes de usuario no son visibles dentro de los namespaces de red que Mininet crea. Al finalizar, verifica con:

```bash
sudo ovs-vsctl show                        # Open vSwitch activo
sudo python3 network/topology.py --test    # chequeos automáticos de conectividad del firewall
```

---

## 📦 Dependencias a Utilizar

**Paquetes de sistema** (no vía `pip`): `mininet`, `openvswitch`, más herramientas usadas por los escenarios de ataque (`nmap`, `hydra`, `wireshark-cli`/`tshark`, `sshpass`).

**Paquetes Python** (fijados por versión en `requirements.txt`, instalados system-wide por `install_deps.sh`):

| Paquete | Versión | Uso |
|---|---|---|
| `pymodbus` | `3.6.4` | Protocolo Modbus/TCP (PLCs, SCADA, proxy DPI); el código mantiene *fallback imports* compatibles con la API 2.x |
| `helics` | `3.4.0` | Co-simulación ciberfísica entre federados |
| `scapy` | `2.6.1` | Construcción/inspección de paquetes para escenarios ofensivos |
| `python-dotenv` | `1.1.0` | Carga de variables de entorno |
| `psutil` | `>=5.9` | Medición real de RSS/CPU (`./citylab.sh profile`); si falta, cae a `/proc` y `resource.getrusage` de la stdlib |

**Opcional**: GridLAB-D (binario de sistema, ver Requisitos Previos). ICSSIM/MiniCPS se documentan como alternativas de simulación física en `requirements.txt` pero no son necesarios para el flujo estándar.

---

## 🔐 Variables de Entorno

CityLab lee más de 50 variables de entorno internas (multiprotocolo, HA, SIEM, AD/Kerberos, etc.) directamente en cada módulo. Las que más importan para el uso diario:

| Variable | Rol | Default |
|---|---|---|
| `PYTHONPATH` | **Obligatoria** para tests y ejecución directa — todos los imports son rutas absolutas de paquete (`from network.x import ...`) | *(usar `PYTHONPATH=.`)* |
| `STRICT_AUTH` | Alterna el modo RBAC del SCADA/HMI: `0` = permisivo (default, sustenta los hallazgos CTF F-03/F-05/F-06/F-07), `1` = reforzado | `0` |
| `AUTO_START_PLC` | Si `1`, `topology.py` autoarranca todos los emuladores de protocolo al levantar Mininet | `1` |
| `USE_MODBUS_PROXY` | Si `1`, `scada_server.py` sondea los PLC vía el proxy DPI (`:15020`) en lugar de conexión directa | `0` |
| `HELICS_STANDALONE` | Fuerza a un federado a correr sin broker HELICS (modo aislado / fallback) | `0` |
| `HELICS_BROKER_ADDRESS` / `HELICS_BROKER_PORT` | Host y puerto del broker HELICS (ZMQ) | `127.0.0.1` / `23404` |
| `SCADA_API_TOKEN`, `SCADA_TOKEN_ENGINEER`, `SCADA_TOKEN_OPERATOR`, `SCADA_TOKEN_AUDITOR` | Tokens RBAC estáticos por rol (`Authorization: Bearer <role>:<token>`) | ver `network/rbac.py` |
| `VIZ_HTTP_URL` / `VIZ_URL` | URL del Visualizador 2D; usada por `fed_viz_bridge.py`, `siem_pipeline.py` y `sdn_controller.py` para notificarle alertas y mitigaciones | `http://127.0.0.1:8090` |
| `SIEM_HTTP_URL` | URL del colector SIEM central | `http://10.0.2.20:8514` |
| `HA_ROLE` / `HA_PEER_URL` | Rol del nodo SCADA en el cluster HA (`PRIMARY`/`STANDBY`) y URL de su par | `PRIMARY` / *(vacío)* |

---

## ⚡ Ejecución

`./citylab.sh` es el **punto de entrada único** del laboratorio. Los scripts `run_phase*.sh` quedan como implementación interna a la que delega `up`.

```bash
./citylab.sh help                  # todos los subcomandos
```

### 1. Iniciar la Co-Simulación Completa (Fase 3)
```bash
sudo ./citylab.sh up
```

### 2. Acceder a los Dashboards (Web y Desktop Nativo)
Una vez iniciado el laboratorio (`sudo ./citylab.sh up`), ambos dashboards web son accesibles directamente desde tu navegador:
- **Visualizador Urbano 2D SVG**: [http://10.0.2.20:8090](http://10.0.2.20:8090) (o `http://127.0.0.1:8090` en modo local/mock).
- **HMI Industrial OpenSCADA**: [http://10.0.2.20:8085](http://10.0.2.20:8085) (diagrama P&ID, mandos y consola de alarmas).

> **Enrutamiento DMZ**: El host anfitrión adquiere automáticamente una interfaz directa (`10.0.2.2/24`) en el switch DMZ `s2` (el mismo mecanismo utilizado en `s3` para la co-simulación de la Celda OT), permitiendo acceso HTTP directo hacia `h_scada` (`10.0.2.20`).

- **Aplicación Desktop Nativa (`network/citylab_gui.py`)**:
  Se despliega en ventana dividida (HMI a la izquierda / Visualizador 2D a la derecha). Para entornos X11 bajo sudo, autoriza el acceso gráfico local antes de iniciar:
  ```bash
  xhost +SI:localuser:root
  ```
  *(En entornos headless/servidor sin display, puede omitirse con `AUTO_START_GUI=0 sudo ./citylab.sh up`).*

### 3. Co-Simulación HELICS sin root (Fase 7 — 10 federados, incluye SIS SIL-3)
```bash
./citylab.sh smoke
```

### 4. Ejecutar la Batería de Pruebas
```bash
./citylab.sh test
```
Ver la sección [🧪 Pruebas](#-pruebas) más abajo para el detalle completo (suites, ejecución de un test individual, etc.).

### 5. Inspeccionar el Log CSV de Eventos en Tiempo Real
```bash
tail -f logs/cascading_events.csv
```

### 6. Medir el Consumo Real de Recursos
```bash
./citylab.sh profile               # RSS/CPU medidos -> logs/resource_profile_summary.txt
```

### 7. Detener y Limpiar (Garantía de 0 Procesos Huérfanos)
```bash
sudo ./citylab.sh down             # mata federados/emuladores/servicios + mn -c
```

---

## 🗂️ Estructura del Proyecto

```
CityLab/
├── network/            # SCADA, HMI, Viz 2D, SIEM, SDN, RBAC, historian, topología Mininet
├── plc/                # Emuladores de protocolo: Modbus, DNP3, IEC 61850, OPC UA, honeypot
├── physical/           # Modelos físicos por sector (elec, gas, water, transport, hospital)
├── helics_sim/         # Federados HELICS (fed_*.py) + puente de telemetría al visualizador
├── attacker/           # Scripts de ataque Red Team (attack_*.py) y su suite de tests
├── config/scenarios/   # Manifiestos YAML de los 29 escenarios CTF + schema.json
├── docs/                # ERS, ARCHITECTURE, OPERATIONS, guías por federado y por escenario
├── scripts/              # Perfilado de recursos, generación de manifiestos, validación E2E
├── gridlabd/              # Modelos .glm de la subestación (normal / disparada)
├── graphify-out/           # Grafo de conocimiento del repo (graph.json, GRAPH_REPORT.md, wiki)
├── logs/                    # Salidas en tiempo de ejecución (eventos en cascada, perfiles)
├── citylab.sh                # Punto de entrada único (up / down / test / smoke / profile / status)
├── install_deps.sh             # Instalador multi-distro de dependencias de sistema y Python
└── requirements.txt              # Paquetes Python fijados por versión
```

---

## 🏛️ Estructura de Infraestructura y Sectores Emulados

| Sector | Componente Físico | Dirección IP OT | Control PLC / Protocolo |
|---|---|---|---|
| 💧 **Agua** | Planta SWaT 2-Etapas (Tanque T1 Sedimentación + T2 Distribución) | `10.0.3.10:502` (`h_plc`) | Modbus/TCP (Coil 0: Bombas P1/P2) |
| 🔥 **Gas** | Red de Gasoducto y Válvula de Presión ($145\text{ PSI}$) | `10.0.3.12:502` (`h_plc_gas`) | Modbus/TCP (Coil 0: Válvula Control) |
| ⚡ **Energía** | Ecuación de Swing Síncrona + Subestación GridLAB-D $13.8\text{ kV}$ | `10.0.3.13:502` (`h_plc_elec`) / `10.0.3.13:20000` | Modbus/TCP + DNP3 Outstation (CROB / SA L1) |
| 🚥 **Transporte** | Intersección Semafórica 4-Fases + Modo Emergencia | `10.0.3.14:502` (`h_plc_trans`) | Modbus/TCP (Coil 1: Corredor Emergencia)|
| 🏥 **Salud** | Hospital Crítico ($850\text{ kW}$) + Failover UPS / Generador ATS | `10.0.3.15:502` (`h_plc_hosp`) | Modbus/TCP + Suscriptor HELICS Automático |
| 🌊 **Desalinizadora** | Planta de Ósmosis Inversa (Bomba Alta Presión + Tanque Permeado) | `10.0.3.16:502` (`h_desal`) | Modbus/TCP + Federado `fed_desal.py` |
| 💡 **Alumbrado** | Red de Iluminación Inteligente Municipal ($120\text{ kW}$) | `10.0.3.17:502` (`h_lighting`) | Modbus/TCP + Federado `fed_lighting.py` |
| 🛡️ **Seguridad SIS** | Sistema Instrumentado de Seguridad (SIL-3 Interlocks) | Suscriptor / Publicador HELICS | Federado `fed_sis.py` (`sis/trip`, `desal/pump_trip`) |
| ⚡ **IED Subestación** | Bahía de Transformador y Disyuntor XCBR1 | `10.0.3.20:10102` (`h_ied`) | IEC 61850 GOOSE (`239.0.0.1`) & SV (`239.0.0.2`) |
| 🌐 **Gateway OPC UA** | Concentrador de Telemetría OT | `10.0.3.30:4840` (`h_gateway`) | OPC UA Binario TCP |
| 🖥️ **SCADA & DMZ** | Servidor SCADA REST, HMI Web, Viz 2D, Proxy DPI y SIEM | `10.0.2.20` (`h_scada`) | HTTP REST `:8080`, HMI `:8085`, Viz `:8090`, SIEM `:8514` |

---

## 📐 Arquitectura de Red (IEC 62443)

```
[Corporate Zone 10.0.1.0/24]
        │
     (fw-eth0)
┌──────────────┐
│ Firewall fw  │ ── (fw-eth1) ── [DMZ Zone 10.0.2.0/24]
└──────────────┘                 ├── h_dmz (10.0.2.10) Jump host
        │                        └── h_scada (10.0.2.20)
        │                             ├── SCADA Server (:8080)
        │                             ├── HMI Dashboard (:8085)
        │                             ├── Visualizador 2D SVG (:8090)
        │                             ├── Modbus DPI Proxy (:15020)
        │                             ├── SIEM Pipeline (:8514)
        │                             └── Flag & Scoring Service (:8570)
     (fw-eth2)
        │
[OT Cell Zone 10.0.3.0/24]
        ├── h_plc (10.0.3.10)       Water SWaT PLC
        ├── h_plc_gas (10.0.3.12)   Gas Distribution PLC
        ├── h_plc_elec (10.0.3.13)  Electric DNP3/Modbus PLC
        ├── h_plc_trans (10.0.3.14) Transport Traffic PLC
        ├── h_plc_hosp (10.0.3.15)  Hospital ATS PLC
        ├── h_desal (10.0.3.16)     Desalination RO PLC
        ├── h_lighting (10.0.3.17)  Smart Lighting PLC
        ├── h_ied (10.0.3.20)       IEC 61850 GOOSE/SV IED
        └── h_gateway (10.0.3.30)   OPC UA Substation Gateway
```

---

## 📚 Documentación

- 📋 **[Especificación de Requisitos ERS (IEEE-830)](docs/ERS.md)**: Requisitos funcionales y no funcionales del sistema.
- 🏗️ **[Guía de Arquitectura Ciberfísica](docs/ARCHITECTURE.md)**: Diagramas Mermaid, ecuaciones de swing, topología HELICS, límites de fidelidad y mapas Modbus.
- 🛠️ **[Guía de Operaciones y Playbook](docs/OPERATIONS.md)**: Manual de despliegue, scripts de automatización, puertos y comandos de ataque.
- 🎨 **[Infraestructura de Visualización 2D y Telemetría](docs/federates/09_viz_bridge_and_2d_dashboard.md)**: Manual del puente HELICS/SCADA y dashboard SVG reactivo.
- 🛡️ **[Currículo de 29 Escenarios CTF](docs/scenarios/SCENARIO_CURRICULUM_ROADMAP.md)**: Catálogo completo de desafíos Red Team / Blue Team.
- 🔍 **[Planes y Auditorías de Calidad](docs/Audits/)**: Remediación QA 2026-09-01, Plan Visualizador 2D Fase 9 y Roadmap de Alta Fidelidad.
- 🧠 **[Grafo de Conocimiento (`graphify-out/`)](graphify-out/GRAPH_REPORT.md)**: Mapa navegable del código y la documentación, generado con `graphify` (god nodes, comunidades, relaciones cruzadas).

---

## 🧪 Pruebas

Los tests **no** tocan Mininet — usan mocks, no requieren `sudo` ni una topología real levantada.

```bash
./citylab.sh test                  # forma recomendada
```

Equivalente directo (`PYTHONPATH=.` es **obligatorio**: no hay `pyproject.toml`/`setup.py`, y todos los imports son rutas absolutas de paquete):
```bash
PYTHONPATH=. python3 -m pytest network/tests plc/tests physical helics_sim attacker/tests -q
```

**5 suites, 272 tests pasando de forma determinista:**

| Suite | Cubre |
|---|---|
| `network/tests` | SCADA, HMI, RBAC, SIEM, SDN, Historian, HA, Viz Server |
| `plc/tests` | Emuladores Modbus, DNP3, IEC 61850, OPC UA, honeypot |
| `physical` | Modelos físicos por sector (agua, gas, eléctrico, transporte, hospital) |
| `helics_sim` | Federados de co-simulación y el puente de telemetría al visualizador |
| `attacker/tests` | Los 29 scripts de ataque Red Team |

Ejecutar un único test:
```bash
PYTHONPATH=. python3 -m pytest attacker/tests/test_scenario_21_loss_of_view.py::TestScenario21LossOfView::test_hmi_detects_loss_of_view_alarm
```

Para validar el laboratorio completo bajo Mininet (requiere root; es un no-op con exit 0 si no hay privilegios):
```bash
sudo ./scripts/validate_e2e.sh
```

---

## 👤 Autor(es)

- **gabriel** — [@gabrielpinones](https://github.com/gabrielpinones)
