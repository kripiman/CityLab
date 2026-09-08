#!/usr/bin/env bash
# smoke_test_phase7.sh — Local non-Mininet smoke test for Phase 7 (10-federate city simulation including SIS)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR"

echo "[*] Cleaning previous test processes..."
pkill -9 -f "helics_broker" || true
pkill -9 -f "fed_icssim.py" || true
pkill -9 -f "fed_transport.py" || true
pkill -9 -f "fed_hospital.py" || true
pkill -9 -f "fed_logger.py" || true
pkill -9 -f "gridlabd_federate.py" || true
pkill -9 -f "fed_desal.py" || true
pkill -9 -f "fed_lighting.py" || true
pkill -9 -f "fed_sis.py" || true
rm -f "$LOG_DIR/cascading_events.csv"

export PYTHONUNBUFFERED=1
export PYTHONPATH="$BASE_DIR":${PYTHONPATH:-}
export MOCK_PLC=1
export HELICS_BROKER_PORT=23700
export HELICS_MAX_STEPS=5
export ENABLE_SIS_FEDERATE=${ENABLE_SIS_FEDERATE:-1}

TOTAL_FEDS=9
if [ "$ENABLE_SIS_FEDERATE" = "1" ]; then
    TOTAL_FEDS=10
fi

PIDS=()

echo "[*] Starting HELICS broker for Phase 7 Smoke Test ($TOTAL_FEDS federates, port 23700)..."
helics_broker -f $TOTAL_FEDS --port=23700 --loglevel=warning > "$LOG_DIR/test_broker_p7.log" 2>&1 &
PIDS+=($!)
sleep 1

echo "[*] Starting physics federates (mock PLC mode)..."
python3 "$SCRIPT_DIR/fed_icssim.py" --plant-type water --mock-plc > "$LOG_DIR/test_water.log" 2>&1 &
PIDS+=($!)
python3 "$SCRIPT_DIR/fed_icssim.py" --plant-type gas --mock-plc > "$LOG_DIR/test_gas.log" 2>&1 &
PIDS+=($!)
python3 "$SCRIPT_DIR/fed_icssim.py" --plant-type elec --mock-plc > "$LOG_DIR/test_elec.log" 2>&1 &
PIDS+=($!)

echo "[*] Starting Transport and Hospital federates..."
python3 "$SCRIPT_DIR/fed_transport.py" --mock-plc > "$LOG_DIR/test_transport.log" 2>&1 &
PIDS+=($!)
python3 "$SCRIPT_DIR/fed_hospital.py" > "$LOG_DIR/test_hospital.log" 2>&1 &
PIDS+=($!)

echo "[*] Starting GridLAB-D and Logger federates..."
python3 "$SCRIPT_DIR/gridlabd_federate.py" > "$LOG_DIR/test_gridlabd.log" 2>&1 &
PIDS+=($!)
python3 "$SCRIPT_DIR/fed_logger.py" > "$LOG_DIR/test_logger.log" 2>&1 &
PIDS+=($!)

echo "[*] Starting Category A federates (Desal & Smart Lighting)..."
python3 "$SCRIPT_DIR/fed_desal.py" > "$LOG_DIR/test_desal.log" 2>&1 &
PIDS+=($!)
python3 "$SCRIPT_DIR/fed_lighting.py" > "$LOG_DIR/test_lighting.log" 2>&1 &
PIDS+=($!)

if [ "$ENABLE_SIS_FEDERATE" = "1" ]; then
    echo "[*] Starting Safety Instrumented System (SIS) federate (#10)..."
    python3 "$SCRIPT_DIR/fed_sis.py" > "$LOG_DIR/test_sis.log" 2>&1 &
    PIDS+=($!)
fi

echo "[*] Waiting for $TOTAL_FEDS federates and broker to complete (timeout: 120s)..."
WAIT_TIMEOUT=120
START_TIME=$(date +%s)
FAIL=0
for pid in "${PIDS[@]}"; do
    while kill -0 "$pid" 2>/dev/null; do
        NOW=$(date +%s)
        if [ $((NOW - START_TIME)) -ge "$WAIT_TIMEOUT" ]; then
            echo "[FAIL] Smoke test Phase 7 excedió el presupuesto global de ${WAIT_TIMEOUT}s. Matando procesos..."
            kill -9 "${PIDS[@]}" 2>/dev/null || true
            exit 1
        fi
        sleep 0.5
    done
    if ! wait "$pid"; then
        FAIL=1
    fi
done

if [ "$FAIL" -ne 0 ]; then
    echo "[FAIL] Smoke test Phase 7 failed (one or more processes exited with error)."
    exit 1
fi

echo "[*] Smoke test Phase 7 complete ($TOTAL_FEDS/$TOTAL_FEDS federates)."
