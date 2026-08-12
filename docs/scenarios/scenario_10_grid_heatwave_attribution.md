# Escenario CTF 10: Falla Natural por Ola de Calor + Ataque Ciberfísico Simultáneo (Incident Attribution)

**Dificultad**: Avanzada  
**Categoría**: Digital Forensics & Incident Response (DFIR) / Incident Attribution / Hybrid Threats  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Durante un día de temperatura extrema (ola de calor), la demanda eléctrica de la ciudad alcanza un pico de $550\text{ kW}$. El grupo de amenaza coordina una inyección ciberfísica sobre el disyuntor principal de la subestación. El desafío defensivo consiste en analizar los registros del SIEM y la telemetría física para discernir si el apagón fue causado por sobrecarga térmica o por un sabotaje informático coordinado.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Ejecución del Ataque Híbrido
1. Ejecutar `attacker/attack_grid_heatwave_attribution.py`:
   ```bash
   python3 attacker/attack_grid_heatwave_attribution.py
   ```
2. Analizar en el SIEM la presencia de paquetes Modbus anormales durante el pico de carga térmica.

---

## 3. Lección Pedagógica

Enseña la dificultad técnica de la **Atribución de Incidentes (Root Cause Analysis)** cuando los vectores ciberfísicos se enmascaran dentro de eventos de contingencia ambiental natural.

---

## 4. Flags CTF

- **FLAG 1 (Heatwave Peak Load Analysis)**: `FLAG_1{heatwave_peak_demand_analyzed_8812}`
- **FLAG 2 (Incident Attribution Cyber Proof)**: `FLAG_2{cyber_disruption_attribution_proven_4419}`
