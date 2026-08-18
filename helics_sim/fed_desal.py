#!/usr/bin/env python3
"""helics_sim/fed_desal.py — Federado HELICS para Planta Desalinizadora de Ósmosis Inversa (Fase 4A)

Publica telemetría de desalinización (potencia kW, nivel de tanque %, permeado ppm TDS).
Suscribe a comandos de trip y corte de captación desde SCADA/PLC.
"""
from __future__ import annotations

import logging
import os
import sys
import time

from physical.water.desal_plant import DesalinationPlant

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('fed_desal')

POLL_INTERVAL = 1.0


def main() -> int:
    desal = DesalinationPlant()
    fed_name = os.environ.get('HELICS_FED_NAME', 'DESAL_fed')
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
        LOGGER.warning("[DESAL] HELICS no disponible o modo standalone activo.")

    if has_helics:
        fi = h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
        h.helicsFederateInfoSetCoreInitString(
            fi,
            f"--federates=1 --broker_address={broker_address} --brokerport={broker_port}",
        )
        h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)

        fed = h.helicsCreateValueFederate(fed_name, fi)
        sub_trip = h.helicsFederateRegisterSubscription(fed, "desal/pump_trip", "")
        pub_kw = h.helicsFederateRegisterGlobalPublication(
            fed, "desal/power_kw", h.HELICS_DATA_TYPE_DOUBLE, "")
        pub_level = h.helicsFederateRegisterGlobalPublication(
            fed, "desal/tank_level_pct", h.HELICS_DATA_TYPE_DOUBLE, "")

        h.helicsFederateEnterExecutingMode(fed)
        LOGGER.info('HELICS federate %s ready (broker=%s:%d)', fed_name, broker_address, broker_port)

    steps = 0
    current_time = 0.0

    while True:
        steps += 1
        current_time += POLL_INTERVAL

        if has_helics:
            h.helicsFederateRequestTime(fed, current_time)
            trip_cmd = h.helicsInputGetInteger(sub_trip)
            if trip_cmd == 1:
                desal.set_hp_pump(False)

        state = desal.step(dt_seconds=POLL_INTERVAL)

        if has_helics:
            h.helicsPublicationPublishDouble(pub_kw, state['power_kw'])
            h.helicsPublicationPublishDouble(pub_level, state['tank_level_pct'])

        LOGGER.info(
            't=%.1f Desal RO: Pump=%s Tank=%.1f%% TDS=%.1fppm Power=%.1fkW',
            current_time,
            "ON" if state['hp_pump_on'] else "OFF",
            state['tank_level_pct'],
            state['permeate_tds_ppm'],
            state['power_kw']
        )

        if max_steps > 0 and steps >= max_steps:
            LOGGER.info("[DESAL] Límite max_steps (%d) alcanzado. Finalizando.", max_steps)
            break

        time.sleep(0.01)

    if has_helics:
        h.helicsFederateFinalize(fed)
        h.helicsFederateFree(fed)

    return 0


if __name__ == '__main__':
    sys.exit(main())
