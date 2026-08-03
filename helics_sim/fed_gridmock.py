#!/usr/bin/env python3
"""HELICS federate: Grid mock for PoC
Subscribes to breaker/trip and logs events. Acts as placeholder for GridLAB-D federate.
"""
from __future__ import annotations

import time
import logging

import helics as h

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('fed_gridmock')

POLL_INTERVAL = 1.0


def main() -> int:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
    h.helicsFederateInfoSetCoreInitString(fi, "--federates=1")
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)

    fed = h.helicsCreateValueFederate("GRID_MOCK_fed", fi)

    sub_trip = h.helicsFederateRegisterSubscription(fed, "breaker/trip", "")

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info('HELICS federate GRID_MOCK ready')

    try:
        current_time = 0.0
        while True:
            # request time
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)

            # read subscription
            val = h.helicsInputGetInteger(sub_trip)
            if val != 0:
                LOGGER.warning('Received breaker trip signal at t=%.1f: %d', current_time, val)
            else:
                LOGGER.info('No trip at t=%.1f', current_time)
            time.sleep(0.01)
    except KeyboardInterrupt:
        LOGGER.info('Shutdown requested')
    finally:
        h.helicsFederateFinalize(fed)
        LOGGER.info('HELICS federate finalized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())