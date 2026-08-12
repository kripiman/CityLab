# Escenario CTF 23: Defensa SDN Dinámica en Caliente (Safety vs Availability Trade-off)

**Dificultad**: Avanzada-Profesional  
**Categoría**: Industrial Cybersecurity / SDN Defense / OpenFlow Hardening / Plant Availability  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Durante un ataque activo *Low-and-Slow* sobre la celda OT, el equipo defensivo Blue Team debe aplicar reglas dinámicas de mitigación SDN a través de Open vSwitch (OVS) sin interrumpir el tráfico legítimo del SCADA ni afectar la disponibilidad operativa de la planta.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Aplicación de Reglas SDN
1. Ejecutar el script `attacker/attack_live_sdn_defense.py`:
   ```bash
   python3 attacker/attack_live_sdn_defense.py
   ```
2. Verificar el aislamiento de la IP maliciosa manteniéndose el proceso industrial dentro de tolerancia.

---

## 3. Lección Pedagógica

Ilustra el dilema central de ciberseguridad industrial: **proteger la integridad sin degradar la disponibilidad del proceso operativo**.

---

## 4. Flags CTF

- **FLAG 1 (Live SDN Mitigation)**: `FLAG_1{live_sdn_openflow_mitigation_success_8819}`
