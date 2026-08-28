# Escenario CTF 12: Ransomware IT con Parada de Emergencia Operacional OT (Colonial Pipeline Pattern)

**Dificultad**: Media  
**Categoría**: IT/OT Convergence / Ransomware Impact / Business Continuity / Human Decision Making  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Basado en el incidente de **Colonial Pipeline** (2021), un ransomware infecta los sistemas de facturación y Active Directory de la zona corporativa. Aunque los PLCs de la zona OT no son infectados por malware, la falta de visibilidad del estado de negocio y control contable lleva a la gerencia a tomar la **decisión precautoria de detener la operación física** del suministro.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Simulación de Cifrado IT y Decisión de Shutdown Operacional
1. Ejecutar `attacker/attack_ransomware_ot_impact.py`:
   ```bash
   python3 attacker/attack_ransomware_ot_impact.py
   ```
2. Observar el apagado ordenado del sistema de bombeo sin que haya habido infección física en la celda OT (`ot_precautionary_shutdown = True`).

---

## 3. Lección Pedagógica

Demuestra que los ataques a la infraestructura IT pueden provocar **disrupción ciberfísica masiva sin necesidad de tocar un solo PLC**, debido a la interdependencia operacional y decisiones humanas bajo presión.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 12 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/12/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 12 --submit "FLAG_1{...}" --team "tu_equipo"
```
