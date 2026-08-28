# Escenario CTF 03: Evasión Sigilosa de SIS Triton/Trisis (Low-and-Slow Attack)

**Dificultad**: Avanzada  
**Categoría**: Industrial Cybersecurity / Safety Instrumented Systems (SIS) / Stealth Process Manipulation  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Basado en la amenaza ciberfísica **Triton/Trisis** (2017), los atacantes han obtenido capacidad de manipulación directa sobre los actuadores del proceso industrial. En lugar de provocar un choque brusco que active los interlocks de seguridad del **Safety Instrumented System (SIS)**, ejecutan un ataque *Low-and-Slow* ajustando los parámetros exactamente un 1% por debajo de los umbrales de disparo.

---

## 2. Mapa de Umbrales de Seguridad (SIS vs Atacante)

- **Tanque SWaT T1**:
  - Umbral SIS Trip: $\ge 19.0\text{ m}^3$
  - Manipulación Atacante: $18.8\text{ m}^3$ (Saturación continua sin activar trip)
- **Red de Gasoducto**:
  - Umbral SIS Trip: $\ge 180.0\text{ PSI}$
  - Manipulación Atacante: $178.5\text{ PSI}$ (Sobre-presión crónica sin activa trip)

---

## 3. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Reconocimiento de Umbrales SIS
1. Analizar el código de interlocks del federado SIS (`helics_sim/fed_sis.py`):
   - Identificar los límites configurados en `SafetyInterlockLimits`.

### Paso 2: Ejecución de Manipulación Sigilosa
1. Ejecutar el script `attacker/attack_triton_low_slow.py`:
   ```bash
   python3 attacker/attack_triton_low_slow.py --sector water --cycles 10
   ```
2. Verificar que el nivel de proceso se mantiene saturado en $18.8\text{ m}^3$ sin disparar el SIS (`sis_tripped = False`).

---

## 4. Lección Pedagógica y Defensiva

Demuestra que la capa de seguridad física independiente (SIS) es una **última línea de defensa** para prevenir explosiones/catástrofes físicas, pero **NO reemplaza al monitoreo de anomalias de proceso (SIEM / TSDB Analytics)** para detectar manipulación sutil.

---

## 5. Flags del Desafío CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 03 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/03/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 03 --submit "FLAG_1{...}" --team "tu_equipo"
```
