#!/usr/bin/env python3
"""scripts/validate_localhost.py — Comprobación de integración sin root para CI/Localhost"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Aislar base de datos del Historian de producción durante la corrida de tests
_temp_dir = tempfile.TemporaryDirectory(prefix="citylab_val_session_")
os.environ.setdefault("HISTORIAN_DB_PATH", os.path.join(_temp_dir.name, "session_historian.db"))

import unittest


def main() -> int:
    print("==========================================================================")
    print(" [CityLab] Ejecutando Validación de Integración Localhost (sin root)")
    print("==========================================================================")

    try:
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        for s in ['network/tests', 'plc/tests', 'physical/tests', 'helics_sim/tests', 'attacker/tests']:
            suite.addTests(loader.discover(s))

        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1
    finally:
        _temp_dir.cleanup()


if __name__ == '__main__':
    sys.exit(main())
