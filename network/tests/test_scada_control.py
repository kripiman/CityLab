#!/usr/bin/env python3
"""network/tests/test_scada_control.py — Pruebas unitarias e integración de control SCADA y escritura Modbus."""
from __future__ import annotations

import json
import os
import threading
import time
import unittest
import urllib.request
import urllib.error
from http.server import HTTPServer
from typing import Any, Dict

from network.citylab_gui import HmiClient
from network.hmi_server import HmiRequestHandler, ThreadedHmiServer
from network.scada_server import (
    PLC_CONFIGS,
    SCADAAPIHandler,
    _determine_control_coils,
    _normalize_target,
    execute_modbus_control,
    scada_state,
)
import network.rbac as rbac_mod
from plc.tests._emulator_harness import running_modbus_server


class TestScadaControlUnit(unittest.TestCase):
    """Pruebas unitarias de resolución de target y coils."""

    def test_normalize_target(self) -> None:
        self.assertEqual(_normalize_target('water'), ['water'])
        self.assertEqual(_normalize_target('sector_water'), ['water'])
        self.assertEqual(_normalize_target('gas'), ['gas'])
        self.assertEqual(_normalize_target('sector_gas'), ['gas'])
        self.assertEqual(_normalize_target('elec'), ['elec'])
        self.assertEqual(_normalize_target('power'), ['elec'])
        self.assertEqual(_normalize_target('sector_power'), ['elec'])
        self.assertEqual(_normalize_target('transport'), ['transport'])
        self.assertEqual(_normalize_target('sector_transport'), ['transport'])
        self.assertEqual(_normalize_target('hospital'), ['hospital'])
        self.assertEqual(_normalize_target('desal'), ['desal'])
        self.assertEqual(_normalize_target('lighting'), ['lighting'])
        self.assertEqual(_normalize_target('all'), ['water', 'gas', 'elec', 'transport'])
        self.assertEqual(_normalize_target('water_pump_1'), ['water'])

    def test_determine_control_coils_water(self) -> None:
        coils, regs = _determine_control_coils('water', 'START', {})
        self.assertEqual(coils, {0: True, 1: False})
        self.assertEqual(regs, {})

        coils, regs = _determine_control_coils('water', 'STOP', {})
        self.assertEqual(coils, {0: False, 1: True})

    def test_determine_control_coils_gas(self) -> None:
        coils, regs = _determine_control_coils('gas', 'OPEN', {})
        self.assertEqual(coils, {0: True, 1: False})

        coils, regs = _determine_control_coils('gas', 'CLOSE', {})
        self.assertEqual(coils, {0: False, 1: True})

    def test_determine_control_coils_elec(self) -> None:
        coils, regs = _determine_control_coils('elec', 'CLOSE', {})
        self.assertEqual(coils, {0: True, 1: False})

        coils, regs = _determine_control_coils('elec', 'TRIP', {})
        self.assertEqual(coils, {0: False, 1: True})

    def test_determine_control_coils_transport(self) -> None:
        coils, regs = _determine_control_coils('transport', 'OPEN_GATE', {})
        self.assertEqual(coils, {0: True, 1: False})

        coils, regs = _determine_control_coils('transport', 'CLOSE_GATE', {})
        self.assertEqual(coils, {0: False, 1: True})

    def test_determine_control_coils_special_and_explicit(self) -> None:
        coils, _ = _determine_control_coils('water', 'EMERGENCY_SHUTDOWN', {})
        self.assertEqual(coils, {0: False, 1: True})

        coils, _ = _determine_control_coils('water', 'FAULT', {})
        self.assertEqual(coils, {0: True, 1: True})

        coils, _ = _determine_control_coils('water', 'RESET', {})
        self.assertEqual(coils, {0: False, 1: False})

        coils, _ = _determine_control_coils('water', 'custom', {'coils': [True, False, True]})
        self.assertEqual(coils, {0: True, 1: False, 2: True})

        coils, _ = _determine_control_coils('water', 'custom', {'coil': 1, 'value': True})
        self.assertEqual(coils, {1: True})

        _, regs = _determine_control_coils('water', 'write_register', {'address': 10, 'value': 25})
        self.assertEqual(regs, {10: 25})


