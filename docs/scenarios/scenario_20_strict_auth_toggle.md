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

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 20 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/20/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 20 --submit "FLAG_1{...}" --team "tu_equipo"
```
