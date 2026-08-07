#!/usr/bin/env python3
"""
Mininet topology for Phase 1 PoC (IEC 62443 segmentation)
Zones:
 - Corporate (10.0.1.0/24) -> attacker host
 - DMZ       (10.0.2.0/24) -> jump/historian host
 - OT        (10.0.3.0/24) -> plc, icssim hosts

A single user-space firewall host (fw) bridges the three switches and enforces
segmentation via iptables. The fw host will have three interfaces:
 - fw-eth0 -> Corporate (gw 10.0.1.1)
 - fw-eth1 -> DMZ       (gw 10.0.2.1)
 - fw-eth2 -> OT        (gw 10.0.3.1)

Usage (run as root):
  sudo python3 network/topology.py

"""
from __future__ import annotations

import argparse
import sys
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

        # Firewall host (will have 4 interfaces once linked)
        fw = self.addHost('fw')

        # Corporate hosts
        attacker = self.addHost('h_attacker', ip='10.0.1.10/24')
        corp_dc  = self.addHost('h_dc',       ip='10.0.1.20/24')

        # DMZ hosts
        dmz_jump     = self.addHost('h_dmz',   ip='10.0.2.10/24')
        scada_server = self.addHost('h_scada', ip='10.0.2.20/24')

        # Isolated EWS Zone (10.0.4.0/24)
        ews_station  = self.addHost('h_ews',   ip='10.0.4.30/24')

        # OT hosts: water (.10), icssim (.11), gas (.12), elec (.13), trans (.14), hosp (.15), honey (.99)
        plc_water = self.addHost('h_plc',        ip='10.0.3.10/24')
        icssim    = self.addHost('h_icssim',     ip='10.0.3.11/24')
        plc_gas   = self.addHost('h_plc_gas',    ip='10.0.3.12/24')
        plc_elec  = self.addHost('h_plc_elec',   ip='10.0.3.13/24')
        plc_trans = self.addHost('h_plc_trans',  ip='10.0.3.14/24')
        plc_hosp  = self.addHost('h_plc_hosp',   ip='10.0.3.15/24')
        plc_honey = self.addHost('h_plc_honey',  ip='10.0.3.99/24')

        # Links (order determines fw-eth names: eth0=corp, eth1=dmz, eth2=ot, eth3=ews)
        self.addLink(fw, s_corp)
        self.addLink(fw, s_dmz)
        self.addLink(fw, s_ot)
        self.addLink(fw, s_ews)

        # Connect switches to hosts
        self.addLink(s_corp, attacker)
        self.addLink(s_corp, corp_dc)
        self.addLink(s_dmz, dmz_jump)
        self.addLink(s_dmz, scada_server)
        self.addLink(s_ews, ews_station)
        self.addLink(s_ot, plc_water)
        self.addLink(s_ot, icssim)
        self.addLink(s_ot, plc_gas)
        self.addLink(s_ot, plc_elec)
        self.addLink(s_ot, plc_trans)
        self.addLink(s_ot, plc_hosp)
        self.addLink(s_ot, plc_honey)


