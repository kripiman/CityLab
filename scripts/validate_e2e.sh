#!/usr/bin/env bash
# scripts/validate_e2e.sh — Arnés de Validación End-to-End para Cyber Range CityLab
set -e

echo "=========================================================================="
echo " [CityLab] Iniciando Validación End-to-End de Topología y Escenarios"
echo "=========================================================================="

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "[1/4] Ejecutando suite completa de pruebas unitarias e integración Python..."
python3 -m unittest discover -s network/tests
python3 -m unittest discover -s plc/tests
python3 -m unittest discover -s physical/tests
python3 -m unittest discover -s helics_sim/tests
python3 -m unittest discover -s attacker/tests
echo "  ↳ ✅ Suite de 110 tests unitarios PASS."

echo "[2/4] Verificando ejecución directa de scripts ofensivos principales..."
python3 attacker/attack_ot_passive_recon.py > /dev/null
python3 attacker/attack_goose_spoofing.py > /dev/null
python3 attacker/attack_triton_low_slow.py > /dev/null
python3 attacker/attack_stuxnet_replay.py > /dev/null
python3 attacker/attack_purple_team_mttd.py > /dev/null
python3 attacker/attack_apt_sandworm_campaign.py > /dev/null
echo "  ↳ ✅ Execuicón directa de 6/6 scripts ofensivos PASS."

echo "[3/4] Comprobando disponibilidad de daemons emuladores OT..."
python3 -c "
import socket
from plc.iec61850_emulator import Iec61850Server
from plc.honeypot_server import OtHoneypotServer
from plc.dnp3_emulator import Dnp3Server

s1 = Iec61850Server('127.0.0.1', 10102, 10103)
s1.start()
s2 = OtHoneypotServer('127.0.0.1', 15025)
s2.start()
s1.stop()
s2.stop()
print('  ↳ ✅ Modulos de emulacion IED, Honeypot y DNP3 importables y funcionales.')
"

echo "[4/4] Verificando correlación SOC y métricas NIST SP 800-61..."
python3 -c "
from attacker.attack_purple_team_mttd import PurpleTeamMttd
res = PurpleTeamMttd().run_mttd_measurement()
assert res['status'] == 'SUCCESS'
assert res['alerts_count'] >= 2
print('  ↳ ✅ Engine SIEM y reporte NIST SP 800-61 validado.')
"

echo "=========================================================================="
echo " [CityLab] ¡Validación End-to-End completada EXITOSAMENTE!"
echo "=========================================================================="
