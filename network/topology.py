#!/usr/bin/env python3
"""
Mininet topology for Phase 1 PoC (IEC 62443 segmentation)
Zones:
 - Corporate (10.0.1.0/24) -> attacker, dc hosts
 - DMZ       (10.0.2.0/24) -> jump, scada historian hosts
 - OT        (10.0.3.0/24) -> plcs, icssim hosts
 - EWS PAW   (10.0.4.0/24) -> engineering workstation host
 - Honeypot  (10.0.5.0/24) -> decoy honeypot host

A single user-space firewall host (fw) bridges the five switches and enforces
segmentation via iptables. The fw host will have five interfaces:
 - fw-eth0 -> Corporate (gw 10.0.1.1)
 - fw-eth1 -> DMZ       (gw 10.0.2.1)
 - fw-eth2 -> OT        (gw 10.0.3.1)
 - fw-eth3 -> EWS PAW   (gw 10.0.4.1)
 - fw-eth4 -> Honeypot  (gw 10.0.5.1)

Usage (run as root):
  sudo python3 network/topology.py

"""
from __future__ import annotations

import argparse
import sys
import time
from typing import Dict

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch, OVSController
from mininet.topo import Topo
import os

# Custom CLI that shortens pingall duration using MININET_PING_TIMEOUT (seconds)
class CustomCLI(CLI):
    """CLI subclass that overrides pingall to use a shorter timeout driven by env var.

    Use:
      export MININET_PING_TIMEOUT=0.5
    or set it from run_phase1.sh to reduce how long 'pingall' blocks.
    """
    def do_pingall(self, line: str) -> None:  # type: ignore[override]
        try:
            timeout = float(os.environ.get('MININET_PING_TIMEOUT', '1'))
        except ValueError:
            timeout = 1.0
        print(f'*** Ping: testing ping reachability (timeout={timeout}s)')
        # Mininet's pingAll accepts a timeout param (seconds) in most versions
        try:
            self.mn.pingAll(timeout=timeout)
        except TypeError:
            # Fallback: call the base implementation if signature differs
            super().do_pingall(line)


class Iec62443Topo(Topo):
    """Custom Mininet topology implementing segmented zones and a routing FW host."""

    def build(self) -> None:
        # Switches per zone
        s_corp = self.addSwitch('s1')
        s_dmz  = self.addSwitch('s2')
        s_ot   = self.addSwitch('s3')
        s_ews  = self.addSwitch('s4')  # Isolated EWS PAW Zone
        s_honey = self.addSwitch('s5') # Honeypot observation VLAN

        # Isolated EWS PAW Zone
        ews = self.addHost('h_ews', ip='10.0.4.30/24')

        # Firewall host (will have 5 interfaces once linked)
        fw = self.addHost('fw')

        # Corporate hosts
        attacker = self.addHost('h_attacker', ip='10.0.1.10/24')
        dc       = self.addHost('h_dc',       ip='10.0.1.20/24')

        # DMZ hosts
        dmz_jump = self.addHost('h_dmz', ip='10.0.2.10/24')
        scada_server = self.addHost('h_scada', ip='10.0.2.20/24')

        # OT hosts: water (10.0.3.10), gas (10.0.3.12), elec (10.0.3.13), trans (10.0.3.14), hosp (10.0.3.15), desal (10.0.3.16), lighting (10.0.3.17), ied (10.0.3.20), gateway (10.0.3.30)
        plc_water = self.addHost('h_plc',        ip='10.0.3.10/24')
        icssim    = self.addHost('h_icssim',     ip='10.0.3.11/24')
        plc_gas   = self.addHost('h_plc_gas',    ip='10.0.3.12/24')
        plc_elec  = self.addHost('h_plc_elec',   ip='10.0.3.13/24')
        plc_trans = self.addHost('h_plc_tr',     ip='10.0.3.14/24')
        plc_hosp  = self.addHost('h_plc_hosp',   ip='10.0.3.15/24')
        plc_desal = self.addHost('h_desal',      ip='10.0.3.16/24')
        plc_light = self.addHost('h_lighting',   ip='10.0.3.17/24')
        ied_subst = self.addHost('h_ied',        ip='10.0.3.20/24')
        gw_telem  = self.addHost('h_gateway',    ip='10.0.3.30/24')
        plc_honey = self.addHost('h_honey',      ip='10.0.5.99/24')

        # Links (order determines fw-eth names: eth0=corp, eth1=dmz, eth2=ot, eth3=ews, eth4=honey)
        self.addLink(fw, s_corp)
        self.addLink(fw, s_dmz)
        self.addLink(fw, s_ot)
        self.addLink(fw, s_ews)
        self.addLink(fw, s_honey)

        # Connect switches to hosts
        self.addLink(s_corp, attacker)
        self.addLink(s_corp, dc)
        self.addLink(s_dmz, dmz_jump)
        self.addLink(s_dmz, scada_server)
        self.addLink(s_ot, plc_water)
        self.addLink(s_ot, icssim)
        self.addLink(s_ot, plc_gas)
        self.addLink(s_ot, plc_elec)
        self.addLink(s_ot, plc_trans)
        self.addLink(s_ot, plc_hosp)
        self.addLink(s_ot, plc_desal)
        self.addLink(s_ot, plc_light)
        self.addLink(s_ot, ied_subst)
        self.addLink(s_ot, gw_telem)
        self.addLink(s_ews, ews)
        self.addLink(s_honey, plc_honey)


