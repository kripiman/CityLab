# CityLab — Guía de Operaciones (Fase 3 Ciudad Completa)

Instrucciones para desplegar y operar la co-simulación multisectorial de ciudad completa (7 federados).

---

## 1. Ejecución de la Ciudad Completa (Fase 3)

### Modo Interactivo con Mininet + 7 Federados
```bash
sudo ./run_phase3.sh
```

El script desplegará:
- Broker HELICS (7 federados en puerto `23404` / `23500`).
- Simulaciones físicas: Agua SWaT 2 Etapas, Gas, Elec Swing, Transporte/Semáforos.
- Federados de Infraestructura: GridLAB-D 13.8 kV, Hospital UPS, Servidor SCADA Central en DMZ (`10.0.2.20:8080`).
- Observabilidad Centralizada CSV.

---

## 2. Acceso al Servidor SCADA Central (DMZ)

Desde la máquina atacante o salto DMZ:
```bash
curl http://10.0.2.20:8080/api/telemetry
```

---

## 3. Pruebas Automatizadas Locales (Smoke Test 7 Federados)

Para validar la federación de 7 procesos sin Mininet:
```bash
./helics_sim/smoke_test_phase3.sh
```

---

## 4. Escenarios CTF Disponibles

- [Escenario 01: Apagón Urbano en Cascada](file:///home/kripi/Documentos/GitHub/CityLab/docs/scenarios/scenario_01_cascading_blackout.md)
