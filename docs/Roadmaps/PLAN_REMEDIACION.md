# 🔧 PLAN DE REMEDIACIÓN — Cierre de Deficiencias Verificadas (CityLab)

> **Estado**: EN PROGRESO / PARCIALMENTE COMPLETADO 🟡 · **Rama**: `test` · **Fecha**: 2026-08-12
> **Resumen**: R0 (A,B,C), R1 (A,B), R2 (A,B) y R3 (A,B) CERRADOS. R1-C (Mininet e2e harness) en progreso con soporte dual (`validate_e2e.sh` sudo/Mininet + `validate_localhost.py` CI/localhost). 113/113 tests PASS.

---

## 🧭 Principio rector

Todo hallazgo aquí es un **defecto real** (código muerto, host fantasma, servicio ausente, etiqueta
falsa), **no** una vulnerabilidad CTF intencional. Las vulnerabilidades pedagógicas
**F-03 / F-05 / F-06 / F-07 permanecen abiertas** y ninguna corrección de este plan debe cerrarlas.
Donde una corrección roza el borde de una vulnerabilidad intencional, se documenta explícitamente
por qué **no** la toca y, si hiciera falta endurecer, se hace mediante *toggle* con el modo vulnerable
por defecto (patrón `STRICT_AUTH=1` ya establecido en el repo).

### Distinción crítica: LoV muerto ≠ F-06

- **F-06 (intencional)**: tras una alerta `LOSS_OF_VIEW`, el SCADA **no aísla automáticamente** —
  exige intervención manual del operador. Esto se conserva.
- **Defecto R1-A (este plan)**: el contador que **detecta** la pérdida de visibilidad
  (`_consecutive_failures`) nunca se incrementa, así que la alerta LoV **jamás se dispara** desde
  fallos reales de sondeo. Reparar la *detección* es ortogonal a F-06 y no viola el diseño CTF:
  F-06 asume que la alerta existe; hoy no llega a existir.

---

## 📊 Resumen por prioridad

| Fase | Título | Bloqueante de | Esfuerzo | Toca CTF |
|:----:|--------|---------------|:--------:|:--------:|
| **R0** | El laboratorio arranca de verdad | Cualquier validación end-to-end | M | No |
| **R1** | La cadena de detección funciona | Escenarios de Blue/Purple Team | M | No (aclara F-06) |
| **R2** | Fidelidad física honesta | Claim "simula una ciudad" | L | No |
| **R3** | Superficie de exposición e higiene | Despliegue en red compartida | S–M | Roza F-05 (con toggle) |

---

## 🟥 FASE R0 — El laboratorio arranca de verdad (P0, bloqueante)

**Problema raíz**: todo lo verificado hasta hoy fue a nivel de código y `localhost`. La topología nunca
corrió su cadena completa en Mininet. Tres defectos garantizan el fallo end-to-end.

### R0-A · Emuladores no-Modbus nunca se levantan

- **Evidencia**: `network/topology.py:269-289` — el bloque `AUTO_START_PLC` solo lanza
  `plc/modbus_emulator.py` para 5 hosts (`h_plc`, `h_plc_gas`, `h_plc_elec`, `h_plc_trans`,
  `h_plc_hosp`) más `scada_server.py`. **No** arranca:
  - Receptor GOOSE IEC 61850 en `h_ied` (10.0.3.20:10102) — `plc/iec61850_emulator.py:271-287`
    (`Iec61850Server._listen_loop`) queda como código muerto en el lab.
  - Servidor OPC UA en `h_gateway` (10.0.3.30:4840) — `plc/opcua_emulator.py`.
  - Outstation DNP3 en `h_plc_elec` (10.0.3.13:20000) — `plc/dnp3_emulator.py` (solo se lanza su
    Modbus, no su DNP3).
  - `h_icssim` (10.0.3.11) ni siquiera figura en la lista `plc_hosts`.
- **Impacto**: los escenarios 02 (GOOSE spoof → trip `XCBR1.Pos.stVal`), los de DNP3 y los de OPC UA
  son **ficción en red real**: el servicio objetivo nunca escucha.
- **Fix**: extender la lista de arranque en `topology.py:272-286` para spawnear cada emulador en su host,
  con su puerto y binario correctos. Redirigir logs a `/tmp/<host>.log` como ya se hace con Modbus.
- **Criterio de aceptación**: tras `sudo python3 network/topology.py`, dentro de la CLI de Mininet un
  `h_ied ss -lun | grep 10102`, `h_gateway ss -ltn | grep 4840` y `h_plc_elec ss -ltn | grep 20000`
  muestran el socket en escucha.

### R0-B · Host fantasma `h_ews`

- **Evidencia**: `network/topology.py` referencia `10.0.4.30` en reglas iptables
  (`:143`, `:150`, `:154`, `:157`) pero **no existe** `addHost('h_ews', ...)`. La interfaz `fw-eth3`
  recibe `10.0.4.1/24` (`:127`) como gateway, pero ningún host habita la subred 10.0.4.0/24.
