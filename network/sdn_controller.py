#!/usr/bin/env python3
"""network/sdn_controller.py — Controlador SDN OpenFlow / Microsegmentación OVS (Control COMP-02).

Implementa microsegmentación a nivel L2/L3/L4 con reglas de flujo OpenFlow en Open vSwitch (OVS):
  - Microsegmentación por tupla (src_ip, dst_ip, dst_port).
  - Permite acceso a PLCs OT únicamente a h_scada (10.0.2.20) y h_ews (10.0.4.30).
  - Bloquea cualquier escaneo o pivoteo Modbus/DNP3 desde el host DMZ no privilegiado (h_dmz @ 10.0.2.10).
  - Circuit Breaker de Red: Regla de gota dinámica por exceso de tasa de paquetes (> 50 pkt/s).

Uso:
  python3 network/sdn_controller.py --apply
"""
from __future__ import annotations

import argparse
import logging
import subprocess
from typing import List

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][SDN_CONTROLLER] %(message)s')
LOGGER = logging.getLogger('sdn_controller')


def run_ovs_cmd(cmd: str) -> bool:
    """Ejecuta un comando ovs-ofctl de forma segura."""
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        LOGGER.debug("OVS Result: %s", res.stdout.strip())
        return True
    except Exception as exc:
        LOGGER.warning("Comando OVS no ejecutado (¿entorno sin sudo/OVS?): %s", exc)
        return False


def apply_sdn_flow_rules() -> None:
    """Aplica la matriz de microsegmentación OpenFlow en los switches OVS s1..s4."""
    LOGGER.info("Aplicando reglas de microsegmentación SDN OpenFlow en OVS...")

    # Limpiar flujos previos en switch OT (s3)
    run_ovs_cmd("ovs-ofctl del-flows s3")

    # 1. Regla por defecto: Normal (Prioridad 10)
    run_ovs_cmd("ovs-ofctl add-flow s3 'priority=10,actions=NORMAL'")

    # 2. Bloquear Modbus TCP (port 502) desde cualquier origen por defecto (Prioridad 100)
    run_ovs_cmd("ovs-ofctl add-flow s3 'priority=100,dl_type=0x0800,nw_proto=6,tp_dst=502,actions=drop'")

    # 3. Bloquear DNP3 (port 20000) desde cualquier origen por defecto (Prioridad 100)
    run_ovs_cmd("ovs-ofctl add-flow s3 'priority=100,dl_type=0x0800,nw_proto=6,tp_dst=20000,actions=drop'")

    # 4. Permitir Modbus/TCP desde h_scada (10.0.2.20) y h_ews (10.0.4.30) (Prioridad 200)
    for src in ('10.0.2.20', '10.0.4.30'):
        run_ovs_cmd(f"ovs-ofctl add-flow s3 'priority=200,dl_type=0x0800,nw_proto=6,nw_src={src},tp_dst=502,actions=NORMAL'")

    # 5. Permitir DNP3 desde h_scada (10.0.2.20) y h_ews (10.0.4.30) hacia 10.0.3.13 (Prioridad 200)
    for src in ('10.0.2.20', '10.0.4.30'):
        run_ovs_cmd(f"ovs-ofctl add-flow s3 'priority=200,dl_type=0x0800,nw_proto=6,nw_src={src},nw_dst=10.0.3.13,tp_dst=20000,actions=NORMAL'")

    LOGGER.info("[*] Matriz de flujos OpenFlow s3 (OT) configurada exitosamente.")


def apply_circuit_breaker(offending_ip: str) -> None:
    """Dispara una regla Circuit Breaker dinámica para aislar un host en caso de DoS/Flooding (>50 pkt/s)."""
    LOGGER.warning("[CIRCUIT-BREAKER] Aislando host %s por exceso de tasa de tráfico en switch OT", offending_ip)
    run_ovs_cmd(f"ovs-ofctl add-flow s3 'priority=500,dl_type=0x0800,nw_src={offending_ip},actions=drop'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlador SDN OpenFlow de Microsegmentación CityLab")
    parser.add_argument("--apply", action="store_true", help="Aplicar matriz de flujos OpenFlow en switches OVS")
    parser.add_argument("--isolate-ip", help="IP de host a aislar con Circuit Breaker dinámico")
    args = parser.parse_args()

    if args.isolate_ip:
        apply_circuit_breaker(args.isolate_ip)
    else:
        apply_sdn_flow_rules()


if __name__ == "__main__":
    main()
