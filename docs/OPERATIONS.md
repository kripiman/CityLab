# CityLab — Guía de Operaciones (Fase 3 Ciudad Completa)

Instrucciones para desplegar y operar la co-simulación multisectorial de ciudad completa (7 federados).

---

## 1. Ejecución de la Ciudad Completa (Fase 3)

`./citylab.sh` es el punto de entrada único. Los `run_phase*.sh` son implementación interna a la que delega `up`; no los invoques directamente.

### Modo Interactivo con Mininet + 7 Federados
```bash
sudo ./citylab.sh up            # Fase 3 por defecto (equivale a --phase 3)
sudo ./citylab.sh up --phase 1  # Nodo mínimo viable
sudo ./citylab.sh up --phase 2  # Co-simulación multisectorial
```

Desplegará:
- Broker HELICS (7 federados en puerto `23404` / `23500`).
- Simulaciones físicas: Agua SWaT 2 Etapas, Gas, Elec Swing, Transporte/Semáforos.
- Federados de Infraestructura: GridLAB-D 13.8 kV, Hospital UPS, Servidor SCADA Central en DMZ (`10.0.2.20:8080`).
- Observabilidad Centralizada CSV.

Detener y limpiar (federados/emuladores/servicios + `mn -c`):
```bash
sudo ./citylab.sh down
```

---

## 2. Acceso al Servidor SCADA Central (DMZ)

Desde la máquina atacante o salto DMZ:
```bash
curl http://10.0.2.20:8080/api/telemetry
```

---

## 3. Pruebas Automatizadas Locales (Smoke Test sin Mininet)

Co-simulación HELICS sin root. `smoke` usa fase 7 por defecto (10 federados, incluye SIS SIL-3):
```bash
./citylab.sh smoke              # fase 7 (10 federados)
./citylab.sh smoke --phase 4    # fase 4 (9 federados)
```

Suite de pruebas unitarias y medición de recursos:
```bash
./citylab.sh test               # 151 tests
./citylab.sh profile            # RSS/CPU medidos -> logs/resource_profile_summary.txt
```

---

## 4. Escenarios CTF Disponibles

- [Escenario 01: Apagón Urbano en Cascada](scenarios/scenario_01_cascading_blackout.md)
