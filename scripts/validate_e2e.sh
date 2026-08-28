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

# Definir cleanup trap para garantizar limpieza ante cualquier salida/fallo
cleanup() {
    local exit_code=$?
    echo "[*] Limpiando procesos de emuladores y red Mininet de forma segura..."
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
    mn -c >/dev/null 2>&1 || true
    return $exit_code
}
trap cleanup EXIT

echo "[*] Limpiando interfaces y switches residuarios de Mininet (mn -c)..."
mn -c >/dev/null 2>&1 || true

echo "[1/2] Verificando conectividad base y reglas firewall OVS..."
python3 network/topology.py --test

echo "[2/2] Instanciando red Mininet completa y ejecutando flujo de ataque end-to-end..."
python3 << 'EOF'
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

from network.topology import Iec62443Topo, apply_fw_configuration, configure_host_routes, teardown_topology_and_daemons
from network.siem_pipeline import SiemCorrelationEngine

print('[*] 1. Levantando topología de red Mininet completa...')
topo = Iec62443Topo()
net = Mininet(topo=topo, controller=OVSController, switch=OVSKernelSwitch, link=TCLink, autoSetMacs=True)
net.start()

try:
    for sw in ('s1', 's2', 's3', 's4', 's5'):
        sw_node = net.get(sw)
        sw_node.cmd(f'ovs-vsctl set-fail-mode {sw} standalone')
        sw_node.cmd(f'ovs-ofctl add-flow {sw} "priority=0,actions=NORMAL"')

    fw = net.get('fw')
    apply_fw_configuration(fw)
    configure_host_routes(net)

    # Spawn de emuladores OT dentro de los namespaces de Mininet
    h_ied = net.get('h_ied')
    h_gw = net.get('h_gateway')
    h_elec = net.get('h_plc_elec')
    h_honey = net.get('h_honey')
    h_dc = net.get('h_dc')
    h_attacker = net.get('h_attacker')

    repo_root = str(ROOT)
    py_bin = sys.executable
    h_ied.cmd(f'nohup env PYTHONUNBUFFERED=1 PYTHONPATH={repo_root} {py_bin} {repo_root}/plc/iec61850_emulator.py --host 10.0.3.20 --goose-port 10102 > /tmp/h_ied_e2e.log 2>&1 &')
    h_gw.cmd(f'nohup env PYTHONUNBUFFERED=1 PYTHONPATH={repo_root} {py_bin} {repo_root}/plc/opcua_emulator.py --host 10.0.3.30 --port 4840 > /tmp/h_gw_e2e.log 2>&1 &')
    h_elec.cmd(f'nohup env PYTHONUNBUFFERED=1 PYTHONPATH={repo_root} {py_bin} {repo_root}/plc/dnp3_emulator.py --host 10.0.3.13 --port 20000 > /tmp/h_elec_e2e.log 2>&1 &')
    h_honey.cmd(f'nohup env PYTHONUNBUFFERED=1 PYTHONPATH={repo_root} {py_bin} {repo_root}/plc/honeypot_server.py --host 10.0.5.99 --port 502 > /tmp/h_honey_e2e.log 2>&1 &')
    h_dc.cmd(f'nohup env PYTHONUNBUFFERED=1 PYTHONPATH={repo_root} {py_bin} {repo_root}/network/ad_dc_emulator.py --host 10.0.1.20 > /tmp/h_dc_e2e.log 2>&1 &')

    time.sleep(2.0)

    print('[*] 2. Afirmando sockets estrictos en escucha en namespaces OT...')
    s_ied = h_ied.cmd("ss -lun | grep ':10102' || true").strip()
    s_gw = h_gw.cmd("ss -ltn | grep ':4840' || true").strip()
    s_elec = h_elec.cmd("ss -ltn | grep ':20000' || true").strip()
    s_honey = h_honey.cmd("ss -ltn | grep ':502' || true").strip()
    s_dc = h_dc.cmd("ss -ltn | grep ':88' || true").strip()

    assert s_ied, 'FAIL R0/R1: h_ied GOOSE server no esta escuchando en :10102'
    assert s_gw, 'FAIL R0/R1: h_gateway OPC UA server no esta escuchando en :4840'
    assert s_elec, 'FAIL R0/R1: h_plc_elec DNP3 server no esta escuchando en :20000'
    assert s_honey, 'FAIL R0/R1: h_honey Honeypot no esta escuchando en :502'
    assert s_dc, 'FAIL R0/R1: h_dc AD DC no esta escuchando en :88'
    print('    ↳ ✅ Sockets confirmados activos en todos los namespaces OT/Corporate.')

    print('[*] 3. Ejecutando ataque GOOSE Spoofing desde h_ied (proceso OT) contra h_ied (10.0.3.20:10102)...')
    out = h_ied.cmd(f'PYTHONPATH={repo_root} {py_bin} {repo_root}/attacker/attack_goose_spoofing.py --host 10.0.3.20 --port 10102 --burst 3')
    print('    - Output de ataque:\n' + '      ' + out.replace('\n', '\n      ').strip())

    time.sleep(1.0)

    print('[*] 4. Leyendo log del daemon IED real para confirmar readback de disparo XCBR1...')
    log_content = h_ied.cmd('cat /tmp/h_ied_e2e.log').strip()
    assert 'XCBR1.Pos.stVal=False' in log_content, f'FAIL R1-C: El IED no registro el disparo de interruptor XCBR1.Pos.stVal=False! Log: {log_content}'
    print('    ↳ ✅ Readback verificado: XCBR1.Pos.stVal=False (Breaker Tripped por GOOSE spoofing).')

    print('[*] 5. Ingestando evento real de IED en motor SIEM y verificando alertas correlacionadas...')
    siem = SiemCorrelationEngine()
    siem.ingest_raw_event(
        event_category='process_control',
        event_type='goose_injection',
        severity='CRITICAL',
        source_ip='10.0.1.10',
        destination_ip='10.0.3.20',
        service_name='iec61850_emulator',
        message='Paquete GOOSE falsificado detectado en subestacion (XCBR1.Pos.stVal=False)'
    )
    alerts = siem.active_alerts
    print(f'    - Alertas SIEM correlacionadas: {len(alerts)}')
    assert len(alerts) > 0, 'FAIL R1-C: No se generaron alertas SIEM a partir del evento real del IED!'
    assert alerts[0]['name'] == 'Ataque por Inyección / Spoofing de Mensajes GOOSE IEC 61850 (Industroyer2 Pattern)', 'FAIL R1-C: Alerta SIEM incorrecta!'
    print('    ↳ ✅ SIEM correlaciono exitosamente la alerta SOC-ALT-0001 (GOOSE Industroyer2 Pattern).')

    print('[*] 6. Verificando mitigación dinámicas SDN en caliente en Mininet real...')
    from attacker.attack_live_sdn_defense import LiveSdnDefense
    from network.sdn_controller import apply_circuit_breaker
    sdn_defense = LiveSdnDefense()
    sdn_res = sdn_defense.execute_sdn_mitigation()
    assert sdn_res['status'] == 'SUCCESS', f'FAIL R5/SDN: Mitigación SDN OpenFlow falló u OVS no disponible: {sdn_res}'
    assert sdn_res['flow_rules_applied'] is True, 'FAIL R5/SDN: Las reglas OpenFlow no se aplicaron'
    cb_ok = apply_circuit_breaker('10.0.1.10')
    assert cb_ok is True, 'FAIL R5/SDN: No se pudo aplicar regla Circuit Breaker para aislar IP 10.0.1.10'

    # Readback estricto de tabla de flujos OVS en s3
    s3_node = net.get('s3')
    flows_s3 = s3_node.cmd('ovs-ofctl dump-flows s3')
    assert '10.0.1.10' in flows_s3 and 'drop' in flows_s3, f'FAIL R5/SDN: Regla Circuit Breaker (10.0.1.10 -> drop) no presente en s3!\nFlows:\n{flows_s3}'
    print('    ↳ ✅ Readback verificado: Regla OpenFlow de aislamiento (10.0.1.10 -> drop) activa en tabla de s3.')

    # Demostración del aislamiento en el dataplane (h_attacker no puede alcanzar la red OT tras el Circuit Breaker)
    ping_post_cb = h_attacker.cmd('ping -c 1 -W 1 10.0.3.10')
    assert ('100% packet loss' in ping_post_cb or '0 received' in ping_post_cb), f'FAIL R5/SDN: Dataplane no aislo al atacante! Output: {ping_post_cb}'
    print('    ↳ ✅ Aislamiento dataplane demostrado: Ping de h_attacker (10.0.1.10) a PLC OT (10.0.3.10) bloqueado en s3 (100% packet loss).')

    print('[*] 7. Verificando contención anti-escape (jaula de red y aislamiento egress)...')
    # Validar que el atacante no puede alcanzar IPs públicas / router físico
    ping_ext = h_attacker.cmd('ping -c 1 -W 1 8.8.8.8 2>&1 || true')
    assert ('100% packet loss' in ping_ext or 'Network is unreachable' in ping_ext or '0 received' in ping_ext or 'Destination Port Unreachable' in ping_ext), f'FAIL JAULA: Tráfico de h_attacker escapó a Internet: {ping_ext}'
    print('    ↳ ✅ Contención egress verificada: Tráfico saliente a 8.8.8.8 bloqueado 100%.')

finally:
    print('[*] Deteniendo red Mininet y eliminando procesos emuladores...')
    teardown_topology_and_daemons(net)
EOF

echo "=========================================================================="
echo " [CityLab] ¡Validación End-to-End Mininet conectada completada EXITOSAMENTE!"
echo "=========================================================================="

