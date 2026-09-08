#!/usr/bin/env python3
"""helics_sim/fed_lighting.py — Federado HELICS para Alumbrado Público Inteligente (Fase 4A)

Publica `lighting/power_kw` (potencia activa consumida).

Fuentes de mando sobre el nivel de dimmer, en orden de precedencia:
  1. `grid/lighting_trip` (HELICS, publicado por fed_icssim rama elec) — disparo de red: 0 %.
  2. Coil 4 del PLC de alumbrado (`h_lighting` 10.0.3.17:502) — apagón de alumbrado
     comandado por Modbus. Es la superficie de ataque real del sector: escribir ese coil
     apaga el alumbrado público. Con `--mock-plc` / `MOCK_PLC=1` no se consulta el PLC.
  3. Control automático por fotocélula del propio modelo físico.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from typing import Any, Optional

try:
    from pymodbus.client import ModbusTcpClient
except ImportError:  # pymodbus 2.x
    from pymodbus.client.sync import ModbusTcpClient

from physical.elec.smart_lighting import SmartLightingSystem

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('fed_lighting')

POLL_INTERVAL = 1.0
DEFAULT_PLC_IP = '10.0.3.17'
BLACKOUT_COIL = 4  # coil de mando "apagón de alumbrado" en el PLC de alumbrado


def read_blackout_command(client: Optional[Any]) -> bool:
    """Lee el coil de apagón del PLC de alumbrado. False si no hay PLC o falla la lectura."""
    if client is None:
        return False
    try:
        rr = client.read_coils(BLACKOUT_COIL, 1)
        if rr and not rr.isError():
            return bool(rr.bits[0])
    except Exception:
        LOGGER.debug('Modbus read error en coil de apagón', exc_info=True)
    return False


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description='HELICS Smart Lighting Federate')
    parser.add_argument('--plc-ip', default='', help='IP Modbus del PLC de alumbrado')
    parser.add_argument('--plc-port', type=int, default=502, help='Puerto Modbus del PLC')
    parser.add_argument('--mock-plc', action='store_true', help='No consultar el PLC por Modbus')
    # argv=None -> lee sys.argv (lanzamiento CLI real); una lista explícita (p. ej. [] en tests)
    # evita que se consuma el argv del proceso anfitrión, como el de pytest.
    args = parser.parse_args(argv)

    lighting = SmartLightingSystem()
    fed_name = os.environ.get('HELICS_FED_NAME', 'LIGHTING_fed')
    broker_address = os.environ.get('HELICS_BROKER_ADDRESS', '127.0.0.1')
    broker_port = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
    max_steps = int(os.environ.get('HELICS_MAX_STEPS', '5'))

    standalone_mode = os.environ.get('HELICS_STANDALONE', '0') == '1'
    try:
        if standalone_mode:
            raise ImportError("Modo standalone forzado por env var")
        import helics as h
        has_helics = True
    except ImportError:
        has_helics = False
        LOGGER.warning("[LIGHTING] HELICS no disponible o modo standalone activo.")

    if has_helics:
        fi = h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
        h.helicsFederateInfoSetCoreInitString(
            fi,
            f"--federates=1 --broker_address={broker_address} --brokerport={broker_port}",
        )
        h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)

        fed = h.helicsCreateValueFederate(fed_name, fi)
        sub_trip = h.helicsFederateRegisterSubscription(fed, "grid/lighting_trip", "")
        pub_kw = h.helicsFederateRegisterGlobalPublication(
            fed, "lighting/power_kw", h.HELICS_DATA_TYPE_DOUBLE, "")

        h.helicsFederateEnterExecutingMode(fed)
        LOGGER.info('HELICS federate %s ready (broker=%s:%d)', fed_name, broker_address, broker_port)

    use_mock = args.mock_plc or os.environ.get('MOCK_PLC', '0') == '1'
    client = None
    if not use_mock:
        plc_ip = args.plc_ip or os.environ.get('PLC_IP', DEFAULT_PLC_IP)
        try:
            client = ModbusTcpClient(plc_ip, port=args.plc_port)
            client.connect()
            LOGGER.info('[LIGHTING] PLC Modbus en %s:%d (coil %d = apagón)',
                        plc_ip, args.plc_port, BLACKOUT_COIL)
        except Exception:
            LOGGER.warning('[LIGHTING] Sin PLC Modbus en %s:%d; solo control por fotocélula',
                           plc_ip, args.plc_port)
            client = None

    steps = 0
    current_time = 0.0

    while True:
        steps += 1
        current_time += POLL_INTERVAL

        if has_helics:
            h.helicsFederateRequestTime(fed, current_time)

        if has_helics and h.helicsInputGetInteger(sub_trip) == 1:
            lighting.set_dimming(0.0, override=True)
        elif read_blackout_command(client):
            LOGGER.warning('[LIGHTING] Apagón comandado por Modbus (coil %d)', BLACKOUT_COIL)
            lighting.set_dimming(0.0, override=True)

        state = lighting.step(dt_seconds=POLL_INTERVAL, ambient_lux=10.0)  # Simulando noche

        if has_helics:
            h.helicsPublicationPublishDouble(pub_kw, state['active_power_kw'])

        LOGGER.info(
            't=%.1f Smart Lighting: Dimmer=%.1f%% Power=%.2fkW Fixtures=%d (Failed=%d)',
            current_time,
            state['dimming_pct'],
            state['active_power_kw'],
            state['total_fixtures'],
            state['failed_fixtures']
        )

        if max_steps > 0 and steps >= max_steps:
            LOGGER.info("[LIGHTING] Límite max_steps (%d) alcanzado. Finalizando.", max_steps)
            break

        time.sleep(0.01)

    if has_helics:
        h.helicsFederateFinalize(fed)
        h.helicsFederateFree(fed)
    if client is not None:
        client.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
