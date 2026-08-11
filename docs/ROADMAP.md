# 🗺️ ROADMAP Y FIDELIDAD ARQUITECTÓNICA — CityLab Cyber Range

## 📊 Evaluación de Fidelidad Realista (Cyber Range Puramente Software)

| Dimensión | Porcentaje de Fidelidad | Estado Actual | Gaps para Producción / Máxima Fidelidad |
|-----------|:-----------------------:|---------------|-----------------------------------------|
| **Ciberseguridad IT/OT** | **65-70%** | Segmentación IEC 62443 (Zonas/Conduits), Modbus DPI Proxy, DNP3 SA L1, Active Directory Domain Controller (`h_dc`). | Protocolos adicionales (IEC 61850, OPC UA, EtherNet/IP, S7comm, BACnet, wireless OT). |
| **Proceso Físico / Ciudad** | **25-30%** | Co-simulación HELICS coordinada (7 federados: Agua, Gas, Eléctrica, Hospital, Transporte, GridLAB-D, Logger). | Dinámica real de fluidos (EPANET), GridLAB-D completo, solvers Modelica/Simulink, gemelo digital físico. |
| **Operación / Realidad SCADA** | **40-45%** | SCADA Server con API JSON, Watchdog Loss of View/Control, Proxy Modbus. | HMI industrial (Ignition Edge/Wonderware), Historian de tiempo real (TSDB InfluxDB/TimescaleDB), MES/ERP, RBAC/PAM, SOC/SIEM (Elastic/Graylog), redundancia DCS (hot-standby), SIS independiente. |
| **FIDELIDAD GLOBAL CIUDAD** | **50-55%** | **Cyber Range 100% software optimizado para RAM (<1.5 GB)** | **Límite máximo en software puro = 70%. El 30% restante requiere Hardware-in-the-Loop (HIL).** |

---

## 🛣️ Roadmap de Evolución Tecnológica (8 Puntos de Mejora)

1. **Protocolos Industriales Adicionales**: Integrar emuladores IEC 61850 (GOOSE/SV en subestaciones), OPC UA (fábricas inteligentes) y BACnet (gestión de edificios).
2. **Historian de Tiempo Real**: Reemplazar almacén JSON en memoria por InfluxDB o TimescaleDB para series temporales industriales.
3. **HMI Profesional**: Conectar una interfaz SCADA/HMI real (ej. Ignition Edge) sobre las APIs emuladas.
4. **Acoplamiento Físico de Alta Fidelidad**: Integración directa con EPANET para redes de agua y extensión de GridLAB-D para flujo de carga trifásico.
5. **Redundancia y Failover DCS**: Implementación de arquitecturas DCS activo/pasivo y PLCs en hot-standby.
6. **Safety Instrumented Systems (SIS)**: Separar la capa de seguridad física (SIS/ESD) de la capa de control básico de proceso (BPCS).
7. **Gestión de Identidad y Accesos**: Evolucionar la autenticación a esquemas RBAC/PAM con integración Kerberos/Vault.
8. **Integración SOC / SIEM**: Canalización de auditoría DPI y logs de red a pila ELK/Graylog out-of-band.

---

## 🔌 Requisitos para Hardware-in-the-Loop (HIL)

La arquitectura de co-simulación HELICS del CityLab permite conectar PLCs físicos reales reemplazando o puenteando los federados emulados mediante interfaces de comunicación red/puerto. La fidelidad >70% requiere integrar latencia física de bus, ruido eléctrico, fallas mecánicas y sensores reales.
