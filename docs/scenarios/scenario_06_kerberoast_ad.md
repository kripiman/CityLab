# Escenario CTF 06: Kerberoasting y Escalado de Privilegios en Active Directory

**Dificultad**: Media  
**Categoría**: Active Directory Security / Kerberoasting / Privilege Escalation / RBAC  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El atacante ha comprometido una cuenta de usuario sin privilegios en el dominio `CITYLAB.LOCAL`. Su objetivo es solicitar un ticket de servicio TGS para la cuenta `scada_engineer_svc`, extraer el hash, realizar crackeo offline y obtener el token con rol `engineer` para tomar control total del SCADA Server.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Extracción de Ticket TGS Kerberos
1. Solicitar el ticket de servicio Kerberos contra el KDC en `h_dc` (`10.0.1.20:10088`):
   ```bash
   python3 attacker/attack_kerberoast_ad.py
   ```
2. Verificar la obtención del token `engineer:ENG_TOKEN_2026`.

### Paso 2: Escalado de Privilegios en API SCADA
1. Usar la credencial obtenida para ejecutar mandos de control crítico (`/api/control/write`).

---

## 3. Lección Pedagógica

Demuestra la importancia de la **protección de cuentas de servicio en Active Directory**, uso de contraseñas complejas y segmentación de cuentas de servicio respecto de la infraestructura OT.

---

## 4. Flags CTF

- **FLAG 1 (Kerberoast TGS Extraction)**: `FLAG_1{kerberoast_tgs_ticket_extracted_5521}`
- **FLAG 2 (AD Privilege Escalation to Engineer)**: `FLAG_2{ad_privilege_escalation_engineer_8830}`
