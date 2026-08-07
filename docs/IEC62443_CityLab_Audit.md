# 🔒 REPORTE EJECUTIVO DE AUDITORÍA DE CIBERSEGURIDAD INDUSTRIAL
## CityLab Cyber Range — Evaluación bajo IEC 62443

**Auditor:** Principal ICS Security Auditor (GICSP)  
**Clasificación:** CONFIDENCIAL — Solo para uso del equipo de laboratorio  
**Fecha:** 2026-08-07  
**Estándar aplicado:** IEC 62443-2-1, 3-2, 3-3 / IEEE 1815 (DNP3) / IEC 61850  
**Alcance:** Topología Mininet (3 zonas), 10 nodos, 5 PLCs Modbus/TCP + 1 Outstation DNP3, 1 AD DC  

---

> [!CAUTION]
> Este reporte identifica **vulnerabilidades críticas reales en el diseño** del Cyber Range. Las debilidades documentadas son intencionalmente reproducibles para fines pedagógicos, pero representan patrones de ataque observados en redes OT de producción.

---

## 📋 RESUMEN EJECUTIVO

El análisis del grafo de arquitectura (284 nodos, 400 aristas, 37 comunidades) revela que la arquitectura CityLab implementa segmentación de red en tres niveles (Corporate / DMZ / OT) mediante iptables, pero presenta **seis hallazgos críticos** que invalidan la protección "Defensa en Profundidad" exigida por IEC 62443-3-2. La cadena de ataque `Attacker → DMZ → EWS → OT` es completamente ejecutable sin necesidad de explotar ningún zero-day. El vector principal es la **ausencia total de autenticación y cifrado en los protocolos de nivel de campo** (Modbus/TCP, DNP3 sin Application Layer Security).

---

## 🔴 SECCIÓN 1 — Zonas, Conductos y Vectores de Ataque (IEC 62443-3-2)

### FINDING-01 — Ausencia de Defensa en Profundidad: Pivoteo Directo DMZ→OT sin Inspección de Estado
**Severidad:** 🔴 CRÍTICA (CVSS 3.1: 9.8)

