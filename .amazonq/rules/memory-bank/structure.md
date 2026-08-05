# CityLab - Project Structure

## Directory Organization

```
CityLab/
├── network/            # Mininet network emulation and firewall rules
│   ├── __init__.py
│   └── topology.py     # Network topology definition and configuration
├── plc/                # PLC control logic and Modbus emulation
│   ├── openplc_config/ # OpenPLC configuration files
│   ├── st_programs/    # Structured Text programs
│   ├── tests/          # Modbus test scripts
│   ├── __init__.py
│   ├── modbus_emulator.py  # Modbus server emulation
│   └── start_openplc.sh    # PLC runtime startup script
├── physical/           # Physical system simulations
│   ├── icssim/         # ICSSIM framework integration
│   │   ├── __init__.py
│   │   └── plant.py    # Base plant simulation class
│   ├── water/          # Water treatment system simulation
│   │   ├── __init__.py
│   │   └── plant_water.py  # Water plant specific logic
│   └── __init__.py
├── helics_sim/         # HELICS federation components
│   ├── __init__.py
│   ├── fed_gridmock.py     # Grid mock federate
│   ├── fed_hospital.py     # Hospital federate
│   ├── fed_icssim.py       # ICSSIM federate
│   ├── fed_logger.py       # Centralized logger federate
│   ├── gridlabd_federate.py # GridLAB-D integration
│   ├── mock_publisher.py   # Mock data publisher
│   ├── smoke_test_local.sh # Local testing script
│   ├── smoke_test_phase2.sh # Phase 2 testing
│   └── start_broker.sh     # HELICS broker startup
├── gridlabd/           # GridLAB-D electrical models
│   ├── substation_normal.glm   # Normal operation model
│   └── substation_tripped.glm  # Tripped/fault state model
├── attacker/           # Attack scripts and tools
│   ├── __init__.py
│   ├── attack_modbus.py       # Basic Modbus attacks
│   ├── attack_multisector.py  # Multi-sector cascading attacks
│   └── exploit_modbus.py      # Modbus exploitation tools
├── docs/               # Project documentation
│   ├── ARCHITECTURE.md    # System architecture and design
│   └── OPERATIONS.md      # Operational procedures and guides
├── logs/               # Runtime logs and output files
├── config/             # Configuration files
└── runfiles/           # Runtime files and temporary data
```

## Core Components

### 1. Network Layer
- **Mininet Topology**: Emulates network segmentation per IEC 62443 standards
- **Firewall Rules**: Implements security zones (Corporate, DMZ, OT Cell)
- **Network Hosts**: h_attacker (10.0.1.10), h_dmz (10.0.2.10), h_plc (10.0.3.10), h_icssim (10.0.3.11)

### 2. Control Systems
- **Modbus Emulator**: Python-based Modbus TCP server for PLC simulation
- **ST Programs**: Structured Text control logic for industrial processes
- **OpenPLC Integration**: Support for OpenPLC runtime configuration

### 3. Physical Simulation
- **ICSSIM Framework**: Industrial Control System simulation platform
- **Water System**: Water treatment plant with tanks, pumps, and valves
- **Multi-Sector Models**: Water, gas, and electrical infrastructure simulations

### 4. Co-Simulation Framework
- **HELICS Federation**: Synchronizes multiple simulation domains
- **GridLAB-D Integration**: Electrical grid simulation and modeling
- **Centralized Logger**: Real-time event logging and monitoring

### 5. Attack Framework
- **Modbus Attacks**: Read/write coil manipulation and protocol exploitation
- **Multi-Sector Attacks**: Coordinated attacks across water, gas, and electrical systems
- **Cascading Failure**: Scripts to trigger cross-sector cascading blackouts

## Architectural Patterns

### Network Segmentation (IEC 62443)
```
[Corporate 10.0.1.0/24] ── Firewall ── [DMZ 10.0.2.0/24] ── Firewall ── [OT Cell 10.0.3.0/24]
       │                                                                          │
  h_attacker (10.0.1.10)                                                   h_plc (10.0.3.10)
                                                                           h_icssim (10.0.3.11)
```

### Co-Simulation Architecture
- **HELICS Broker**: Central coordination point for federates
- **Federates**: Independent simulation components (ICSSIM, GridLAB-D, Logger)
- **Time Synchronization**: Wall-clock time synchronization across simulations
- **Data Exchange**: Publication/subscription model for state sharing

### Component Relationships
1. **Network → Control**: Mininet hosts run PLC emulators and attack scripts
2. **Control → Physical**: Modbus commands control simulated physical processes
3. **Physical → Co-Sim**: ICSSIM publishes state to HELICS federation
4. **Co-Sim → Monitoring**: Logger federate captures events for analysis
5. **Attack → All**: Attack scripts interact with network, control, and physical layers

## File Naming Conventions
- **Python files**: snake_case.py for implementation modules
- **Configuration**: .cfg, .env, .glm extensions
- **Scripts**: run_*.sh for execution scripts, smoke_test_*.sh for testing
- **Logs**: *.log for process logs, *.csv for structured data
- **Documentation**: *.md for markdown documentation files