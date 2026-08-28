# Escenario CTF 23: Defensa SDN Dinámica en Caliente (Safety vs Availability Trade-off)

**Dificultad**: Avanzada-Profesional  
**Categoría**: Industrial Cybersecurity / SDN Defense / OpenFlow Hardening / Plant Availability  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Durante un ataque activo *Low-and-Slow* sobre la celda OT, el equipo defensivo Blue Team debe aplicar reglas dinámicas de mitigación SDN a través de Open vSwitch (OVS) sin interrumpir el tráfico legítimo del SCADA ni afectar la disponibilidad operativa de la planta.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Aplicación de Reglas SDN
1. Ejecutar el script `attacker/attack_live_sdn_defense.py`:
   ```bash
   python3 attacker/attack_live_sdn_defense.py
   ```
2. Verificar el aislamiento de la IP maliciosa manteniéndose el proceso industrial dentro de tolerancia.

---

## 3. Lección Pedagógica

Ilustra el dilema central de ciberseguridad industrial: **proteger la integridad sin degradar la disponibilidad del proceso operativo**.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 23 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/23/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 23 --submit "FLAG_1{...}" --team "tu_equipo"
```
