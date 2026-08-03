CityLab Phase1 — Operaciones rápidas

Propósito: instrucciones concisas para instalar dependencias y ejecutar PoC en una máquina Linux (Nobara/Fedora, Arch, Ubuntu/Mint).

1) Instalar dependencias (recomendado):
   sudo ./install_deps.sh

2) Verificar OVS activo:
   sudo ovs-vsctl show

3) Ejecutar topología Mininet (como root):
   sudo python3 network/topology.py --test
   (Interactivo: sudo python3 network/topology.py)

4) En la CLI de Mininet, arrancar el PLC runtime en h_plc:
   mininet> h_plc bash -c "cd /home/kripi/Documentos/GitHub/CityLab/plc && chmod +x start_openplc.sh modbus_emulator.py && bash start_openplc.sh"

   - Si OpenPLC no está instalado, el script lanzará el emulador Python en el host plc (escucha 0.0.0.0:502).

5) Ejecutar cliente de integración desde DMZ (h_dmz):
   mininet> h_dmz bash -c "cd /home/kripi/Documentos/GitHub/CityLab && python3 -m pip install --user pymodbus==2.5.3 && python3 plc/tests/poc_modbus_test.py --host 10.0.3.10"

6) Comprobaciones manuales rápidas:
   - Desde h_attacker: ping 10.0.3.10  # debe FALLAR
   - Desde h_dmz: timeout 1 bash -c '</dev/tcp/10.0.3.10/502' && echo open || echo closed

Notas:
 - Ejecutar los comandos dentro de Mininet asegura que las rutas y namespaces sean correctos.
 - Si Python packages no son visibles bajo sudo, instalar system-wide con: sudo python3 -m pip install pymodbus==2.5.3
 - Logs: ../logs/openplc_runtime.log

Siguientes pasos recomendados:
 - Implementar ICSSIM federado y federar con HELICS
 - Crear scripts para arrancar broker HELICS y GridLAB-D y orquestar con run_phase1.sh
