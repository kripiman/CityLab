# Escenario CTF 18: Escritura Forzada de Coil Modbus Único (Manipulación Guiada)

**Dificultad**: Fácil-Media  
**Categoría**: Industrial Cybersecurity / Modbus Control Injection / Process Actuation  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Reutilizando la herramienta `attacker/exploit_modbus.py` desarrollada en la Fase 1, el estudiante debe enviar una instrucción forzada de encendido (`Coil 0 = True`) a la bomba del PLC de Agua (`10.0.3.10:502`) y observar cómo responde el actuador físico en la telemetría HMI.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Forzado de Escritura Modbus
1. Ejecutar la acción `start` mediante la utilidad de explotación:
   ```bash
   python3 attacker/exploit_modbus.py --host 10.0.3.10 start
   ```
2. Verificar en la consola y HMI que la bobina `pump_running` pasa a estado activo (`True`).

---

## 3. Lección Pedagógica

Muestra la ausencia de controles de integridad y autorización en Modbus/TCP legado, donde cualquier host con conectividad IP a la puerto 502 puede alterar el estado operacional de los actuadores de la planta.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 18 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/18/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 18 --submit "FLAG_1{...}" --team "tu_equipo"
```
