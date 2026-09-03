# CityLab — Cyber Range Ciberfísico Multisectorial (Fase 9 Ciudad Completa)

**CityLab** es un entorno de entrenamiento ciberfísico (*Cyber Range*) 100% basado en software, diseñado para simular ataques ofensivos (Red Team / Hacking Ético) y monitoreo defensivo (Blue Team) sobre infraestructuras críticas urbanas e interdependencias ciberfísicas en cascada.

- **0% Sobrecarga de Máquinas Virtuales**: Ejecución nativa en Linux mediante Mininet y procesos distribuidos.
- **Eficiencia de Recursos**: Consumo de memoria RAM total $<1.5\text{ GB}$ para la ciudad completa.
- **Co-Simulación Multisectorial**: Coordinación temporal a tiempo real vía **HELICS 3.x** (hasta 11 federados).
- **Estándar Industrial**: Segmentación de red alineada con **IEC 62443** (Zonas Corporate, DMZ, Celda OT, PAW EWS y Decoy Honeypot).
- **Visualizador 2D Airgapped**: Dashboard interactivo vectorial SVG/CSS en tiempo real (puerto `:8090`), 100% offline sin dependencias externas.
- **Fiabilidad y Calidad de Código**: **258 tests unitarios e integración PASS** y 0 procesos huérfanos garantizados tras teardown.

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

## 📚 Documentación Técnica Completa

- 📋 **[Especificación de Requisitos ERS (IEEE-830)](docs/ERS.md)**: Requisitos funcionales y no funcionales del sistema.
- 🏗️ **[Guía de Arquitectura Ciberfísica](docs/ARCHITECTURE.md)**: Diagramas Mermaid, ecuaciones de swing, topología HELICS, límites de fidelidad y mapas Modbus.
- 🛠️ **[Guía de Operaciones y Playbook](docs/OPERATIONS.md)**: Manual de despliegue, scripts de automatización, puertos y comandos de ataque.
- 🎨 **[Infraestructura de Visualización 2D y Telemetría](docs/federates/09_viz_bridge_and_2d_dashboard.md)**: Manual del puente HELICS/SCADA y dashboard SVG reactivo.
- 🛡️ **[Currículo de 29 Escenarios CTF](docs/scenarios/SCENARIO_CURRICULUM_ROADMAP.md)**: Catálogo completo de desafíos Red Team / Blue Team.
- 🔍 **[Planes y Auditorías de Calidad](docs/Audits/)**: Remediación QA 2026-09-01, Plan Visualizador 2D Fase 9 y Roadmap de Alta Fidelidad.

---

## ⚡ Inicio Rápido

`./citylab.sh` es el **punto de entrada único** del laboratorio. Los scripts `run_phase*.sh` quedan como implementación interna a la que delega `up`.

```bash
./citylab.sh help                  # todos los subcomandos
```

### 1. Iniciar la Co-Simulación Completa (Fase 3)
```bash
sudo ./citylab.sh up
```

### 2. Abrir el Visualizador 2D SVG Airgapped
Una vez iniciado el laboratorio, accede desde cualquier navegador web en la red DMZ o host local:
```
http://10.0.2.20:8090        # Desde dentro de la topología Mininet
http://127.0.0.1:8090        # En ejecuciones locales o de desarrollo
```

### 3. Co-Simulación HELICS sin root (Fase 7 — 10 federados, incluye SIS SIL-3)
```bash
./citylab.sh smoke
```

### 4. Ejecutar la Batería Completa de Pruebas (258 Tests)
```bash
./citylab.sh test
# o directamente:
PYTHONPATH=. pytest network/tests plc/tests physical helics_sim attacker/tests -q
```

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
