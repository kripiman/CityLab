# Graph Report - CityLab  (2026-08-28)

## Corpus Check
- 212 files · ~97,302 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1852 nodes · 3214 edges · 139 communities (128 shown, 11 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 174 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `65a12692`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- running_modbus_server
- KerberosServerThread
- SmartLightingSystem
- SCADAPrimarySecondaryCluster
- ModbusDpiEngine
- BacnetListener
- ElectricalSubstationGrid
- 金律 — 蓄意之弱點
- BacnetAttacker
- VizRequestHandler
- TestRBACResolver
- HistorianAntiForensicsAttack
- profile_resources.py
- Dnp3OutstationState
- ScoreboardEngine
- rbac.py
- TestOpcUaServerClient
- .encode
- test_flag_service.py
- exploit_modbus.py
- siem_pipeline.py
- 🛡️ Arquitectura del Cyber Range CityLab (IEC 62443 / Co-Simulación Ciberfísica)
- .ingest_zeek_log
- Especificación de Requisitos de Software (ERS)
- OpcUaClient
- Dnp3BreakerAttack
- SiemCorrelationEngine
- topology.py
- RBACResolver
- TestScadaRBACHTTPEndpoints
- socket
- attack_apt_sandworm_campaign.py
- NtpTimeSpoofingAttack
- OtActiveScan
- LiveSdnDefense
- fed_icssim.py
- IndustrialHmiEngine
- EpanetHydraulicSolver
- ChemicalDosingAttack
- HistorianTSDB
- traffic.py
- TestHistorianTSDB
- ._conn
- HoneypotTouch
- InsiderRbacAttack
- KerberoastAttack
- execute_cascading_attack
- PostIncidentRecovery
- PurpleTeamMttd
- test_scenario_manifest.py
- TestScadaHistorianHTTPEndpoints
- ModbusReadOnly
- OpcUaServer
- TestOpcUaNodeSpace
- TritonLowSlowAttack
- citylab.sh
- Development Workflow
- BlindRandomizedEnv
- run_modbus_attack
- properties
- RansomwareTabletop
- RedVsBlueMatch
- SCADAAPIHandler
- OtHoneypotServer
- spoof_goose_trip
- create_federate
- SafetyInstrumentedLogic
- .enforce_safety_override
- 4. Matriz de Escenarios CTF / Ataques Industriales
- Objetivo
- gridlabd_federate.py
- 🧪 品保者提示 QA — CityLab Cyber Range (IEC 62443)
- run_phase1.sh
- run_phase2.sh
- run_phase3.sh
- CityLab - Development Guidelines
- CityLab - Product Overview
- TwoStageWaterPlant
- Escenario CTF 09: Dosificación Química en Planta de Tratamiento de Agua (SWaT /
- smoke_test_phase7.sh
- GridHeatwaveAttributionAttack
- HmiRequestHandler
- poc_modbus_test.py
- Any
- Escenario CTF 14: Escaneo Activo de Subredes OT (Segmentación Nmap)
- load_scenario_manifest
- ThreadedFlagServer
- smoke_test_phase2.sh
- smoke_test_phase3.sh
- smoke_test_phase4.sh
- Iec61850Server
- Dnp3MasterClient
- Escenario CTF 01: Apagón Urbano en Cascada (THM / HTB Style)
- run_scenario.py
- properties
- Escenario CTF 08: Insider Threat y Violación de Principio de Mínimo Privilegio R
- .read
- build_server
- Escenario CTF 13: Reconocimiento Pasivo en Redes OT (Onboarding Pasivo)
- Escenario CTF 16: Interacción con Trampas Deception (Honeypot OT)
- NtcipListener
- Escenario CTF 19: Cadena de Pivoteo Guiado Attacker -> DMZ -> OT
- Escenario CTF 20: Comparación de Hardening SCADA API (STRICT_AUTH Toggle)
- main
- Escenario CTF 26: Capstone Campaña APT Persistente (Sandworm / ELECTRUM Pattern)
- cmd_down
- conftest.py
- smoke_test_local.sh
- Dnp3Server
- Escenario CTF 12: Ransomware IT con Parada de Emergencia Operacional OT (Colonia
- start_broker.sh
- install_deps.sh
- start_openplc.sh
- patch
- patch
- 🎓 CityLab Cyber Range — Roadmap Curricular de Escenarios CTF (IEC 62443 / GICSP
- Enum
- patch
- IEC61850DataSet
- test_flag_server
- enum
- items
- required
- properties
- id
- schema.json
- Escenario CTF 24: Evasión de Reglas de Correlación SIEM (Multi-IP Distributed At
- TankPlant
- _emulator_harness.py
- Any

## God Nodes (most connected - your core abstractions)
1. `HistorianTSDB` - 58 edges
2. `SiemCorrelationEngine` - 47 edges
3. `cmd_down()` - 34 edges
4. `OpcUaServer` - 30 edges
5. `running_modbus_server()` - 29 edges
6. `金律 — 蓄意之弱點` - 27 edges
7. `IndustrialHmiEngine` - 26 edges
8. `SCADAPrimarySecondaryCluster` - 26 edges
9. `Arquitectura verificada (referencia; confírmala, no la asumas)` - 25 edges
10. `TwoStageWaterPlant` - 24 edges

## Surprising Connections (you probably didn't know these)
- `2. Estructura del Proyecto y Módulos de Código` --references--> `cmd_down()`  [EXTRACTED]
  docs/ARCHITECTURE.md → citylab.sh
- `2. Descripción General` --references--> `cmd_down()`  [EXTRACTED]
  docs/ERS.md → citylab.sh
- `4. Requisitos No Funcionales (RNF)` --references--> `cmd_down()`  [EXTRACTED]
  docs/ERS.md → citylab.sh
- `1. Comandos de Ciclo de Vida del Cyber Range (`./citylab.sh`)` --references--> `cmd_down()`  [EXTRACTED]
  docs/OPERATIONS.md → citylab.sh
- `⚡ Inicio Rápido` --references--> `cmd_down()`  [EXTRACTED]
  README.md → citylab.sh

## Import Cycles
- None detected.

## Communities (139 total, 11 thin omitted)

### Community 0 - "running_modbus_server"
Cohesion: 0.09
Nodes (14): El entrypoint CLI main() ejecuta el escaneo activo con flags sin errores., El entrypoint CLI main() ejecuta la sobre-dosificación contra el puerto de test, Verifica ejecución de la CLI., El entrypoint CLI main() ejecuta el vector replay contra el puerto de test sin e, El entrypoint CLI main() ejecuta la manipulación Triton sobre el puerto de test, Verifica que el ataque force_start active Coil 0 en el datastore del emulador., Verifica que el ataque force_stop active Coil 1 en el datastore del emulador., Verifica que el ataque fault active START y STOP vía socket real. (+6 more)

### Community 1 - "KerberosServerThread"
Cohesion: 0.17
Nodes (10): DomainControllerEmulator, KerberosServerThread, LdapServerThread, main(), socket, Escuchador SMB v2/v3 en puerto 445., Orquestador completo del controlador de dominio h_dc., Escuchador LDAP en puerto 389. (+2 more)

### Community 2 - "SmartLightingSystem"
Cohesion: 0.08
Nodes (15): main(), main(), Any, Lee el coil de apagón del PLC de alumbrado. False si no hay PLC o falla la lectu, read_blackout_command(), TestPhase4Federates, Any, Modelo físico determinista de Red de Alumbrado Público Inteligente. (+7 more)

### Community 3 - "SCADAPrimarySecondaryCluster"
Cohesion: 0.10
Nodes (14): FailoverExploitAttack, main(), Any, Verifica que la ausencia de heartbeat fuerce la conmutación a PRIMARY., Verifica ejecución CLI., TestFailoverAttack, 2. Cadena de Ataque y Ejecución Paso a Paso, Any (+6 more)

### Community 4 - "ModbusDpiEngine"
Cohesion: 0.09
Nodes (17): Ejercita la lógica de producción poll_plcs_once() y verifica la transición real, main(), ModbusDpiEngine, ModbusDpiProxyServer, socket, RateLimiter, Controlador de tasa de escrituras por IP de origen., Motor de Inspección Profunda de Paquetes (DPI) Modbus/TCP. (+9 more)

### Community 5 - "BacnetListener"
Cohesion: 0.21
Nodes (5): BacnetListener, main(), Listener BACnet/IP (UDP 47808) de baja fidelidad para automatización de edificio, run_server(), TestBacnetListener

### Community 6 - "ElectricalSubstationGrid"
Cohesion: 0.12
Nodes (14): Estado actual (verificado por lectura directa del código; las Fases de abajo NO , ElectricalSubstationGrid, GridParams, Modelo físico de subestación de transmisión / distribución eléctrica., Avanza la simulación dinámica de la red eléctrica dt_s segundos., GasPipelineParams, GasPipelinePlant, Modelo físico dinámico de gasoducto con estación compresora. (+6 more)

### Community 7 - "金律 — 蓄意之弱點"
Cohesion: 0.12
Nodes (20): Architecture — the big picture, 5. Capa de Emulación de Dispositivos de Campo (OT), 7. Pipeline de Seguridad: SIEM Central y Defensa Dinámica SDN, 📌 1. Visión General del Módulo, 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Reenvío Asíncrono y Detección SIEM, 🛡️ 3. Reglas de Correlación SIEM en Código (`network/siem_pipeline.py`), 🔀 4. Matriz de Flujos OpenFlow Microsegmentación OVS (`s3` OT / `s5` Honeypot) (+12 more)

### Community 8 - "BacnetAttacker"
Cohesion: 0.11
Nodes (17): BacnetAttacker, main(), Any, Emulador de ataque BACnet/IP sobre UDP 47808., main(), NtcipAttacker, Any, Emulador de ataque NTCIP 1202 sobre TCP 161. (+9 more)

### Community 9 - "VizRequestHandler"
Cohesion: 0.14
Nodes (10): TestVizServer, TestCityVisualizer, CityVisualizerStateEngine, main(), Any, HTTPServer, ThreadingMixIn, Motor de estado de visualización presentacional 2D/3D. (+2 more)

### Community 10 - "TestRBACResolver"
Cohesion: 0.07
Nodes (15): Bearer auditor:<operator_token> → 403 (rol incorrecto para token)., Rol auditor puede leer telemetría pero no /api/control/write., Rol operator puede acceder a /api/control/read pero no /api/control/write., Rol engineer tiene acceso completo (wildcard)., Rol None (no autenticado) → siempre False., reload() recarga almacén de tokens con cambios de env var., Tests unitarios del RBACResolver (network/rbac.py)., Bearer <token> plano → rol operator en STRICT_AUTH=0 (modo CTF). (+7 more)

### Community 11 - "HistorianAntiForensicsAttack"
Cohesion: 0.21
Nodes (7): HistorianAntiForensicsAttack, main(), Any, Verifica que el ataque purgue físicamente los registros de telemetría de la base, Verifica ejecución CLI con DB temporal., TestAntiForensicsAttack, 2. Cadena de Ataque y Ejecución Paso a Paso

### Community 12 - "profile_resources.py"
Cohesion: 0.16
Nodes (19): resource.getrusage debe devolver un RSS positivo real, no una estimación fija., El muestreo real no debe clasificar procesos ajenos al laboratorio., TestProfileResources, classify(), collect_sample(), _iter_processes_proc(), _iter_processes_psutil(), main() (+11 more)

### Community 13 - "Dnp3OutstationState"
Cohesion: 0.14
Nodes (10): TestSdnAndDnp3Sa, Dnp3OutstationState, Dnp3ProtocolHandler, Decodifica tramas DNP3 TCP/IP y genera respuestas de Outstation DNP3 validas., Procesa una trama DNP3 entrante y devuelve el paquete de respuesta DNP3., Construye un paquete de respuesta DNP3 READ conteniendo BI (0,1) y AI (0,1,2)., Construye respuesta DNP3 CROB ACK (Success)., Envuelve la carga útil en la trama Link Layer de DNP3 con CRCs. (+2 more)

### Community 14 - "ScoreboardEngine"
Cohesion: 0.13
Nodes (17): main(), parse_iso_or_epoch(), Genera un reporte completo de Scorecard y métricas SOC., Convierte un timestamp (ISO 8601 string o epoch float) a segundos epoch float., Métricas SOC calculadas., Motor de análisis de eventos SIEM y cálculo de scorecard de ciberdefensa., Recupera los eventos ECS del buffer del SIEM central., Calcula MTTD y MTTR analizando la secuencia temporal de eventos ECS. (+9 more)

### Community 15 - "rbac.py"
Cohesion: 0.11
Nodes (21): Commands, Golden rule — intentional vulnerabilities, Gotchas, What this is, 3. Topología de Red y Microsegmentación (IEC 62443), 1. Comandos de Ciclo de Vida del Cyber Range (`./citylab.sh`), 2. Acceso a Servicios y Dashboards de Supervisión, 3. Pruebas y Validación Automatizada (+13 more)

### Community 16 - "TestOpcUaServerClient"
Cohesion: 0.11
Nodes (13): El servidor responde ACK al HEL correctamente (UA/TCP handshake)., Lectura de nodo Float (WaterTank_Level, NodeId=1001) retorna valor numérico., Lectura de nodo Boolean (WaterPump_State, NodeId=1002)., Lectura de nodo Int32 (Traffic_Light_State, NodeId=4001)., Lectura de NodeId desconocido retorna None (BadNodeIdUnknown)., Escritura directa al NodeSpace y lectura confirmada vía cliente., Browse retorna lista con conteo correcto de nodos., GetEndpoints responde con 200 de servicio (SecurityMode=None). (+5 more)

### Community 17 - ".encode"
Cohesion: 0.20
Nodes (3): Codifica un PDU GOOSE binario en formato TLV / APDU con ConfRev y Test mode., Publica un paquete GOOSE inmediatamente hacia goose_dest., Publica una muestra SV de voltaje y corriente hacia sv_dest.

### Community 18 - "test_flag_service.py"
Cohesion: 0.16
Nodes (15): generate_flag_hmac(), RateLimiter, Limitador de tasa de peticiones deslizante por clave., Genera una flag dinámica e inmemorizable: FLAG_<id>{HMAC_SHA256(seed,…, Verifica si la flag enviada coincide exactamente con la calculada para la…, verify_flag_hmac(), Tests unitarios y de integración para network/flag_service.py (Fase 1 - Roadmap), Verifica la evaluación del oráculo de estado de sector SCADA. (+7 more)

### Community 19 - "exploit_modbus.py"
Cohesion: 0.19
Nodes (22): action_fault(), action_sabotage(), action_start(), action_status(), action_stop(), main(), print_status(), ModbusTcpClient (+14 more)

### Community 20 - "siem_pipeline.py"
Cohesion: 0.13
Nodes (9): main(), BaseHTTPRequestHandler, HTTPServer, ThreadingMixIn, SiemRequestHandler, ThreadedSiemServer, Verifica que la Regla 2 (Industroyer2 GOOSE Spoofing) active alerta crítica., Verifica que el daemon central SIEM reciba eventos de honeypot y proxy, gatillan (+1 more)

### Community 21 - "🛡️ Arquitectura del Cyber Range CityLab (IEC 62443 / Co-Simulación Ciberfísica)"
Cohesion: 0.11
Nodes (18): Architectural Patterns, Core Components, Directory Organization, CityLab - Project Structure, File Naming Conventions, 1. Visión General del Sistema y Filosofía de Diseño, 2. Estructura del Proyecto y Módulos de Código, 4. Capa Ciberfísica y Co-Simulación HELICS (+10 more)

### Community 22 - ".ingest_zeek_log"
Cohesion: 0.19
Nodes (11): 1. Breve del Escenario (Storyline), 3. Lección Pedagógica y Respuesta Defensiva, 4. Flags CTF, Escenario CTF 07: Anti-Forense y Borrado de Registros en Historian TSDB, EcsEvent, forward_event_to_central_siem(), Any, Aplica reglas de correlación SOC sobre los eventos ingresados. (+3 more)

### Community 23 - "Especificación de Requisitos de Software (ERS)"
Cohesion: 0.10
Nodes (21): 2. Descripción General, 4. Requisitos No Funcionales (RNF), Especificación de Requisitos de Software (ERS), Proyecto: Cyber Range Ciberfísico Multisectorial (CityLab), 🎯 DECISIONES DE DISEÑO PEDAGÓGICO CTF (HALLAZGOS INTENCIONALES), ✅ REPORTE DE CIERRE DE AUDITORÍA — CityLab Cyber Range, 📈 EVOLUCIÓN DEL GRAFO DE CONOCIMIENTO, Programa de Remediación IEC 62443 · Cierre de 3 Semanas (+13 more)

### Community 24 - "OpcUaClient"
Cohesion: 0.16
Nodes (8): OpcUaClient, Cliente OPC UA TCP mínimo para pruebas de integración.      Replica exactamente, Establece conexión y realiza handshake HEL/ACK + OpenSecureChannel., Lee el valor de un nodo OPC UA., Lista nodos disponibles en el servidor., Escribe un valor numérico a un nodo OPC UA sobre la red., Consulta los endpoints disponibles (GetEndpoints)., Recibe un mensaje UA/TCP. Retorna (tipo, body) o None.

### Community 25 - "Dnp3BreakerAttack"
Cohesion: 0.17
Nodes (11): Dnp3BreakerAttack, main(), Any, Emulador de ataque DNP3 CROB sobre TCP 20000., Verifica que el ataque DNP3 CROB TRIP abra el disyuntor real en el servidor DNP3, Verifica que el ataque DNP3 CROB CLOSE cierre el disyuntor real., Verifica que si el outstation DNP3 está inalcanzable caiga en TABLETOP_FALLBACK., Verifica invocación CLI. (+3 more)

### Community 26 - "SiemCorrelationEngine"
Cohesion: 0.11
Nodes (13): main(), Any, SiemRuleEvasion, Verifica que el ataque distribuido multi-IP evada el umbral de disparo del SIEM., Prueba negativa / anti-trampa: ráfaga de eventos desde una sola IP sí activa ale, Verifica la ejecución CLI., TestScenario24SiemEvasion, Exporta buffer de eventos en formato JSON compatible con Logstash / Elasticsearc (+5 more)

### Community 27 - "topology.py"
Cohesion: 0.13
Nodes (21): CLI, Mininet, apply_egress_containment(), apply_fw_configuration(), cleanup_egress_containment(), configure_host_routes(), CustomCLI, Iec62443Topo (+13 more)

### Community 28 - "RBACResolver"
Cohesion: 0.12
Nodes (12): TestScenario20StrictAuth, _load_env_file(), _load_token_store(), Intenta autenticar contra el AD LDAP emulado de h_dc (`ad_dc_emulator.py`).…, Resuelve el rol de una petición HTTP a partir de su cabecera Authorization.…, Recarga el almacén de tokens (útil tras rotación de credenciales)., Resuelve el rol asociado a una cabecera Authorization. Args: auth_header: Valor…, Verifica si el rol tiene permiso para acceder al endpoint. Args: role: Rol… (+4 more)

### Community 29 - "TestScadaRBACHTTPEndpoints"
Cohesion: 0.14
Nodes (9): Tests de integración HTTP para RBAC en scada_server., /health responde 200 sin Authorization., /api/telemetry con token válido → 200., /api/telemetry sin token → 401., /api/whoami retorna el rol del token presentado., /api/whoami con token legado → rol operator (modo CTF)., STRICT_AUTH=1 rechaza token plano legado con 403., Auditor recibe 403 en /api/control/write. (+1 more)

### Community 30 - "socket"
Cohesion: 0.15
Nodes (10): socket, Maneja una conexión de cliente OPC UA., Lee exactamente n bytes del socket., Responde a HEL con ACK — primer paso del handshake UA/TCP., Maneja OpenSecureChannel con SecurityMode=None., Despacha servicios OPC UA: Read, Browse, GetEndpoints., Retorna la lista de endpoints disponibles., Lee el valor de un nodo del espacio OPC UA. (+2 more)

### Community 31 - "attack_apt_sandworm_campaign.py"
Cohesion: 0.20
Nodes (8): AptSandwormCampaign, main(), Any, main(), OtPassiveRecon, Any, TestPassiveRecon, TestScenario26Apt

### Community 32 - "NtpTimeSpoofingAttack"
Cohesion: 0.15
Nodes (11): main(), NtpTimeSpoofingAttack, Any, Verifica que el ataque inyecte muestras con timestamp manipulado en el Historian, Verifica ejecución CLI., TestTimeSpoofingAttack, 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso (+3 more)

### Community 33 - "OtActiveScan"
Cohesion: 0.20
Nodes (10): main(), OtActiveScan, Escáner activo de servicios y puertos OT., Realiza un probe TCP connect a un endpoint host:port con timeout corto., Ejecuta el escaneo activo TCP sobre la lista de objetivos dada o los defaults., Verifica que el escáner detecte empíricamente puertos abiertos y cerrados usando, Si no hay objetivos alcanzables en localhost, aplica fallback TABLETOP_FALLBACK, TestActiveScan (+2 more)

### Community 34 - "LiveSdnDefense"
Cohesion: 0.23
Nodes (8): LiveSdnDefense, main(), TestScenario23Sdn, apply_circuit_breaker(), apply_sdn_flow_rules(), main(), Aplica la matriz de microsegmentación OpenFlow en los switches OVS s3 (OT) y s5, Dispara una regla Circuit Breaker dinámica para aislar un host en caso de DoS/Fl

### Community 35 - "fed_icssim.py"
Cohesion: 0.16
Nodes (13): create_federate(), main(), Any, helics_federate, ModbusTcpClient, read_actuator_running(), ElecPlant, GasPlant (+5 more)

### Community 36 - "IndustrialHmiEngine"
Cohesion: 0.12
Nodes (18): main(), Any, Explora la API REST y estado HMI SCADA vía HTTP o motor directo., ScadaTour, Verifica la exploración directa sobre el motor HMI., Verifica la consulta HTTP contra el servidor HMI real en puerto alto., Verifica la invocación CLI., TestScadaTour (+10 more)

### Community 37 - "EpanetHydraulicSolver"
Cohesion: 0.17
Nodes (8): TestPhysicsEngine, EpanetHydraulicSolver, PipeConfig, PumpConfig, Solver hidráulico de red de distribución de agua (Modelo didáctico Hazen-William, Calcula la pérdida de fricción en la tubería usando Hazen-Williams., Calcula la presión generada por la bomba según su curva TDH., physical/water/plant_water.py — Modelo físico de tratamiento de agua en 2 etapas

### Community 38 - "ChemicalDosingAttack"
Cohesion: 0.23
Nodes (8): ChemicalDosingAttack, main(), Any, Ejecuta el ataque escribiendo en el Holding Register Modbus/TCP y confirmando el, Ataque real vía Modbus/TCP muta el Holding Register 10 en el PLC y confirma cont, Dosificación dentro de rango seguro muta el registro pero no marca contaminación, Si el PLC no está disponible, el ataque activa el modo TABLETOP_FALLBACK documen, TestChemicalDosingAttack

### Community 39 - "HistorianTSDB"
Cohesion: 0.17
Nodes (11): main(), Any, Ataque Replay con sabotaje físico y verificación de divergencia telemetría vs pr, StuxnetReplayAttack, Verifica que el ataque sabotee el PLC vía Modbus mientras el Historian recibe re, Si el PLC no está activo, el ataque activa el modo TABLETOP_FALLBACK documentado, TestStuxnetAttack, HistorianTSDB (+3 more)

### Community 40 - "traffic.py"
Cohesion: 0.15
Nodes (12): create_federate(), main(), helics_federate, helics_input, helics_publication, physical/transport package, LightPhase, Enum (+4 more)

### Community 41 - "TestHistorianTSDB"
Cohesion: 0.10
Nodes (10): prune() elimina puntos más antiguos manteniendo los más recientes., query() con parámetro `since` filtra por timestamp correctamente., Tests unitarios del módulo historian.py (HistorianTSDB)., write() persiste puntos individuales y query() los recupera correctamente., write_snapshot() persiste el estado completo y query_snapshots() lo recupera., last() devuelve el snapshot más reciente de un sector., last() devuelve None cuando el sector no tiene datos., sectors() lista exactamente los sectores con datos registrados. (+2 more)

### Community 42 - "._conn"
Cohesion: 0.16
Nodes (9): Connection, Any, Escribe un punto de telemetría.          Args:             sector:    Nombre del, Escribe el snapshot JSON completo de un sector.          Permite consultas de te, Consulta puntos de telemetría históricos.          Args:             sector: Sec, Consulta snapshots completos del sector.          Returns:             Lista de, Lista los sectores con datos en el historian., Elimina puntos excedentes para mantener retención máxima por sector.          Ar (+1 more)

### Community 43 - "HoneypotTouch"
Cohesion: 0.22
Nodes (9): HoneypotTouch, main(), Any, Verifica que la conexión socket real al Honeypot dispare la alerta en el pipelin, Verifica que si el honeypot está inalcanzable caiga en TABLETOP_FALLBACK., Verifica la invocación CLI., TestHoneypotTouch, Inicia OtHoneypotServer en puerto alto y asegura stop() en finally. (+1 more)

### Community 44 - "InsiderRbacAttack"
Cohesion: 0.24
Nodes (7): InsiderRbacAttack, main(), Any, Verifica que con STRICT_AUTH=1 el rol auditor sea bloqueado para writes., Verifica que con STRICT_AUTH=0 el rol auditor siga sin permiso de escritura en l, Verifica invocación CLI., TestInsiderRbacAttack

### Community 45 - "KerberoastAttack"
Cohesion: 0.18
Nodes (10): KerberoastAttack, main(), Any, Verifica si el servicio KDC Kerberos está respondiendo en la red., Verifica que el ataque solicite y reciba un ticket TGS vía socket real TCP al KD, Verifica que si el KDC está inaccesible caiga en TABLETOP_FALLBACK sin romper., Verifica la invocación por CLI., TestKerberoastAttack (+2 more)

### Community 46 - "execute_cascading_attack"
Cohesion: 0.16
Nodes (11): execute_cascading_attack(), force_coil(), main(), Any, Ejecuta ataque multi-sectorial cascada vía sockets Modbus reales o fallback., read_plc_state(), Verifica que el ataque multi-sectorial ejecute writes reales vía Modbus/TCP., Verifica que si ningún objetivo está disponible caiga en TABLETOP_FALLBACK. (+3 more)

### Community 47 - "PostIncidentRecovery"
Cohesion: 0.18
Nodes (9): main(), PostIncidentRecovery, Any, TestScenario29Recovery, 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF (+1 more)

### Community 48 - "PurpleTeamMttd"
Cohesion: 0.18
Nodes (10): main(), PurpleTeamMttd, Any, TestScenario22PurpleTeam, 7. Fase 4 — Scoreboard y Métricas MTTD/MTTR Automáticas, 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica (+2 more)

### Community 49 - "test_scenario_manifest.py"
Cohesion: 0.15
Nodes (12): Tests unitarios para la validación de manifiestos YAML de escenarios contra…, Valida exhaustivamente cada uno de los 29 manifiestos generados contra…, Verifica que schema.json sea un esquema JSON válido., Valida el manifiesto piloto scenario_01.yml contra schema.json., Valida que todos los tipos de checks permitidos pasen la validación., Verifica que un manifiesto inválido falle la validación., test_all_29_manifests_valid(), test_all_check_types_schema() (+4 more)

### Community 50 - "TestScadaHistorianHTTPEndpoints"
Cohesion: 0.16
Nodes (8): Tests de integración HTTP para los endpoints /api/history del SCADA Server., Arrancar un servidor HTTP de test con el handler real del SCADA., Helper: realiza GET con Bearer token y retorna (status_code, json_body)., GET /api/history?sector=water retorna filas históricas del sector., GET /api/history?sector=water&field=pressure filtra por campo., GET /api/history sin sector retorna 400., GET /api/history/snapshot?sector=water retorna snapshots del sector., TestScadaHistorianHTTPEndpoints

### Community 51 - "ModbusReadOnly"
Cohesion: 0.31
Nodes (6): main(), ModbusReadOnly, Lee telemetría vía Modbus/TCP en modo pasivo sin escrituras., Verifica que la lectura pasiva lea correctamente valores reales del datastore de, Verifica que ante un host no alcanzable caiga en TABLETOP_FALLBACK., TestModbusRead

### Community 52 - "OpcUaServer"
Cohesion: 0.17
Nodes (7): OpcUaNodeSpace, OpcUaServer, Lista todos los nodos disponibles., Servidor TCP que emula el protocolo UA/TCP de OPC UA.      Suficiente para finge, Envía un mensaje UA/TCP., Espacio de nodos OPC UA en memoria. Thread-safe., TestProtocolFidelityPhase3

### Community 53 - "TestOpcUaNodeSpace"
Cohesion: 0.13
Nodes (8): Tests unitarios del espacio de nodos OpcUaNodeSpace., read() retorna datos correctos para un nodo existente., read() retorna None para un NodeId desconocido., write() actualiza el valor y read() lo refleja., write() retorna False para NodeId desconocido., browse() lista todos los nodos del espacio., all_values() agrupa datos por sector correctamente., TestOpcUaNodeSpace

### Community 54 - "TritonLowSlowAttack"
Cohesion: 0.23
Nodes (8): main(), Any, Ataque de manipulación progresiva con evasión de disparo de interlocks SIS., TritonLowSlowAttack, Verifica manipulación de proceso vía Modbus manteniendo valores bajo umbral SIS, Manipulación sobre el umbral de seguridad provoca disparo inmediato del SIS (Pér, Si el PLC no está activo, el ataque activa el modo TABLETOP_FALLBACK documentado, TestTritonAttack

### Community 55 - "citylab.sh"
Cohesion: 0.33
Nodes (12): c_err(), c_info(), cmd_profile(), cmd_smoke(), cmd_status(), cmd_test(), cmd_up(), main() (+4 more)

### Community 56 - "Development Workflow"
Cohesion: 0.15
Nodes (13): Build Systems and Development Tools, Core Dependencies, Development Workflow, CityLab - Technology Stack, Platform Requirements, Programming Languages and Versions, Runtime Environment, Any (+5 more)

### Community 57 - "BlindRandomizedEnv"
Cohesion: 0.22
Nodes (9): BlindRandomizedEnv, main(), Any, TestScenario28Blind, 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF (+1 more)

### Community 58 - "run_modbus_attack"
Cohesion: 0.45
Nodes (9): connect(), do_fault(), do_start_stop_blast(), main(), ModbusTcpClient, Ejecuta ataque Modbus/TCP contra PLC objetivo vía socket real o fallback tableto, read_coils(), run_modbus_attack() (+1 more)

### Community 59 - "properties"
Cohesion: 0.17
Nodes (12): properties, expect, field, pattern, query, rule, rule_id, sector (+4 more)

### Community 60 - "RansomwareTabletop"
Cohesion: 0.22
Nodes (9): main(), Any, RansomwareTabletop, TestScenario25Tabletop, 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF (+1 more)

### Community 61 - "RedVsBlueMatch"
Cohesion: 0.22
Nodes (9): main(), Any, RedVsBlueMatch, TestScenario27RedBlue, 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF (+1 more)

### Community 62 - "SCADAAPIHandler"
Cohesion: 0.13
Nodes (4): BaseHTTPRequestHandler, SCADAAPIHandler, Verifica que IndustrialHmiEngine y HmiRequestHandler autentiquen exitosamente co, TestHmiServer

### Community 63 - "OtHoneypotServer"
Cohesion: 0.26
Nodes (3): main(), OtHoneypotServer, TestHoneypotServer

### Community 64 - "spoof_goose_trip"
Cohesion: 0.15
Nodes (9): is_multicast_addr(), main(), Construye y transmite un paquete GOOSE malicioso de disparo de interruptor., spoof_goose_trip(), Verifica la codificación y decodificación binaria del PDU GOOSE., Ataque real vía socket UDP provoca mutación de estado observable en el IED., Paquetes UDP malformados no deben mutar el estado del interruptor., El entrypoint CLI main() ejecuta ráfagas de spoofing sobre el puerto de test sin (+1 more)

### Community 65 - "create_federate"
Cohesion: 0.25
Nodes (9): Enum, create_federate(), HospitalPlant, main(), PowerState, helics_federate, helics_input, helics_publication (+1 more)

### Community 66 - "SafetyInstrumentedLogic"
Cohesion: 0.12
Nodes (10): create_federate(), main(), Any, helics_sim/fed_sis.py — Safety Instrumented System (SIS / ESD Independiente) (Fa, Lógica de interlocks SIL-3 independiente., Evalúa los interlocks de seguridad física.                  Retorna (must_trip,, SafetyInstrumentedLogic, SafetyInterlockLimits (+2 more)

### Community 67 - ".enforce_safety_override"
Cohesion: 0.22
Nodes (11): 1. Introducción, 3. Requisitos Funcionales Específicos, 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Lógica Indesconectable SIL-3, 🧮 3. Envolvente de Seguridad Física (Safety Limits), 📡 4. Interfaz HELICS Pub-Sub, 💾 5. Presupuesto de Recursos y Memoria RAM, 🛡️ Federado 05 — Sistema de Seguridad SIS / ESD (SIL-3) (`fed_sis.py`) (+3 more)

### Community 68 - "4. Matriz de Escenarios CTF / Ataques Industriales"
Cohesion: 0.05
Nodes (43): Any, 4. Matriz de Escenarios CTF / Ataques Industriales, 1. Breve del Escenario (Storyline), 2. Mapa de Componentes e IPs, 3. Cadena de Ataque y Ejecución Paso a Paso, 4. Detección y Regla SOC / SIEM (Blue Team), 5. Flags del Desafío CTF, Escenario CTF 02: Inyección de Mensajes GOOSE IEC 61850 (Estilo Industroyer2 / U (+35 more)

### Community 69 - "Objetivo"
Cohesion: 0.14
Nodes (19): 6. Capa de Supervisión, DMZ y Servicios Centrales, 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Control, DPI Proxy e Historian, 🔀 3. Modbus DPI Proxy y Enrutamiento por Unit ID (`network/modbus_proxy.py`), 🔄 4. Alta Disponibilidad (HA) y Sincronización de Estado (`network/scada_ha.py`), 🔐 5. Control de Acceso por Roles (RBAC Bearer Estático & Toggle `STRICT_AUTH`), 🌐 6. Endpoints REST API de Infraestructura SCADA / HMI / Viz (`:8080`, `:8085`, , 🖥️ Infraestructura 07 — Servidor SCADA Central, HA Cluster, Modbus DPI Proxy y H (+11 more)

### Community 70 - "gridlabd_federate.py"
Cohesion: 0.36
Nodes (7): create_federate(), main(), helics_federate, helics_input, helics_publication, start_gridlabd(), stop_gridlabd()

### Community 71 - "🧪 品保者提示 QA — CityLab Cyber Range (IEC 62443)"
Cohesion: 0.40
Nodes (4): 金律 — 蓄意之弱點，兩枝皆須測, 🧪 品保者提示 QA — CityLab Cyber Range (IEC 62443), PASO 0.5 — 「test 已加/已過」之分診（若驗一 build 報則必）, test 質之 checklist（QA 病，須明搜之）

### Community 72 - "run_phase1.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase1.sh script

### Community 73 - "run_phase2.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase2.sh script

### Community 74 - "run_phase3.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase3.sh script

### Community 75 - "CityLab - Development Guidelines"
Cohesion: 0.29
Nodes (7): Code Quality Standards Analysis, Development Workflow Guidelines, CityLab - Development Guidelines, Practices Followed Throughout Codebase, Semantic Patterns Overview, Structural Conventions, Textual Standards

### Community 76 - "CityLab - Product Overview"
Cohesion: 0.29
Nodes (7): Capabilities, CityLab - Product Overview, Key Features, Project Purpose, Target Users, Use Cases, Value Proposition

### Community 77 - "TwoStageWaterPlant"
Cohesion: 0.20
Nodes (7): main(), Any, RansomwareOtImpactAttack, TestRansomwareAttack, physical/water package, Regla de disparo de protección de planta:         - T1 desborde (>95%) o seco (<, TwoStageWaterPlant

### Community 78 - "Escenario CTF 09: Dosificación Química en Planta de Tratamiento de Agua (SWaT /"
Cohesion: 0.33
Nodes (6): Vector de ataque de sobre-dosificación química sobre PLC de agua., 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 09: Dosificación Química en Planta de Tratamiento de Agua (SWaT / 

### Community 79 - "smoke_test_phase7.sh"
Cohesion: 0.29
Nodes (6): ENABLE_SIS_FEDERATE, HELICS_BROKER_PORT, HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED

### Community 80 - "GridHeatwaveAttributionAttack"
Cohesion: 0.18
Nodes (9): GridHeatwaveAttributionAttack, main(), Any, TestAttributionAttack, 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF (+1 more)

### Community 81 - "HmiRequestHandler"
Cohesion: 0.17
Nodes (8): format_rbac_token(), HmiRequestHandler, Any, BaseHTTPRequestHandler, Consulta series de tiempo históricas directamente a HistorianTSDB en SQLite WAL., Envía una acción de control al SCADA Server con token RBAC., Asegura que el token posea el formato <role>:<token> para compatibilidad STRICT_, Consulta el estado actual del servidor SCADA con cabecera de autenticación RBAC.

### Community 82 - "poc_modbus_test.py"
Cohesion: 0.62
Nodes (6): main(), ModbusTcpClient, Automated integration test for the PoC PLC Modbus interface. Usage (from within…, read_coils(), wait_for_coil(), write_coil()

### Community 83 - "Any"
Cohesion: 0.31
Nodes (6): Any, ConditionChecker, Evalúa oráculos de verificación de estado físico, SCADA, SIEM y red., Evalúa una definición de check y retorna (éxito, mensaje/detalle)., Verifica la evaluación del oráculo de estado físico sobre el Historian TSDB., test_checker_historian_condition()

### Community 84 - "Escenario CTF 14: Escaneo Activo de Subredes OT (Segmentación Nmap)"
Cohesion: 0.33
Nodes (6): Any, 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 14: Escaneo Activo de Subredes OT (Segmentación Nmap)

### Community 85 - "load_scenario_manifest"
Cohesion: 0.26
Nodes (5): BaseHTTPRequestHandler, FlagServiceHandler, load_scenario_manifest(), Carga y parsea el archivo YAML del manifiesto de escenario., Manejador HTTP REST para el servicio de flags y scoring.

### Community 86 - "ThreadedFlagServer"
Cohesion: 0.20
Nodes (8): HistorianTSDB, HTTPServer, Path, Servidor HTTP multihilo para el servicio de flags y scoring., Inicia el demonio de Flag Service., run_flag_service(), ThreadedFlagServer, ThreadingMixIn

### Community 87 - "smoke_test_phase2.sh"
Cohesion: 0.33
Nodes (5): HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase2.sh script

### Community 88 - "smoke_test_phase3.sh"
Cohesion: 0.33
Nodes (5): HELICS_BROKER_PORT, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase3.sh script

### Community 89 - "smoke_test_phase4.sh"
Cohesion: 0.33
Nodes (5): HELICS_BROKER_PORT, HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED

### Community 90 - "Iec61850Server"
Cohesion: 0.19
Nodes (9): Iec61850GooseEncoder, Iec61850Server, Iec61850SvEncoder, is_multicast_addr(), main(), Codificador/Decodificador binario simplificado para PDU GOOSE IEC 61850., Codificador/Decodificador binario para Sampled Values (SV)., Servidor IED Subestación IEC 61850 con emisión GOOSE & SV y recepción de… (+1 more)

### Community 91 - "Dnp3MasterClient"
Cohesion: 0.18
Nodes (9): Dnp3MasterClient, main(), Any, Cliente Master DNP3 ultraligero para consulta y control en Cyber Range., Envía una solicitud DNP3 READ (Group 1 BI & Group 30 AI)., Envía comando CROB Direct Operate / Pulse ON para disparar o cerrar el…, crc16_dnp(), Calcula el CRC-16 especificado por DNP3 (invertido / complemento a unos). (+1 more)

### Community 92 - "Escenario CTF 01: Apagón Urbano en Cascada (THM / HTB Style)"
Cohesion: 0.40
Nodes (5): 1. Breve del Escenario (Storyline), 2. Mapa de Red e IPs Relevantes, 3. Cadena de Ataque (Walkthrough Paso a Paso), 4. Flags del Desafío CTF, Escenario CTF 01: Apagón Urbano en Cascada (THM / HTB Style)

### Community 93 - "run_scenario.py"
Cohesion: 0.27
Nodes (10): main(), Path, Envía una flag para verificación., Consulta y muestra el Scoreboard y métricas., Valida el manifiesto del escenario contra schema.json., Ejecuta los checks del escenario y muestra el estado y las flags obtenidas., run_checks(), show_scorecard() (+2 more)

### Community 94 - "properties"
Cohesion: 0.18
Nodes (11): additionalProperties, required, type, type, properties, minimum, type, check (+3 more)

### Community 95 - "Escenario CTF 08: Insider Threat y Violación de Principio de Mínimo Privilegio R"
Cohesion: 0.40
Nodes (5): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 08: Insider Threat y Violación de Principio de Mínimo Privilegio R

### Community 96 - ".read"
Cohesion: 0.29
Nodes (4): Any, Lee el valor actual de un nodo., Escribe el valor de un nodo. Retorna True si el nodo existe., Retorna snapshot completo del espacio de nodos por sector.

### Community 97 - "build_server"
Cohesion: 0.24
Nodes (6): ModbusTcpServer, ActuatorEmulator, build_server(), ModbusServerContext, Construye las instancias del emulador Modbus sin iniciar el bucle bloqueante., Emula la lógica ST del PLC: TON arranque/parada y detección de fallo.

### Community 98 - "Escenario CTF 13: Reconocimiento Pasivo en Redes OT (Onboarding Pasivo)"
Cohesion: 0.40
Nodes (5): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 13: Reconocimiento Pasivo en Redes OT (Onboarding Pasivo)

### Community 99 - "Escenario CTF 16: Interacción con Trampas Deception (Honeypot OT)"
Cohesion: 0.40
Nodes (5): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 16: Interacción con Trampas Deception (Honeypot OT)

### Community 100 - "NtcipListener"
Cohesion: 0.29
Nodes (3): NtcipListener, Listener NTCIP 1202 de baja fidelidad en el mismo host que el PLC de transporte., TestNtcipListener

### Community 101 - "Escenario CTF 19: Cadena de Pivoteo Guiado Attacker -> DMZ -> OT"
Cohesion: 0.40
Nodes (5): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 19: Cadena de Pivoteo Guiado Attacker -> DMZ -> OT

### Community 102 - "Escenario CTF 20: Comparación de Hardening SCADA API (STRICT_AUTH Toggle)"
Cohesion: 0.40
Nodes (5): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 20: Comparación de Hardening SCADA API (STRICT_AUTH Toggle)

### Community 103 - "main"
Cohesion: 0.33
Nodes (3): main(), Arranca el servidor. Bloqueante — llamar desde un hilo., Punto de entrada standalone del emulador OPC UA.

### Community 104 - "Escenario CTF 26: Capstone Campaña APT Persistente (Sandworm / ELECTRUM Pattern)"
Cohesion: 0.40
Nodes (5): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 26: Capstone Campaña APT Persistente (Sandworm / ELECTRUM Pattern)

### Community 105 - "cmd_down"
Cohesion: 0.07
Nodes (36): cmd_down(), 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Código y Flujo de Trabajo, 🧮 3. Modelo Físico e Interdependencia Ciberfísica, 🗺️ 4. Mapa de Registros Modbus TCP (PLC Agua `10.0.3.10:502`), 📡 5. Interfaz de Co-Simulación HELICS, 💾 6. Presupuesto de Recursos y Memoria RAM, 📘 Federado 01 — Sector Agua SWaT (Tratamiento y Distribución Multi-Etapa) (+28 more)

### Community 106 - "conftest.py"
Cohesion: 0.50
Nodes (3): pytest_sessionfinish(), conftest.py — Pytest session configuration and test isolation., Clean up the temporary historian session directory.

### Community 108 - "Dnp3Server"
Cohesion: 0.43
Nodes (4): Dnp3Server, main(), socket, Servidor TCP Outstation DNP3 para la subestación eléctrica.

### Community 109 - "Escenario CTF 12: Ransomware IT con Parada de Emergencia Operacional OT (Colonia"
Cohesion: 0.40
Nodes (5): 1. Breve del Escenario (Storyline), 2. Cadena de Ataque y Ejecución Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 12: Ransomware IT con Parada de Emergencia Operacional OT (Colonia

### Community 126 - "IEC61850DataSet"
Cohesion: 0.22
Nodes (3): IEC61850DataSet, Hilo receptor de mensajes GOOSE entrantes en la subestación., Dataset IEC 61850 con modelos LNode standard (XCBR, MMXU, CSWI).

### Community 127 - "test_flag_server"
Cohesion: 0.40
Nodes (5): fixture, Inicia un ThreadedFlagServer en un puerto efímero de test., temp_historian(), test_flag_server(), manifest_schema()

### Community 129 - "enum"
Cohesion: 0.22
Nodes (9): enum, type, difficulty, Avanzada, Avanzado, Básico, Capstone, Intermedio (+1 more)

### Community 130 - "items"
Cohesion: 0.22
Nodes (9): type, items, minItems, type, objectives, seed_scope, description, items (+1 more)

### Community 132 - "required"
Cohesion: 0.29
Nodes (7): required, required, check, desc, id, objectives, title

### Community 133 - "properties"
Cohesion: 0.33
Nodes (6): type, properties, category, title, description, type

### Community 134 - "id"
Cohesion: 0.33
Nodes (6): description, pattern, type, id, integer, string

### Community 135 - "schema.json"
Cohesion: 0.40
Nodes (4): additionalProperties, $schema, title, type

### Community 136 - "Escenario CTF 24: Evasión de Reglas de Correlación SIEM (Multi-IP Distributed At"
Cohesion: 0.40
Nodes (5): 1. Breve del Escenario (Storyline), 2. Cadena de Trabajo Paso a Paso, 3. Lección Pedagógica, 4. Flags CTF, Escenario CTF 24: Evasión de Reglas de Correlación SIEM (Multi-IP Distributed At

### Community 141 - "TankPlant"
Cohesion: 0.40
Nodes (3): Advance plant state by dt seconds. Returns new level., Simple rule: if level below 1 m^3 or above 95% capacity, trip., TankPlant

## Knowledge Gaps
- **242 isolated node(s):** `PYTHONPATH`, `validate_e2e.sh script`, `$schema`, `title`, `type` (+237 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistorianTSDB` connect `HistorianTSDB` to `NtpTimeSpoofingAttack`, `IndustrialHmiEngine`, `TestHistorianTSDB`, `._conn`, `HistorianAntiForensicsAttack`, `PostIncidentRecovery`, `HmiRequestHandler`, `TestScadaHistorianHTTPEndpoints`, `🛡️ Arquitectura del Cyber Range CityLab (IEC 62443 / Co-Simulación Ciberfísica)`, `run_scenario.py`, `SCADAAPIHandler`, `test_flag_server`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Why does `金律 — 蓄意之弱點` connect `金律 — 蓄意之弱點` to `SmartLightingSystem`, `.enforce_safety_override`, `IndustrialHmiEngine`, `Objetivo`, `ElectricalSubstationGrid`, `cmd_down`, `rbac.py`, `OpcUaServer`, `🛡️ Arquitectura del Cyber Range CityLab (IEC 62443 / Co-Simulación Ciberfísica)`, `.ingest_zeek_log`, `Especificación de Requisitos de Software (ERS)`, `OtHoneypotServer`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `OpcUaServer` connect `OpcUaServer` to `OtActiveScan`, `Objetivo`, `main`, `金律 — 蓄意之弱點`, `_emulator_harness.py`, `TestOpcUaServerClient`, `TestOpcUaNodeSpace`, `OpcUaClient`, `Iec61850Server`, `socket`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `HistorianTSDB` (e.g. with `HistorianAntiForensicsAttack` and `NtpTimeSpoofingAttack`) actually correct?**
  _`HistorianTSDB` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SiemCorrelationEngine` (e.g. with `HoneypotTouch` and `NtpTimeSpoofingAttack`) actually correct?**
  _`SiemCorrelationEngine` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `OpcUaServer` (e.g. with `TestOpcUaNodeSpace` and `TestOpcUaServerClient`) actually correct?**
  _`OpcUaServer` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `PYTHONPATH`, `validate_e2e.sh script`, `$schema` to the rest of the system?**
  _242 weakly-connected nodes found - possible documentation gaps or missing edges._