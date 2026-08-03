#!/usr/bin/env bash
# run_phase1.sh — Punto de entrada para la Fase 1: Nodo Mínimo Viable
# Cadena: Ataque → PLC → ICSSIM → HELICS → GridLAB-D
set -euo pipefail

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

check_dep() {
    command -v "$1" &>/dev/null || { echo "[ERROR] Dependencia faltante: $1"; exit 1; }
}

echo "[*] Verificando dependencias del sistema..."
check_dep python3
check_dep gridlabd
check_dep mn          # mininet

echo "[*] Cargando variables de entorno..."
cp -n .env.example .env 2>/dev/null || true
# shellcheck source=.env.example
set -a; source .env; set +a

echo "[*] Iniciando broker HELICS..."
# Use 2 federates (ICSSIM + Grid mock) for this PoC
HELICS_FED_COUNT=${HELICS_FED_COUNT:-2}
helics_broker -f "$HELICS_FED_COUNT" --loglevel=warning ${HELICS_BROKER_PORT:+--port="$HELICS_BROKER_PORT"} \
    > "$LOG_DIR/helics_broker.log" 2>&1 &
BROKER_PID=$!
echo "    broker PID: $BROKER_PID"

echo "[*] Setting PYTHONPATH to repository root so federates import local packages correctly"
export PYTHONPATH="$BASE_DIR":${PYTHONPATH:-}

echo "[*] Iniciando simulación física (ICSSIM federado)..."
python3 helics_sim/fed_icssim.py > "$LOG_DIR/icssim.log" 2>&1 &
ICSSIM_PID=$!

echo "[*] Iniciando federado Grid mock (sustituye GridLAB-D en PoC)..."
python3 helics_sim/fed_gridmock.py > "$LOG_DIR/gridlabd.log" 2>&1 &
GRID_PID=$!

echo "[*] Iniciando topología de red (Mininet)..."
# sudo+redirección: usar tee para que el proceso sudo escriba al log correctamente
sudo python3 network/topology.py 2>&1 | tee "$LOG_DIR/network.log" &
NET_PID=$!

echo ""
echo "[+] Fase 1 en ejecución. PIDs activos:"
echo "    HELICS broker : $BROKER_PID"
echo "    ICSSIM        : $ICSSIM_PID"
echo "    GridLAB-D fed : $GRID_PID"
echo "    Red (Mininet) : $NET_PID"
echo ""
echo "    Logs en: $LOG_DIR/"
echo "    Para detener: sudo kill $BROKER_PID $ICSSIM_PID $GRID_PID $NET_PID"
