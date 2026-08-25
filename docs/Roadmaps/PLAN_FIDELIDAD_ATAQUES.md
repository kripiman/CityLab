# Plan de Fidelidad de Ataques — De Simulación a Laboratorio Profesional

## Objetivo

Cerrar la brecha diagnosticada entre **ancho** (29 escenarios, 5 sectores, 6+ protocolos) y **fondo** (la mayoría de los scripts `attacker/attack_*.py` autoreportan `{'status': 'SUCCESS'}` sin tocar un dispositivo real). La meta es que cada escenario piloto **abra un socket real contra el emulador correspondiente y verifique una mutación de estado real** (coil, holding register, `XCBR1.Pos.stVal`, fila en el historian), en vez de construir un diccionario sintético en memoria.

Este plan NO expande sectores. La expansión de ancho (`ethereal-launching-grove.md`) queda **pausada** por decisión explícita: fondo antes que ancho.

## Principio rector (Regla P0)

> Cero diccionarios sintéticos `{'status': 'SUCCESS'}`. Todo escenario piloto abre un socket real contra `plc/*_emulator.py` (o el servicio real correspondiente) y hace `assert` sobre la mutación de estado física/lógica que el ataque provocó de verdad.

Corolario: un escenario que es legítimamente de mesa (tabletop / ejercicio de decisión, p. ej. `attack_ransomware_tabletop.py`) se **etiqueta como tal** y no se disfraza de exploit técnico. La honestidad de la etiqueta es parte de la profesionalización.

## Restricción de entorno (verificada)

- Usuario `kripi`, uid 1000, **sin root**. Confirmado esta sesión.
- **Puerto 502 es privilegiado**: un emulador Modbus no puede bindearlo sin root. Los tests piloto bindean un **puerto alto** (convención de bloque abajo) exactamente como ya hacen `test_rbac.py` (18082), `test_historian.py` (18081) y `test_opcua.py`. Con puerto alto, **cero root**.
- Los puertos GOOSE (10102), SV (10103), OPC UA (4840), DNP3 (20000) son **> 1024 = no privilegiados**: testeables sin root tal cual.
- Conclusión: **los 5 pilotos son ejecutables sin root** en la capa de test unitario. La validación bajo Mininet real (segmentación entre zonas, alcanzabilidad cruzada) permanece **BLOQUEADA** hasta una sesión con `sudo` + Mininet, y debe marcarse explícitamente así en cada reporte de progreso, nunca omitirse en silencio.

### Convención de puertos de test (bloque reservado 15000–15999)

| Protocolo | Puerto producción | Puerto de test (alto, sin root) |
|---|---|---|
| Modbus/TCP | 502 | 15020 |
| DNP3 | 20000 | 15200 |
| OPC UA | 4840 | 14840 (ya usado por `test_opcua.py`) |
| GOOSE UDP | 10102 | 15102 |
| SV UDP | 10103 | 15103 |

## Estado real de cada script piloto (auditado línea por línea)

Ninguna de estas afirmaciones es de segunda mano; cada una fue leída del código en esta sesión.

| # | Script | Estado actual | Socket real | Muta estado real | Verificación |
|---|---|---|---|---|---|
| 1 | `attack_chemical_dosing.py` | **COMPLETADO (Fase 2)** | **Sí** (Modbus TCP 15020 HR 10) | **Sí** (HR 10 = 85, readback 8.5 ppm) | `test_attack_dosing.py` (4/4 PASS) |
| 2 | `attack_goose_spoofing.py` | **COMPLETADO (Fase 1)** | **Sí** (UDP 15102 PDU codificado) | **Sí** (`XCBR1.Pos.stVal = False`) | `test_attack_goose.py` (4/4 PASS) |
| 3 | `attack_ot_active_scan.py` | **COMPLETADO (Fase 3)** | **Sí** (`socket.connect_ex` 15020/14840/15200) | **Sí** (Detección empírica open/closed) | `test_attack_active_scan.py` (3/3 PASS) |
| 4 | `attack_stuxnet_replay.py` | **COMPLETADO (Fase 4)** | **Sí** (Modbus TCP 15020 HR 20 + TSDB Replay) | **Sí** (Divergencia `real != historian_last`) | `test_attack_stuxnet.py` (3/3 PASS) |
| 5 | `attack_triton_low_slow.py` | **COMPLETADO (Fase 4)** | **Sí** (Modbus TCP 15020 HR 20) | **Sí** (Sigilo 18.8 vs Disparo SIS 21.0) | `test_attack_triton.py` (4/4 PASS) |

### Dependencias técnicas resueltas

1. **Emulador Modbus con Holding Registers**: `plc/modbus_emulator.py` ahora cuenta con bloque `hr=ModbusSequentialDataBlock(0, [0]*100)` con `zero_mode=True`. HR 10 asignado a dosificación química (ppm × 10) y HR 20 asignado a variable de proceso (nivel de tanque en agua / presión en gas).
2. **Servidor Modbus stoppable**: `build_server` modularizado y `run_server` refactorizado con `serve_forever()` y `shutdown()`/`server_close()` en `finally`.
3. **Receptor GOOSE con cierre limpio**: `Iec61850Server.stop()` cierra `self._listen_sock` explícitamente.
4. **Harness reutilizable**: `plc/tests/_emulator_harness.py` proporciona context managers limpios para Modbus (15020), OPC UA (14840), DNP3 (15200) e IEC 61850 (15102/15103).

