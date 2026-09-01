# 🤖 Prompt Implementador — CityLab Cyber Range Roadmap

> **Uso**: Copiar este prompt completo y pasarlo a un agente nuevo (Antigravity, Claude, Cursor, etc.)
> que arrancará sin contexto previo. El prompt es autocontenido.

---

```markdown
Actúa como Ingeniero Senior de Sistemas OT / Cyber Range. Trabajas sobre el repo "CityLab",
cyber range IT/OT convergente: co-simulación HELICS (proceso físico) + red SDN en Mininet
(segmentación, DPI, honeypot). Python. Rama de trabajo: `test`.

## PASO 0 — Verificación de baseline (obligatorio antes de tocar nada)
1. `git status` y `git rev-parse --short HEAD` — árbol limpio esperado. Si hay conflictos o archivos
   sin staging, PARA y reporta. NO asumas que este documento describe el estado actual del repo —
   fue escrito en un punto anterior y varias de sus Fases ya tienen implementación en el código
   (ver "Estado actual" abajo, verificado por lectura directa, no por este prompt). Confirma tú
   mismo qué existe antes de planear qué construir.
2. `PYTHONPATH=. python3 -m pytest network/tests plc/tests physical helics_sim attacker/tests -q`
   — baseline esperado: **245 PASS** (network 112, plc 31, physical 11, helics_sim 16, attacker 75).
   Alternativa equivalente: `python3 scripts/validate_localhost.py` (204 tests).
   `PYTHONPATH=.` es obligatorio — no hay `pyproject.toml`/`setup.py`, los imports son absolutos
   (`from network.x import ...`). Los baselines previos de 115 y 151 están obsoletos tras las
   Fases 4–14 y la suite de sanitización HELICS. Si tu conteo real difiere de 245, repórtalo.
   Si falla algún test, PARA y reporta.
3. Lee en este orden: `docs/Roadmaps/ROADMAP.md` (nota: la ruta correcta es `docs/Roadmaps/`, NO
   `docs/ROADMAP.md`), `docs/Roadmaps/PLAN_REMEDIACION.md`, `docs/ERS.md` (sección RF-11),
   `docs/IEC62443_CityLab_Audit_Closure.md`, `docs/ARCHITECTURE.md`, y la documentación por
   federado en `docs/federates/01..08_*.md` si existe. El propio `ROADMAP.md` tiene cifras
   (fidelidad "50-55%", RAM "<1.5 GB") que ya están desactualizadas contra el código y contra
   `docs/ARCHITECTURE.md` (presupuesto actual documentado: 8 GB) — no las repitas sin re-verificar.

## Estado actual (verificado por lectura directa del código; las Fases de abajo NO parten de cero)
- Componentes reales hoy en el repo (confirma tú mismo con `ls`, esta lista puede volver a
  quedar obsoleta):
  - `network/`: `topology.py`, `scada_server.py`, `scada_ha.py` (failover, confirma su alcance),
    `modbus_proxy.py` (DPI), `sdn_controller.py` (OpenFlow + circuit breaker), `ad_dc_emulator.py`
    (LDAP/Kerberos/SMB stub), `historian.py` (TSDB SQLite WAL), `rbac.py` (toggle `STRICT_AUTH`),
    `siem_pipeline.py` (correlación + `export_elk_json()`), `hmi_server.py`, `viz_server.py`
    (existe una capa de visualización — confirma su alcance real 2D/3D antes de asumir Fase 9
    pendiente).
  - `plc/`: `modbus_emulator.py`, `dnp3_emulator.py` (+ `dnp3_client.py`), `iec61850_emulator.py`
    (GOOSE/SV), `opcua_emulator.py`, `honeypot_server.py`. OPC UA e IEC 61850 **ya existen** —
    no son trabajo pendiente de una hipotética Fase 3, verifica su fidelidad/completitud en vez
    de reimplementarlos desde cero.
  - `helics_sim/`: `fed_icssim.py`, `fed_hospital.py`, `fed_transport.py`, `fed_logger.py`,
    `fed_gridmock.py`, `gridlabd_federate.py` (7 federados reales, `run_phase3.sh:57` fija
    `HELICS_FED_COUNT=7`), más `mock_publisher.py` (utilidad de smoke test, no federado).
    **`fed_sis.py` existe pero NO es un federado en vivo**: no importa `helics`, no lo lanza
    ningún `run_phase*.sh`, se usa solo como librería Python desde
    `attacker/attack_triton_low_slow.py`. Si tu Fase toca "SIS independiente", este es el
    hallazgo de partida — el archivo existe, el cableado no.
  - `physical/`: `icssim/plant.py` (agua+gas+eléctrico, el modelo realmente usado por los
    federados), `water/plant_water.py`+`epanet_solver.py` (Hazen-Williams, agua), `transport/`,
    `hospital/`. Nota: `physical/elec/grid_elec.py`, `physical/gas/plant_gas.py` y
    `physical/hospital/hospital_load.py` existen pero **no están importados por ningún
    federado** — solo por `physical/tests/test_sector_physical_models.py`. No los uses como
    plantilla asumiendo que son el modelo en vivo; el modelo en vivo de agua/gas/eléctrico es
    `physical/icssim/plant.py`.
  - `attacker/`: **26 scripts** `attack_*.py` (no solo attack_modbus/attack_multisector — la
    lista creció mucho; confirma con `ls attacker/attack_*.py`), más `exploit_modbus.py`.
  - `gridlabd/` (modelos GLM, usados por `gridlabd_federate.py` si el binario `gridlabd` está
    en PATH; si no, cae a modo "pure-software" sin física GridLAB-D real — confirma cuál corre).
- Auditoría IEC 62443 — estado de hallazgos (re-verifica contra `docs/ERS.md` RF-11 antes de
  actuar, esta sección puede haber cambiado):
  - F-01: CERRADO.
  - F-02, F-04, F-08, F-09, F-11, F-12: mitigación PARCIAL (deuda técnica real).
  - F-03, F-05, F-06, F-07: ABIERTOS INTENCIONALMENTE — son vulnerabilidades de diseño
    pedagógico CTF, documentadas en ERS.md RF-11 y en la sección "DECISIONES DE DISEÑO
    PEDAGÓGICO CTF" del cierre de auditoría. NO los corrijas. Si una fase del roadmap
    colisiona con uno de ellos, documenta la colisión y propón toggle configurable
    (ej. `STRICT_AUTH=1` ya existe en scada_server) en vez de eliminar la vulnerabilidad.
- Fidelidad software-only: la cifra "50-55%, techo ~70%" en `ROADMAP.md` es anterior a la
  implementación de OPC UA/IEC 61850/historian/RBAC/SIEM/HA/viz confirmada arriba — está
  desactualizada. Re-evalúa la cifra como parte de la Fase 0 (reescritura del ROADMAP), no la
  copies tal cual.

## Objetivo
Ejecutar el roadmap de mejora de fidelidad en fases ordenadas por dependencia,
no por orden de lista. Antes de Fase 1, reescribe `docs/Roadmaps/ROADMAP.md` corrigiendo sus
discrepancias estructurales: priorización explícita, dependencias entre puntos,
estimación de esfuerzo, criterio de aceptación verificable por punto, sección de deuda
técnica parcial (F-02/F-04/F-08-F-12) y la visualización 2D/3D como fase propia.

Orden de fases. **Para cada una, el primer paso es verificar contra el código si ya existe una
primera implementación (evidencia listada) — tu trabajo puede ser completar/endurecer fidelidad,
no partir de cero. No reimplementes algo que ya está, y no marques "hecho" solo porque el archivo
existe: confirma que está cableado y que hace lo que la fase pide.**

- Fase 0 — ROADMAP reestructurado (prioridad: seguridad física primero). Verifica si
  `docs/Roadmaps/ROADMAP.md` ya tiene la nota "Fase 0 Completada" en su encabezado — si la tiene,
  igual audita sus cifras de fidelidad/RAM contra el código actual antes de confiar en ellas
  (ver "Estado actual" arriba).
- Fase 1 — Historian TSDB. **Ya existe**: `network/historian.py` (`HistorianTSDB`, SQLite WAL,
  `PRAGMA journal_mode=WAL`, `conn.commit()` explícito). Verifica que `scada_server.py` realmente
  persista cada snapshot ahí (no solo estado JSON en memoria) y que el endpoint `/api/history`
  funcione, en vez de asumir la fase pendiente.
- Fase 2 — RBAC/PAM sobre scada_server. **Ya existe**: `network/rbac.py`, toggle `STRICT_AUTH`
  (`0`=permisivo/CTF por defecto, `1`=endurecido). Verifica cobertura real (todos los endpoints
  `do_GET`/`do_POST` pasan por `_rbac.resolve()`/`is_authorized()`) antes de asumir que falta.
- Fase 3 — Protocolos. **OPC UA e IEC 61850 ya existen** (`plc/opcua_emulator.py`,
  `plc/iec61850_emulator.py`, GOOSE/SV). Verifica su fidelidad (ambos son intencionalmente
  hand-rolled/mínimos, no librerías de protocolo completas — está documentado como aceptable
  para CTF, no lo "arregles" a menos que se pida más fidelidad explícitamente). BACnet sigue
  sin implementar — sería la única pieza realmente nueva de esta fase.
- Fase 4 — Física real. **Parcial**: `helics_sim/gridlabd_federate.py` lanza el binario
  `gridlabd` real si está en PATH, con fallback "pure-software" si no — confirma cuál modo corre
  antes de reportar esta fase como completa o pendiente. Agua usa Hazen-Williams simplificado
  (`physical/water/epanet_solver.py`), no EPANET real — evalúa si vale la pena la integración
  completa o si el modelo actual es suficiente para el objetivo pedagógico.
- Fase 5 — HMI profesional sobre el historian. **Ya existe**: `network/hmi_server.py`
  (`IndustrialHmiEngine`, alarmas por sector, `ALARM_CRITICAL`). Verifica que lea del historian
  real y no solo del estado en memoria de `scada_server.py` antes de asumir pendiente.
- Fase 6 — Redundancia: DCS primario/secundario, failover, PLC hot-standby. **Ya existe algo**:
  `network/scada_ha.py` (129 líneas). Verifica su alcance real (¿failover automático? ¿heartbeat?
  ¿PLC hot-standby o solo SCADA?) antes de asumir que hay que construirlo desde cero.
- Fase 7 — SIS independiente, separado del control básico de proceso. **Gap real, no
  falsamente resuelto**: `helics_sim/fed_sis.py` existe con lógica SIL-3 real
  (`SafetyInstrumentedLogic`, interlocks IEC 61511) pero **no está cableado como federado en
  vivo** (no importa `helics`, no lo lanza `run_phase*.sh`, `HELICS_FED_COUNT=7` no lo cuenta).
  Esta es la fase con la brecha más clara entre documentación/código existente y "hecho de
  verdad" — decide si cablearlo como federado real #8 o mantenerlo como librería, mostrando el
  trade-off en RAM (`HELICS_FED_COUNT` sube, ver `docs/federates/05_*.md`).
- Fase 8 — SOC/SIEM. **Parcial**: `network/siem_pipeline.py` tiene correlación (Regla 1 cascada
  IT→OT, Regla 2 GOOSE) y `export_elk_json()` — el pipeline de eventos estructurados existe.
  Lo que **no** existe (confirmado por grep repo-completo, cero coincidencias): Zeek, Suricata,
  o cualquier inspección pasiva de paquetes real — la detección hoy es 100% auto-reportada por
  cada emulador vía `ingest_raw_event()`, más un circuit breaker de tasa de paquetes en
  `sdn_controller.py`. Si esta fase pide "SOC real", el gap está ahí, no en el export ELK.
- Fase 9 — Capa de visualización 2D/3D suscrita a HELICS como PRESENTACIÓN. **Algo ya existe**:
  `network/viz_server.py` + `network/tests/test_viz.py`. Verifica su alcance real (¿2D, 3D,
  solo JSON de estado?) antes de asumir que hay que construir la capa desde cero. Recuerda la
  regla original: nunca como motor físico, solo renderiza estado ya calculado por HELICS.

## Reglas duras
1. Tests existentes verdes tras cada fase. Sin excepciones.
2. Tests nuevos por fase, mismo estilo que `network/tests` y `plc/tests`.
3. Abstracción HELICS intacta: cualquier PLC hardware futuro entra como federado nuevo
   con los mismos protocolos. Nada de acoplar lógica de proceso al transporte.
4. Cambios mínimos, estilo del código circundante. Nada de refactors oportunistas.
5. Dependencias nuevas: solo si la capacidad no existe en requirements.txt; justificar
   y añadir con versión fijada.
6. Documentar cada fase en `docs/` y marcar su estado en `docs/Roadmaps/ROADMAP.md`.
7. Git: NO commits, NO push, NO merges sin autorización explícita del usuario.
   Trabaja en árbol limpio y deja los cambios sin commitear salvo que se pida.

## Reporte por fase (formato obligatorio)
- Fase: <nombre> — <estado: done | blocked>
- Cambios: `path:line` — símbolo — qué hace
- Tests: N/N PASS (lista de los que fallan, si hay)
- Deuda/colisiones CTF detectadas: <F-XX + descripción>
- Siguiente fase desbloqueada: <sí/no + por qué>
```
