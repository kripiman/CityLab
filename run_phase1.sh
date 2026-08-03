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
set -a; source .env; set +a

echo "[*] Iniciando broker HELICS..."
helics_broker -f 3 --loglevel=warning --port="$HELICS_BROKER_PORT" \
    > "$LOG_DIR/helics_broker.log" 2>&1 &
BROKER_PID=$!
echo "    broker PID: $BROKER_PID"

echo "[*] Iniciando simulación física (ICSSIM federado)..."
python3 helics/fed_icssim.py > "$LOG_DIR/icssim.log" 2>&1 &
ICSSIM_PID=$!

echo "[*] Iniciando federado Grid mock (sustituye GridLAB-D en PoC)..."
python3 helics/fed_gridmock.py > "$LOG_DIR/gridlabd.log" 2>&1 &
GRID_PID=$!

echo "[*] Iniciando topología de red (Mininet)..."
# Mininet debe ejecutarse en primer plano normalmente; aquí se lanza en background para orquestación local
sudo python3 network/topology.py > "$LOG_DIR/network.log" 2>&1 &
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
