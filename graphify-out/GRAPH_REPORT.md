# Graph Report - .  (2026-08-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 324 nodes · 467 edges · 43 communities (30 shown, 13 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d5993d7b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Dnp3OutstationState
- fed_icssim.py
- TestDnp3AndAdDcEmulators
- ModbusDpiProxyServer
- exploit_modbus.py
- main
- traffic.py
- Dnp3MasterClient
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
5. `ModbusDpiProxyServer` - 10 edges
6. `Dnp3Server` - 10 edges
7. `LdapServerThread` - 9 edges
8. `KerberosServerThread` - 9 edges
9. `SmbServerThread` - 9 edges
10. `ModbusDpiEngine` - 9 edges

## Surprising Connections (you probably didn't know these)
- `TestDnp3AndAdDcEmulators` --uses--> `LdapServerThread`  [INFERRED]
  plc/tests/test_dnp3_ad.py → network/ad_dc_emulator.py
- `TestDnp3AndAdDcEmulators` --uses--> `KerberosServerThread`  [INFERRED]
  plc/tests/test_dnp3_ad.py → network/ad_dc_emulator.py
- `TestDnp3AndAdDcEmulators` --uses--> `SmbServerThread`  [INFERRED]
  plc/tests/test_dnp3_ad.py → network/ad_dc_emulator.py
- `TestSdnAndDnp3Sa` --uses--> `Dnp3OutstationState`  [INFERRED]
  network/tests/test_sdn_and_dnp3_sa.py → plc/dnp3_emulator.py
- `TestSdnAndDnp3Sa` --uses--> `Dnp3ProtocolHandler`  [INFERRED]
  network/tests/test_sdn_and_dnp3_sa.py → plc/dnp3_emulator.py

## Import Cycles
- None detected.

## Communities (43 total, 13 thin omitted)

### Community 0 - "Dnp3OutstationState"
Cohesion: 0.09
Nodes (19): apply_circuit_breaker(), apply_sdn_flow_rules(), main(), Ejecuta un comando ovs-ofctl de forma segura., Aplica la matriz de microsegmentación OpenFlow en los switches OVS s1..s4., Dispara una regla Circuit Breaker dinámica para aislar un host en caso de DoS/Fl, run_ovs_cmd(), TestSdnAndDnp3Sa (+11 more)

### Community 1 - "fed_icssim.py"
Cohesion: 0.08
Nodes (22): create_federate(), main(), Any, helics_federate, ModbusTcpClient, read_actuator_running(), ElecPlant, GasPlant (+14 more)

### Community 2 - "TestDnp3AndAdDcEmulators"
Cohesion: 0.15
Nodes (11): DomainControllerEmulator, KerberosServerThread, LdapServerThread, main(), socket, Escuchador SMB v2/v3 en puerto 445., Orquestador completo del controlador de dominio h_dc., Escuchador LDAP en puerto 389. (+3 more)

### Community 3 - "ModbusDpiProxyServer"
Cohesion: 0.14
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

### Community 7 - "Dnp3MasterClient"
Cohesion: 0.22
Nodes (8): Dnp3MasterClient, main(), Any, Cliente Master DNP3 ultraligero para consulta y control en Cyber Range., Envía una solicitud DNP3 READ (Group 1 BI & Group 30 AI)., Envía comando CROB Direct Operate / Pulse ON para disparar o cerrar el disyuntor, crc16_dnp(), Calcula el CRC-16 especificado por DNP3 (invertido / complemento a unos).

### Community 8 - "fed_hospital.py"
Cohesion: 0.25
Nodes (9): Enum, helics_federate, helics_input, helics_publication, create_federate(), HospitalPlant, main(), PowerState (+1 more)

### Community 9 - "ActuatorEmulator"
Cohesion: 0.29
Nodes (5): ModbusServerContext, ActuatorEmulator, main(), Emula la lógica ST del PLC: TON arranque/parada y detección de fallo., run_server()

### Community 10 - "scada_server.py"
Cohesion: 0.31
Nodes (6): BaseHTTPRequestHandler, main(), poll_plcs(), Hilo de fondo que consulta periódicamente los PLCs OT e implementa Watchdog Loss, run_http_server(), SCADAAPIHandler

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
Nodes (6): main(), ModbusTcpClient, Automated integration test for the PoC PLC Modbus interface.  Usage (from within, read_coils(), wait_for_coil(), write_coil()

### Community 17 - "smoke_test_phase2.sh"
Cohesion: 0.33
Nodes (5): HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase2.sh script

### Community 18 - "smoke_test_phase3.sh"
Cohesion: 0.33
Nodes (5): HELICS_BROKER_PORT, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase3.sh script

### Community 19 - "attack_multisector.py"
Cohesion: 0.70
Nodes (4): execute_cascading_attack(), force_coil(), main(), read_plc_state()

### Community 22 - "README.md"
Cohesion: 1.00
Nodes (3): README.md, docs/OPERATIONS.md, requirements.txt

## Knowledge Gaps
- **29 isolated node(s):** `smoke_test_local.sh script`, `PYTHONPATH`, `smoke_test_phase2.sh script`, `PYTHONUNBUFFERED`, `PYTHONPATH` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Dnp3Server` connect `Dnp3OutstationState` to `TestDnp3AndAdDcEmulators`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `TestDnp3AndAdDcEmulators` (e.g. with `KerberosServerThread` and `LdapServerThread`) actually correct?**
  _`TestDnp3AndAdDcEmulators` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `smoke_test_local.sh script`, `PYTHONPATH`, `smoke_test_phase2.sh script` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Dnp3OutstationState` be split into smaller, more focused modules?**
  _Cohesion score 0.0931174089068826 - nodes in this community are weakly interconnected._
- **Should `fed_icssim.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0766488413547237 - nodes in this community are weakly interconnected._
- **Should `TestDnp3AndAdDcEmulators` be split into smaller, more focused modules?**
  _Cohesion score 0.14814814814814814 - nodes in this community are weakly interconnected._
- **Should `ModbusDpiProxyServer` be split into smaller, more focused modules?**
  _Cohesion score 0.14492753623188406 - nodes in this community are weakly interconnected._