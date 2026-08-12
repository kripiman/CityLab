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

- **FLAG 1 (Disaster Recovery Successful)**: `FLAG_1{disaster_recovery_post_incident_success_9901}`
