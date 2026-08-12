# Escenario CTF 20: Comparación de Hardening SCADA API (STRICT_AUTH Toggle)

**Dificultad**: Fácil-Media  
**Categoría**: Industrial Cybersecurity / RBAC Hardening / API Protection  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El estudiante analiza el impacto del control de acceso evaluando el comportamiento de la API SCADA ante un token de autenticación en dos modos distintos: `STRICT_AUTH=0` (modo legado permisivo) vs `STRICT_AUTH=1` (modo Bearer estricto por roles).

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Prueba de Petición con STRICT_AUTH=0 vs STRICT_AUTH=1
1. Probar la resolución del token con el resolver RBAC (`network/rbac.py`):
   - Con `STRICT_AUTH=0`: Permite tokens legados asignando rol de operador por defecto (HTTP 200).
   - Con `STRICT_AUTH=1`: Exige formato `Bearer <role>:<token>` y rechaza tokens planos (HTTP 403 Forbidden).

---

## 3. Lección Pedagógica

Demuestra de forma práctica el concepto de **Hardening defensivo (Blue Team)** y cómo la transición a esquemas estrictos de autorización evita el abuso de credenciales heredadas.

---

## 4. Flags CTF

- **FLAG 1 (STRICT_AUTH Hardened)**: `FLAG_1{strict_auth_enabled_403_enforced_9921}`
