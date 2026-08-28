# Escenario CTF 24: Evasión de Reglas de Correlación SIEM (Multi-IP Distributed Attack)

**Dificultad**: Avanzada-Profesional  
**Categoría**: Industrial Cybersecurity / SIEM Evasion / Distributed Attacks  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El estudiante analiza el código de correlación en `network/siem_pipeline.py` y diseña un patrón de ataque distribuido desde múltiples direcciones IP para evitar que el motor SIEM active alertas críticas por umbral de repetición.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución de Evasión Distribuida
1. Ejecutar `attacker/attack_siem_rule_evasion.py`:
   ```bash
   python3 attacker/attack_siem_rule_evasion.py
   ```
2. Verificar que las peticiones individuales no alcanzan el umbral de disparo.

---

## 3. Lección Pedagógica

Enseña las **limitaciones de las reglas de detección basadas en firmas estáticas** y la necesidad de analítica de comportamiento basada en anomalías.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 24 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/24/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 24 --submit "FLAG_1{...}" --team "tu_equipo"
```
