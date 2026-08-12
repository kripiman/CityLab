# Escenario CTF 21: Respuesta a Pérdida de Visibilidad (Loss of View & Manual Isolation)

**Dificultad**: Fácil-Media  
**Categoría**: Industrial Cybersecurity / Incident Response / Loss of View / Manual Switch Isolation  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Durante la operación normal, una interrupción maliciosa corta el enlace de comunicación entre el servidor SCADA y los PLCs. El estudiante observa la alerta de congelamiento/pérdida de visibilidad (*Loss of View*) en el watchdog y ejecuta la respuesta de contingencia aislando manualmente el puerto del switch OT (F-06).

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Detección y Respuesta IR
1. Observar la falla de temporizador Watchdog en la consola HMI.
2. Ejecutar la acción de aislamiento manual de emergencia para contener la anomalía.

---

## 3. Lección Pedagógica

Resalta los procedimientos de **Respuesta a Incidentes (IR) operacionales**, enfatizando que ante la pérdida de visibilidad, la prioridad del operador es mantener la seguridad física del proceso.

---

## 4. Flags CTF

- **FLAG 1 (Loss of View Contained)**: `FLAG_1{loss_of_view_manual_isolation_success_3301}`
