# Escenario CTF 16: Interacción con Trampas Deception (Honeypot OT)

**Dificultad**: Fácil (Onboarding)  
**Categoría**: Industrial Cybersecurity / Deception Technology / Honeypots  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El estudiante intenta escanear o conectar a una dirección no documentada en la celda OT (`10.0.5.99`). Este servicio actúa como una trampa Honeypot (*Deception Technology*), disparando inmediatamente una alerta de alta severidad hacia el SIEM central.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Conexión al Honeypot
1. Ejecutar `attacker/attack_honeypot_touch.py`:
   ```bash
   python3 attacker/attack_honeypot_touch.py
   ```
2. Verificar el ID de evento generado y su aparición en el log del SIEM.

---

## 3. Lección Pedagógica

Introduce la primera experiencia defensiva de **"me vieron"**, enseñando cómo la tecnología de engaño (*Deception Technology*) detecta exploraciones de adversarios antes de que alcancen los PLCs de producción.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 16 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/16/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 16 --submit "FLAG_1{...}" --team "tu_equipo"
```
