# 🖥️ Infraestructura 07 — Servidor SCADA Central, HA Cluster y Dashboard HMI

## 📌 1. Visión General del Módulo
La infraestructura SCADA/HMI proporciona la capa de supervisión centralizada, adquisición de datos (SCADA Polling Engine), alta disponibilidad (Cluster Primario/Standby con Heartbeat), autenticación RBAC con tokens Bearer estáticos (`Authorization: Bearer <role>:<token>`, sin JWT), y la interfaz HMI P&ID para operadores de planta.

- **Archivos fuente**: [`network/scada_server.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/scada_server.py), [`network/scada_ha.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/scada_ha.py), [`network/hmi_server.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/hmi_server.py), [`network/historian.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/historian.py), [`network/viz_server.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/viz_server.py), [`network/rbac.py`](file:///home/kripi/Documentos/GitHub/CityLab/network/rbac.py).
- **IPs / Puertos**: `h_scada` (`0.0.0.0:8080` SCADA REST API), HMI Engine (`http://127.0.0.1:8085` / `:8080`), Viz Server (`http://127.0.0.1:8090`).
- **Asignación de Memoria (RAM)**: ~220 MB en ejecución continua (dentro del margen global de **8 GB RAM**).

---

## ⚙️ 2. Arquitectura de Control, Historian y Conmutación HA (High Availability)

```mermaid
sequenceDiagram
    autonumber
    participant HMI as Industrial HMI Engine (:8085)
    participant SCADA_PRI as SCADA Primario (h_scada:8080)
    participant SCADA_STBY as SCADA Standby (:8081)
    participant HIST as Historian TSDB (SQLite WAL)
    participant PLC as PLCs OT (Water/Gas/Elec/Transport/Hosp)

    loop Polling Loop Continuo (1.0 s)
        SCADA_PRI->>PLC: poll_plcs_once() via ModbusTcpClient / DNP3
        alt Conexión Exitosa
            PLC-->>SCADA_PRI: Retorna Coils y Holding Registers
            SCADA_PRI->>HIST: write_snapshot() / write() en WAL
            SCADA_PRI->>SCADA_PRI: Resetea _consecutive_failures[sector] = 0
        else Fallo de Comunicación (Errno 99 / ConnectionRefused)
            SCADA_PRI->>SCADA_PRI: Incrementa _consecutive_failures[sector] += 1
            opt _consecutive_failures >= 3 (LOSS_OF_VIEW_THRESHOLD)
                SCADA_PRI->>SCADA_PRI: Marca sector['status'] = 'LOSS_OF_VIEW'
            end
        end
        SCADA_PRI->>SCADA_STBY: Sync Estado de Estado ('/api/ha/sync')
    end

    HMI->>SCADA_PRI: GET /api/scada (Overview & Alarmas)
    SCADA_PRI-->>HMI: Retorna JSON Estado de Sectores + Alertas Loss-of-View
    HMI->>HIST: query() / GET /api/history (Series Temporales)
```

---

## 🔐 3. Control de Acceso por Roles (RBAC Bearer Estático & Toggle `STRICT_AUTH`)

> **Nota de fidelidad**: `network/rbac.py` resuelve el token contra una tabla estática en memoria (`Bearer <role>:<token>`) — no hay JWT (sin firma, sin claims, sin expiración). Cero `import jwt`/`PyJWT`/`jose` en el repo.

```mermaid
flowchart TD
    Req["Petición HTTP Client / Attacker"] --> AuthCheck{"STRICT_AUTH activado? (0 ó 1)"}
    AuthCheck -- "0 (Fase Permisiva)" --> PassAll["Permite acceso con rol por defecto 'operator' (200 OK)"]
    AuthCheck -- "1 (Fase Estricta)" --> CheckToken{"Token 'Authorization: Bearer <token>' presente?"}
    CheckToken -- "No" --> Deny401["401 Unauthorized / 403 Forbidden"]
    CheckToken -- "Sí" --> VerifyRole{"Rol extraído ('auditor'/'operator'/'engineer') tiene permiso?"}
    VerifyRole -- "Insuficiente ('auditor' intenta POST /api/control)" --> Deny403["403 Forbidden: Rol insuficiente"]
    VerifyRole -- "Válido ('operator' / 'engineer')" --> ExecCmd["Ejecuta comando en SCADA (200 OK)"]
```

---

## 🌐 4. Endpoints REST API de Infraestructura SCADA / HMI / Viz (`:8080`, `:8085`, `:8090`)

| Método | Endpoint | Componente | Descripción |
|---|---|---|---|
| `GET` | `/api/scada` | SCADA Server (`:8080`) | Retorna telemetría consolidada de los 5 sectores y alarmas activo |
| `GET` | `/api/whoami` | SCADA Server (`:8080`) | Introspección de identidad de usuario y permisos |
| `POST` | `/api/control` | SCADA Server (`:8080`) | Ejecuta mandos de conmutación de bombas, válvulas o interruptores |
| `POST` | `/api/control/write` | SCADA Server (`:8080`) | Modificación estricta de parámetros de calibración de PLC |
| `GET` | `/api/ha/status` | SCADA HA (`:8080`) | Estado de cluster HA (PRIMARY/STANDBY, timestamp último heartbeat) |
| `POST` | `/api/ha/heartbeat` | SCADA HA (`:8080`) | Recepción de latido entre nodos SCADA |
| `POST` | `/api/ha/sync` | SCADA HA (`:8080`) | Sincronización de estado entre SCADA Primario y Standby |
| `GET` | `/api/history` | HMI Historian (`:8085`) | Consulta de series temporales históricas almacenadas en SQLite WAL |
| `GET` | `/api/viz/frame` | Viz Server (`:8090`) | Cuadro de renderizado en tiempo real para visualizador 2D/3D |
| `GET` | `/api/viz/history` | Viz Server (`:8090`) | Histórico de cuadros para reproductor de tendencias 2D/3D |
| `POST` | `/api/viz/update` | Viz Server (`:8090`) | Actualización de estado sectorial desde HELICS o SCADA |

---

## 💾 5. Presupuesto de Recursos y Memoria RAM
- **Huella de memoria RAM objetivo**: **~220 MB** (Python + HTTPServer + PyModbus). *Estimación de diseño. Para la cifra medida ejecuta `./citylab.sh profile` (`scripts/profile_resources.py`) y consulta `logs/resource_profile_summary.txt`.*
- **Límite de tiempo de respuesta REST**: <10 ms.
- **Uso de CPU**: <3% 1 vCPU.
