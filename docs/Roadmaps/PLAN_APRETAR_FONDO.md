# Plan para Apretar el Fondo — De Ancho-con-Núcleo a Fidelidad Profunda

## Diagnóstico honesto de partida

CityLab **abarca mucho y aprieta en un núcleo chico**. Medido línea por línea sobre `attacker/` en esta sesión:

- **29 scripts de ataque, 29 tests, 5 sectores, 6+ protocolos, 5 zonas IEC 62443** — ancho legítimo y sólido.
- **5/29 (17%)** aprietan de verdad: el test verifica **mutación real del emulador** vía socket + readback (`getValues`, `dataset.get`, fila del historian). Son los pilotos: `goose_spoofing`, `chemical_dosing`, `ot_active_scan`, `stuxnet_replay`, `triton_low_slow`.
- **6/29** abren un socket pero el test **no** verifica mutación — solo afirma sobre el diccionario devuelto (`bacnet`, `ntcip`, `kerberoast`, `multisector`, `modbus`, `exploit_modbus`). Socket intentado ≠ dispositivo cambiado.
- **18/29** no abren ningún socket. **25/29** contienen `'status': 'SUCCESS'` autoreportado. **21/29** tests pasarían aunque el ataque no hiciera nada.
- De los 24 que no aprietan, **~6 son tabletop legítimos** (ejercicios de decisión/gobernanza, honestamente etiquetados) y **~18 son la brecha real** (ataques OT/red que deberían tocar un device y no lo hacen, o lo tocan sin verificar).

Segundo agujero, más grave que el conteo: **todo lo profundo se prueba solo en capa unitaria con puerto alto**. Cero validación bajo Mininet real (segmentación entre zonas, GOOSE multicast L2, alcance a PLC en `10.0.3.x:502`, SIEM end-to-end). Sin `sudo` sigue bloqueado.

Este plan cierra ambos agujeros. No expande sectores (la expansión de ancho queda pausada, igual que en `PLAN_FIDELIDAD_ATAQUES.md`).

## Definición de "Apretar" (Definition of Done por ataque)

