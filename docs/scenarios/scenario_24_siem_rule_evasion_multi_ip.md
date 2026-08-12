# Escenario CTF 24: Evasión de Reglas de Correlación SIEM (Multi-IP Distributed Attack)

**Dificultad**: Avanzada-Profesional  
**Categoría**: Industrial Cybersecurity / SIEM Evasion / Distributed Attacks  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El estudiante analiza el código de correlación en `network/siem_pipeline.py` y diseña un patrón de ataque distribuido desde múltiples direcciones IP para evitar que el motor SIEM active alertas críticas por umbral de repetición.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución de Evasión Distribuida
1. Ejecutar `attacker/attack_siem_rule_evasion.py`:
   ```bash
   python3 attacker/attack_siem_rule_evasion.py
   ```
2. Verificar que las peticiones individuales no alcanzan el umbral de disparo.

---

## 3. Lección Pedagógica

Enseña las **limitaciones de las reglas de detección basadas en firmas estáticas** y la necesidad de analítica de comportamiento basada en anomalías.

---

## 4. Flags CTF

- **FLAG 1 (SIEM Evasion Successful)**: `FLAG_1{siem_correlation_rules_evaded_multi_ip_9901}`
