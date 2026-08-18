#!/usr/bin/env python3
"""scripts/profile_resources.py — Instrumentación de medición de recursos de CityLab.

Sustituye las estimaciones de diseño de la documentación (`~N MB`) por mediciones reales
de RSS y CPU de los procesos vivos del laboratorio.

Uso:
    ./citylab.sh profile                    # muestreo por defecto (5 muestras, 1 s)
    ./citylab.sh profile --samples 30 --interval 2.0
    PYTHONPATH=. python3 scripts/profile_resources.py --json

Salidas:
    logs/resource_profile.csv       — una fila por (muestra, proceso)
    logs/resource_profile_summary.* — resumen por componente (texto y/o JSON)

Notas de fidelidad:
  - Mide únicamente los procesos que estén corriendo en el momento del muestreo. Si el
    laboratorio no está desplegado, el informe sale vacío y así se reporta: no inventa cifras.
  - `psutil` es la vía preferente. Sin psutil se cae a `/proc/<pid>` (Linux) y a
    `resource.getrusage` para el propio proceso, que es lo que garantiza la biblioteca estándar.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import resource
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:  # pragma: no cover - depende del entorno
    HAS_PSUTIL = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

#: Clasificación de procesos de CityLab: etiqueta -> patrón sobre la línea de comandos.
COMPONENT_PATTERNS = (
    ('helics_broker',   r'helics_broker'),
    ('fed_icssim',      r'fed_icssim\.py'),
    ('fed_transport',   r'fed_transport\.py'),
    ('fed_hospital',    r'fed_hospital\.py'),
    ('fed_logger',      r'fed_logger\.py'),
    ('fed_desal',       r'fed_desal\.py'),
    ('fed_lighting',    r'fed_lighting\.py'),
    ('fed_sis',         r'fed_sis\.py'),
    ('gridlabd_fed',    r'gridlabd_federate\.py'),
    ('modbus_emulator', r'modbus_emulator\.py'),
    ('dnp3_emulator',   r'dnp3_emulator\.py'),
    ('iec61850_emulator', r'iec61850_emulator\.py'),
    ('opcua_emulator',  r'opcua_emulator\.py'),
    ('honeypot',        r'honeypot_server\.py'),
    ('ad_dc_emulator',  r'ad_dc_emulator\.py'),
    ('scada_server',    r'scada_server\.py'),
    ('hmi_server',      r'hmi_server\.py'),
    ('viz_server',      r'viz_server\.py'),
    ('siem_pipeline',   r'siem_pipeline\.py'),
    ('sdn_controller',  r'sdn_controller\.py'),
    ('mininet',         r'\bmn\b|mininet'),
    ('ovs',             r'ovs-vswitchd|ovsdb-server'),
)


@dataclass
class Sample:
    """Una medición puntual de un proceso."""
    ts: float
    component: str
    pid: int
    rss_mb: float
    cpu_pct: float
    cmdline: str


def classify(cmdline: str) -> Optional[str]:
    """Devuelve la etiqueta de componente CityLab para una línea de comandos, o None."""
    for label, pattern in COMPONENT_PATTERNS:
        if re.search(pattern, cmdline):
            return label
    return None


def _iter_processes_psutil() -> List[Dict[str, Any]]:
    procs = []
    for proc in psutil.process_iter(['pid', 'cmdline', 'memory_info', 'cpu_percent']):
        try:
            info = proc.info
            cmdline = ' '.join(info.get('cmdline') or [])
            if not cmdline:
                continue
            mem = info.get('memory_info')
            procs.append({
                'pid': info['pid'],
                'cmdline': cmdline,
                'rss_mb': (mem.rss / (1024 * 1024)) if mem else 0.0,
                'cpu_pct': info.get('cpu_percent') or 0.0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs


def _iter_processes_proc() -> List[Dict[str, Any]]:
    """Fallback sin psutil: lee /proc directamente (Linux)."""
    procs = []
    page_size = os.sysconf('SC_PAGE_SIZE') if hasattr(os, 'sysconf') else 4096
    for entry in os.listdir('/proc'):
        if not entry.isdigit():
            continue
        pid = int(entry)
        try:
            with open(f'/proc/{pid}/cmdline', 'rb') as f:
                cmdline = f.read().replace(b'\x00', b' ').decode('utf-8', 'replace').strip()
            if not cmdline:
                continue
            with open(f'/proc/{pid}/statm', 'r', encoding='utf-8') as f:
                rss_pages = int(f.read().split()[1])
        except (OSError, ValueError, IndexError):
            continue
        procs.append({
            'pid': pid,
            'cmdline': cmdline,
            'rss_mb': (rss_pages * page_size) / (1024 * 1024),
            'cpu_pct': 0.0,  # sin psutil no se mide CPU por proceso
        })
    return procs


def collect_sample() -> List[Sample]:
    """Toma una muestra de todos los procesos CityLab vivos."""
    raw = _iter_processes_psutil() if HAS_PSUTIL else _iter_processes_proc()
    ts = time.time()
    samples: List[Sample] = []
    for proc in raw:
        component = classify(proc['cmdline'])
        if component is None:
            continue
        samples.append(Sample(
            ts=ts,
            component=component,
            pid=proc['pid'],
            rss_mb=round(proc['rss_mb'], 2),
            cpu_pct=round(proc['cpu_pct'], 1),
            cmdline=proc['cmdline'][:180],
        ))
    return samples


def summarize(samples: List[Sample]) -> Dict[str, Dict[str, Any]]:
    """Agrega las muestras por componente."""
    by_component: Dict[str, Dict[str, Any]] = {}
    for s in samples:
        entry = by_component.setdefault(s.component, {
            'component': s.component,
            'samples': 0,
            'rss_mb_peak': 0.0,
            'rss_mb_total': 0.0,
            'cpu_pct_peak': 0.0,
            'pids': [],
        })
        entry['samples'] += 1
        entry['rss_mb_total'] += s.rss_mb
        entry['rss_mb_peak'] = max(entry['rss_mb_peak'], s.rss_mb)
        entry['cpu_pct_peak'] = max(entry['cpu_pct_peak'], s.cpu_pct)
        if s.pid not in entry['pids']:
            entry['pids'].append(s.pid)

    for entry in by_component.values():
        entry['rss_mb_mean'] = round(entry['rss_mb_total'] / entry['samples'], 2)
        entry['rss_mb_peak'] = round(entry['rss_mb_peak'], 2)
        entry['processes'] = len(entry['pids'])
        del entry['rss_mb_total']
    return by_component


def self_usage_mb() -> float:
    """RSS máximo del propio proceso vía `resource.getrusage` (stdlib, sin dependencias)."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # En Linux ru_maxrss viene en kilobytes.
    return round(usage.ru_maxrss / 1024.0, 2)