- **Impacto**: las reglas de firewall PAW apuntan a un host inexistente; la zona EWS aislada está vacía.
- **Fix**: crear `h_ews = self.addHost('h_ews', ip='10.0.4.30/24')` junto al resto de hosts
  (`topology.py:73-88`) y enlazarlo al switch/segmento EWS (`s4`) coherente con `fw-eth3`.
- **Criterio de aceptación**: `net.get('h_ews')` resuelve; `h_ews ping -c1 10.0.4.1` responde; las reglas
  `:143-157` dejan de referenciar un host fantasma.

### R0-C · Honeypot sin servicio

- **Evidencia**: `h_plc_honey` (10.0.5.99) existe en topología (`topology.py:88`) pero **no hay ningún
  daemon honeypot**. `find -iname "*honey*"` solo devuelve el atacante `attacker/attack_honeypot_touch.py`,
  su test y `docs/scenarios/scenario_16_honeypot_interaction.md`. No existe implementación de listener.
- **Impacto**: los escenarios 14 (escaneo) y 16 (interacción con honeypot) no tienen nada que tocar; la
  premisa "el honeypot detecta el escaneo" es hoy inverificable.
- **Fix**: crear `plc/honeypot_server.py` — un listener mínimo (Modbus/TCP falso en :502 + log de cada
  conexión entrante con IP origen) que reenvíe eventos al `siem_pipeline`. Arrancarlo desde `topology.py`
  en `h_plc_honey`.
- **Criterio de aceptación**: desde `h_attacker`, un escaneo a 10.0.5.99:502 genera un registro de
  "touch" con la IP atacante que el SIEM correlaciona como evento de honeypot.

---

## 🟧 FASE R1 — La cadena de detección funciona (P1)

### R1-A · Contador Loss-of-View muerto

- **Evidencia**: `network/scada_server.py:55-56` declara `LOSS_OF_VIEW_THRESHOLD = 3` y
  `_consecutive_failures = {sector: 0 ...}`, pero **ninguna ruta de código lo incrementa**. El test
  `network/tests/test_dpi_and_scada.py:65` (`test_scada_watchdog_loss_of_view`) lo fija a mano y afirma
  el valor que él mismo puso — es tautológico.
- **Impacto**: la alerta `LOSS_OF_VIEW` nunca se emite ante fallos reales de sondeo. El watchdog de
  visibilidad, pilar del narrativo Blue Team, está inerte.
- **Fix**: en el bucle de sondeo `poll_plcs()` (`scada_server.py:43`), incrementar
  `_consecutive_failures[sector]` en cada excepción/timeout de sondeo y resetear a 0 en éxito. Al alcanzar
  el umbral, marcar el sector `LOSS_OF_VIEW` y emitir la alerta. **Conservar F-06**: no aislar
  automáticamente — solo alertar.
- **Criterio de aceptación**: un test que detiene el PLC objetivo (o simula 3 timeouts consecutivos vía
  el transporte real) y verifica que el estado transiciona a `LOSS_OF_VIEW` **por el propio bucle**, no
  por asignación manual.

### R1-B · Test tautológico reescrito

- **Evidencia**: mismo `test_dpi_and_scada.py:65`.
- **Fix**: reescribir para ejercitar el incremento real de R1-A. Barrer el resto de la suite en busca del
  mismo antipatrón (afirmar un valor recién asignado por el propio test).
- **Criterio de aceptación**: el test falla si se revierte R1-A (prueba de que valida comportamiento, no
  el *setter*).

### R1-C · Arnés de validación end-to-end

- **Problema raíz**: la brecha de fondo — nunca hubo un procedimiento repetible que levante el lab y
  valide una cadena de ataque completa en red real.
- **Fix**: crear `scripts/validate_e2e.sh` (o federado equivalente) que, bajo `sudo`: (1) levante la
  topología, (2) confirme que todos los sockets de R0-A escuchan, (3) ejecute la cadena del escenario 02
  (pivoteo → GOOSE spoof contra 10.0.3.20:10102), (4) verifique el cambio real de `XCBR1.Pos.stVal`, y
  (5) confirme la alerta correlacionada en el SIEM. Reportar PASS/FAIL por eslabón.
- **Criterio de aceptación**: el script corre de principio a fin y reporta el estado de cada eslabón; los
  fallos de OVS/rutas/timing HELICS quedan visibles en vez de asumidos.

---

## 🟨 FASE R2 — Fidelidad física honesta (P1)

### R2-A · Física de juguete mal etiquetada como "EPANET"

- **Evidencia**: `physical/water/epanet_solver.py` se llama `EpanetHydraulicSolver` pero solo importa
  `math` (`:21`). No es EPANET. Todo el directorio `physical/` (349 LOC) usa física hecha a mano: cero
  `wntr`, `epanet`, `pandapower`, `scipy` o `numpy`.
- **Impacto**: honestidad de fidelidad. `ROADMAP.md` ya cifra el proceso físico en 25-30%, pero el nombre
  del solver promete una fidelidad que el código no entrega.
