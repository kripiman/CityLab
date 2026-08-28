# Escenario CTF 09: Dosificación Química en Planta de Tratamiento de Agua (SWaT / Oldsmar Pattern)

**Dificultad**: Avanzada  
**Categoría**: Industrial Cybersecurity / Water Treatment / Chemical Dosing Attack  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Basado en incidentes y bancos de pruebas reales de potabilización de agua (SWaT / incidente de Oldsmar), un atacante accede al sistema de control de aditivos químicos e incrementa la tasa de dosificación de hidróxido de sodio/cloro de $1.5\text{ ppm}$ a $8.5\text{ ppm}$. Mantiene el nivel por debajo de los umbrales de emergencia del SIS para causar degradación de calidad del agua potable en la red de distribución urbana.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Alteración de la Tasa de Dosificación
1. Ejecutar el script `attacker/attack_chemical_dosing.py`:
   ```bash
   python3 attacker/attack_chemical_dosing.py --ppm 8.5
   ```
2. Verificar la alteración de parámetros de dosificación sanitaria (`contamination_achieved = True`).

---

## 3. Lección Pedagógica

Demuestra cómo los ataques ciberfísicos no solo buscan la destrucción de activos (equipos rotos/tanques secos) sino la **contaminación del producto final**, exigiendo analizadores de calidad de agua independientes fuera del bus SCADA.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 09 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/09/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 09 --submit "FLAG_1{...}" --team "tu_equipo"
```
