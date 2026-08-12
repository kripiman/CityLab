# Escenario CTF 04: Replay de Telemetría Man-in-the-Middle (Estilo Stuxnet)

**Dificultad**: Avanzada  
**Categoría**: Industrial Cybersecurity / Man-in-the-Middle / Telemetry Replay / Stuxnet Pattern  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Basado en la técnica usada por **Stuxnet** (2010), el atacante intercepta la comunicación entre los sensores de la planta y el Servidor SCADA/Historian. El ataque graba $N$ segundos de operación completamente normal y luego entra en fase de *Replay*: transmite en bucle la grabación previa hacia la pantalla del operador HMI y la base de datos Historian, mientras en paralelo se sabotea destructivamente el proceso físico.

---

## 2. Diagrama de Flujo del Ataque

```
[Proceso Físico Real] ──(Nivel Crítico 0.1m³)──> [Atacante MITM]
                                                       │
                                          (Inyección Baseline Falso 10.0m³)
                                                       ▼
                                            [HMI Operator / TSDB]
```

---

## 3. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Grabación de Telemetría de Baseline
1. Ejecutar fase 1 de captura de datos limpios:
   ```bash
   python3 attacker/attack_stuxnet_replay.py --duration 5
   ```

### Paso 2: Engaño a la HMI y Sabotaje de Planta
1. Observar en los logs del servidor Historian cómo las lecturas persisten en rango normal ($10.0\text{ m}^3$) a pesar de que el tanque real se encuentra desabastecido o en condición de falla.

---

## 4. Lección Pedagógica y Defensiva

Enseña el peligro de la **falsa sensación de seguridad en pantalla (Blindness to Operations)** y la necesidad de defensas de validación cruzada física (monitoreo independiente fuera de banda / redundancia de sensores no conectados al mismo bus).

---

## 5. Flags del Desafío CTF

- **FLAG 1 (Telemetry Interception)**: `FLAG_1{stuxnet_normal_baseline_recorded_1029}`
- **FLAG 2 (HMI Replay Deception)**: `FLAG_2{stuxnet_hmi_replay_deception_success_8842}`
