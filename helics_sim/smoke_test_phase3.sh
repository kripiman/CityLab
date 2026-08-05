#!/usr/bin/env bash
# smoke_test_phase3.sh — Local non-Mininet smoke test for Phase 3 (7-federate city simulation)
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
pkill -9 -f "fed_gridmock.py" || true
rm -f "$LOG_DIR/cascading_events.csv"

export PYTHONUNBUFFERED=1
export PYTHONPATH="$BASE_DIR":${PYTHONPATH:-}
export MOCK_PLC=1
export HELICS_BROKER_PORT=23500

echo "[*] Starting HELICS broker for Phase 3 Smoke Test (7 federates, port 23500)..."
helics_broker -f 7 --port=23500 --loglevel=warning > "$LOG_DIR/test_broker_p3.log" 2>&1 &
BROKER_PID=$!
sleep 1

echo "[*] Starting physics federates (mock PLC mode)..."
python3 "$SCRIPT_DIR/fed_icssim.py" --plant-type water --mock-plc > "$LOG_DIR/test_water.log" 2>&1 &
WATER_PID=$!

python3 "$SCRIPT_DIR/fed_icssim.py" --plant-type gas --mock-plc > "$LOG_DIR/test_gas.log" 2>&1 &
GAS_PID=$!

python3 "$SCRIPT_DIR/fed_icssim.py" --plant-type elec --mock-plc > "$LOG_DIR/test_elec.log" 2>&1 &
ELEC_PID=$!

echo "[*] Starting Transport federate (mock PLC mode)..."
python3 "$SCRIPT_DIR/fed_transport.py" --mock-plc > "$LOG_DIR/test_transport.log" 2>&1 &
TRANSPORT_PID=$!

echo "[*] Starting Grid federate mock..."
python3 "$SCRIPT_DIR/fed_gridmock.py" > "$LOG_DIR/test_gridmock_p3.log" 2>&1 &
GRID_PID=$!

echo "[*] Starting Hospital federate..."
python3 "$SCRIPT_DIR/fed_hospital.py" > "$LOG_DIR/test_hospital.log" 2>&1 &
HOSPITAL_PID=$!

echo "[*] Starting Observer Logger federate..."
python3 "$SCRIPT_DIR/fed_logger.py" > "$LOG_DIR/test_logger_p3.log" 2>&1 &
LOGGER_PID=$!

echo "[*] Waiting for federation execution (10 steps)..."
wait $WATER_PID $GAS_PID $ELEC_PID $TRANSPORT_PID $GRID_PID $HOSPITAL_PID $LOGGER_PID || true

echo "[*] Phase 3 Smoke Test Completed. Checking CSV log output:"
if [ -f "$LOG_DIR/cascading_events.csv" ]; then
    echo "--- cascading_events.csv ---"
    head -n 5 "$LOG_DIR/cascading_events.csv"
    echo "[PASS] Phase 3 7-Federate Centralized Observer log generated successfully."
else
    echo "[FAIL] CSV log missing."
    exit 1
fi