def apply_fw_configuration(fw: Node) -> None:
    """Configure FW host interfaces, IP forwarding and iptables rules.

    Assumes interfaces: fw-eth0 (corp), fw-eth1 (dmz), fw-eth2 (ot), fw-eth3 (ews)
    """
    # Assign IPs to firewall interfaces
    fw.cmd('ip addr flush dev fw-eth0')
    fw.cmd('ip addr flush dev fw-eth1')
    fw.cmd('ip addr flush dev fw-eth2')
    fw.cmd('ip addr flush dev fw-eth3')

    fw.cmd('ip addr add 10.0.1.1/24 dev fw-eth0')
    fw.cmd('ip addr add 10.0.2.1/24 dev fw-eth1')
    fw.cmd('ip addr add 10.0.3.1/24 dev fw-eth2')
    fw.cmd('ip addr add 10.0.4.1/24 dev fw-eth3')

    # Enable IP forwarding
    fw.cmd('sysctl -w net.ipv4.ip_forward=1 > /dev/null')

    # Default DROP policy for forwarding (deny by default)
    fw.cmd('iptables -F')
    fw.cmd('iptables -P FORWARD DROP')

    # Allow established related
    fw.cmd("iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT")

    # Permit h_scada (10.0.2.20) and h_ews (10.0.4.30) -> OT Modbus/TCP (port 502)
    for plc_ip in ('10.0.3.10', '10.0.3.12', '10.0.3.13', '10.0.3.14', '10.0.3.15', '10.0.3.99'):
        fw.cmd(f"iptables -A FORWARD -i fw-eth1 -o fw-eth2 -s 10.0.2.20 -d {plc_ip} -p tcp --dport 502 -j ACCEPT")
        fw.cmd(f"iptables -A FORWARD -i fw-eth3 -o fw-eth2 -s 10.0.4.30 -d {plc_ip} -p tcp --dport 502 -j ACCEPT")

    # Permit h_scada and h_ews -> OT DNP3 (port 20000) for Electrical PLC (10.0.3.13)
    fw.cmd("iptables -A FORWARD -i fw-eth1 -o fw-eth2 -s 10.0.2.20 -d 10.0.3.13 -p tcp --dport 20000 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -i fw-eth3 -o fw-eth2 -s 10.0.4.30 -d 10.0.3.13 -p tcp --dport 20000 -j ACCEPT")

    # Permit Corporate (10.0.1.0/24) -> Isolated EWS Zone (10.0.4.30) ONLY via SSH (PAW Rule)
    fw.cmd("iptables -A FORWARD -i fw-eth0 -o fw-eth3 -d 10.0.4.30 -p tcp --dport 22 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -i fw-eth0 -o fw-eth1 -p tcp --dport 22 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -i fw-eth0 -o fw-eth1 -p icmp -j ACCEPT")

    # Explicitly block DMZ -> Isolated EWS Zone (10.0.4.0/24)
    fw.cmd("iptables -A FORWARD -i fw-eth1 -o fw-eth3 -j REJECT")

    # Explicitly block Corporate -> OT
    fw.cmd("iptables -A FORWARD -i fw-eth0 -o fw-eth2 -j REJECT")
    fw.cmd("iptables -A FORWARD -i fw-eth2 -o fw-eth0 -j REJECT")

    # Allow local host operations on fw
    fw.cmd("iptables -A INPUT -i lo -j ACCEPT")

    print('[*] Firewall configured (Zones: Corp 10.0.1.1, DMZ 10.0.2.1, OT 10.0.3.1, EWS PAW 10.0.4.1)')


def configure_host_routes(net: Mininet) -> None:
    """Set default routes on hosts to point to the FW gateway in each zone."""
    for corp_host in ('h_attacker', 'h_dc'):
        try:
            h = net.get(corp_host)
            h.cmd('ip route flush default')
            h.cmd('ip route add default via 10.0.1.1')
        except KeyError:
            pass

    for dmz_host in ('h_dmz', 'h_scada'):
        try:
            h = net.get(dmz_host)
            h.cmd('ip route flush default')
            h.cmd('ip route add default via 10.0.2.1')
        except KeyError:
            pass

    try:
        h_ews = net.get('h_ews')
        h_ews.cmd('ip route flush default')
        h_ews.cmd('ip route add default via 10.0.4.1')
    except KeyError:
        pass

    for ot_host in ('h_plc', 'h_icssim', 'h_plc_gas', 'h_plc_elec', 'h_plc_trans', 'h_plc_hosp', 'h_plc_honey'):
        try:
            h = net.get(ot_host)
            h.cmd('ip route flush default')
            h.cmd('ip route add default via 10.0.3.1')
        except KeyError:
            pass

    print('[*] Host default routes configured to use FW as gateway')


