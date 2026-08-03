#!/usr/bin/env bash
# run_phase1.sh — Punto de entrada para la Fase 1: Nodo Mínimo Viable
set -euo pipefail

if command -v mn >/dev/null 2>&1; then echo '[*] Cleaning previous Mininet state (mn -c)' sudo mn -c || true 
fi

# 1. Definir BASE_DIR dinámicamente (Portable: funciona en Nobara, Ubuntu, Arch)
# Obtiene la ruta absoluta del directorio donde reside este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export BASE_DIR="$SCRIPT_DIR"

# 2. Cargar GridLAB-D desde instalación local o sistema
GLD_INSTALL="$HOME/gridlabd-install/bin"
if [ -d "$GLD_INSTALL" ]; then
    echo "[DEBUG] Agregando GridLAB-D desde: $GLD_INSTALL"
    export PATH="$GLD_INSTALL:$PATH"
    export GLPATH="$HOME/gridlabd-install/lib/gridlabd:$HOME/gridlabd-install/share/gridlabd"
else
    echo "[DEBUG] No se encontró instalación local en $GLD_INSTALL, usando sistema."
fi

LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR"

check_dep() {
    # Depuración: mostrar dónde se encuentra el comando si existe
    local path_cmd
    path_cmd=$(command -v "$1" 2>/dev/null)
    if [ -z "$path_cmd" ]; then
        echo "[ERROR] Dependencia faltante: $1"
        echo "[DEBUG] PATH actual: $PATH"
        exit 1
    fi
    echo "[OK] $1 encontrado en: $path_cmd"
}

echo "[*] Verificando dependencias del sistema..."
check_dep python3
check_dep gridlabd
check_dep mn

echo "[*] Cargando variables de entorno..."
if [ -f "$BASE_DIR/.env.example" ]; then
    cp -n "$BASE_DIR/.env.example" "$BASE_DIR/.env" 2>/dev/null || true
fi

# Cargar .env si existe
if [ -f "$BASE_DIR/.env" ]; then
    set -a
    source "$BASE_DIR/.env"
    set +a
else
    echo "[AVISO] No se encontró .env, usando valores por defecto."
fi

echo "[*] Iniciando broker HELICS..."
HELICS_FED_COUNT=${HELICS_FED_COUNT:-2}
helics_broker -f "$HELICS_FED_COUNT" --loglevel=warning ${HELICS_BROKER_PORT:+--port="$HELICS_BROKER_PORT"} \
    > "$LOG_DIR/helics_broker.log" 2>&1 &
BROKER_PID=$!
echo "    broker PID: $BROKER_PID"

echo "[*] Setting PYTHONPATH to repository root..."
export PYTHONPATH="$BASE_DIR":${PYTHONPATH:-}

echo "[*] Iniciando simulación física (ICSSIM federado)..."
python3 "$BASE_DIR/helics_sim/fed_icssim.py" > "$LOG_DIR/icssim.log" 2>&1 &
ICSSIM_PID=$!

echo "[*] Iniciando federado Grid mock..."
python3 "$BASE_DIR/helics_sim/fed_gridmock.py" > "$LOG_DIR/gridlabd.log" 2>&1 &
GRID_PID=$!

echo "[*] Iniciando topología de red (Mininet)..."
# Control de modo: interactivo (por defecto) o detached (para ejecuciones headless).
MININET_DETACH=${MININET_DETACH:-0}
# Acortar tiempo por defecto usado por 'pingall' en Mininet (segundos)
# Se puede ajustar exportando MININET_PING_TIMEOUT antes de invocar este script.
export MININET_PING_TIMEOUT=${MININET_PING_TIMEOUT:-0.5}
# Auto-start PLC runtime inside Mininet host 'h_plc' (1 = yes, 0 = no)
export AUTO_START_PLC=${AUTO_START_PLC:-1}

# Mostrar información de procesos ya iniciados antes de lanzar la topología interactiva
echo ""
echo "[+] Fase 1 en ejecución. PIDs activos (Mininet puede estar en modo interactivo):"
echo "    HELICS broker : $BROKER_PID"
echo "    ICSSIM        : $ICSSIM_PID"
echo "    GridLAB-D fed : $GRID_PID"

if [ "$MININET_DETACH" = "1" ]; then
    echo "    Red (Mininet) : (detached; registros -> $LOG_DIR/network.log)"
    echo ""
    echo "    Logs en: $LOG_DIR/"
    echo "    Para detener: sudo kill $BROKER_PID $ICSSIM_PID $GRID_PID \$NET_PID"
    # Detached: usar setsid y desconectar stdin para evitar dejar el pty colgado
    sudo setsid env PYTHONPATH="$BASE_DIR" python3 "$BASE_DIR/network/topology.py" </dev/null > "$LOG_DIR/network.log" 2>&1 &
    NET_PID=$!
    echo "    Mininet PID: $NET_PID"
else
    echo "    Red (Mininet) : (interactive; use Ctrl+D o 'exit' en la CLI de Mininet para salir)"
    echo ""
    echo "    Logs en: $LOG_DIR/"
    echo "    Para detener (procesos en background): sudo kill $BROKER_PID $ICSSIM_PID $GRID_PID"
    # Interactivo: ejecutar en primer plano (no background) para que Mininet use el tty
    sudo env PYTHONPATH="$BASE_DIR" python3 "$BASE_DIR/network/topology.py" 2>&1 | tee "$LOG_DIR/network.log"
    NET_PID=""
fi   