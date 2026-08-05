# CityLab - Development Guidelines

## Code Quality Standards Analysis

### 1. Python Code Formatting (5/5 files follow these patterns)
- **Shebang**: All executable Python scripts start with `#!/usr/bin/env python3`
- **Module Docstrings**: Comprehensive triple-quoted docstrings with usage examples
- **Type Hints**: Extensive use of Python type annotations (`from __future__ import annotations`)
- **Imports**: Standard library imports first, then third-party, then local modules
- **Line Length**: Generally 80-100 characters, with logical breaks
- **Indentation**: 4 spaces (no tabs)

### 2. Naming Conventions
- **Variables**: snake_case for all variables and function names
- **Constants**: UPPER_SNAKE_CASE for module-level constants
- **Classes**: PascalCase for class definitions
- **Private Members**: Leading underscore for private methods/variables
- **Acronyms**: Treated as words (ModbusTCP, not MODBUSTCP)

### 3. Documentation Standards
- **Module-level**: Purpose, usage, and architecture overview
- **Function-level**: Parameters, returns, and behavior description
- **Class-level**: Responsibilities and usage patterns
- **Inline Comments**: Explain complex logic, not obvious operations

## Structural Conventions

### 1. Project Organization Patterns
- **Component Separation**: Clear separation of network, physical, control, and attack layers
- **Configuration Management**: Environment variables and .env files for runtime configuration
- **Logging Strategy**: Centralized logs directory with structured naming
- **Test Organization**: Smoke tests in helics_sim/, unit tests in component tests/ directories

### 2. File Structure Patterns
- **Entry Points**: run_phase*.sh scripts as main execution entry points
- **Component Modules**: Each directory has __init__.py for Python package structure
- **Configuration Files**: .glm for GridLAB-D, .cfg for OpenPLC, .env for environment
- **Documentation**: README.md and docs/ directory for user-facing documentation

### 3. Error Handling Patterns
- **Graceful Degradation**: Fallback mechanisms (e.g., modbus_emulator as PLC fallback)
- **Resource Cleanup**: try/finally blocks for process termination and resource release
- **Logging Levels**: Appropriate use of INFO, WARNING, ERROR, DEBUG levels
- **User Feedback**: Clear error messages with actionable guidance

## Textual Standards

### 1. Language and Terminology
- **English Primary**: Code and comments in English, documentation in Spanish/English
- **ICS Terminology**: Consistent use of industrial control system terms (coils, trips, federates)
- **Network Terminology**: Standard networking terms (subnet, gateway, firewall rules)
- **Simulation Terms**: Co-simulation, federates, time synchronization

### 2. Comment Style
- **Purpose Comments**: Explain "why" not "what"
- **TODO/FIXME**: Used sparingly with clear context
- **Section Headers**: Visual separation with comment blocks
- **Parameter Documentation**: Type and purpose in function docstrings

## Practices Followed Throughout Codebase

### 1. Security Practices (5/5 files exhibit)
- **Network Segmentation**: IEC 62443 compliance in network topology
- **Input Validation**: Command-line argument validation with argparse
- **Resource Isolation**: Mininet network namespaces for process isolation
- **Least Privilege**: Root privileges only where absolutely necessary

### 2. Simulation Practices
- **Time Management**: Wall-clock time synchronization across federates
- **State Management**: Clear separation of simulation state from control logic
- **Event Logging**: Structured CSV logging for analysis and replay
- **Resource Cleanup**: Proper termination of simulation processes

### 3. Development Practices
- **Environment Awareness**: PYTHONPATH configuration for module imports
- **Cross-Platform**: Linux-focused but with portability considerations
- **Dependency Management**: Clear separation of system vs Python dependencies
- **Version Control**: .gitignore for logs, temporary files, and build artifacts

## Semantic Patterns Overview

### 1. Recurring Implementation Patterns

#### Network Configuration Pattern (topology.py)
```python
# Firewall rule application pattern
def apply_fw_configuration(fw: Node) -> None:
    fw.cmd('ip addr add 10.0.1.1/24 dev fw-eth0')
    fw.cmd('sysctl -w net.ipv4.ip_forward=1')
    fw.cmd('iptables -P FORWARD DROP')  # Default deny
    # Allow specific rules
    fw.cmd('iptables -A FORWARD -i fw-eth1 -o fw-eth2 -p tcp --dport 502 -j ACCEPT')
```

#### Physical Simulation Pattern (plant_water.py)
```python
# Dataclass-based state management
@dataclass
class TwoStageWaterPlant:
    t1_level_m3: float = 10.0
    t1_capacity_m3: float = 20.0
    
    def step(self, p1_cmd: bool, p2_cmd: bool, power_available: bool = True, dt: float = 1.0):
        # Physics simulation with clamping
        p1_active = p1_cmd and power_available
        self.t1_level_m3 = max(0.0, min(self.t1_capacity_m3, self.t1_level_m3))
```

#### HELICS Federation Pattern (gridlabd_federate.py)
```python
# Standard HELICS federate setup
def create_federate() -> tuple[h.helics_federate, list[h.helics_input], h.helics_publication]:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, 'zmq')
    h.helicsFederateInfoSetCoreInitString(fi, '--federates=1 --broker_address=127.0.0.1')
    fed = h.helicsCreateValueFederate(FED_NAME, fi)
    sub = h.helicsFederateRegisterSubscription(fed, 'breaker/trip', '')
    pub = h.helicsFederateRegisterGlobalPublication(fed, 'grid/voltage_pu', h.HELICS_DATA_TYPE_DOUBLE, '')
    h.helicsFederateEnterExecutingMode(fed)
```

