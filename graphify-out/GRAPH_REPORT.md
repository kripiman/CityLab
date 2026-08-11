# Graph Report - .  (2026-08-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 312 nodes · 462 edges · 33 communities (29 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `46addbb9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- fed_icssim.py
- Dnp3OutstationState
- TestDnp3AndAdDcEmulators
- ModbusDpiEngine
- Dnp3MasterClient
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
- start_broker.sh
- install_deps.sh
- start_openplc.sh

## God Nodes (most connected - your core abstractions)
1. `Dnp3OutstationState` - 12 edges
2. `Dnp3ProtocolHandler` - 12 edges
3. `ModbusDpiEngine` - 10 edges
4. `ModbusDpiProxyServer` - 10 edges
5. `Dnp3MasterClient` - 10 edges
6. `Dnp3Server` - 10 edges
7. `TestDnp3AndAdDcEmulators` - 10 edges
8. `LdapServerThread` - 9 edges
9. `KerberosServerThread` - 9 edges
10. `SmbServerThread` - 9 edges

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

## Communities (33 total, 4 thin omitted)

### Community 0 - "fed_icssim.py"
Cohesion: 0.08
Nodes (22): create_federate(), main(), Any, helics_federate, ModbusTcpClient, read_actuator_running(), ElecPlant, GasPlant (+14 more)

### Community 1 - "Dnp3OutstationState"
Cohesion: 0.11
Nodes (16): apply_circuit_breaker(), apply_sdn_flow_rules(), main(), Ejecuta un comando ovs-ofctl de forma segura., Aplica la matriz de microsegmentación OpenFlow en los switches OVS s3 (OT) y s5, Dispara una regla Circuit Breaker dinámica para aislar un host en caso de DoS/Fl, run_ovs_cmd(), TestSdnAndDnp3Sa (+8 more)

### Community 2 - "TestDnp3AndAdDcEmulators"
Cohesion: 0.14
Nodes (11): DomainControllerEmulator, KerberosServerThread, LdapServerThread, main(), socket, Escuchador SMB v2/v3 en puerto 445., Orquestador completo del controlador de dominio h_dc., Escuchador LDAP en puerto 389. (+3 more)

### Community 3 - "ModbusDpiEngine"
Cohesion: 0.13
Nodes (10): main(), ModbusDpiEngine, ModbusDpiProxyServer, socket, RateLimiter, Proxy TCP transparente/inverso que filtra tráfico Modbus hacia los PLCs., Controlador de tasa de escrituras por IP de origen., Motor de Inspección Profunda de Paquetes (DPI) Modbus/TCP. (+2 more)

### Community 4 - "Dnp3MasterClient"
Cohesion: 0.16
Nodes (12): Dnp3MasterClient, main(), Any, Cliente Master DNP3 ultraligero para consulta y control en Cyber Range., Envía una solicitud DNP3 READ (Group 1 BI & Group 30 AI)., Envía comando CROB Direct Operate / Pulse ON para disparar o cerrar el disyuntor, crc16_dnp(), Dnp3Server (+4 more)

### Community 5 - "exploit_modbus.py"
Cohesion: 0.27
Nodes (17): action_fault(), action_sabotage(), action_start(), action_status(), action_stop(), main(), print_status(), ModbusTcpClient (+9 more)

### Community 6 - "main"
Cohesion: 0.16
Nodes (15): CLI, Mininet, apply_fw_configuration(), configure_host_routes(), CustomCLI, Iec62443Topo, main(), Configure FW host interfaces, IP forwarding and iptables rules.      Assumes int (+7 more)

### Community 7 - "traffic.py"
Cohesion: 0.16
Nodes (12): create_federate(), main(), helics_federate, helics_input, helics_publication, physical/transport package, LightPhase, Enum (+4 more)

### Community 8 - "fed_hospital.py"
Cohesion: 0.25
Nodes (9): create_federate(), HospitalPlant, main(), PowerState, Enum, helics_federate, helics_input, helics_publication (+1 more)

### Community 9 - "ActuatorEmulator"
Cohesion: 0.29
Nodes (5): ModbusServerContext, ActuatorEmulator, main(), Emula la lógica ST del PLC: TON arranque/parada y detección de fallo., run_server()

### Community 10 - "scada_server.py"
Cohesion: 0.31
Nodes (6): BaseHTTPRequestHandler, main(), poll_plcs(), Hilo de fondo que consulta periódicamente los PLCs OT., run_http_server(), SCADAAPIHandler

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

## Knowledge Gaps
- **29 isolated node(s):** `smoke_test_local.sh script`, `PYTHONPATH`, `smoke_test_phase2.sh script`, `PYTHONUNBUFFERED`, `PYTHONPATH` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Dnp3ProtocolHandler` connect `Dnp3OutstationState` to `Dnp3MasterClient`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `Dnp3OutstationState` connect `Dnp3OutstationState` to `Dnp3MasterClient`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `Dnp3Server` connect `Dnp3MasterClient` to `Dnp3OutstationState`, `TestDnp3AndAdDcEmulators`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `smoke_test_local.sh script`, `PYTHONPATH`, `smoke_test_phase2.sh script` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `fed_icssim.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0766488413547237 - nodes in this community are weakly interconnected._
- **Should `Dnp3OutstationState` be split into smaller, more focused modules?**
  _Cohesion score 0.11088709677419355 - nodes in this community are weakly interconnected._
- **Should `TestDnp3AndAdDcEmulators` be split into smaller, more focused modules?**
  _Cohesion score 0.13675213675213677 - nodes in this community are weakly interconnected._