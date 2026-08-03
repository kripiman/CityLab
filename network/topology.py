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
        s_dmz = self.addSwitch('s2')
        s_ot = self.addSwitch('s3')

        # Firewall host (will have 3 interfaces once linked)
        fw = self.addHost('fw')

        # Corporate hosts
        attacker = self.addHost('h_attacker', ip='10.0.1.10/24')

        # DMZ hosts
        dmz_jump = self.addHost('h_dmz', ip='10.0.2.10/24')

        # OT hosts (PLC + ICSSIM)
        plc = self.addHost('h_plc', ip='10.0.3.10/24')
        icssim = self.addHost('h_icssim', ip='10.0.3.11/24')

        # Links (order determines fw-eth names)
        # Connect fw to corp, dmz, ot in that exact order so interface names are predictable
        self.addLink(fw, s_corp)
        self.addLink(fw, s_dmz)
        self.addLink(fw, s_ot)

        # Connect switches to hosts
        self.addLink(s_corp, attacker)
        self.addLink(s_dmz, dmz_jump)
        self.addLink(s_ot, plc)
        self.addLink(s_ot, icssim)


def apply_fw_configuration(fw: Node) -> None:
    """Configure FW host interfaces, IP forwarding and iptables rules.

    Assumes interfaces are named fw-eth0 (corp), fw-eth1 (dmz), fw-eth2 (ot)
    and sets gateway IPs for each zone on the FW.
    """
    # Assign IPs to firewall interfaces
    fw.cmd('ip addr flush dev fw-eth0')
    fw.cmd('ip addr flush dev fw-eth1')
    fw.cmd('ip addr flush dev fw-eth2')

    fw.cmd('ip addr add 10.0.1.1/24 dev fw-eth0')
    fw.cmd('ip addr add 10.0.2.1/24 dev fw-eth1')
    fw.cmd('ip addr add 10.0.3.1/24 dev fw-eth2')

    # Enable IP forwarding
    fw.cmd('sysctl -w net.ipv4.ip_forward=1 > /dev/null')

    # Default DROP policy for forwarding (deny by default)
    fw.cmd('iptables -F')
    fw.cmd('iptables -P FORWARD DROP')

    # Allow established related
    fw.cmd("iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT")

    # Permit DMZ -> OT Modbus/TCP (port 502) to PLC
    fw.cmd("iptables -A FORWARD -i fw-eth1 -o fw-eth2 -p tcp --dport 502 -d 10.0.3.10 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -i fw-eth2 -o fw-eth1 -p tcp --sport 502 -s 10.0.3.10 -j ACCEPT")

    # Permit DMZ <-> Corporate (for management) on limited ports (SSH 22, icmp)
    fw.cmd("iptables -A FORWARD -i fw-eth0 -o fw-eth1 -p tcp --dport 22 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -i fw-eth1 -o fw-eth0 -p tcp --sport 22 -j ACCEPT")
    fw.cmd("iptables -A FORWARD -i fw-eth0 -o fw-eth1 -p icmp -j ACCEPT")
    fw.cmd("iptables -A FORWARD -i fw-eth1 -o fw-eth0 -p icmp -j ACCEPT")

    # Explicitly block Corporate -> OT
    fw.cmd("iptables -A FORWARD -i fw-eth0 -o fw-eth2 -j REJECT")
    fw.cmd("iptables -A FORWARD -i fw-eth2 -o fw-eth0 -j REJECT")

    # Allow local host operations on fw
    fw.cmd("iptables -A INPUT -i lo -j ACCEPT")

    print('[*] Firewall configured (fw IPs: 10.0.1.1, 10.0.2.1, 10.0.3.1)')


def configure_host_routes(net: Mininet) -> None:
    """Set default routes on hosts to point to the FW gateway in each zone."""
    h_attacker = net.get('h_attacker')
    h_dmz = net.get('h_dmz')
    h_plc = net.get('h_plc')
    h_icssim = net.get('h_icssim')

    h_attacker.cmd('ip route flush default')
    h_attacker.cmd('ip route add default via 10.0.1.1')

    h_dmz.cmd('ip route flush default')
    h_dmz.cmd('ip route add default via 10.0.2.1')

    h_plc.cmd('ip route flush default')
    h_plc.cmd('ip route add default via 10.0.3.1')

    h_icssim.cmd('ip route flush default')
    h_icssim.cmd('ip route add default via 10.0.3.1')

    print('[*] Host default routes configured to use FW as gateway')


def run_connectivity_tests(net: Mininet) -> Dict[str, bool]:
    """Run minimal connectivity checks and return statuses.

    Tests:
    - Attacker -> PLC (ICMP) should FAIL (segmentation)
    - DMZ -> PLC (TCP port 502) should SUCCEED (allowed Modbus)
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
    # Default fail_mode=secure drops all frames until a controller connects — root cause of
    # the ARP/L2 failure observed in testing.
    for sw in ('s1', 's2', 's3'):
        net.get(sw).cmd(f'ovs-vsctl set-fail-mode {sw} standalone')

    fw = net.get('fw')
    apply_fw_configuration(fw)
    configure_host_routes(net)

    # Optionally auto-start PLC runtime inside the Mininet host 'h_plc'. This
    # starts start_openplc.sh (which launches OpenPLC or fallback emulator) so
    # Modbus/TCP is available at 10.0.3.10:502 from other hosts.
    try:
        auto_plc = os.environ.get('AUTO_START_PLC', '1')
    except Exception:
        auto_plc = '1'
    if auto_plc == '1':
        try:
            h_plc = net.get('h_plc')
            # Resolve repo root and start script path relative to this file
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            plc_dir = os.path.join(repo_root, 'plc')
            start_script = os.path.join(plc_dir, 'start_openplc.sh')
            # Ensure script exists and is executable
            h_plc.cmd(f'chmod +x {start_script} || true')
            # Run start script inside h_plc namespace; use setsid to background inside ns
            cmd = f'cd {plc_dir} && setsid bash {start_script} > /tmp/openplc.log 2>&1 &'
            h_plc.cmd(cmd)
            print('[*] PLC runtime start requested inside h_plc (check /tmp/openplc.log in host namespace)')
        except KeyError:
            # h_plc missing; continue without starting PLC
            print('[WARN] h_plc host not present; skipping auto-start of PLC runtime')
        except Exception as exc:
            print(f'[ERROR] Failed to auto-start PLC runtime inside h_plc: {exc}')

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
    # Use CustomCLI to allow a shortened pingall via MININET_PING_TIMEOUT env var
    CustomCLI(net)
    net.stop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
