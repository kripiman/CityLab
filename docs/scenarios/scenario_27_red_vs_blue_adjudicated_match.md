# Escenario CTF 27: Ciberejercicio Simultáneo Red vs Blue con Motor de Arbitraje

**Dificultad**: Profesional (Capstone)  
**Categoría**: Red vs Blue Match / Live Scoring Engine / Cyber Competition  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Competencia simultánea en tiempo real entre Red Team (buscando lograr disrupción física) y Blue Team (buscando aislar y mitigar amenazas), con un motor de arbitraje automático que otorga puntos según la velocidad y efectividad de respuesta.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Ejecución del Ciberejercicio
1. Ejecutar `attacker/attack_red_vs_blue_match.py`:
   ```bash
   python3 attacker/attack_red_vs_blue_match.py
   ```
2. Inspeccionar la puntuación final otorgada a cada equipo.

---

## 3. Lección Pedagógica

Fomenta el **trabajo en equipo operacional en entornos hiperrealistas**, donde la agilidad defensiva se mide directamente contra ataques en vivo.

---

## 4. Flags CTF

- **FLAG 1 (Red vs Blue Match Adjudicated)**: `FLAG_1{red_vs_blue_adjudicated_match_completed_8819}`