## Fases Ejecutadas

- **Fase 0 [COMPLETADA]**: Harness de emuladores (`_emulator_harness.py`), `build_server` y bloque de holding registers con `zero_mode=True`.
- **Fase 1 [COMPLETADA]**: Piloto GOOSE Spoofing con socket UDP real y mutación observable de `XCBR1.Pos.stVal`.
- **Fase 2 [COMPLETADA]**: Piloto Modbus Chemical Dosing con escritura y readback en HR 10.
- **Fase 3 [COMPLETADA]**: Piloto OT Active Scan con probes TCP connect reales contra endpoints mixtos.
- **Fase 4 [COMPLETADA]**: Pilotos Stuxnet Replay (divergencia física vs TSDB) y Triton Low-and-Slow (manipulación HR 20 con evaluación SIS).
- **Fase 5 [COMPLETADA]**: Consolidación de QA en `PROMPT_QA.md` (reglas anti-trampa y flake por timing) y categorización de los 29 escenarios.

## Inventario y Categorización de los 29 Escenarios

### Grupo 1: Pilotos con Socket Real y Mutación Física (5 escenarios — 100% Completados)
- `attack_goose_spoofing.py`: Socket UDP 15102 contra IED subestación eléctrica.
- `attack_chemical_dosing.py`: Socket Modbus TCP 15020 (HR 10) contra Water PLC.
- `attack_ot_active_scan.py`: Probes TCP connect reales contra puertos OT (Modbus, OPC UA, DNP3).
- `attack_stuxnet_replay.py`: Socket Modbus TCP 15020 (HR 20) + TSDB Historian replay.
- `attack_triton_low_slow.py`: Socket Modbus TCP 15020 (HR 20) con evaluación de interlocks SIS.

### Grupo 2: Ejercicios Tabletop / Decisión / Gobernanza Legítimos (6 escenarios)
*No requieren socket a PLC; son ejercicios de crisis ejecutiva, arbitraje o forense teórico.*
- `attack_ransomware_tabletop.py` (Escenario 25): Simulación de crisis ejecutiva C-Level / ransomware IT.
- `attack_red_vs_blue_match.py` (Escenario 27): Motor de arbitraje y puntuación para ciberejercicio Red vs Blue.
- `attack_blind_randomized_env.py` (Escenario 28): Generación dinámica de parámetros para evitar memorización.
- `attack_post_incident_recovery.py` (Escenario 29): Procedimiento de reconstrucción y recuperación post-incidente.
- `attack_purple_team_mttd.py` (Escenario 30): Métricas de detección y respuesta MTTD / MTTR (NIST SP 800-61).
- `attack_grid_heatwave_attribution.py` (Escenario 23): Atribución forense de fallo físico por calor vs ciberataque.

### Grupo 3: Ataques a Servicios de Red / Identidad / SDN (7 escenarios)
*Interactúan con servicios de red (HTTP, Kerberos KDC, OVS SDN, SIEM, SQLite). (Nota: identificadores con letra como 24b/24c/24d o 25b son agrupaciones temáticas informales de scripts en `attacker/`, no títulos 1:1 de documentos).*
- `attack_kerberoast_ad.py` (Escenario 16): Petición de tickets TGS contra servicio KDC/AD (puerto 88).
- `attack_insider_rbac.py` (Escenario 17): Intento de escritura HTTP contra SCADA API (`/api/control/write`).
- `attack_honeypot_touch.py` (Escenario 22): Interacción con honeypot OT e ingestión de alerta SIEM.
- `attack_live_sdn_defense.py` (Escenario 24): Inserción de reglas de filtrado OpenFlow en controlador SDN.
- `attack_siem_rule_evasion.py`: Dispersión de tráfico multi-IP para evadir umbrales SIEM.
- `attack_ntp_time_spoofing.py`: Desfase de marcas temporales de telemetría para cegar correlación.
- `attack_dcs_failover.py`: Inducción de conmutación primaria/secundaria en DCS HA.

### Grupo 4: Candidatos para Próxima Migración a Sockets OT (11 escenarios)
*Escenarios de protocolo OT a migrar en siguientes ciclos utilizando el harness existente.*
- `attack_modbus.py` / `exploit_modbus.py` / `test_scenario_18_modbus_write.py`: Modbus TCP coils/registers.
- `attack_modbus_read_only.py`: Lectura no autorizada de Holding Registers / Coils.
- `attack_bacnet.py`: Inyección BACnet/IP (puerto 47808) contra Hospital PLC.
- `attack_ntcip.py`: Comandos NTCIP (puerto 161) contra Transport Traffic Controller.
- `attack_ot_passive_recon.py`: Captura y análisis de tráfico de red OT en vivo.
- `attack_multisector.py` / `attack_scada_tour.py`: Barridos multi-sectoriales sobre la red OT.
- `attack_ransomware_ot_impact.py`: Cifrado y disrupción en endpoints OT.
- `attack_apt_sandworm_campaign.py`: Campaña compuesta APT en 5 fases (parcialmente migrada).
- `attack_historian_anti_forensics.py`: Manipulación de base de datos TSDB WAL.

## Verificación de la Suite
- **163/163 PASS** en `python3 scripts/validate_localhost.py` (24.9s).
- Cero fallos, cero flakes en 3 ejecuciones consecutivas.

