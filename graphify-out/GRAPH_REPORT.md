# Graph Report - /home/kripi/Documentos/GitHub/CityLab  (2026-08-31)

## Corpus Check
- 7 files · ~12,000 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 36 nodes · 51 edges · 7 communities
- Extraction: 67% EXTRACTED · 33% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Industrial Digital Twin & High Fidelity
- HELICS Remediation & Physics Fixes
- IEC 62443 Architecture & Defense
- HELICS Remediation & Physics Fixes
- HELICS Remediation & Physics Fixes
- Co-simulation & Interlock Defects
- Industrial Digital Twin & High Fidelity

## God Nodes (most connected - your core abstractions)
1. `🛡️ 稽核者提示 — CityLab Cyber Range (IEC 62443)` - 8 edges
2. `🏗️ Roadmap Alta Fidelidad Industrial y Gemelo Digital` - 8 edges
3. `已驗之架構 (5 Zones/PLC/HELICS/SCADA/29 Attacks)` - 6 edges
4. `HELICS 3.4.0 網實聯動 (8 Federates + Physical Plants)` - 6 edges
5. `已知缺陷 Checklist (24 抗偽稽核模式)` - 5 edges
6. `🛠️ Plan de Remediación HELICS Sentinel (Hallazgo 01)` - 5 edges
7. `守勢防禦 Stack (SCADA HA/Historian/SIEM/SDN)` - 4 edges
8. `PASO 0 — 基準 (HEAD/151 Tests/Sudo e2e/Topology)` - 3 edges
9. `PLC Daemons & Protocols (Modbus/DNP3/IEC61850/OPC UA)` - 3 edges
10. `缺陷模式 #16/#17: 物理不可達死連鎖 / 哨兵值偽綠` - 3 edges

## Surprising Connections (you probably didn't know these)
- `GridLAB-D Sentinel Sanitization (t == 1 & double < -1e20)` --implements--> `Paso 1: Parche en helics_sim/gridlabd_federate.py`  [EXTRACTED]
  helics_sim/gridlabd_federate.py → docs/Audits/PLAN_REMEDIACION_HELICS_SENTINEL.md
- `Mock Grid Sentinel Sanitization (1 if raw == 1 else 0)` --implements--> `Paso 2: Parche en helics_sim/fed_gridmock.py`  [EXTRACTED]
  helics_sim/fed_gridmock.py → docs/Audits/PLAN_REMEDIACION_HELICS_SENTINEL.md
- `Fase 3: Co-Simulación Dinámica C-API & OVS SPAN Zeek` --conceptually_related_to--> `HELICS 3.4.0 網實聯動 (8 Federates + Physical Plants)`  [INFERRED]
  docs/Audits/PLAN_ALTA_FIDELIDAD_DIGITAL_TWIN.md → docs/Roadmaps/PROMPT_AUDITOR.md
- `Fase 3: Física No Lineal C-API (EPANET/GridLAB-D) & OVS SPAN Zeek/Suricata` --rationale_for--> `HELICS 3.4.0 網實聯動 (8 Federates + Physical Plants)`  [INFERRED]
  docs/Audits/PLAN_ALTA_FIDELIDAD_DIGITAL_TWIN.md → docs/Roadmaps/PROMPT_AUDITOR.md
- `Causa Raíz: HELICS INT64_MIN (-9223372036854775808)` --conceptually_related_to--> `HELICS 3.4.0 網實聯動 (8 Federates + Physical Plants)`  [INFERRED]
  docs/Audits/PLAN_REMEDIACION_HELICS_SENTINEL.md → docs/Roadmaps/PROMPT_AUDITOR.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Industrial Cyber Range Audit Verification Protocol** — docs_roadmaps_prompt_auditor_paso_0_baseline, docs_roadmaps_prompt_auditor_paso_0_5_triage, docs_roadmaps_prompt_auditor_audit_goals, docs_roadmaps_prompt_auditor_hard_rules [EXTRACTED 1.00]
- **24-Point Anti-Hallucination Defect Detection Matrix** — docs_roadmaps_prompt_auditor_defects_checklist, docs_roadmaps_prompt_auditor_defect_fake_claims, docs_roadmaps_prompt_auditor_defect_ghost_code, docs_roadmaps_prompt_auditor_defect_physics_interlocks, docs_roadmaps_prompt_auditor_defect_fake_tech [EXTRACTED 1.00]
- **CityLab IEC 62443 Cyber Range Architecture Model** — docs_roadmaps_prompt_auditor_network_iec62443_zones, docs_roadmaps_prompt_auditor_plc_emulators, docs_roadmaps_prompt_auditor_helics_cosimulation, docs_roadmaps_prompt_auditor_scada_defense_stack, docs_roadmaps_prompt_auditor_attack_scenarios [EXTRACTED 1.00]

## Communities (7 total, 0 thin omitted)

### Community 0 - "Industrial Digital Twin & High Fidelity"
Cohesion: 0.32
Nodes (8): Criterios de Aceptación (Raw 0x88B8 / Impacket TGS / EPANET C-API), Matriz de Transición Arquitectónica (Maqueta vs Digital Twin), 🏗️ Roadmap Alta Fidelidad Industrial y Gemelo Digital, Fase 2: Samba 4 AD DC & Autenticación GSSAPI/Kerberos, Fase 2: Samba 4 AD DC & KDC Kerberos Real (Kerberoasting auténtico), Fase 3: Física No Lineal C-API (EPANET/GridLAB-D) & OVS SPAN Zeek/Suricata, 缺陷模式 #8/#9: 死常數 doc 誑真機 / 偽造 JWT 等技名, 守勢防禦 Stack (SCADA HA/Historian/SIEM/SDN)

