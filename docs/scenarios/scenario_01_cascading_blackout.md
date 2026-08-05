# Escenario CTF 01: Apagón Urbano en Cascada (THM / HTB Style)

**Dificultad**: Media  
**Categoría**: Industrial Cybersecurity / OT Hacking / CPS Cascading Failures  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Una célula adversaria ha ganado acceso inicial a la red corporativa de la municipalidad (`10.0.1.10`). El objetivo táctico es comprometer la red de infraestructura crítica de la ciudad, provocando un colapso en cascada que afecte la generación eléctrica, el suministro de agua potable y la red de semáforos urbanos.

---

## 2. Mapa de Red e IPs Relevantes

- **Atacante (Corporate Zone)**: `10.0.1.10` (`h_attacker`)
- **Salto DMZ (DMZ Zone)**: `10.0.2.10` (`h_dmz`)
- **Servidor SCADA Central (DMZ)**: `10.0.2.20:8080` (`h_scada`)
- **PLC Agua OT**: `10.0.3.10:502` (`h_plc`)
- **PLC Gas OT**: `10.0.3.12:502` (`h_plc_gas`)
- **PLC Eléctrico OT**: `10.0.3.13:502` (`h_plc_elec`)
- **PLC Transporte OT**: `10.0.3.14:502` (`h_plc_trans`)

---

## 3. Cadena de Ataque (Walkthrough Paso a Paso)

### Paso 1: Pivoteo de Corporate a DMZ
1. Desde la máquina de ataque, verificar conectividad con la DMZ (`10.0.2.10`):
   ```bash
   ping -c 2 10.0.2.10
   ssh user@10.0.2.10
   ```
2. Inspeccionar la API REST del Servidor SCADA Central:
   ```bash
   curl http://10.0.2.20:8080/api/telemetry
   ```
   *Obtener estado de bobinas Modbus de todos los sectores.*

### Paso 2: Reconocimiento Modbus en la Zona OT (`10.0.3.0/24`)
1. Probar acceso al puerto `TCP/502` de los PLCs desde la DMZ:
   ```bash
   nc -zv 10.0.3.13 502
   ```
2. Leer el estado de la bobina de generación eléctrica (`Coil 2`):
   ```bash
   python3 attacker/attack_multisector.py --sector elec --mode start
   ```

### Paso 3: Inyección de Disparo Eléctrico (Sabotaje Cinético)
1. Forzar la detención de la generación eléctrica (`Coil 1 = 1` en `10.0.3.13`):
   ```bash
   python3 attacker/attack_multisector.py --sector elec --mode stop
   ```

### Paso 4: Validación del Efecto Dominó en Cascada
1. Monitorear el registro centralizado de eventos (`cascading_events.csv`):
   - **T+0s**: `grid_freq_hz` cae de $60.0\text{ Hz}$ a $<58.0\text{ Hz}$.
   - **T+2s**: `hospital_on_ups = 1` (Failover del Hospital a baterías/generador diésel).
   - **T+5s**: `grid_voltage_pu` cae a $0.0\text{ pu} \implies \text{power\_available} = \text{False}$.
   - **T+7s**: Bomba P1 de Agua se apaga por falta de energía.
   - **T+12s**: Semáforos urbanos entran en `FLASHING_YELLOW_EMERGENCY` $\implies \text{transport\_congestion} \to 1.0$.
   - **T+20s**: Tanque T2 de Agua se vacía por consumo urbano $\implies \text{water\_trip} = 1$.
   - **Alerta final**: `CASCADING_BLACKOUT+HOSPITAL_UPS`.

---

## 4. Flags del Desafío CTF

- **FLAG 1 (DMZ Pivoting)**: `FLAG_1{dmz_pivoting_modbus_recon_8492}`
- **FLAG 2 (Swing Equation Subfrequency)**: `FLAG_2{elec_swing_underfrequency_trip_9910}`
- **FLAG 3 (Cascading City Blackout)**: `FLAG_3{cascading_city_blackout_achieved_0023}`
