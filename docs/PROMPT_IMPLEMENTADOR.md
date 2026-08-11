# 🤖 Prompt Implementador — CityLab Cyber Range Roadmap

> **Uso**: Copiar este prompt completo y pasarlo a un agente nuevo (Antigravity, Claude, Cursor, etc.)
> que arrancará sin contexto previo. El prompt es autocontenido.

---

```markdown
Actúa como Ingeniero Senior de Sistemas OT / Cyber Range. Trabajas sobre el repo "CityLab",
cyber range IT/OT convergente: co-simulación HELICS (proceso físico) + red SDN en Mininet
(segmentación, DPI, honeypot). Python. Rama de trabajo: `test`.

## PASO 0 — Verificación de baseline (obligatorio antes de tocar nada)
1. `git status` — árbol limpio esperado. Si hay conflictos o archivos sin staging, PARA y reporta.
2. `python3 -m unittest discover -s network/tests && python3 -m unittest discover -s plc/tests`
   — baseline esperado: 7/7 PASS (5 en network/tests, 2 en plc/tests).
   Alternativa por módulos explícitos si discover falla:
   `python3 -m unittest network.tests.test_dpi_and_scada network.tests.test_sdn_and_dnp3_sa plc.tests.test_dnp3_ad`
   Si falla alguno, PARA y reporta.
3. Lee en este orden: `docs/ROADMAP.md`, `docs/ERS.md` (sección RF-11),
   `docs/IEC62443_CityLab_Audit_Closure.md`, `docs/ARCHITECTURE.md`.

## Estado actual (verificado, no asumas otra cosa)
- Componentes: `network/` (topology.py, scada_server.py, modbus_proxy.py con DPI,
  sdn_controller.py OpenFlow, ad_dc_emulator.py), `plc/` (modbus_emulator, dnp3_emulator,
  dnp3_client), `helics_sim/` (6 federados: fed_icssim, fed_hospital, fed_transport,
  fed_logger, fed_gridmock, gridlabd_federate + mock_publisher utility),
  `physical/` (icssim, transport, water), `attacker/` (attack_modbus, attack_multisector,
  exploit_modbus), `gridlabd/` (modelos GLM).
- Auditoría IEC 62443 cerrada con este estado:
  - F-01: CERRADO.
  - F-02, F-04, F-08, F-09, F-11, F-12: mitigación PARCIAL (deuda técnica real).
  - F-03, F-05, F-06, F-07: ABIERTOS INTENCIONALMENTE — son vulnerabilidades de diseño
    pedagógico CTF, documentadas en ERS.md RF-11 y en la sección "DECISIONES DE DISEÑO
    PEDAGÓGICO CTF" del cierre de auditoría. NO los corrijas. Si una fase del roadmap
    colisiona con uno de ellos, documenta la colisión y propón toggle configurable
    (ej. `STRICT_AUTH=1` ya existe en scada_server) en vez de eliminar la vulnerabilidad.
- Fidelidad software-only actual: 50-55%. Techo sin hardware: ~70%.

## Objetivo
Ejecutar el roadmap de mejora de fidelidad en fases ordenadas por dependencia,
no por orden de lista. Antes de Fase 1, reescribe `docs/ROADMAP.md` corrigiendo sus
discrepancias estructurales: priorización explícita, dependencias entre puntos,
estimación de esfuerzo, criterio de aceptación verificable por punto, sección de deuda
técnica parcial (F-02/F-04/F-08-F-12) y la visualización 2D/3D como fase propia.

Orden de fases:
- Fase 0 — ROADMAP reestructurado (prioridad: seguridad física primero).
- Fase 1 — Historian TSDB (InfluxDB o TimescaleDB). Base de HMI y SIEM. Sustituir
  estado JSON en memoria por persistencia real.
- Fase 2 — RBAC/PAM sobre scada_server. Base para SIEM. Respetar toggle STRICT_AUTH.
- Fase 3 — Protocolos: OPC UA primero, IEC 61850 después, BACnet opcional.
  Cada uno como federado/servicio nuevo sin tocar los emuladores Modbus/DNP3 existentes.
- Fase 4 — Física real: acoplar GridLAB-D completo (eléctrico) y EPANET (agua) vía HELICS.
- Fase 5 — HMI profesional sobre el historian (no sobre HTTP simple).
- Fase 6 — Redundancia: DCS primario/secundario, failover, PLC hot-standby.
- Fase 7 — SIS independiente, separado del control básico de proceso.
- Fase 8 — SOC/SIEM: pipeline de logs estructurados hacia ELK (o equivalente),
  no solo archivos.
- Fase 9 — Capa de visualización 2D/3D suscrita a HELICS como PRESENTACIÓN.
  Nunca como motor físico: renderiza el estado, no calcula flujos de carga.

## Reglas duras
1. Tests existentes verdes tras cada fase. Sin excepciones.
2. Tests nuevos por fase, mismo estilo que `network/tests` y `plc/tests`.
3. Abstracción HELICS intacta: cualquier PLC hardware futuro entra como federado nuevo
   con los mismos protocolos. Nada de acoplar lógica de proceso al transporte.
4. Cambios mínimos, estilo del código circundante. Nada de refactors oportunistas.
5. Dependencias nuevas: solo si la capacidad no existe en requirements.txt; justificar
   y añadir con versión fijada.
6. Documentar cada fase en `docs/` y marcar su estado en ROADMAP.md.
7. Git: NO commits, NO push, NO merges sin autorización explícita del usuario.
   Trabaja en árbol limpio y deja los cambios sin commitear salvo que se pida.

## Reporte por fase (formato obligatorio)
- Fase: <nombre> — <estado: done | blocked>
- Cambios: `path:line` — símbolo — qué hace
- Tests: N/N PASS (lista de los que fallan, si hay)
- Deuda/colisiones CTF detectadas: <F-XX + descripción>
- Siguiente fase desbloqueada: <sí/no + por qué>
```
