# Graph Report - CityLab  (2026-09-08)

## Corpus Check
- 226 files · ~113,897 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2253 nodes · 3513 edges · 190 communities (182 shown, 8 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 215 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ee6be01b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Iec61850Server
- test_flag_service.py
- ChemicalDosingAttack
- run_ovs_cmd
- SmartLightingSystem
- ModbusDpiEngine
- ElectricalSubstationGrid
- modbus_emulator.py
- SCADAPrimarySecondaryCluster
- 📌 1. Visión General del Módulo
- BacnetAttacker
- TestRBACResolver
- CityVisualizerStateEngine
- IndustrialHmiEngine
- Dnp3BreakerAttack
- 3. Requisitos Funcionales Específicos
- profile_resources.py
- execute_cascading_attack
- TestOpcUaServerClient
- SiemCorrelationEngine
- exploit_modbus.py
- ScoreboardEngine
- topology.py
- siem_pipeline.py
- running_modbus_server
- TritonLowSlowAttack
- SCADAAPIHandler
- RBACResolver
- TestScadaHistorianHTTPEndpoints
- TestHistorianTSDB
- ._recv_msg
- _emulator_harness.py
- 🏗️ PLAN DE IMPLEMENTACIÓN TÉCNICA: VISUALIZADOR URBANO 2D (FASE 9)
- TestScadaRBACHTTPEndpoints
- ._send_msg
- run_scenario.py
- HistorianTSDB
- EcsEvent
- HmiRequestHandler
- cmd_down
- HistorianAntiForensicsAttack
- traffic.py
- CityLab - Development Guidelines
- 🛡️ Arquitectura del Cyber Range CityLab (IEC 62443 / Co-Simulación Ciberfísica)
- HoneypotTouch
- ._conn
- NtpTimeSpoofingAttack
- KerberoastAttack
- OpcUaServer
- TestOpcUaNodeSpace
- Dnp3OutstationState
- InsiderRbacAttack
- citylab.sh
- Apagón Urbano en Cascada (Scenario #01, Avanzado)
- ModbusReadOnly
- Dnp3MasterClient
- test_scenario_manifest.py
- properties
- NtcipListener
- OtHoneypotServer
- 📌 1. Visión General del Módulo
- Inyección y Spoofing de Mensajes GOOSE IEC 61850 (Scenario #02, Avanzada)
- Ataque Low and Slow al Sistema SIS SIL-3 (Scenario #03, Avanzado)
- Replay Attack Modbus Tipo Stuxnet (Scenario #04, Intermedio)
- Conmutación y Failover en Cluster SCADA HA (Scenario #05, Intermedio)
- Kerberoasting y Abuso de Samba Active Directory (Scenario #06, Avanzado)
- Anti-Forense y Manipulación de Historian TSDB (Scenario #07, Avanzado)
- Abuso de Privilegios y Escalación RBAC en SCADA (Scenario #08, Intermedio)
- Dosificación Química en Planta de Tratamiento de Agua (Scenario #09, Avanzada)
- Atribución de Ola de Calor vs Ciberataque a la Red Eléctrica (Scenario #10, Avanzado)
- Spoofing de Tiempo NTP y Desincronización de Subestación (Scenario #11, Avanzado)
- Ransomware con Impacto en Infraestructura OT (Scenario #12, Avanzado)
- Escaneo Activo y Enumeración de PLCs OT (Scenario #14, Básico)
- Escritura de Bobina Individual Modbus (Single Coil Write) (Scenario #18, Intermedio)
- Cadena de Pivoteo Guiada Attacker -> DMZ -> OT (Scenario #19, Intermedio)
- Pérdida de Visibilidad (Loss of View) y Aislamiento Manual (Scenario #21, Intermedio)
- Métricas Purple Team: Medición y Optimización de MTTD (Scenario #22, Avanzado)
- properties
- 1. DIAGNÓSTICO Y ANÁLISIS DE CAUSA RAÍZ
- PostIncidentRecovery
- Plan Director de Evolución Alta Fidelidad y Gemelo Digital
- PurpleTeamMttd
- enum
- items
- run_modbus_attack
- BlindRandomizedEnv
- RansomwareTabletop
- RedVsBlueMatch
- Reconocimiento Pasivo en Red OT (Scenario #13, Básico)
- Lectura de Telemetría Modbus TCP sin Autenticación (Scenario #15, Básico)
- Interacción y Detección de Honeypot OT (Scenario #16, Básico)
- Exploración y Tour de la API HMI/SCADA (Scenario #17, Básico)
- Conmutación de Modo de Autenticación Estricta (STRICT_AUTH) (Scenario #20, Intermedio)
- 2. PLAN TÉCNICO DE REMEDIACIÓN REVISADO
- ConditionChecker
- run_phase1.sh
- run_phase2.sh
- run_phase3.sh
- CityLab - Product Overview
- required
- Development Workflow
- Prompt Auditor Principal de Ciberseguridad Industrial
- smoke_test_phase4.sh
- .read_node
- poc_modbus_test.py
- properties
- id
- Escenario 22: Medición de Métricas SOC Purple Team (MTTD / MTTR)
- Escenario 09: Dosificación Química de Cloro/NaOH
- Escenario 10: Atribución de Incidentes en Red Eléctrica (Ola de Calor + Sabotaje)
- Escenario 11: Ataque de Desincronización Horaria NTP/PTP
- Escenario 12: Ransomware IT con Parada Preventiva OT
- Escenario 13: Reconocimiento Pasivo y Sniffing de Redes OT
- Escenario 19: Cadena de Pivoteo Multi-Zona IEC 62443
- smoke_test_phase2.sh
- smoke_test_phase3.sh
- 🎨 Infraestructura 09 — Visualizador Urbano 2D SVG Airgapped y Puente de Telemetría (`fed_viz_bridge.py` & `viz_server.py`)
- Scenario 26 Manifest - Campaña APT Sandworm
- schema.json
- Plan de Remediación Técnica Sanitización Sentinels HELICS
- CityLab Runbook y Manual de Operaciones
- Escenario 14: Escaneo Activo Nmap y Verificación de Segmentación
- Escenario 15: Lectura de Memoria y Telemetría Modbus
- Escenario 16: Interacción con Señuelos Honeypot OT
- Escenario 17: API REST y Visualización HMI P&ID
- Escenario 18: Inyección y Forzado de Coil Modbus (Bomba de Agua)
- Escenario 20: Hardening Defensivo de SCADA API (STRICT_AUTH)
- Escenario 23: Defensa SDN Dinámica en Caliente con Open vSwitch
- Escenario 24: Evasión de Correlación SIEM mediante Ataque Distribuido Multi-IP
- Escenario 25: Ejercicio Tabletop de Gestión de Crisis por Ransomware
- Escenario 26 (Capstone): Emulación de Campaña APT Sandworm / ELECTRUM
- Escenario 27 (Capstone): Competencia Red vs Blue Arbitrada en Tiempo Real
- Escenario 28 (Capstone): Evaluación Ciega y Entorno Dinámico Anti-Memorización
- Escenario 29 (Capstone): Recuperación Post-Incidente y Reintegración Segura
- Scenario 23 Manifest - Defensa Dinámica SDN
- Scenario 24 Manifest - Evasión SIEM Multi-IP
- Scenario 27 Manifest - Live Fire Red vs Blue
- Entorno Ciego Anti-Memorización
- Recuperación ante Desastres (Disaster Recovery) Post-Incidente
- conftest.py
- Escenario 21: Respuesta a Pérdida de Visibilidad y Aislamiento Manual
- smoke_test_local.sh
- scada_server.py
- FLAG_1: Plan de Contingencia y Aislamiento de Activos
- Prompt Implementador Senior OT / Cyber Range
- Prompt QA Lead — Aseguramiento de Calidad de Tests
- Walkthrough Escenario 02: Inyección de Mensajes GOOSE IEC 61850
- Walkthrough Escenario 03: Evasión Sigilosa SIS Triton
- Ceguera Operativa en HMI y Base de Datos Historian
- Walkthrough Escenario 05: Explotación de Ventana de Conmutación SCADA HA
- Walkthrough Escenario 06: Kerberoasting y Escalado en Active Directory
- Borrado Anti-Forense de Base de Datos Historian
- Walkthrough Escenario 08: Insider Threat y Violación RBAC
- start_broker.sh
- install_deps.sh
- start_openplc.sh
- 🚦 Federado 03 — Sector Transporte y Tráfico Urbano (`fed_transport.py`)
- IEC61850DataSet
- TwoStageWaterPlant
- 📌 1. Visión General del Módulo
- EpanetHydraulicSolver
- SafetyInstrumentedLogic
- .decode
- ActuatorEmulator
- Especificación de Requisitos de Software (ERS)
- spoof_goose_trip
- sanitize_trip_signal
- SafetyInterlockLimits
- attack_apt_sandworm_campaign.py
- BacnetListener
- attack_grid_heatwave_attribution.py
- TestSisFederate
- ✅ REPORTE DE CIERRE DE AUDITORÍA — CityLab Cyber Range
- smoke_test_phase7.sh
- ModbusDpiProxyServer
- Dnp3Server
- Architecture — the big picture
- .test_loss_of_view_behavioral_polling_accumulation
- Enum

## God Nodes (most connected - your core abstractions)
1. `HistorianTSDB` - 68 edges
2. `SiemCorrelationEngine` - 47 edges
3. `running_modbus_server()` - 29 edges
4. `cmd_down()` - 27 edges
5. `OpcUaServer` - 27 edges
6. `IndustrialHmiEngine` - 26 edges
7. `SCADAPrimarySecondaryCluster` - 26 edges
8. `TwoStageWaterPlant` - 24 edges
9. `Iec61850Server` - 22 edges
10. `OpcUaClient` - 20 edges

## Surprising Connections (you probably didn't know these)
- `8. Fase 5 — Migración Masiva de Escenarios y Anti-Memorización` --references--> `BlindRandomizedEnv`  [EXTRACTED]
  docs/Roadmaps/PLAN_MEDICION_Y_CONTENCION.md → attacker/attack_blind_randomized_env.py
- `Build Systems and Development Tools` --references--> `execute_cascading_attack()`  [EXTRACTED]
  .amazonq/rules/memory-bank/tech.md → attacker/attack_multisector.py
- `2. Estructura del Proyecto y Módulos de Código` --references--> `cmd_down()`  [EXTRACTED]
  docs/ARCHITECTURE.md → citylab.sh
- `2. Descripción General` --references--> `cmd_down()`  [EXTRACTED]
  docs/ERS.md → citylab.sh
- `4. Requisitos No Funcionales (RNF)` --references--> `cmd_down()`  [EXTRACTED]
  docs/ERS.md → citylab.sh

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Scenario 01 Attack & Defense Workflow** — config_scenarios_scenario_01, config_scenarios_scenario_01_definition, config_scenarios_scenario_01_category_multi_sector_industrial_impact, config_scenarios_scenario_01_seed_unit_ids, config_scenarios_scenario_01_seed_flags, config_scenarios_scenario_01_flag_1, config_scenarios_scenario_01_flag_2, config_scenarios_scenario_01_flag_3, config_scenarios_scenario_01_flag_1_check_http_status, config_scenarios_scenario_01_flag_2_check_historian_condition, config_scenarios_scenario_01_flag_3_check_scada_sector_status [EXTRACTED 1.00]
- **Scenario 02 Attack & Defense Workflow** — config_scenarios_scenario_02, config_scenarios_scenario_02_definition, config_scenarios_scenario_02_category_industrial_cybersecurity, config_scenarios_scenario_02_seed_stnum_offsets, config_scenarios_scenario_02_seed_flags, config_scenarios_scenario_02_flag_1, config_scenarios_scenario_02_flag_2, config_scenarios_scenario_02_flag_1_check_http_status, config_scenarios_scenario_02_flag_2_check_siem_alert [EXTRACTED 1.00]
- **Scenario 03 Attack & Defense Workflow** — config_scenarios_scenario_03, config_scenarios_scenario_03_definition, config_scenarios_scenario_03_category_safety_instrumented_systems, config_scenarios_scenario_03_seed_delta_drift, config_scenarios_scenario_03_seed_flags, config_scenarios_scenario_03_flag_1, config_scenarios_scenario_03_flag_2, config_scenarios_scenario_03_flag_1_check_http_status, config_scenarios_scenario_03_flag_2_check_historian_condition [EXTRACTED 1.00]
- **Scenario 04 Attack & Defense Workflow** — config_scenarios_scenario_04, config_scenarios_scenario_04_definition, config_scenarios_scenario_04_category_industrial_protocol_exploitation, config_scenarios_scenario_04_seed_packet_hashes, config_scenarios_scenario_04_seed_flags, config_scenarios_scenario_04_flag_1, config_scenarios_scenario_04_flag_2, config_scenarios_scenario_04_flag_1_check_http_status, config_scenarios_scenario_04_flag_2_check_siem_alert [EXTRACTED 1.00]
- **Scenario 05 Attack & Defense Workflow** — config_scenarios_scenario_05, config_scenarios_scenario_05_definition, config_scenarios_scenario_05_category_high_availability, config_scenarios_scenario_05_seed_heartbeat_interval, config_scenarios_scenario_05_seed_flags, config_scenarios_scenario_05_flag_1, config_scenarios_scenario_05_flag_2, config_scenarios_scenario_05_flag_1_check_http_status, config_scenarios_scenario_05_flag_2_check_scada_sector_status [EXTRACTED 1.00]
- **Scenario 06 Attack & Defense Workflow** — config_scenarios_scenario_06, config_scenarios_scenario_06_definition, config_scenarios_scenario_06_category_identity_access_management, config_scenarios_scenario_06_seed_spn_accounts, config_scenarios_scenario_06_seed_flags, config_scenarios_scenario_06_flag_1, config_scenarios_scenario_06_flag_2, config_scenarios_scenario_06_flag_1_check_http_status, config_scenarios_scenario_06_flag_2_check_siem_alert [EXTRACTED 1.00]
- **Scenario 07 Attack & Defense Workflow** — config_scenarios_scenario_07, config_scenarios_scenario_07_definition, config_scenarios_scenario_07_category_industrial_forensics, config_scenarios_scenario_07_seed_sqlite_wal_salts, config_scenarios_scenario_07_seed_flags, config_scenarios_scenario_07_flag_1, config_scenarios_scenario_07_flag_2, config_scenarios_scenario_07_flag_1_check_http_status, config_scenarios_scenario_07_flag_2_check_historian_condition [EXTRACTED 1.00]
- **Scenario 08 Attack & Defense Workflow** — config_scenarios_scenario_08, config_scenarios_scenario_08_definition, config_scenarios_scenario_08_category_access_control, config_scenarios_scenario_08_seed_role_tokens, config_scenarios_scenario_08_seed_flags, config_scenarios_scenario_08_flag_1, config_scenarios_scenario_08_flag_2, config_scenarios_scenario_08_flag_1_check_http_status, config_scenarios_scenario_08_flag_2_check_siem_alert [EXTRACTED 1.00]
- **Scenario 09 Attack & Defense Workflow** — config_scenarios_scenario_09, config_scenarios_scenario_09_definition, config_scenarios_scenario_09_category_water_treatment_process, config_scenarios_scenario_09_seed_chemical_thresholds, config_scenarios_scenario_09_seed_flags, config_scenarios_scenario_09_flag_1, config_scenarios_scenario_09_flag_2, config_scenarios_scenario_09_flag_1_check_http_status, config_scenarios_scenario_09_flag_2_check_historian_condition [EXTRACTED 1.00]
- **Scenario 10 Attack & Defense Workflow** — config_scenarios_scenario_10, config_scenarios_scenario_10_definition, config_scenarios_scenario_10_category_incident_response, config_scenarios_scenario_10_seed_ambient_temp_profile, config_scenarios_scenario_10_seed_flags, config_scenarios_scenario_10_flag_1, config_scenarios_scenario_10_flag_2, config_scenarios_scenario_10_flag_1_check_http_status, config_scenarios_scenario_10_flag_2_check_siem_alert [EXTRACTED 1.00]
- **Scenario 11 Attack & Defense Workflow** — config_scenarios_scenario_11, config_scenarios_scenario_11_definition, config_scenarios_scenario_11_category_time_synchronization, config_scenarios_scenario_11_seed_ntp_offset, config_scenarios_scenario_11_seed_flags, config_scenarios_scenario_11_flag_1, config_scenarios_scenario_11_flag_2, config_scenarios_scenario_11_flag_1_check_http_status, config_scenarios_scenario_11_flag_2_check_siem_alert [EXTRACTED 1.00]
- **Scenario 12 Attack & Defense Workflow** — config_scenarios_scenario_12, config_scenarios_scenario_12_definition, config_scenarios_scenario_12_category_ransomware_emulation, config_scenarios_scenario_12_seed_encrypted_extensions, config_scenarios_scenario_12_seed_flags, config_scenarios_scenario_12_flag_1, config_scenarios_scenario_12_flag_2, config_scenarios_scenario_12_flag_1_check_http_status, config_scenarios_scenario_12_flag_2_check_openflow_rule [EXTRACTED 1.00]
- **Scenario 13 Attack & Defense Workflow** — config_scenarios_scenario_13, config_scenarios_scenario_13_definition, config_scenarios_scenario_13_category_network_reconnaissance, config_scenarios_scenario_13_seed_mac_prefixes, config_scenarios_scenario_13_seed_flags, config_scenarios_scenario_13_flag_1, config_scenarios_scenario_13_flag_1_check_http_status [EXTRACTED 1.00]
- **Scenario 14 Attack & Defense Workflow** — config_scenarios_scenario_14, config_scenarios_scenario_14_definition, config_scenarios_scenario_14_category_network_scanning, config_scenarios_scenario_14_seed_unit_id_ranges, config_scenarios_scenario_14_seed_flags, config_scenarios_scenario_14_flag_1, config_scenarios_scenario_14_flag_2, config_scenarios_scenario_14_flag_1_check_http_status, config_scenarios_scenario_14_flag_2_check_siem_alert [EXTRACTED 1.00]
- **Scenario 15 Attack & Defense Workflow** — config_scenarios_scenario_15, config_scenarios_scenario_15_definition, config_scenarios_scenario_15_category_industrial_protocols, config_scenarios_scenario_15_seed_register_offsets, config_scenarios_scenario_15_seed_flags, config_scenarios_scenario_15_flag_1, config_scenarios_scenario_15_flag_1_check_http_status [EXTRACTED 1.00]
- **Scenario 16 Attack & Defense Workflow** — config_scenarios_scenario_16, config_scenarios_scenario_16_definition, config_scenarios_scenario_16_category_deception_technology, config_scenarios_scenario_16_seed_honey_coils, config_scenarios_scenario_16_seed_flags, config_scenarios_scenario_16_flag_1, config_scenarios_scenario_16_flag_1_check_siem_alert [EXTRACTED 1.00]
- **Scenario 17 Attack & Defense Workflow** — config_scenarios_scenario_17, config_scenarios_scenario_17_definition, config_scenarios_scenario_17_category_scada_web_interface, config_scenarios_scenario_17_seed_endpoints, config_scenarios_scenario_17_seed_flags, config_scenarios_scenario_17_flag_1, config_scenarios_scenario_17_flag_1_check_http_status [EXTRACTED 1.00]
- **Scenario 18 Attack & Defense Workflow** — config_scenarios_scenario_18, config_scenarios_scenario_18_definition, config_scenarios_scenario_18_category_process_control_manipulation, config_scenarios_scenario_18_seed_coil_index, config_scenarios_scenario_18_seed_flags, config_scenarios_scenario_18_flag_1, config_scenarios_scenario_18_flag_2, config_scenarios_scenario_18_flag_1_check_http_status, config_scenarios_scenario_18_flag_2_check_historian_condition [EXTRACTED 1.00]
- **Scenario 19 Attack & Defense Workflow** — config_scenarios_scenario_19, config_scenarios_scenario_19_definition, config_scenarios_scenario_19_category_network_pivoting, config_scenarios_scenario_19_seed_pivoting_paths, config_scenarios_scenario_19_seed_flags, config_scenarios_scenario_19_flag_1, config_scenarios_scenario_19_flag_2, config_scenarios_scenario_19_flag_1_check_http_status, config_scenarios_scenario_19_flag_2_check_http_status [EXTRACTED 1.00]
- **Scenario 20 Attack & Defense Workflow** — config_scenarios_scenario_20, config_scenarios_scenario_20_definition, config_scenarios_scenario_20_category_security_hardening, config_scenarios_scenario_20_seed_strict_tokens, config_scenarios_scenario_20_seed_flags, config_scenarios_scenario_20_flag_1, config_scenarios_scenario_20_flag_1_check_http_status [EXTRACTED 1.00]
- **Scenario 21 Attack & Defense Workflow** — config_scenarios_scenario_21, config_scenarios_scenario_21_definition, config_scenarios_scenario_21_category_loss_of_view, config_scenarios_scenario_21_seed_timeout_thresholds, config_scenarios_scenario_21_seed_flags, config_scenarios_scenario_21_flag_1, config_scenarios_scenario_21_flag_2, config_scenarios_scenario_21_flag_1_check_scada_sector_status, config_scenarios_scenario_21_flag_2_check_openflow_rule [EXTRACTED 1.00]
- **Scenario 22 Attack & Defense Workflow** — config_scenarios_scenario_22, config_scenarios_scenario_22_definition, config_scenarios_scenario_22_category_purple_teaming, config_scenarios_scenario_22_seed_detection_windows, config_scenarios_scenario_22_seed_flags, config_scenarios_scenario_22_flag_1, config_scenarios_scenario_22_flag_2, config_scenarios_scenario_22_flag_1_check_http_status, config_scenarios_scenario_22_flag_2_check_siem_alert [EXTRACTED 1.00]
- **Scenario 23 SDN Circuit Breaker Defense** — config_scenarios_scenario_23_manifest, config_scenarios_scenario_23_sdn_defense_breaker, config_scenarios_scenario_23_flag_1_breaker, config_scenarios_scenario_23_flag_2_openflow_drop [EXTRACTED 1.00]
- **Scenario 26 Sandworm APT Emulation Structure** — config_scenarios_scenario_26_manifest, config_scenarios_scenario_26_sandworm_apt_campaign, config_scenarios_scenario_26_flag_1_ad_compromise, config_scenarios_scenario_26_flag_2_substation_trip, config_scenarios_scenario_26_flag_3_antiforensics_siem [EXTRACTED 1.00]
- **Digital Twin High Fidelity Evolution Phases** — docs_audits_plan_alta_fidelidad_digital_twin_doc, docs_audits_plan_alta_fidelidad_digital_twin_phase_1_iec61131, docs_audits_plan_alta_fidelidad_digital_twin_phase_2_ad_samba4, docs_audits_plan_alta_fidelidad_digital_twin_phase_3_nonlinear_physics [EXTRACTED 1.00]
- **HELICS Sentinel Remediation Execution Flow** — docs_audits_plan_remediacion_helics_sentinel_doc, docs_audits_plan_remediacion_helics_sentinel_hallazgo_sentinel, docs_audits_plan_remediacion_helics_sentinel_sanitization_spec, docs_audits_plan_remediacion_helics_sentinel_logging_alignment, docs_audits_plan_remediacion_helics_sentinel_unit_tests [EXTRACTED 1.00]
- **CityLab Operations Lifecycle & Verification Ecosystem** — docs_operations_runbook_doc, docs_operations_citylab_sh, docs_operations_endpoints_matrix, docs_operations_test_validation_suites, docs_operations_ctf_evaluation [EXTRACTED 1.00]
- **CityLab Audit, Implementation and QA Governance Prompts** — docs_roadmaps_prompt_auditor_doc, docs_roadmaps_prompt_auditor_spanish_doc, docs_roadmaps_prompt_qa_doc, docs_roadmaps_prompt_implementador_doc [INFERRED 0.85]
- **Scenario 01 Cascading Blackout Walkthrough Structure** — docs_scenarios_scenario_01_cascading_blackout_doc, docs_scenarios_scenario_01_cascading_blackout_attack_chain, docs_scenarios_scenario_01_cascading_blackout_hospital_failover [EXTRACTED 1.00]
- **Scenario 02 GOOSE Spoofing & Detection Structure** — docs_scenarios_scenario_02_goose_spoofing_doc, docs_scenarios_scenario_02_goose_spoofing_industroyer2_pattern, docs_scenarios_scenario_02_goose_spoofing_siem_detection [EXTRACTED 1.00]
- **Scenario Package: Escenario 09: Dosificación Química de Cloro/NaOH** — docs_scenarios_scenario_09_chemical_dosing_doc, docs_scenarios_scenario_09_chemical_dosing_chemical_dosing_scenario, docs_scenarios_scenario_09_chemical_dosing_swat_oldsmar_pattern, docs_scenarios_scenario_09_chemical_dosing_chemical_dosing_controller, docs_scenarios_scenario_09_chemical_dosing_independent_water_analyzers, docs_scenarios_scenario_09_chemical_dosing_attack_script_chemical_dosing [EXTRACTED 1.00]
- **Scenario Package: Escenario 10: Atribución de Incidentes en Red Eléctrica (Ola de Calor + Sabotaje)** — docs_scenarios_scenario_10_grid_heatwave_attribution_doc, docs_scenarios_scenario_10_grid_heatwave_attribution_grid_heatwave_attribution_scenario, docs_scenarios_scenario_10_grid_heatwave_attribution_incident_attribution_rca, docs_scenarios_scenario_10_grid_heatwave_attribution_substation_main_breaker, docs_scenarios_scenario_10_grid_heatwave_attribution_thermal_overload_vs_cyber_sabotage, docs_scenarios_scenario_10_grid_heatwave_attribution_attack_script_grid_heatwave [EXTRACTED 1.00]
- **Scenario Package: Escenario 11: Ataque de Desincronización Horaria NTP/PTP** — docs_scenarios_scenario_11_ntp_time_spoofing_doc, docs_scenarios_scenario_11_ntp_time_spoofing_ntp_time_spoofing_scenario, docs_scenarios_scenario_11_ntp_time_spoofing_ntp_ptp_time_sync, docs_scenarios_scenario_11_ntp_time_spoofing_time_skewing_siem_blinding, docs_scenarios_scenario_11_ntp_time_spoofing_iec61850_sv_historian_integrity, docs_scenarios_scenario_11_ntp_time_spoofing_attack_script_ntp_spoofing [EXTRACTED 1.00]
- **Scenario Package: Escenario 12: Ransomware IT con Parada Preventiva OT** — docs_scenarios_scenario_12_ransomware_ot_impact_doc, docs_scenarios_scenario_12_ransomware_ot_impact_ransomware_ot_impact_scenario, docs_scenarios_scenario_12_ransomware_ot_impact_colonial_pipeline_pattern, docs_scenarios_scenario_12_ransomware_ot_impact_it_ot_precautionary_shutdown, docs_scenarios_scenario_12_ransomware_ot_impact_it_billing_and_ot_pumping_boundary, docs_scenarios_scenario_12_ransomware_ot_impact_attack_script_ransomware_ot [EXTRACTED 1.00]
- **Scenario Package: Escenario 13: Reconocimiento Pasivo y Sniffing de Redes OT** — docs_scenarios_scenario_13_ot_passive_recon_doc, docs_scenarios_scenario_13_ot_passive_recon_ot_passive_recon_scenario, docs_scenarios_scenario_13_ot_passive_recon_passive_network_sniffing, docs_scenarios_scenario_13_ot_passive_recon_unencrypted_ot_protocols, docs_scenarios_scenario_13_ot_passive_recon_ot_cell_switches_sniff, docs_scenarios_scenario_13_ot_passive_recon_attack_script_passive_recon [EXTRACTED 1.00]
- **Scenario Package: Escenario 14: Escaneo Activo Nmap y Verificación de Segmentación** — docs_scenarios_scenario_14_ot_active_scanning_doc, docs_scenarios_scenario_14_ot_active_scanning_ot_active_scanning_scenario, docs_scenarios_scenario_14_ot_active_scanning_nmap_segmentation_audit, docs_scenarios_scenario_14_ot_active_scanning_dmz_firewall_policies_audit, docs_scenarios_scenario_14_ot_active_scanning_attack_script_active_scan [EXTRACTED 1.00]
- **Scenario Package: Escenario 15: Lectura de Memoria y Telemetría Modbus** — docs_scenarios_scenario_15_modbus_read_telemetry_doc, docs_scenarios_scenario_15_modbus_read_telemetry_modbus_read_telemetry_scenario, docs_scenarios_scenario_15_modbus_read_telemetry_unauthenticated_modbus_read, docs_scenarios_scenario_15_modbus_read_telemetry_water_plc_memory_map, docs_scenarios_scenario_15_modbus_read_telemetry_attack_script_modbus_read [EXTRACTED 1.00]
- **Scenario Package: Escenario 16: Interacción con Señuelos Honeypot OT** — docs_scenarios_scenario_16_honeypot_interaction_doc, docs_scenarios_scenario_16_honeypot_interaction_honeypot_interaction_scenario, docs_scenarios_scenario_16_honeypot_interaction_ics_deception_technology, docs_scenarios_scenario_16_honeypot_interaction_decoy_honeypot_service, docs_scenarios_scenario_16_honeypot_interaction_attack_script_honeypot_touch [EXTRACTED 1.00]
- **Scenario Package: Escenario 17: API REST y Visualización HMI P&ID** — docs_scenarios_scenario_17_scada_tour_api_doc, docs_scenarios_scenario_17_scada_tour_api_scada_tour_api_scenario, docs_scenarios_scenario_17_scada_tour_api_web_based_scada_architecture, docs_scenarios_scenario_17_scada_tour_api_hmi_pid_web_server, docs_scenarios_scenario_17_scada_tour_api_attack_script_scada_tour [EXTRACTED 1.00]
- **Scenario Package: Escenario 18: Inyección y Forzado de Coil Modbus (Bomba de Agua)** — docs_scenarios_scenario_18_modbus_single_coil_write_doc, docs_scenarios_scenario_18_modbus_single_coil_write_modbus_single_coil_write_scenario, docs_scenarios_scenario_18_modbus_single_coil_write_modbus_control_injection, docs_scenarios_scenario_18_modbus_single_coil_write_water_plc_pump_coil_actuator, docs_scenarios_scenario_18_modbus_single_coil_write_exploit_modbus_utility [EXTRACTED 1.00]
- **Scenario Package: Escenario 19: Cadena de Pivoteo Multi-Zona IEC 62443** — docs_scenarios_scenario_19_guided_pivoting_chain_doc, docs_scenarios_scenario_19_guided_pivoting_chain_guided_pivoting_chain_scenario, docs_scenarios_scenario_19_guided_pivoting_chain_iec62443_zone_pivoting, docs_scenarios_scenario_19_guided_pivoting_chain_dmz_bastion_ot_routing, docs_scenarios_scenario_19_guided_pivoting_chain_spi_firewall_proxy_defense, docs_scenarios_scenario_19_guided_pivoting_chain_attack_script_multisector [EXTRACTED 1.00]
- **Scenario Package: Escenario 20: Hardening Defensivo de SCADA API (STRICT_AUTH)** — docs_scenarios_scenario_20_strict_auth_toggle_doc, docs_scenarios_scenario_20_strict_auth_toggle_strict_auth_toggle_scenario, docs_scenarios_scenario_20_strict_auth_toggle_rbac_token_hardening, docs_scenarios_scenario_20_strict_auth_toggle_rbac_module_resolver, docs_scenarios_scenario_20_strict_auth_toggle_strict_auth_modes [EXTRACTED 1.00]
- **Scenario Package: Escenario 21: Respuesta a Pérdida de Visibilidad y Aislamiento Manual** — docs_scenarios_scenario_21_loss_of_view_manual_isolation_doc, docs_scenarios_scenario_21_loss_of_view_manual_isolation_loss_of_view_manual_isolation_scenario, docs_scenarios_scenario_21_loss_of_view_manual_isolation_loss_of_view_incident_response, docs_scenarios_scenario_21_loss_of_view_manual_isolation_scada_watchdog_switch_port_isolation [EXTRACTED 1.00]
- **Scenario Package: Escenario 22: Medición de Métricas SOC Purple Team (MTTD / MTTR)** — docs_scenarios_scenario_22_purple_team_metrics_mttd_doc, docs_scenarios_scenario_22_purple_team_metrics_mttd_purple_team_metrics_mttd_scenario, docs_scenarios_scenario_22_purple_team_metrics_mttd_nist_sp_800_61_metrics, docs_scenarios_scenario_22_purple_team_metrics_mttd_substation_goose_siem_injection, docs_scenarios_scenario_22_purple_team_metrics_mttd_attack_script_purple_team_mttd [EXTRACTED 1.00]
- **Scenario Package: Escenario 23: Defensa SDN Dinámica en Caliente con Open vSwitch** — docs_scenarios_scenario_23_live_sdn_defense_under_fire_doc, docs_scenarios_scenario_23_live_sdn_defense_under_fire_live_sdn_defense_scenario, docs_scenarios_scenario_23_live_sdn_defense_under_fire_safety_vs_availability_tradeoff, docs_scenarios_scenario_23_live_sdn_defense_under_fire_ovs_dynamic_openflow_mitigation, docs_scenarios_scenario_23_live_sdn_defense_under_fire_attack_script_live_sdn_defense [EXTRACTED 1.00]
- **Scenario Package: Escenario 24: Evasión de Correlación SIEM mediante Ataque Distribuido Multi-IP** — docs_scenarios_scenario_24_siem_rule_evasion_multi_ip_doc, docs_scenarios_scenario_24_siem_rule_evasion_multi_ip_siem_rule_evasion_scenario, docs_scenarios_scenario_24_siem_rule_evasion_multi_ip_static_rule_evasion_behavioral_analytics, docs_scenarios_scenario_24_siem_rule_evasion_multi_ip_siem_pipeline_engine, docs_scenarios_scenario_24_siem_rule_evasion_multi_ip_attack_script_siem_evasion [EXTRACTED 1.00]
- **Scenario Package: Escenario 25: Ejercicio Tabletop de Gestión de Crisis por Ransomware** — docs_scenarios_scenario_25_ransomware_tabletop_exercise_doc, docs_scenarios_scenario_25_ransomware_tabletop_exercise_ransomware_tabletop_scenario, docs_scenarios_scenario_25_ransomware_tabletop_exercise_executive_crisis_management, docs_scenarios_scenario_25_ransomware_tabletop_exercise_csuite_decision_roles, docs_scenarios_scenario_25_ransomware_tabletop_exercise_attack_script_ransomware_tabletop [EXTRACTED 1.00]
- **Scenario Package: Escenario 26 (Capstone): Emulación de Campaña APT Sandworm / ELECTRUM** — docs_scenarios_scenario_26_apt_campaign_sandworm_emulation_doc, docs_scenarios_scenario_26_apt_campaign_sandworm_emulation_apt_sandworm_campaign_scenario, docs_scenarios_scenario_26_apt_campaign_sandworm_emulation_sandworm_electrum_pattern, docs_scenarios_scenario_26_apt_campaign_sandworm_emulation_multistage_ot_campaign_orchestration, docs_scenarios_scenario_26_apt_campaign_sandworm_emulation_attack_script_apt_sandworm [EXTRACTED 1.00]
- **Scenario Package: Escenario 27 (Capstone): Competencia Red vs Blue Arbitrada en Tiempo Real** — docs_scenarios_scenario_27_red_vs_blue_adjudicated_match_doc, docs_scenarios_scenario_27_red_vs_blue_adjudicated_match_red_vs_blue_match_scenario, docs_scenarios_scenario_27_red_vs_blue_adjudicated_match_live_scoring_arbitration_engine, docs_scenarios_scenario_27_red_vs_blue_adjudicated_match_simultaneous_red_blue_operations, docs_scenarios_scenario_27_red_vs_blue_adjudicated_match_attack_script_red_vs_blue_match [EXTRACTED 1.00]
- **Scenario Package: Escenario 28 (Capstone): Evaluación Ciega y Entorno Dinámico Anti-Memorización** — docs_scenarios_scenario_28_blind_anti_memorization_environment_doc, docs_scenarios_scenario_28_blind_anti_memorization_environment_blind_anti_memorization_scenario, docs_scenarios_scenario_28_blind_anti_memorization_environment_methodological_ttp_assessment, docs_scenarios_scenario_28_blind_anti_memorization_environment_dynamic_env_randomization, docs_scenarios_scenario_28_blind_anti_memorization_environment_attack_script_blind_randomized [EXTRACTED 1.00]
- **Scenario Package: Escenario 29 (Capstone): Recuperación Post-Incidente y Reintegración Segura** — docs_scenarios_scenario_29_post_incident_disaster_recovery_doc, docs_scenarios_scenario_29_post_incident_disaster_recovery_post_incident_disaster_recovery_scenario, docs_scenarios_scenario_29_post_incident_disaster_recovery_digital_trust_operational_resilience, docs_scenarios_scenario_29_post_incident_disaster_recovery_plc_firmware_historian_rebuild, docs_scenarios_scenario_29_post_incident_disaster_recovery_attack_script_post_incident_recovery [EXTRACTED 1.00]
- **CityLab Industrial CTF Scenarios (09-29)** — docs_scenarios_scenario_09_chemical_dosing_chemical_dosing_scenario, docs_scenarios_scenario_10_grid_heatwave_attribution_grid_heatwave_attribution_scenario, docs_scenarios_scenario_11_ntp_time_spoofing_ntp_time_spoofing_scenario, docs_scenarios_scenario_12_ransomware_ot_impact_ransomware_ot_impact_scenario, docs_scenarios_scenario_13_ot_passive_recon_ot_passive_recon_scenario, docs_scenarios_scenario_14_ot_active_scanning_ot_active_scanning_scenario, docs_scenarios_scenario_15_modbus_read_telemetry_modbus_read_telemetry_scenario, docs_scenarios_scenario_16_honeypot_interaction_honeypot_interaction_scenario, docs_scenarios_scenario_17_scada_tour_api_scada_tour_api_scenario, docs_scenarios_scenario_18_modbus_single_coil_write_modbus_single_coil_write_scenario, docs_scenarios_scenario_19_guided_pivoting_chain_guided_pivoting_chain_scenario, docs_scenarios_scenario_20_strict_auth_toggle_strict_auth_toggle_scenario, docs_scenarios_scenario_21_loss_of_view_manual_isolation_loss_of_view_manual_isolation_scenario, docs_scenarios_scenario_22_purple_team_metrics_mttd_purple_team_metrics_mttd_scenario, docs_scenarios_scenario_23_live_sdn_defense_under_fire_live_sdn_defense_scenario, docs_scenarios_scenario_24_siem_rule_evasion_multi_ip_siem_rule_evasion_scenario, docs_scenarios_scenario_25_ransomware_tabletop_exercise_ransomware_tabletop_scenario, docs_scenarios_scenario_26_apt_campaign_sandworm_emulation_apt_sandworm_campaign_scenario, docs_scenarios_scenario_27_red_vs_blue_adjudicated_match_red_vs_blue_match_scenario, docs_scenarios_scenario_28_blind_anti_memorization_environment_blind_anti_memorization_scenario, docs_scenarios_scenario_29_post_incident_disaster_recovery_post_incident_disaster_recovery_scenario [EXTRACTED 1.00]
- **Water Sector & Modbus Exploitation Scenarios** — docs_scenarios_scenario_09_chemical_dosing_chemical_dosing_scenario, docs_scenarios_scenario_15_modbus_read_telemetry_modbus_read_telemetry_scenario, docs_scenarios_scenario_18_modbus_single_coil_write_modbus_single_coil_write_scenario [INFERRED 0.85]
- **OT Network Reconnaissance & Deception Scenarios** — docs_scenarios_scenario_13_ot_passive_recon_ot_passive_recon_scenario, docs_scenarios_scenario_14_ot_active_scanning_ot_active_scanning_scenario, docs_scenarios_scenario_16_honeypot_interaction_honeypot_interaction_scenario [INFERRED 0.85]
- **Purple Team Metrics & Dynamic SDN Defense Scenarios** — docs_scenarios_scenario_21_loss_of_view_manual_isolation_loss_of_view_manual_isolation_scenario, docs_scenarios_scenario_22_purple_team_metrics_mttd_purple_team_metrics_mttd_scenario, docs_scenarios_scenario_23_live_sdn_defense_under_fire_live_sdn_defense_scenario, docs_scenarios_scenario_24_siem_rule_evasion_multi_ip_siem_rule_evasion_scenario [INFERRED 0.85]
- **Capstone Advanced Adversary Emulation & Recovery Scenarios** — docs_scenarios_scenario_26_apt_campaign_sandworm_emulation_apt_sandworm_campaign_scenario, docs_scenarios_scenario_27_red_vs_blue_adjudicated_match_red_vs_blue_match_scenario, docs_scenarios_scenario_28_blind_anti_memorization_environment_blind_anti_memorization_scenario, docs_scenarios_scenario_29_post_incident_disaster_recovery_post_incident_disaster_recovery_scenario [INFERRED 0.85]

## Communities (190 total, 8 thin omitted)

### Community 0 - "Iec61850Server"
Cohesion: 0.20
Nodes (7): Iec61850Server, Iec61850SvEncoder, is_multicast_addr(), main(), Codificador/Decodificador binario para Sampled Values (SV)., Servidor IED Subestación IEC 61850 con emisión GOOSE & SV y recepción de…, TestIEC61850Emulator

### Community 1 - "test_flag_service.py"
Cohesion: 0.08
Nodes (28): FlagServiceHandler, generate_flag_hmac(), load_scenario_manifest(), BaseHTTPRequestHandler, HTTPServer, ThreadingMixIn, RateLimiter, Carga y parsea el archivo YAML del manifiesto de escenario. (+20 more)

### Community 2 - "ChemicalDosingAttack"
Cohesion: 0.21
Nodes (9): ChemicalDosingAttack, main(), Any, Vector de ataque de sobre-dosificación química sobre PLC de agua., Ejecuta el ataque escribiendo en el Holding Register Modbus/TCP y confirmando…, Ataque real vía Modbus/TCP muta el Holding Register 10 en el PLC y confirma…, Dosificación dentro de rango seguro muta el registro pero no marca…, Si el PLC no está disponible, el ataque activa el modo TABLETOP_FALLBACK… (+1 more)

### Community 3 - "run_ovs_cmd"
Cohesion: 0.12
Nodes (19): LiveSdnDefense, main(), Any, patch, TestScenario23Sdn, 7. Pipeline de Seguridad: SIEM Central y Defensa Dinámica SDN, 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Reenvío Asíncrono y Detección SIEM (+11 more)

### Community 4 - "SmartLightingSystem"
Cohesion: 0.08
Nodes (15): main(), main(), Any, Lee el coil de apagón del PLC de alumbrado. False si no hay PLC o falla la…, read_blackout_command(), TestPhase4Federates, Any, Modelo físico determinista de Red de Alumbrado Público Inteligente. (+7 more)

### Community 5 - "ModbusDpiEngine"
Cohesion: 0.16
Nodes (6): ModbusDpiEngine, RateLimiter, Controlador de tasa de escrituras por IP de origen., Motor de Inspección Profunda de Paquetes (DPI) Modbus/TCP., Inspecciona la trama Modbus/TCP en Capa 7. Header Modbus TCP (MBAP): -…, TestDpiProxyAndScadaWatchdog

### Community 6 - "ElectricalSubstationGrid"
Cohesion: 0.06
Nodes (29): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Código y Máquina de Estados de Energía, 🧮 3. Modelo Físico de Descarga de Baterías y Generador, 🗺️ 4. Mapa de Registros Modbus TCP (PLC Hospital `10.0.3.15:502`), 📡 5. Interfaz HELICS Pub-Sub, 💾 6. Presupuesto de Recursos y Memoria RAM, 🏥 Federado 04 — Sector Hospital Carga Crítica y Sistema ATS/UPS (`fed_hospital.p, Enum (+21 more)

### Community 7 - "modbus_emulator.py"
Cohesion: 0.28
Nodes (5): ModbusTcpServer, build_server(), main(), Construye las instancias del emulador Modbus sin iniciar el bucle bloqueante., run_server()

### Community 8 - "SCADAPrimarySecondaryCluster"
Cohesion: 0.10
Nodes (13): FailoverExploitAttack, main(), Any, Verifica que la ausencia de heartbeat fuerce la conmutación a PRIMARY., Verifica ejecución CLI., TestFailoverAttack, Any, Administrador de cluster de Alta Disponibilidad SCADA. (+5 more)

### Community 9 - "📌 1. Visión General del Módulo"
Cohesion: 0.06
Nodes (31): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Código y Flujo de Trabajo, 🧮 3. Modelo Físico e Inercia de Red, 🗺️ 4. Mapa de Protocolos (DNP3 SA `10.0.3.13` & IEC 61850 GOOSE `10.0.3.20`), 📡 5. Interfaz HELICS Pub-Sub, 💾 6. Presupuesto de Recursos y Memoria RAM, ⚡ Federado 02 — Sector Eléctrico y Subestación (GridLab-D & IEC 61850 / DNP3 SA), create_federate() (+23 more)

### Community 10 - "BacnetAttacker"
Cohesion: 0.10
Nodes (18): BacnetAttacker, main(), Any, Emulador de ataque BACnet/IP sobre UDP 47808., main(), NtcipAttacker, Any, Emulador de ataque NTCIP 1202 sobre TCP 161. (+10 more)

### Community 11 - "TestRBACResolver"
Cohesion: 0.07
Nodes (15): Bearer auditor:<operator_token> → 403 (rol incorrecto para token)., Rol auditor puede leer telemetría pero no /api/control/write., Rol operator puede acceder a /api/control/read pero no /api/control/write., Rol engineer tiene acceso completo (wildcard)., Rol None (no autenticado) → siempre False., reload() recarga almacén de tokens con cambios de env var., Tests unitarios del RBACResolver (network/rbac.py)., Bearer <token> plano → rol operator en STRICT_AUTH=0 (modo CTF). (+7 more)

### Community 12 - "CityVisualizerStateEngine"
Cohesion: 0.05
Nodes (36): create_helics_subscriptions(), format_bearer_header(), main(), poll_scada_once(), Any, Mapea telemetría SCADA REST (/api/telemetry) a esquemas del visualizador., Despacha estado acumulado a VIZ_URL respetando throttling 1 Hz., Consulta /api/telemetry de SCADA Server con cabecera Authorization: Bearer. (+28 more)

### Community 13 - "IndustrialHmiEngine"
Cohesion: 0.09
Nodes (18): main(), Any, Explora la API REST y estado HMI SCADA vía HTTP o motor directo., ScadaTour, Verifica la exploración directa sobre el motor HMI., Verifica la consulta HTTP contra el servidor HMI real en puerto alto., Verifica la invocación CLI., TestScadaTour (+10 more)

### Community 14 - "Dnp3BreakerAttack"
Cohesion: 0.09
Nodes (21): Dnp3BreakerAttack, main(), Any, Emulador de ataque DNP3 CROB sobre TCP 20000., main(), OtActiveScan, Any, Escáner activo de servicios y puertos OT. (+13 more)

### Community 15 - "3. Requisitos Funcionales Específicos"
Cohesion: 0.13
Nodes (17): 1. Introducción, 3. Requisitos Funcionales Específicos, 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Lógica Indesconectable SIL-3, 🧮 3. Envolvente de Seguridad Física (Safety Limits), 📡 4. Interfaz HELICS Pub-Sub, 💾 5. Presupuesto de Recursos y Memoria RAM, 🛡️ Federado 05 — Sistema de Seguridad SIS / ESD (SIL-3) (`fed_sis.py`) (+9 more)

### Community 16 - "profile_resources.py"
Cohesion: 0.16
Nodes (19): resource.getrusage debe devolver un RSS positivo real, no una estimación fija., El muestreo real no debe clasificar procesos ajenos al laboratorio., TestProfileResources, classify(), collect_sample(), _iter_processes_proc(), _iter_processes_psutil(), main() (+11 more)

### Community 17 - "execute_cascading_attack"
Cohesion: 0.16
Nodes (11): execute_cascading_attack(), force_coil(), main(), Any, Ejecuta ataque multi-sectorial cascada vía sockets Modbus reales o fallback., read_plc_state(), Verifica que el ataque multi-sectorial ejecute writes reales vía Modbus/TCP., Verifica que si ningún objetivo está disponible caiga en TABLETOP_FALLBACK. (+3 more)

### Community 18 - "TestOpcUaServerClient"
Cohesion: 0.10
Nodes (13): El servidor responde ACK al HEL correctamente (UA/TCP handshake)., Lectura de nodo Float (WaterTank_Level, NodeId=1001) retorna valor numérico., Lectura de nodo Boolean (WaterPump_State, NodeId=1002)., Lectura de nodo Int32 (Traffic_Light_State, NodeId=4001)., Lectura de NodeId desconocido retorna None (BadNodeIdUnknown)., Escritura directa al NodeSpace y lectura confirmada vía cliente., Browse retorna lista con conteo correcto de nodos., GetEndpoints responde con 200 de servicio (SecurityMode=None). (+5 more)

### Community 19 - "SiemCorrelationEngine"
Cohesion: 0.11
Nodes (13): main(), Any, SiemRuleEvasion, Verifica que el ataque distribuido multi-IP evada el umbral de disparo del SIEM., Prueba negativa / anti-trampa: ráfaga de eventos desde una sola IP sí activa…, Verifica la ejecución CLI., TestScenario24SiemEvasion, Exporta buffer de eventos en formato JSON compatible con Logstash /… (+5 more)

### Community 20 - "exploit_modbus.py"
Cohesion: 0.17
Nodes (23): action_fault(), action_sabotage(), action_start(), action_status(), action_stop(), main(), print_status(), ModbusTcpClient (+15 more)

### Community 21 - "ScoreboardEngine"
Cohesion: 0.13
Nodes (18): main(), parse_iso_or_epoch(), Any, Genera un reporte completo de Scorecard y métricas SOC., Convierte un timestamp (ISO 8601 string o epoch float) a segundos epoch float., Métricas SOC calculadas., Motor de análisis de eventos SIEM y cálculo de scorecard de ciberdefensa., Recupera los eventos ECS del buffer del SIEM central. (+10 more)

### Community 22 - "topology.py"
Cohesion: 0.13
Nodes (21): CLI, Mininet, apply_egress_containment(), apply_fw_configuration(), cleanup_egress_containment(), configure_host_routes(), CustomCLI, Iec62443Topo (+13 more)

### Community 23 - "siem_pipeline.py"
Cohesion: 0.14
Nodes (7): main(), HTTPServer, ThreadingMixIn, ThreadedSiemServer, Verifica que la Regla 2 (Industroyer2 GOOSE Spoofing) active alerta crítica., Verifica que el daemon central SIEM reciba eventos de honeypot y proxy,…, TestSiemPipeline

### Community 24 - "running_modbus_server"
Cohesion: 0.10
Nodes (13): El entrypoint CLI main() ejecuta la sobre-dosificación contra el puerto de test…, Verifica ejecución de la CLI., El entrypoint CLI main() ejecuta el vector replay contra el puerto de test sin…, El entrypoint CLI main() ejecuta la manipulación Triton sobre el puerto de test…, Verifica que el ataque force_start active Coil 0 en el datastore del emulador., Verifica que el ataque force_stop active Coil 1 en el datastore del emulador., Verifica que el ataque fault active START y STOP vía socket real., Verifica que ante un host no disponible el ataque caiga en TABLETOP_FALLBACK. (+5 more)

### Community 25 - "TritonLowSlowAttack"
Cohesion: 0.23
Nodes (8): main(), Any, Ataque de manipulación progresiva con evasión de disparo de interlocks SIS., TritonLowSlowAttack, Verifica manipulación de proceso vía Modbus manteniendo valores bajo umbral SIS…, Manipulación sobre el umbral de seguridad provoca disparo inmediato del SIS…, Si el PLC no está activo, el ataque activa el modo TABLETOP_FALLBACK…, TestTritonAttack

### Community 26 - "SCADAAPIHandler"
Cohesion: 0.13
Nodes (8): BaseHTTPRequestHandler, SCADAAPIHandler, Rol operator autenticado válidamente no tiene permiso para escribir control ->…, Rol engineer autenticado tiene permiso para control/write -> 200 y confirmación., Endpoint /api/whoami confirma identidad y bandera strict_auth., Petición POST a /api/control/write sin header Authorization debe retornar 401., En STRICT_AUTH=1, un token legado plano sin prefijo de rol debe ser rechazado…, TestScadaHttpStrictIntegration

### Community 27 - "RBACResolver"
Cohesion: 0.14
Nodes (12): TestScenario20StrictAuth, _load_env_file(), _load_token_store(), Intenta autenticar contra el AD LDAP emulado de h_dc (`ad_dc_emulator.py`).…, Resuelve el rol de una petición HTTP a partir de su cabecera Authorization.…, Recarga el almacén de tokens (útil tras rotación de credenciales)., Resuelve el rol asociado a una cabecera Authorization. Args: auth_header: Valor…, Verifica si el rol tiene permiso para acceder al endpoint. Args: role: Rol… (+4 more)

### Community 28 - "TestScadaHistorianHTTPEndpoints"
Cohesion: 0.16
Nodes (8): Tests de integración HTTP para los endpoints /api/history del SCADA Server., Arrancar un servidor HTTP de test con el handler real del SCADA., Helper: realiza GET con Bearer token y retorna (status_code, json_body)., GET /api/history?sector=water retorna filas históricas del sector., GET /api/history?sector=water&field=pressure filtra por campo., GET /api/history sin sector retorna 400., GET /api/history/snapshot?sector=water retorna snapshots del sector., TestScadaHistorianHTTPEndpoints

### Community 29 - "TestHistorianTSDB"
Cohesion: 0.10
Nodes (10): prune() elimina puntos más antiguos manteniendo los más recientes., query() con parámetro `since` filtra por timestamp correctamente., Tests unitarios del módulo historian.py (HistorianTSDB)., write() persiste puntos individuales y query() los recupera correctamente., write_snapshot() persiste el estado completo y query_snapshots() lo recupera., last() devuelve el snapshot más reciente de un sector., last() devuelve None cuando el sector no tiene datos., sectors() lista exactamente los sectores con datos registrados. (+2 more)

### Community 30 - "._recv_msg"
Cohesion: 0.29
Nodes (3): Escribe un valor numérico a un nodo OPC UA sobre la red., Consulta los endpoints disponibles (GetEndpoints)., Recibe un mensaje UA/TCP. Retorna (tipo, body) o None.

### Community 31 - "_emulator_harness.py"
Cohesion: 0.11
Nodes (15): DomainControllerEmulator, KerberosServerThread, LdapServerThread, main(), socket, Escuchador SMB v2/v3 en puerto 445., Orquestador completo del controlador de dominio h_dc., Escuchador LDAP en puerto 389. (+7 more)

### Community 32 - "🏗️ PLAN DE IMPLEMENTACIÓN TÉCNICA: VISUALIZADOR URBANO 2D (FASE 9)"
Cohesion: 0.10
Nodes (20): 1.1 Contexto y Oportunidad Arquitectónica, 1.2 Diagnóstico de Brecha (Gap Real), 1. RESUMEN EJECUTIVO Y DIAGNÓSTICO, 2. LAS 4 ENMIENDAS TÉCNICAS AUDITADAS Y APROBADAS, 3.1 Componente: Puente de Telemetría (`helics_sim/fed_viz_bridge.py`), 3.2 Componente: Suite de Pruebas Unitarias (`helics_sim/tests/test_fed_viz_bridge.py`), 3.3 Componente: Servidor Visualizador y UI 2D (`network/viz_server.py`), 3.4 Componente: Supervisión de Procesos y Teardown Limpio (+12 more)

### Community 33 - "TestScadaRBACHTTPEndpoints"
Cohesion: 0.14
Nodes (9): Tests de integración HTTP para RBAC en scada_server., /health responde 200 sin Authorization., /api/telemetry con token válido → 200., /api/telemetry sin token → 401., /api/whoami retorna el rol del token presentado., /api/whoami con token legado → rol operator (modo CTF)., STRICT_AUTH=1 rechaza token plano legado con 403., Auditor recibe 403 en /api/control/write. (+1 more)

### Community 34 - "._send_msg"
Cohesion: 0.12
Nodes (13): socket, Maneja una conexión de cliente OPC UA., Lee exactamente n bytes del socket., Envía un mensaje UA/TCP., Responde a HEL con ACK — primer paso del handshake UA/TCP., Maneja OpenSecureChannel con SecurityMode=None., Despacha servicios OPC UA: Read, Browse, GetEndpoints., Retorna la lista de endpoints disponibles. (+5 more)

### Community 35 - "run_scenario.py"
Cohesion: 0.12
Nodes (18): Pruebas unitarias sobre scripts/run_scenario.py., Validar manifiesto existente de scenario_01 vía función interna., Validar manifiesto inexistente debe retornar False sin lanzar excepción no…, main() con --validate-manifest en escenario válido debe retornar código 0., main() con --validate-manifest en escenario inválido debe retornar código 2., main() con --scorecard hacia URL caída no debe romper ejecución y retorna…, main() con --submit hacia servicio caído retorna código 1 controladamente., TestRunScenario (+10 more)

### Community 36 - "HistorianTSDB"
Cohesion: 0.15
Nodes (12): main(), Any, Ataque Replay con sabotaje físico y verificación de divergencia telemetría vs…, StuxnetReplayAttack, Verifica que el ataque sabotee el PLC vía Modbus mientras el Historian recibe…, Si el PLC no está activo, el ataque activa el modo TABLETOP_FALLBACK…, TestStuxnetAttack, HistorianTSDB (+4 more)

### Community 37 - "EcsEvent"
Cohesion: 0.21
Nodes (9): EcsEvent, forward_event_to_central_siem(), Any, BaseHTTPRequestHandler, Aplica reglas de correlación SOC sobre los eventos ingresados., Ingiere y normaliza un registro de log Zeek (conn.log, notice.log, modbus.log)., Ingiere y normaliza un registro de alerta Suricata Eve JSON (eve.json)., Reenvía asíncronamente un evento normalizado ECS hacia el daemon SIEM central. (+1 more)

### Community 38 - "HmiRequestHandler"
Cohesion: 0.17
Nodes (8): format_rbac_token(), HmiRequestHandler, Any, BaseHTTPRequestHandler, Consulta series de tiempo históricas directamente a HistorianTSDB en SQLite WAL., Envía una acción de control al SCADA Server con token RBAC., Asegura que el token posea el formato <role>:<token> para compatibilidad…, Consulta el estado actual del servidor SCADA con cabecera de autenticación RBAC.

### Community 39 - "cmd_down"
Cohesion: 0.19
Nodes (13): Verifica que el motor HMI registre alarma de LOSS_OF_VIEW y cambie a…, cmd_down(), Commands, 10. Lo que este Plan NO Persigue, 2. Objetivos Estratégicos y Métricas de Éxito, 3. Fase 0 — Cimientos: Manifiestos de Escenario y Semilla de Sesión, 5. Fase 2 — Contención: Egress, Namespaces y Jaula Probada, 6. Fase 3 — Ciclo de Vida por Cgroups y Secretos Fuera del Repo (+5 more)

### Community 40 - "HistorianAntiForensicsAttack"
Cohesion: 0.23
Nodes (6): HistorianAntiForensicsAttack, main(), Any, Verifica que el ataque purgue físicamente los registros de telemetría de la…, Verifica ejecución CLI con DB temporal., TestAntiForensicsAttack

### Community 41 - "traffic.py"
Cohesion: 0.15
Nodes (12): create_federate(), main(), helics_federate, helics_input, helics_publication, physical/transport package, LightPhase, Enum (+4 more)

### Community 42 - "CityLab - Development Guidelines"
Cohesion: 0.18
Nodes (11): Code Quality Standards Analysis, Development Workflow Guidelines, CityLab - Development Guidelines, Practices Followed Throughout Codebase, Semantic Patterns Overview, Structural Conventions, Textual Standards, 📐 Arquitectura de Red (IEC 62443) (+3 more)

### Community 43 - "🛡️ Arquitectura del Cyber Range CityLab (IEC 62443 / Co-Simulación Ciberfísica)"
Cohesion: 0.13
Nodes (14): Architectural Patterns, Core Components, Directory Organization, CityLab - Project Structure, File Naming Conventions, 1. Visión General del Sistema y Filosofía de Diseño, 2. Estructura del Proyecto y Módulos de Código, 3. Topología de Red y Microsegmentación (IEC 62443) (+6 more)

### Community 44 - "HoneypotTouch"
Cohesion: 0.20
Nodes (9): HoneypotTouch, main(), Any, Verifica que la conexión socket real al Honeypot dispare la alerta en el…, Verifica que si el honeypot está inalcanzable caiga en TABLETOP_FALLBACK., Verifica la invocación CLI., TestHoneypotTouch, Inicia OtHoneypotServer en puerto alto y asegura stop() en finally. (+1 more)

### Community 45 - "._conn"
Cohesion: 0.16
Nodes (9): Connection, Any, Escribe un punto de telemetría. Args: sector: Nombre del sector OT ('water',…, Escribe el snapshot JSON completo de un sector. Permite consultas de telemetría…, Consulta puntos de telemetría históricos. Args: sector: Sector OT a consultar.…, Consulta snapshots completos del sector. Returns: Lista de dicts con keys: ts,…, Lista los sectores con datos en el historian., Elimina puntos excedentes para mantener retención máxima por sector. Args:… (+1 more)

### Community 46 - "NtpTimeSpoofingAttack"
Cohesion: 0.23
Nodes (6): main(), NtpTimeSpoofingAttack, Any, Verifica que el ataque inyecte muestras con timestamp manipulado en el…, Verifica ejecución CLI., TestTimeSpoofingAttack

### Community 47 - "KerberoastAttack"
Cohesion: 0.20
Nodes (8): KerberoastAttack, main(), Any, Verifica si el servicio KDC Kerberos está respondiendo en la red., Verifica que el ataque solicite y reciba un ticket TGS vía socket real TCP al…, Verifica que si el KDC está inaccesible caiga en TABLETOP_FALLBACK sin romper., Verifica la invocación por CLI tanto en live como en fallback., TestKerberoastAttack

### Community 48 - "OpcUaServer"
Cohesion: 0.13
Nodes (13): main(), OpcUaClient, OpcUaNodeSpace, OpcUaServer, Lista todos los nodos disponibles., Servidor TCP que emula el protocolo UA/TCP de OPC UA. Suficiente para…, Arranca el servidor. Bloqueante — llamar desde un hilo., Cliente OPC UA TCP mínimo para pruebas de integración. Replica exactamente el… (+5 more)

### Community 49 - "TestOpcUaNodeSpace"
Cohesion: 0.13
Nodes (8): Tests unitarios del espacio de nodos OpcUaNodeSpace., read() retorna datos correctos para un nodo existente., read() retorna None para un NodeId desconocido., write() actualiza el valor y read() lo refleja., write() retorna False para NodeId desconocido., browse() lista todos los nodos del espacio., all_values() agrupa datos por sector correctamente., TestOpcUaNodeSpace

### Community 50 - "Dnp3OutstationState"
Cohesion: 0.14
Nodes (10): TestSdnAndDnp3Sa, Dnp3OutstationState, Dnp3ProtocolHandler, Decodifica tramas DNP3 TCP/IP y genera respuestas de Outstation DNP3 validas., Procesa una trama DNP3 entrante y devuelve el paquete de respuesta DNP3., Construye un paquete de respuesta DNP3 READ conteniendo BI (0,1) y AI (0,1,2)., Construye respuesta DNP3 CROB ACK (Success)., Envuelve la carga útil en la trama Link Layer de DNP3 con CRCs. (+2 more)

### Community 51 - "InsiderRbacAttack"
Cohesion: 0.22
Nodes (7): InsiderRbacAttack, main(), Any, Verifica que con STRICT_AUTH=1 el rol auditor sea bloqueado para writes., Verifica que con STRICT_AUTH=0 el rol auditor siga sin permiso de escritura en…, Verifica invocación CLI., TestInsiderRbacAttack

### Community 52 - "citylab.sh"
Cohesion: 0.33
Nodes (12): c_err(), c_info(), cmd_profile(), cmd_smoke(), cmd_status(), cmd_test(), cmd_up(), main() (+4 more)

### Community 53 - "Apagón Urbano en Cascada (Scenario #01, Avanzado)"
Cohesion: 0.14
Nodes (14): Scenario 01: Apagón Urbano en Cascada, Category: Multi-Sector Industrial Impact / Cascading Failure, Apagón Urbano en Cascada (Scenario #01, Avanzado), FLAG_1: Reconocimiento DMZ completado (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, FLAG_2: Subfrecuencia de red provocada (200 pts), Validation Check: Type: historian_condition, query=grid_freq_hz < 58.0, sector=elec, window_s=60, FLAG_3: Apagón en cascada logrado (300 pts) (+6 more)

### Community 54 - "ModbusReadOnly"
Cohesion: 0.31
Nodes (6): main(), ModbusReadOnly, Lee telemetría vía Modbus/TCP en modo pasivo sin escrituras., Verifica que la lectura pasiva lea correctamente valores reales del datastore…, Verifica que ante un host no alcanzable caiga en TABLETOP_FALLBACK., TestModbusRead

### Community 55 - "Dnp3MasterClient"
Cohesion: 0.19
Nodes (8): Dnp3MasterClient, main(), Any, Cliente Master DNP3 ultraligero para consulta y control en Cyber Range., Envía una solicitud DNP3 READ (Group 1 BI & Group 30 AI)., Envía comando CROB Direct Operate / Pulse ON para disparar o cerrar el…, crc16_dnp(), Calcula el CRC-16 especificado por DNP3 (invertido / complemento a unos).

### Community 56 - "test_scenario_manifest.py"
Cohesion: 0.13
Nodes (14): manifest_schema(), fixture, Tests unitarios para la validación de manifiestos YAML de escenarios contra…, Valida exhaustivamente cada uno de los 29 manifiestos generados contra…, Verifica que schema.json sea un esquema JSON válido., Valida el manifiesto piloto scenario_01.yml contra schema.json., Valida que todos los tipos de checks permitidos pasen la validación., Verifica que un manifiesto inválido falle la validación. (+6 more)

### Community 57 - "properties"
Cohesion: 0.17
Nodes (12): properties, expect, field, pattern, query, rule, rule_id, sector (+4 more)

### Community 58 - "NtcipListener"
Cohesion: 0.29
Nodes (3): NtcipListener, Listener NTCIP 1202 de baja fidelidad en el mismo host que el PLC de…, TestNtcipListener

### Community 59 - "OtHoneypotServer"
Cohesion: 0.26
Nodes (3): main(), OtHoneypotServer, TestHoneypotServer

### Community 60 - "📌 1. Visión General del Módulo"
Cohesion: 0.20
Nodes (9): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Código y Flujo de Trabajo, 🧮 3. Modelo Físico e Interdependencia Ciberfísica, 🗺️ 4. Mapa de Registros Modbus TCP (PLC Agua `10.0.3.10:502`), 📡 5. Interfaz de Co-Simulación HELICS, 💾 6. Presupuesto de Recursos y Memoria RAM, 📘 Federado 01 — Sector Agua SWaT (Tratamiento y Distribución Multi-Etapa), Calcula el estado hidráulico de la red. Retorna (flow_m3_s, pressure_bar,… (+1 more)

### Community 61 - "Inyección y Spoofing de Mensajes GOOSE IEC 61850 (Scenario #02, Avanzada)"
Cohesion: 0.18
Nodes (11): Scenario 02: Inyección y Spoofing de Mensajes GOOSE IEC 61850, Category: Industrial Cybersecurity / Substation Automation / IEC 61850, Inyección y Spoofing de Mensajes GOOSE IEC 61850 (Scenario #02, Avanzada), FLAG_1: Sniffing de multicast GOOSE en subestación (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/health, expect=200, FLAG_2: Disparo no autorizado de interruptor de subestación detectado en SIEM (200 pts), Validation Check: Type: siem_alert, rule=GOOSE, HTTP Endpoint: http://10.0.2.20:8080/health (+3 more)

### Community 62 - "Ataque Low and Slow al Sistema SIS SIL-3 (Scenario #03, Avanzado)"
Cohesion: 0.18
Nodes (11): Scenario 03: Ataque Low and Slow al Sistema SIS SIL-3, Category: Safety Instrumented Systems / Triton / HatMan Emulation, Ataque Low and Slow al Sistema SIS SIL-3 (Scenario #03, Avanzado), FLAG_1: Lectura de telemetría de seguridad SIL-3 (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, FLAG_2: Desvío sigiloso de umbrales SIS verificado en Historian (250 pts), Validation Check: Type: historian_condition, query=pressure_psi > 120.0, sector=gas, window_s=90, Historian Condition (gas): pressure_psi > 120.0 (+3 more)

### Community 63 - "Replay Attack Modbus Tipo Stuxnet (Scenario #04, Intermedio)"
Cohesion: 0.18
Nodes (11): Scenario 04: Replay Attack Modbus Tipo Stuxnet, Category: Industrial Protocol Exploitation / Modbus Replay, Replay Attack Modbus Tipo Stuxnet (Scenario #04, Intermedio), FLAG_1: Captura de paquetes Modbus legítimos (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, FLAG_2: Replay inyectado y detectado por anomalía Modbus DPI (200 pts), Validation Check: Type: siem_alert, rule=Modbus, HTTP Endpoint: http://10.0.2.20:8080/api/telemetry (+3 more)

### Community 64 - "Conmutación y Failover en Cluster SCADA HA (Scenario #05, Intermedio)"
Cohesion: 0.18
Nodes (11): Scenario 05: Conmutación y Failover en Cluster SCADA HA, Category: High Availability / SCADA Resilience, Conmutación y Failover en Cluster SCADA HA (Scenario #05, Intermedio), FLAG_1: Inspección de estado de cluster SCADA HA (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/ha/status, expect=200, FLAG_2: Failover ejecutado exitosamente manteniendo visibilidad (200 pts), Validation Check: Type: scada_sector_status, sector=elec, expect=NORMAL, HTTP Endpoint: http://10.0.2.20:8080/api/ha/status (+3 more)

### Community 65 - "Kerberoasting y Abuso de Samba Active Directory (Scenario #06, Avanzado)"
Cohesion: 0.18
Nodes (11): Scenario 06: Kerberoasting y Abuso de Samba Active Directory, Category: Identity & Access Management / Active Directory / Kerberos, Kerberoasting y Abuso de Samba Active Directory (Scenario #06, Avanzado), FLAG_1: Enumeración de SPNs en Domain Controller (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/whoami, expect=200, FLAG_2: Alerta de Kerberoasting / Ticket TGS anómalo detectada en SIEM (250 pts), Validation Check: Type: siem_alert, rule=Kerberos, HTTP Endpoint: http://10.0.2.20:8080/api/whoami (+3 more)

### Community 66 - "Anti-Forense y Manipulación de Historian TSDB (Scenario #07, Avanzado)"
Cohesion: 0.18
Nodes (11): Scenario 07: Anti-Forense y Manipulación de Historian TSDB, Category: Industrial Forensics / TSDB Integrity / Anti-Forensics, Anti-Forense y Manipulación de Historian TSDB (Scenario #07, Avanzado), FLAG_1: Consulta de auditoría sobre tabla de telemetría Historian (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/history?sector=water, expect=200, FLAG_2: Detección de manipulación de registros históricos (250 pts), Validation Check: Type: historian_condition, query=tampered == 1, window_s=120, Historian Condition (general): tampered == 1 (+3 more)

### Community 67 - "Abuso de Privilegios y Escalación RBAC en SCADA (Scenario #08, Intermedio)"
Cohesion: 0.18
Nodes (11): Scenario 08: Abuso de Privilegios y Escalación RBAC en SCADA, Category: Access Control / RBAC / Privilege Escalation, Abuso de Privilegios y Escalación RBAC en SCADA (Scenario #08, Intermedio), FLAG_1: Auditoría de roles y permisos SCADA API (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/whoami, expect=200, FLAG_2: Intento de comando no autorizado bloqueado con 403 (200 pts), Validation Check: Type: siem_alert, rule=RBAC, HTTP Endpoint: http://10.0.2.20:8080/api/whoami (+3 more)

### Community 68 - "Dosificación Química en Planta de Tratamiento de Agua (Scenario #09, Avanzada)"
Cohesion: 0.18
Nodes (11): Scenario 09: Dosificación Química en Planta de Tratamiento de Agua, Category: Water Treatment Process / Chemical Dosing (Oldsmar Pattern), Dosificación Química en Planta de Tratamiento de Agua (Scenario #09, Avanzada), FLAG_1: Monitoreo de pH y nivel de cloro en sector agua (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, FLAG_2: Sobredosificación química detectada en Historian (250 pts), Validation Check: Type: historian_condition, query=ph_level > 8.5, sector=water, window_s=60, Historian Condition (water): ph_level > 8.5 (+3 more)

### Community 69 - "Atribución de Ola de Calor vs Ciberataque a la Red Eléctrica (Scenario #10, Avanzado)"
Cohesion: 0.18
Nodes (11): Scenario 10: Atribución de Ola de Calor vs Ciberataque a la Red Eléctrica, Category: Incident Response / Cyber-Physical Attribution / Electrical Grid, Atribución de Ola de Calor vs Ciberataque a la Red Eléctrica (Scenario #10, Avanzado), FLAG_1: Análisis de carga térmica y demanda en transformadores (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, FLAG_2: Correlación de eventos climáticos vs anomalía maliciosa (250 pts), Validation Check: Type: siem_alert, rule=Grid, HTTP Endpoint: http://10.0.2.20:8080/api/telemetry (+3 more)

### Community 70 - "Spoofing de Tiempo NTP y Desincronización de Subestación (Scenario #11, Avanzado)"
Cohesion: 0.18
Nodes (11): Scenario 11: Spoofing de Tiempo NTP y Desincronización de Subestación, Category: Time Synchronization / NTP Spoofing / Substation Telemetry, Spoofing de Tiempo NTP y Desincronización de Subestación (Scenario #11, Avanzado), FLAG_1: Verificación de drift de reloj en subestación (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/health, expect=200, FLAG_2: Alerta de desincronización horaria en SIEM (200 pts), Validation Check: Type: siem_alert, rule=Time, HTTP Endpoint: http://10.0.2.20:8080/health (+3 more)

### Community 71 - "Ransomware con Impacto en Infraestructura OT (Scenario #12, Avanzado)"
Cohesion: 0.18
Nodes (11): Scenario 12: Ransomware con Impacto en Infraestructura OT, Category: Ransomware Emulation / IT-OT Lateral Movement, Ransomware con Impacto en Infraestructura OT (Scenario #12, Avanzado), FLAG_1: Detección de cifrado de archivos en estación de ingeniería (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/health, expect=200, FLAG_2: Aislamiento de segmento OT activado ante ransomware (250 pts), Validation Check: Type: openflow_rule, switch=s3, pattern=drop, HTTP Endpoint: http://10.0.2.20:8080/health (+3 more)

### Community 72 - "Escaneo Activo y Enumeración de PLCs OT (Scenario #14, Básico)"
Cohesion: 0.18
Nodes (11): Scenario 14: Escaneo Activo y Enumeración de PLCs OT, Category: Network Scanning / Modbus Enumeration / Asset Profiling, Escaneo Activo y Enumeración de PLCs OT (Scenario #14, Básico), FLAG_1: Identificación de puertos industriales abiertos (502, 20000, 4840) (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, FLAG_2: Alerta de escaneo masivo de puertos detectada en honeypot/SIEM (150 pts), Validation Check: Type: siem_alert, rule=Scan, HTTP Endpoint: http://10.0.2.20:8080/api/telemetry (+3 more)

### Community 73 - "Escritura de Bobina Individual Modbus (Single Coil Write) (Scenario #18, Intermedio)"
Cohesion: 0.18
Nodes (11): Scenario 18: Escritura de Bobina Individual Modbus (Single Coil Write), Category: Process Control Manipulation / Modbus Function Code 05, Escritura de Bobina Individual Modbus (Single Coil Write) (Scenario #18, Intermedio), FLAG_1: Escritura de bobina FC05 sobre PLC de gas o agua (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, FLAG_2: Cambio de actuador registrado en Historian (150 pts), Validation Check: Type: historian_condition, query=pump_state == 1, window_s=60, Historian Condition (general): pump_state == 1 (+3 more)

### Community 74 - "Cadena de Pivoteo Guiada Attacker -> DMZ -> OT (Scenario #19, Intermedio)"
Cohesion: 0.18
Nodes (11): Scenario 19: Cadena de Pivoteo Guiada Attacker -> DMZ -> OT, Category: Network Pivoting / Multi-Tier Segmentation / Conduit Traversal, Cadena de Pivoteo Guiada Attacker -> DMZ -> OT (Scenario #19, Intermedio), FLAG_1: Salto desde segmento corporativo a DMZ (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/health, expect=200, FLAG_2: Pivoteo exitoso de DMZ a red OT (200 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, HTTP Endpoint: http://10.0.2.20:8080/health (+3 more)

### Community 75 - "Pérdida de Visibilidad (Loss of View) y Aislamiento Manual (Scenario #21, Intermedio)"
Cohesion: 0.18
Nodes (11): Scenario 21: Pérdida de Visibilidad (Loss of View) y Aislamiento Manual, Category: Loss of View / SCADA Watchdog / Incident Containment, Pérdida de Visibilidad (Loss of View) y Aislamiento Manual (Scenario #21, Intermedio), FLAG_1: Pérdida de paquetes de telemetría provocada (100 pts), Validation Check: Type: scada_sector_status, sector=water, expect=LOSS_OF_VIEW, FLAG_2: Aislamiento manual ejecutado en switch de acceso (150 pts), Validation Check: Type: openflow_rule, switch=s3, pattern=drop, OpenFlow SDN Rule on s3 (drop) (+3 more)

### Community 76 - "Métricas Purple Team: Medición y Optimización de MTTD (Scenario #22, Avanzado)"
Cohesion: 0.18
Nodes (11): Scenario 22: Métricas Purple Team: Medición y Optimización de MTTD, Category: Purple Teaming / SOC Evaluation / MTTD Metrics, Métricas Purple Team: Medición y Optimización de MTTD (Scenario #22, Avanzado), FLAG_1: Generación de eventos de prueba y correlación SIEM (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8514/health, expect=200, FLAG_2: MTTD inferior a 15 segundos registrado en Scoreboard (200 pts), Validation Check: Type: siem_alert, rule=MTTD, HTTP Endpoint: http://10.0.2.20:8514/health (+3 more)

### Community 77 - "properties"
Cohesion: 0.18
Nodes (11): additionalProperties, required, type, type, properties, minimum, type, check (+3 more)

### Community 78 - "1. DIAGNÓSTICO Y ANÁLISIS DE CAUSA RAÍZ"
Cohesion: 0.18
Nodes (10): 1.1 Punto Ciego CI en `scripts/validate_localhost.py` (P0), 1.2 Falso Verde por Redundancia en `test_sentinel_sanitization.py` (P1 / Checklist #6), 1.3 Asertos Débiles en `network/tests/test_siem.py` (P2 / Checklist #1), 1.4 Riesgo de Flakiness por `time.sleep` Fijo (P3 / Checklist #19), 1.5 Incompatibilidad `argv` en `scripts/run_scenario.py` (P4 / Checklist #11 & Brecha de Cobertura #2), 1. DIAGNÓSTICO Y ANÁLISIS DE CAUSA RAÍZ, 2. ETAPAS DE IMPLEMENTACIÓN, 3. CRITERIOS DE ACEPTACIÓN (+2 more)

### Community 79 - "PostIncidentRecovery"
Cohesion: 0.31
Nodes (4): main(), PostIncidentRecovery, Any, TestScenario29Recovery

### Community 80 - "Plan Director de Evolución Alta Fidelidad y Gemelo Digital"
Cohesion: 0.20
Nodes (10): Plan Director de Evolución Alta Fidelidad y Gemelo Digital, EPANET2 C-API Motor Hidráulico, GridLAB-D C++ Multifásico y Flujo de Carga AC, Estándar IEC 62443-3-3 y NIST SP 800-82r3, libiec61850 Native Daemon Layer 2 Sockets, open62541 OPC UA Server Cifrado con X.509, Sondas SOC Pasivas en Puerto SPAN OVS Zeek y Suricata, Fase 1: Runtimes IEC 61131-3 OpenPLC y Protocolos Nativos L2/L7 (+2 more)

### Community 81 - "PurpleTeamMttd"
Cohesion: 0.36
Nodes (4): main(), PurpleTeamMttd, Any, TestScenario22PurpleTeam

### Community 82 - "enum"
Cohesion: 0.22
Nodes (9): enum, type, difficulty, Avanzada, Avanzado, Básico, Capstone, Intermedio (+1 more)

### Community 83 - "items"
Cohesion: 0.22
Nodes (9): type, items, minItems, type, objectives, seed_scope, description, items (+1 more)

### Community 84 - "run_modbus_attack"
Cohesion: 0.45
Nodes (9): connect(), do_fault(), do_start_stop_blast(), main(), ModbusTcpClient, Ejecuta ataque Modbus/TCP contra PLC objetivo vía socket real o fallback…, read_coils(), run_modbus_attack() (+1 more)

### Community 85 - "BlindRandomizedEnv"
Cohesion: 0.43
Nodes (4): BlindRandomizedEnv, main(), Any, TestScenario28Blind

### Community 86 - "RansomwareTabletop"
Cohesion: 0.43
Nodes (4): main(), Any, RansomwareTabletop, TestScenario25Tabletop

### Community 87 - "RedVsBlueMatch"
Cohesion: 0.43
Nodes (4): main(), Any, RedVsBlueMatch, TestScenario27RedBlue

### Community 88 - "Reconocimiento Pasivo en Red OT (Scenario #13, Básico)"
Cohesion: 0.25
Nodes (8): Scenario 13: Reconocimiento Pasivo en Red OT, Category: Network Reconnaissance / Passive Sniffing / Industrial Asset Discovery, Reconocimiento Pasivo en Red OT (Scenario #13, Básico), FLAG_1: Descubrimiento de hosts y controladores en segmento OT (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, HTTP Endpoint: http://10.0.2.20:8080/api/telemetry, Seed Scope Parameter: flags, Seed Scope Parameter: mac_prefixes

### Community 89 - "Lectura de Telemetría Modbus TCP sin Autenticación (Scenario #15, Básico)"
Cohesion: 0.25
Nodes (8): Scenario 15: Lectura de Telemetría Modbus TCP sin Autenticación, Category: Industrial Protocols / Modbus TCP / Unauthenticated Telemetry, Lectura de Telemetría Modbus TCP sin Autenticación (Scenario #15, Básico), FLAG_1: Lectura de Holding Registers de sector agua vía Modbus TCP (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, HTTP Endpoint: http://10.0.2.20:8080/api/telemetry, Seed Scope Parameter: flags, Seed Scope Parameter: register_offsets

### Community 90 - "Interacción y Detección de Honeypot OT (Scenario #16, Básico)"
Cohesion: 0.25
Nodes (8): Scenario 16: Interacción y Detección de Honeypot OT, Category: Deception Technology / OT Honeypot / Threat Detection, Interacción y Detección de Honeypot OT (Scenario #16, Básico), FLAG_1: Conexión e interacción con servicio decoy en 10.0.5.99 (100 pts), Validation Check: Type: siem_alert, rule=Honeypot, Seed Scope Parameter: flags, Seed Scope Parameter: honey_coils, SIEM Alert Rule: Honeypot

### Community 91 - "Exploración y Tour de la API HMI/SCADA (Scenario #17, Básico)"
Cohesion: 0.25
Nodes (8): Scenario 17: Exploración y Tour de la API HMI/SCADA, Category: SCADA Web Interface / REST API / Telemetry Exploration, Exploración y Tour de la API HMI/SCADA (Scenario #17, Básico), FLAG_1: Inspección de endpoints /api/telemetry y /api/history (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/telemetry, expect=200, HTTP Endpoint: http://10.0.2.20:8080/api/telemetry, Seed Scope Parameter: endpoints, Seed Scope Parameter: flags

### Community 92 - "Conmutación de Modo de Autenticación Estricta (STRICT_AUTH) (Scenario #20, Intermedio)"
Cohesion: 0.25
Nodes (8): Scenario 20: Conmutación de Modo de Autenticación Estricta (STRICT_AUTH), Category: Security Hardening / RBAC / Authentication Enforcing, Conmutación de Modo de Autenticación Estricta (STRICT_AUTH) (Scenario #20, Intermedio), FLAG_1: Verificación de enforcement de tokens de rol en SCADA API (100 pts), Validation Check: Type: http_status, url=http://10.0.2.20:8080/api/whoami, expect=200, HTTP Endpoint: http://10.0.2.20:8080/api/whoami, Seed Scope Parameter: flags, Seed Scope Parameter: strict_tokens

### Community 93 - "2. PLAN TÉCNICO DE REMEDIACIÓN REVISADO"
Cohesion: 0.12
Nodes (15): 1.1 Contexto, 1.2 Diagnóstico Detallado, 1. RESUMEN EJECUTIVO Y ANÁLISIS DE CAUSA RAÍZ, 2. PLAN TÉCNICO DE REMEDIACIÓN REVISADO, 3.1 Pruebas Unitarias e Integración (Pytest), 3.2 Pruebas de Humo (Smoke Tests), 3.3 Validación E2E Mininet y Verificación de Entorno Limpio, 3. PROTOCOLO DE VERIFICACIÓN Y CRITERIOS DE ACEPTACIÓN CORREGIDOS (+7 more)

### Community 94 - "ConditionChecker"
Cohesion: 0.21
Nodes (9): ConditionChecker, Any, Path, Evalúa oráculos de verificación de estado físico, SCADA, SIEM y red., Evalúa una definición de check y retorna (éxito, mensaje/detalle)., Verifica la evaluación del oráculo de estado de sector SCADA., Verifica la evaluación del oráculo de estado físico sobre el Historian TSDB., test_checker_historian_condition() (+1 more)

### Community 95 - "run_phase1.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase1.sh script

### Community 96 - "run_phase2.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase2.sh script

### Community 97 - "run_phase3.sh"
Cohesion: 0.29
Nodes (7): AUTO_START_PLC, BASE_DIR, check_dep(), MININET_PING_TIMEOUT, PYTHONPATH, PYTHONUNBUFFERED, run_phase3.sh script

### Community 98 - "CityLab - Product Overview"
Cohesion: 0.29
Nodes (7): Capabilities, CityLab - Product Overview, Key Features, Project Purpose, Target Users, Use Cases, Value Proposition

### Community 99 - "required"
Cohesion: 0.29
Nodes (7): required, required, check, desc, id, objectives, title

### Community 100 - "Development Workflow"
Cohesion: 0.25
Nodes (8): Build Systems and Development Tools, Core Dependencies, Development Workflow, CityLab - Technology Stack, Platform Requirements, Programming Languages and Versions, Runtime Environment, Any

### Community 101 - "Prompt Auditor Principal de Ciberseguridad Industrial"
Cohesion: 0.29
Nodes (7): Checklist de 24 Patologías y Defectos de Auditoría, Prompt Auditor Principal de Ciberseguridad Industrial, Metodología de Auditoría IEC 62443 y Verificación Empírica, Regla de Oro de Vulnerabilidades Intencionales F-03 F-05 F-06 F-07, Catálogo de Defectos y Checklist de Verificación (Español), Prompt Auditor de Ciberseguridad Industrial (Español), Metodología de Auditoría IEC 62443 (Español)

### Community 102 - "smoke_test_phase4.sh"
Cohesion: 0.29
Nodes (6): HELICS_BROKER_PORT, HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase4.sh script

### Community 103 - ".read_node"
Cohesion: 0.22
Nodes (5): Any, Lee el valor actual de un nodo., Escribe el valor de un nodo. Retorna True si el nodo existe., Retorna snapshot completo del espacio de nodos por sector., Lee el valor de un nodo OPC UA.

### Community 104 - "poc_modbus_test.py"
Cohesion: 0.62
Nodes (6): main(), ModbusTcpClient, Automated integration test for the PoC PLC Modbus interface. Usage (from within…, read_coils(), wait_for_coil(), write_coil()

### Community 105 - "properties"
Cohesion: 0.33
Nodes (6): type, properties, category, title, description, type

### Community 106 - "id"
Cohesion: 0.33
Nodes (6): description, pattern, type, id, integer, string

### Community 107 - "Escenario 22: Medición de Métricas SOC Purple Team (MTTD / MTTR)"
Cohesion: 0.33
Nodes (6): 7. Fase 4 — Scoreboard y Métricas MTTD/MTTR Automáticas, Script attacker/attack_purple_team_mttd.py, Escenario CTF 22: Ejercicio Purple Team y Medición de Métricas SOC (MTTD / MTTR), Métricas Cuantitativas de Respuesta SOC (MTTD / MTTR) según NIST SP 800-61, Escenario 22: Medición de Métricas SOC Purple Team (MTTD / MTTR), Inyección de Tráfico GOOSE en Subestación y Telemetría SIEM

### Community 108 - "Escenario 09: Dosificación Química de Cloro/NaOH"
Cohesion: 0.33
Nodes (6): Script attacker/attack_chemical_dosing.py, Controlador de Dosificación de Químicos (NaOH/Cloro), Escenario 09: Dosificación Química de Cloro/NaOH, Escenario CTF 09: Dosificación Química en Planta de Tratamiento de Agua (SWaT / Oldsmar Pattern), Analizadores Independientes de Calidad de Agua Fuera de SCADA, Patrón de Ataque SWaT / Oldsmar (Manipulación Química)

### Community 109 - "Escenario 10: Atribución de Incidentes en Red Eléctrica (Ola de Calor + Sabotaje)"
Cohesion: 0.33
Nodes (6): Script attacker/attack_grid_heatwave_attribution.py, Escenario CTF 10: Falla Natural por Ola de Calor + Ataque Ciberfísico Simultáneo (Incident Attribution), Escenario 10: Atribución de Incidentes en Red Eléctrica (Ola de Calor + Sabotaje), Atribución de Incidentes Ciberfísicos y Root Cause Analysis (RCA), Disyuntor Principal de Subestación Eléctrica, Discriminación entre Sobrecarga Térmica y Modbus Sabotaje

### Community 110 - "Escenario 11: Ataque de Desincronización Horaria NTP/PTP"
Cohesion: 0.33
Nodes (6): Script attacker/attack_ntp_time_spoofing.py, Escenario CTF 11: Ataque de Desincronización de Tiempo NTP / PTP (Time Synchronization Hardening), Integridad Temporal de Muestras IEC 61850 SV e Historian, Sincronización Horaria Industrial (NTP / IEEE 1588 PTP), Escenario 11: Ataque de Desincronización Horaria NTP/PTP, Desfase Temporal (Time Skewing) y Ceguera de Correlación SIEM

### Community 111 - "Escenario 12: Ransomware IT con Parada Preventiva OT"
Cohesion: 0.33
Nodes (6): Script attacker/attack_ransomware_ot_impact.py, Patrón de Incidente Colonial Pipeline (2021), Escenario CTF 12: Ransomware IT con Parada de Emergencia Operacional OT (Colonial Pipeline Pattern), Frontera entre Facturación Corporativa/AD y Bombeo Físico OT, Interdependencia IT/OT y Decisión Humana de Shutdown Precautorio, Escenario 12: Ransomware IT con Parada Preventiva OT

### Community 112 - "Escenario 13: Reconocimiento Pasivo y Sniffing de Redes OT"
Cohesion: 0.33
Nodes (6): Script attacker/attack_ot_passive_recon.py, Escenario CTF 13: Reconocimiento Pasivo en Redes OT (Onboarding Pasivo), Switches de Celda OT (s1, s2, s3), Escenario 13: Reconocimiento Pasivo y Sniffing de Redes OT, Captura Pasiva de Tráfico OT (tcpdump / Wireshark), Protocolos OT en Claro (Modbus 502, OPC UA 4840, GOOSE 10102)

### Community 113 - "Escenario 19: Cadena de Pivoteo Multi-Zona IEC 62443"
Cohesion: 0.33
Nodes (6): Script attacker/attack_multisector.py, Bastión DMZ (10.0.2.10) y Celda OT (10.0.3.10), Escenario CTF 19: Cadena de Pivoteo Guiado Attacker -> DMZ -> OT, Escenario 19: Cadena de Pivoteo Multi-Zona IEC 62443, Zonificación de Red y Salto Secuencial IEC 62443 (Attacker -> DMZ -> OT), Cortafuegos con Inspección de Estado (SPI) y Proxies de Aplicación

### Community 114 - "smoke_test_phase2.sh"
Cohesion: 0.33
Nodes (5): HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase2.sh script

### Community 115 - "smoke_test_phase3.sh"
Cohesion: 0.33
Nodes (5): HELICS_BROKER_PORT, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED, smoke_test_phase3.sh script

### Community 116 - "🎨 Infraestructura 09 — Visualizador Urbano 2D SVG Airgapped y Puente de Telemetría (`fed_viz_bridge.py` & `viz_server.py`)"
Cohesion: 0.25
Nodes (7): 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Flujo de Datos, 🗺️ 3. Mapeo de Tópicos y Sectores Urbanos (8 Sectores), 🌐 4. Endpoints REST API de `viz_server.py`, 🚀 5. Modos de Ejecución y Opciones de CLI, 🔒 6. Garantías de Seguridad y Resiliencia, 🎨 Infraestructura 09 — Visualizador Urbano 2D SVG Airgapped y Puente de Telemetría (`fed_viz_bridge.py` & `viz_server.py`)

### Community 117 - "Scenario 26 Manifest - Campaña APT Sandworm"
Cohesion: 0.70
Nodes (5): FLAG_1: Compromiso de Credenciales Active Directory, FLAG_2: Desconexión de Subestación Eléctrica, FLAG_3: Detección Anti-Forense y Borrado de Logs en SIEM, Scenario 26 Manifest - Campaña APT Sandworm, Emulación de Campaña APT Tipo Sandworm

### Community 118 - "schema.json"
Cohesion: 0.40
Nodes (4): additionalProperties, $schema, title, type

### Community 119 - "Plan de Remediación Técnica Sanitización Sentinels HELICS"
Cohesion: 0.50
Nodes (5): Plan de Remediación Técnica Sanitización Sentinels HELICS, HALLAZGO-2026-08-31-01: Sanitización de Sentinels HELICS, Alineación de Patrones de Log y Smoke Test Harness, Especificación de Sanitización de Enteros y Flotantes HELICS, Suite test_sentinel_sanitization

### Community 120 - "CityLab Runbook y Manual de Operaciones"
Cohesion: 0.50
Nodes (5): Script de Ciclo de Vida citylab.sh, Evaluación de Escenarios CTF y Scoreboard MTTD/MTTR, Matriz de Endpoints y Servicios HMI/SCADA/SIEM, CityLab Runbook y Manual de Operaciones, Suites de Validación Pytest, Smoke y E2E

### Community 121 - "Escenario 14: Escaneo Activo Nmap y Verificación de Segmentación"
Cohesion: 0.40
Nodes (5): Script attacker/attack_ot_active_scan.py, Políticas de Cortafuegos en la DMZ y Bloqueo de Escaneo, Escenario CTF 14: Escaneo Activo de Subredes OT (Segmentación Nmap), Auditoría de Segmentación de Red con Escaneo Activo Nmap, Escenario 14: Escaneo Activo Nmap y Verificación de Segmentación

### Community 122 - "Escenario 15: Lectura de Memoria y Telemetría Modbus"
Cohesion: 0.40
Nodes (5): Script attacker/attack_modbus_read_only.py, Escenario CTF 15: Lectura de Telemetría Modbus sin Escritura, Escenario 15: Lectura de Memoria y Telemetría Modbus, Ausencia de Autenticación en Funciones de Lectura Modbus, Mapa de Memoria y Bobinas del PLC de Agua (10.0.3.10:502)

### Community 123 - "Escenario 16: Interacción con Señuelos Honeypot OT"
Cohesion: 0.40
Nodes (5): Script attacker/attack_honeypot_touch.py, Servicio Honeypot Señuelo (10.0.5.99) y Alertas SIEM, Escenario CTF 16: Interacción con Trampas Deception (Honeypot OT), Escenario 16: Interacción con Señuelos Honeypot OT, Tecnología de Decepción (Deception Technology / Honeypots OT)

### Community 124 - "Escenario 17: API REST y Visualización HMI P&ID"
Cohesion: 0.40
Nodes (5): Script attacker/attack_scada_tour.py, Escenario CTF 17: Tour Guiado por la API SCADA y Servidor HMI, Servidor Web HMI P&ID (:8085 /api/telemetry, /api/history), Escenario 17: API REST y Visualización HMI P&ID, Arquitectura SCADA / HMI Basada en Web (REST / WebSockets)

### Community 125 - "Escenario 18: Inyección y Forzado de Coil Modbus (Bomba de Agua)"
Cohesion: 0.40
Nodes (5): Escenario CTF 18: Escritura Forzada de Coil Modbus Único (Manipulación Guiada), Herramienta attacker/exploit_modbus.py, Inyección de Comandos Modbus sin Autenticación en Puerto 502, Escenario 18: Inyección y Forzado de Coil Modbus (Bomba de Agua), Actuador de Bomba del PLC de Agua (10.0.3.10:502 Coil 0)

### Community 126 - "Escenario 20: Hardening Defensivo de SCADA API (STRICT_AUTH)"
Cohesion: 0.40
Nodes (5): Escenario CTF 20: Comparación de Hardening SCADA API (STRICT_AUTH Toggle), Módulo network/rbac.py y Resolución de Roles Bearer, Hardening de Tokens RBAC en APIs SCADA, Modo Legado Permisivo (STRICT_AUTH=0) vs Modo Estricto (STRICT_AUTH=1), Escenario 20: Hardening Defensivo de SCADA API (STRICT_AUTH)

### Community 127 - "Escenario 23: Defensa SDN Dinámica en Caliente con Open vSwitch"
Cohesion: 0.40
Nodes (5): Script attacker/attack_live_sdn_defense.py, Escenario CTF 23: Defensa SDN Dinámica en Caliente (Safety vs Availability Trade-off), Escenario 23: Defensa SDN Dinámica en Caliente con Open vSwitch, Mitigación Dinámica de Tráfico Malicioso vía Open vSwitch (OVS), Dilema Operativo de Ciberseguridad Industrial: Safety vs Availability

### Community 128 - "Escenario 24: Evasión de Correlación SIEM mediante Ataque Distribuido Multi-IP"
Cohesion: 0.40
Nodes (5): Script attacker/attack_siem_rule_evasion.py, Escenario CTF 24: Evasión de Reglas de Correlación SIEM (Multi-IP Distributed Attack), Motor de Correlación SIEM en network/siem_pipeline.py, Escenario 24: Evasión de Correlación SIEM mediante Ataque Distribuido Multi-IP, Evasión de Firmas Estáticas y Analítica de Comportamiento por Anomalías

### Community 129 - "Escenario 25: Ejercicio Tabletop de Gestión de Crisis por Ransomware"
Cohesion: 0.40
Nodes (5): Script attacker/attack_ransomware_tabletop.py, Roles Directivos en Gestión de Incidentes (CISO, Operaciones, Legal), Escenario CTF 25: Ejercicio Tabletop de Crisis por Ransomware Industrial, Gestión de Crisis Ejecutiva, Toma de Decisiones y Comunicación Regulatoria, Escenario 25: Ejercicio Tabletop de Gestión de Crisis por Ransomware

### Community 130 - "Escenario 26 (Capstone): Emulación de Campaña APT Sandworm / ELECTRUM"
Cohesion: 0.40
Nodes (5): Escenario 26 (Capstone): Emulación de Campaña APT Sandworm / ELECTRUM, Script attacker/attack_apt_sandworm_campaign.py, Escenario CTF 26: Capstone Campaña APT Persistente (Sandworm / ELECTRUM Pattern), Orquestación de Cadena de Ataque Ciberfísica Multietapa (5 Fases), Patrón de Operaciones del Grupo APT Sandworm / ELECTRUM

### Community 131 - "Escenario 27 (Capstone): Competencia Red vs Blue Arbitrada en Tiempo Real"
Cohesion: 0.40
Nodes (5): Script attacker/attack_red_vs_blue_match.py, Escenario CTF 27: Ciberejercicio Simultáneo Red vs Blue con Motor de Arbitraje, Motor de Arbitraje en Vivo y Puntuación Automática de Competencia, Escenario 27 (Capstone): Competencia Red vs Blue Arbitrada en Tiempo Real, Operaciones Simultáneas de Disrupción Física (Red) y Mitigación (Blue)

### Community 132 - "Escenario 28 (Capstone): Evaluación Ciega y Entorno Dinámico Anti-Memorización"
Cohesion: 0.40
Nodes (5): Script attacker/attack_blind_randomized_env.py, Escenario 28 (Capstone): Evaluación Ciega y Entorno Dinámico Anti-Memorización, Escenario CTF 28: Entorno Ciego Dinámico Anti-Memorización, Generador de Parámetros Dinámicos (IP, Puertos, Umbrales SIS), Evaluación de Habilidades Metodológicas Reales (TTPs) sin Parámetros Estáticos

### Community 133 - "Escenario 29 (Capstone): Recuperación Post-Incidente y Reintegración Segura"
Cohesion: 0.40
Nodes (5): Script attacker/attack_post_incident_recovery.py, Restauración de Confianza Digital y Resiliencia Operacional Post-Incidente, Escenario CTF 29: Recuperación Post-Incidente y Reintegración Operacional (Disaster Recovery), Verificación de Integridad de Firmware de PLCs y Reconstrucción Out-of-Band del Historian, Escenario 29 (Capstone): Recuperación Post-Incidente y Reintegración Segura

### Community 134 - "Scenario 23 Manifest - Defensa Dinámica SDN"
Cohesion: 0.83
Nodes (4): FLAG_1: Disparo Automático Circuit Breaker, FLAG_2: Regla OpenFlow DROP en Switch s3, Scenario 23 Manifest - Defensa Dinámica SDN, Defensa Dinámica con Controlador SDN y Circuit Breaker

### Community 135 - "Scenario 24 Manifest - Evasión SIEM Multi-IP"
Cohesion: 0.83
Nodes (4): FLAG_1: Sondas Modbus Distribuidas Multi-IP, FLAG_2: Correlación Multi-Origen Pipeline SIEM, Scenario 24 Manifest - Evasión SIEM Multi-IP, Evasión de Reglas SIEM con Múltiples IPs de Origen

### Community 136 - "Scenario 27 Manifest - Live Fire Red vs Blue"
Cohesion: 0.83
Nodes (4): FLAG_1: Primer Objetivo de Intrusión Capturado, FLAG_2: Mitigación Blue Team en Tiempo Objetivo, Scenario 27 Manifest - Live Fire Red vs Blue, Enfrentamiento Red vs Blue Adjudicado

### Community 137 - "Entorno Ciego Anti-Memorización"
Cohesion: 0.83
Nodes (4): Entorno Ciego Anti-Memorización, FLAG_1: Descubrimiento de Parámetros Dinámicos de Sesión, FLAG_2: Resolución de Objetivo con Offsets Aleatorizados, Scenario 28 Manifest - Entorno Ciego Anti-Memorización

### Community 138 - "Recuperación ante Desastres (Disaster Recovery) Post-Incidente"
Cohesion: 0.83
Nodes (4): Recuperación ante Desastres (Disaster Recovery) Post-Incidente, FLAG_1: Restauración de Base de Datos Historian, FLAG_2: Reanudación de Operación Nominal en Sectores Urbanos, Scenario 29 Manifest - Disaster Recovery

### Community 139 - "conftest.py"
Cohesion: 0.50
Nodes (3): pytest_sessionfinish(), conftest.py — Pytest session configuration and test isolation., Clean up the temporary historian session directory.

### Community 140 - "Escenario 21: Respuesta a Pérdida de Visibilidad y Aislamiento Manual"
Cohesion: 0.50
Nodes (4): Escenario CTF 21: Respuesta a Pérdida de Visibilidad (Loss of View & Manual Isolation), Procedimiento Operacional de Respuesta ante Pérdida de Visibilidad (Loss of View), Escenario 21: Respuesta a Pérdida de Visibilidad y Aislamiento Manual, Watchdog SCADA y Aislamiento Manual de Puerto de Switch OT (F-06)

### Community 142 - "scada_server.py"
Cohesion: 0.23
Nodes (9): main(), poll_plcs(), poll_plcs_once(), Any, Hilo de fondo que consulta periódicamente los PLCs OT., Ejecuta una ronda individual de consulta a los PLCs OT (directo o vía DPI…, run_http_server(), patch (+1 more)

### Community 143 - "FLAG_1: Plan de Contingencia y Aislamiento de Activos"
Cohesion: 1.00
Nodes (3): FLAG_1: Plan de Contingencia y Aislamiento de Activos, Scenario 25 Manifest - Tabletop Ransomware, Ejercicio Tabletop Respuesta a Incidentes Ransomware

### Community 144 - "Prompt Implementador Senior OT / Cyber Range"
Cohesion: 0.67
Nodes (3): Reglas de Baseline 245 PASS y No-Regresión, Prompt Implementador Senior OT / Cyber Range, Arquitectura y Fases del Roadmap OT

### Community 145 - "Prompt QA Lead — Aseguramiento de Calidad de Tests"
Cohesion: 0.67
Nodes (3): Prompt QA Lead — Aseguramiento de Calidad de Tests, Metodología de Verificación y Calidad de Suites de Prueba, Checklist de 19 Patologías y Falsos Positivos en Tests

### Community 146 - "Walkthrough Escenario 02: Inyección de Mensajes GOOSE IEC 61850"
Cohesion: 1.00
Nodes (3): Walkthrough Escenario 02: Inyección de Mensajes GOOSE IEC 61850, Inyección GOOSE con Salto de stNum Tipo Industroyer2, Detección SIEM de Salto de Secuencia GOOSE

### Community 147 - "Walkthrough Escenario 03: Evasión Sigilosa SIS Triton"
Cohesion: 1.00
Nodes (3): Walkthrough Escenario 03: Evasión Sigilosa SIS Triton, Límites de Seguridad e Interlock SIL-3 IEC 61511, Manipulación Low-and-Slow Sub-Umbral SIS

### Community 148 - "Ceguera Operativa en HMI y Base de Datos Historian"
Cohesion: 1.00
Nodes (3): Ceguera Operativa en HMI y Base de Datos Historian, Walkthrough Escenario 04: Replay de Telemetría MITM Tipo Stuxnet, Ataque MITM de Telemetría Grabada y Sabotaje Físico

### Community 149 - "Walkthrough Escenario 05: Explotación de Ventana de Conmutación SCADA HA"
Cohesion: 1.00
Nodes (3): Walkthrough Escenario 05: Explotación de Ventana de Conmutación SCADA HA, Mecanismo de Heartbeat y Timeout de Sincronización HA, Explotación de Ventana de Failover SCADA Primario a Standby

### Community 150 - "Walkthrough Escenario 06: Kerberoasting y Escalado en Active Directory"
Cohesion: 1.00
Nodes (3): Walkthrough Escenario 06: Kerberoasting y Escalado en Active Directory, Escalado a Token con Rol Engineer en SCADA, Extracción de Ticket TGS Kerberos y Crackeo Offline

### Community 151 - "Borrado Anti-Forense de Base de Datos Historian"
Cohesion: 1.00
Nodes (3): Borrado Anti-Forense de Base de Datos Historian, Walkthrough Escenario 07: Anti-Forense y Borrado en Historian TSDB, Defensa SIEM Centralizada Inmutable Fuera de Banda

### Community 152 - "Walkthrough Escenario 08: Insider Threat y Violación RBAC"
Cohesion: 1.00
Nodes (3): Walkthrough Escenario 08: Insider Threat y Violación RBAC, Principio de Mínimo Privilegio y Token Auditor, Enforcement de Control de Acceso RBAC en SCADA Server

### Community 167 - "🚦 Federado 03 — Sector Transporte y Tráfico Urbano (`fed_transport.py`)"
Cohesion: 0.33
Nodes (6): ⚙️ 2. Arquitectura de Código y Flujo de Trabajo, 🧮 3. Modelo Físico de Congestión e Interdependencia, 🗺️ 4. Mapa de Registros Modbus TCP (PLC Transporte `10.0.3.14:502`), 📡 5. Interfaz HELICS Pub-Sub, 💾 6. Presupuesto de Recursos y Memoria RAM, 🚦 Federado 03 — Sector Transporte y Tráfico Urbano (`fed_transport.py`)

### Community 168 - "IEC61850DataSet"
Cohesion: 0.17
Nodes (5): IEC61850DataSet, Any, Publica un paquete GOOSE inmediatamente hacia goose_dest., Publica una muestra SV de voltaje y corriente hacia sv_dest., Dataset IEC 61850 con modelos LNode standard (XCBR, MMXU, CSWI).

### Community 169 - "TwoStageWaterPlant"
Cohesion: 0.20
Nodes (7): main(), Any, RansomwareOtImpactAttack, TestRansomwareAttack, physical/water package, Regla de disparo de protección de planta: - T1 desborde (>95%) o seco (<0.5m³)…, TwoStageWaterPlant

### Community 170 - "📌 1. Visión General del Módulo"
Cohesion: 0.21
Nodes (11): 6. Capa de Supervisión, DMZ y Servicios Centrales, 📌 1. Visión General del Módulo, ⚙️ 2. Arquitectura de Control, DPI Proxy e Historian, 🔀 3. Modbus DPI Proxy y Enrutamiento por Unit ID (`network/modbus_proxy.py`), 🔄 4. Alta Disponibilidad (HA) y Sincronización de Estado (`network/scada_ha.py`), 🔐 5. Control de Acceso por Roles (RBAC Bearer Estático & Toggle `STRICT_AUTH`), 🌐 6. Endpoints REST API de Infraestructura SCADA / HMI / Viz (`:8080`, `:8085`, , 🖥️ Infraestructura 07 — Servidor SCADA Central, HA Cluster, Modbus DPI Proxy y H (+3 more)

### Community 171 - "EpanetHydraulicSolver"
Cohesion: 0.17
Nodes (8): TestPhysicsEngine, EpanetHydraulicSolver, PipeConfig, PumpConfig, Solver hidráulico de red de distribución de agua (Modelo didáctico Hazen-…, Calcula la pérdida de fricción en la tubería usando Hazen-Williams., Calcula la presión generada por la bomba según su curva TDH., physical/water/plant_water.py — Modelo físico de tratamiento de agua en 2…

### Community 172 - "SafetyInstrumentedLogic"
Cohesion: 0.30
Nodes (8): create_federate(), main(), Any, helics_sim/fed_sis.py — Safety Instrumented System (SIS / ESD Independiente)…, Lógica de interlocks SIL-3 independiente., Evalúa los interlocks de seguridad física. Retorna (must_trip, reason)., Aplica la regla de anulación SIS sobre comandos BPCS. Retorna (allowed_cmd,…, SafetyInstrumentedLogic

### Community 173 - ".decode"
Cohesion: 0.29
Nodes (3): Codifica un PDU GOOSE binario en formato TLV / APDU con ConfRev y Test mode., Decodifica un PDU GOOSE binario., Hilo receptor de mensajes GOOSE entrantes en la subestación.

### Community 174 - "ActuatorEmulator"
Cohesion: 0.24
Nodes (5): 5. Capa de Emulación de Dispositivos de Campo (OT), 📌 1. Visión General del Módulo, ActuatorEmulator, ModbusServerContext, Emula la lógica ST del PLC: TON arranque/parada y detección de fallo.

### Community 175 - "Especificación de Requisitos de Software (ERS)"
Cohesion: 0.25
Nodes (9): 2. Descripción General, 4. Requisitos No Funcionales (RNF), Especificación de Requisitos de Software (ERS), Proyecto: Cyber Range Ciberfísico Multisectorial (CityLab), 1. Contexto y Justificación, Cadena de Sabotaje Eléctrico y Cascada Ciberfísica, Walkthrough Escenario 01: Apagón Urbano en Cascada, Efecto Dominó Hospital UPS y Tráfico Urbano (+1 more)

### Community 176 - "spoof_goose_trip"
Cohesion: 0.15
Nodes (11): is_multicast_addr(), main(), Construye y transmite un paquete GOOSE malicioso de disparo de interruptor., spoof_goose_trip(), Verifica la codificación y decodificación binaria del PDU GOOSE., Ataque real vía socket UDP provoca mutación de estado observable en el IED., Paquetes UDP malformados no deben mutar el estado del interruptor., El entrypoint CLI main() ejecuta ráfagas de spoofing sobre el puerto de test… (+3 more)

### Community 177 - "sanitize_trip_signal"
Cohesion: 0.16
Nodes (13): main(), main(), Sanitiza señales booleanas/enteras de disparo (trip/interlock/ups). Solo un…, Sanitiza valores analógicos continuos tipo double. Si el valor es inferior al…, sanitize_telemetry_double(), sanitize_trip_signal(), Pruebas directas de las funciones del SUT (helics_sim.sentinel_utils)., Valores no inicializados (-9223372036854775808) deben ser normalizados a 0 por… (+5 more)

### Community 179 - "attack_apt_sandworm_campaign.py"
Cohesion: 0.20
Nodes (8): AptSandwormCampaign, main(), Any, main(), OtPassiveRecon, Any, TestPassiveRecon, TestScenario26Apt

### Community 180 - "BacnetListener"
Cohesion: 0.33
Nodes (3): BacnetListener, Listener BACnet/IP (UDP 47808) de baja fidelidad para automatización de…, TestBacnetListener

### Community 181 - "attack_grid_heatwave_attribution.py"
Cohesion: 0.43
Nodes (4): GridHeatwaveAttributionAttack, main(), Any, TestAttributionAttack

### Community 183 - "✅ REPORTE DE CIERRE DE AUDITORÍA — CityLab Cyber Range"
Cohesion: 0.29
Nodes (7): 🎯 DECISIONES DE DISEÑO PEDAGÓGICO CTF (HALLAZGOS INTENCIONALES), ✅ REPORTE DE CIERRE DE AUDITORÍA — CityLab Cyber Range, 📈 EVOLUCIÓN DEL GRAFO DE CONOCIMIENTO, Programa de Remediación IEC 62443 · Cierre de 3 Semanas, 🔍 REGISTRO DE RIESGO RESIDUAL, 🔒 SCORECARD DE SEGURIDAD: INICIAL vs FINAL, 🧪 VERIFICACIÓN FINAL DEL SISTEMA

### Community 184 - "smoke_test_phase7.sh"
Cohesion: 0.29
Nodes (6): ENABLE_SIS_FEDERATE, HELICS_BROKER_PORT, HELICS_MAX_STEPS, MOCK_PLC, PYTHONPATH, PYTHONUNBUFFERED

### Community 185 - "ModbusDpiProxyServer"
Cohesion: 0.52
Nodes (3): main(), ModbusDpiProxyServer, socket

### Community 186 - "Dnp3Server"
Cohesion: 0.43
Nodes (4): Dnp3Server, main(), socket, Servidor TCP Outstation DNP3 para la subestación eléctrica.

### Community 187 - "Architecture — the big picture"
Cohesion: 0.40
Nodes (4): Architecture — the big picture, Golden rule — intentional vulnerabilities, Gotchas, What this is

## Knowledge Gaps
- **427 isolated node(s):** `PYTHONPATH`, `$schema`, `title`, `type`, `title` (+422 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistorianTSDB` connect `HistorianTSDB` to `test_flag_service.py`, `run_scenario.py`, `HmiRequestHandler`, `HistorianAntiForensicsAttack`, `🛡️ Arquitectura del Cyber Range CityLab (IEC 62443 / Co-Simulación Ciberfísica)`, `IndustrialHmiEngine`, `NtpTimeSpoofingAttack`, `PostIncidentRecovery`, `._conn`, `scada_server.py`, `SCADAAPIHandler`, `TestScadaHistorianHTTPEndpoints`, `TestHistorianTSDB`, `ConditionChecker`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `3. Requisitos Funcionales Específicos` connect `3. Requisitos Funcionales Específicos` to `run_ovs_cmd`, `SmartLightingSystem`, `EcsEvent`, `cmd_down`, `📌 1. Visión General del Módulo`, `🛡️ Arquitectura del Cyber Range CityLab (IEC 62443 / Co-Simulación Ciberfísica)`, `SafetyInstrumentedLogic`, `IndustrialHmiEngine`, `Especificación de Requisitos de Software (ERS)`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `Architecture — the big picture` connect `Architecture — the big picture` to `run_ovs_cmd`, `EcsEvent`, `ElectricalSubstationGrid`, `cmd_down`, `OtHoneypotServer`, `IndustrialHmiEngine`, `scada_server.py`, `.decode`, `ActuatorEmulator`, `OpcUaServer`, `Dnp3OutstationState`, `RBACResolver`, `_emulator_harness.py`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `HistorianTSDB` (e.g. with `HistorianAntiForensicsAttack` and `NtpTimeSpoofingAttack`) actually correct?**
  _`HistorianTSDB` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SiemCorrelationEngine` (e.g. with `HoneypotTouch` and `NtpTimeSpoofingAttack`) actually correct?**
  _`SiemCorrelationEngine` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `OpcUaServer` (e.g. with `TestOpcUaNodeSpace` and `TestOpcUaServerClient`) actually correct?**
  _`OpcUaServer` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `PYTHONPATH`, `$schema`, `title` to the rest of the system?**
  _427 weakly-connected nodes found - possible documentation gaps or missing edges._