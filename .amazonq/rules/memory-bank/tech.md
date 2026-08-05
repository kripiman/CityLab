# CityLab - Technology Stack

## Programming Languages and Versions

### Primary Languages
- **Python 3**: Main implementation language for simulations, attacks, and orchestration
- **Bash**: System scripts and automation (run_phase1.sh, run_phase2.sh)
- **Structured Text (ST)**: PLC control logic programming (poc_pump.st)

### Domain-Specific Languages
- **GridLAB-D GLM**: Electrical system modeling language (.glm files)
- **Modbus Protocol**: Industrial communication protocol for PLC control

## Core Dependencies

### System Dependencies
```bash
# Network Emulation
mininet          # Network virtualization and emulation
openvswitch      # Virtual switch implementation

# Electrical Simulation
gridlabd         # Electrical distribution system simulator

# PLC Runtime
openplc          # Open-source PLC runtime (optional)
```

### Python Dependencies (requirements.txt)
```python
# Network/Emulation
# Mininet installed via system package manager

# PLC/Modbus
pymodbus==2.5.3  # Modbus protocol implementation

# Simulation Orchestration
helics==3.4.0    # Co-simulation framework

# Attack/Offensive
scapy==2.6.1     # Packet manipulation and network attacks

# Utilities
python-dotenv==1.0.0  # Environment variable management
```

### Specialized Frameworks
- **ICSSIM**: Industrial Control System simulation framework (installed from source)
- **HELICS**: Hierarchical Engine for Large-scale Infrastructure Co-Simulation
- **GridLAB-D**: Electrical distribution system simulation and analysis

## Build Systems and Development Tools

### No Traditional Build System
- **Direct Execution**: Python scripts run directly with python3
- **Shell Script Orchestration**: Bash scripts coordinate system components
- **Environment Management**: .env files for configuration

### Development Commands

#### System Setup
```bash
# Install system dependencies
sudo ./install_deps.sh

# Install Python dependencies
pip install -r requirements.txt

# Start Open vSwitch
sudo systemctl start openvswitch-switch
```

#### Simulation Execution
```bash
# Phase 1: Minimum Viable Node
sudo ./run_phase1.sh

# Phase 2: Multi-Sector Co-Simulation
sudo ./run_phase2.sh

# Headless/Detached Mode
sudo MININET_DETACH=1 ./run_phase2.sh
```

#### Testing and Validation
```bash
# Local smoke test (no Mininet)
./helics_sim/smoke_test_phase2.sh

# Clean previous state
mn -c  # Mininet cleanup
```

#### Attack Execution
```bash
# From Mininet CLI
mininet> h_dmz bash
python3 attacker/attack_multisector.py --sector water --mode start
python3 attacker/attack_multisector.py --sector all --mode fault
```

## Runtime Environment

### Environment Variables
- **PYTHONUNBUFFERED=1**: Real-time log output
- **PYTHONPATH**: Set to repository root for module imports
- **HELICS_FED_COUNT**: Number of HELICS federates
- **MININET_DETACH**: Run Mininet in detached mode (0=interactive, 1=detached)
- **AUTO_START_PLC**: Auto-start PLC runtime in Mininet host

### Logging Configuration
- **Centralized Logs**: logs/ directory for all runtime output
- **CSV Event Logs**: logs/cascading_events.csv for structured event data
- **Process Logs**: Individual .log files for each component
- **Real-time Monitoring**: tail -f logs/cascading_events.csv

## Development Workflow

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd CityLab

# Install dependencies
sudo ./install_deps.sh
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env as needed
```

### 2. Development Testing
```bash
# Test individual components
python3 plc/modbus_emulator.py
python3 helics_sim/fed_icssim.py
python3 network/topology.py

# Run smoke tests
./helics_sim/smoke_test_local.sh
```

### 3. Integration Testing
```bash
# Full system test (requires sudo)
sudo ./run_phase1.sh

# Multi-sector test
sudo ./run_phase2.sh
```

### 4. Attack Development
```bash
# Test attack scripts
python3 attacker/attack_modbus.py --help
python3 attacker/attack_multisector.py --sector water --mode scan
```

## Platform Requirements

### Operating System
- **Primary**: Linux (Debian/Ubuntu, Fedora/Nobara, Arch)
- **Required**: Root/sudo privileges for network emulation
- **Recommended**: 4+ GB RAM, 2+ CPU cores

### Network Configuration
- **No Internet Required**: All simulations run locally
- **Network Namespaces**: Mininet creates isolated network environments
- **Port Usage**: Modbus TCP (502), HELICS broker ports

### Performance Considerations
- **RAM**: <1 GB typical consumption
- **CPU**: Moderate usage during co-simulation
- **Disk**: Minimal storage requirements (~100MB for code and logs)