# Escenario CTF 13: Reconocimiento Pasivo en Redes OT (Onboarding Pasivo)

**Dificultad**: Fácil (Onboarding)  
**Categoría**: Industrial Cybersecurity / Passive Reconnaissance / Network Sniffing  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El estudiante asume el rol de un analista de ciberseguridad industrial desplegado en la red de control. Su objetivo es capturar el tráfico que fluye por los switches de celda OT (`s1`, `s2`, `s3`) utilizando herramientas de análisis de tráfico pasivo como `tcpdump` o Wireshark, identificando dispositivos e inferiendo los protocolos industriales en uso sin transmitir ningún paquete en la red.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Captura de Tráfico Pasivo
1. Ejecutar el script de captura pasiva `attacker/attack_ot_passive_recon.py`:
   ```bash
   python3 attacker/attack_ot_passive_recon.py
   ```
2. Inspeccionar la lista de dispositivos capturados y sus puertos (`502` Modbus, `4840` OPC UA, `10102` GOOSE).

---

## 3. Lección Pedagógica

Enseña que los **protocolos OT legados transmiten información en claro**, permitiendo mapear la infraestructura crítica completa mediante simple escucha pasiva.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 13 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/13/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 13 --submit "FLAG_1{...}" --team "tu_equipo"
```
