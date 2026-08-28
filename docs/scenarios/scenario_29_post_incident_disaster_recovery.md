# Escenario CTF 29: Recuperación Post-Incidente y Reintegración Operacional (Disaster Recovery)

**Dificultad**: Profesional (Capstone)  
**Categoría**: Post-Incident Recovery / Disaster Recovery / Integrity Verification  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Tras la contención de una intrusión masiva, el equipo de respuesta debe ejecutar la recuperación post-incidente: validar la integridad del firmware de los PLCs, reconstruir la base de datos Historian desde los logs del SIEM out-of-band y reiniciar de forma segura la planta.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución del Procedimiento de Recuperación
1. Ejecutar `attacker/attack_post_incident_recovery.py`:
   ```bash
   python3 attacker/attack_post_incident_recovery.py
   ```
2. Confirmar la restauración del estado operativo seguro.

---

## 3. Lección Pedagógica

Cubre la etapa crítica que la mayoría de los laboratorios ignoran: **la restauración de la confianza digital y la resiliencia operacional post-incidente**.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 29 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/29/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 29 --submit "FLAG_1{...}" --team "tu_equipo"
```
