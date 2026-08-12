# Escenario CTF 07: Anti-Forense y Borrado de Registros en Historian TSDB

**Dificultad**: Media  
**Categoría**: Digital Forensics & Incident Response (DFIR) / Anti-Forensics / Log Wiping  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Tras completar el sabotaje industrial en la planta de tratamiento de agua, la célula atacante busca dificultar la investigación forense. Acceden a la base de datos del Historian local (`/tmp/citylab_historian.db`) y ejecutan un borrado completo de los registros de series temporales antes de desconectarse.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Ejecución del Borrado Anti-Forense
1. Ejecutar el script `attacker/attack_historian_anti_forensics.py`:
   ```bash
   python3 attacker/attack_historian_anti_forensics.py
   ```
2. Confirmar la eliminación de todos los registros de telemetría del Historian local (`historian_cleared = True`).

---

## 3. Lección Pedagógica y Respuesta Defensiva

Demuestra que los **logs locales son vulnerables al borrado por el atacante** y resalta la necesidad imperiosa de contar con una arquitectura **SIEM centralizada e inmutable fuera de banda** (`network/siem_pipeline.py`).

---

## 4. Flags CTF

- **FLAG 1 (Historian Database Compromise)**: `FLAG_1{historian_tsdb_compromised_3310}`
- **FLAG 2 (Anti-Forensics Log Wiping)**: `FLAG_2{anti_forensics_log_wiping_success_9912}`
