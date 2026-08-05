#!/usr/bin/env python3
"""HELICS federate: Transport Sector — Semáforos urbanos e índice de congestión.

Suscribe:
  grid/voltage_pu (double) — Tensión de la red eléctrica

Publica:
  transport/congestion (double) — Índice de congestión vehicular [0.0 - 1.0]
  transport/trip       (int)    — 1 si la congestión supera 0.80 (colapso vial)
"""
from __future__ import annotations

import argparse
import logging
import os
import time
from typing import Optional

import helics as h
try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    from pymodbus.client.sync import ModbusTcpClient

from physical.transport.traffic import TrafficLightIntersection

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][FED_TRANSPORT] %(message)s')
LOGGER = logging.getLogger('fed_transport')

POLL_INTERVAL = 1.0  # s
FED_NAME = os.environ.get('HELICS_FED_NAME', 'TRANSPORT_fed')
BROKER_ADDRESS = os.environ.get('HELICS_BROKER_ADDRESS', '127.0.0.1')
BROKER_PORT = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
MAX_STEPS = int(os.environ.get('HELICS_MAX_STEPS', '0'))


def create_federate() -> tuple[h.helics_federate, h.helics_publication, h.helics_publication, h.helics_input]:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, 'zmq')
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f'--federates=1 --broker_address={BROKER_ADDRESS} --brokerport={BROKER_PORT}',
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate(FED_NAME, fi)

    pub_congestion = h.helicsFederateRegisterGlobalPublication(
        fed, 'transport/congestion', h.HELICS_DATA_TYPE_DOUBLE, ''
    )
    pub_trip = h.helicsFederateRegisterGlobalPublication(
        fed, 'transport/trip', h.HELICS_DATA_TYPE_INT, ''
    )
    sub_voltage = h.helicsFederateRegisterSubscription(fed, 'grid/voltage_pu', '')

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info('TRANSPORT federate ready (broker=%s:%d)', BROKER_ADDRESS, BROKER_PORT)
    return fed, pub_congestion, pub_trip, sub_voltage


def main() -> int:
    parser = argparse.ArgumentParser(description="HELICS Transport Federate")
    parser.add_argument("--plc-ip", default=os.environ.get("PLC_IP", "10.0.3.14"))
    parser.add_argument("--plc-port", type=int, default=int(os.environ.get("PLC_PORT", "502")))
    parser.add_argument("--mock-plc", action="store_true")
    args = parser.parse_args()

    use_mock = args.mock_plc or os.environ.get("MOCK_PLC", "0") == "1"
    client: Optional[ModbusTcpClient] = None

    if not use_mock:
        LOGGER.info('Connecting to Transport PLC at %s:%d...', args.plc_ip, args.plc_port)
        client = ModbusTcpClient(args.plc_ip, port=args.plc_port, timeout=2.0)
        connected = False
        for _ in range(5):
            if client.connect():
                connected = True
                break
            time.sleep(0.5)

        if not connected:
            if os.environ.get("MOCK_FALLBACK", "0") == "1":
                LOGGER.warning("Transport PLC connection failed; falling back to mock mode.")
                use_mock = True
                client = None
            else:
                LOGGER.error("Cannot connect to Transport PLC at %s:%d", args.plc_ip, args.plc_port)
                return 2

    fed, pub_congestion, pub_trip, sub_voltage = create_federate()
    plant = TrafficLightIntersection()

    try:
        current_time = 0.0
        steps = 0
        while True:
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)

            emergency_override = False
            if client is not None:
                try:
                    rr = client.read_coils(1, 1)  # Coil 1 = Emergency Corridor
                    if rr and not rr.isError():
                        emergency_override = bool(rr.bits[0])
                except Exception as exc:
                    LOGGER.debug('Modbus read failed: %s', exc)

            power_ok = True
            if h.helicsInputIsUpdated(sub_voltage):
                v_pu = h.helicsInputGetDouble(sub_voltage)
                power_ok = (v_pu >= 0.85)

            phase, congestion = plant.step(emergency_override, power_available=power_ok, dt=POLL_INTERVAL)
            trip = 1 if plant.needs_trip() else 0

            h.helicsPublicationPublishDouble(pub_congestion, float(congestion))
            h.helicsPublicationPublishInteger(pub_trip, int(trip))

            LOGGER.info('t=%.1fs phase=%s congestion=%.2f power_ok=%s trip=%d',
                        current_time, phase, congestion, power_ok, trip)

            steps += 1
            if MAX_STEPS > 0 and steps >= MAX_STEPS:
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        LOGGER.info('Shutdown requested')
    finally:
        if client is not None:
            client.close()
        h.helicsFederateFinalize(fed)
        LOGGER.info('TRANSPORT federate finalized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
