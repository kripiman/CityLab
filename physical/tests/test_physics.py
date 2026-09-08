#!/usr/bin/env python3
"""physical/tests/test_physics.py — Pruebas de integración del motor físico EPANET (Fase 4)"""
from __future__ import annotations

import unittest
from physical.water.epanet_solver import EpanetHydraulicSolver, PipeConfig, PumpConfig
from physical.water.plant_water import TwoStageWaterPlant


class TestPhysicsEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.solver = EpanetHydraulicSolver()

    def test_epanet_head_loss(self) -> None:
        hf_zero = self.solver.compute_head_loss(0.0)
        self.assertEqual(hf_zero, 0.0)
        
        hf_flow = self.solver.compute_head_loss(1.0)
        self.assertGreater(hf_flow, 0.0)

    def test_epanet_pump_curve(self) -> None:
        head_off = self.solver.compute_pump_head(0.0)
        self.assertEqual(head_off, 50.0)
        
        head_run = self.solver.compute_pump_head(1.0)
        self.assertLess(head_run, head_off)

    def test_epanet_network_solver(self) -> None:
        flow, pressure, hf = self.solver.solve_network(pump_active=True, requested_flow_m3_s=1.0)
        self.assertEqual(flow, 1.0)
        self.assertGreater(pressure, 0.0)
        self.assertGreater(hf, 0.0)

    def test_water_plant_integration_with_epanet(self) -> None:
        plant = TwoStageWaterPlant()
        t1_init, t2_init = plant.t1_level_m3, plant.t2_level_m3
        
        # Step with pumps ON and power available
        t1_next, t2_next = plant.step(p1_cmd=True, p2_cmd=True, power_available=True, dt=1.0)
        self.assertIsNotNone(t1_next)
        self.assertIsNotNone(t2_next)
        self.assertIsInstance(t1_next, float)
        self.assertIsInstance(t2_next, float)
        self.assertGreater(t1_next, 0.0)
        self.assertGreater(t2_next, 0.0)

        # Step without power — levels decay or stay constant minus demand
        t1_off, t2_off = plant.step(p1_cmd=True, p2_cmd=True, power_available=False, dt=1.0)
        self.assertLessEqual(t2_off, t2_next)


if __name__ == '__main__':
    unittest.main()
