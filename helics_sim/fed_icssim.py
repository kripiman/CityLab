#!/usr/bin/env python3
"""HELICS federate: ICSSIM PoC federate
Reads pump_running via Modbus/TCP from PLC and simulates tank. Publishes tank level
and breaker trip as HELICS publications.
"""
from __future__ import annotations

import argparse
import logging
import time
from typing import Optional, Any
import os

import helics as h
try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    from pymodbus.client.sync import ModbusTcpClient

from physical.icssim.plant import GasPlant, ElecPlant
from physical.water.plant_water import TwoStageWaterPlant

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('fed_icssim')

POLL_INTERVAL = 1.0  # seconds
BROKER_ADDRESS = os.environ.get("HELICS_BROKER_ADDRESS", "127.0.0.1")
BROKER_PORT = int(os.environ.get("HELICS_BROKER_PORT", "23404"))


def create_federate(fed_name: str, plant_type: str) -> tuple[h.helics_federate, Any, Any, Optional[Any], Optional[Any]]:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f"--federates=1 --broker_address={BROKER_ADDRESS} --brokerport={BROKER_PORT}",
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate(fed_name, fi)

    pub_t1: Optional[Any] = None  # solo usado por water

    if plant_type == "gas":
        pub_val = h.helicsFederateRegisterGlobalPublication(fed, "gas/pressure", h.HELICS_DATA_TYPE_DOUBLE, "")
        pub_trip = h.helicsFederateRegisterGlobalPublication(fed, "gas/trip", h.HELICS_DATA_TYPE_INT, "")
        sub_input = h.helicsFederateRegisterSubscription(fed, "grid/voltage_pu", "")
    elif plant_type == "elec":
        pub_val = h.helicsFederateRegisterGlobalPublication(fed, "grid/frequency", h.HELICS_DATA_TYPE_DOUBLE, "")
        pub_trip = h.helicsFederateRegisterGlobalPublication(fed, "grid/trip", h.HELICS_DATA_TYPE_INT, "")
        sub_input = h.helicsFederateRegisterSubscription(fed, "hospital/load_kw", "")
        pub_t1 = h.helicsFederateRegisterSubscription(fed, "gas/trip", "")  # reutilizado como sub_gas_trip para elec
    else:  # water
        pub_val  = h.helicsFederateRegisterGlobalPublication(fed, "water/t2_level", h.HELICS_DATA_TYPE_DOUBLE, "")
        pub_t1   = h.helicsFederateRegisterGlobalPublication(fed, "water/t1_level", h.HELICS_DATA_TYPE_DOUBLE, "")
        pub_trip = h.helicsFederateRegisterGlobalPublication(fed, "breaker/trip", h.HELICS_DATA_TYPE_INT, "")
        sub_input = h.helicsFederateRegisterSubscription(fed, "grid/voltage_pu", "")

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info("HELICS federate %s [%s] ready (broker=%s:%d)", fed_name, plant_type, BROKER_ADDRESS, BROKER_PORT)
    return fed, pub_val, pub_trip, sub_input, pub_t1


