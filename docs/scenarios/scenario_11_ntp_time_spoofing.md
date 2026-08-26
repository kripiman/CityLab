# Escenario CTF 11: Ataque de Desincronización de Tiempo NTP / PTP (Time Synchronization Hardening)

**Dificultad**: Media-Avanzada  
**Categoría**: Network Infrastructure / Time Synchronization / NTP/PTP Spoofing  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Las redes industriales modernas dependen de la sincronización horaria mediante **NTP / IEEE 1588 PTP** para el estampado temporal de muestras **IEC 61850 SV** y la correlación SIEM. El atacante falsifica las respuestas NTP introduciendo un desfasaje de reloj (+1 hora). Esto impide que el motor de correlación SIEM vincule los escaneos de red con los eventos de disrupción en los PLCs.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Falsificación de Estampas Temporales (Time Skewing)
1. Ejecutar `attacker/attack_ntp_time_spoofing.py` para inyectar telemetría con marcas de tiempo desfasadas:
   ```bash
   python3 attacker/attack_ntp_time_spoofing.py --offset 3600
   ```
2. Verificar en el SIEM la desvinculación temporal de los eventos correlacionados (`siem_blinded = True`) y la fragmentación en el Historian.

---

## 3. Lección Pedagógica

Resalta que la **sincronización de tiempo es una dependencia de seguridad crítica** a menudo olvidada en el hardening de arquitecturas OT.

---

## 4. Flags CTF

- **FLAG 1 (NTP Clock Drift Attack)**: `FLAG_1{ntp_clock_drift_injected_4418}`
- **FLAG 2 (SIEM Time Correlation Blinded)**: `FLAG_2{siem_time_correlation_blinded_9903}`
