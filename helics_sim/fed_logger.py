#!/usr/bin/env python3
"""HELICS federate: Centralized Observer & CSV Logger for Phase 2.

Subscribes to all sector metrics and trip publications across the bus:
 - water/t1_level, water/t2_level, breaker/trip (water)
 - gas/pressure, gas/trip (gas)
 - grid/frequency, grid/trip (elec)
 - sis/trip (parada de emergencia SIL-3 publicada por fed_sis)

Outputs structured CSV data to logs/cascading_events.csv for analysis.
"""
from __future__ import annotations

import csv
import logging
import os
import time

import helics as h

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][LOGGER_FED] %(message)s')
LOGGER = logging.getLogger('fed_logger')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
CSV_PATH = os.path.join(LOG_DIR, 'cascading_events.csv')
os.makedirs(LOG_DIR, exist_ok=True)

POLL_INTERVAL = 1.0
FED_NAME = os.environ.get('HELICS_FED_NAME', 'LOGGER_fed')
BROKER_ADDRESS = os.environ.get('HELICS_BROKER_ADDRESS', '127.0.0.1')
BROKER_PORT = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
MAX_STEPS = int(os.environ.get('HELICS_MAX_STEPS', '0'))


def main() -> int:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, 'zmq')
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f'--federates=1 --broker_address={BROKER_ADDRESS} --brokerport={BROKER_PORT}',
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate(FED_NAME, fi)

    sub_water_t2  = h.helicsFederateRegisterSubscription(fed, 'water/t2_level', '')
    sub_water_t1  = h.helicsFederateRegisterSubscription(fed, 'water/t1_level', '')
    sub_water_trip = h.helicsFederateRegisterSubscription(fed, 'breaker/trip', '')

    sub_gas_val = h.helicsFederateRegisterSubscription(fed, 'gas/pressure', '')
    sub_gas_trip = h.helicsFederateRegisterSubscription(fed, 'gas/trip', '')

    sub_grid_val = h.helicsFederateRegisterSubscription(fed, 'grid/frequency', '')
    sub_grid_trip = h.helicsFederateRegisterSubscription(fed, 'grid/trip', '')
    sub_grid_voltage = h.helicsFederateRegisterSubscription(fed, 'grid/voltage_pu', '')

    sub_hospital_load = h.helicsFederateRegisterSubscription(fed, 'hospital/load_kw', '')
    sub_hospital_ups  = h.helicsFederateRegisterSubscription(fed, 'hospital/on_ups', '')

    sub_trans_cong = h.helicsFederateRegisterSubscription(fed, 'transport/congestion', '')
    sub_trans_trip = h.helicsFederateRegisterSubscription(fed, 'transport/trip', '')

    # SIS SIL-3: fed_sis solo se lanza con ENABLE_SIS_FEDERATE=1 (smoke_test_phase7.sh).
    # Si no está presente, la entrada queda en centinela y se sanea a 0 más abajo.
    sub_sis_trip = h.helicsFederateRegisterSubscription(fed, 'sis/trip', '')

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info('Central Observer Logger federate ready (CSV log: %s)', CSV_PATH)

    with open(CSV_PATH, 'w', newline='\n', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp_s',
                          'water_t1_m3', 'water_t2_m3', 'water_trip',
                          'gas_pressure_psi', 'gas_trip',
                          'grid_freq_hz', 'grid_trip', 'grid_voltage_pu',
                          'hospital_load_kw', 'hospital_on_ups',
                          'transport_congestion', 'transport_trip',
                          'sis_trip',
                          'cascade_alert'])

        current_time = 0.0
        steps = 0
        try:
            while True:
                current_time += POLL_INTERVAL
                h.helicsFederateRequestTime(fed, current_time)

                w_t2  = h.helicsInputGetDouble(sub_water_t2)
                w_t1  = h.helicsInputGetDouble(sub_water_t1)
                w_trip = h.helicsInputGetInteger(sub_water_trip)

                g_val = h.helicsInputGetDouble(sub_gas_val)
                g_trip = h.helicsInputGetInteger(sub_gas_trip)

                e_val = h.helicsInputGetDouble(sub_grid_val)
                e_trip = h.helicsInputGetInteger(sub_grid_trip)
                e_voltage = h.helicsInputGetDouble(sub_grid_voltage)

                h_load = h.helicsInputGetDouble(sub_hospital_load)
                h_ups  = h.helicsInputGetInteger(sub_hospital_ups)

                tr_cong = h.helicsInputGetDouble(sub_trans_cong)
                tr_trip = h.helicsInputGetInteger(sub_trans_trip)

                sis_trip = h.helicsInputGetInteger(sub_sis_trip)

                # Sanitización de valores iniciales (sentinels HELICS pre-publicación)
                w_t1 = 10.0 if w_t1 < -1e20 else w_t1
                w_t2 = 15.0 if w_t2 < -1e20 else w_t2
                g_val = 90.0 if g_val < -1e20 else g_val
                e_val = 60.0 if (e_val < -1e20 or e_val > 70.0) else e_val
                e_voltage = 1.0 if e_voltage < -1e20 else e_voltage
                h_load = 0.0 if h_load < -1e20 else h_load
                tr_cong = 0.0 if tr_cong < -1e20 else tr_cong

                w_trip = 0 if w_trip < -9000000 else w_trip
                g_trip = 0 if g_trip < -9000000 else g_trip
                e_trip = 0 if e_trip < -9000000 else e_trip
                h_ups = 0 if h_ups < -9000000 else h_ups
                tr_trip = 0 if tr_trip < -9000000 else tr_trip
                sis_trip = 0 if sis_trip < -9000000 else sis_trip

                tripped_count = w_trip + g_trip + e_trip + tr_trip
                alert = 'NORMAL' if tripped_count == 0 else ('PARTIAL_TRIP' if tripped_count < 4 else 'CASCADING_BLACKOUT')
                if h_ups == 1:
                    alert += '+HOSPITAL_UPS'
                if sis_trip == 1:
                    alert += '+SIS_ESD'

                writer.writerow([f"{current_time:.1f}",
                                  f"{w_t1:.2f}", f"{w_t2:.2f}", w_trip,
                                  f"{g_val:.2f}", g_trip,
                                  f"{e_val:.2f}", e_trip, f"{e_voltage:.3f}",
                                  f"{h_load:.1f}", h_ups,
                                  f"{tr_cong:.2f}", tr_trip,
                                  sis_trip,
                                  alert])
                f.flush()

                LOGGER.info('t=%.1fs | W T1=%.2f T2=%.2f(t=%d) Gas=%.1fpsi(t=%d) Grid=%.1fHz(t=%d V=%.3f) Hosp=%.1fkW(ups=%d) Trans=%.2f(t=%d) SIS=%d [%s]',
                            current_time, w_t1, w_t2, w_trip, g_val, g_trip, e_val, e_trip, e_voltage, h_load, h_ups, tr_cong, tr_trip, sis_trip, alert)

                steps += 1
                if MAX_STEPS > 0 and steps >= MAX_STEPS:
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            LOGGER.info('Observer logger interrupted')
        finally:
            h.helicsFederateFinalize(fed)
            LOGGER.info('Observer logger finalized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