def read_actuator_running(client: ModbusTcpClient) -> Optional[bool]:
    try:
        rr = client.read_coils(2, 1)  # coil index 2 is actuator_running (status)
        if rr and not rr.isError():
            return bool(rr.bits[0])
    except Exception:
        LOGGER.exception('Modbus read error')
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="HELICS ICSSIM Federate")
    parser.add_argument("--plant-type", choices=["water", "gas", "elec"], default="water", help="Plant type")
    parser.add_argument("--plc-ip", default="", help="Target PLC Modbus IP")
    parser.add_argument("--plc-port", type=int, default=502, help="Target PLC Modbus port")
    parser.add_argument("--fed-name", default="", help="HELICS federate name")
    parser.add_argument("--mock-plc", action="store_true", help="Use mock PLC state instead of connecting to Modbus")
    args = parser.parse_args()

    default_ips = {"water": "10.0.3.10", "gas": "10.0.3.12", "elec": "10.0.3.13"}
    plc_ip = args.plc_ip or os.environ.get("PLC_IP", default_ips.get(args.plant_type, "10.0.3.10"))
    fed_name = args.fed_name or os.environ.get("HELICS_FED_NAME", f"fed_icssim_{args.plant_type}")

    use_mock = args.mock_plc or os.environ.get("MOCK_PLC", "0") == "1"
    client = None

    if not use_mock:
        client = ModbusTcpClient(plc_ip, port=args.plc_port)
        LOGGER.info('Connecting to PLC Modbus [%s] at %s:%d...', args.plant_type, plc_ip, args.plc_port)
        connected = False
        for attempt in range(5 if os.environ.get("MOCK_FALLBACK", "0") == "1" else 30):
            try:
                client.connect()
                connected = True
                break
            except (ConnectionRefusedError, OSError):
                pass
            LOGGER.warning('Attempt %d: Connection to PLC failed, retrying in 1s...', attempt + 1)
            time.sleep(1)

        if not connected:
            if os.environ.get("MOCK_FALLBACK", "0") == "1":
                LOGGER.warning("Connection to PLC failed. Falling back to mock PLC mode.")
                use_mock = True
                client = None
            else:
                LOGGER.error('Cannot connect to PLC Modbus at %s:%d after retry limit', plc_ip, args.plc_port)
                return 2

    if use_mock:
        LOGGER.info('Running in MOCK PLC mode [%s]', args.plant_type)
    else:
        LOGGER.info('Successfully connected to PLC Modbus.')
    fed, pub_val, pub_trip, sub_input, pub_t1 = create_federate(fed_name, args.plant_type)

    if args.plant_type == "gas":
        plant: Any = GasPlant()
    elif args.plant_type == "elec":
        plant = ElecPlant()
    else:
        plant = TwoStageWaterPlant()

    try:
        current_time = 0.0
        while True:
            if client is not None:
                actuator_state = read_actuator_running(client)
                if actuator_state is None:
                    LOGGER.debug('Actuator status read failed; treating as OFF/False')
                    actuator_state = False
            else:
                # Mock PLC behavior: default active (running/closed)
                actuator_state = True

            if args.plant_type == 'water' and isinstance(plant, TwoStageWaterPlant):
                power_available = True
                if sub_input is not None:
                    v_pu = h.helicsInputGetDouble(sub_input)
                    if v_pu > 0.0:
                        power_available = (v_pu >= 0.85)
                # P1 comandada por PLC (coil 2). P2 sin PLC propio: activa si hay energía y T1 tiene agua.
                # Decisión de diseño explícita: P2 comparte alimentación eléctrica con P1.
                t1, t2 = plant.step(p1_cmd=actuator_state, p2_cmd=True, power_available=power_available, dt=POLL_INTERVAL)
                val = t2
                if pub_t1 is not None:
                    h.helicsPublicationPublishDouble(pub_t1, float(t1))
                LOGGER.info('[water] t=%.1f T1=%.2fm3 T2=%.2fm3 power=%s trip=%d',
                            current_time, t1, t2, power_available, 1 if plant.needs_trip() else 0)
            elif args.plant_type == 'gas' and isinstance(plant, GasPlant):
                power_available = True
                if sub_input is not None:
                    v_pu = h.helicsInputGetDouble(sub_input)
                    if v_pu > 0.0:
                        power_available = (v_pu >= 0.85)
                # Gas: válvula solo abre si hay energía eléctrica para control/compresores
                valve_open = actuator_state and power_available
                val = plant.step(valve_open, dt=POLL_INTERVAL)
                LOGGER.info('[gas] t=%.1f pressure=%.1fpsi valve=%s power=%s trip=%d',
                            current_time, val, valve_open, power_available, 1 if plant.needs_trip() else 0)
            else:
                # Interdependencia real: actualizar p_load_pu y gas_available ANTES de step()
                if args.plant_type == 'elec' and isinstance(plant, ElecPlant):
                    if sub_input is not None:
                        hospital_kw = h.helicsInputGetDouble(sub_input)
                        hospital_pu = hospital_kw / 550.0
                        city_pu = 400.0 / 550.0
                        plant.p_load_pu = city_pu + hospital_pu
                    if pub_t1 is not None:
                        g_trip = h.helicsInputGetInteger(pub_t1)
                        plant.gas_available = (g_trip == 0)

                val = plant.step(
                    not actuator_state if args.plant_type == 'elec' else actuator_state,
                    dt=POLL_INTERVAL,
                )

            trip = 1 if plant.needs_trip() else 0

            h.helicsPublicationPublishDouble(pub_val, float(val))
            h.helicsPublicationPublishInteger(pub_trip, int(trip))
            LOGGER.info('[%s] t=%.1f val=%.3f actuator=%s trip=%d', args.plant_type, current_time, val, actuator_state, trip)

            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        LOGGER.info('Shutdown requested')
    finally:
        if client is not None:
            client.close()
        h.helicsFederateFinalize(fed)
        LOGGER.info('HELICS federate finalized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

