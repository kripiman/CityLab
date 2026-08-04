# CityLab Phase1 — Operaciones rápidas

Instalar dependencias, ejecutar PoC en Linux (Nobara/Fedora, Arch, Ubuntu/Mint).

1) Instalar dependencias:
   sudo ./install_deps.sh

2) Verificar OVS:
   sudo ovs-vsctl show

3) Ejecutar Mininet (root):
   sudo python3 network/topology.py --test
   (Interactivo: sudo python3 network/topology.py)

4) Iniciar PLC en h_plc (CLI Mininet):
   mininet> h_plc bash -c "cd /home/kripi/Documentos/GitHub/CityLab/plc && chmod +x start_openplc.sh modbus_emulator.py && bash start_openplc.sh"

   - Sin OpenPLC, script inicia emulador Python en plc (0.0.0.0:502).

5) Ejecutar cliente integración en h_dmz (CLI Mininet):
   mininet> h_dmz bash -c "cd /home/kripi/Documentos/GitHub/CityLab && python3 -m pip install --user pymodbus==2.5.3 && python3 plc/tests/poc_modbus_test.py --host 10.0.3.10"

6) Comprobación manual:
   - h_attacker: ping 10.0.3.10  # FALLAR
   - h_dmz: timeout 1 bash -c '</dev/tcp/10.0.3.10/502' && echo open || echo closed

Notas:
 - Ejecutar dentro de Mininet asegura rutas y namespaces correctos.
 - Paquetes Python no visibles con sudo: instalar global `sudo python3 -m pip install pymodbus==2.5.3`.
 - Logs: ../logs/openplc_runtime.log

Siguientes pasos:
 - Integrar ICSSIM federado con HELICS.
 - Crear scripts iniciar broker HELICS + GridLAB-D, orquestar con run_phase1.sh.
