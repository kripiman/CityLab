#!/usr/bin/env python3
"""scripts/generate_scenario_manifests.py — Generador de manifiestos YAML para escenarios 01-29
"""
from pathlib import Path
import json
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = REPO_ROOT / "config" / "scenarios"
SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)

MANIFESTS = {
    "01": {
        "id": "01",
        "title": "Apagón Urbano en Cascada",
        "difficulty": "Avanzado",
        "category": "Multi-Sector Industrial Impact / Cascading Failure",
        "seed_scope": ["unit_ids", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Reconocimiento DMZ completado",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Subfrecuencia de red provocada",
                "points": 200,
                "check": {"type": "historian_condition", "query": "grid_freq_hz < 58.0", "sector": "elec", "window_s": 60}
            },
            {
                "id": "FLAG_3",
                "desc": "Apagón en cascada logrado",
                "points": 300,
                "check": {"type": "scada_sector_status", "sector": "water", "expect": "LOSS_OF_VIEW"}
            }
        ]
    },
    "02": {
        "id": "02",
        "title": "Inyección y Spoofing de Mensajes GOOSE IEC 61850",
        "difficulty": "Avanzada",
        "category": "Industrial Cybersecurity / Substation Automation / IEC 61850",
        "seed_scope": ["stnum_offsets", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Sniffing de multicast GOOSE en subestación",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/health", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Disparo no autorizado de interruptor de subestación detectado en SIEM",
                "points": 200,
                "check": {"type": "siem_alert", "rule": "GOOSE"}
            }
        ]
    },
    "03": {
        "id": "03",
        "title": "Ataque Low and Slow al Sistema SIS SIL-3",
        "difficulty": "Avanzado",
        "category": "Safety Instrumented Systems / Triton / HatMan Emulation",
        "seed_scope": ["delta_drift", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Lectura de telemetría de seguridad SIL-3",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Desvío sigiloso de umbrales SIS verificado en Historian",
                "points": 250,
                "check": {"type": "historian_condition", "query": "pressure_psi > 120.0", "sector": "gas", "window_s": 90}
            }
        ]
    },
    "04": {
        "id": "04",
        "title": "Replay Attack Modbus Tipo Stuxnet",
        "difficulty": "Intermedio",
        "category": "Industrial Protocol Exploitation / Modbus Replay",
        "seed_scope": ["packet_hashes", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Captura de paquetes Modbus legítimos",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Replay inyectado y detectado por anomalía Modbus DPI",
                "points": 200,
                "check": {"type": "siem_alert", "rule": "Modbus"}
            }
        ]
    },
    "05": {
        "id": "05",
        "title": "Conmutación y Failover en Cluster SCADA HA",
        "difficulty": "Intermedio",
        "category": "High Availability / SCADA Resilience",
        "seed_scope": ["heartbeat_interval", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Inspección de estado de cluster SCADA HA",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/ha/status", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Failover ejecutado exitosamente manteniendo visibilidad",
                "points": 200,
                "check": {"type": "scada_sector_status", "sector": "elec", "expect": "NORMAL"}
            }
        ]
    },
    "06": {
        "id": "06",
        "title": "Kerberoasting y Abuso de Samba Active Directory",
        "difficulty": "Avanzado",
        "category": "Identity & Access Management / Active Directory / Kerberos",
        "seed_scope": ["spn_accounts", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Enumeración de SPNs en Domain Controller",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/whoami", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Alerta de Kerberoasting / Ticket TGS anómalo detectada en SIEM",
                "points": 250,
                "check": {"type": "siem_alert", "rule": "Kerberos"}
            }
        ]
    },
    "07": {
        "id": "07",
        "title": "Anti-Forense y Manipulación de Historian TSDB",
        "difficulty": "Avanzado",
        "category": "Industrial Forensics / TSDB Integrity / Anti-Forensics",
        "seed_scope": ["sqlite_wal_salts", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Consulta de auditoría sobre tabla de telemetría Historian",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/history?sector=water", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Detección de manipulación de registros históricos",
                "points": 250,
                "check": {"type": "historian_condition", "query": "tampered == 1", "window_s": 120}
            }
        ]
    },
    "08": {
        "id": "08",
        "title": "Abuso de Privilegios y Escalación RBAC en SCADA",
        "difficulty": "Intermedio",
        "category": "Access Control / RBAC / Privilege Escalation",
        "seed_scope": ["role_tokens", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Auditoría de roles y permisos SCADA API",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/whoami", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Intento de comando no autorizado bloqueado con 403",
                "points": 200,
                "check": {"type": "siem_alert", "rule": "RBAC"}
            }
        ]
    },
    "09": {
        "id": "09",
        "title": "Dosificación Química en Planta de Tratamiento de Agua",
        "difficulty": "Avanzada",
        "category": "Water Treatment Process / Chemical Dosing (Oldsmar Pattern)",
        "seed_scope": ["chemical_thresholds", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Monitoreo de pH y nivel de cloro en sector agua",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Sobredosificación química detectada en Historian",
                "points": 250,
                "check": {"type": "historian_condition", "query": "ph_level > 8.5", "sector": "water", "window_s": 60}
            }
        ]
    },
    "10": {
        "id": "10",
        "title": "Atribución de Ola de Calor vs Ciberataque a la Red Eléctrica",
        "difficulty": "Avanzado",
        "category": "Incident Response / Cyber-Physical Attribution / Electrical Grid",
        "seed_scope": ["ambient_temp_profile", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Análisis de carga térmica y demanda en transformadores",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Correlación de eventos climáticos vs anomalía maliciosa",
                "points": 250,
                "check": {"type": "siem_alert", "rule": "Grid"}
            }
        ]
    },
    "11": {
        "id": "11",
        "title": "Spoofing de Tiempo NTP y Desincronización de Subestación",
        "difficulty": "Avanzado",
        "category": "Time Synchronization / NTP Spoofing / Substation Telemetry",
        "seed_scope": ["ntp_offset", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Verificación de drift de reloj en subestación",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/health", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Alerta de desincronización horaria en SIEM",
                "points": 200,
                "check": {"type": "siem_alert", "rule": "Time"}
            }
        ]
    },
    "12": {
        "id": "12",
        "title": "Ransomware con Impacto en Infraestructura OT",
        "difficulty": "Avanzado",
        "category": "Ransomware Emulation / IT-OT Lateral Movement",
        "seed_scope": ["encrypted_extensions", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Detección de cifrado de archivos en estación de ingeniería",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/health", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Aislamiento de segmento OT activado ante ransomware",
                "points": 250,
                "check": {"type": "openflow_rule", "switch": "s3", "pattern": "drop"}
            }
        ]
    },
    "13": {
        "id": "13",
        "title": "Reconocimiento Pasivo en Red OT",
        "difficulty": "Básico",
        "category": "Network Reconnaissance / Passive Sniffing / Industrial Asset Discovery",
        "seed_scope": ["mac_prefixes", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Descubrimiento de hosts y controladores en segmento OT",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            }
        ]
    },
    "14": {
        "id": "14",
        "title": "Escaneo Activo y Enumeración de PLCs OT",
        "difficulty": "Básico",
        "category": "Network Scanning / Modbus Enumeration / Asset Profiling",
        "seed_scope": ["unit_id_ranges", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Identificación de puertos industriales abiertos (502, 20000, 4840)",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Alerta de escaneo masivo de puertos detectada en honeypot/SIEM",
                "points": 150,
                "check": {"type": "siem_alert", "rule": "Scan"}
            }
        ]
    },
    "15": {
        "id": "15",
        "title": "Lectura de Telemetría Modbus TCP sin Autenticación",
        "difficulty": "Básico",
        "category": "Industrial Protocols / Modbus TCP / Unauthenticated Telemetry",
        "seed_scope": ["register_offsets", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Lectura de Holding Registers de sector agua vía Modbus TCP",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            }
        ]
    },
    "16": {
        "id": "16",
        "title": "Interacción y Detección de Honeypot OT",
        "difficulty": "Básico",
        "category": "Deception Technology / OT Honeypot / Threat Detection",
        "seed_scope": ["honey_coils", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Conexión e interacción con servicio decoy en 10.0.5.99",
                "points": 100,
                "check": {"type": "siem_alert", "rule": "Honeypot"}
            }
        ]
    },
    "17": {
        "id": "17",
        "title": "Exploración y Tour de la API HMI/SCADA",
        "difficulty": "Básico",
        "category": "SCADA Web Interface / REST API / Telemetry Exploration",
        "seed_scope": ["endpoints", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Inspección de endpoints /api/telemetry y /api/history",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            }
        ]
    },
    "18": {
        "id": "18",
        "title": "Escritura de Bobina Individual Modbus (Single Coil Write)",
        "difficulty": "Intermedio",
        "category": "Process Control Manipulation / Modbus Function Code 05",
        "seed_scope": ["coil_index", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Escritura de bobina FC05 sobre PLC de gas o agua",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Cambio de actuador registrado en Historian",
                "points": 150,
                "check": {"type": "historian_condition", "query": "pump_state == 1", "window_s": 60}
            }
        ]
    },
    "19": {
        "id": "19",
        "title": "Cadena de Pivoteo Guiada Attacker -> DMZ -> OT",
        "difficulty": "Intermedio",
        "category": "Network Pivoting / Multi-Tier Segmentation / Conduit Traversal",
        "seed_scope": ["pivoting_paths", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Salto desde segmento corporativo a DMZ",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/health", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Pivoteo exitoso de DMZ a red OT",
                "points": 200,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            }
        ]
    },
    "20": {
        "id": "20",
        "title": "Conmutación de Modo de Autenticación Estricta (STRICT_AUTH)",
        "difficulty": "Intermedio",
        "category": "Security Hardening / RBAC / Authentication Enforcing",
        "seed_scope": ["strict_tokens", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Verificación de enforcement de tokens de rol en SCADA API",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/whoami", "expect": 200}
            }
        ]
    },
    "21": {
        "id": "21",
        "title": "Pérdida de Visibilidad (Loss of View) y Aislamiento Manual",
        "difficulty": "Intermedio",
        "category": "Loss of View / SCADA Watchdog / Incident Containment",
        "seed_scope": ["timeout_thresholds", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Pérdida de paquetes de telemetría provocada",
                "points": 100,
                "check": {"type": "scada_sector_status", "sector": "water", "expect": "LOSS_OF_VIEW"}
            },
            {
                "id": "FLAG_2",
                "desc": "Aislamiento manual ejecutado en switch de acceso",
                "points": 150,
                "check": {"type": "openflow_rule", "switch": "s3", "pattern": "drop"}
            }
        ]
    },
    "22": {
        "id": "22",
        "title": "Métricas Purple Team: Medición y Optimización de MTTD",
        "difficulty": "Avanzado",
        "category": "Purple Teaming / SOC Evaluation / MTTD Metrics",
        "seed_scope": ["detection_windows", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Generación de eventos de prueba y correlación SIEM",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8514/health", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "MTTD inferior a 15 segundos registrado en Scoreboard",
                "points": 200,
                "check": {"type": "siem_alert", "rule": "MTTD"}
            }
        ]
    },
    "23": {
        "id": "23",
        "title": "Defensa Dinámica con Controlador SDN y Circuit Breaker",
        "difficulty": "Avanzado",
        "category": "Software-Defined Networking / Automated Incident Response / OpenFlow",
        "seed_scope": ["flow_priorities", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Disparo automático de Circuit Breaker ante anomalía",
                "points": 100,
                "check": {"type": "siem_alert", "rule": "Circuit Breaker"}
            },
            {
                "id": "FLAG_2",
                "desc": "Regla OpenFlow DROP activa en tabla de flujo de s3",
                "points": 200,
                "check": {"type": "openflow_rule", "switch": "s3", "pattern": "drop"}
            }
        ]
    },
    "24": {
        "id": "24",
        "title": "Evasión de Reglas SIEM con Múltiples IPs de Origen",
        "difficulty": "Avanzada",
        "category": "SIEM Evasion / Distributed Probing / Correlation Engine Testing",
        "seed_scope": ["ip_pool", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Distribución de sondas Modbus entre múltiples direcciones IP",
                "points": 150,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Correlación multi-origen activada en pipeline SIEM",
                "points": 250,
                "check": {"type": "siem_alert", "rule": "Multi-IP"}
            }
        ]
    },
    "25": {
        "id": "25",
        "title": "Ejercicio Tabletop de Respuesta a Incidentes por Ransomware",
        "difficulty": "Intermedio",
        "category": "Incident Response / Tabletop Simulation / Crisis Management",
        "seed_scope": ["incident_timeline", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Evaluación de plan de contingencia y aislamiento de activos críticos",
                "points": 100,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/health", "expect": 200}
            }
        ]
    },
    "26": {
        "id": "26",
        "title": "Emulación de Campaña APT Tipo Sandworm",
        "difficulty": "Capstone",
        "category": "Threat Emulation / APT Campaign / BlackEnergy & Industroyer",
        "seed_scope": ["attack_vectors", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Compromiso de credenciales en Active Directory",
                "points": 150,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/whoami", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Desconexión de subestación eléctrica mediante ataque coordinado",
                "points": 250,
                "check": {"type": "historian_condition", "query": "grid_freq_hz < 58.0", "sector": "elec", "window_s": 60}
            },
            {
                "id": "FLAG_3",
                "desc": "Anti-forense y borrado de logs detectado en SIEM",
                "points": 300,
                "check": {"type": "siem_alert", "rule": "Sandworm"}
            }
        ]
    },
    "27": {
        "id": "27",
        "title": "Enfrentamiento Red vs Blue Adjudicado",
        "difficulty": "Capstone",
        "category": "Live Fire Exercise / Red vs Blue Adjudication / Scoreboard",
        "seed_scope": ["match_id", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Primer objetivo de intrusión capturado",
                "points": 200,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Mitigación Blue Team aplicada en tiempo objetivo",
                "points": 300,
                "check": {"type": "openflow_rule", "switch": "s3", "pattern": "drop"}
            }
        ]
    },
    "28": {
        "id": "28",
        "title": "Entorno Ciego Anti-Memorización",
        "difficulty": "Avanzado",
        "category": "Anti-Memorization / Dynamic Target Obfuscation / Seeded Range",
        "seed_scope": ["all", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Descubrimiento de parámetros dinámicos de sesión",
                "points": 150,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8570/health", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Resolución de objetivo con offsets aleatorizados",
                "points": 250,
                "check": {"type": "scada_sector_status", "sector": "water", "expect": "NORMAL"}
            }
        ]
    },
    "29": {
        "id": "29",
        "title": "Recuperación ante Desastres (Disaster Recovery) Post-Incidente",
        "difficulty": "Profesional",
        "category": "Disaster Recovery / Restoration of Process / Cold Restart",
        "seed_scope": ["backup_timestamps", "flags"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Restauración de base de datos Historian desde snapshot de respaldo",
                "points": 150,
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/history?sector=water", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Reanudación de operación nominal en todos los sectores urbanos",
                "points": 250,
                "check": {"type": "scada_sector_status", "sector": "water", "expect": "NORMAL"}
            }
        ]
    }
}

def generate_all():
    schema_path = REPO_ROOT / "config" / "scenarios" / "schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        import jsonschema
        has_jsonschema = True
    except ImportError:
        has_jsonschema = False

    for sc_id, manifest in MANIFESTS.items():
        norm_id = str(sc_id).zfill(2)
        out_file = SCENARIOS_DIR / f"scenario_{norm_id}.yml"
        
        if has_jsonschema:
            jsonschema.validate(instance=manifest, schema=schema)
            
        with open(out_file, "w", encoding="utf-8") as f:
            yaml.dump(manifest, f, sort_keys=False, allow_unicode=True)
            
        print(f"✅ Generado: scenario_{norm_id}.yml ({manifest['title']})")

if __name__ == '__main__':
    generate_all()
