#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_ROOT="$BASE_DIR/logs"
RUN_ID="$(date +%Y%m%d_%H%M%S)_$$"
LOG_DIR="$LOG_ROOT/helics_smoke_$RUN_ID"
mkdir -p "$LOG_DIR"

HELICS_BROKER_ADDRESS="${HELICS_BROKER_ADDRESS:-127.0.0.1}"
HELICS_BROKER_PORT="${HELICS_BROKER_PORT:-24040}"
HELICS_MAX_STEPS="${HELICS_MAX_STEPS:-8}"

PUB_NAME="MOCK_PUB_${RUN_ID}"
GRID_NAME="GRID_MOCK_${RUN_ID}"

cleanup() {
    local ec=$?
    if [[ -n "${GRID_PID:-}" ]] && kill -0 "$GRID_PID" 2>/dev/null; then kill "$GRID_PID" 2>/dev/null || true; fi
    if [[ -n "${PUB_PID:-}" ]] && kill -0 "$PUB_PID" 2>/dev/null; then kill "$PUB_PID" 2>/dev/null || true; fi
    if [[ -n "${BROKER_PID:-}" ]] && kill -0 "$BROKER_PID" 2>/dev/null; then kill "$BROKER_PID" 2>/dev/null || true; fi
    exit "$ec"
}
trap cleanup EXIT

export PYTHONPATH="$BASE_DIR":${PYTHONPATH:-}

echo "[*] HELICS smoke test"
echo "    broker: ${HELICS_BROKER_ADDRESS}:${HELICS_BROKER_PORT}"
echo "    run id: ${RUN_ID}"
echo "    logs:   ${LOG_DIR}"

helics_broker -f 2 --loglevel=warning --port="$HELICS_BROKER_PORT" >"$LOG_DIR/broker.log" 2>&1 &
BROKER_PID=$!
sleep 0.5

env \
  HELICS_FED_NAME="$PUB_NAME" \
  HELICS_BROKER_ADDRESS="$HELICS_BROKER_ADDRESS" \
  HELICS_BROKER_PORT="$HELICS_BROKER_PORT" \
  HELICS_MAX_STEPS="$HELICS_MAX_STEPS" \
  python3 "$BASE_DIR/helics_sim/mock_publisher.py" >"$LOG_DIR/mock_publisher.log" 2>&1 &
PUB_PID=$!

env \
  HELICS_FED_NAME="$GRID_NAME" \
  HELICS_BROKER_ADDRESS="$HELICS_BROKER_ADDRESS" \
  HELICS_BROKER_PORT="$HELICS_BROKER_PORT" \
  HELICS_MAX_STEPS="$HELICS_MAX_STEPS" \
  python3 "$BASE_DIR/helics_sim/fed_gridmock.py" >"$LOG_DIR/grid_mock.log" 2>&1 &
GRID_PID=$!

wait "$PUB_PID"
wait "$GRID_PID"
sleep 0.2

echo "--- broker.log ---"
tail -n 120 "$LOG_DIR/broker.log" || true
echo "--- mock_publisher.log ---"
tail -n 120 "$LOG_DIR/mock_publisher.log" || true
echo "--- grid_mock.log ---"
tail -n 120 "$LOG_DIR/grid_mock.log" || true

if grep -q "Unable to bind zmq reply socket" "$LOG_DIR/broker.log"; then
    echo "[FAIL] Broker bind error"
    exit 1
fi
if ! grep -q "ready" "$LOG_DIR/mock_publisher.log"; then
    echo "[FAIL] Publisher not ready"
    exit 1
fi
if ! grep -q "ready" "$LOG_DIR/grid_mock.log"; then
    echo "[FAIL] Grid mock not ready"
    exit 1
fi
if ! grep -q "Received breaker trip signal" "$LOG_DIR/grid_mock.log"; then
    echo "[FAIL] Grid mock did not receive trip signal"
    exit 1
fi

echo "[PASS] HELICS local smoke test successful"
