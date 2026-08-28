# Escenario CTF 22: Ejercicio Purple Team y Medición de Métricas SOC (MTTD / MTTR)

**Dificultad**: Avanzada-Profesional  
**Categoría**: Purple Teaming / SOC Metrics / NIST SP 800-61 / MTTD & MTTR  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El equipo defensivo (Blue Team) y ofensivo (Red Team) colaboran para medir la ventana de tiempo de detección (**MTTD**) y respuesta (**MTTR**) ante un ataque por inyección de trafico GOOSE en la subestación, generando un informe de incidente alineado con **NIST SP 800-61**.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución del Test Purple Team
1. Ejecutar `attacker/attack_purple_team_mttd.py`:
   ```bash
   python3 attacker/attack_purple_team_mttd.py
   ```
2. Verificar el tiempo exacto transcurrido entre la inyección y el disparo de la alerta SIEM.

---

## 3. Lección Pedagógica

Enseña la importancia de las **métricas cuantitativas de respuesta (KPIs del SOC)** para justificar la eficacia de las inversiones en visibilidad OT.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 22 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/22/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 22 --submit "FLAG_1{...}" --team "tu_equipo"
```
