#!/usr/bin/env bash
# lab_terminal.sh — CityLab Cyber Range Interactive Terminal Launcher
# Provides full PTY-enabled interactive Bash shells for Mininet hosts (h_attacker, h_dmz, h_scada, h_ews).

set -euo pipefail

TARGET="${1:-attacker}"

get_host_pid() {
    local host_name="$1"
    # Find process ID of mininet host bash shell
    local pid
    pid=$(pgrep -f "mininet:${host_name}" | head -n1 || true)
    if [[ -z "$pid" ]]; then
        # Alternative lookup using ps/mnexec pattern
        pid=$(ps aux | grep -v grep | grep "mininet:${host_name}" | awk '{print $2}' | head -n1 || true)
    fi
    echo "$pid"
}

open_shell() {
    local host_name="$1"
    local pid
    pid=$(get_host_pid "$host_name")

    if [[ -z "$pid" ]]; then
        echo "[ERROR] Host '$host_name' is not currently running. Make sure CityLab is active (sudo ./run_phase3.sh)." >&2
        exit 1
    fi

    echo "[*] Connecting interactive PTY shell to $host_name (PID: $pid)..."
    echo "[*] Full terminal support active: clear, nano, vim, nmap, hydra, tshark, tmux enabled."
    echo "--------------------------------------------------------------------------------"
    
    # Run interactive bash inside network namespace with allocated PTY
    if [[ $EUID -ne 0 ]]; then
        exec sudo mnexec -a "$pid" env TERM=xterm-256color HOME="/root" PS1="[CityLab \h \W]\$ " bash --norc -i
    else
        exec mnexec -a "$pid" env TERM=xterm-256color HOME="/root" PS1="[CityLab \h \W]\$ " bash --norc -i
    fi
}

case "$TARGET" in
    attacker|h_attacker)
        open_shell "h_attacker"
        ;;
    dmz|h_dmz)
        open_shell "h_dmz"
        ;;
    scada|h_scada)
        open_shell "h_scada"
        ;;
    ews|h_ews)
        open_shell "h_ews"
        ;;
    attach|tmux)
        if ! command -v tmux >/dev/null 2>&1; then
            echo "[ERROR] tmux is not installed. Run install_deps.sh or use './lab_terminal.sh attacker'." >&2
            exit 1
        fi
        echo "[*] Spawning tmux Cyber Range Dashboard..."
        tmux new-session -d -s citylab "./lab_terminal.sh attacker"
        tmux split-window -h "./lab_terminal.sh dmz"
        tmux split-window -v "./lab_terminal.sh ews"
        tmux select-pane -t 0
        tmux split-window -v "./lab_terminal.sh scada"
        tmux select-layout tiled
        exec tmux attach-session -t citylab
        ;;
    *)
        echo "Usage: $0 {attacker|dmz|scada|ews|attach}"
        echo ""
        echo "Targets:"
        echo "  attacker : Open PTY terminal on h_attacker (10.0.1.10)"
        echo "  dmz      : Open PTY terminal on h_dmz (10.0.2.10)"
        echo "  scada    : Open PTY terminal on h_scada (10.0.2.20)"
        echo "  ews      : Open PTY terminal on h_ews (10.0.2.30)"
        echo "  attach   : Open multi-pane tmux Cyber Range dashboard"
        exit 1
        ;;
esac