- **Fix (elegir uno, no ambos)**:
  - **Opción A (honestidad barata)**: renombrar a `SimplifiedHydraulicModel` y documentar que es una
    aproximación lineal didáctica. Esfuerzo S.
  - **Opción B (fidelidad real)**: adoptar `wntr`/EPANET real para el sector agua y `pandapower` para la
    red eléctrica, detrás de la misma interfaz `solve_network()`. Esfuerzo L. Recomendado solo si la
    fidelidad física entra en los objetivos a medio plazo.
- **Criterio de aceptación**: el nombre del artefacto coincide con lo que hace; si se elige B, un caso de
  prueba compara la salida contra un resultado EPANET/pandapower conocido.

### R2-B · Sectores cáscara (gas, eléctrico, hospital)

- **Evidencia**: Gas (10.0.3.12), Eléctrico (10.0.3.13) y Hospital (10.0.3.15) tienen host en topología,
  emulador Modbus y federado HELICS, pero **no tienen modelo de proceso físico** en `physical/`. Solo
  existen modelos para agua (`plant_water.py`), transporte (`traffic.py`) y un tanque genérico
  (`icssim/plant.py`).
- **Impacto**: la afirmación de "6 sectores de ciudad" describe 3 procesos reales y 3 cáscaras. Un
  ataque a esos PLC mueve registros Modbus que no representan ninguna dinámica física.
- **Fix (elegir uno)**:
  - Modelar cada sector con un proceso físico mínimo pero real (presión de gasoducto, flujo de potencia,
    carga hospitalaria crítica) conectado a su federado HELICS.
  - O recortar el claim: documentar explícitamente qué sectores tienen física y cuáles son superficie de
    ataque de protocolo sin dinámica.
- **Criterio de aceptación**: para cada sector "con física", un cambio en un registro del PLC produce un
  cambio observable en su variable física federada.

---

## 🟦 FASE R3 — Superficie de exposición e higiene (P2)

### R3-A · Binds `0.0.0.0` parametrizables

- **Evidencia**: `plc/modbus_emulator.py:111` (default `:122`), `plc/dnp3_emulator.py:214` (default
  `:202`), `plc/opcua_emulator.py:162` (default `:148`) enlazan a `0.0.0.0`.
- **Impacto (IEC 62443-3-3 FR5)**: en Mininet los namespaces aíslan, pero si el lab corre en una red
  universitaria compartida sin namespaces, cualquier alumno alcanza los servicios OT.
- **Relación con F-05**: F-05 es "Modbus/TCP plano sin TLS ni auth" — una vulnerabilidad **de protocolo**,
  intencional. El bind `0.0.0.0` **no** es parte de F-05: se puede enlazar a la IP OT concreta del host
  sin quitar la falta de cifrado/autenticación. Esta corrección **no** toca la superficie CTF.
- **Fix**: mantener el parámetro `--host` pero cambiar el default a la IP Mininet del host (o exponer
  `BIND_ADDR`), documentando que `0.0.0.0` sigue disponible para escenarios que lo requieran.
- **Criterio de aceptación**: por defecto, `ss -ltn` muestra el bind en la IP OT del host, no en
  `0.0.0.0`; el flag para volver a `0.0.0.0` sigue existiendo.

### R3-B · `ROADMAP.md` afirma un `h_dc` inexistente

- **Evidencia**: `docs/Roadmaps/ROADMAP.md` lista "Samba AD DC (`h_dc`)" como componente existente, pero
  `network/topology.py` no contiene `addHost('h_dc')` ni configuración Samba. El escenario de
  kerberoasting (`attacker/attack_apt_sandworm_campaign.py`, fase kerberoast) ataca un DC que no existe.
- **Impacto**: documentación falsa; escenario APT sin objetivo real.
- **Fix (elegir uno)**: crear el host `h_dc` con un Samba AD DC mínimo y enlazarlo al segmento
  corporativo/DMZ; **o** corregir `ROADMAP.md` y el escenario para marcar el DC como pendiente/simulado.
- **Criterio de aceptación**: la documentación y el código concuerdan — o el DC existe y responde, o
  ningún documento lo afirma como presente.

---

## ✅ Orden de ejecución recomendado

1. **R0 completa** (A, B, C) — sin esto no hay end-to-end; es la raíz de todo.
2. **R1-C** (arnés) inmediatamente después de R0, para convertir "creemos que funciona" en "está probado".
3. **R1-A/B** (LoV real) — repara el narrativo Blue Team.
4. **R2** y **R3** en paralelo según prioridad del curso: R2 si la fidelidad física es objetivo próximo;
   R3 si el lab va a desplegarse en red compartida con alumnos.

## 🚫 Fuera de alcance de este plan (no tocar)

- F-03, F-05, F-06, F-07 permanecen abiertas por diseño.
- Nuevas capacidades del `ROADMAP.md` estratégico (TSDB, HMI industrial, SIEM ELK, redundancia DCS): no
  se adelantan aquí; este plan solo deja el terreno firme para construirlas.
