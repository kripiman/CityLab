# CityLab — Cyber Range ICS/SCADA

Laboratorio de simulación ofensiva/defensiva en entornos ciberfísicos e infraestructuras críticas.
100% software, ejecución nativa en Linux, bajo consumo de RAM (<1 GB).

## Documentación
- [Guía de Arquitectura](file:///home/kripi/Documentos/GitHub/CityLab/docs/ARCHITECTURE.md): Diagramas de red (IEC 62443), secuencia de simulación e integración de HELICS.
- [Guía de Operaciones](file:///home/kripi/Documentos/GitHub/CityLab/docs/OPERATIONS.md): Pasos detallados para ejecutar ataques Modbus manuales y automatizados.

---

## Estructura del Proyecto

```
CityLab/
├── network/            # Emulación de red Mininet y reglas de firewall
├── plc/                # Lógica de control en ST y emulador Modbus
├── physical/           # Simulación física de tanques y bombas (ICSSIM)
├── helics_sim/         # Federados HELICS (ICSSIM, GridLAB-D, mocks)
├── gridlabd/           # Modelos de subestaciones eléctricas (.glm)
├── attacker/           # Scripts de ataque Modbus
├── docs/               # Documentación del proyecto
└── run_phase1.sh       # Script de inicio e integración
```

---

## Segmentación de Red (IEC 62443)

```
[Corporate 10.0.1.0/24] ── Firewall ── [DMZ 10.0.2.0/24] ── Firewall ── [OT Cell 10.0.3.0/24]
       │                                                                          │
  h_attacker (10.0.1.10)                                                   h_plc (10.0.3.10)
                                                                           h_icssim (10.0.3.11)
```

---

## Inicio Rápido

1. **Instalar dependencias del sistema**:
   - Debian/Ubuntu: `sudo apt install mininet openvswitch-switch`
   - Activar OVS: `sudo systemctl start openvswitch-switch`

2. **Instalar dependencias de Python**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar co-simulación**:
   ```bash
   sudo ./run_phase1.sh
   ```
