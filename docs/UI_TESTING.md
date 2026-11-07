# Pruebas de UI y regeneración de capturas (ISA-101)

Las superficies web de supervisión (Visualizador 2D `viz_server` y HMI Industrial
`hmi_server`) se verifican con un test E2E de navegador y se documentan con capturas.
Ambas cosas salen de un único script reproducible: `scripts/ui_e2e_test.py`.

El test ejercita el **camino de polling en vivo**: cambia el estado en el servidor y
comprueba que el `fetch` de la propia página lo recoge y transiciona la banda de alarmas
L1. Esto cubre lo que una captura estática no puede, porque el estado de la banda depende
de JavaScript asíncrono, no del HTML servido.

## Requisitos

El driver usa [Playwright](https://playwright.dev) sobre Chromium, aislado en un entorno
[`uv`](https://docs.astral.sh/uv/) para no tocar las dependencias system-python del
proyecto (`pymodbus`, etc.). Los servidores corren bajo el mismo intérprete y solo usan la
stdlib más el paquete local `network`.

Instalación del navegador (una sola vez, **requiere red**):

```bash
uv run --with playwright -- playwright install chromium
```

Esto es una herramienta de verificación para desarrollo. No forma parte de
`./citylab.sh test` (la suite unitaria se mantiene sin dependencias de navegador) ni del
runtime airgapped del laboratorio.

## Correr el test E2E

```bash
uv run --with playwright -- python scripts/ui_e2e_test.py
```

No necesita root, Mininet ni el laboratorio: el script levanta `viz_server` y `hmi_server`
en puertos de prueba (`18190`/`18191`), alimenta al HMI con un stub SCADA embebido
(`127.0.0.1:18192`) y lo desmantela todo al terminar. Sale con código `1` si alguna
verificación falla.

Qué comprueba (16 verificaciones):

- **Banda L1 en vivo (viz).** Gris «SIN ALARMAS ACTIVAS» en normal; tras inyectar una
  cascada IT→OT por `POST /api/viz/update`, el poll de 1 s la vuelve roja con
  «6 CRÍTICAS · 1 ADVERTENCIA» nombrando las áreas; vuelve a gris al despejar.
- **Banda L1 en vivo (HMI).** Conmuta el stub SCADA a `LOSS_OF_VIEW`; el poll de 2 s vuelve
  la banda roja nombrando `WATER`; vuelve a gris tras la recuperación.
- **Reserva de color ISA-101.** La aguja del manómetro de gas está muteada, el gauge no
  tiene arcos de semáforo, la carga/busbar están en gris y el busbar del HMI ya no es
  ámbar. Se confirma que los colores semánticos (verde del semáforo) se preservan.

## Regenerar las capturas del README

Las imágenes de `docs/img/` (`viz-normal.png`, `viz-alarm.png`, `hmi.png`) salen del mismo
script. Cuando cambie la UI, regéneralas con:

```bash
uv run --with playwright -- python scripts/ui_e2e_test.py --screenshots docs/img
```

El modo `--screenshots` corre las mismas aserciones y además captura las tres vistas
ajustadas al contenido (ancho 1460 px). La captura de alarma se toma con la cascada ya
renderizada, así que refleja el estado real de la banda, no el HTML inicial.
