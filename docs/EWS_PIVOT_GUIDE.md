# Guía de Pivote a EWS — Autorización de Escritura Modbus (COMP-01)

> **Corrección 2026-09-15**: la versión anterior de esta guía (Opciones A y C) recomendaba que `h_ews` conectara contra `10.0.2.20:15020` (el Proxy DPI, en la zona DMZ). Eso es **inalcanzable**: el firewall nunca abre un conducto EWS→DMZ (ver §1.1). Confirmado en vivo por el propio usuario: `mininet> h_ews python3 attacker/exploit_modbus.py --host 10.0.2.20 --port 15020 start` devuelve `Connection failed to 10.0.2.20:15020` — el paquete muere en `iptables FORWARD DROP` antes de llegar siquiera al proxy. La única ruta de escritura real desde EWS es directa al PLC (§3).

## 1. Por qué el botón dice "rechazado" en vez de fallar en silencio

Desde `v0.18.1`, `network/scada_server.py:execute_modbus_control()` escribe coils Modbus reales en los PLCs. Cuando `USE_MODBUS_PROXY=1` (el default real bajo `sudo ./citylab.sh up`, fijado en `network/topology.py:507`), `scada_server.py` rutea esa escritura a través de **`network/modbus_proxy.py`**, que impone una política de origen:

```python
# network/modbus_proxy.py
ALLOWED_READ_SOURCES  = {'10.0.2.20', '10.0.4.30', '127.0.0.1'}  # h_scada, h_ews
ALLOWED_WRITE_SOURCES = {'10.0.4.30', '127.0.0.1'}               # Solo h_ews (PAW)
```

`h_scada` (`10.0.2.20`) — desde donde salen los mandos de la HMI web y de la app de escritorio (`network/citylab_gui.py`) — puede **leer** telemetría pero **no puede escribir** por esta ruta. Cuando el Proxy DPI rechaza una escritura, responde con una **Modbus Exception 0x01 (Illegal Function)**, y desde `v0.18.2` `execute_modbus_control()` detecta esa excepción explícitamente y la HMI/app nativa muestran el rechazo real en pantalla en vez de fingir éxito.

### 1.1 — Lo que el firewall realmente permite (verificado en `network/topology.py:161-167`)

```python
# 1. Allow DMZ SCADA (10.0.2.20) <-> OT Zone (10.0.3.0/24)
fw.cmd("iptables -A FORWARD -s 10.0.2.20 -d 10.0.3.0/24 -j ACCEPT")
fw.cmd("iptables -A FORWARD -s 10.0.3.0/24 -d 10.0.2.20 -j ACCEPT")

# 2. Allow EWS PAW (10.0.4.30) <-> OT Zone (10.0.3.0/24)
fw.cmd("iptables -A FORWARD -s 10.0.4.30 -d 10.0.3.0/24 -j ACCEPT")
fw.cmd("iptables -A FORWARD -s 10.0.3.0/24 -d 10.0.4.30 -j ACCEPT")
```

Con `iptables -P FORWARD DROP` como política por defecto, estas son las **únicas** dos rutas de reenvío que existen hacia/desde la zona OT (`10.0.3.0/24`). No hay ninguna regla EWS(`10.0.4.0/24`)↔DMZ(`10.0.2.0/24`), en ningún puerto. Consecuencias directas:

- `h_ews` **nunca** puede alcanzar `10.0.2.20:15020` (el Proxy DPI) ni `10.0.2.20:8080` (la API REST de SCADA) — cualquier intento se cae en el firewall, antes de que `ALLOWED_WRITE_SOURCES` entre en juego.
- Tanto `h_scada` **como** `h_ews` tienen acceso L3/L4 completo (lectura y escritura, sin filtro de puerto) a toda la zona OT. **El firewall no implementa la separación de funciones** — eso es una decisión puramente de aplicación dentro de `scada_server.py`, que solo se activa porque ese código, al tener `USE_MODBUS_PROXY=1`, elige rutear por `:15020` en vez de conectar directo al PLC. Cualquier script que conecte directo al PLC (como hacen los scripts de `attacker/`) salta esa política por completo — no porque explote nada, sino porque el firewall ya le da el camino libre.

Esto significa que **la única forma real de escribir Modbus desde `h_ews` es conectar directo al PLC en la zona OT** (`10.0.3.X:502`), no vía el Proxy DPI. El mensaje "el comando nunca llegó a alterar el actuador físico" (§ arriba) describe correctamente lo que le pasa a la HMI/app nativa (que sí están forzadas por código a pasar por el proxy) — pero no aplica a un script que conecta directo, que ese firewall nunca frena.

## 2. Estado actual: qué existe y qué no (léase antes de intentar pivotar)

Búsqueda exhaustiva en el repositorio (2026-09-15): **ningún** escenario CTF numerado (`config/scenarios/*.yml`, `docs/scenarios/*.md`) ni script de ataque (`attacker/*.py`) referencia `h_ews`, `10.0.4.30` o "PAW" como parte de su narrativa. El Escenario 18 (`docs/scenarios/scenario_18_modbus_single_coil_write.md`) escribe una coil directamente contra el PLC (`10.0.3.10:502`) desde `h_attacker`, sin pasar por SCADA ni por el proxy — de hecho, ese mismo patrón (conexión directa a OT) es exactamente lo que hace falta para escribir desde EWS también, porque la restricción del proxy solo alcanza al tráfico que pasa por él.

