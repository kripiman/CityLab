# Escenario CTF 21: Respuesta a Pérdida de Visibilidad (Loss of View & Manual Isolation)

**Dificultad**: Fácil-Media  
**Categoría**: Industrial Cybersecurity / Incident Response / Loss of View / Manual Switch Isolation  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Durante la operación normal, una interrupción maliciosa corta el enlace de comunicación entre el servidor SCADA y los PLCs. El estudiante observa la alerta de congelamiento/pérdida de visibilidad (*Loss of View*) en el watchdog y ejecuta la respuesta de contingencia aislando manualmente el puerto del switch OT (F-06).

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Detección de Pérdida de Visibilidad (Loss of View)
1. Cortar la comunicación hacia el PLC o simular fallos de sondeo consecutivos.
2. Observar en `http://10.0.2.20:8080/api/telemetry` que al alcanzar `_consecutive_failures[sector] >= 3` (`LOSS_OF_VIEW_THRESHOLD = 3`), el servidor SCADA etiqueta el sector como `LOSS_OF_VIEW` y genera la alerta operativa sin parada automática (vulnerabilidad pedagógica F-06).

### Paso 2: Respuesta y Aislamiento Manual de Contingencia
1. Como operador/ingeniero de planta, aplicar aislamiento manual o invocar la mitigación dinámica del controlador SDN (`apply_circuit_breaker`) para contener el vector de red.

---

## 3. Lección Pedagógica

Resalta los procedimientos de **Respuesta a Incidentes (IR) operacionales**, enfatizando que ante la pérdida de visibilidad, la prioridad del operador es mantener la seguridad física del proceso.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 21 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/21/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 21 --submit "FLAG_1{...}" --team "tu_equipo"
```
