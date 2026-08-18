# 🛡️ Infraestructura 08 — SIEM, SDN Controller y Active Directory Domain Controller

> **Estado**: **COMPLETADO (Fase 8)** — `network/siem_pipeline.py` opera como motor de recolección, normalización y correlación de eventos IT/OT en formato Elastic Common Schema (ECS), Syslog RFC 5424 y exportación directa a disco para integración con Kibana / ELK / Graylog.

## 📌 1. Visión General del Módulo
Esta infraestructura engloba los componentes centrales de seguridad cibernética e identidad corporativa de CityLab:
1. **Motor de Correlación SIEM**: Ingestión y normalización de eventos en formato ECS (Elastic Common Schema), Syslog RFC 5424, Zeek logs y Suricata Eve JSON, con detección de patrones de ciberguerra en cascada (GOOSE Spoofing, Kerberoasting, Fuerza Bruta).
2. **Controlador SDN OpenFlow**: Microsegmentación dinámica en switches Open vSwitch (OVS `s3` OT y `s5` Honeypot) con aislamiento automático Circuit Breaker.
3. **Active Directory DC Emulator**: Servidor Samba AD DC (`CITYLAB.LOCAL`) emulando servicios Kerberos (`:88`), LDAP (`:389`) y SMB (`:445`).
4. **Decoy Honeypot Server**: Trampa Conpot emulada en `10.0.5.99:502` para atracción y registro de escaneos hostiles.

- **Archivos fuente**: [`network/siem_pipeline.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/siem_pipeline.py), [`network/sdn_controller.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/sdn_controller.py), [`network/ad_dc_emulator.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/ad_dc_emulator.py), [`plc/honeypot_server.py`](file:///home/kripi/Documentos/GitHub/CityLab/plc/honeypot_server.py).
- **Asignación de Memoria (RAM)**: ~250 MB en ejecución conjunta (dentro del margen global de **8 GB RAM**).

---

## ⚙️ 2. Arquitectura de Defensa SDN y Correlación SIEM en Caliente

```mermaid
sequenceDiagram
    autonumber
    participant ATTACKER as Atacante (10.0.1.10)
    participant IED as IED Subestación (10.0.3.20)
    participant SIEM as SIEM Correlation Engine
    participant SDN as SDN Controller (OVS s3)

    ATTACKER->>IED: Inyección GOOSE Spoofing (XCBR1.Pos.stVal=False)
    IED->>IED: Registra disparo anormal XCBR1
    IED->>SIEM: Ingesta evento ilícito en formato ECS
    SIEM->>SIEM: Evalúa Regla 2 (Industroyer2 GOOSE Pattern)
    SIEM-->>SIEM: Genera Alerta Crítica SOC-ALT-0001
    SIEM->>SDN: Dispara Mitigación Dinámica / Circuit Breaker ('10.0.1.10')
    SDN->>SDN: Ejecuta ovs-ofctl add-flow s3 'priority=500,nw_src=10.0.1.10,actions=drop'
    Note over SDN: Switch OVS s3 instala regla Drop.<br/>Ping / Tráfico de 10.0.1.10 a OT sufre 100% loss.
```

---

## 🛡️ 3. Reglas de Correlación SIEM Destacadas

| ID Alerta | Regla SIEM | Vector de Ataque Detectado | Criterio de Activación ECS | Acción Automática |
|---|---|---|---|---|
| `SOC-ALT-0001` | Regla 2: GOOSE Spoofing | Industroyer2 / IEC 61850 Injection | `event_type == 'goose_injection'` & `severity == 'CRITICAL'` | Notificación SOC + Circuit Breaker SDN |
| `SOC-ALT-0002` | Regla 6: Kerberoasting | Extracción de tickets TGS en AD DC | `service_name == 'krbe_ews'` & `event_type == 'tgs_req'` | Aislamiento de cuenta de usuario en LDAP |
| `SOC-ALT-0003` | Regla 16: Honeypot Touch | Reconocimiento en Trampa OT | `destination_ip == '10.0.5.99'` & `dst_port == 502` | Bloqueo IP origen en Switch `s5` |

---

## 🔀 4. Matriz de Flujos OpenFlow Microsegmentación OVS (`s3` OT / `s5` Honeypot)

```mermaid
graph TD
    s3_flow["Matriz Flujos Switch s3 (OT)"]
    s3_flow --> F0["Priority 0: actions=NORMAL (Fallback)"]
    s3_flow --> F100_1["Priority 100: proto=TCP, dst_port=502 -> DROP (Default Block Modbus)"]
    s3_flow --> F100_2["Priority 100: proto=TCP, dst_port=20000 -> DROP (Default Block DNP3)"]
    s3_flow --> F200_1["Priority 200: src=10.0.2.20 (SCADA), dst_port=502 -> NORMAL"]
    s3_flow --> F200_2["Priority 200: src=10.0.4.30 (EWS), dst_port=502 -> NORMAL"]
    s3_flow --> F500["Priority 500: Circuit Breaker src=10.0.1.10 -> DROP"]

    s5_flow["Matriz Flujos Switch s5 (Honeypot)"]
    s5_flow --> H200["Priority 200: src=10.0.5.99, dst=10.0.3.0/24 -> DROP (Aísla Pivoteo a OT)"]
    s5_flow --> H100["Priority 100: dst=10.0.5.99 -> NORMAL (Permite Entrada a Trampa)"]
```

---

## 💾 5. Presupuesto de Recursos y Memoria RAM
- **Huella de memoria RAM objetivo**: **~250 MB** (Python + OVS daemon + Samba AD emulator). *Estimación de diseño. Para la cifra medida ejecuta `./citylab.sh profile` (`scripts/profile_resources.py`) y consulta `logs/resource_profile_summary.txt`.*
- **Límite de tiempo de procesamiento de regla SIEM**: <2 ms por evento.
- **Uso de CPU**: <2.5% 1 vCPU.
