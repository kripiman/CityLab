# CityLab — Cyber Range Ciberfísico Multisectorial (Fase 3 Ciudad Completa)

**CityLab** es un entorno de entrenamiento ciberfísico (*Cyber Range*) 100% basado en software, diseñado para simular ataques ofensivos (Red Team / Hacking Ético) y monitoreo defensivo (Blue Team) sobre infraestructuras críticas urbanas e interdependencias ciberfísicas en cascada.

- **0% Sobrecarga de Máquinas Virtuales**: Ejecución nativa en Linux mediante Mininet y procesos distribuidos.
- **Eficiencia de Recursos**: Consumo de memoria RAM total $<1.5\text{ GB}$ para la ciudad completa.
- **Co-Simulación Multisectorial**: Coordinación temporal a tiempo real vía **HELICS 3.x** (7 federados).
- **Estándar Industrial**: Segmentación de red alineada con **IEC 62443** (Zonas Corporate, DMZ y Celda OT).

---

## 🏛️ Estructura de Infraestructura y Sectores Emulados

| Sector | Componente Físico | Dirección IP OT | Control PLC / Protocolo |
|---|---|---|---|
| 💧 **Agua** | Planta SWaT 2-Etapas (Tanque T1 Sedimentación + T2 Distribución) | `10.0.3.10:502` (`h_plc`) | Modbus/TCP (Coil 0: Bombas P1/P2) |
| 🔥 **Gas** | Red de Gasoducto y Válvula de Presión ($100\text{ PSI}$) | `10.0.3.12:502` (`h_plc_gas`) | Modbus/TCP (Coil 0: Válvula Control) |
| ⚡ **Energía** | Ecuación de Swing Síncrona + Subestación GridLAB-D $13.8\text{ kV}$ | `10.0.3.13:502` (`h_plc_elec`) | Modbus/TCP (Coil 1: Disyuntor Gen) |
| 🚥 **Transporte** | Intersección Semafórica 4-Fases + Modo Emergencia | `10.0.3.14:502` (`h_plc_trans`) | Modbus/TCP (Coil 1: Corredor Emergencia)|
| 🏥 **Salud** | Hospital Crítico ($150\text{ kW}$) + Failover UPS ($75\text{ kWh}$) / Generador | Suscriptor HELICS | Transición Automática por Subtensión |
| 🖥️ **SCADA** | Servidor Historian REST / Dashboard Central | `10.0.2.20:8080` (`h_scada`) | Polling Modbus en DMZ / JSON API |

---

## 📐 Arquitectura de Red (IEC 62443)

```
[Corporate Zone 10.0.1.0/24]
        │
     (fw-eth0)
┌──────────────┐
│ Firewall fw  │ ── (fw-eth1) ── [DMZ Zone 10.0.2.0/24]
└──────────────┘                 ├── h_dmz (10.0.2.10) Jump host
        │                        └── h_scada (10.0.2.20:8080) SCADA Server
     (fw-eth2)
        │
[OT Cell Zone 10.0.3.0/24]
        ├── h_plc (10.0.3.10)       Water PLC
        ├── h_plc_gas (10.0.3.12)   Gas PLC
        ├── h_plc_elec (10.0.3.13)  Electric PLC
        └── h_plc_trans (10.0.3.14) Transport PLC
```

---

## 📚 Documentación Técnica Completa

- 📋 **[Especificación de Requisitos ERS (IEEE-830)](docs/ERS.md)**: Requisitos funcionales y no funcionales del sistema.
- 🏗️ **[Guía de Arquitectura Ciberfísica](docs/ARCHITECTURE.md)**: Diagramas Mermaid, ecuaciones de swing, topología HELICS y mapas Modbus.
- 🛠️ **[Guía de Operaciones y Playbook](docs/OPERATIONS.md)**: Manual de despliegue, scripts de automatización y comandos de ataque.
- 🚩 **[Escenario CTF 01: Apagón Urbano en Cascada](docs/scenarios/scenario_01_cascading_blackout.md)**: Desafío estilo TryHackMe / HackTheBox.

---

## ⚡ Inicio Rápido

### 1. Iniciar la Co-Simulación Completa (Fase 3)
```bash
sudo ./run_phase3.sh
```

### 2. Ejecutar Pruebas Automatizadas Locales (Smoke Test 7 Federados)
```bash
./helics_sim/smoke_test_phase3.sh
```

### 3. Inspeccionar el Log CSV de Eventos en Tiempo Real
```bash
tail -f logs/cascading_events.csv
```
