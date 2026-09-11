# Escenario CTF 28: Entorno Ciego Dinámico Anti-Memorización

**Dificultad**: Profesional (Capstone)  
**Categoría**: Anti-Memorization / Dynamic Parameters / Blind Assessment  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Escenario dinámico en el que el laboratorio asigna aleatoriamente direcciones IP, puertos de servicio y umbrales de seguridad SIS. El estudiante no puede seguir una guía o receta previa y debe descubrir las vulnerabilidades aplicando metodologías de análisis desde cero.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución del Generador de Entorno Ciego
1. Ejecutar `attacker/attack_blind_randomized_env.py`:
   ```bash
   python3 attacker/attack_blind_randomized_env.py
   ```
   El script persiste los parámetros generados en `/tmp/citylab_blind_env.json` y `/tmp/citylab_blind_env.sh`.
2. Antes de levantar el laboratorio, cargar los parámetros aleatorizados en el entorno:
   ```bash
   source /tmp/citylab_blind_env.sh   # exporta DNP3_PORT y SIS_MAX_TANK_LEVEL
   sudo -E ./citylab.sh up            # -E preserva las variables exportadas bajo sudo
   ```
3. Analizar las variables aleatorias y adaptar la estrategia de intrusión.

---

## 3. Lección Pedagógica

Garantiza que la evaluación evalúe **habilidades metodológicas reales (TTPs)** y no la memorización estática de parámetros de laboratorio.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 28 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/28/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 28 --submit "FLAG_1{...}" --team "tu_equipo"
```