Un ataque **aprieta** cuando su test cumple TODAS estas condiciones (gate no negociable, extiende las reglas #18/#19 de `PROMPT_QA.md`):

1. **Socket real** contra el emulador/servicio objetivo (no un diccionario en memoria).
2. **`assert res['mode'] == 'SOCKET_LIVE'`** — bloquea el enmascaramiento por fallback silencioso.
3. **Assert sobre la mutación de estado observada en el objetivo**, leída del datastore del propio emulador o servicio: `context[0x00].getValues(...)`, `dataset.get('XCBR1.Pos.stVal')`, estado de breaker DNP3, present-value BACnet, fila/timestamp del historian, verdict de RBAC, alerta ingerida por el SIEM. Nunca solo sobre el dict devuelto.
4. **Ciclo de vida limpio** vía context manager de `plc/tests/_emulator_harness.py` (start → yield → stop en `finally`), puerto alto (bloque 15000–15999), sin root.
5. Si el escenario es legítimamente de mesa, se etiqueta **`mode: 'TABLETOP_FALLBACK'`** o `tabletop` explícito — la honestidad de la etiqueta es parte del entregable, no un disfraz de exploit.

Métrica única de progreso: **fidelidad verificada = (tests con mutación real) / 29**. Base **5/29 (17%)**.

## Restricción de entorno (heredada, verificada)

Usuario `kripi`, uid 1000, **sin root**. Puertos altos (15020, 15102, 14840, 15200, y los nuevos que se reserven) son testeables sin root. Todo cambio a `network/topology.py` (hosts Mininet, `iptables`, OVS/OpenFlow, sniffing L2) permanece **BLOQUEADO** hasta una sesión con `sudo` + Mininet, y debe marcarse así explícitamente en cada reporte, nunca omitirse en silencio.

## Activos ya disponibles (no reinventar)

- **Harness**: `plc/tests/_emulator_harness.py` con `running_modbus_server` (15020), `running_iec61850_server` (15102/15103), `running_opcua_server` (14840), `running_dnp3_server` (15200).
- **Emulador Modbus** con holding registers (`build_server`, HR 10 dosificación, HR 20 variable de proceso) y servidor stoppable.
- **`BacnetListener` vive dentro de `plc/modbus_emulator.py`** — el objetivo BACnet ya existe in-process, no hay que construir un emulador nuevo desde cero.
- **`Dnp3Server`** con `trip_breaker`/`close_breaker` y challenge HMAC de Secure Authentication — permite verificar mutación de breaker real.
- **Servicios defensivos in-process**: `scada_server` (:8080, RBAC), `honeypot_server` (:502), `siem_pipeline` (`ingest_raw_event`), `historian` (TSDB SQLite/WAL).

## Golden rule — vulnerabilidades intencionales

F-03, F-05, F-06, F-07 son material CTF deliberado. Al migrar `insider_rbac` y cualquier ataque de auth/segmentación se **preserva el toggle** (`STRICT_AUTH=0` permisivo por defecto, `STRICT_AUTH=1` endurecido) y **ambas ramas** deben quedar funcionales y testeadas. Apretar el fondo nunca significa cerrar estas vulnerabilidades — significa demostrar que el ataque las ejerce de verdad en la rama permisiva y es contenido en la endurecida.

## Tracks de ejecución

Ordenados por relación esfuerzo/valor, no por número de escenario. Se recomienda ejecutarlos A → B → C, dejando D para la sesión root.

### Track A — Familia Modbus [COMPLETADO]

Reutilizan `running_modbus_server` + readback exactamente como los pilotos `dosing`/`triton`. Migración mecánica.

| Script | Objetivo | Mutación a verificar | Estado |
|---|---|---|---|
| `attack_modbus.py` / `exploit_modbus.py` | Modbus `:15020`, coil write | coil real conmuta (`getValues(1, addr, 1)`) | **COMPLETADO** (`test_scenario_18_modbus_write.py`, 5/5 PASS) |
| `attack_modbus_read_only.py` | Modbus `:15020`, HR/coil read | valores leídos == sembrados en el emulador | **COMPLETADO** (`test_attack_modbus_read.py`, 3/3 PASS) |
| `attack_scada_tour.py` | Servidor HMI `:18085` + engine | consulta HTTP/engine de overview y alarmas | **COMPLETADO** (`test_attack_scada_tour.py`, 3/3 PASS) |
| `attack_multisector.py` | Modbus barrido multi-sector | read/write reales en targets Modbus | **COMPLETADO** (`test_attack_multisector.py`, 3/3 PASS) |

Salida de Track A: fidelidad verificada **5 → 9 (31%)** [LOGRADO]. 174/174 suite PASS.

### Track B — Nuevos objetivos de protocolo [COMPLETADO]

Se extendió el harness con `running_bacnet_server`, `running_ntcip_server` y `running_ad_dc` en `_emulator_harness.py`.

| Script | Objetivo | Mutación a verificar | Estado |
|---|---|---|---|
| `attack_bacnet.py` | `BacnetListener` `:14780` (UDP) | `listener.status == 'ALARM'` en datastore | **COMPLETADO** (`test_attack_bacnet_ntcip.py`, 3/3 PASS) |
| `attack_ntcip.py` | `NtcipListener` `:14161` (TCP) | `listener.phase == 'FLASHING_YELLOW'` & `coord == 'OFF'` | **COMPLETADO** (`test_attack_bacnet_ntcip.py`, 3/3 PASS) |
| `attack_kerberoast_ad.py` | `ad_dc_emulator` KDC `:14088` (TCP) | ticket TGS extraído vía socket TCP | **COMPLETADO** (`test_attack_kerberoast.py`, 3/3 PASS) |
| Ataque DNP3 breaker | `Dnp3Server` `:20006` (TCP) | `breaker_closed == False` tras CROB TRIP | **COMPLETADO** (`test_protocols_fidelity.py`, CROB PASS) |

Salida de Track B: fidelidad verificada **9 → 13 (45%)** [LOGRADO]. 180/180 suite PASS.

### Track C — Integración con el stack defensivo in-process (sin root)

El objetivo es un servicio Python real (SCADA HTTP, SIEM, historian, HA), no un PLC. La mutación se verifica en el estado de ese servicio.

| Script | Objetivo | Mutación a verificar | Nota |
|---|---|---|---|
| `attack_insider_rbac.py` | `scada_server :8080` `/api/control/write` + `rbac` | write aceptado (STRICT_AUTH=0) y denegado (STRICT_AUTH=1) | **Preservar toggle F-06, testear ambas ramas** |
| `attack_honeypot_touch.py` | `honeypot_server :502` + `siem_pipeline` | honeypot registra la conexión Y el SIEM ingiere la alerta | encadena dos objetivos reales |
| `attack_siem_rule_evasion.py` | `siem_pipeline.ingest_raw_event` | eventos multi-IP ingresan; umbral evaluado sobre estado real | verificar que la evasión efectivamente no dispara la regla |
| `attack_ntp_time_spoofing.py` | `historian` | telemetría con timestamp desfasado persiste; divergencia detectable | fila real con timestamp manipulado |
| `attack_historian_anti_forensics.py` | `historian` TSDB SQLite/WAL | fila/WAL manipulada; tamper detectable en readback | ya toca DB, falta assert de mutación |
| `attack_dcs_failover.py` | clúster HA de `scada_server` | conmutación primaria→secundaria observable | Medio-Alto |

Salida de Track C: fidelidad verificada **13 → 19 (66%)**. Techo alcanzable **sin root**.

### Track D — Bloqueados por root / Mininet (sesión con `sudo`)

No migrables en capa unitaria sin red real. Marcar **BLOQUEADO** explícito hasta sesión root; no simular en verde.

| Script | Objetivo | Mutación a verificar | Bloqueo |
|---|---|---|---|
| `attack_live_sdn_defense.py` | `sdn_controller` OpenFlow sobre OVS | flow rule insertada / IP aislada en el switch real | OVS requiere root |
| `attack_ot_passive_recon.py` | sniff L2 en vivo | paquetes reales capturados del segmento OT | interfaz Mininet + root |
| `attack_ransomware_ot_impact.py` | endpoints OT en namespaces | proceso/endpoint caído verificable | hosts Mininet (parcial sin root) |
| `attack_apt_sandworm_campaign.py` | compuesto de 5 fases | cada fase toca su objetivo real (encadena A–D) | depende de todo lo anterior |

Salida de Track D: fidelidad verificada **19 → 23 (79%)**.

### Track E — Validación Mininet real end-to-end (cross-cutting, root)

Independiente del conteo por script: correr los ataques ya profundos **dentro de la red emulada real** y verificar la capa que la unitaria no puede tocar — segmentación entre zonas (`FORWARD DROP`), pivoting obligatorio a OT para GOOSE L2, alcance real a `10.0.3.x:502`, correlación SIEM bajo tráfico real, y **medición real de RAM/CPU** (`./citylab.sh profile`) para reemplazar toda estimación por medición. Es el paso que convierte "aprieta en banco" en "aprieta en el rango".

## Fuera de alcance de "apretar": los 6 tabletop legítimos

`ransomware_tabletop`, `red_vs_blue_match`, `blind_randomized_env`, `post_incident_recovery`, `purple_team_mttd`, `grid_heatwave_attribution` son ejercicios de decisión/gobernanza/forense. No necesitan socket. La única acción es **verificar que estén etiquetados honestamente** (`tabletop` / `TABLETOP_FALLBACK`) y no disfrazados de exploit técnico. Con esto, los 29 quedan **honestos**: 23 técnicos verificables + 6 tabletop etiquetados.

## Trayectoria de la métrica

| Hito | Fidelidad verificada (mutación real) | Cobertura honesta total |
|---|---|---|
| Base (hoy) | 5/29 (17%) | 5 + 6 tabletop = 11/29 |
| Tras Track A | 9/29 (31%) | 15/29 |
| Tras Track B | 13/29 (45%) | 19/29 |
| Tras Track C (techo sin root) | 19/29 (66%) | **25/29** (4 marcados BLOQUEADO) |
| Tras Track D+E (con root) | 23/29 (79%) | **29/29 honestos** |

"Apretar mucho" = llegar a 23/29 con mutación real + 6 tabletop honestos + capa Mininet validada. Sin root, el objetivo firme y verificable es **19/29 (66%)**.

## Riesgos y disciplina

- **No cerrar vulnerabilidades intencionales** (F-03/05/06/07): apretar = demostrar el ataque en la rama permisiva y su contención en la endurecida, ambas testeadas.
- **No falso-verde**: el gate `mode == 'SOCKET_LIVE'` + assert de mutación es obligatorio; un test que pasa en fallback silencioso es una regresión.
- **No omitir bloqueos root**: cada script de Track D/E se reporta BLOQUEADO hasta que exista sesión `sudo`, nunca como completado.
- **Deuda de mantenibilidad**: al acumular context managers nuevos en el harness, mantener la convención "un context manager por protocolo, cierre en `finally`", sin descubrimiento dinámico.

## Verificación

- **Sin root (disponible ahora)**: `python3 scripts/validate_localhost.py` o `PYTHONPATH=. python3 -m pytest network/tests plc/tests physical helics_sim attacker/tests -q`. El discovery ya cubre los tests nuevos de las 5 carpetas automáticamente. Cada nuevo test debe cumplir el gate de la Definition of Done.
- **Con root (pendiente)**: `sudo ./citylab.sh up` + `sudo ./scripts/validate_e2e.sh` + `./citylab.sh profile` para Track D/E.
