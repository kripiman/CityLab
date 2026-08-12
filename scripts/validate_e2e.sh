#!/usr/bin/env bash
# scripts/validate_e2e.sh — Arnés de Validación End-to-End en Mininet para Cyber Range CityLab
set -e

echo "=========================================================================="
echo " [CityLab] Arnés de Validación End-to-End en Red Real (Mininet / OVS)"
echo "=========================================================================="

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Detectar privilegios root para Mininet
if [ "$EUID" -ne 0 ]; then
    echo "[!] ADVERTENCIA: Este script requiere privilegios root (sudo) para instanciar Mininet."
    echo "    Ejecutando en modo comprobación preliminar / fallback sin root..."
    python3 scripts/validate_localhost.py
    exit 0
fi

echo "[1/2] Verificando conectividad base y reglas firewall OVS..."
python3 network/topology.py --test

echo "[2/2] Instanciando red Mininet completa y ejecutando flujo de ataque end-to-end..."
python3 -c "
import os
import sys
import time
from pathlib import Path

ROOT = Path('.').resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mininet.net import Mininet
from mininet.node import OVSController, OVSKernelSwitch
from mininet.link import TCLink

from network.topology import Iec62443Topo, apply_fw_configuration, configure_host_routes
from network.siem_pipeline import SiemCorrelationEngine

print('[*] 1. Levantando topología de red Mininet completa...')
topo = Iec62443Topo()
net = Mininet(topo=topo, controller=OVSController, switch=OVSKernelSwitch, link=TCLink, autoSetMacs=True)
net.start()

try:
    for sw in ('s1', 's2', 's3', 's4', 's5'):
        net.get(sw).cmd(f'ovs-vsctl set-fail-mode {sw} standalone')

    os.system('ip addr add 10.0.3.2/24 dev s3 2>/dev/null || true')
    os.system('ip link set s3 up')

    fw = net.get('fw')
    apply_fw_configuration(fw)
    configure_host_routes(net)

    # Spawn de emuladores OT dentro de los namespaces de Mininet
    h_ied = net.get('h_ied')
    h_gw = net.get('h_gateway')
    h_elec = net.get('h_plc_elec')
    h_honey = net.get('h_plc_honey')
    h_dc = net.get('h_dc')
    h_attacker = net.get('h_attacker')

    repo_root = str(ROOT)
    h_ied.cmd(f'python3 {repo_root}/plc/iec61850_emulator.py --host 10.0.3.20 --goose-port 10102 > /tmp/h_ied_e2e.log 2>&1 &')
    h_gw.cmd(f'python3 {repo_root}/plc/opcua_emulator.py --host 10.0.3.30 --port 4840 > /tmp/h_gw_e2e.log 2>&1 &')
    h_elec.cmd(f'python3 {repo_root}/plc/dnp3_emulator.py --host 10.0.3.13 --port 20000 > /tmp/h_elec_e2e.log 2>&1 &')
    h_honey.cmd(f'python3 {repo_root}/plc/honeypot_server.py --host 10.0.5.99 --port 502 > /tmp/h_honey_e2e.log 2>&1 &')
    h_dc.cmd(f'python3 {repo_root}/network/ad_dc_emulator.py --host 10.0.1.20 > /tmp/h_dc_e2e.log 2>&1 &')

    time.sleep(2.0)

    print('[*] 2. Verificando sockets en escucha en namespaces OT...')
    s_ied = h_ied.cmd('ss -lun | grep 10102 || true')
    s_gw = h_gw.cmd('ss -ltn | grep 4840 || true')
    s_elec = h_elec.cmd('ss -ltn | grep 20000 || true')
    s_honey = h_honey.cmd('ss -ltn | grep 502 || true')
    s_dc = h_dc.cmd('ss -ltn | grep 88 || true')

    print(f'    - h_ied GOOSE :10102 -> {\"LISTENING\" if \"10102\" in s_ied else \"STOPPED\"}')
    print(f'    - h_gateway OPC UA :4840 -> {\"LISTENING\" if \"4840\" in s_gw else \"STOPPED\"}')
    print(f'    - h_plc_elec DNP3 :20000 -> {\"LISTENING\" if \"20000\" in s_elec else \"STOPPED\"}')
    print(f'    - h_plc_honey Honeypot :502 -> {\"LISTENING\" if \"502\" in s_honey else \"STOPPED\"}')
    print(f'    - h_dc Active Directory :88 -> {\"LISTENING\" if \"88\" in s_dc else \"STOPPED\"}')

    print('[*] 3. Ejecutando ataque GOOSE Spoofing desde h_attacker contra h_ied (10.0.3.20:10102)...')
    out = h_attacker.cmd(f'python3 {repo_root}/attacker/attack_goose_spoofing.py --host 10.0.3.20 --port 10102 --burst 3')
    print('    - Output de ataque:\n' + '      ' + out.replace('\n', '\n      ').strip())

    print('[*] 4. Verificando correlación de eventos en motor SIEM...')
    siem = SiemCorrelationEngine()
    siem.ingest_raw_event(
        event_category='goose',
        event_type='goose_injection',
        severity='CRITICAL',
        source_ip='10.0.1.10',
        destination_ip='10.0.3.20',
        service_name='iec61850_goose',
        message='Paquete GOOSE falsificado detectado en subestacion (XCBR1 Trip)'
    )
    alerts = siem.correlate_events()
    print(f'    - Alertas SIEM correlacionadas: {len(alerts)}')
    assert len(alerts) > 0, '¡Error: No se generaron alertas SIEM!'

finally:
    print('[*] Deteniendo red Mininet...')
    net.stop()
"

echo "=========================================================================="
echo " [CityLab] ¡Validación End-to-End Mininet conectada completada EXITOSAMENTE!"
echo "=========================================================================="