def apply_fw_configuration(fw: Node) -> None:
    """Configure FW host interfaces, IP forwarding and iptables rules.

    Assumes interfaces: fw-eth0 (corp), fw-eth1 (dmz), fw-eth2 (ot), fw-eth3 (ews), fw-eth4 (honey)
    """
    # Assign IPs to firewall interfaces
    fw.cmd('ip addr flush dev fw-eth0')
    fw.cmd('ip addr flush dev fw-eth1')
    fw.cmd('ip addr flush dev fw-eth2')
    fw.cmd('ip addr flush dev fw-eth3')
    fw.cmd('ip addr flush dev fw-eth4')

    fw.cmd('ip addr add 10.0.1.1/24 dev fw-eth0')
    fw.cmd('ip addr add 10.0.2.1/24 dev fw-eth1')
    fw.cmd('ip addr add 10.0.3.1/24 dev fw-eth2')
    fw.cmd('ip addr add 10.0.4.1/24 dev fw-eth3')
    fw.cmd('ip addr add 10.0.5.1/24 dev fw-eth4')

    for intf in ('fw-eth0', 'fw-eth1', 'fw-eth2', 'fw-eth3', 'fw-eth4'):
        fw.cmd(f'ip link set dev {intf} up')

    # Enable IP forwarding and disable rp_filter for multihomed routing
    fw.cmd('sysctl -w net.ipv4.ip_forward=1 > /dev/null')
    fw.cmd('sysctl -w net.ipv4.conf.all.rp_filter=0 > /dev/null')
    fw.cmd('sysctl -w net.ipv4.conf.default.rp_filter=0 > /dev/null')
    for intf in ('fw-eth0', 'fw-eth1', 'fw-eth2', 'fw-eth3', 'fw-eth4'):
        fw.cmd(f'sysctl -w net.ipv4.conf.{intf}.rp_filter=0 > /dev/null')

    # Default DROP policy for forwarding (deny by default)
    fw.cmd('iptables -F')
    fw.cmd('iptables -P FORWARD DROP')

    # Allow established/related connections
    fw.cmd("iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || true")

    # 1. Allow DMZ SCADA (10.0.2.20) <-> OT Zone (10.0.3.0/24)
    fw.cmd("iptables -A FORWARD -s 10.0.2.20 -d 10.0.3.0/24 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -s 10.0.3.0/24 -d 10.0.2.20 -j ACCEPT")

    # 2. Allow EWS PAW (10.0.4.30) <-> OT Zone (10.0.3.0/24)
    fw.cmd("iptables -A FORWARD -s 10.0.4.30 -d 10.0.3.0/24 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -s 10.0.3.0/24 -d 10.0.4.30 -j ACCEPT")

    # 3. Allow Corporate (10.0.1.0/24) <-> Corporate (10.0.1.0/24) & DMZ SSH / ICMP ping
    fw.cmd("iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.1.0/24 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -i fw-eth0 -o fw-eth1 -p tcp --dport 22 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -i fw-eth1 -o fw-eth0 -p tcp --sport 22 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -s 10.0.2.0/24 -d 10.0.1.0/24 -p icmp -j ACCEPT")
    fw.cmd("iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 -p icmp -j ACCEPT")
    # Allow DMZ SCADA (10.0.2.20) -> Corporate AD DC (10.0.1.20:389 TCP) for SCADA_AD_AUTH
    fw.cmd("iptables -A FORWARD -s 10.0.2.20 -d 10.0.1.20 -p tcp --dport 389 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -s 10.0.1.20 -d 10.0.2.20 -p tcp --sport 389 -j ACCEPT")

    # 4. Allow traffic to honeypot from anywhere to detect scanning
    fw.cmd("iptables -A FORWARD -d 10.0.5.99 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -s 10.0.5.99 -j ACCEPT")

    # 5. Explicitly block Corporate (10.0.1.0/24) -> OT Zone (10.0.3.0/24)
    fw.cmd("iptables -A FORWARD -i fw-eth0 -o fw-eth2 -j DROP")
    fw.cmd("iptables -A FORWARD -i fw-eth2 -o fw-eth0 -j DROP")

    # Allow local loopback on fw
    fw.cmd("iptables -A INPUT -i lo -j ACCEPT")

    print('[*] Firewall configured (fw IPs: 10.0.1.1, 10.0.2.1, 10.0.3.1)')


