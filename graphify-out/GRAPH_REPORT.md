# Graph Report - CityLab  (2026-08-18)

## Corpus Check
- 197 files · ~72,437 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1686 nodes · 2443 edges · 133 communities (124 shown, 9 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 139 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f5b6489a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- fed_icssim.py
- Dnp3OutstationState
- Dnp3MasterClient
- scada_server.py
- Iec61850Server
- exploit_modbus.py
- main
- traffic.py
- fed_hospital.py
- BacnetListener
- SmartLightingSystem
- create_federate
- run_phase1.sh
- run_phase2.sh
- run_phase3.sh
- attack_modbus.py
- poc_modbus_test.py
- smoke_test_phase2.sh
- smoke_test_phase3.sh
- attack_multisector.py
- smoke_test_local.sh
- start_broker.sh
- install_deps.sh
- attack_grid_heatwave_attribution.py
- start_openplc.sh
- CityLab - Development Guidelines
- ThreadedHmiServer
- TestRBACResolver
- CityLab - Technology Stack
- SCADAPrimarySecondaryCluster
- ElectricalSubstationGrid
- OpcUaServer
- TestOpcUaServerClient
- CityVisualizerStateEngine
- SafetyInstrumentedLogic
- EpanetHydraulicSolver
- 🔧 PLAN DE REMEDIACIÓN — Cierre de Deficiencias Verificadas (CityLab)
- TestHistorianTSDB
- HistorianTSDB
- TestScadaRBACHTTPEndpoints
- RBACResolver
- ._conn
- profile_resources.py
- 🎯 3. Fases del Roadmap de Fidelidad (Fases 0 a 9)
- socket
- OpcUaClient
- IndustrialHmiEngine
- TestScadaHistorianHTTPEndpoints
- TestOpcUaNodeSpace
- Core Components
- 🎓 CityLab Cyber Range — Roadmap Curricular de Escenarios CTF (IEC 62443 / GICSP Aligned)
- 3. Requisitos Funcionales Específicos
- ⚡ Federado 02 — Sector Eléctrico y Subestación (GridLab-D & IEC 61850 / DNP3 SA)
- ✅ REPORTE DE CIERRE DE AUDITORÍA — CityLab Cyber Range
- SiemCorrelationEngine
- OtHoneypotServer
- attack_apt_sandworm_campaign.py
- Escenario CTF 02: Inyección de Mensajes GOOSE IEC 61850 (Estilo Industroyer2 / Ucrania 2022)
- Especificación de Requisitos de Software (ERS)
- 📘 Federado 01 — Sector Agua SWaT (Tratamiento y Distribución Multi-Etapa)
- 🏥 Federado 04 — Sector Hospital Carga Crítica y Sistema ATS/UPS (`fed_hospital.py`)
- citylab.sh
- ScadaTour
- HoneypotTouch
- InsiderRbacAttack
- NtpTimeSpoofingAttack
- .solve_network
- PurpleTeamMttd
- SiemRuleEvasion
- CLAUDE.md
- 🚦 Federado 03 — Sector Transporte y Tráfico Urbano (`fed_transport.py`)
- 3. Cadena de Ataque (Walkthrough Paso a Paso)
- Escenario CTF 03: Evasión Sigilosa de SIS Triton/Trisis (Low-and-Slow Attack)
- Escenario CTF 04: Replay de Telemetría Man-in-the-Middle (Estilo Stuxnet)
- EcsEvent
- ._svc_write
- CityLab - Product Overview
- BlindRandomizedEnv
- RansomwareTabletop
- RedVsBlueMatch
- Escenario CTF 05: Explotación de Ventana de Conmutación SCADA/DCS HA
- Escenario CTF 06: Kerberoasting y Escalado de Privilegios en Active Directory
- ⚡ Inicio Rápido
- 🛡️ Federado 05 — Sistema de Seguridad SIS / ESD (SIL-3) (`fed_sis.py`)
- 📊 Federado 06 — Observer y Logger de Co-Simulación HELICS (`fed_logger.py`)
- 🖥️ Infraestructura 07 — Servidor SCADA Central, HA Cluster y Dashboard HMI
- 🛡️ Infraestructura 08 — SIEM, SDN Controller y Active Directory Domain Controller
- Escenario CTF 07: Anti-Forense y Borrado de Registros en Historian TSDB
- Escenario CTF 08: Insider Threat y Violación de Principio de Mínimo Privilegio RBAC
- Escenario CTF 09: Dosificación Química en Planta de Tratamiento de Agua (SWaT / Oldsmar Pattern)
- Escenario CTF 10: Falla Natural por Ola de Calor + Ataque Ciberfísico Simultáneo (Incident Attribution)
- Escenario CTF 11: Ataque de Desincronización de Tiempo NTP / PTP (Time Synchronization Hardening)
- Escenario CTF 12: Ransomware IT con Parada de Emergencia Operacional OT (Colonial Pipeline Pattern)
- Escenario CTF 13: Reconocimiento Pasivo en Redes OT (Onboarding Pasivo)
- Escenario CTF 14: Escaneo Activo de Subredes OT (Segmentación Nmap)
- Escenario CTF 15: Lectura de Telemetría Modbus sin Escritura
- Escenario CTF 16: Interacción con Trampas Deception (Honeypot OT)
- Escenario CTF 17: Tour Guiado por la API SCADA y Servidor HMI
- Escenario CTF 18: Escritura Forzada de Coil Modbus Único (Manipulación Guiada)
- Escenario CTF 19: Cadena de Pivoteo Guiado Attacker -> DMZ -> OT
- Escenario CTF 20: Comparación de Hardening SCADA API (STRICT_AUTH Toggle)
- Escenario CTF 21: Respuesta a Pérdida de Visibilidad (Loss of View & Manual Isolation)
- Escenario CTF 22: Ejercicio Purple Team y Medición de Métricas SOC (MTTD / MTTR)
- Escenario CTF 23: Defensa SDN Dinámica en Caliente (Safety vs Availability Trade-off)
- Escenario CTF 24: Evasión de Reglas de Correlación SIEM (Multi-IP Distributed Attack)
- Escenario CTF 25: Ejercicio Tabletop de Crisis por Ransomware Industrial
- Escenario CTF 26: Capstone Campaña APT Persistente (Sandworm / ELECTRUM Pattern)
- Escenario CTF 27: Ciberejercicio Simultáneo Red vs Blue con Motor de Arbitraje
- Escenario CTF 28: Entorno Ciego Dinámico Anti-Memorización
- Escenario CTF 29: Recuperación Post-Incidente y Reintegración Operacional (Disaster Recovery)
- TestSiemPipeline
- CityLab — Guía de Operaciones (Fase 3 Ciudad Completa)
- main
- 🛡️ Arquitectura del Cyber Range CityLab (Fase 3 Ciudad Completa)
- TankPlant
- PROMPT_AUDITOR.md
- PROMPT_IMPLEMENTADOR.md
- validate_e2e.sh
- TwoStageWaterPlant
- SCADAAPIHandler
- RansomwareOtImpactAttack
- smoke_test_phase7.sh
- smoke_test_phase4.sh

## God Nodes (most connected - your core abstractions)
1. `HistorianTSDB` - 41 edges
2. `SiemCorrelationEngine` - 37 edges
3. `TwoStageWaterPlant` - 26 edges
4. `OpcUaServer` - 25 edges
5. `SCADAPrimarySecondaryCluster` - 20 edges
6. `OpcUaClient` - 20 edges
7. `IndustrialHmiEngine` - 19 edges
8. `RBACResolver` - 19 edges
9. `TestRBACResolver` - 19 edges
10. `Iec61850Server` - 19 edges

## Surprising Connections (you probably didn't know these)
- `AptSandwormCampaign` --uses--> `Iec61850Server`  [INFERRED]
  attacker/attack_apt_sandworm_campaign.py → plc/iec61850_emulator.py
- `GridHeatwaveAttributionAttack` --uses--> `TwoStageWaterPlant`  [INFERRED]
  attacker/attack_grid_heatwave_attribution.py → physical/water/plant_water.py
- `HistorianAntiForensicsAttack` --uses--> `HistorianTSDB`  [INFERRED]
  attacker/attack_historian_anti_forensics.py → network/historian.py
- `HoneypotTouch` --uses--> `SiemCorrelationEngine`  [INFERRED]
  attacker/attack_honeypot_touch.py → network/siem_pipeline.py
- `InsiderRbacAttack` --uses--> `RBACResolver`  [INFERRED]
  attacker/attack_insider_rbac.py → network/rbac.py

## Import Cycles
- None detected.

## Communities (133 total, 9 thin omitted)

### Community 0 - "fed_icssim.py"
Cohesion: 0.14
Nodes (14): create_federate(), main(), Any, helics_federate, ModbusTcpClient, read_actuator_running(), ElecPlant, GasPlant (+6 more)

### Community 1 - "Dnp3OutstationState"
Cohesion: 0.08
Nodes (22): LiveSdnDefense, main(), Any, patch, TestScenario23Sdn, apply_circuit_breaker(), apply_sdn_flow_rules(), main() (+14 more)

### Community 2 - "Dnp3MasterClient"
Cohesion: 0.08
Nodes (23): DomainControllerEmulator, KerberosServerThread, LdapServerThread, main(), socket, Escuchador SMB v2/v3 en puerto 445., Orquestador completo del controlador de dominio h_dc., Escuchador LDAP en puerto 389. (+15 more)

### Community 3 - "scada_server.py"
Cohesion: 0.09
Nodes (19): patch, Ejercita la lógica de producción poll_plcs_once() y verifica la transición real…, main(), ModbusDpiEngine, ModbusDpiProxyServer, socket, RateLimiter, Proxy TCP transparente/inverso que filtra tráfico Modbus hacia los PLCs. (+11 more)

### Community 4 - "Iec61850Server"
Cohesion: 0.08
Nodes (20): main(), Construye y transmite un paquete GOOSE malicioso de disparo de interruptor., spoof_goose_trip(), TestGooseSpoofingAttack, IEC61850DataSet, Iec61850GooseEncoder, Iec61850Server, Iec61850SvEncoder (+12 more)

### Community 5 - "exploit_modbus.py"
Cohesion: 0.22
Nodes (18): action_fault(), action_sabotage(), action_start(), action_status(), action_stop(), main(), print_status(), ModbusTcpClient (+10 more)

### Community 6 - "main"
Cohesion: 0.16
Nodes (15): CLI, Mininet, apply_fw_configuration(), configure_host_routes(), CustomCLI, Iec62443Topo, main(), Configure FW host interfaces, IP forwarding and iptables rules. Assumes… (+7 more)

### Community 7 - "traffic.py"
Cohesion: 0.16
Nodes (12): create_federate(), main(), helics_federate, helics_input, helics_publication, physical/transport package, LightPhase, Enum (+4 more)

### Community 8 - "fed_hospital.py"
Cohesion: 0.25
Nodes (9): create_federate(), HospitalPlant, main(), PowerState, Enum, helics_federate, helics_input, helics_publication (+1 more)

### Community 9 - "BacnetListener"
Cohesion: 0.07
Nodes (20): BacnetAttacker, main(), Any, Emulador de ataque BACnet/IP sobre UDP 47808., main(), NtcipAttacker, Any, Emulador de ataque NTCIP 1202 sobre TCP 161. (+12 more)

### Community 10 - "SmartLightingSystem"
Cohesion: 0.08
Nodes (15): main(), main(), Any, Lee el coil de apagón del PLC de alumbrado. False si no hay PLC o falla la…, read_blackout_command(), TestPhase4Federates, Any, Modelo físico determinista de Red de Alumbrado Público Inteligente. (+7 more)

### Community 11 - "create_federate"
Cohesion: 0.36
Nodes (7): create_federate(), main(), helics_federate, helics_input, helics_publication, start_gridlabd(), stop_gridlabd()

### Community 12 - "run_phase1.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase1.sh script

### Community 13 - "run_phase2.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase2.sh script

### Community 14 - "run_phase3.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase3.sh script

### Community 15 - "attack_modbus.py"
Cohesion: 0.71
Nodes (6): connect(), do_fault(), do_start_stop_blast(), main(), ModbusTcpClient, write_coil()

### Community 16 - "poc_modbus_test.py"
Cohesion: 0.62
Nodes (6): main(), ModbusTcpClient, Automated integration test for the PoC PLC Modbus interface. Usage (from within…, read_coils(), wait_for_coil(), write_coil()

### Community 17 - "smoke_test_phase2.sh"
Cohesion: 0.33
Nodes (5): HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase2.sh script

### Community 18 - "smoke_test_phase3.sh"
Cohesion: 0.33
Nodes (5): HELICS_BROKER_PORT, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase3.sh script

### Community 19 - "attack_multisector.py"
Cohesion: 0.13
Nodes (13): main(), ModbusReadOnly, Any, execute_cascading_attack(), force_coil(), main(), read_plc_state(), main() (+5 more)

### Community 23 - "attack_grid_heatwave_attribution.py"
Cohesion: 0.33
Nodes (5): GridHeatwaveAttributionAttack, main(), Any, TestAttributionAttack, main()

### Community 33 - "CityLab - Development Guidelines"
Cohesion: 0.04
Nodes (47): 1. Language and Terminology, 1. New Component Development, 1. Project Organization Patterns, 1. Python Code Formatting (5/5 files follow these patterns), 1. Recurring Implementation Patterns, 1. Security Practices (5/5 files exhibit), 2. Comment Style, 2. Common Architectural Approaches (+39 more)

### Community 34 - "ThreadedHmiServer"
Cohesion: 0.17
Nodes (5): HTTPServer, ThreadingMixIn, ThreadedHmiServer, TestHmiHistorianIntegration, TestHmiServer

### Community 35 - "TestRBACResolver"
Cohesion: 0.07
Nodes (15): Bearer auditor:<operator_token> → 403 (rol incorrecto para token)., Rol auditor puede leer telemetría pero no /api/control/write., Rol operator puede acceder a /api/control/read pero no /api/control/write., Rol engineer tiene acceso completo (wildcard)., Rol None (no autenticado) → siempre False., reload() recarga almacén de tokens con cambios de env var., Tests unitarios del RBACResolver (network/rbac.py)., Bearer <token> plano → rol operator en STRICT_AUTH=0 (modo CTF). (+7 more)

### Community 36 - "CityLab - Technology Stack"
Cohesion: 0.07
Nodes (27): 1. Environment Setup, 2. Development Testing, 3. Integration Testing, 4. Attack Development, Attack Execution, Build Systems and Development Tools, CityLab - Technology Stack, Core Dependencies (+19 more)

### Community 37 - "SCADAPrimarySecondaryCluster"
Cohesion: 0.12
Nodes (9): FailoverExploitAttack, main(), Any, TestFailoverAttack, Any, Administrador de cluster de Alta Disponibilidad SCADA., Procesa un heartbeat recibido del peer., SCADAPrimarySecondaryCluster (+1 more)

### Community 38 - "ElectricalSubstationGrid"
Cohesion: 0.11
Nodes (13): ElectricalSubstationGrid, GridParams, Modelo físico de subestación de transmisión / distribución eléctrica., Avanza la simulación dinámica de la red eléctrica dt_s segundos., GasPipelineParams, GasPipelinePlant, Modelo físico dinámico de gasoducto con estación compresora., Avanza la simulación física de gas dt_s segundos. (+5 more)

### Community 39 - "OpcUaServer"
Cohesion: 0.17
Nodes (7): OpcUaNodeSpace, OpcUaServer, Lista todos los nodos disponibles., Servidor TCP que emula el protocolo UA/TCP de OPC UA. Suficiente para…, Envía un mensaje UA/TCP., Espacio de nodos OPC UA en memoria. Thread-safe., TestProtocolFidelityPhase3

### Community 40 - "TestOpcUaServerClient"
Cohesion: 0.11
Nodes (13): El servidor responde ACK al HEL correctamente (UA/TCP handshake)., Lectura de nodo Float (WaterTank_Level, NodeId=1001) retorna valor numérico., Lectura de nodo Boolean (WaterPump_State, NodeId=1002)., Lectura de nodo Int32 (Traffic_Light_State, NodeId=4001)., Lectura de NodeId desconocido retorna None (BadNodeIdUnknown)., Escritura directa al NodeSpace y lectura confirmada vía cliente., Browse retorna lista con conteo correcto de nodos., GetEndpoints responde con 200 de servicio (SecurityMode=None). (+5 more)

### Community 41 - "CityVisualizerStateEngine"
Cohesion: 0.13
Nodes (10): TestVizServer, TestCityVisualizer, CityVisualizerStateEngine, Any, BaseHTTPRequestHandler, HTTPServer, ThreadingMixIn, Motor de estado de visualización presentacional 2D/3D. (+2 more)

### Community 42 - "SafetyInstrumentedLogic"
Cohesion: 0.09
Nodes (15): main(), Any, TritonLowSlowAttack, TestTritonAttack, create_federate(), main(), Any, helics_sim/fed_sis.py — Safety Instrumented System (SIS / ESD Independiente)… (+7 more)

### Community 43 - "EpanetHydraulicSolver"
Cohesion: 0.26
Nodes (6): TestPhysicsEngine, EpanetHydraulicSolver, PipeConfig, PumpConfig, Solver hidráulico de red de distribución de agua (Modelo didáctico Hazen-…, physical/water/plant_water.py — Modelo físico de tratamiento de agua en 2…

### Community 44 - "🔧 PLAN DE REMEDIACIÓN — Cierre de Deficiencias Verificadas (CityLab)"
Cohesion: 0.10
Nodes (20): Distinción crítica: LoV muerto ≠ F-06, 🟥 FASE R0 — El laboratorio arranca de verdad (P0, bloqueante), 🟧 FASE R1 — La cadena de detección funciona (P1), 🟨 FASE R2 — Fidelidad física honesta (P1), 🟦 FASE R3 — Superficie de exposición e higiene (P2), 🚫 Fuera de alcance de este plan (no tocar), ✅ Orden de ejecución recomendado, 🔧 PLAN DE REMEDIACIÓN — Cierre de Deficiencias Verificadas (CityLab) (+12 more)

### Community 45 - "TestHistorianTSDB"
Cohesion: 0.10
Nodes (11): prune() elimina puntos más antiguos manteniendo los más recientes., query() con parámetro `since` filtra por timestamp correctamente., Tests unitarios del módulo historian.py (HistorianTSDB)., write() persiste puntos individuales y query() los recupera correctamente., write_snapshot() persiste el estado completo y query_snapshots() lo recupera., last() devuelve el snapshot más reciente de un sector., last() devuelve None cuando el sector no tiene datos., sectors() lista exactamente los sectores con datos registrados. (+3 more)

### Community 46 - "HistorianTSDB"
Cohesion: 0.18
Nodes (8): main(), Any, StuxnetReplayAttack, TestStuxnetAttack, HistorianTSDB, Cierra la conexión del hilo actual., Time-Series historian embebido sobre SQLite WAL. Interfaz pública idéntica a la…, Crea las tablas si no existen. Idempotente.

### Community 47 - "TestScadaRBACHTTPEndpoints"
Cohesion: 0.14
Nodes (9): Tests de integración HTTP para RBAC en scada_server., /health responde 200 sin Authorization., /api/telemetry con token válido → 200., /api/telemetry sin token → 401., /api/whoami retorna el rol del token presentado., /api/whoami con token legado → rol operator (modo CTF)., STRICT_AUTH=1 rechaza token plano legado con 403., Auditor recibe 403 en /api/control/write. (+1 more)

### Community 48 - "RBACResolver"
Cohesion: 0.14
Nodes (10): TestScenario20StrictAuth, _load_token_store(), Resuelve el rol de una petición HTTP a partir de su cabecera Authorization.…, Recarga el almacén de tokens (útil tras rotación de credenciales)., Resuelve el rol asociado a una cabecera Authorization. Args: auth_header: Valor…, Verifica si el rol tiene permiso para acceder al endpoint. Args: role: Rol…, Carga el mapa de tokens a roles desde variables de entorno. Variables de…, Intenta autenticar contra el AD LDAP emulado de h_dc (`ad_dc_emulator.py`).… (+2 more)

### Community 49 - "._conn"
Cohesion: 0.14
Nodes (10): Connection, Any, Escribe un punto de telemetría. Args: sector: Nombre del sector OT ('water',…, Escribe el snapshot JSON completo de un sector. Permite consultas de telemetría…, Consulta puntos de telemetría históricos. Args: sector: Sector OT a consultar.…, Consulta snapshots completos del sector. Returns: Lista de dicts con keys: ts,…, Retorna el snapshot más reciente de un sector, o None si no hay datos., Lista los sectores con datos en el historian. (+2 more)

### Community 50 - "profile_resources.py"
Cohesion: 0.15
Nodes (20): resource.getrusage debe devolver un RSS positivo real, no una estimación fija., El muestreo real no debe clasificar procesos ajenos al laboratorio., TestProfileResources, classify(), collect_sample(), _iter_processes_proc(), _iter_processes_psutil(), main() (+12 more)

### Community 51 - "🎯 3. Fases del Roadmap de Fidelidad (Fases 0 a 9)"
Cohesion: 0.12
Nodes (16): 📌 1. Estado de Arquitectura y Baseline Real (Fase 0), 🔒 2. Matriz de Deuda Técnica y Hallazgos IEC 62443, 🎯 3. Fases del Roadmap de Fidelidad (Fases 0 a 9), 🗺️ CityLab Cyber Range — Roadmap de Fidelidad e Implementación, Componentes en Vivo (7 Federados HELICS):, Estado de Módulos Específicos:, 🔵 Fase 0 — Fundaciones sin Root & Reestructuración (COMPLETADA), 🔵 Fase 1 — Endpoints Livianos OT Categoría B (NTCIP / BACnet) (COMPLETADA) (+8 more)

### Community 52 - "socket"
Cohesion: 0.16
Nodes (9): socket, Maneja una conexión de cliente OPC UA., Lee exactamente n bytes del socket., Responde a HEL con ACK — primer paso del handshake UA/TCP., Maneja OpenSecureChannel con SecurityMode=None., Despacha servicios OPC UA: Read, Browse, GetEndpoints., Retorna la lista de endpoints disponibles., Lee el valor de un nodo del espacio OPC UA. (+1 more)

### Community 53 - "OpcUaClient"
Cohesion: 0.18
Nodes (8): OpcUaClient, Cliente OPC UA TCP mínimo para pruebas de integración. Replica exactamente el…, Establece conexión y realiza handshake HEL/ACK + OpenSecureChannel., Lee el valor de un nodo OPC UA., Lista nodos disponibles en el servidor., Escribe un valor numérico a un nodo OPC UA sobre la red., Consulta los endpoints disponibles (GetEndpoints)., Recibe un mensaje UA/TCP. Retorna (tipo, body) o None.

### Community 54 - "IndustrialHmiEngine"
Cohesion: 0.15
Nodes (10): Verifica que el motor HMI registre alarma de LOSS_OF_VIEW y cambie a…, TestScenario21LossOfView, HmiRequestHandler, IndustrialHmiEngine, Any, BaseHTTPRequestHandler, Envía una acción de control al SCADA Server., Motor de estado HMI para consolidación P&ID, tendencias históricas y gestión de… (+2 more)

### Community 55 - "TestScadaHistorianHTTPEndpoints"
Cohesion: 0.16
Nodes (8): Tests de integración HTTP para los endpoints /api/history del SCADA Server., Arrancar un servidor HTTP de test con el handler real del SCADA., Helper: realiza GET con Bearer token y retorna (status_code, json_body)., GET /api/history?sector=water retorna filas históricas del sector., GET /api/history?sector=water&field=pressure filtra por campo., GET /api/history sin sector retorna 400., GET /api/history/snapshot?sector=water retorna snapshots del sector., TestScadaHistorianHTTPEndpoints

### Community 56 - "TestOpcUaNodeSpace"
Cohesion: 0.13
Nodes (8): Tests unitarios del espacio de nodos OpcUaNodeSpace., read() retorna datos correctos para un nodo existente., read() retorna None para un NodeId desconocido., write() actualiza el valor y read() lo refleja., write() retorna False para NodeId desconocido., browse() lista todos los nodos del espacio., all_values() agrupa datos por sector correctamente., TestOpcUaNodeSpace

### Community 57 - "Core Components"
Cohesion: 0.14
Nodes (13): 1. Network Layer, 2. Control Systems, 3. Physical Simulation, 4. Co-Simulation Framework, 5. Attack Framework, Architectural Patterns, CityLab - Project Structure, Co-Simulation Architecture (+5 more)

### Community 58 - "🎓 CityLab Cyber Range — Roadmap Curricular de Escenarios CTF (IEC 62443 / GICSP Aligned)"
Cohesion: 0.14
Nodes (13): 1. 📊 Diagnóstico y Distribución Curricular, 2. 🗺️ Propuesta de Extensión por Lotes, 3. 📝 Desglose de Escenarios por Lote, 4. 📈 Matriz Resumen de Distribución Final, 5. 🎯 Recomendación de Ejecución, 🎓 CityLab Cyber Range — Roadmap Curricular de Escenarios CTF (IEC 62443 / GICSP Aligned), Estado Anterior (Escenarios 01 a 12), 🟢 LOTE 1: Base de la Curva (Fácil & Fácil-Media) (+5 more)

### Community 59 - "3. Requisitos Funcionales Específicos"
Cohesion: 0.11
Nodes (19): 3.10 Módulo IT/OT Corporate Active Directory Domain Controller (RF-10), 3.11 Decisiones de Diseño Pedagógico CTF (RF-11), 3.12 Matriz de Conduit de Red e Inventario de Puertos IEC 62443 (RF-12), 3.13 Módulo de Sistema Instrumentado de Seguridad SIS / ESD SIL-3 (RF-13), 3.14 Módulo de Redundancia SCADA y Failover HA (RF-14), 3.15 Módulo HMI Industrial y Visualización Web 2D/3D (RF-15), 3.16 Módulo SOC / SIEM y Exportación Empresarial (RF-16), 3.17 Módulo de Alumbrado Público Inteligente (RF-17) (+11 more)

### Community 60 - "⚡ Federado 02 — Sector Eléctrico y Subestación (GridLab-D & IEC 61850 / DNP3 SA)"
Cohesion: 0.17
Nodes (11): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Código y Flujo de Trabajo, 🧮 3. Modelo Físico e Inercia de Red, 🗺️ 4. Mapa de Protocolos (DNP3 SA `10.0.3.13` & IEC 61850 GOOSE `10.0.3.20`), 📡 5. Interfaz HELICS Pub-Sub, 💾 6. Presupuesto de Recursos y Memoria RAM, DNP3 Outstation (Puerto `:20000`), Ecuación de Swing Síncrona (+3 more)

### Community 61 - "✅ REPORTE DE CIERRE DE AUDITORÍA — CityLab Cyber Range"
Cohesion: 0.17
Nodes (11): 🎯 DECISIONES DE DISEÑO PEDAGÓGICO CTF (HALLAZGOS INTENCIONALES), 📈 EVOLUCIÓN DEL GRAFO DE CONOCIMIENTO, 📦 INVENTARIO DE COMPONENTES IMPLEMENTADOS, Programa de Remediación IEC 62443 · Cierre de 3 Semanas, 🔍 REGISTRO DE RIESGO RESIDUAL, ✅ REPORTE DE CIERRE DE AUDITORÍA — CityLab Cyber Range, 🔒 SCORECARD DE SEGURIDAD: INICIAL vs FINAL, Semana 1 — Quick Wins (+3 more)

### Community 62 - "SiemCorrelationEngine"
Cohesion: 0.17
Nodes (6): Exporta buffer de eventos en formato JSON compatible con Logstash /…, Guarda buffer de eventos ECS en un archivo JSON en disco., Exporta eventos en formato Syslog estandarizado RFC 5424., Motor de correlación SIEM para alertas de seguridad ciberfísica., SiemCorrelationEngine, TestSiemPassiveBridge

### Community 63 - "OtHoneypotServer"
Cohesion: 0.26
Nodes (3): main(), OtHoneypotServer, TestHoneypotServer

### Community 64 - "attack_apt_sandworm_campaign.py"
Cohesion: 0.08
Nodes (21): AptSandwormCampaign, main(), Any, HistorianAntiForensicsAttack, main(), Any, KerberoastAttack, main() (+13 more)

### Community 65 - "Escenario CTF 02: Inyección de Mensajes GOOSE IEC 61850 (Estilo Industroyer2 / Ucrania 2022)"
Cohesion: 0.18
Nodes (10): 1. Breve del Escenario (Storyline), 2. Mapa de Componentes e IPs, 3. Cadena de Ataque y Ejecución Paso a Paso, 4. Detección y Regla SOC / SIEM (Blue Team), 5. Flags del Desafío CTF, Escenario CTF 02: Inyección de Mensajes GOOSE IEC 61850 (Estilo Industroyer2 / Ucrania 2022), Paso 1: Pivoteo hacia la Red OT, Paso 2: Escaneo y Sniffing de Mensajes GOOSE (+2 more)

### Community 66 - "Especificación de Requisitos de Software (ERS)"
Cohesion: 0.18
Nodes (10): 1.1 Propósito, 1.2 Alcance, 1.3 Definiciones, Acrónimos y Abreviaturas, 1. Introducción, 2.1 Perspectiva del Producto, 2.2 Restricciones de Hardware y Entorno, 2. Descripción General, 4. Requisitos No Funcionales (RNF) (+2 more)

### Community 67 - "📘 Federado 01 — Sector Agua SWaT (Tratamiento y Distribución Multi-Etapa)"
Cohesion: 0.20
Nodes (9): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Código y Flujo de Trabajo, 🧮 3. Modelo Físico e Interdependencia Ciberfísica, 🗺️ 4. Mapa de Registros Modbus TCP (PLC Agua `10.0.3.10:502`), 📡 5. Interfaz de Co-Simulación HELICS, 💾 6. Presupuesto de Recursos y Memoria RAM, Balance de Niveles de Tanques, Ecuación de Pérdida de Carga (Hazen-Williams) (+1 more)

### Community 68 - "🏥 Federado 04 — Sector Hospital Carga Crítica y Sistema ATS/UPS (`fed_hospital.py`)"
Cohesion: 0.20
Nodes (9): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Código y Máquina de Estados de Energía, 🧮 3. Modelo Físico de Descarga de Baterías y Generador, 🗺️ 4. Mapa de Registros Modbus TCP (PLC Hospital `10.0.3.15:502`), 📡 5. Interfaz HELICS Pub-Sub, 💾 6. Presupuesto de Recursos y Memoria RAM, Criterio de Failover (IEEE 1159), Demanda de Carga e Integración de Energía UPS (+1 more)

### Community 69 - "citylab.sh"
Cohesion: 0.32
Nodes (13): c_err(), c_info(), cmd_down(), cmd_profile(), cmd_smoke(), cmd_status(), cmd_test(), cmd_up() (+5 more)

### Community 70 - "ScadaTour"
Cohesion: 0.43
Nodes (4): main(), Any, ScadaTour, TestScadaTour

### Community 71 - "HoneypotTouch"
Cohesion: 0.36
Nodes (4): HoneypotTouch, main(), Any, TestHoneypotTouch

### Community 72 - "InsiderRbacAttack"
Cohesion: 0.43
Nodes (4): InsiderRbacAttack, main(), Any, TestInsiderRbacAttack

### Community 73 - "NtpTimeSpoofingAttack"
Cohesion: 0.36
Nodes (4): main(), NtpTimeSpoofingAttack, Any, TestTimeSpoofingAttack

### Community 74 - ".solve_network"
Cohesion: 0.33
Nodes (3): Calcula la pérdida de fricción en la tubería usando Hazen-Williams., Calcula la presión generada por la bomba según su curva TDH., Calcula el estado hidráulico de la red. Retorna (flow_m3_s, pressure_bar,…

### Community 75 - "PurpleTeamMttd"
Cohesion: 0.36
Nodes (4): main(), PurpleTeamMttd, Any, TestScenario22PurpleTeam

### Community 76 - "SiemRuleEvasion"
Cohesion: 0.36
Nodes (4): main(), Any, SiemRuleEvasion, TestScenario24SiemEvasion

### Community 77 - "CLAUDE.md"
Cohesion: 0.22
Nodes (7): Architecture — the big picture, Attack scripts & scenarios, Commands, Defensive stack (DMZ/Blue Team), Golden rule — intentional vulnerabilities, Gotchas, What this is

### Community 78 - "🚦 Federado 03 — Sector Transporte y Tráfico Urbano (`fed_transport.py`)"
Cohesion: 0.22
Nodes (8): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Código y Flujo de Trabajo, 🧮 3. Modelo Físico de Congestión e Interdependencia, 🗺️ 4. Mapa de Registros Modbus TCP (PLC Transporte `10.0.3.14:502`), 📡 5. Interfaz HELICS Pub-Sub, 💾 6. Presupuesto de Recursos y Memoria RAM, Ecuación de Dinámica de Congestión Vehicular, 🚦 Federado 03 — Sector Transporte y Tráfico Urbano (`fed_transport.py`)

### Community 79 - "3. Cadena de Ataque (Walkthrough Paso a Paso)"
Cohesion: 0.22
Nodes (9): 1. Breve del Escenario (Storyline), 2. Mapa de Red e IPs Relevantes, 3. Cadena de Ataque (Walkthrough Paso a Paso), 4. Flags del Desafío CTF, Escenario CTF 01: Apagón Urbano en Cascada (THM / HTB Style), Paso 1: Pivoteo de Corporate a DMZ, Paso 2: Reconocimiento Modbus en la Zona OT (`10.0.3.0/24`), Paso 3: Inyección de Disparo Eléctrico (Sabotaje Cinético) (+1 more)

### Community 80 - "Escenario CTF 03: Evasión Sigilosa de SIS Triton/Trisis (Low-and-Slow Attack)"
Cohesion: 0.22
Nodes (8): 1. Breve del Escenario (Storyline), 2. Mapa de Umbrales de Seguridad (SIS vs Atacante), 3. Cadena de Ataque y Ejecución Paso a Paso, 4. Lección Pedagógica y Defensiva, 5. Flags del Desafío CTF, Escenario CTF 03: Evasión Sigilosa de SIS Triton/Trisis (Low-and-Slow Attack), Paso 1: Reconocimiento de Umbrales SIS, Paso 2: Ejecución de Manipulación Sigilosa

### Community 81 - "Escenario CTF 04: Replay de Telemetría Man-in-the-Middle (Estilo Stuxnet)"
Cohesion: 0.22
Nodes (8): 1. Breve del Escenario (Storyline), 2. Diagrama de Flujo del Ataque, 3. Cadena de Ataque y Ejecución Paso a Paso, 4. Lección Pedagógica y Defensiva, 5. Flags del Desafío CTF, Escenario CTF 04: Replay de Telemetría Man-in-the-Middle (Estilo Stuxnet), Paso 1: Grabación de Telemetría de Baseline, Paso 2: Engaño a la HMI y Sabotaje de Planta

### Community 82 - "EcsEvent"
Cohesion: 0.36
Nodes (5): EcsEvent, Any, Ingiere y normaliza un registro de log Zeek (conn.log, notice.log, modbus.log)., Ingiere y normaliza un registro de alerta Suricata Eve JSON (eve.json)., Aplica reglas de correlación SOC sobre los eventos ingresados.

### Community 83 - "._svc_write"
Cohesion: 0.22
Nodes (5): Any, Lee el valor actual de un nodo., Escribe el valor de un nodo. Retorna True si el nodo existe., Retorna snapshot completo del espacio de nodos por sector., Escribe un nuevo valor en el espacio de nodos OPC UA.

### Community 84 - "CityLab - Product Overview"
Cohesion: 0.25
Nodes (7): Capabilities, CityLab - Product Overview, Key Features, Project Purpose, Target Users, Use Cases, Value Proposition

### Community 85 - "BlindRandomizedEnv"
Cohesion: 0.43
Nodes (4): BlindRandomizedEnv, main(), Any, TestScenario28Blind

### Community 86 - "RansomwareTabletop"
Cohesion: 0.43
Nodes (4): main(), Any, RansomwareTabletop, TestScenario25Tabletop

### Community 87 - "RedVsBlueMatch"
Cohesion: 0.43
Nodes (4): main(), Any, RedVsBlueMatch, TestScenario27RedBlue

### Community 88 - "Escenario CTF 05: Explotación de Ventana de Conmutación SCADA/DCS HA"
Cohesion: 0.25
Nodes (7): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 05: Explotación de Ventana de Conmutación SCADA/DCS HA, Paso 1: Interrupción del Servidor SCADA Primario, Paso 2: Explotación de la Transición HA

### Community 89 - "Escenario CTF 06: Kerberoasting y Escalado de Privilegios en Active Directory"
Cohesion: 0.25
Nodes (7): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 06: Kerberoasting y Escalado de Privilegios en Active Directory, Paso 1: Extracción de Ticket TGS Kerberos, Paso 2: Escalado de Privilegios en API SCADA

### Community 90 - "⚡ Inicio Rápido"
Cohesion: 0.20
Nodes (10): 1. Iniciar la Co-Simulación Completa (Fase 3), 2. Co-Simulación HELICS sin root (Fase 7 — 10 federados, incluye SIS SIL-3), 3. Inspeccionar el Log CSV de Eventos en Tiempo Real, 4. Medir el Consumo Real de Recursos, 5. Detener y Limpiar, 📐 Arquitectura de Red (IEC 62443), CityLab — Cyber Range Ciberfísico Multisectorial (Fase 3 Ciudad Completa), 📚 Documentación Técnica Completa (+2 more)

### Community 91 - "🛡️ Federado 05 — Sistema de Seguridad SIS / ESD (SIL-3) (`fed_sis.py`)"
Cohesion: 0.29
Nodes (6): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Lógica Indesconectable SIL-3, 🧮 3. Envolvente de Seguridad Física (Safety Limits), 📡 4. Interfaz HELICS Pub-Sub, 💾 5. Presupuesto de Recursos y Memoria RAM, 🛡️ Federado 05 — Sistema de Seguridad SIS / ESD (SIL-3) (`fed_sis.py`)

### Community 92 - "📊 Federado 06 — Observer y Logger de Co-Simulación HELICS (`fed_logger.py`)"
Cohesion: 0.29
Nodes (6): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Captura y Registro de Eventos, 🗺️ 3. Esquema del Archivo CSV de Eventos (`cascading_events.csv`), 📡 4. Suscripciones HELICS, 💾 5. Presupuesto de Recursos y Memoria RAM, 📊 Federado 06 — Observer y Logger de Co-Simulación HELICS (`fed_logger.py`)

### Community 93 - "🖥️ Infraestructura 07 — Servidor SCADA Central, HA Cluster y Dashboard HMI"
Cohesion: 0.29
Nodes (6): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Control, Historian y Conmutación HA (High Availability), 🔐 3. Control de Acceso por Roles (RBAC Bearer Estático & Toggle `STRICT_AUTH`), 🌐 4. Endpoints REST API de Infraestructura SCADA / HMI / Viz (`:8080`, `:8085`, `:8090`), 💾 5. Presupuesto de Recursos y Memoria RAM, 🖥️ Infraestructura 07 — Servidor SCADA Central, HA Cluster y Dashboard HMI

### Community 94 - "🛡️ Infraestructura 08 — SIEM, SDN Controller y Active Directory Domain Controller"
Cohesion: 0.29
Nodes (6): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Defensa SDN y Correlación SIEM en Caliente, 🛡️ 3. Reglas de Correlación SIEM Destacadas, 🔀 4. Matriz de Flujos OpenFlow Microsegmentación OVS (`s3` OT / `s5` Honeypot), 💾 5. Presupuesto de Recursos y Memoria RAM, 🛡️ Infraestructura 08 — SIEM, SDN Controller y Active Directory Domain Controller

### Community 95 - "Escenario CTF 07: Anti-Forense y Borrado de Registros en Historian TSDB"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica y Respuesta Defensiva, 4. Flags CTF, Escenario CTF 07: Anti-Forense y Borrado de Registros en Historian TSDB, Paso 1: Ejecución del Borrado Anti-Forense

### Community 96 - "Escenario CTF 08: Insider Threat y Violación de Principio de Mínimo Privilegio RBAC"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 08: Insider Threat y Violación de Principio de Mínimo Privilegio RBAC, Paso 1: Intento de Escritura con Token de Auditor

### Community 97 - "Escenario CTF 09: Dosificación Química en Planta de Tratamiento de Agua (SWaT / Oldsmar Pattern)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 09: Dosificación Química en Planta de Tratamiento de Agua (SWaT / Oldsmar Pattern), Paso 1: Alteración de la Tasa de Dosificación

### Community 98 - "Escenario CTF 10: Falla Natural por Ola de Calor + Ataque Ciberfísico Simultáneo (Incident Attribution)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 10: Falla Natural por Ola de Calor + Ataque Ciberfísico Simultáneo (Incident Attribution), Paso 1: Ejecución del Ataque Híbrido

### Community 99 - "Escenario CTF 11: Ataque de Desincronización de Tiempo NTP / PTP (Time Synchronization Hardening)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 11: Ataque de Desincronización de Tiempo NTP / PTP (Time Synchronization Hardening), Paso 1: Falsificación de Respuestas NTP

### Community 100 - "Escenario CTF 12: Ransomware IT con Parada de Emergencia Operacional OT (Colonial Pipeline Pattern)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 12: Ransomware IT con Parada de Emergencia Operacional OT (Colonial Pipeline Pattern), Paso 1: Simulación de Cifrado IT y Decisión de Shutdown Operacional

### Community 101 - "Escenario CTF 13: Reconocimiento Pasivo en Redes OT (Onboarding Pasivo)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 13: Reconocimiento Pasivo en Redes OT (Onboarding Pasivo), Paso 1: Captura de Tráfico Pasivo

### Community 102 - "Escenario CTF 14: Escaneo Activo de Subredes OT (Segmentación Nmap)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 14: Escaneo Activo de Subredes OT (Segmentación Nmap), Paso 1: Ejecución de Escaneo Activo

### Community 103 - "Escenario CTF 15: Lectura de Telemetría Modbus sin Escritura"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 15: Lectura de Telemetría Modbus sin Escritura, Paso 1: Lectura de Memoria Modbus

### Community 104 - "Escenario CTF 16: Interacción con Trampas Deception (Honeypot OT)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 16: Interacción con Trampas Deception (Honeypot OT), Paso 1: Conexión al Honeypot

### Community 105 - "Escenario CTF 17: Tour Guiado por la API SCADA y Servidor HMI"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 17: Tour Guiado por la API SCADA y Servidor HMI, Paso 1: Exploración REST API HMI

### Community 106 - "Escenario CTF 18: Escritura Forzada de Coil Modbus Único (Manipulación Guiada)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 18: Escritura Forzada de Coil Modbus Único (Manipulación Guiada), Paso 1: Forzado de Escritura Modbus

### Community 107 - "Escenario CTF 19: Cadena de Pivoteo Guiado Attacker -> DMZ -> OT"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 19: Cadena de Pivoteo Guiado Attacker -> DMZ -> OT, Paso 1: Salto Secuencial de Pivoteo

### Community 108 - "Escenario CTF 20: Comparación de Hardening SCADA API (STRICT_AUTH Toggle)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 20: Comparación de Hardening SCADA API (STRICT_AUTH Toggle), Paso 1: Prueba de Petición con STRICT_AUTH=0 vs STRICT_AUTH=1

### Community 109 - "Escenario CTF 21: Respuesta a Pérdida de Visibilidad (Loss of View & Manual Isolation)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 21: Respuesta a Pérdida de Visibilidad (Loss of View & Manual Isolation), Paso 1: Detección y Respuesta IR

### Community 110 - "Escenario CTF 22: Ejercicio Purple Team y Medición de Métricas SOC (MTTD / MTTR)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 22: Ejercicio Purple Team y Medición de Métricas SOC (MTTD / MTTR), Paso 1: Ejecución del Test Purple Team

### Community 111 - "Escenario CTF 23: Defensa SDN Dinámica en Caliente (Safety vs Availability Trade-off)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 23: Defensa SDN Dinámica en Caliente (Safety vs Availability Trade-off), Paso 1: Aplicación de Reglas SDN

### Community 112 - "Escenario CTF 24: Evasión de Reglas de Correlación SIEM (Multi-IP Distributed Attack)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 24: Evasión de Reglas de Correlación SIEM (Multi-IP Distributed Attack), Paso 1: Ejecución de Evasión Distribuida

### Community 113 - "Escenario CTF 25: Ejercicio Tabletop de Crisis por Ransomware Industrial"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 25: Ejercicio Tabletop de Crisis por Ransomware Industrial, Paso 1: Ejecución del Simulador Tabletop

### Community 114 - "Escenario CTF 26: Capstone Campaña APT Persistente (Sandworm / ELECTRUM Pattern)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 26: Capstone Campaña APT Persistente (Sandworm / ELECTRUM Pattern), Paso 1: Ejecución de la Campaña APT

### Community 115 - "Escenario CTF 27: Ciberejercicio Simultáneo Red vs Blue con Motor de Arbitraje"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 27: Ciberejercicio Simultáneo Red vs Blue con Motor de Arbitraje, Paso 1: Ejecución del Ciberejercicio

### Community 116 - "Escenario CTF 28: Entorno Ciego Dinámico Anti-Memorización"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 28: Entorno Ciego Dinámico Anti-Memorización, Paso 1: Ejecución del Generador de Entorno Ciego

### Community 117 - "Escenario CTF 29: Recuperación Post-Incidente y Reintegración Operacional (Disaster Recovery)"
Cohesion: 0.29
Nodes (6): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 29: Recuperación Post-Incidente y Reintegración Operacional (Disaster Recovery), Paso 1: Ejecución del Procedimiento de Recuperación

### Community 119 - "CityLab — Guía de Operaciones (Fase 3 Ciudad Completa)"
Cohesion: 0.33
Nodes (6): 1. Ejecución de la Ciudad Completa (Fase 3), 2. Acceso al Servidor SCADA Central (DMZ), 3. Pruebas Automatizadas Locales (Smoke Test 7 Federados), 4. Escenarios CTF Disponibles, CityLab — Guía de Operaciones (Fase 3 Ciudad Completa), Modo Interactivo con Mininet + 7 Federados

### Community 120 - "main"
Cohesion: 0.33
Nodes (3): main(), Arranca el servidor. Bloqueante — llamar desde un hilo., Punto de entrada standalone del emulador OPC UA.

### Community 121 - "🛡️ Arquitectura del Cyber Range CityLab (Fase 3 Ciudad Completa)"
Cohesion: 0.25
Nodes (5): 🛡️ Arquitectura del Cyber Range CityLab (Fase 3 Ciudad Completa), 📌 Contexto del Proyecto y Presupuesto de Recursos, ⚡ Matriz de Co-Simulación HELICS y Flujo Ciberfísico, 📐 Topología de Red y Microsegmentación (IEC 62443), 📂 Índice de Documentación Quirúrgica por Federado e Infraestructura

### Community 122 - "TankPlant"
Cohesion: 0.40
Nodes (3): Advance plant state by dt seconds. Returns new level., Simple rule: if level below 1 m^3 or above 95% capacity, trip., TankPlant

### Community 128 - "TwoStageWaterPlant"
Cohesion: 0.16
Nodes (8): ChemicalDosingAttack, main(), Any, TestChemicalDosingAttack, physical/water package, Avanza el estado de la planta 2 etapas con motor EPANET. Retorna (t1_level_m3,…, Regla de disparo de protección de planta: - T1 desborde (>95%) o seco (<0.5m³)…, TwoStageWaterPlant

### Community 130 - "RansomwareOtImpactAttack"
Cohesion: 0.43
Nodes (4): main(), Any, RansomwareOtImpactAttack, TestRansomwareAttack

### Community 132 - "smoke_test_phase7.sh"
Cohesion: 0.25
Nodes (7): ENABLE_SIS_FEDERATE, HELICS_BROKER_PORT, HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase7.sh script

### Community 134 - "smoke_test_phase4.sh"
Cohesion: 0.29
Nodes (6): HELICS_BROKER_PORT, HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase4.sh script

## Knowledge Gaps
- **383 isolated node(s):** `PYTHONPATH`, `smoke_test_local.sh script`, `PYTHONPATH`, `smoke_test_phase2.sh script`, `PYTHONUNBUFFERED` (+378 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistorianTSDB` connect `HistorianTSDB` to `attack_apt_sandworm_campaign.py`, `SCADAAPIHandler`, `ThreadedHmiServer`, `scada_server.py`, `TestHistorianTSDB`, `._conn`, `IndustrialHmiEngine`, `TestScadaHistorianHTTPEndpoints`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `TwoStageWaterPlant` connect `TwoStageWaterPlant` to `fed_icssim.py`, `RansomwareOtImpactAttack`, `SafetyInstrumentedLogic`, `EpanetHydraulicSolver`, `HistorianTSDB`, `attack_grid_heatwave_attribution.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `OpcUaClient` connect `OpcUaClient` to `Dnp3MasterClient`, `OpcUaServer`, `TestOpcUaServerClient`, `main`, `TestOpcUaNodeSpace`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `HistorianTSDB` (e.g. with `HistorianAntiForensicsAttack` and `PostIncidentRecovery`) actually correct?**
  _`HistorianTSDB` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `SiemCorrelationEngine` (e.g. with `HoneypotTouch` and `NtpTimeSpoofingAttack`) actually correct?**
  _`SiemCorrelationEngine` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TwoStageWaterPlant` (e.g. with `ChemicalDosingAttack` and `GridHeatwaveAttributionAttack`) actually correct?**
  _`TwoStageWaterPlant` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `OpcUaServer` (e.g. with `TestScenario18ModbusWrite` and `TestOpcUaNodeSpace`) actually correct?**
  _`OpcUaServer` has 4 INFERRED edges - model-reasoned connections that need verification._