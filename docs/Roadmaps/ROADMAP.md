# 🗺️ CityLab Cyber Range — Roadmap de Fidelidad e Implementación

> **Estado**: **Fases 0 a 9 COMPLETADAS (100% Roadmap Realizado)**  
> **Fecha de Actualización**: Agosto 2026  
> **Baseline Verificado**: **145 PASS** (`PYTHONPATH=. python3 -m unittest discover -s network/tests && ...`)  
> **Presupuesto RAM**: $\le 6\text{ GB}$ (10 federados HELICS nativos + Mininet + AD DC + SDN).  

---

## 📌 1. Estado de Arquitectura y Baseline Real (Fase 0)

El Cyber Range CityLab emula infraestructuras críticas urbanas convergentes IT/OT mediante co-simulación distribuida (HELICS 3.x) y redes SDN (Mininet / OpenFlow / `iptables`).

### Componentes en Vivo (7 Federados HELICS):
1. `fed_icssim.py` (Agua SWaT + Gasoducto + Red Eléctrica)
2. `fed_hospital.py` (Resiliencia UCI / UPS / Generador)
3. `fed_transport.py` (Control Semafórico NTCIP 1202)
4. `fed_gridmock.py` (Red Distribución Eléctrica)
5. `gridlabd_federate.py` (Flujo de carga 13.8 kV con fallback software)
6. `fed_logger.py` (Observabilidad y telemetría CSV)
7. `scada_server.py` (SCADA DMZ / Historian WAL / REST API / HMI)

### Estado de Módulos Específicos:
- **`helics_sim/fed_sis.py`**: Lógica SIL-3 independiente. **No cableado como federado HELICS en vivo** (librería Python invocada por `attack_triton_low_slow.py`).
- **Modelos Standalone (`physical/elec/grid_elec.py`, `plant_gas.py`, `hospital_load.py`)**: Reservados para pruebas aisladas y expansión futura. Marcados con banners de alcance.
- **Seguridad IT/OT**: Proxy DPI Modbus (`network/modbus_proxy.py`), Controlador SDN OpenFlow (`sdn_controller.py`), Active Directory DC (`ad_dc_emulator.py`), DNP3 SA L1 (`plc/dnp3_emulator.py`), SIEM Correlation (`siem_pipeline.py`).

---

## 🔒 2. Matriz de Deuda Técnica y Hallazgos IEC 62443

| ID Finding | Clasificación | Estado / Tratamiento | Justificación / Control Compensatorio |
|---|---|---|---|
| **F-01** | Conduit DMZ→OT | ✅ CERRADO (SL2) | Firewall `iptables` ACL por IP + Proxy DPI Modbus. |
| **F-02** | SPOF EWS | ✅ CERRADO (SL2) | Zona PAW aislada `s4` (`10.0.4.0/24`) con restricción SSH. |
| **F-03** | L2 Corp/DMZ | ⚠️ ACEPTADO CTF (SL1) | Debilidad intencional para prácticas de Kerberoasting/AS-REP. |
| **F-04** | Safe State Hospital | ✅ CERRADO (SL2) | Hardware Interlock Override en `fed_hospital.py`. |
| **F-05** | Modbus Plano | ⚠️ ACEPTADO CTF (SL1) | Inyección Modbus sin cifrar requerida para escenarios CTF. |
| **F-06** | Loss of View Alarm | ⚠️ ACEPTADO CTF (SL1) | Alarma SCADA activa; sin aislamiento automático por software. |
| **F-07** | Load-Shedding | ⚠️ ACEPTADO CTF (SL1) | Deslastre automático desactivado para permitir cascadas. |
| **F-08..12** | Mitigación Parcial | 🔄 RECONCILIADO | RF-12 Matriz de Conduit e IP/Puerto documentada en `docs/ERS.md`. |

---

## 🎯 3. Fases del Roadmap de Fidelidad (Fases 0 a 9)

> **Leyenda de Estado**:
> - 🔵 **Completada**: Fase totalmente implementada y validada con suite de tests.
> - 🟡 **En Progreso**: Fase en desarrollo activo (implementación parcial verificada).
> - ⚪ **Planificada**: Fase pendiente por ejecutar en el orden de dependencias.

### 🔵 Fase 0 — Fundaciones sin Root & Reestructuración (COMPLETADA)
- **Alcance**: Reconciliación de documentación (`ERS.md` RF-12 IP/Conduit matrix, RAM budget 6 GB, banners de alcance en módulos `physical/` y `fed_sis.py`, actualización de `ROADMAP.md`).
- **Verificación**: 122 PASS pytest baseline.

### 🔵 Fase 1 — Endpoints Livianos OT Categoría B (NTCIP / BACnet) (COMPLETADA)
- **Dependencias**: Fase 0.
- **Esfuerzo**: 2 días-hombre.
- **Alcance**: `NtcipListener` (NTCIP 1202 TCP `:161`) y `BacnetListener` (BACnet/IP UDP `:47808`) integrados en `plc/modbus_emulator.py` sin requerir permisos root.
- **Criterio de Aceptación**: `PYTHONPATH=. python3 -m pytest plc/tests/test_modbus_ntcip.py plc/tests/test_bacnet.py -q` pasa 100% verificando NTCIP y BACnet.

### 🔵 Fase 2 — SOC / Bridge de Inspección Pasiva (Zeek / Suricata Mock Bridge) (COMPLETADA)
- **Dependencias**: Fase 1.
- **Esfuerzo**: 3 días-hombre.
- **Alcance**: Extendido `network/siem_pipeline.py` con `ingest_zeek_log()` e `ingest_suricata_eve()` para inspección pasiva en software sin interfaces promiscuas root.
- **Criterio de Aceptación**: `PYTHONPATH=. python3 -m pytest network/tests/test_siem_passive.py -q` valida parsers de Zeek y Suricata e ingesta a `export_elk_json()`.

