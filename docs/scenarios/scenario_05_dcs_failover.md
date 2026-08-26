# Escenario CTF 05: Explotación de Ventana de Conmutación SCADA/DCS HA

**Dificultad**: Media-Avanzada  
**Categoría**: Industrial Cybersecurity / High Availability Failover / Race Conditions  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Los sistemas de alta disponibilidad (HA) reducen el tiempo de inactividad pero introducen una **superficie de ataque en la ventana de transición**. En este escenario, el atacante provoca una falla en el SCADA Primario y aprovecha los segundos de Failover hacia el nodo Standby para inyectar comandos desincronizados antes de la consolidación de estado.

---

## 2. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Interrupción del Servidor SCADA Primario y Monitoreo HA
1. Consultar el estado del cluster SCADA HA en `http://10.0.2.20:8080/api/ha/status`:
   ```bash
   curl -s http://10.0.2.20:8080/api/ha/status | jq .
   ```
2. Provocar la caída o interrupción de latidos (`/api/ha/heartbeat`) del nodo primario para disparar el timeout de 3 segundos en el nodo Standby (`network/scada_ha.py`).

### Paso 2: Explotación de la Transición HA y Desincronización
1. Ejecutar `attacker/attack_dcs_failover.py`:
   ```bash
   python3 attacker/attack_dcs_failover.py
   ```
2. Verificar en los logs la conmutación a rol `PRIMARY` y la ventana de sincronización de instantáneas de proceso (`/api/ha/sync`).

---

## 3. Lección Pedagógica

Enseña que **Alta Disponibilidad $\neq$ Seguridad**. Las ventanas de failover requieren autenticación mutua estricta y bloqueo temporal de comandos de escritura hasta verificar la sincronización completa del estado de proceso.

---

## 4. Flags CTF

- **FLAG 1 (Primary SCADA Interruption)**: `FLAG_1{scada_primary_dos_interrupted_4412}`
- **FLAG 2 (DCS Failover Race Condition)**: `FLAG_2{dcs_failover_race_condition_exploited_9901}`
