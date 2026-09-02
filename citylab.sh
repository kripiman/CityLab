#!/usr/bin/env bash
# citylab.sh — Punto de entrada único de CityLab Cyber Range.
#
# Reemplaza el uso directo de run_phase1.sh / run_phase2.sh / run_phase3.sh, que quedan
# como implementación interna invocada por `citylab.sh up`.
#
#   ./citylab.sh help                 Ayuda
#   sudo ./citylab.sh up [--phase N]  Desplegar el laboratorio (por defecto fase 3; requiere root)
#   sudo ./citylab.sh down            Detener todo y limpiar estado de Mininet/OVS
#   ./citylab.sh smoke [--phase N]    Co-simulación HELICS sin root (fase 4 o 7; por defecto 7)
#   ./citylab.sh test [args...]       Suite de pruebas unitarias (sin root)
#   ./citylab.sh profile [args...]    Medición real de RAM/CPU de los procesos vivos
#   ./citylab.sh status               Qué componentes están corriendo ahora mismo
set -uo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR"

export PYTHONPATH="$BASE_DIR:${PYTHONPATH:-}"

c_info()  { echo -e "\033[1;36m[citylab]\033[0m $*"; }
c_warn()  { echo -e "\033[1;33m[citylab]\033[0m $*"; }
c_err()   { echo -e "\033[1;31m[citylab]\033[0m $*" >&2; }

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        c_err "'$1' requiere root (Mininet y Open vSwitch). Usa: sudo ./citylab.sh $1"
        exit 1
    fi
}

usage() {
    sed -n '2,16p' "$BASE_DIR/citylab.sh" | sed 's/^# \{0,1\}//'
}

cmd_up() {
    local phase=3
    while [ $# -gt 0 ]; do
        case "$1" in
            --phase) phase="${2:-3}"; shift 2 ;;
            *) c_err "Opción desconocida para 'up': $1"; exit 2 ;;
        esac
    done
    require_root up

    # Generar e inyectar semilla de sesión única e inmemorizable si no existe
    export CITYLAB_SESSION_SEED="${CITYLAB_SESSION_SEED:-$(python3 -c 'import secrets; print(secrets.token_hex(16))' 2>/dev/null || date +%s%N)}"
    c_info "Semilla de sesión generada: ${CITYLAB_SESSION_SEED:0:8}..."

    local script="$BASE_DIR/run_phase${phase}.sh"
    if [ ! -x "$script" ]; then
        c_err "No existe la fase $phase ($script). Fases disponibles: 1, 2, 3."
        exit 2
    fi
    c_info "Desplegando CityLab — fase $phase (delegando en run_phase${phase}.sh)"
    exec "$script"
}

cmd_down() {
    require_root down
    c_info "Deteniendo federados, emuladores y servicios de forma segura..."
    if [ -f "/tmp/citylab_daemons.pids" ]; then
        while read -r pid; do
            [ -n "$pid" ] && kill -15 "$pid" 2>/dev/null || true
        done < "/tmp/citylab_daemons.pids"
        sleep 0.1
        while read -r pid; do
            [ -n "$pid" ] && kill -9 "$pid" 2>/dev/null || true
        done < "/tmp/citylab_daemons.pids"
        rm -f "/tmp/citylab_daemons.pids"
    fi
    local citylab_procs="modbus_emulator.py|dnp3_emulator.py|iec61850_emulator.py|opcua_emulator.py|honeypot_server.py|ad_dc_emulator.py|scada_server.py|fed_icssim.py|fed_transport.py|fed_hospital.py|fed_logger.py|fed_desal.py|fed_lighting.py|fed_sis.py|fed_viz_bridge.py|gridlabd_federate.py|fed_gridmock.py|helics_broker"
    pkill -15 -f "$citylab_procs" 2>/dev/null || true
    sleep 0.2
    pkill -9 -f "$citylab_procs" 2>/dev/null || true
    # Cleanup topology & egress iptables rules
    python3 -c 'import sys; sys.path.insert(0, "."); from network.topology import teardown_topology_and_daemons; teardown_topology_and_daemons()' 2>/dev/null || true
    c_info "Limpiando estado de Mininet / Open vSwitch (mn -c)..."
    mn -c >/dev/null 2>&1 || true
    c_info "Laboratorio detenido."
}

cmd_smoke() {
    local phase=7
    while [ $# -gt 0 ]; do
        case "$1" in
            --phase) phase="${2:-7}"; shift 2 ;;
            *) c_err "Opción desconocida para 'smoke': $1"; exit 2 ;;
        esac
    done
    local script="$BASE_DIR/helics_sim/smoke_test_phase${phase}.sh"
    if [ ! -f "$script" ]; then
        c_err "No hay smoke test para la fase $phase ($script)."
        exit 2
    fi
    if ! command -v helics_broker >/dev/null 2>&1; then
        c_err "helics_broker no está en PATH: la co-simulación no puede arrancar."
        exit 1
    fi
    c_info "Co-simulación HELICS — smoke fase $phase (sin root)"
    bash "$script"
}

cmd_test() {
    c_info "Ejecutando suite de pruebas unitarias (sin root)"
    if [ $# -gt 0 ]; then
        python3 -m pytest "$@"
    else
        python3 -m pytest network/tests plc/tests physical helics_sim attacker/tests -q
    fi
}

cmd_profile() {
    c_info "Midiendo recursos reales de los procesos CityLab en ejecución"
    python3 "$BASE_DIR/scripts/profile_resources.py" "$@"
}

cmd_status() {
    c_info "Componentes CityLab en ejecución:"
    local found=0
    local patterns=(
        helics_broker fed_icssim fed_transport fed_hospital fed_logger fed_desal
        fed_lighting fed_sis fed_viz_bridge gridlabd_federate modbus_emulator dnp3_emulator
        iec61850_emulator opcua_emulator honeypot_server ad_dc_emulator
        modbus_proxy scada_server hmi_server viz_server siem_pipeline sdn_controller
    )
    for pat in "${patterns[@]}"; do
        local n
        n=$(pgrep -c -f "$pat" 2>/dev/null || true)
        n=${n:-0}
        if [ "$n" -gt 0 ]; then
            printf '  %-22s %s proceso(s)\n' "$pat" "$n"
            found=$((found + n))
        fi
    done
    if [ "$found" -eq 0 ]; then
        echo "  (ninguno)"
    fi
    if command -v ovs-vsctl >/dev/null 2>&1 && [ "$(id -u)" -eq 0 ]; then
        echo
        c_info "Puentes Open vSwitch:"
        ovs-vsctl list-br 2>/dev/null | sed 's/^/  /' || echo "  (ninguno)"
    fi
}

main() {
    local cmd="${1:-help}"
    shift || true
    case "$cmd" in
        up)      cmd_up "$@" ;;
        down)    cmd_down "$@" ;;
        smoke)   cmd_smoke "$@" ;;
        test)    cmd_test "$@" ;;
        profile) cmd_profile "$@" ;;
        status)  cmd_status "$@" ;;
        help|-h|--help) usage ;;
        *) c_err "Comando desconocido: $cmd"; echo; usage; exit 2 ;;
    esac
}

main "$@"
