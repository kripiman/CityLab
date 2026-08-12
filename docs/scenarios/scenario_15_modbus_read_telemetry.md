# Escenario CTF 15: Lectura de Telemetría Modbus sin Escritura

**Dificultad**: Fácil (Onboarding)  
**Categoría**: Industrial Cybersecurity / Modbus Read-Only / Process Visibility  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El estudiante debe consultar el estado operacional del PLC de Agua (`10.0.3.10:502`) leyendo las bobinas e inputs sin modificar ningún parámetro de control, aprendiendo el mapa de memoria Modbus y su correspondencia física.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Lectura de Memoria Modbus
1. Ejecutar `attacker/attack_modbus_read_only.py`:
   ```bash
   python3 attacker/attack_modbus_read_only.py
   ```
2. Verificar la correspondencia entre los bits leídos y el nivel del tanque físico.

---

## 3. Lección Pedagógica

Muestra cómo la **ausencia de autenticación en la función de lectura Modbus** permite a un atacante espiar el proceso industrial antes de lanzar un sabotaje.

---

## 4. Flags CTF

- **FLAG 1 (Modbus Memory Mapped)**: `FLAG_1{modbus_coils_holding_registers_mapped_1102}`