`h_ews` en `network/topology.py:74` es un host Mininet **sin ningún servicio propio auto-arrancado** (a diferencia de `h_scada`, que levanta `scada_server.py`, `hmi_server.py`, `viz_server.py`, `siem_pipeline.py`). No hay SSH, RDP, ni ningún daemon escuchando ahí para que un atacante remoto lo comprometa — no existe (todavía) una cadena de intrusión de red hacia EWS. Sí existe una cuenta de servicio Kerberoasteable ligada a EWS en el emulador de AD (`network/ad_dc_emulator.py`, SPN `HTTP/h_ews.citylab.local`), pero no está conectada a ningún mecanismo que otorgue acceso real al host — es infraestructura de Kerberoasting existente, no (todavía) un camino de pivote funcional.

**En resumen**: hoy, "operar como EWS" no es un escenario de Red Team con explotación de red — es una operación legítima de **consola de Mininet**, disponible para cualquiera con acceso `sudo` al laboratorio. No hay "pasos distintos según el escenario" porque ningún escenario lo contempla todavía.

## 3. Cómo operar como EWS hoy (método confirmado en vivo)

### Opción A — Escribir directo al PLC (la única ruta que el firewall realmente permite)

Desde la consola `mininet>` (o adjuntando al namespace vía `mnexec -a $(pgrep -f 'mininet:h_ews')` si estás en otra terminal):

```
mininet> h_ews python3 attacker/attack_multisector.py --sector elec --mode stop
```

Esto conecta directo a `10.0.3.13:502` (el PLC de electricidad), sin pasar por el proxy — exactamente el comportamiento verificado: `status: SUCCESS`, coils modificados. Cualquier script en `attacker/` que reciba `--host`/`--sector` apuntando a la IP OT real (ver la tabla de IPs en el README, sección "Estructura de Infraestructura") funciona igual, para cualquier sector.

### ~~Opción A anterior / Opción C anterior~~ — NO FUNCIONAN, no las uses

Las versiones previas de esta guía sugerían `--host 10.0.2.20 --port 15020` (Proxy DPI) o `curl http://10.0.2.20:8080/api/control` desde `h_ews`. Ambas apuntan a la zona DMZ, que `h_ews` no puede alcanzar (§1.1) — fallan con `Connection failed` / timeout, no con un rechazo Modbus. Se eliminaron de esta guía tras confirmarlo en un despliegue real.

### Opción B — Vía la HMI/API real, pero para eso hay que estar en `h_scada`, no en `h_ews`

El único cliente que efectivamente pasa por el Proxy DPI es `scada_server.py` mismo (porque el código lo fuerza cuando `USE_MODBUS_PROXY=1`), y ese proceso corre en `h_scada`, no en `h_ews`. Es decir: no existe hoy una forma de usar el flujo `/api/control` normal *originándolo* en `h_ews` con éxito, porque `h_ews` no puede llegar a `10.0.2.20:8080` en absoluto. Si tu objetivo es ver el flujo HTTP completo aceptado, hacelo desde `h_scada` mismo — pero ahí la escritura seguirá siendo rechazada por `ALLOWED_WRITE_SOURCES` (ese es justamente el punto de COMP-01 para ese código en particular).

## 4. Verificar que el comando fue aceptado

```bash
mininet> h_ews python3 attacker/exploit_modbus.py --host 10.0.3.10 status
```

Para ver un intento efectivamente evaluado por el Proxy DPI (no el caso EWS, que ni lo alcanza), generá tráfico desde `h_scada` y revisá `logs/modbus_dpi_audit.log` — cada intento que sí llega al proxy queda registrado con `SRC`, `FC`, `STATUS` y `REASON` (`network/modbus_proxy.py:log_audit`).

## 5. Si lo que necesitás es que el botón de la HMI funcione sin pivotear

Esa es una decisión de arquitectura distinta (aflojar `ALLOWED_WRITE_SOURCES` para incluir `10.0.2.20`, correr con `USE_MODBUS_PROXY=0`, o abrir un conducto de firewall EWS↔DMZ para que el proxy sea alcanzable como se pensó originalmente), discutida y **descartada a propósito** por el momento: erosiona la lección de segregación de funciones que el laboratorio modela, y la brecha descrita en §1.1 (firewall no segrega OT) es en sí misma material pedagógico relacionado con F-03, no un bug a ocultar. Ver el hilo de auditoría `/graphify` del 2026-09-14/15 para el razonamiento completo.

## Referencias

- `network/topology.py:161-167` — reglas de firewall reales que gobiernan qué zonas alcanzan la OT (verificado, no derivado).
- `network/modbus_proxy.py` — motor DPI y política COMP-01 (solo aplica al tráfico que efectivamente pasa por `:15020`).
- `network/scada_server.py:execute_modbus_control()` — detección y reporte de rechazo cuando el proxy sí está en el camino.
- `docs/federates/07_scada_hmi_infrastructure.md` §3 — tabla original de Function Codes por Unit ID.
- `docs/scenarios/scenario_18_modbus_single_coil_write.md` — único escenario existente que escribe una coil directo al PLC.
- `docs/scenarios/scenario_19_guided_pivoting_chain.md` — escenario de pivoteo DMZ existente; solo prueba conectividad (ping/portscan), nunca asume un servicio SSH en `h_dmz`.
