#!/usr/bin/env python3
"""HELICS federate: GridLAB-D controller for PoC

Behavior:
 - On start launches gridlabd with gridlabd/substation_normal.glm (background)
 - Subscribes to HELICS topic 'breaker/trip'
 - When trip==1: kills current gridlabd and launches gridlabd/substation_tripped.glm
 - When trip returns to 0: restores normal model

Notes:
 - Requires gridlabd installed and on PATH
 - Models are minimal and may need tuning per GridLAB-D version
"""
from __future__ import annotations

import shutil
import subprocess
import time
import logging
import os
import signal

import helics as h

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('gridlabd_fed')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLM_DIR = os.path.join(BASE_DIR, 'gridlabd')
NORMAL_GLM = os.path.join(GLM_DIR, 'substation_normal.glm')
TRIPPED_GLM = os.path.join(GLM_DIR, 'substation_tripped.glm')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

POLL_INTERVAL = 1.0
FED_NAME = os.environ.get('HELICS_FED_NAME', 'GRIDLABD_fed')
BROKER_ADDRESS = os.environ.get('HELICS_BROKER_ADDRESS', '127.0.0.1')
BROKER_PORT = int(os.environ.get('HELICS_BROKER_PORT', '23404'))
MAX_STEPS = int(os.environ.get('HELICS_MAX_STEPS', '0'))


def start_gridlabd(glm_path: str):
    log_path = os.path.join(LOG_DIR, f'gridlabd_{os.path.basename(glm_path)}.log')
    logf = open(log_path, 'a')  # noqa: SIM115 — kept open intentionally for subprocess lifetime
    # glm_path is a resolved absolute path from module constants, not user input
    cmd = ['gridlabd', '-D', 'NL=1', glm_path]
    LOGGER.info('Starting gridlabd: %s', ' '.join(cmd))
    p = subprocess.Popen(cmd, stdout=logf, stderr=logf, preexec_fn=os.setsid)  # noqa: S603
    return p, logf


def stop_gridlabd(proc, logf) -> None:
    if proc is None:
        return
    try:
        LOGGER.info('Stopping gridlabd pid=%d', proc.pid)
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=5)
    except (ProcessLookupError, ChildProcessError, TimeoutError) as exc:
        LOGGER.exception('Error stopping gridlabd, killing: %s', exc)
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, ChildProcessError) as kill_exc:
            LOGGER.warning('SIGKILL also failed: %s', kill_exc)
    finally:
        logf.close()


def create_federate() -> tuple[h.helics_federate, h.helics_input]:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, 'zmq')
    h.helicsFederateInfoSetCoreInitString(
        fi,
        f'--federates=1 --broker_address={BROKER_ADDRESS} --brokerport={BROKER_PORT}',
    )
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate(FED_NAME, fi)

    sub_trip = h.helicsFederateRegisterSubscription(fed, 'breaker/trip', '')

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info('HELICS federate %s ready (broker=%s:%d)', FED_NAME, BROKER_ADDRESS, BROKER_PORT)
    return fed, sub_trip


def main() -> int:
    if not shutil.which('gridlabd'):
        LOGGER.error('gridlabd not found in PATH; install gridlabd to use this federate')
        return 2

    fed, sub_trip = create_federate()

    # start normal model
    proc, logf = start_gridlabd(NORMAL_GLM)
    current_tripped = False

    try:
        current_time = 0.0
        steps = 0
        while True:
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)

            trip_val = h.helicsInputGetInteger(sub_trip)
            trip = int(trip_val)

            if trip and not current_tripped:
                LOGGER.warning('Trip detected -> switching to TRIPPED GLM')
                stop_gridlabd(proc, logf)
                proc, logf = start_gridlabd(TRIPPED_GLM)
                current_tripped = True
            elif not trip and current_tripped:
                LOGGER.info('Trip cleared -> restoring NORMAL GLM')
                stop_gridlabd(proc, logf)
                proc, logf = start_gridlabd(NORMAL_GLM)
                current_tripped = False

            steps += 1
            if MAX_STEPS > 0 and steps >= MAX_STEPS:
                LOGGER.info('Reached HELICS_MAX_STEPS=%d, exiting', MAX_STEPS)
                break

            time.sleep(0.1)
    except KeyboardInterrupt:
        LOGGER.info('Shutdown requested')
    finally:
        stop_gridlabd(proc, logf)
        h.helicsFederateFinalize(fed)
        LOGGER.info('GRIDLABD federate finalized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
