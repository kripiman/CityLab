# Escenario CTF 26: Capstone Campaña APT Persistente (Sandworm / ELECTRUM Pattern)

**Dificultad**: Profesional (Capstone)  
**Categoría**: Advanced Persistent Threats / Full Campaign Orchestration / Sandworm  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Ejercicio capstone de 4 a 6 horas donde el estudiante debe orquestar e integrar toda la cadena de ataque (Reconocimiento pasivo, Pivoteo DMZ, Explotación Kerberos, Inyección GOOSE/Modbus, Evasión de SIS y borrado Anti-forense), recreando las operaciones del grupo de amenaza Sandworm / ELECTRUM.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución de la Campaña APT
1. Ejecutar el orquestador de campaña `attacker/attack_apt_sandworm_campaign.py`:
   ```bash
   python3 attacker/attack_apt_sandworm_campaign.py
   ```
2. Verificar el cumplimiento de las 5 fases del ataque ciberfísico.

---

## 3. Lección Pedagógica

Evalúa la **capacidad del analista/estudiante para integrar técnicas múltiples en una sola campaña cohesiva** con impacto industrial tangible.

---

## 4. Flags CTF

- **FLAG 1 (APT Sandworm Campaign Complete)**: `FLAG_1{apt_sandworm_electrum_full_campaign_success_0029}`
