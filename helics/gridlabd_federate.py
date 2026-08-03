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


def start_gridlabd(glm_path: str):
    logf = open(os.path.join(LOG_DIR, f'gridlabd_{os.path.basename(glm_path)}.log'), 'a')
    cmd = ['gridlabd', '-D', 'NL=1', glm_path]
    LOGGER.info('Starting gridlabd: %s', ' '.join(cmd))
    p = subprocess.Popen(cmd, stdout=logf, stderr=logf, preexec_fn=os.setsid)
    return p, logf


def stop_gridlabd(proc, logf):
    if proc is None:
        return
    try:
        LOGGER.info('Stopping gridlabd pid=%d', proc.pid)
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=5)
    except Exception:
        LOGGER.exception('Error stopping gridlabd, killing')
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            pass
    try:
        logf.close()
    except Exception:
        pass


def create_federate() -> h.helics_federate:
    fi = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fi, 'zmq')
    h.helicsFederateInfoSetCoreInitString(fi, '--federates=1')
    h.helicsFederateInfoSetTimeProperty(fi, h.helics_property_time_delta, POLL_INTERVAL)
    fed = h.helicsCreateValueFederate('GRIDLABD_fed', fi)

    sub_trip = h.helicsFederateRegisterSubscription(fed, 'breaker/trip', '')

    h.helicsFederateEnterExecutingMode(fed)
    LOGGER.info('HELICS federate GRIDLAB-D ready')
    return fed


def main() -> int:
    if not shutil.which('gridlabd'):
        LOGGER.error('gridlabd not found in PATH; install gridlabd to use this federate')
        return 2

    fed = create_federate()

    # start normal model
    proc, logf = start_gridlabd(NORMAL_GLM)
    current_tripped = False

    try:
        current_time = 0.0
        while True:
            current_time += POLL_INTERVAL
            h.helicsFederateRequestTime(fed, current_time)

            trip_val = h.helicsInputGetInteger(h.helicsFederateGetInput(fed, 0))
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

            time.sleep(0.1)
    except KeyboardInterrupt:
        LOGGER.info('Shutdown requested')
    finally:
        stop_gridlabd(proc, logf)
        h.helicsFederateFinalize(fed)
        LOGGER.info('GRIDLABD federate finalized')
    return 0


if __name__ == '__main__':
    import shutil
    raise SystemExit(main())
