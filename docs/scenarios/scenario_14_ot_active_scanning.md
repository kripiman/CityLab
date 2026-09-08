# Escenario CTF 14: Escaneo Activo de Subredes OT (Segmentación Nmap)

**Dificultad**: Fácil (Onboarding)  
**Categoría**: Industrial Cybersecurity / Active Scanning / Network Segmentation  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El estudiante debe ejecutar un escaneo activo de red desde la posición del atacante `h_attacker` (`10.0.1.10`) utilizando `nmap` para descubrir qué servicios e IPs responden en la celda OT (`10.0.3.0/24`) y verificar si la segmentación de red permite o bloquea el escaneo directo.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución de Escaneo Activo
1. Ejecutar `attacker/attack_ot_active_scan.py`:
   ```bash
   python3 attacker/attack_ot_active_scan.py
   ```
2. Analizar la lista de hosts y puertos expuestos.

---

## 3. Lección Pedagógica

Permite entender la **efectividad de las políticas de cortafuegos en la DMZ** y cómo la exposición de puertos de control en subredes no autorizadas incrementa la superficie de ataque.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 14 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/14/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 14 --submit "FLAG_1{...}" --team "tu_equipo"
```
