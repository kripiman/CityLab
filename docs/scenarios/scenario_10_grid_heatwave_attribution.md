# Escenario CTF 10: Falla Natural por Ola de Calor + Ataque Ciberfísico Simultáneo (Incident Attribution)

**Dificultad**: Avanzada  
**Categoría**: Digital Forensics & Incident Response (DFIR) / Incident Attribution / Hybrid Threats  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Durante un día de temperatura extrema (ola de calor), la demanda eléctrica de la ciudad alcanza un pico de $550\text{ kW}$. El grupo de amenaza coordina una inyección ciberfísica sobre el disyuntor principal de la subestación. El desafío defensivo consiste en analizar los registros del SIEM y la telemetría física para discernir si el apagón fue causado por sobrecarga térmica o por un sabotaje informático coordinado.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Ejecución del Ataque Híbrido
1. Ejecutar `attacker/attack_grid_heatwave_attribution.py`:
   ```bash
   python3 attacker/attack_grid_heatwave_attribution.py
   ```
2. Analizar en el SIEM la presencia de paquetes Modbus anormales durante el pico de carga térmica.

---

## 3. Lección Pedagógica

Enseña la dificultad técnica de la **Atribución de Incidentes (Root Cause Analysis)** cuando los vectores ciberfísicos se enmascaran dentro de eventos de contingencia ambiental natural.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 10 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/10/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 10 --submit "FLAG_1{...}" --team "tu_equipo"
```
