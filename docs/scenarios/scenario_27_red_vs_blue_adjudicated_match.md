# Escenario CTF 27: Ciberejercicio Simultáneo Red vs Blue con Motor de Arbitraje

**Dificultad**: Profesional (Capstone)  
**Categoría**: Red vs Blue Match / Live Scoring Engine / Cyber Competition  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Competencia simultánea en tiempo real entre Red Team (buscando lograr disrupción física) y Blue Team (buscando aislar y mitigar amenazas), con un motor de arbitraje automático que otorga puntos según la velocidad y efectividad de respuesta.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución del Ciberejercicio
1. Ejecutar `attacker/attack_red_vs_blue_match.py`:
   ```bash
   python3 attacker/attack_red_vs_blue_match.py
   ```
2. Inspeccionar la puntuación final otorgada a cada equipo.

---

## 3. Lección Pedagógica

Fomenta el **trabajo en equipo operacional en entornos hiperrealistas**, donde la agilidad defensiva se mide directamente contra ataques en vivo.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 27 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/27/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 27 --submit "FLAG_1{...}" --team "tu_equipo"
```
