# Escenario CTF 25: Ejercicio Tabletop de Crisis por Ransomware Industrial

**Dificultad**: Avanzada-Profesional  
**Categoría**: Tabletop Exercises / Executive Incident Response / Crisis Management  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Simulación de crisis guiada por un instructor donde se asignan roles ejecutivos (CISO, Director de Operaciones, Asesor Legal) y se toman decisiones ante la parálisis total de la red corporativa por un ataque de ransomware.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución del Simulador Tabletop
1. Ejecutar `attacker/attack_ransomware_tabletop.py`:
   ```bash
   python3 attacker/attack_ransomware_tabletop.py
   ```
2. Evaluar las decisiones ejecutivas en el reporte.

---

## 3. Lección Pedagógica

Fomenta el entendimiento de la **gestión de crisis directiva**, comunicación con entes reguladores y resiliencia estratégica.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 25 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/25/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 25 --submit "FLAG_1{...}" --team "tu_equipo"
```