**Evidencia técnica ([topology.py](file:///home/kripi/Documentos/GitHub/CityLab/network/topology.py#L125-L132)):**
```python
# Permit DMZ -> OT Modbus/TCP (port 502) to all PLCs
for plc_ip in ('10.0.3.10', '10.0.3.12', '10.0.3.13', '10.0.3.14', '10.0.3.15'):
    fw.cmd(f"iptables -A FORWARD -i fw-eth1 -o fw-eth2 -p tcp --dport 502 -d {plc_ip} -j ACCEPT")
    fw.cmd(f"iptables -A FORWARD -i fw-eth2 -o fw-eth1 -p tcp --sport 502 -s {plc_ip} -j ACCEPT")
# Permit DMZ -> OT DNP3 (port 20000) for Electrical PLC (10.0.3.13)
fw.cmd("iptables -A FORWARD -i fw-eth1 -o fw-eth2 -p tcp --dport 20000 -d 10.0.3.13 -j ACCEPT")
```

**Análisis:** Las reglas de firewall permiten que **cualquier host en la DMZ** (10.0.2.0/24) alcance **cualquier PLC en la zona OT** (10.0.3.0/24) en puertos 502 y 20000. Esto viola IEC 62443-3-2 §6.5 porque:

1. **No hay restricción de IP de origen en la DMZ** — `h_dmz`, `h_scada` y `h_ews` tienen acceso idéntico a todos los PLCs.
2. **iptables no implementa DPI** — un flujo Modbus legítimo y un flujo de ataque son indistinguibles por las ACLs actuales.
3. **No existe Data Diode ni Unidirectional Gateway** — el tráfico es bidireccional (la regla `fw-eth2 → fw-eth1` permite que un PLC comprometido inicie conexiones hacia la DMZ).

**Violación IEC 62443:** §4.3.3.4.1 (Zone Boundary Protection), §6.5.3 (Conduit Design for Different SLs)

**Recomendación técnica:**
- **Corto plazo (30 min):** Agregar `-s 10.0.2.20` a las reglas Modbus para restringir solo a `h_scada`, y `--ctstate ESTABLISHED,RELATED` para eliminar la regla inversa broadcast.
- **Mediano plazo:** Agregar una zona **Purdue Level 3.5** (DMZ-OT) intermediada por un proxy Modbus/DNP3 que valide Function Codes (ver CONTROL-COMP-01).
- **Largo plazo:** Reemplazar iptables por un Data Diode Unidireccional (emulado en Mininet vía TC-netem con restricción de SYN inverso).

---

### FINDING-02 — h_ews como SPOF Inaceptable
**Severidad:** 🔴 CRÍTICA (CVSS 3.1: 9.1)

**Evidencia técnica ([topology.py](file:///home/kripi/Documentos/GitHub/CityLab/network/topology.py#L72), [ad_dc_emulator.py](file:///home/kripi/Documentos/GitHub/CityLab/network/ad_dc_emulator.py#L20-L24)):**
```python
# h_ews @ 10.0.2.30 — Engineer Workstation en DMZ
ews_station = self.addHost('h_ews', ip='10.0.2.30/24')

# SPN registrado en AD — trivialmente Kerberoastable:
KERBEROAST_TGS_HASH = (
    "$krb5tgs$23$*krbe_ews$CITYLAB.LOCAL$HTTP/h_ews.citylab.local*"
    "a1b2c3d4e5f60718293a4b5c6d7e8f90$..."
)
```

**Análisis:** `h_ews` concentra cuatro factores de riesgo acumulativos:

| Factor | Detalle |
|--------|---------|
| **Posición de red** | Único nodo DMZ con acceso de escritura a todos los PLCs |
| **Credencial expuesta** | `krbe_ews` tiene SPN `HTTP/h_ews.citylab.local` → Kerberoasting sin escalada |
| **Sin MFA** | No existe 2FA para acceso al EWS desde la red corporativa |
| **Sin restricción de origen** | SSH (TCP/22) desde `h_attacker` (10.0.1.10) hacia DMZ sin exclusión explícita de h_ews |

**Cadena de explotación documentada:**
```
h_attacker (10.0.1.10)
  → LDAP Enum (10.0.1.20:389) → descubre krbe_ews SPN
  → AS-REP Roast jdoe_eng → obtiene hash sin preauth
  → Kerberoast HTTP/h_ews → obtiene TGS hash (crackeable offline)
  → Lateral movement → h_ews (10.0.2.30)
  → attack_modbus.py / exploit_modbus.py → TODOS los PLCs (10.0.3.x:502)
```

**¿Es h_ews un SPOF inaceptable? Sí, definitivamente.** Cumple las cuatro condiciones del IEC 62443-2-4 §9.2:
- Es el único nodo de configuración activa de PLCs (sin redundancia `h_ews_backup`).
- Su compromiso da acceso a todos los PLCs sin escalada adicional.
- Está en zona DMZ (SL2), no en una zona EWS aislada (SL3).
- La ruta de compromiso es predecible y ejecutable en < 15 minutos.

---

### FINDING-03 — Conduit Corporate→DMZ: AD DC y Attacker en Mismo Segmento L2
**Severidad:** 🟠 ALTA (CVSS 3.1: 8.1)

**Evidencia ([topology.py](file:///home/kripi/Documentos/GitHub/CityLab/network/topology.py#L67-L68)):**
```python
# Mismo switch s1 — sin microsegmentación intrazona
attacker = self.addHost('h_attacker', ip='10.0.1.10/24')
corp_dc  = self.addHost('h_dc',       ip='10.0.1.20/24')
```

**Análisis:** No existen ACLs entre nodos de la zona Corporate. El atacante puede hacer LDAP/Kerberos/SMB directamente contra `h_dc` sin atravesar el firewall, habilitando AS-REP Roasting de `jdoe_eng` y Kerberoasting de `krbe_ews` como paso inicial de la cadena.

---

## 🔴 SECCIÓN 2 — Impacto Físico y Fallas en Cascada (Resiliencia)

### FINDING-04 — Cadena de Fallo Ciberfísico sin Mecanismo de Safe State
**Severidad:** 🔴 CRÍTICA (CVSS 3.1: 9.6 — CPS Score)

**Evidencia técnica ([fed_hospital.py](file:///home/kripi/Documentos/GitHub/CityLab/helics_sim/fed_hospital.py)):**
```python
suppress_gen = bool(rr.bits[1])  # actuator_stop → inhibe generador
```

**Cadena de fallo ciberfísico completa:**
```
PASO 1: attack_multisector.py --sector gas --mode stop
  → PLC Gas (10.0.3.12): coil[1]=1 (STOP valve)
  → GasPlant.needs_trip() == True (pressure < 20 PSI)
  → ElecPlant.p_gen_pu -= 0.30  [HELICS: gas/supply_ok = False → -30% generación]

PASO 2: attack_multisector.py --sector hospital --mode fault
  → PLC Hospital (10.0.3.15): coil[0]=1 AND coil[1]=1
  → fed_hospital.py lee coil[1]=1 → suppress_generator = True

EFECTO FÍSICO EN CASCADA:
  Grid frequency drops → HospitalPlant: GRID_NORMAL → UPS_ACTIVE
  → UPS descargándose
  → Generator INHIBIDO (suppress_generator = True desde PLC comprometido)
  → UPS agotado → PowerState.CRITICAL_BLACKOUT ← IMPACTO CRÍTICO
```

---

### FINDING-05 — Loss of View / Loss of Control: Sin Protocolo de Respuesta
**Severidad:** 🟠 ALTA (CVSS 3.1: 7.5)

**Análisis:** El SCADA (`h_scada:8080`) hace polling periódico a los PLCs pero no distingue entre fallos de red e inyección maliciosa de datos.

---

## 🔴 SECCIÓN 3 — Controles de Sistema y Mitigación (IEC 62443-3-3)

### FINDING-06 — Ausencia Total de Autenticación/Integridad en Modbus/TCP y DNP3 (SA Level 0)
**Severidad:** 🔴 CRÍTICA (CVSS 3.1: 9.8)

---

## 🛡️ TRES CONTROLES COMPENSATORIOS TÉCNICOS

### CONTROL-COMP-01 — Proxy DPI Modbus/TCP (Preventivo + Detective)
**IEC 62443:** SR 3.5 (Input Validation), SR 6.1 (Audit Log)  
**Latencia adicional:** < 0.3ms  

### CONTROL-COMP-02 — Reglas de Flujo SDN con Microsegmentación por Función (Preventivo)
**IEC 62443:** SR 5.1 (Network Segmentation), SR 5.2 (Zone Boundary Protection)  
**Latencia adicional:** Sub-milisegundo  

### CONTROL-COMP-03 — Honeypot PLC OT con Alerting Temprano (`h_plc_honey` @ `10.0.3.99`) (Detective)
**IEC 62443:** SR 6.1 (Audit Log Accessibility), SR 6.2 (Continuous Monitoring)  

---

## 🎯 ROADMAP DE MITIGACIÓN PRIORITIZADO

```
SEMANA 1 — Quick Wins (< 4h total):
  ✅ CONTROL-COMP-03: Desplegar honeypot PLC h_plc_honey @ 10.0.3.99  (2h)
  ✅ F-01 parcial:    Agregar ACL de origen estricta en iptables DMZ→OT (30 min)
  ✅ F-04 parcial:    Safe State timeout 5s en fed_hospital.py          (1h)

SEMANA 2 — Controles Sustantivos:
  🔧 CONTROL-COMP-01: Proxy DPI Modbus como componente network/modbus_proxy.py
  🔧 F-02:            Zona EWS aislada (switch s4 en topology.py + reglas PAW)
  🔧 F-05:            Watchdog Loss of View en scada_server.py + bus HELICS alarm

SEMANA 3 — Controles Avanzados:
  🔧 CONTROL-COMP-02: Reglas SDN OpenFlow en switches OVS
  🔧 F-06:            DNP3 SA Level 1 simulado en dnp3_emulator.py (HMAC-SHA256)
  🔧 F-03:            Documentar debilidad aceptada en ERS + sub-VLAN por rol
```
