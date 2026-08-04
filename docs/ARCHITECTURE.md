# Arquitectura del Cyber Range (Fase 1)

## Contexto del Proyecto

Cyber Range 100% software para simular incidentes cibernéticos en infraestructura crítica (ICS/SCADA).
- **Entorno**: Ejecución nativa en Linux sin máquinas virtuales pesadas.
- **Eficiencia**: Bajo consumo de memoria RAM (<1 GB en total).

---

## Segmentación de Red (IEC 62443)

Topología emulada por Mininet con tres zonas aisladas mediante un firewall (`iptables`):

```mermaid
graph TD
    subgraph CorpZone ["1. Corporate (10.0.1.0/24)"]
        h_attacker["h_attacker (10.0.1.10)"]
    end

    subgraph DmzZone ["2. DMZ (10.0.2.0/24)"]
        h_dmz["h_dmz (10.0.2.10)"]
    end

    subgraph OtZone ["3. OT Cell (10.0.3.0/24)"]
        h_plc["h_plc (10.0.3.10)"]
        h_icssim["h_icssim (10.0.3.11)"]
    end

    fw["Firewall (fw)"]

    h_attacker <--> fw-eth0
    h_dmz <--> fw-eth1
    h_plc <--> fw-eth2
    h_icssim <--> fw-eth2

    classDef zone fill:#2a2a2a,stroke:#444,stroke-width:2px;
    class CorpZone,DmzZone,OtZone zone;
```

### Reglas de Acceso (Firewall)
- **Corporate -> OT**: DENEGADO (Bloqueo total).
- **DMZ -> OT**: PERMITIDO tráfico Modbus/TCP (puerto `502`) hacia el PLC (`10.0.3.10`).

---

## Cadena de Ataque y Co-Simulación (End-to-End)

El flujo de control ciberfísico está orquestado por HELICS 3.x y sincronizado en tiempo real (1 paso de simulación = 1 segundo real):

```mermaid
sequenceDiagram
    autonumber
    actor Atacante as h_dmz (Ataque)
    participant PLC as h_plc (OpenPLC)
    participant ICSSIM as fed_icssim (Física)
    participant Broker as HELICS Broker
    participant Grid as gridlabd_federate (Eléctrica)

    Note over Atacante, Grid: Estado Normal: Bomba OFF, Nivel Tanque baja (fuga)
    Atacante->>PLC: Modbus Write Coil 0 = True (Forzar arranque bomba)
    Note over PLC: safety delay (TON 5s)
    PLC->>PLC: Transición a RUNNING (Coil 2 = True)
    
    loop Co-Simulación (1s / paso)
        ICSSIM->>PLC: Leer Coil 2 (Estado Bomba)
        PLC-->>ICSSIM: Retorna pump_running = True
        Note over ICSSIM: Avanzar nivel tanque (inflow +1.0 m3/s)
        ICSSIM->>Broker: Publicar tank/level (nivel actual)
        ICSSIM->>Broker: Publicar breaker/trip (0 = normal, 1 = trip)
        Broker->>Grid: Propagar datos publicados
        Note over ICSSIM: Si nivel > 19.0 m3, cambiar trip = 1
    end

    Note over Grid: Nivel supera 95% capacidad (trip = 1)
    Grid->>Grid: Parar Normal GLM
    Grid->>Grid: Iniciar Tripped GLM (Disparar disyuntor subestación)
```

---

## Lógica Física y de Control

### 1. Lógica del PLC
- **IEC 61131-3 (Structured Text)**:
  - Entrada: `pump_start` (Coil 0), `pump_stop` (Coil 1).
  - Salida: `pump_running` (Coil 2), `pump_fault` (Coil 3).
  - Control de seguridad: Si `pump_start` y `pump_stop` activos a la vez, activa `pump_fault` y detiene bomba.

### 2. Modelo Físico (Bomba y Tanque)
- **Capacidad Tanque**: 20.0 m³
- **Nivel Inicial**: 10.0 m³
- **Tasa de Llenado**: 1.0 m³/s (bomba encendida)
- **Tasa de Fuga**: 0.001 m³/s (bomba apagada)
- **Criterio de Disparo (Trip)**:
  - Nivel crítico superior: > 19.0 m³ (95% capacidad).
  - Nivel crítico inferior: < 1.0 m³.

---

## Simplificaciones de Diseño (Ponytail Notes)

- **OpenPLC Fallback**:
  <!-- ponytail: OpenPLC Fallback (Ceiling: No corre Structured Text nativo. Upgrade: Compilar e integrar OpenPLC completo en h_plc) -->
  Si OpenPLC no está en el host, se levanta el emulador Python (`modbus_emulator.py`) emulando bobinas y retardos en el puerto `502`.
- **Uso de pymodbus en lugar de scapy**:
  `pymodbus` ofrece una abstracción limpia del protocolo sin necesidad de generar y calcular checksums IP/TCP de forma manual.
