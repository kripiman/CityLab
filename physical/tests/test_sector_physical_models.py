#!/usr/bin/env python3
"""physical/tests/test_sector_physical_models.py — Unit tests para modelos físicos de gas, eléctrico y hospital"""
from __future__ import annotations

import unittest
from physical.gas.plant_gas import GasPipelinePlant
from physical.elec.grid_elec import ElectricalSubstationGrid
from physical.hospital.hospital_load import HospitalPowerSystem


class TestSectorPhysicalModels(unittest.TestCase):

    def test_gas_pipeline_dynamics(self) -> None:
        plant = GasPipelinePlant()
        p0 = plant.pressure_bar
        plant.compressor_running = False
        p1 = plant.step(dt_s=10.0)
        self.assertLess(p1, p0)

    def test_grid_substation_breaker_trip(self) -> None:
        grid = ElectricalSubstationGrid()
        f0 = grid.frequency_hz
        grid.breaker_closed = False
        f1 = grid.step(dt_s=2.0)
        self.assertLess(f1, f0)
        self.assertLess(grid.bus_voltage_kv, 110.0)

    def test_hospital_ups_drain(self) -> None:
        hosp = HospitalPowerSystem()
        hosp.grid_available = False
        soc1 = hosp.step(dt_s=100.0)
        self.assertLess(soc1, 100.0)


if __name__ == '__main__':
    unittest.main()
