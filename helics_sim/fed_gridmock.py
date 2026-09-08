#!/usr/bin/env python3
"""HELICS federate: Grid mock for PoC
Subscribes to breaker/trip and logs events. Acts as placeholder for GridLAB-D federate.
"""
from __future__ import annotations

import time
import logging
import os

import helics as h

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('fed_gridmock')

from helics_sim.sentinel_utils import sanitize_trip_signal, sanitize_telemetry_double

POLL_INTERVAL = 1.0


def main() -> int:
    fed_name = os.environ.get('HELICS_FED_NAME', 'GRID_MOCK_fed')
    broker_address = os.environ.get('HELICS_BROKER_ADDRESS', '127.0.0.1')
    broker_port = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
    max_steps = int(os.environ.get('HELICS_MAX_STEPS', '0'))

    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f"--federates=1 --broker_address={broker_address} --brokerport={broker_port}",
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)

    fed = h.helicsCreateValueFederate(fed_name, fi)

    sub_trip = h.helicsFederateRegisterSubscription(fed, "breaker/trip", "")
    sub_gas_trip   = h.helicsFederateRegisterSubscription(fed, "gas/trip", "")
    sub_grid_trip  = h.helicsFederateRegisterSubscription(fed, "grid/trip", "")
    sub_trans_trip = h.helicsFederateRegisterSubscription(fed, "transport/trip", "")
    sub_hospital_load = h.helicsFederateRegisterSubscription(fed, "hospital/load_kw", "")

    pub_voltage = h.helicsFederateRegisterGlobalPublication(
        fed, "grid/voltage_pu", h.HELICS_DATA_TYPE_DOUBLE, "")

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info(
        'HELICS federate %s ready (broker=%s:%d)',
        fed_name,
        broker_address,
        broker_port,
    )

    try:
        current_time = 0.0
        steps = 0
        while True:
            # request time
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)

            # Sanitización de sentinels pre-publicación HELICS
            raw_w = h.helicsInputGetInteger(sub_trip)
            raw_g = h.helicsInputGetInteger(sub_gas_trip)
            raw_e = h.helicsInputGetInteger(sub_grid_trip)
            raw_t = h.helicsInputGetInteger(sub_trans_trip)
            raw_h = h.helicsInputGetDouble(sub_hospital_load)

            water_trip = sanitize_trip_signal(raw_w)
            gas_trip   = sanitize_trip_signal(raw_g)
            grid_trip  = sanitize_trip_signal(raw_e)
            trans_trip = sanitize_trip_signal(raw_t)
            hospital_kw = sanitize_telemetry_double(raw_h, default=0.0, min_val=0.0)

            any_trip = (water_trip == 1 or gas_trip == 1 or grid_trip == 1 or trans_trip == 1)
            if any_trip:
                LOGGER.warning('Received breaker trip signal [w=%d g=%d e=%d t=%d] -> switching to TRIPPED state',
                               water_trip, gas_trip, grid_trip, trans_trip)
            voltage_pu = 0.0 if any_trip else 1.0
            h.helicsPublicationPublishDouble(pub_voltage, voltage_pu)

            LOGGER.info('t=%.1f trips=[w=%d g=%d e=%d] V=%.1fpu hosp=%.1fkW',
                        current_time, water_trip, gas_trip, grid_trip, voltage_pu, hospital_kw)
            steps += 1
            if max_steps > 0 and steps >= max_steps:
                LOGGER.info('Reached HELICS_MAX_STEPS=%d, exiting', max_steps)
                break
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        LOGGER.info('Shutdown requested')
    finally:
        h.helicsFederateFinalize(fed)
        LOGGER.info('HELICS federate finalized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())