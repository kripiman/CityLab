#!/usr/bin/env python3
"""helics_sim/tests/test_phase4_federates.py — Tests de federados de Fase 4A (Desal y Lighting)"""

import unittest
from helics_sim.fed_desal import main as desal_main
from helics_sim.fed_lighting import main as lighting_main


class TestPhase4Federates(unittest.TestCase):
    def tearDown(self) -> None:
        import os
        os.environ.pop('HELICS_STANDALONE', None)
        os.environ.pop('MOCK_PLC', None)

    def test_fed_desal_standalone_execution(self) -> None:
        import os
        os.environ['HELICS_STANDALONE'] = '1'
        exit_code = desal_main()
        self.assertEqual(exit_code, 0)

    def test_fed_lighting_standalone_execution(self) -> None:
        import os
        os.environ['HELICS_STANDALONE'] = '1'
        os.environ['MOCK_PLC'] = '1'
        # argv=[] para no heredar los argumentos de pytest.
        exit_code = lighting_main([])
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()
