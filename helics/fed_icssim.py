#!/usr/bin/env python3
"""HELICS federate: ICSSIM PoC federate
Reads pump_running via Modbus/TCP from PLC and simulates tank. Publishes tank level
and breaker trip as HELICS publications.
"""
from __future__ import annotations

import time
import logging
from typing import Optional

import helics as h
from pymodbus.client.sync import ModbusTcpClient

from physical.icssim.plant import TankPlant

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('fed_icssim')

PLC_IP = "10.0.3.10"
PLC_PORT = 502
POLL_INTERVAL = 1.0  # seconds


def create_federate() -> h.helics_federate:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
    h.helicsFederateInfoSetCoreInitString(fi, "--federates=1")
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate("ICSSIM_fed", fi)

    pub_level = h.helicsFederateRegisterGlobalPublication(fed, "tank/level", h.HELICS_DATA_TYPE_DOUBLE, "")
    pub_trip = h.helicsFederateRegisterGlobalPublication(fed, "breaker/trip", h.HELICS_DATA_TYPE_INT, "")

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info('HELICS federate ICSSIM ready')
    return fed


def read_pump_running(client: ModbusTcpClient) -> Optional[bool]:
    try:
        rr = client.read_coils(2, 1)  # coil index 2 is pump_running (status)
        if rr and not rr.isError():
            return bool(rr.bits[0])
    except Exception:
        LOGGER.exception('Modbus read error')
    return None


def main() -> int:
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    if not client.connect():
        LOGGER.error('Cannot connect to PLC Modbus at %s:%d', PLC_IP, PLC_PORT)
        return 2

    fed = create_federate()
    plant = TankPlant()

    try:
        current_time = 0.0
        while True:
            pump_running = read_pump_running(client)
            if pump_running is None:
                LOGGER.debug('Pump status read failed; treating as OFF')
                pump_running = False

            level = plant.step(pump_running, dt=POLL_INTERVAL)
            trip = 1 if plant.needs_trip() else 0

            # publish
            h.helicsPublicationPublishDouble(h.helicsFederateGetPublication(fed, 0), float(level))
            h.helicsPublicationPublishInteger(h.helicsFederateGetPublication(fed, 1), int(trip))
            LOGGER.info('t=%.1f level=%.3f m3 pump=%s trip=%d', current_time, level, pump_running, trip)

            # advance time
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)
            time.sleep(0.01)
    except KeyboardInterrupt:
        LOGGER.info('Shutdown requested')
    finally:
        client.close()
        h.helicsFederateFinalize(fed)
        LOGGER.info('HELICS federate finalized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
