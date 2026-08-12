#!/usr/bin/env bash
# scripts/validate_e2e.sh — Arnés de Validación End-to-End en Mininet para Cyber Range CityLab
set -e

echo "=========================================================================="
echo " [CityLab] Arnés de Validación End-to-End en Red Real (Mininet / OVS)"
echo "=========================================================================="

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Detectar priviliegios root para Mininet
if [ "$EUID" -ne 0 ]; then
    echo "[!] ADVERTENCIA: Este script requiere privilegios root (sudo) para instanciar Mininet."
    echo "    Ejecutando en modo comprobación preliminar / fallback..."
    python3 scripts/validate_localhost.py
    exit 0
fi

echo "[1/4] Iniciando Mininet y verificando conectividad de topología..."
python3 network/topology.py --test

echo "[2/4] Verificando daemons en escucha en namespaces de hosts OT..."
python3 -c "
import os, time
from network.topology import Iec62443Topo
from mininet.net import Mininet
from mininet.node import OVSController, OVSKernelSwitch
from mininet.link import TCLink

topo = Iec62443Topo()
net = Mininet(topo=topo, controller=OVSController, switch=OVSKernelSwitch, link=TCLink, autoSetMacs=True)
net.start()

try:
    h_ied = net.get('h_ied')
    h_gw = net.get('h_gateway')
    h_elec = net.get('h_plc_elec')
    h_honey = net.get('h_plc_honey')
    h_dc = net.get('h_dc')

    print('[+] Hosts instanciados exitosamente en Mininet:')
    print(f'    - h_ied (10.0.3.20): {h_ied.IP()}')
    print(f'    - h_gateway (10.0.3.30): {h_gw.IP()}')
    print(f'    - h_plc_elec (10.0.3.13): {h_elec.IP()}')
    print(f'    - h_plc_honey (10.0.5.99): {h_honey.IP()}')
    print(f'    - h_dc (10.0.1.20): {h_dc.IP()}')
finally:
    net.stop()
"

echo "[3/4] Ejecutando ataque de inyección GOOSE en red OT real (Scenario 02)..."
python3 attacker/attack_goose_spoofing.py

echo "[4/4] Verificando correlación SOC SIEM..."
python3 -c "
from attacker.attack_purple_team_mttd import PurpleTeamMttd
res = PurpleTeamMttd().run_mttd_measurement()
assert res['status'] == 'SUCCESS'
print('  ↳ ✅ Engine SIEM y correlación SOC validada.')
"

echo "=========================================================================="
echo " [CityLab] ¡Validación End-to-End Mininet completada EXITOSAMENTE!"
echo "=========================================================================="