def configure_host_routes(net: Mininet) -> None:
    """Set default routes on hosts to point to the FW gateway in each zone."""
    for host in net.hosts:
        host.cmd('sysctl -w net.ipv4.conf.all.rp_filter=0 > /dev/null 2>&1 || true')
        host.cmd('sysctl -w net.ipv4.conf.default.rp_filter=0 > /dev/null 2>&1 || true')

    h_attacker = net.get('h_attacker')
    h_attacker.cmd('ip route flush default')
    h_attacker.cmd('ip route add default via 10.0.1.1')

    h_dc = net.get('h_dc')
    h_dc.cmd('ip route flush default')
    h_dc.cmd('ip route add default via 10.0.1.1')

    h_dmz = net.get('h_dmz')
    h_dmz.cmd('ip route flush default')
    h_dmz.cmd('ip route add default via 10.0.2.1')

    try:
        h_scada = net.get('h_scada')
        h_scada.cmd('ip route flush default')
        h_scada.cmd('ip route add default via 10.0.2.1')
    except KeyError:
        pass

    try:
        h_ews = net.get('h_ews')
        h_ews.cmd('ip route flush default')
        h_ews.cmd('ip route add default via 10.0.4.1')
    except KeyError:
        pass

    for ot_host in ('h_plc', 'h_icssim', 'h_plc_gas', 'h_plc_elec', 'h_plc_tr', 'h_plc_hosp', 'h_desal', 'h_lighting', 'h_ied', 'h_gateway'):
        try:
            h = net.get(ot_host)
            h.cmd('ip route flush default')
            h.cmd('ip route add default via 10.0.3.1')
        except KeyError:
            pass

    try:
        h_honey = net.get('h_honey')
        h_honey.cmd('ip route flush default')
        h_honey.cmd('ip route add default via 10.0.5.1')
    except KeyError:
        pass

    print('[*] Host default routes configured to use FW as gateway')


