# CityLab — Cyber Range ICS/SCADA

Laboratorio de entrenamiento defensivo/ofensivo para infraestructura crítica.
100% software, Linux nativo, 4-8 GB RAM.

## Fase 1: Nodo Mínimo Viable

**Cadena de ataque objetivo:**
```
Ataque en Red (Python/Scapy)
  → Compromiso PLC (OpenPLC / Modbus TCP)
    → Alteración variable física (ICSSIM)
      → Sincronización bus (HELICS)
        → Caída disyuntor (GridLAB-D)
```

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Red / Emulación | Mininet (Python) |
| Lógica de Control | OpenPLC v3 + Structured Text (IEC 61131-3) |
| Simulación Física | ICSSIM (Python nativo) |
| Bus de Orquestación | HELICS 3.x |
| Simulación Eléctrica | GridLAB-D (.glm) |
| Ofensiva | pymodbus + scapy |

## Árbol de Directorios

```
CityLab/
├── network/            # Topología Mininet, zonas IEC 62443
│   └── topology.py
├── plc/                # Configuración OpenPLC
│   └── st_programs/    # Programas en Structured Text
├── physical/           # Simulación del proceso físico
│   └── icssim/
│       └── plant.py    # Federado HELICS + modelo de bomba/tanque
├── helics/             # Federados y configuración del broker
│   └── gridlabd_federate.py
├── gridlabd/           # Modelos eléctricos .glm
│   └── substation_phase1.glm
├── attacker/           # Scripts de ataque (uso ético/lab)
├── config/             # Configuraciones adicionales
├── logs/               # Salida de ejecución (generado en runtime)
├── .env.example        # Variables de entorno (copiar a .env)
├── requirements.txt    # Dependencias Python
└── run_phase1.sh       # Punto de entrada único
```

## Segmentación de Red (IEC 62443)

```
[Corporate 10.0.3.0/24] ── Firewall ── [DMZ 10.0.2.0/24] ── Firewall ── [OT Cell 10.0.1.0/24]
       │                                                                          │
  Nodo Atacante                                                            PLC (10.0.1.10)
                                                                           ICSSIM / Bomba
```

## Inicio Rápido

```bash
# 1. Instalar dependencias Python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configurar entorno
cp .env.example .env

# 3. Levantar Fase 1
./run_phase1.sh
```

## Estándares

- Segmentación de red: **IEC 62443** (Corporate / DMZ / OT Cell Zone)
- Programación PLC: **IEC 61131-3** (Structured Text)
- Python: **PEP 8**, tipado estático (`typing`), POO
