# Escenario CTF 17: Tour Guiado por la API SCADA y Servidor HMI

**Dificultad**: Fácil (Onboarding)  
**Categoría**: Industrial Cybersecurity / HMI Exploration / SCADA API  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

El estudiante explora la interfaz de supervisión industrial HMI P&ID que se ejecuta en el puerto HTTP `:8085` (`10.0.2.20:8085` en Mininet o `127.0.0.1:8085` en local). Aprende a consultar el estado del proceso mediante las llamadas REST (`/api/scada` y `/api/history`) e interactuar con la visualización web.

---

## 2. Cadena de Trabajo Paso a Paso

### Paso 1: Exploración REST API HMI
1. Ejecutar `attacker/attack_scada_tour.py`:
   ```bash
   python3 attacker/attack_scada_tour.py --host 10.0.2.20 --port 8085
   ```
2. Verificar la recepción del esquema JSON con las presiones, niveles de tanques y alarmas.

---

## 3. Lección Pedagógica

Familiariza al estudiante con la arquitectura moderna de supervisión industrial basada en tecnologías web (HTTP REST/WebSockets sobre HMI).

---

## 4. Flags CTF

- **FLAG 1 (HMI REST API Explored)**: `FLAG_1{scada_hmi_api_tour_completed_9920}`
