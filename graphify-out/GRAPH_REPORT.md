# Graph Report - .  (2026-08-03)

## Corpus Check
- Corpus is ~3,811 words - fits in a single context window. You may not need a graph.

## Summary
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

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `TankPlant`  [EXTRACTED]
  helics/fed_icssim.py → physical/icssim/plant.py

## Import Cycles
- None detected.

## Communities (17 total, 4 thin omitted)

### Community 0 - "Mininet Network Topology (IEC 62443)"
Cohesion: 0.21
Nodes (12): Mininet, apply_fw_configuration(), configure_host_routes(), Iec62443Topo, main(), Set default routes on hosts to point to the FW gateway in each zone., Run minimal connectivity checks and return statuses.      Tests:     - Attacker, Custom Mininet topology implementing segmented zones and a routing FW host. (+4 more)

### Community 1 - "ICSSIM HELICS Physical Co-simulation"
Cohesion: 0.22
Nodes (9): create_federate(), main(), helics_federate, ModbusTcpClient, read_pump_running(), ICSSIM-like plant model for PoC: simple tank and pump.  This module implements a, Advance plant state by dt seconds. Returns new level., Simple rule: if level below 1 m^3 or above 95% capacity, trip. (+1 more)

### Community 2 - "PLC Modbus Emulator Server"
Cohesion: 0.36
Nodes (3): ModbusServerContext, PumpEmulator, run_server()

### Community 3 - "Modbus Integration Test Scripts"
Cohesion: 0.62
Nodes (6): main(), ModbusTcpClient, Automated integration test for the PoC PLC Modbus interface.  Usage (from within, read_coils(), wait_for_coil(), write_coil()

### Community 4 - "GridLAB-D HELICS Federate"
Cohesion: 0.53
Nodes (5): create_federate(), main(), helics_federate, start_gridlabd(), stop_gridlabd()

### Community 5 - "Project Documentation & Requirements"
Cohesion: 1.00
Nodes (3): README.md, docs/OPERATIONS.md, requirements.txt

## Knowledge Gaps
- **2 isolated node(s):** `start_broker.sh script`, `start_openplc.sh script`
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `start_broker.sh script`, `start_openplc.sh script` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._