class TestScadaControlIntegration(unittest.TestCase):
    """Pruebas de integración con servidores Modbus y HTTP reales."""

    _port_mb = 15031
    _port_scada = 18095
    _port_hmi = 18096

    @classmethod
    def setUpClass(cls) -> None:
        cls._orig_env = {
            k: os.environ.get(k)
            for k in ('SCADA_API_TOKEN', 'SCADA_TOKEN_OPERATOR', 'SCADA_TOKEN_ENGINEER',
                      'SCADA_TOKEN_AUDITOR', 'STRICT_AUTH')
        }
        os.environ['SCADA_API_TOKEN'] = 'SCADA_TOKEN_2026'
        os.environ['SCADA_TOKEN_OPERATOR'] = 'OP_TOKEN_2026'
        os.environ['SCADA_TOKEN_ENGINEER'] = 'ENG_TOKEN_2026'
        os.environ['SCADA_TOKEN_AUDITOR'] = 'AUD_TOKEN_2026'
        os.environ['STRICT_AUTH'] = '0'
        rbac_mod._rbac.reload()

        cls.scada_server = HTTPServer(('127.0.0.1', cls._port_scada), SCADAAPIHandler)
        cls.scada_thread = threading.Thread(target=cls.scada_server.serve_forever, daemon=True)
        cls.scada_thread.start()

        cls.orig_water_cfg = PLC_CONFIGS['water']
        PLC_CONFIGS['water'] = ('127.0.0.1', cls._port_mb)

    @classmethod
    def tearDownClass(cls) -> None:
        PLC_CONFIGS['water'] = cls.orig_water_cfg
        cls.scada_server.shutdown()
        cls.scada_server.server_close()
        for k, v in cls._orig_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        rbac_mod._rbac.reload()

    def _post(self, path: str, data: Dict[str, Any], auth: str) -> tuple[int, Dict[str, Any]]:
        url = f"http://127.0.0.1:{self._port_scada}{path}"
        payload = json.dumps(data).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        if auth:
            headers['Authorization'] = auth
        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                return resp.status, json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as err:
            body = err.read().decode('utf-8') if err.fp else '{}'
            try:
                return err.code, json.loads(body)
            except Exception:
                return err.code, {'raw': body}

    def test_live_modbus_write_start_and_stop(self) -> None:
        """Verifica que el comando START y STOP modifique físicamente los coils en el PLC Modbus."""
        with running_modbus_server(host='127.0.0.1', port=self._port_mb, plant_type='water') as (_, ctx):
            # Estado inicial del esclavo Modbus
            initial_coils = ctx[0x00].getValues(1, 0, 4)
            self.assertEqual(initial_coils[0], 0)
            self.assertEqual(initial_coils[1], 0)

            # 1. Enviar START
            status, res = self._post(
                '/api/control',
                {'action': 'START', 'target': 'water'},
                auth='Bearer engineer:ENG_TOKEN_2026'
            )
            self.assertEqual(status, 200)
            self.assertEqual(res.get('status'), 'SUCCESS')
            self.assertEqual(res.get('role'), 'engineer')
            water_detail = res.get('details', {}).get('water', {})
            self.assertTrue(water_detail.get('connected'))
            # coils_written keys can be string or int in JSON
            coils_written = {str(k): v for k, v in water_detail.get('coils_written', {}).items()}
            self.assertTrue(coils_written.get('0'))

            # Coils físicos en el PLC deben ser coil 0 = 1, coil 1 = 0
            coils_after_start = ctx[0x00].getValues(1, 0, 4)
            self.assertEqual(coils_after_start[0], 1)
            self.assertEqual(coils_after_start[1], 0)

            # 2. Enviar STOP
            status, res = self._post(
                '/api/control',
                {'action': 'STOP', 'target': 'water'},
                auth='Bearer engineer:ENG_TOKEN_2026'
            )
            self.assertEqual(status, 200)
            self.assertEqual(res.get('status'), 'SUCCESS')
            coils_after_stop = ctx[0x00].getValues(1, 0, 4)
            self.assertEqual(coils_after_stop[0], 0)
            self.assertEqual(coils_after_stop[1], 1)

    def test_rbac_roles_on_control_and_write(self) -> None:
        """Verifica permisos de rol para /api/control y /api/control/write."""
        # 1. Operator tiene acceso a /api/control (operación)
        status, res = self._post(
            '/api/control',
            {'action': 'START', 'target': 'water'},
            auth='Bearer operator:OP_TOKEN_2026'
        )
        self.assertEqual(status, 200)
        self.assertEqual(res.get('status'), 'SUCCESS')
        self.assertEqual(res.get('role'), 'operator')

        # 2. Operator no tiene acceso a /api/control/write (calibración/configuración) -> 403
        status, res = self._post(
            '/api/control/write',
            {'action': 'START', 'target': 'water'},
            auth='Bearer operator:OP_TOKEN_2026'
        )
        self.assertEqual(status, 403)
        self.assertEqual(res.get('error'), 'forbidden')

        # 3. Auditor no tiene acceso a /api/control -> 403
        status, res = self._post(
            '/api/control',
            {'action': 'START', 'target': 'water'},
            auth='Bearer auditor:AUD_TOKEN_2026'
        )
        self.assertEqual(status, 403)
        self.assertEqual(res.get('error'), 'forbidden')

        # 4. Petición sin auth -> 401
        status, res = self._post(
            '/api/control',
            {'action': 'START', 'target': 'water'},
            auth=''
        )
        self.assertEqual(status, 401)
        self.assertEqual(res.get('error'), 'unauthorized')

    def test_end_to_end_gui_client_to_modbus(self) -> None:
        """Verifica la cadena completa: HmiClient -> HmiRequestHandler -> SCADA -> Modbus Server."""
        HmiRequestHandler.engine.scada_url = f"http://127.0.0.1:{self._port_scada}"
        HmiRequestHandler.engine.auth_token = "engineer:ENG_TOKEN_2026"

        hmi_server = ThreadedHmiServer(('127.0.0.1', self._port_hmi), HmiRequestHandler)
        hmi_thread = threading.Thread(target=hmi_server.serve_forever, daemon=True)
        hmi_thread.start()

        try:
            with running_modbus_server(host='127.0.0.1', port=self._port_mb, plant_type='water') as (_, ctx):
                gui_client = HmiClient(f"http://127.0.0.1:{self._port_hmi}")

                # El cliente envía 'START' a 'water'
                ctrl_res = gui_client.send_control('START', 'water')
                self.assertTrue(ctrl_res.get('success'))
                scada_resp = ctrl_res.get('scada_response', {})
                self.assertEqual(scada_resp.get('status'), 'SUCCESS')

                # Verificar que el coil 0 del PLC es 1
                coils = ctx[0x00].getValues(1, 0, 4)
                self.assertEqual(coils[0], 1)
                self.assertEqual(coils[1], 0)

                # El cliente envía 'STOP' a 'water'
                ctrl_res = gui_client.send_control('STOP', 'water')
                self.assertTrue(ctrl_res.get('success'))
                coils = ctx[0x00].getValues(1, 0, 4)
                self.assertEqual(coils[0], 0)
                self.assertEqual(coils[1], 1)
        finally:
            hmi_server.shutdown()
            hmi_server.server_close()


if __name__ == '__main__':
    unittest.main()