### Community 1 - "HELICS Remediation & Physics Fixes"
Cohesion: 0.43
Nodes (7): Protocolo de Validación (smoke_test_local & 241 tests), 稽核目標 (實證狀態/全鏈驗證/Sudo e2e/回歸), 🛡️ 稽核者提示 — CityLab Cyber Range (IEC 62443), 金律 — 蓄意之弱點 (F-03/05/06/07 CTF), 硬律 (碼勝於文/不閉CTF/Sudo親跑/不移物理閾值), PASO 0 — 基準 (HEAD/151 Tests/Sudo e2e/Topology), 文言極簡格式規範 (wenyan-ultra / 確引數據 / 禁裝飾)

### Community 2 - "IEC 62443 Architecture & Defense"
Cohesion: 0.33
Nodes (6): Fase 1: OpenPLC v3 & libiec61850 Native Daemons, Fase 1: OpenPLC v3 (ST/LD) & Stacks Nativos L2 (libiec61850/libdnp3), 攻防情境驗證 (29 Docs & Scenarios vs Real Code), IEC 62443 五區拓撲 (Corporate/DMZ/OT/EWS/Honeypot), PLC Daemons & Protocols (Modbus/DNP3/IEC61850/OPC UA), 已驗之架構 (5 Zones/PLC/HELICS/SCADA/29 Attacks)

### Community 3 - "HELICS Remediation & Physics Fixes"
Cohesion: 0.50
Nodes (4): 🛠️ Plan de Remediación HELICS Sentinel (Hallazgo 01), Especificación de Sanitización (t == 1 & double < -1e20), Paso 2: Parche en helics_sim/fed_gridmock.py, Mock Grid Sentinel Sanitization (1 if raw == 1 else 0)

### Community 4 - "HELICS Remediation & Physics Fixes"
Cohesion: 0.50
Nodes (4): Paso 1: Parche en helics_sim/gridlabd_federate.py, 缺陷模式 #16/#17: 物理不可達死連鎖 / 哨兵值偽綠, GridLAB-D Sentinel Sanitization (t == 1 & double < -1e20), Unit Tests: TestSentinelSanitization (4/4 PASS)

### Community 5 - "Co-simulation & Interlock Defects"
Cohesion: 0.50
Nodes (4): 缺陷模式 #12/#21: 確引行號而檔未觸 / 舊碼冒新, 缺陷模式 #11/#13/#14: 文載為活未起 / 死檔 / Handle 未用, 已知缺陷 Checklist (24 抗偽稽核模式), PASO 0.5 — Build 報之分診 (Git Diff/Log/Grep)

### Community 6 - "Industrial Digital Twin & High Fidelity"
Cohesion: 0.67
Nodes (3): Fase 3: Co-Simulación Dinámica C-API & OVS SPAN Zeek, Causa Raíz: HELICS INT64_MIN (-9223372036854775808), HELICS 3.4.0 網實聯動 (8 Federates + Physical Plants)

## Knowledge Gaps
- **5 isolated node(s):** `IEC 62443 五區拓撲 (Corporate/DMZ/OT/EWS/Honeypot)`, `攻防情境驗證 (29 Docs & Scenarios vs Real Code)`, `Especificación de Sanitización (t == 1 & double < -1e20)`, `Matriz de Transición Arquitectónica (Maqueta vs Digital Twin)`, `Criterios de Aceptación (Raw 0x88B8 / Impacket TGS / EPANET C-API)`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `已驗之架構 (5 Zones/PLC/HELICS/SCADA/29 Attacks)` connect `IEC 62443 Architecture & Defense` to `Industrial Digital Twin & High Fidelity`, `HELICS Remediation & Physics Fixes`, `Industrial Digital Twin & High Fidelity`?**
  _High betweenness centrality (0.312) - this node is a cross-community bridge._
- **Why does `🛡️ 稽核者提示 — CityLab Cyber Range (IEC 62443)` connect `HELICS Remediation & Physics Fixes` to `IEC 62443 Architecture & Defense`, `Co-simulation & Interlock Defects`?**
  _High betweenness centrality (0.310) - this node is a cross-community bridge._
- **Why does `HELICS 3.4.0 網實聯動 (8 Federates + Physical Plants)` connect `Industrial Digital Twin & High Fidelity` to `Industrial Digital Twin & High Fidelity`, `IEC 62443 Architecture & Defense`, `HELICS Remediation & Physics Fixes`, `Co-simulation & Interlock Defects`?**
  _High betweenness centrality (0.305) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `HELICS 3.4.0 網實聯動 (8 Federates + Physical Plants)` (e.g. with `Fase 3: Co-Simulación Dinámica C-API & OVS SPAN Zeek` and `Fase 3: Física No Lineal C-API (EPANET/GridLAB-D) & OVS SPAN Zeek/Suricata`) actually correct?**
  _`HELICS 3.4.0 網實聯動 (8 Federates + Physical Plants)` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `IEC 62443 五區拓撲 (Corporate/DMZ/OT/EWS/Honeypot)`, `攻防情境驗證 (29 Docs & Scenarios vs Real Code)`, `Especificación de Sanitización (t == 1 & double < -1e20)` to the rest of the system?**
  _5 weakly-connected nodes found - possible documentation gaps or missing edges._