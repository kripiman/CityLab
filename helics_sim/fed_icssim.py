#!/usr/bin/env python3
"""HELICS federate: ICSSIM PoC federate
Reads pump_running via Modbus/TCP from PLC and simulates tank. Publishes tank level
and breaker trip as HELICS publications.
"""
from __future__ import annotations

import time
import logging
from typing import Optional
import os

import helics as h
from pymodbus.client.sync import ModbusTcpClient

from physical.icssim.plant import TankPlant

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('fed_icssim')

PLC_IP = "10.0.3.10"
PLC_PORT = 502
POLL_INTERVAL = 1.0  # seconds
FED_NAME = os.environ.get("HELICS_FED_NAME", "ICSSIM_fed")
BROKER_ADDRESS = os.environ.get("HELICS_BROKER_ADDRESS", "127.0.0.1")
BROKER_PORT = int(os.environ.get("HELICS_BROKER_PORT", "23404"))


def create_federate() -> h.helics_federate:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f"--federates=1 --broker_address={BROKER_ADDRESS} --brokerport={BROKER_PORT}",
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate(FED_NAME, fi)

    pub_level = h.helicsFederateRegisterGlobalPublication(fed, "tank/level", h.HELICS_DATA_TYPE_DOUBLE, "")
    pub_trip = h.helicsFederateRegisterGlobalPublication(fed, "breaker/trip", h.HELICS_DATA_TYPE_INT, "")

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info("HELICS federate %s ready (broker=%s:%d)", FED_NAME, BROKER_ADDRESS, BROKER_PORT)
    return fed


def read_pump_running(client: ModbusTcpClient) -> Optional[bool]:
    try:
        if not client.is_socket_open():
            client.connect()
        rr = client.read_coils(2, 1)  # coil index 2 is pump_running (status)
        if rr and not rr.isError():
            return bool(rr.bits[0])
    except Exception:
        LOGGER.exception('Modbus read error')
    return None


def main() -> int:
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    LOGGER.info('Connecting to PLC Modbus at %s:%d...', PLC_IP, PLC_PORT)
    
    connected = False
    # Intentar conexión durante 30 segundos (esperando a que Mininet/PLC inicien)
    for attempt in range(30):
        try:
            if client.connect():
                connected = True
                break
        except Exception:
            pass
        LOGGER.warning('Attempt %d: Connection to PLC failed, retrying in 1s...', attempt + 1)
        time.sleep(1)

    if not connected:
        LOGGER.error('Cannot connect to PLC Modbus at %s:%d after 30 seconds', PLC_IP, PLC_PORT)
        return 2

    LOGGER.info('Successfully connected to PLC Modbus.')
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
            h.helicsPublicationPublishDouble(h.helicsFederateGetPublication(fed, "tank/level"), float(level))
            h.helicsPublicationPublishInteger(h.helicsFederateGetPublication(fed, "breaker/trip"), int(trip))
            LOGGER.info('t=%.1f level=%.3f m3 pump=%s trip=%d', current_time, level, pump_running, trip)

            # advance time
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        LOGGER.info('Shutdown requested')
    finally:
        client.close()
        h.helicsFederateFinalize(fed)
        LOGGER.info('HELICS federate finalized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
