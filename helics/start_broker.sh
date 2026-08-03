#!/usr/bin/env bash
set -euo pipefail

# Start HELICS broker for local PoC
helics_broker_cmd() {
  if command -v helics_broker >/dev/null 2>&1; then
    echo "helics_broker -f 3" # 3 federates
  else
    echo "Error: helics_broker not found. Install HELICS (system package or pip helics==3.4.0)" >&2
    return 1
  fi
}

if ! command -v helics_broker >/dev/null 2>&1; then
  echo "HELICS broker not installed. Please install via package manager or pip. Aborting." >&2
  exit 1
fi

helics_broker -f 3 &
B_PID=$!

echo "HELICS broker started (pid $B_PID)"