def run_connectivity_tests(net: Mininet) -> Dict[str, bool]:
    """Run minimal connectivity checks and return statuses.

    Tests:
    - Attacker -> PLC (ICMP) should FAIL (segmentation)
    - DMZ -> PLC (TCP port 502) should SUCCEED (allowed Modbus)
    - DMZ -> Electrical PLC (TCP port 20000) should SUCCEED (allowed DNP3)
    - Attacker -> Corporate DC (TCP port 88/389) should SUCCEED (Corporate internal)
    - DMZ -> Attacker (icmp) should SUCCEED (management allowed)
    """
    results: Dict[str, bool] = {}
    attacker = net.get('h_attacker')
    dmz = net.get('h_dmz')
    plc = net.get('h_plc')

    print('[*] Testing: Attacker -> PLC (ping) - expected: BLOCKED')
    out = attacker.cmd('ping -c1 -W1 10.0.3.10')
    results['attacker_ping_plc'] = ('1 packets transmitted, 1 received' in out)

    print('[*] Testing: DMZ -> PLC (tcp:502) - expected: ALLOWED (if PLC listens)')
    tcp_test = dmz.cmd("timeout 1 bash -c '</dev/tcp/10.0.3.10/502' && echo open || echo closed'")
    results['dmz_modbus_502'] = ('open' in tcp_test)

    print('[*] Testing: DMZ -> Electrical PLC (tcp:20000 DNP3) - expected: ALLOWED')
    dnp3_test = dmz.cmd("timeout 1 bash -c '</dev/tcp/10.0.3.13/20000' && echo open || echo closed'")
    results['dmz_dnp3_20000'] = ('open' in dnp3_test)

    print('[*] Testing: Attacker -> Corporate DC (tcp:88 Kerberos) - expected: ALLOWED')
    kdc_test = attacker.cmd("timeout 1 bash -c '</dev/tcp/10.0.1.20/88' && echo open || echo closed'")
    results['attacker_kdc_88'] = ('open' in kdc_test)

    print('[*] Testing: DMZ -> Attacker (ping) - expected: ALLOWED')
    out2 = dmz.cmd('ping -c1 -W1 10.0.1.10')
    results['dmz_ping_attacker'] = ('1 packets transmitted, 1 received' in out2)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description='Start Mininet IEC62443 PoC topology')
    parser.add_argument('--test', action='store_true', help='Run automated connectivity tests and exit')
    args = parser.parse_args()

    topo = Iec62443Topo()
    net = Mininet(topo=topo, controller=OVSController, switch=OVSKernelSwitch, link=TCLink, autoSetMacs=True)

    print('[*] Starting network... (requires root)')
    net.start()

    # Force standalone mode so OVS switches learn MACs/ARP without an external controller.
    for sw in ('s1', 's2', 's3'):
        net.get(sw).cmd(f'ovs-vsctl set-fail-mode {sw} standalone')

    # Configure switch s3 interface on the host to allow host processes to communicate with OT devices.
    os.system('ip addr add 10.0.3.2/24 dev s3 2>/dev/null || true')
    os.system('ip link set s3 up')

    fw = net.get('fw')
    apply_fw_configuration(fw)
    configure_host_routes(net)

    # Auto-start services
    try:
        auto_plc = os.environ.get('AUTO_START_PLC', '1')
    except Exception:
        auto_plc = '1'
    if auto_plc == '1':
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        emulator = os.path.join(repo_root, 'plc', 'modbus_emulator.py')
        dnp3_script = os.path.join(repo_root, 'plc', 'dnp3_emulator.py')
        ad_script = os.path.join(repo_root, 'network', 'ad_dc_emulator.py')

        # Auto-start Corporate DC (h_dc @ 10.0.1.20)
        try:
            h_dc = net.get('h_dc')
            h_dc.cmd(f'python3 {ad_script} > /tmp/h_dc.log 2>&1 &')
            print('[*] h_dc (10.0.1.20): Samba AD DC emulator spawned on :88, :389, :445')
        except Exception as exc:
            print(f'[WARN] h_dc auto-start skipped: {exc}')

        # (host_name, plant_type) — mismo puerto 502, IPs aisladas por Mininet
        plc_hosts = [
            ('h_plc',        'water'),
            ('h_plc_gas',    'gas'),
            ('h_plc_elec',   'elec'),
            ('h_plc_trans',  'transport'),
            ('h_plc_hosp',   'elec'),
            ('h_plc_honey',  'water'),
        ]
        for host_name, plant_type in plc_hosts:
            try:
                h = net.get(host_name)
                cmd = f'python3 {emulator} --plant-type {plant_type} > /tmp/{host_name}.log 2>&1 &'
                h.cmd(cmd)
                print(f'[*] {host_name} ({plant_type}): modbus_emulator spawned on :502')

                # Spawn DNP3 Outstation on h_plc_elec (10.0.3.13:20000)
                if host_name == 'h_plc_elec':
                    h.cmd(f'python3 {dnp3_script} --port 20000 > /tmp/h_plc_elec_dnp3.log 2>&1 &')
                    print('[*] h_plc_elec (10.0.3.13): dnp3_emulator spawned on :20000')
            except KeyError:
                print(f'[WARN] {host_name} not present; skipping')
            except Exception as exc:
                print(f'[ERROR] {host_name}: {exc}')

        # Auto-start SCADA Server en DMZ (h_scada @ 10.0.2.20:8080)
        try:
            scada = net.get('h_scada')
            scada_script = os.path.join(repo_root, 'network', 'scada_server.py')
            scada.cmd(f'python3 {scada_script} > /tmp/h_scada.log 2>&1 &')
            print('[*] h_scada (10.0.2.20): scada_server spawned on :8080')
        except Exception as exc:
            print(f'[WARN] h_scada auto-start skipped: {exc}')

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
        return 0 if not results['attacker_ping_plc'] else 2

    print('[*] Mininet CLI activa. Pruebas: sudo python3 network/topology.py --test')
    CustomCLI(net)
    net.stop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
