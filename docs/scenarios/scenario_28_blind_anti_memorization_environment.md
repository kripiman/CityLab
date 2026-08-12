# Escenario CTF 28: Entorno Ciego Dinámico Anti-Memorización

**Dificultad**: Profesional (Capstone)  
**Categoría**: Anti-Memorization / Dynamic Parameters / Blind Assessment  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Escenario dinámico en el que el laboratorio asigna aleatoriamente direcciones IP, puertos de servicio y umbrales de seguridad SIS. El estudiante no puede seguir una guía o receta previa y debe descubrir las vulnerabilidades aplicando metodologías de análisis desde cero.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución del Generador de Entorno Ciego
1. Ejecutar `attacker/attack_blind_randomized_env.py`:
   ```bash
   python3 attacker/attack_blind_randomized_env.py
   ```
2. Analizar las variables aleatorias y adaptar la estrategia de intrusión.

---

## 3. Lección Pedagógica

Garantiza que la evaluación evalúe **habilidades metodológicas reales (TTPs)** y no la memorización estática de parámetros de laboratorio.

---

## 4. Flags CTF

- **FLAG 1 (Blind Environment Solved)**: `FLAG_1{blind_dynamic_environment_methodology_proven_4412}`
