# Escenario CTF 15: Lectura de Telemetría Modbus sin Escritura

**Dificultad**: Fácil (Onboarding)  
**Categoría**: Industrial Cybersecurity / Modbus Read-Only / Process Visibility  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El estudiante debe consultar el estado operacional del PLC de Agua (`10.0.3.10:502`) leyendo las bobinas e inputs sin modificar ningún parámetro de control, aprendiendo el mapa de memoria Modbus y su correspondencia física.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Lectura de Memoria Modbus
1. Ejecutar `attacker/attack_modbus_read_only.py`:
   ```bash
   python3 attacker/attack_modbus_read_only.py
   ```
2. Verificar la correspondencia entre los bits leídos y el nivel del tanque físico.

---

## 3. Lección Pedagógica

Muestra cómo la **ausencia de autenticación en la función de lectura Modbus** permite a un atacante espiar el proceso industrial antes de lanzar un sabotaje.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 15 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/15/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 15 --submit "FLAG_1{...}" --team "tu_equipo"
```
