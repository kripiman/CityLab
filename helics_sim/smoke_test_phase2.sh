#!/usr/bin/env bash
# smoke_test_phase2.sh — Local non-Mininet smoke test for Phase 2 federation
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR"

echo "[*] Cleaning previous test processes..."
pkill -9 -f "helics_broker" || true
pkill -9 -f "fed_icssim.py" || true
pkill -9 -f "fed_logger.py" || true
pkill -9 -f "gridlabd_federate.py" || true
pkill -9 -f "fed_gridmock.py" || true

export PYTHONUNBUFFERED=1
export PYTHONPATH="$BASE_DIR":${PYTHONPATH:-}
export MOCK_PLC=1
export HELICS_MAX_STEPS=10

echo "[*] Starting HELICS broker for Phase 2 Smoke Test (6 federates)..."
helics_broker -f 6 --loglevel=warning > "$LOG_DIR/test_broker_p2.log" 2>&1 &
BROKER_PID=$!
sleep 1

echo "[*] Starting physics federates (mock PLC mode)..."
python3 "$SCRIPT_DIR/fed_icssim.py" --plant-type water --mock-plc > "$LOG_DIR/test_water.log" 2>&1 &
WATER_PID=$!

python3 "$SCRIPT_DIR/fed_icssim.py" --plant-type gas --mock-plc > "$LOG_DIR/test_gas.log" 2>&1 &
GAS_PID=$!

python3 "$SCRIPT_DIR/fed_icssim.py" --plant-type elec --mock-plc > "$LOG_DIR/test_elec.log" 2>&1 &
ELEC_PID=$!

echo "[*] Starting Grid federate mock..."
python3 "$SCRIPT_DIR/fed_gridmock.py" > "$LOG_DIR/test_gridmock_p2.log" 2>&1 &
GRID_PID=$!

echo "[*] Starting Hospital federate..."
python3 "$SCRIPT_DIR/fed_hospital.py" > "$LOG_DIR/test_hospital.log" 2>&1 &
HOSPITAL_PID=$!

echo "[*] Starting Observer Logger federate..."
python3 "$SCRIPT_DIR/fed_logger.py" > "$LOG_DIR/test_logger_p2.log" 2>&1 &
LOGGER_PID=$!

echo "[*] Waiting for federation execution (10 steps)..."
wait $WATER_PID $GAS_PID $ELEC_PID $GRID_PID $HOSPITAL_PID $LOGGER_PID || true

echo "[*] Phase 2 Smoke Test Completed. Checking CSV log output:"
if [ -f "$LOG_DIR/cascading_events.csv" ]; then
    echo "--- cascading_events.csv ---"
    head -n 5 "$LOG_DIR/cascading_events.csv"
    echo "[PASS] Centralized observer log generated successfully."
else
    echo "[FAIL] CSV log missing."
    exit 1
fi