### 🔵 Fase 3 — Fidelidad en Protocolos OT (OPC UA / IEC 61850 / DNP3 SA) (COMPLETADA)
- **Dependencias**: Fase 1.
- **Esfuerzo**: 3 días-hombre.
- **Alcance**: Reforzados servidores `plc/opcua_emulator.py` (OPC UA write payload `SVC_WRITE_REQ`), `iec61850_emulator.py` (GOOSE/SV dataset state counter) y `dnp3_emulator.py` (DNP3 SA L1 HMAC-SHA256).
- **Criterio de Aceptación**: `PYTHONPATH=. python3 -m pytest plc/tests/test_protocols_fidelity.py -q` pasa 100% verificando la suite de fidelidad de protocolos OT.

### 🔵 Fase 4 — Categoría A Nuevos Federados Físicos OT (Desalinización / Alumbrado) (COMPLETADA)
- **Dependencias**: Fase 0.
- **Esfuerzo**: 4 días-hombre.
- **Alcance**: Modelos físicos (`physical/water/desal_plant.py`, `physical/elec/smart_lighting.py`), federados HELICS (`helics_sim/fed_desal.py`, `fed_lighting.py`), acople de carga eléctrica e interdependencias en `fed_icssim.py` (`plant_type == 'elec'`), orquestación de co-simulación de 9 federados (`helics_sim/smoke_test_phase4.sh`), e integración completa en topología Mininet (`h_desal` `10.0.3.16` y `h_lighting` `10.0.3.17` en `network/topology.py`).
- **Criterio de Aceptación**: `sudo python3 network/topology.py --test` y `PYTHONPATH=. python3 -m pytest physical/tests helics_sim/tests -q` pasan 100% verificando los modelos físicos, federación de 9 nodos y conectividad de 17 hosts en Mininet.

### 🔵 Fase 5 — HMI Industrial Integrado sobre Historian WAL (COMPLETADA)
- **Dependencias**: Fase 1, `network/historian.py`.
- **Esfuerzo**: 2 días-hombre.
- **Alcance**: Integración directa de `HistorianTSDB` (SQLite WAL) en `IndustrialHmiEngine` (`network/hmi_server.py`) expuesta en los endpoints `/api/history` y `/api/hmi/history`.
- **Criterio de Aceptación**: `PYTHONPATH=. python3 -m unittest network/tests/test_hmi_historian.py` pasa 100% verificando retorno de series de tiempo desde la DB SQLite WAL.

### 🔵 Fase 6 — DCS Redundante y Failover HA (COMPLETADA)
- **Dependencias**: Fase 5.
- **Esfuerzo**: 3 días-hombre.
- **Alcance**: Heartbeat continuo, sincronización de estado y failover activo-pasivo (< 0.2s) implementado en `network/scada_ha.py` e integrado en `network/scada_server.py` (`/api/ha/status`, `/api/ha/heartbeat`, `/api/ha/sync`).
- **Criterio de Aceptación**: `PYTHONPATH=. python3 -m unittest network/tests/test_scada_ha.py` pasa 100% verificando la conmutación activa-pasiva.

### 🔵 Fase 7 — Cableado del SIS Independiente (SIL-3) (COMPLETADA)
- **Dependencias**: Fase 4, `helics_sim/fed_sis.py`.
- **Esfuerzo**: 3 días-hombre.
- **Alcance**: Integración de `helics_sim/fed_sis.py` como federado HELICS SIL-3 activo (#10 en co-simulación), evaluación de interlocks físicos y orquestación con `ENABLE_SIS_FEDERATE=1` (`helics_sim/smoke_test_phase7.sh`).
- **Criterio de Aceptación**: `PYTHONPATH=. python3 -m unittest helics_sim/tests/test_fed_sis.py` y `helics_sim/smoke_test_phase7.sh` pasan 100% verificando sincronización de 10 federados.

### 🔵 Fase 8 — Pipeline SOC/SIEM Avanzado y Observabilidad CTF (COMPLETADA)
- **Dependencias**: Fase 2, Fase 5.
- **Esfuerzo**: 2 días-hombre.
- **Alcance**: Exportación centralizada de eventos ciberfísicos e IoC a formato ECS (Elastic Common Schema), Syslog RFC 5424 y JSON en `network/siem_pipeline.py` (`export_elk_json`, `export_syslog_rfc5424`, `export_file`).
- **Criterio de Aceptación**: `PYTHONPATH=. python3 -m unittest network/tests/test_siem.py network/tests/test_siem_passive.py` pasa 100% verificando ingestión, correlación y exportación de logs estructurados.

### 🔵 Fase 9 — Capa de Visualización Web 2D/3D (Presentación Suscrita) (COMPLETADA)
- **Dependencias**: Fase 5, `network/viz_server.py`.
- **Esfuerzo**: 4 días-hombre.
- **Alcance**: Servidor de visualización desacoplado en `network/viz_server.py` (`CityVisualizerStateEngine`) con endpoints HTTP `/api/viz/frame`, `/api/viz/history`, y `/api/viz/update` para streaming en tiempo real del estado ciberfísico urbano.
- **Criterio de Aceptación**: `PYTHONPATH=. python3 -m unittest network/tests/test_viz_server.py` pasa 100% verificando actualización de cuadros e interfaz REST/JSON 2D/3D.
