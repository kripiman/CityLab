#!/usr/bin/env python3
"""attacker/tests/test_run_scenario.py — Tests unitarios para scripts/run_scenario.py.

Verifica el orquestador principal de escenarios, validación de manifiestos y sumisión de flags
garantizando compatibilidad con paso de argumentos (argv) sin interferencia con sys.argv.
"""
import unittest

from scripts.run_scenario import main, validate_manifest


class TestRunScenario(unittest.TestCase):
    """Pruebas unitarias sobre scripts/run_scenario.py."""

    def test_validate_manifest_scenario_01(self) -> None:
        """Validar manifiesto existente de scenario_01 vía función interna."""
        valid = validate_manifest("01")
        self.assertTrue(valid)

    def test_validate_manifest_nonexistent_negative(self) -> None:
        """Validar manifiesto inexistente debe retornar False sin lanzar excepción no controlada."""
        valid = validate_manifest("999")
        self.assertFalse(valid)

    def test_main_cli_validate_manifest_success(self) -> None:
        """main() con --validate-manifest en escenario válido debe retornar código 0."""
        ret = main(["--id", "01", "--validate-manifest"])
        self.assertEqual(ret, 0)

    def test_main_cli_validate_manifest_failure(self) -> None:
        """main() con --validate-manifest en escenario inválido debe retornar código 2."""
        ret = main(["--id", "999", "--validate-manifest"])
        self.assertEqual(ret, 2)

    def test_main_cli_scorecard_unreachable_fallback(self) -> None:
        """main() con --scorecard hacia URL caída no debe romper ejecución y retorna código 1."""
        ret = main(["--scorecard", "--flag-service-url", "http://127.0.0.1:59991"])
        self.assertEqual(ret, 1)

    def test_main_cli_submit_unreachable_fallback(self) -> None:
        """main() con --submit hacia servicio caído retorna código 1 controladamente."""
        ret = main(["--id", "01", "--submit", "FLAG_1{test}", "--flag-service-url", "http://127.0.0.1:59991"])
        self.assertEqual(ret, 1)


if __name__ == '__main__':
    unittest.main()
