# Escenario CTF 06: Kerberoasting y Escalado de Privilegios en Active Directory

**Dificultad**: Media  
**Categoría**: Active Directory Security / Kerberoasting / Privilege Escalation / RBAC  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El atacante ha comprometido una cuenta de usuario sin privilegios en el dominio `CITYLAB.LOCAL`. Su objetivo es solicitar un ticket de servicio TGS para la cuenta `krbe_ews` (o `jdoe_eng`), extraer el hash, realizar crackeo offline y obtener el token con rol `engineer` para tomar control total del SCADA Server.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Extracción de Ticket TGS Kerberos
1. Solicitar el ticket de servicio Kerberos contra el KDC en `h_dc` (`10.0.1.20:88`):
   ```bash
   python3 attacker/attack_kerberoast_ad.py
   ```
2. Verificar la obtención del token `engineer:ENG_TOKEN_2026`.

### Paso 2: Escalado de Privilegios en API SCADA
1. Usar la credencial obtenida para ejecutar mandos de control crítico (`/api/control/write` o `/api/control`).

---

## 3. Lección Pedagógica

Demuestra la importancia de la **protección de cuentas de servicio en Active Directory**, uso de contraseñas complejas y segmentación de cuentas de servicio respecto de la infraestructura OT.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 06 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/06/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 06 --submit "FLAG_1{...}" --team "tu_equipo"
```
