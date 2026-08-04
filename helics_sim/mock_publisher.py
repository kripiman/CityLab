#!/usr/bin/env python3
"""Local HELICS mock publisher for smoke tests.

Publishes:
 - tank/level (double)
 - breaker/trip (int)

Config via environment:
 - HELICS_FED_NAME (default: MOCK_PUB_fed)
 - HELICS_BROKER_ADDRESS (default: 127.0.0.1)
 - HELICS_BROKER_PORT (default: 23404)
 - HELICS_MAX_STEPS (default: 10)
 - HELICS_TRIP_STEP (default: 4)  # 0-based index where trip=1 is emitted
"""
from __future__ import annotations

import logging
import os
import time

import helics as h

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('mock_publisher')


def main() -> int:
    fed_name = os.environ.get('HELICS_FED_NAME', 'MOCK_PUB_fed')
    broker_address = os.environ.get('HELICS_BROKER_ADDRESS', '127.0.0.1')
    broker_port = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
    max_steps = int(os.environ.get('HELICS_MAX_STEPS', '10'))
    trip_step = int(os.environ.get('HELICS_TRIP_STEP', '4'))
    dt = 1.0

    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, 'zmq')
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f'--federates=1 --broker_address={broker_address} --brokerport={broker_port}',
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, dt)

    fed = h.helicsCreateValueFederate(fed_name, fi)
    pub_level = h.helicsFederateRegisterGlobalPublication(fed, 'tank/level', h.HELICS_DATA_TYPE_DOUBLE, '')
    pub_trip = h.helicsFederateRegisterGlobalPublication(fed, 'breaker/trip', h.HELICS_DATA_TYPE_INT, '')

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info('HELICS federate %s ready (broker=%s:%d)', fed_name, broker_address, broker_port)

    try:
        current_time = 0.0
        for i in range(max_steps):
            current_time += dt
            level = 10.0 + (0.1 * i)
            trip = 1 if i == trip_step else 0
            h.helicsPublicationPublishDouble(pub_level, float(level))
            h.helicsPublicationPublishInteger(pub_trip, int(trip))
            LOGGER.info('t=%.1f publish level=%.2f trip=%d', current_time, level, trip)
            h.helicsFederateRequestTime(fed, current_time)
            time.sleep(0.05)
    finally:
        h.helicsFederateFinalize(fed)
        LOGGER.info('HELICS federate finalized')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
