# Escenario CTF 08: Insider Threat y Violación de Principio de Mínimo Privilegio RBAC

**Dificultad**: Fácil-Media  
**Categoría**: Identity & Access Management (IAM) / RBAC Enforcement / Insider Threat  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Un empleado descontento o un atacante que ha comprometido una credencial de auditoría (`auditor`) intenta enviar comandos de modificación de proceso (`/api/control/write`) al SCADA Server. El ejercicio evalúa la efectividad del control de acceso basado en roles (**RBAC**) bajo el estándar **IEC 62443**.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Intento de Escritura con Token de Auditor
1. Ejecutar `attacker/attack_insider_rbac.py`:
   ```bash
   python3 attacker/attack_insider_rbac.py
   ```
2. Verificar la denegación de acceso (`access_granted = False`, `blocked_by_rbac = True`).

---

## 3. Lección Pedagógica

Demuestra cómo el principio de **Mínimo Privilegio (Least Privilege)** limita el radio de impacto (*blast radius*) de credenciales comprometidas en redes OT.

---

## 4. Flags CTF

- **FLAG 1 (Auditor Credentials Compromised)**: `FLAG_1{auditor_bearer_token_compromised_7719}`
- **FLAG 2 (RBAC Access Denied 403)**: `FLAG_2{rbac_access_denied_403_success_1102}`
