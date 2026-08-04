#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG_PATH="$SCRIPT_DIR/openplc_config/openplc.cfg"
LOG_DIR="$SCRIPT_DIR/../../logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/openplc_runtime.log"
PIDFILE="$LOG_DIR/openplc.pid"

echo "[*] Starting PLC runtime (OpenPLC or fallback emulator) - $(date)" >> "$LOG"

# Detect OpenPLC runtime binary names commonly used
if command -v openplc >/dev/null 2>&1 || command -v openplc_runtime >/dev/null 2>&1 || command -v openplc_server >/dev/null 2>&1; then
    if command -v openplc_server >/dev/null 2>&1; then
        CMD="openplc_server -c $CFG_PATH"
    elif command -v openplc_runtime >/dev/null 2>&1; then
        CMD="openplc_runtime -c $CFG_PATH"
    else
        CMD="openplc -c $CFG_PATH"
    fi
    setsid $CMD >> "$LOG" 2>&1 &
    echo $! > "$PIDFILE"
    echo "[*] OpenPLC started, pid $(cat $PIDFILE)" >> "$LOG"
else
    # Fallback to Python emulator located alongside this script
    setsid python3 "$SCRIPT_DIR/modbus_emulator.py" >> "$LOG" 2>&1 &
    echo $! > "$PIDFILE"
    echo "[*] Fallback emulator started, pid $(cat $PIDFILE)" >> "$LOG"
fi

echo "Started. Log: $LOG"
