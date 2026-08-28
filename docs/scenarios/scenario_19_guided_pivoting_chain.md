# Escenario CTF 19: Cadena de Pivoteo Guiado Attacker -> DMZ -> OT

**Dificultad**: Fácil-Media  
**Categoría**: Industrial Cybersecurity / Pivoting Chain / Defense in Depth  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Demuestra el salto secuencial entre zonas de red IEC 62443: desde la zona corporativa `h_attacker` (`10.0.1.10`), pivoteando a través de la DMZ (`10.0.2.10`) para alcanzar la celda de control OT (`10.0.3.10`).

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Salto Secuencial de Pivoteo
1. Probar conectividad desde la zona corporativa `h_attacker` (`10.0.1.10`) hacia el bastión DMZ (`10.0.2.10`) y el host SCADA (`10.0.2.20`).
2. Desde la DMZ, ejecutar el script de ataque multisectorial apuntando al sector de agua (conectando por defecto a `10.0.3.10:502` o vía proxy):
   ```bash
   python3 attacker/attack_multisector.py --sector water --mode start
   ```
3. Documentar la brecha de aislamiento detectada (F-03).

---

## 3. Lección Pedagógica

Explica la necesidad de implementar cortafuegos con inspección profunda de estado (SPI) y proxying de aplicaciones para evitar que las credenciales comprometidas en TI permitan el pivoteo directo a OT.

---

## 4. Flags CTF

Las flags de este escenario son generadas y verificadas dinámicamente por el servidor en función de la semilla de sesión `CITYLAB_SESSION_SEED` y el cumplimiento de las condiciones físicas y operativas reales.

### 🏁 Obtención y Verificación de Flags:
```bash
# Evaluar cumplimiento de objetivos y obtener flags server-side:
python3 scripts/run_scenario.py --id 19 --check

# O mediante consulta REST al Flag Service:
curl -s http://10.0.2.20:8570/api/flag/mint/19/FLAG_1

# Enviar flag obtenida para registro en el Scoreboard:
python3 scripts/run_scenario.py --id 19 --submit "FLAG_1{...}" --team "tu_equipo"
```
