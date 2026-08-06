# CityLab — Guía de Operaciones (Fase 3 Ciudad Completa)

Instrucciones para desplegar, operar e interactuar con el Cyber Range ciberfísico de la ciudad completa (7 federados).

---

## 1. Despliegue de la Ciudad Completa (Fase 3)

### Modo Interactivo con Mininet + 7 Federados
```bash
sudo ./run_phase3.sh
```

El script desplegará:
- **Broker HELICS 3.x**: Orquestación de 7 federados en puerto `23404` / `23500`.
- **Procesos Ciberfísicos**: Agua SWaT 2 Etapas, Gasoducto, Ecuación de Swing Eléctrica, Transporte Semafórico.
- **Federados de Infraestructura**: GridLAB-D 13.8 kV, Hospital Crítico, Servidor SCADA DMZ (`10.0.2.20:8080`), Estación de Ingeniería `h_ews` (`10.0.2.30`).
- **Observabilidad Centralizada**: CSV Logger (`logs/cascading_events.csv`).

---

## 2. Consolas Nativas Interactivas (`lab_terminal.sh`)

Para interactuar con soporte terminal completo PTY (`clear`, `nano`, `vim`, `nmap`, `hydra`, `tshark`, `tmux`):

```bash
# Terminal de Atacante (10.0.1.10)
./lab_terminal.sh attacker

# Terminal Salto DMZ (10.0.2.10)
./lab_terminal.sh dmz

# Terminal Estación de Ingeniería DMZ (10.0.2.30)
./lab_terminal.sh ews

# Terminal Servidor SCADA (10.0.2.20)
./lab_terminal.sh scada

# Dashboard Multi-Panel tmux
./lab_terminal.sh attach
```

---

## 3. Acceso a la API REST SCADA Central (DMZ)

Desde la consola del atacante o salto DMZ:
```bash
curl http://10.0.2.20:8080/api/telemetry
```

---

## 4. Pruebas Automatizadas Locales (Smoke Test 7 Federados)

Para validar la federación de 7 procesos sin Mininet:
```bash
./helics_sim/smoke_test_phase3.sh
```

---

## 5. Escenarios CTF Disponibles

- [Escenario 01: Apagón Urbano en Cascada](scenarios/scenario_01_cascading_blackout.md)