def write_csv(samples: List[Sample], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='\n', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ts', 'component', 'pid', 'rss_mb', 'cpu_pct', 'cmdline'])
        for s in samples:
            writer.writerow([f"{s.ts:.3f}", s.component, s.pid, f"{s.rss_mb:.2f}",
                             f"{s.cpu_pct:.1f}", s.cmdline])


def render_report(summary: Dict[str, Dict[str, Any]], total_peak_mb: float,
                  budget_gb: float, sampler: str) -> str:
    lines = []
    lines.append('=' * 78)
    lines.append('CityLab — Medición real de recursos (no estimación de diseño)')
    lines.append(f'Muestreo: {sampler}')
    lines.append('=' * 78)
    if not summary:
        lines.append('')
        lines.append('Ningún proceso de CityLab en ejecución: no hay nada que medir.')
        lines.append('Despliega el laboratorio (`sudo ./citylab.sh up`) o lanza la co-simulación')
        lines.append('(`./citylab.sh smoke`) y vuelve a ejecutar esta medición.')
        return '\n'.join(lines)

    lines.append('')
    lines.append(f"{'Componente':<20}{'Procs':>6}{'RSS medio MB':>15}{'RSS pico MB':>14}{'CPU pico %':>12}")
    lines.append('-' * 78)
    for name in sorted(summary, key=lambda k: summary[k]['rss_mb_peak'], reverse=True):
        e = summary[name]
        lines.append(f"{name:<20}{e['processes']:>6}{e['rss_mb_mean']:>15.2f}"
                     f"{e['rss_mb_peak']:>14.2f}{e['cpu_pct_peak']:>12.1f}")
    lines.append('-' * 78)
    budget_mb = budget_gb * 1024
    pct = (total_peak_mb / budget_mb * 100) if budget_mb else 0.0
    lines.append(f"{'TOTAL (pico)':<20}{'':>6}{'':>15}{total_peak_mb:>14.2f}")
    lines.append('')
    lines.append(f'Presupuesto documentado: {budget_gb:.0f} GB ({budget_mb:.0f} MB) — '
                 f'uso medido: {pct:.1f} %')
    if not HAS_PSUTIL:
        lines.append('AVISO: psutil no disponible; CPU por proceso no medida (RSS sí, vía /proc).')
    return '\n'.join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description='Medición real de RAM/CPU de CityLab')
    parser.add_argument('--samples', type=int, default=5, help='Número de muestras')
    parser.add_argument('--interval', type=float, default=1.0, help='Segundos entre muestras')
    parser.add_argument('--json', action='store_true', help='Emitir el resumen en JSON por stdout')
    parser.add_argument('--budget-gb', type=float, default=8.0,
                        help='Presupuesto documentado contra el que comparar')
    parser.add_argument('--csv', default=os.path.join(LOG_DIR, 'resource_profile.csv'),
                        help='Ruta del CSV de muestras')
    args = parser.parse_args(argv)

    all_samples: List[Sample] = []
    for i in range(max(1, args.samples)):
        all_samples.extend(collect_sample())
        if i < args.samples - 1:
            time.sleep(max(0.0, args.interval))

    summary = summarize(all_samples)

    # Pico total: mayor suma de RSS observada en una misma marca de tiempo.
    by_ts: Dict[float, float] = {}
    for s in all_samples:
        by_ts[s.ts] = by_ts.get(s.ts, 0.0) + s.rss_mb
    total_peak_mb = round(max(by_ts.values()), 2) if by_ts else 0.0

    write_csv(all_samples, args.csv)

    sampler = (f'{args.samples} muestras cada {args.interval:.1f} s '
               f'({"psutil " + psutil.__version__ if HAS_PSUTIL else "/proc (sin psutil)"})')
    payload = {
        'sampler': sampler,
        'psutil': HAS_PSUTIL,
        'budget_gb': args.budget_gb,
        'total_peak_mb': total_peak_mb,
        'profiler_self_rss_mb': self_usage_mb(),
        'components': summary,
    }

    summary_json = os.path.join(LOG_DIR, 'resource_profile_summary.json')
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(summary_json, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        report = render_report(summary, total_peak_mb, args.budget_gb, sampler)
        print(report)
        with open(os.path.join(LOG_DIR, 'resource_profile_summary.txt'), 'w', encoding='utf-8') as f:
            f.write(report + '\n')

    return 0


if __name__ == '__main__':
    sys.exit(main())
