#!/usr/bin/env python3
"""network/ui_theme.py — Sistema de tokens de UI compartido (ISA-101 High-Performance HMI).

Fuente única de verdad para el aspecto del ecosistema de supervisión: el visualizador
2D (viz_server), el HMI industrial (hmi_server) y el dashboard nativo (citylab_gui).

Principio ISA-101 / High-Performance HMI: el lienzo es gris desaturado, el estado
normal se muestra en monocromo de bajo contraste que "descansa" la vista, y el color
(ámbar/rojo) se reserva para la condición anómala. En un ciberrango esto hace que la
consecuencia de un ataque (TRIP, apagón, spoofing) sea lo único que enciende la pantalla.

Restricción: la red corre en namespaces Mininet sin internet y el viz opera airgapped,
así que todo es self-contained: stacks de fuentes del sistema, cero web fonts, cero CDNs.
Los colores se definen una vez aquí; el CSS los expone como custom properties y Tkinter
los consume como constantes. Cambiar un valor aquí lo cambia en las tres superficies.
"""
from __future__ import annotations

CANVAS = '#23272e'
SURFACE = '#2b3038'
SURFACE_2 = '#313742'
LINE = '#3a4149'

FG = '#d7dce1'
FG_DIM = '#aab2bd'
FG_FAINT = '#7f8a97'

# El estado sano es gris, no verde: en ISA-101 el color es un recurso escaso para alarmas.
STATE_NORMAL = '#96a1ae'

ALARM_WARN = '#f0a000'
ALARM_WARN_BG = '#3a2d05'
ALARM_CRIT = '#ff7a72'
ALARM_CRIT_BG = '#3a0f0f'

# Azul desaturado solo para afordancia interactiva (botones, foco), nunca como decoración.
ACCENT = '#6aa2c8'
ACCENT_BG = '#1c2730'

# Fluidos de proceso en tono apagado: identifican el medio sin competir con las alarmas.
FLUID_WATER = '#527a93'

# Alias retrocompatibles para citylab_gui.py. Mapear "verde" a gris aplica la inversión
# ISA-101 en los ~31 usos del GUI sin reescribir cada call-site ni las cadenas de badge.
BG_MAIN = CANVAS
BG_CARD = SURFACE
BG_HEADER = SURFACE_2
TEXT_COLOR = FG
TEXT_MUTED = FG_DIM
ACCENT_CYAN = ACCENT
ACCENT_GREEN = STATE_NORMAL
ACCENT_RED = ALARM_CRIT
ACCENT_AMBER = ALARM_WARN
BORDER_COLOR = LINE

FONT_SANS = ('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, '
             '"Helvetica Neue", Arial, sans-serif')
FONT_MONO = ('ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, '
             '"Liberation Mono", monospace')

_TOKENS = {
    '--canvas': CANVAS,
    '--surface': SURFACE,
    '--surface-2': SURFACE_2,
    '--line': LINE,
    '--fg': FG,
    '--fg-dim': FG_DIM,
    '--fg-faint': FG_FAINT,
    '--state-normal': STATE_NORMAL,
    '--alarm-warn': ALARM_WARN,
    '--alarm-warn-bg': ALARM_WARN_BG,
    '--alarm-crit': ALARM_CRIT,
    '--alarm-crit-bg': ALARM_CRIT_BG,
    '--accent': ACCENT,
    '--accent-bg': ACCENT_BG,
    '--fluid-water': FLUID_WATER,
    '--font-sans': FONT_SANS,
    '--font-mono': FONT_MONO,
}

_ROOT = ':root{' + ''.join(f'{k}:{v};' for k, v in _TOKENS.items()) + '}'

# Componentes comunes a viz_server y hmi_server. Texto en sans para legibilidad; el mono
# se reserva a los valores numéricos de telemetría (clase .mono / .metric-val / .val).
_COMPONENTS = """
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--canvas);color:var(--fg);font-family:var(--font-sans);
  font-size:14px;line-height:1.45;padding:16px;}
.mono,.metric-val,.val{font-family:var(--font-mono);font-variant-numeric:tabular-nums;}
header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;
  gap:10px;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:16px;}
h1{font-size:1.25rem;font-weight:600;color:var(--fg);letter-spacing:0;}
.sub{color:var(--fg-dim);font-size:0.8125rem;}
.status-bar,.badge-bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;}
.badge{padding:4px 10px;border-radius:4px;font-weight:600;font-size:0.75rem;
  border:1px solid var(--line);}
.badge-ok{background:var(--canvas);color:var(--fg-dim);border-color:var(--line);}
.badge-warn{background:var(--alarm-warn-bg);color:var(--alarm-warn);
  border-color:var(--alarm-warn);}
.badge-crit{background:var(--alarm-crit-bg);color:var(--alarm-crit);
  border-color:var(--alarm-crit);animation:pulse 1.1s ease-in-out infinite;}
@keyframes pulse{50%{opacity:0.45;}}
@media (prefers-reduced-motion: reduce){.badge-crit{animation:none;}}
.btn{background:var(--accent-bg);color:var(--accent);border:1px solid var(--accent);
  padding:7px 14px;min-height:34px;border-radius:4px;cursor:pointer;
  font-family:inherit;font-size:0.8125rem;}
.btn:hover{background:var(--accent);color:var(--canvas);}
.btn-danger{color:var(--alarm-crit);border-color:var(--alarm-crit);background:transparent;}
.btn-danger:hover{background:var(--alarm-crit);color:var(--canvas);}
.btn-success{color:var(--fg-dim);border-color:var(--line);background:transparent;}
.btn-success:hover{background:var(--surface-2);color:var(--fg);}
.card{background:var(--surface);border:1px solid var(--line);border-radius:6px;
  padding:12px;display:flex;flex-direction:column;justify-content:space-between;}
.card-header{display:flex;justify-content:space-between;align-items:center;
  margin-bottom:8px;border-bottom:1px solid var(--line);padding-bottom:6px;}
.card-title{font-size:0.9rem;font-weight:600;color:var(--fg);}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
"""

SHARED_CSS = _ROOT + _COMPONENTS