#### Modbus Interaction Pattern (attack_multisector.py)
```python
# Consistent Modbus client usage
def read_plc_state(host: str, port: int = 502) -> Tuple[int, ...]:
    client = ModbusTcpClient(host, port=port, timeout=2.0)
    connected = client.connect()
    if not connected:
        raise ConnectionError(f"Cannot connect to Modbus server at {host}:{port}")
    try:
        rr = client.read_coils(0, 4)
        return tuple(int(b) for b in rr.bits[:4])
    finally:
        client.close()
```

### 2. Common Architectural Approaches

#### Layered Architecture
1. **Network Layer**: Mininet topology and firewall rules
2. **Control Layer**: Modbus PLC emulation and ST logic
3. **Physical Layer**: ICSSIM-based process simulation
4. **Co-Simulation Layer**: HELICS federation and time synchronization
5. **Attack Layer**: Penetration testing tools and scripts

#### Publisher-Subscriber Pattern
- **HELICS Topics**: Structured topic naming (sector/parameter)
- **Data Flow**: ICSSIM publishes → Logger subscribes → GridLAB-D reacts
- **Event Propagation**: Trip signals propagate across federates

#### Configuration-Driven Execution
- **Environment Variables**: Control behavior without code changes
- **Command-line Arguments**: Flexible script execution
- **Configuration Files**: .env, .glm, .cfg for domain-specific settings

### 3. Frequent Design Patterns

#### Factory Pattern
```python
# Plant type-based configuration
_PLANT_TIMINGS = {
    'water': (5.0, 3.0),
    'gas':   (8.0, 5.0),
    'elec':  (2.0, 1.0),
}
```

#### Strategy Pattern
```python
# Attack mode selection
if mode == 'fault':
    force_coil(ip, 0, True)
    force_coil(ip, 1, True)
elif mode == 'start':
    force_coil(ip, 0, True)
    force_coil(ip, 1, False)
```

#### Observer Pattern
```python
# Event monitoring and reaction
trips = [h.helicsInputGetInteger(sub) for sub in sub_trips]
trip = any(t != 0 for t in trips)
if trip and not current_tripped:
    # React to state change
```

### 4. Proper Internal API Usage

#### Mininet API Usage
```python
# Standard Mininet host configuration
h_attacker = net.get('h_attacker')
h_attacker.cmd('ip route add default via 10.0.1.1')
```

#### HELICS API Usage
```python
# Correct HELICS lifecycle management
h.helicsFederateEnterExecutingMode(fed)
current_time = h.helicsFederateRequestTime(fed, requested_time)
h.helicsFederateFinalize(fed)
```

#### Modbus API Usage
```python
# Proper Modbus client resource management
client = ModbusTcpClient(host, port=port, timeout=2.0)
try:
    rr = client.read_coils(0, 4)
finally:
    client.close()
```

### 5. Frequently Used Code Idioms

#### Safe Process Management
```python
# Process startup and cleanup
proc = subprocess.Popen(cmd, stdout=logf, stderr=logf, preexec_fn=os.setsid)
try:
    # ... use process
finally:
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    logf.close()
```

#### Environment Configuration
```python
# Flexible configuration with defaults
FED_NAME = os.environ.get('HELICS_FED_NAME', 'GRIDLABD_fed')
BROKER_PORT = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
```

#### Command-line Interface
```python
# Consistent argparse usage
parser = argparse.ArgumentParser(description='Component description')
parser.add_argument('--sector', choices=['water', 'gas', 'elec', 'all'], default='all')
parser.add_argument('--mode', choices=['start', 'stop', 'fault'], default='fault')
args = parser.parse_args()
```

### 6. Popular Annotations and Decorators

#### Type Annotations
```python
from __future__ import annotations
from typing import Dict, Tuple, List

def read_plc_state(host: str, port: int = 502) -> Tuple[int, ...]:
```

#### Dataclasses
```python
from dataclasses import dataclass

@dataclass
class TwoStageWaterPlant:
    t1_level_m3: float = 10.0
    t1_capacity_m3: float = 20.0
```

#### Logging Configuration
```python
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s] %(message)s')
LOGGER = logging.getLogger('component_name')
```

## Development Workflow Guidelines

### 1. New Component Development
1. **Define Purpose**: Clear single responsibility for each component
2. **Follow Patterns**: Use established patterns from similar components
3. **Add Documentation**: Comprehensive docstrings and usage examples
4. **Include Tests**: Smoke tests for integration, unit tests for logic
5. **Update Configuration**: Add necessary environment variables and dependencies

### 2. Modification Guidelines
1. **Maintain Compatibility**: Don't break existing interfaces without migration path
2. **Update Documentation**: Keep docstrings and README current
3. **Test Changes**: Run smoke tests before and after modifications
4. **Consider Dependencies**: Understand impact on other components

### 3. Testing Strategy
1. **Unit Tests**: Test individual functions and classes in isolation
2. **Integration Tests**: Test component interactions within directories
3. **Smoke Tests**: End-to-end validation of complete scenarios
4. **Attack Testing**: Validate attack scripts against emulated systems

### 4. Code Review Checklist
- [ ] Follows established naming conventions
- [ ] Includes comprehensive documentation
- [ ] Proper error handling and resource cleanup
- [ ] Appropriate logging levels and messages
- [ ] Security considerations addressed
- [ ] Performance implications considered
- [ ] Cross-component dependencies documented
- [ ] Environment configuration updated if needed