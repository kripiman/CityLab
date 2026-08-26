# 🛡️ Infraestructura 08 — SIEM Central, SDN Controller y Active Directory DC

## 📌 1. Visión General del Módulo
Esta infraestructura engloba los componentes centrales de detección, respuesta a incidentes e identidad corporativa de CityLab:
1. **Colector y Motor de Correlación SIEM (`network/siem_pipeline.py`)**: Opera como daemon HTTP en `10.0.2.20:8514`. Ingesta eventos en formato Elastic Common Schema (ECS), Syslog RFC 5424 y JSON directo. Recibe reenvíos asíncronos de auditoría de todos los emuladores y proxies OT mediante `SIEM_HTTP_URL=http://10.0.2.20:8514`.
2. **Controlador SDN OpenFlow (`network/sdn_controller.py`)**: Microsegmentación dinámica en switches Open vSwitch (OVS `s3` OT y `s5` Honeypot) con aislamiento automático Circuit Breaker en plano de datos.
3. **Active Directory DC Emulator (`network/ad_dc_emulator.py`)**: Servidor Samba AD DC (`CITYLAB.LOCAL` @ `10.0.1.20`) emulando Kerberos (`:88`), LDAP (`:389`) y SMB (`:445`), interconectado con la DMZ mediante conduit TCP 389.
4. **Decoy Honeypot Server (`plc/honeypot_server.py`)**: Trampa Conpot emulada en `10.0.5.99:502` para atracción y registro de escaneos hostiles.

- **Archivos fuente**: [`network/siem_pipeline.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/siem_pipeline.py), [`network/sdn_controller.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/sdn_controller.py), [`network/ad_dc_emulator.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/ad_dc_emulator.py), [`plc/honeypot_server.py`](file:///home/kripi/Documentos/GitHub/CityLab/plc/honeypot_server.py).
- **Asignación de Memoria (RAM)**: ~250 MB en ejecución conjunta (dentro del margen global de **8 GB RAM**).

---

## ⚙️ 2. Arquitectura de Reenvío Asíncrono y Detección SIEM

```mermaid
flowchart LR
    subgraph Producers ["Generadores de Eventos OT / IT"]
        PLC["PLCs Modbus (10.0.3.10..17)"]
        IED["IED Subestación (10.0.3.20)"]
        PROXY["Modbus DPI Proxy (10.0.2.20:15020)"]
        SCADA["SCADA Server (10.0.2.20:8080)"]
        HONEY["Honeypot (10.0.5.99:502)"]
    end

    subgraph SIEM_Daemon ["Colector y Motor de Correlación SIEM (10.0.2.20:8514)"]
        HTTP_Ingest["HTTP POST Ingest Engine"]
        Engine["SiemCorrelationEngine"]
        Rules["Reglas de Detección Heurísticas"]
        Alerts[("Alertas Activas SOC")]
    end

    subgraph SDN_Enforce ["Controlador SDN / OpenFlow"]
        SDN_Ctrl["SDN Controller"]
        Switch_S3["Switch OVS s3 (OT Data Plane)"]
    end

    PLC & IED & PROXY & SCADA & HONEY -.->|HTTP POST JSON (SIEM_HTTP_URL)| HTTP_Ingest
    HTTP_Ingest --> Engine
    Engine --> Rules
    Rules --> Alerts
    Rules -->|Trigger Circuit Breaker| SDN_Ctrl
    SDN_Ctrl -->|ovs-ofctl add-flow drop| Switch_S3
```

---

## 🛡️ 3. Reglas de Correlación SIEM Destacadas

| ID Alerta | Regla SIEM | Vector de Ataque Detectado | Criterio de Activación ECS | Acción Automática |
|---|---|---|---|---|
| `SOC-ALT-0001` | Regla 2: GOOSE Spoofing | Industroyer2 / IEC 61850 Injection | `event_type == 'goose_injection'` & `severity == 'CRITICAL'` | Notificación SOC + Circuit Breaker SDN |
| `SOC-ALT-0002` | Regla 1: Cascada Multisectorial | Ataque simultáneo a múltiples plantas | Eventos en >2 sectores en ventana $\le 10\text{ s}$ | Alerta crítica de ciberguerra urbana |
| `SOC-ALT-0003` | Regla 6: Kerberoasting | Extracción de tickets TGS en AD DC | `service_name == 'krbe_ews'` & `event_type == 'tgs_req'` | Aislamiento de cuenta de usuario en LDAP |
| `SOC-ALT-0004` | Regla 16: Honeypot Touch | Reconocimiento en Trampa OT | `destination_ip == '10.0.5.99'` & `dst_port == 502` | Bloqueo IP origen en Switch `s5` |
| `SOC-ALT-0005` | Regla 3: Modbus DPI Anomaly | Modbus FC no permitida o fuera de rango | Ingestión de denegación desde `modbus_proxy` | Registro de auditoría y penalización IP |

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

## 💾 5. Presupuesto de Recursos y Rendimiento
- **Huella de memoria RAM objetivo**: **~250 MB** (Python HTTP + OVS daemon + Samba AD emulator).
- **Límite de tiempo de procesamiento de regla SIEM**: <2 ms por evento.
- **Uso de CPU**: <2.5% 1 vCPU.

