#!/usr/bin/env bash
# run_phase3.sh — Punto de entrada para la Fase 3: Cyber Range de Ciudad Completa
set -euo pipefail

# Asegurar privilegios de root/sudo
if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] Este script requiere privilegios de root. Ejecutar con: sudo ./run_phase3.sh"
  exit 1
fi

# Limpiar estado previo de Mininet y procesos de simulación
if command -v mn >/dev/null 2>&1; then
  echo '[*] Cleaning previous Mininet state (mn -c)...'
  mn -c || true
fi

echo '[*] Cleaning previous simulation processes...'
pkill -9 -f "helics_broker" || true
pkill -9 -f "fed_icssim.py" || true
pkill -9 -f "gridlabd_federate.py" || true
pkill -9 -f "fed_hospital.py" || true
pkill -9 -f "fed_transport.py" || true
pkill -9 -f "fed_logger.py" || true
pkill -9 -f "fed_gridmock.py" || true
pkill -9 -f "modbus_emulator.py" || true

export PYTHONUNBUFFERED=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export BASE_DIR="$SCRIPT_DIR"

INVOKING_USER="${SUDO_USER:-$(whoami)}"
USER_HOME=$(eval echo "~$INVOKING_USER")
GLD_INSTALL="$USER_HOME/gridlabd-install/bin"
if [ -d "$GLD_INSTALL" ]; then
    export PATH="$GLD_INSTALL:$PATH"
    export GLPATH="$USER_HOME/gridlabd-install/lib/gridlabd:$USER_HOME/gridlabd-install/share/gridlabd"
fi

LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR"

check_dep() {
    local path_cmd
    path_cmd=$(command -v "$1" 2>/dev/null)
    if [ -z "$path_cmd" ]; then
        echo "[ERROR] Dependencia faltante: $1"
        exit 1
    fi
}

check_dep python3
check_dep gridlabd
check_dep mn

echo "[*] Iniciando broker HELICS (Fase 3: 7 federados)..."
HELICS_FED_COUNT=${HELICS_FED_COUNT:-7}
helics_broker -f "$HELICS_FED_COUNT" --loglevel=warning ${HELICS_BROKER_PORT:+--port="$HELICS_BROKER_PORT"} \
    > "$LOG_DIR/helics_broker.log" 2>&1 &
BROKER_PID=$!

export PYTHONPATH="$BASE_DIR":${PYTHONPATH:-}

echo "[*] Iniciando federados de simulación física multisectorial..."
python3 "$BASE_DIR/helics_sim/fed_icssim.py" --plant-type water > "$LOG_DIR/icssim_water.log" 2>&1 &
WATER_PID=$!

python3 "$BASE_DIR/helics_sim/fed_icssim.py" --plant-type gas > "$LOG_DIR/icssim_gas.log" 2>&1 &
GAS_PID=$!

python3 "$BASE_DIR/helics_sim/fed_icssim.py" --plant-type elec > "$LOG_DIR/icssim_elec.log" 2>&1 &
ELEC_PID=$!

echo "[*] Iniciando federado de Transporte (semáforos)..."
python3 "$BASE_DIR/helics_sim/fed_transport.py" > "$LOG_DIR/transport.log" 2>&1 &
TRANSPORT_PID=$!

echo "[*] Iniciando federado GridLAB-D..."
python3 "$BASE_DIR/helics_sim/gridlabd_federate.py" > "$LOG_DIR/gridlabd.log" 2>&1 &
GRID_PID=$!

echo "[*] Iniciando federado Hospital (carga crítica + UPS)..."
python3 "$BASE_DIR/helics_sim/fed_hospital.py" > "$LOG_DIR/hospital.log" 2>&1 &
HOSPITAL_PID=$!

echo "[*] Iniciando logger centralizado (CSV cascading_events)..."
python3 "$BASE_DIR/helics_sim/fed_logger.py" > "$LOG_DIR/fed_logger.log" 2>&1 &
LOGGER_PID=$!

MININET_DETACH=${MININET_DETACH:-0}
export MININET_PING_TIMEOUT=${MININET_PING_TIMEOUT:-0.5}
export AUTO_START_PLC=${AUTO_START_PLC:-1}

echo ""
echo "[+] Fase 3 (Ciudad Completa) en ejecución. Federados activos:"
echo "    HELICS broker : $BROKER_PID"
echo "    Water ICSSIM  : $WATER_PID"
echo "    Gas ICSSIM    : $GAS_PID"
echo "    Elec ICSSIM   : $ELEC_PID"
echo "    Transport Fed : $TRANSPORT_PID"
echo "    GridLAB-D fed : $GRID_PID"
echo "    Hospital      : $HOSPITAL_PID"
echo "    Logger CSV    : $LOGGER_PID"

if [ "$MININET_DETACH" = "1" ]; then
    setsid env PYTHONPATH="$BASE_DIR" python3 "$BASE_DIR/network/topology.py" </dev/null > "$LOG_DIR/network.log" 2>&1 &
    NET_PID=$!
    echo "    Mininet PID   : $NET_PID"
else
    env PYTHONPATH="$BASE_DIR" python3 "$BASE_DIR/network/topology.py" 2>&1 | tee "$LOG_DIR/network.log"
fi
