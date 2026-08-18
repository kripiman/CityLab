#!/usr/bin/env python3
"""network/tests/test_profile_resources.py — Pruebas de la instrumentación de medición."""
from __future__ import annotations

import json
import os
import tempfile
import unittest

from scripts.profile_resources import (
    Sample,
    classify,
    collect_sample,
    self_usage_mb,
    summarize,
    write_csv,
)


class TestProfileResources(unittest.TestCase):

    def test_classify_recognises_citylab_processes(self) -> None:
        self.assertEqual(classify('python3 /opt/citylab/helics_sim/fed_sis.py'), 'fed_sis')
        self.assertEqual(classify('python3 helics_sim/fed_icssim.py --plant-type elec'), 'fed_icssim')
        self.assertEqual(classify('/usr/local/bin/helics_broker -f 10 --port=23700'), 'helics_broker')
        self.assertEqual(classify('python3 network/scada_server.py'), 'scada_server')

    def test_classify_ignores_foreign_processes(self) -> None:
        self.assertIsNone(classify('/usr/bin/firefox --new-tab'))
        self.assertIsNone(classify('sshd: kripi@pts/0'))

    def test_summarize_aggregates_peak_and_mean(self) -> None:
        samples = [
            Sample(ts=1.0, component='fed_sis', pid=10, rss_mb=80.0, cpu_pct=1.0, cmdline='fed_sis.py'),
            Sample(ts=2.0, component='fed_sis', pid=10, rss_mb=100.0, cpu_pct=3.0, cmdline='fed_sis.py'),
            Sample(ts=1.0, component='fed_logger', pid=11, rss_mb=50.0, cpu_pct=0.5, cmdline='fed_logger.py'),
        ]
        summary = summarize(samples)

        self.assertEqual(summary['fed_sis']['samples'], 2)
        self.assertEqual(summary['fed_sis']['processes'], 1)
        self.assertAlmostEqual(summary['fed_sis']['rss_mb_peak'], 100.0)
        self.assertAlmostEqual(summary['fed_sis']['rss_mb_mean'], 90.0)
        self.assertAlmostEqual(summary['fed_sis']['cpu_pct_peak'], 3.0)
        self.assertAlmostEqual(summary['fed_logger']['rss_mb_peak'], 50.0)

    def test_write_csv_roundtrip(self) -> None:
        samples = [
            Sample(ts=1.5, component='fed_desal', pid=42, rss_mb=64.25, cpu_pct=2.5, cmdline='fed_desal.py'),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'sub', 'profile.csv')
            write_csv(samples, path)
            self.assertTrue(os.path.exists(path))
            with open(path, 'r', encoding='utf-8') as f:
                rows = f.read().strip().splitlines()
        self.assertEqual(rows[0], 'ts,component,pid,rss_mb,cpu_pct,cmdline')
        self.assertIn('fed_desal', rows[1])
        self.assertIn('64.25', rows[1])

    def test_self_usage_is_a_real_measurement(self) -> None:
        """resource.getrusage debe devolver un RSS positivo real, no una estimación fija."""
        rss = self_usage_mb()
        self.assertGreater(rss, 0.0)
        self.assertLess(rss, 4096.0)

    def test_collect_sample_returns_only_citylab_processes(self) -> None:
        """El muestreo real no debe clasificar procesos ajenos al laboratorio."""
        for sample in collect_sample():
            self.assertIsNotNone(classify(sample.cmdline))
            self.assertGreaterEqual(sample.rss_mb, 0.0)


if __name__ == '__main__':
    unittest.main()