def run_connectivity_tests(net: Mininet) -> Dict[str, bool]:
    """Run L3/L4 firewall connectivity and conduit checks across all zones."""
    time.sleep(1.5)
    results: Dict[str, bool] = {}
    h_attacker = net.get('h_attacker')
    h_dmz = net.get('h_dmz')
    h_scada = net.get('h_scada')
    h_dc = net.get('h_dc')

    print('[*] Testing: Attacker -> PLC (ping) - expected: BLOCKED')
    out_ping = h_attacker.cmd('ping -c 1 -W 1 10.0.3.10')
    attacker_blocked = '100% packet loss' in out_ping or 'Destination Port Unreachable' in out_ping or '0 received' in out_ping or 'reject' in out_ping.lower()
    results['attacker_ping_plc_blocked'] = attacker_blocked

    print('[*] Testing: h_scada (DMZ) -> PLC (ping) - expected: ALLOWED')
    out_dmz_ot = h_scada.cmd('ping -c 1 -W 1 10.0.3.10')
    results['dmz_ping_plc_allowed'] = ('1 received' in out_dmz_ot or ('0% packet loss' in out_dmz_ot and '100% packet loss' not in out_dmz_ot))

    print('[*] Testing: DMZ -> Attacker (ping) - expected: ALLOWED')
    out2 = h_dmz.cmd('ping -c 1 -W 1 10.0.1.10')
    results['dmz_ping_attacker_allowed'] = ('1 received' in out2 or ('0% packet loss' in out2 and '100% packet loss' not in out2))

    print('[*] Testing: h_scada (10.0.2.20) -> h_dc (10.0.1.20:389 TCP LDAP) - expected: ALLOWED')
    out_ldap = h_scada.cmd('python3 -c "import socket\ntry:\n s=socket.socket(); s.settimeout(2.0); s.connect((\'10.0.1.20\', 389)); s.close(); print(\'LDAP_OK\')\nexcept Exception:\n print(\'LDAP_FAIL\')"')
    results['scada_to_dc_ldap_tcp389_allowed'] = 'LDAP_OK' in out_ldap

    print('[*] Testing: Attacker (10.0.1.10) -> PLC (10.0.3.10:502 Modbus) - expected: BLOCKED')
    out_atk_modbus = h_attacker.cmd('python3 -c "import socket\ntry:\n s=socket.socket(); s.settimeout(1.5); s.connect((\'10.0.3.10\', 502)); s.close(); print(\'MODBUS_LEAK\')\nexcept Exception:\n print(\'MODBUS_BLOCKED_OK\')"')
    results['attacker_to_plc_modbus_blocked'] = 'MODBUS_BLOCKED_OK' in out_atk_modbus

    print('[*] Testing: h_scada (10.0.2.20) -> PLC (10.0.3.10:502 Modbus) - expected: ALLOWED')
    out_scada_modbus = h_scada.cmd('python3 -c "import socket\ntry:\n s=socket.socket(); s.settimeout(2.0); s.connect((\'10.0.3.10\', 502)); s.close(); print(\'MODBUS_OK\')\nexcept Exception:\n print(\'MODBUS_FAIL\')"')
    results['scada_to_plc_modbus_allowed'] = 'MODBUS_OK' in out_scada_modbus

    print('[*] Testing: Attacker (10.0.1.10) -> Honeypot (10.0.5.99:502) - expected: ALLOWED')
    out_honey = h_attacker.cmd('python3 -c "import socket\ntry:\n s=socket.socket(); s.settimeout(2.0); s.connect((\'10.0.5.99\', 502)); s.close(); print(\'HONEY_OK\')\nexcept Exception:\n print(\'HONEY_FAIL\')"')
    results['attacker_to_honeypot_allowed'] = 'HONEY_OK' in out_honey

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description='CityLab IEC 62443 Cyber Range Topology')
    parser.add_argument('--test', action='store_true', help='Run automated connectivity tests and exit')
    args = parser.parse_args()

    topo = Iec62443Topo()
    net = Mininet(topo=topo, controller=OVSController, switch=OVSKernelSwitch, link=TCLink, autoSetMacs=True)

    print('[*] Starting network... (requires root)')
    net.start()

    # Configure OVS switches to standalone mode and add NORMAL fallback flow
    for sw_name in ('s1', 's2', 's3', 's4', 's5'):
        try:
            sw_node = net.get(sw_name)
            res1 = sw_node.cmd(f'ovs-vsctl set-fail-mode {sw_name} standalone')
            res2 = sw_node.cmd(f'ovs-ofctl add-flow {sw_name} "priority=0,actions=NORMAL"')
            if 'error' in res1.lower() or 'error' in res2.lower() or 'ovs-ofctl:' in res2.lower() or 'ovs-vsctl:' in res1.lower():
                print(f'[WARN] OVS command emitted error on {sw_name}: {res1.strip()} {res2.strip()}')
        except Exception as exc:
            print(f'[WARN] Fallo al configurar switch OVS {sw_name}: {exc}')

    # Configure switch s3 interface on the host to allow host processes (like fed_icssim.py)
    # to communicate with OT devices (like h_plc).
    os.system('ip addr add 10.0.3.2/24 dev s3 2>/dev/null || true')
    os.system('ip link set s3 up')

    fw = net.get('fw')
    apply_fw_configuration(fw)
    configure_host_routes(net)

    # Optionally auto-start PLC runtime & OT emulators inside Mininet hosts.
    try:
        auto_plc = os.environ.get('AUTO_START_PLC', '1')
    except Exception:
        auto_plc = '1'
    if auto_plc == '1':
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        py_bin = sys.executable
        emulator = os.path.join(repo_root, 'plc', 'modbus_emulator.py')
        siem_url = os.getenv('SIEM_HTTP_URL', 'http://10.0.2.20:8514')
        # (host_name, plant_type) — mismo puerto 502, IPs aisladas por Mininet
        plc_hosts = [
            ('h_plc',        'water'),
            ('h_plc_gas',    'gas'),
            ('h_plc_elec',   'elec'),
            ('h_plc_tr',     'transport'),
            ('h_plc_hosp',   'hospital'),
            ('h_desal',      'water'),
            ('h_lighting',   'elec'),
        ]
        for host_name, plant_type in plc_hosts:
            try:
                h = net.get(host_name)
                cmd = f'nohup env PYTHONPATH={repo_root} SIEM_HTTP_URL={siem_url} {py_bin} {emulator} --plant-type {plant_type} > /tmp/{host_name}.log 2>&1 &'
                h.cmd(cmd)
                print(f'[*] {host_name} ({plant_type}): modbus_emulator spawned on :502')
            except KeyError:
                print(f'[WARN] {host_name} not present; skipping')
            except Exception as exc:
                print(f'[ERROR] {host_name}: {exc}')

        # Auto-start DNP3 Outstation en h_plc_elec (10.0.3.13:20000)
        try:
            dnp3_script = os.path.join(repo_root, 'plc', 'dnp3_emulator.py')
            h_elec = net.get('h_plc_elec')
            h_elec.cmd(f'nohup env PYTHONPATH={repo_root} SIEM_HTTP_URL={siem_url} {py_bin} {dnp3_script} --host 0.0.0.0 --port 20000 > /tmp/h_plc_elec_dnp3.log 2>&1 &')
            print('[*] h_plc_elec (10.0.3.13): dnp3_emulator spawned on :20000')
        except Exception as exc:
            print(f'[WARN] DNP3 auto-start skipped: {exc}')

        # Auto-start IEC 61850 IED en h_ied (10.0.3.20:10102) con multicast GOOSE/SV (239.0.0.1 / 239.0.0.2)
        try:
            iec_script = os.path.join(repo_root, 'plc', 'iec61850_emulator.py')
            h_ied_node = net.get('h_ied')
            h_ied_node.cmd(f'nohup env PYTHONPATH={repo_root} SIEM_HTTP_URL={siem_url} ENABLE_MULTICAST=1 GOOSE_DEST=239.0.0.1 SV_DEST=239.0.0.2 {py_bin} {iec_script} --host 0.0.0.0 --goose-port 10102 --multicast > /tmp/h_ied.log 2>&1 &')
            print('[*] h_ied (10.0.3.20): iec61850_emulator spawned on :10102 (multicast 239.0.0.1/239.0.0.2)')
        except Exception as exc:
            print(f'[WARN] IEC 61850 auto-start skipped: {exc}')

        # Auto-start OPC UA Server en h_gateway (10.0.3.30:4840)
        try:
            opcua_script = os.path.join(repo_root, 'plc', 'opcua_emulator.py')
            h_gw_node = net.get('h_gateway')
            h_gw_node.cmd(f'nohup env PYTHONPATH={repo_root} SIEM_HTTP_URL={siem_url} {py_bin} {opcua_script} --host 0.0.0.0 --port 4840 > /tmp/h_gateway.log 2>&1 &')
            print('[*] h_gateway (10.0.3.30): opcua_emulator spawned on :4840')
        except Exception as exc:
            print(f'[WARN] OPC UA auto-start skipped: {exc}')

        # Auto-start Honeypot en h_honey (10.0.5.99:502)
        try:
            honey_script = os.path.join(repo_root, 'plc', 'honeypot_server.py')
            h_honey_node = net.get('h_honey')
            h_honey_node.cmd(f'nohup env PYTHONPATH={repo_root} SIEM_HTTP_URL={siem_url} {py_bin} {honey_script} --host 0.0.0.0 --port 502 > /tmp/h_honey.log 2>&1 &')
            print('[*] h_honey (10.0.5.99): honeypot_server daemon spawned on :502')
        except Exception as exc:
            print(f'[WARN] Honeypot auto-start skipped: {exc}')

        # Auto-start Samba AD DC Emulator en h_dc (10.0.1.20)
        try:
            dc_script = os.path.join(repo_root, 'network', 'ad_dc_emulator.py')
            h_dc_node = net.get('h_dc')
            h_dc_node.cmd(f'nohup env PYTHONPATH={repo_root} {py_bin} {dc_script} --host 0.0.0.0 > /tmp/h_dc.log 2>&1 &')
            print('[*] h_dc (10.0.1.20): ad_dc_emulator spawned on :88, :389, :445')
        except Exception as exc:
            print(f'[WARN] AD DC auto-start skipped: {exc}')

        # Auto-start Modbus DPI Proxy en DMZ (h_scada @ 10.0.2.20:15020)
        try:
            scada = net.get('h_scada')
            proxy_script = os.path.join(repo_root, 'network', 'modbus_proxy.py')
            scada.cmd(f'nohup env PYTHONPATH={repo_root} SIEM_HTTP_URL={siem_url} {py_bin} {proxy_script} --host 0.0.0.0 --port 15020 > /tmp/h_modbus_proxy.log 2>&1 &')
            print('[*] h_scada (10.0.2.20): modbus_proxy spawned on :15020')
        except Exception as exc:
            print(f'[WARN] modbus_proxy auto-start skipped: {exc}')

        # Auto-start SCADA Server en DMZ (h_scada @ 10.0.2.20:8080) con USE_MODBUS_PROXY=1
        try:
            use_proxy_env = os.getenv('USE_MODBUS_PROXY', '1')
            scada_script = os.path.join(repo_root, 'network', 'scada_server.py')
            scada.cmd(f'nohup env PYTHONPATH={repo_root} SIEM_HTTP_URL={siem_url} USE_MODBUS_PROXY={use_proxy_env} {py_bin} {scada_script} > /tmp/h_scada.log 2>&1 &')
            print(f'[*] h_scada (10.0.2.20): scada_server spawned on :8080 (USE_MODBUS_PROXY={use_proxy_env})')
        except Exception as exc:
            print(f'[WARN] h_scada auto-start skipped: {exc}')

        # Auto-start HMI Server en DMZ (h_scada @ 10.0.2.20:8085)
        try:
            hmi_script = os.path.join(repo_root, 'network', 'hmi_server.py')
            scada.cmd(f'nohup env PYTHONPATH={repo_root} {py_bin} {hmi_script} --port 8085 > /tmp/h_hmi.log 2>&1 &')
            print('[*] h_scada (10.0.2.20): hmi_server spawned on :8085')
        except Exception as exc:
            print(f'[WARN] hmi_server auto-start skipped: {exc}')

        # Auto-start Viz Server en DMZ (h_scada @ 10.0.2.20:8090)
        try:
            viz_script = os.path.join(repo_root, 'network', 'viz_server.py')
            scada.cmd(f'nohup env PYTHONPATH={repo_root} {py_bin} {viz_script} --port 8090 > /tmp/h_viz.log 2>&1 &')
            print('[*] h_scada (10.0.2.20): viz_server spawned on :8090')
        except Exception as exc:
            print(f'[WARN] viz_server auto-start skipped: {exc}')

        # Auto-start SOC / SIEM Central Pipeline en DMZ (h_scada @ 10.0.2.20:8514)
        try:
            siem_script = os.path.join(repo_root, 'network', 'siem_pipeline.py')
            scada.cmd(f'nohup env PYTHONPATH={repo_root} {py_bin} {siem_script} --host 0.0.0.0 --port 8514 > /tmp/h_siem.log 2>&1 &')
            print('[*] h_scada (10.0.2.20): siem_pipeline daemon spawned on :8514')
        except Exception as exc:
            print(f'[WARN] siem_pipeline auto-start skipped: {exc}')

    if args.test:
        try:
            results = run_connectivity_tests(net)
        except KeyError as exc:
            print(f'[ERROR] Test result key missing: {exc}')
            net.stop()
            return 1
        for k, v in results.items():
            print(f' - {k}: {"PASS" if v else "FAIL"}')
        net.stop()
        # Limpieza limpia de emuladores y daemons spawneados en modo test
        for pat in (
            'modbus_emulator.py', 'dnp3_emulator.py', 'iec61850_emulator.py',
            'opcua_emulator.py', 'honeypot_server.py', 'ad_dc_emulator.py',
            'modbus_proxy.py', 'scada_server.py', 'hmi_server.py',
            'viz_server.py', 'siem_pipeline.py'
        ):
            os.system(f"pkill -9 -f {pat} 2>/dev/null || true")
        return 0 if all(results.values()) else 2

    print('[*] Mininet CLI activa. Pruebas: sudo python3 network/topology.py --test')
    # Use CustomCLI to allow a shortened pingall via MININET_PING_TIMEOUT env var
    CustomCLI(net)
    net.stop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
