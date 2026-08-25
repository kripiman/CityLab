#!/usr/bin/env bash
# smoke_test_phase4.sh — Local non-Mininet smoke test for Phase 4 (9-federate city simulation)
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
rm -f "$LOG_DIR/cascading_events.csv"

export PYTHONUNBUFFERED=1
export PYTHONPATH="$BASE_DIR":${PYTHONPATH:-}
export MOCK_PLC=1
export HELICS_BROKER_PORT=23600
export HELICS_MAX_STEPS=5

PIDS=()

echo "[*] Starting HELICS broker for Phase 4 Smoke Test (9 federates, port 23600)..."
helics_broker -f 9 --port=23600 --loglevel=warning > "$LOG_DIR/test_broker_p4.log" 2>&1 &
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

echo "[*] Waiting for 9 federates and broker to complete..."
FAIL=0
for pid in "${PIDS[@]}"; do
    if ! wait "$pid"; then
        FAIL=1
    fi
done

if [ "$FAIL" -ne 0 ]; then
    echo "[FAIL] Smoke test Phase 4 failed (one or more processes exited with error)."
    exit 1
fi

echo "[*] Smoke test Phase 4 complete (9/9 federates)."
