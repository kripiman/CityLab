<<<<<<< Updated upstream
# Graph Report - .  (2026-08-03)
=======
# Graph Report - .  (2026-08-11)
>>>>>>> Stashed changes

## Corpus Check
- Corpus is ~3,811 words - fits in a single context window. You may not need a graph.

## Summary
<<<<<<< Updated upstream
- 71 nodes · 83 edges · 17 communities (13 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Mininet Network Topology (IEC 62443)
- ICSSIM HELICS Physical Co-simulation
- PLC Modbus Emulator Server
- Modbus Integration Test Scripts
- GridLAB-D HELICS Federate
- Project Documentation & Requirements
- HELICS Broker Startup
- Dependency Installer Script
- Phase 1 Entry Runner
- OpenPLC Startup Script

## God Nodes (most connected - your core abstractions)
1. `PumpEmulator` - 7 edges
2. `main()` - 6 edges
3. `main()` - 5 edges
4. `Iec62443Topo` - 5 edges
5. `TankPlant` - 5 edges
6. `main()` - 5 edges
7. `main()` - 4 edges
8. `apply_fw_configuration()` - 4 edges
9. `configure_host_routes()` - 4 edges
10. `run_connectivity_tests()` - 4 edges
=======
- 326 nodes · 470 edges · 42 communities (29 shown, 13 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2756f34c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Dnp3MasterClient
- Dnp3OutstationState
- fed_icssim.py
- ModbusDpiEngine
- exploit_modbus.py
- main
- traffic.py
- fed_hospital.py
- ActuatorEmulator
- scada_server.py
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
- lab_terminal.sh
- README.md
- start_broker.sh
- install_deps.sh
- start_openplc.sh
- helics_federate
- ModbusTcpClient
- helics_federate
- Enum
- helics_federate
- helics_input
- helics_publication
- socket

## God Nodes (most connected - your core abstractions)
1. `Dnp3OutstationState` - 12 edges
2. `Dnp3ProtocolHandler` - 12 edges
3. `Dnp3MasterClient` - 10 edges
4. `TestDnp3AndAdDcEmulators` - 10 edges
5. `Dnp3Server` - 10 edges
6. `ModbusDpiEngine` - 10 edges
7. `ModbusDpiProxyServer` - 10 edges
8. `LdapServerThread` - 9 edges
9. `KerberosServerThread` - 9 edges
10. `SmbServerThread` - 9 edges
>>>>>>> Stashed changes

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `TankPlant`  [EXTRACTED]
  helics/fed_icssim.py → physical/icssim/plant.py

## Import Cycles
- None detected.

<<<<<<< Updated upstream
## Communities (17 total, 4 thin omitted)

### Community 0 - "Mininet Network Topology (IEC 62443)"
Cohesion: 0.21
Nodes (12): Mininet, apply_fw_configuration(), configure_host_routes(), Iec62443Topo, main(), Set default routes on hosts to point to the FW gateway in each zone., Run minimal connectivity checks and return statuses.      Tests:     - Attacker, Custom Mininet topology implementing segmented zones and a routing FW host. (+4 more)

### Community 1 - "ICSSIM HELICS Physical Co-simulation"
Cohesion: 0.22
Nodes (9): create_federate(), main(), helics_federate, ModbusTcpClient, read_pump_running(), ICSSIM-like plant model for PoC: simple tank and pump.  This module implements a, Advance plant state by dt seconds. Returns new level., Simple rule: if level below 1 m^3 or above 95% capacity, trip. (+1 more)

### Community 2 - "PLC Modbus Emulator Server"
=======
## Communities (42 total, 13 thin omitted)

### Community 0 - "Dnp3MasterClient"
Cohesion: 0.09
Nodes (19): DomainControllerEmulator, KerberosServerThread, LdapServerThread, main(), socket, Escuchador SMB v2/v3 en puerto 445., Orquestador completo del controlador de dominio h_dc., Escuchador LDAP en puerto 389. (+11 more)

### Community 1 - "Dnp3OutstationState"
Cohesion: 0.09
Nodes (19): apply_circuit_breaker(), apply_sdn_flow_rules(), main(), Ejecuta un comando ovs-ofctl de forma segura., Aplica la matriz de microsegmentación OpenFlow en los switches OVS s3 (OT) y s5, Dispara una regla Circuit Breaker dinámica para aislar un host en caso de DoS/Fl, run_ovs_cmd(), TestSdnAndDnp3Sa (+11 more)

### Community 2 - "fed_icssim.py"
Cohesion: 0.08
Nodes (22): create_federate(), main(), Any, helics_federate, ModbusTcpClient, read_actuator_running(), ElecPlant, GasPlant (+14 more)

### Community 3 - "ModbusDpiEngine"
Cohesion: 0.13
Nodes (10): main(), ModbusDpiEngine, ModbusDpiProxyServer, RateLimiter, Proxy TCP transparente/inverso que filtra tráfico Modbus hacia los PLCs., Controlador de tasa de escrituras por IP de origen., Motor de Inspección Profunda de Paquetes (DPI) Modbus/TCP., Inspecciona la trama Modbus/TCP en Capa 7.                  Header Modbus TCP (M (+2 more)

### Community 4 - "exploit_modbus.py"
Cohesion: 0.27
Nodes (17): action_fault(), action_sabotage(), action_start(), action_status(), action_stop(), main(), print_status(), ModbusTcpClient (+9 more)

### Community 5 - "main"
Cohesion: 0.16
Nodes (15): CLI, Mininet, apply_fw_configuration(), configure_host_routes(), CustomCLI, Iec62443Topo, main(), Configure FW host interfaces, IP forwarding and iptables rules.      Assumes int (+7 more)

### Community 6 - "traffic.py"
Cohesion: 0.16
Nodes (12): create_federate(), main(), helics_federate, helics_input, helics_publication, physical/transport package, LightPhase, Enum (+4 more)

### Community 7 - "fed_hospital.py"
Cohesion: 0.25
Nodes (9): Enum, helics_federate, helics_input, helics_publication, create_federate(), HospitalPlant, main(), PowerState (+1 more)

### Community 8 - "ActuatorEmulator"
Cohesion: 0.29
Nodes (5): ModbusServerContext, ActuatorEmulator, main(), Emula la lógica ST del PLC: TON arranque/parada y detección de fallo., run_server()

### Community 9 - "scada_server.py"
Cohesion: 0.31
Nodes (6): BaseHTTPRequestHandler, main(), poll_plcs(), Hilo de fondo que consulta periódicamente los PLCs OT e implementa Watchdog Loss, run_http_server(), SCADAAPIHandler

### Community 10 - "create_federate"
>>>>>>> Stashed changes
Cohesion: 0.36
Nodes (3): ModbusServerContext, PumpEmulator, run_server()

<<<<<<< Updated upstream
### Community 3 - "Modbus Integration Test Scripts"
Cohesion: 0.62
Nodes (6): main(), ModbusTcpClient, Automated integration test for the PoC PLC Modbus interface.  Usage (from within, read_coils(), wait_for_coil(), write_coil()

### Community 4 - "GridLAB-D HELICS Federate"
Cohesion: 0.53
Nodes (5): create_federate(), main(), helics_federate, start_gridlabd(), stop_gridlabd()

### Community 5 - "Project Documentation & Requirements"
=======
### Community 11 - "run_phase1.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase1.sh script

### Community 12 - "run_phase2.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase2.sh script

### Community 13 - "run_phase3.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase3.sh script

### Community 14 - "attack_modbus.py"
Cohesion: 0.71
Nodes (6): connect(), do_fault(), do_start_stop_blast(), main(), ModbusTcpClient, write_coil()

### Community 15 - "poc_modbus_test.py"
Cohesion: 0.62
Nodes (6): main(), ModbusTcpClient, Automated integration test for the PoC PLC Modbus interface.  Usage (from within, read_coils(), wait_for_coil(), write_coil()

### Community 16 - "smoke_test_phase2.sh"
Cohesion: 0.33
Nodes (5): HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase2.sh script

### Community 17 - "smoke_test_phase3.sh"
Cohesion: 0.33
Nodes (5): HELICS_BROKER_PORT, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase3.sh script

### Community 18 - "attack_multisector.py"
Cohesion: 0.70
Nodes (4): execute_cascading_attack(), force_coil(), main(), read_plc_state()

### Community 21 - "README.md"
>>>>>>> Stashed changes
Cohesion: 1.00
Nodes (3): README.md, docs/OPERATIONS.md, requirements.txt

## Knowledge Gaps
- **2 isolated node(s):** `start_broker.sh script`, `start_openplc.sh script`
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

<<<<<<< Updated upstream
- **What connects `start_broker.sh script`, `start_openplc.sh script` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
=======
- **Why does `Dnp3Server` connect `Dnp3OutstationState` to `Dnp3MasterClient`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `TestDnp3AndAdDcEmulators` (e.g. with `KerberosServerThread` and `LdapServerThread`) actually correct?**
  _`TestDnp3AndAdDcEmulators` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `smoke_test_local.sh script`, `PYTHONPATH`, `smoke_test_phase2.sh script` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Dnp3MasterClient` be split into smaller, more focused modules?**
  _Cohesion score 0.09268292682926829 - nodes in this community are weakly interconnected._
- **Should `Dnp3OutstationState` be split into smaller, more focused modules?**
  _Cohesion score 0.0931174089068826 - nodes in this community are weakly interconnected._
- **Should `fed_icssim.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0766488413547237 - nodes in this community are weakly interconnected._
- **Should `ModbusDpiEngine` be split into smaller, more focused modules?**
  _Cohesion score 0.13230769230769232 - nodes in this community are weakly interconnected._
>>>>>>> Stashed changes
