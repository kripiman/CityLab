#!/usr/bin/env python3
"""scripts/update_scenario_docs_dynamic_flags.py — Actualiza los documentos de escenario
para usar el mecanismo dinámico de flags y el evaluador scripts/run_scenario.py
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_DOC_DIR = REPO_ROOT / "docs" / "scenarios"

for doc_file in sorted(SCENARIOS_DOC_DIR.glob("scenario_*.md")):
    m = re.search(r"scenario_(\d+)_", doc_file.name)
    if not m:
        continue
    sc_id = m.group(1)

    content = doc_file.read_text(encoding="utf-8")

    # Match section heading for flags
    # E.g. "## 5. Flags del Desafío CTF..." or "## 4. Flags CTF..." or "## Flags CTF..."
    pattern = r"(## (?:\d+\. )?Flags[^\n]*\n)([\s\S]*)$"
    
    dynamic_section = (
        r"\1\n"
        f"Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.\n\n"
        f"### 🏁 Obtención y Verificación de Flags:\n"
        f"```bash\n"
        f"# Evaluar cumplimiento de objetivos y obtener flags server-side:\n"
        f"python3 scripts/run_scenario.py --id {sc_id} --check\n\n"
        f"# O mediante consulta REST al Flag Service:\n"
        f"curl -s http://10.0.2.20:8570/api/flag/mint/{sc_id}/FLAG_1\n\n"
        f"# Enviar flag obtenida para registro en el Scoreboard:\n"
        f"python3 scripts/run_scenario.py --id {sc_id} --submit \"FLAG_1{{...}}\" --team \"tu_equipo\"\n"
        f"```\n"
    )

    new_content = re.sub(pattern, dynamic_section, content)
    if new_content != content:
        doc_file.write_text(new_content, encoding="utf-8")
        print(f"✅ Actualizado docs: {doc_file.name}")
    else:
        print(f"⚠️ No se encontró sección de flags en {doc_file.name}")
