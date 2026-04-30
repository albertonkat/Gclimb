# Graph Report - .  (2026-04-30)

## Corpus Check
- Corpus is ~2,304 words - fits in a single context window. You may not need a graph.

## Summary
- 43 nodes · 85 edges · 12 communities detected
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Device Protocols & Handlers|Device Protocols & Handlers]]
- [[_COMMUNITY_Gclimb Project & CI|Gclimb Project & CI]]
- [[_COMMUNITY_Healthcare IoT Knowledge|Healthcare IoT Knowledge]]
- [[_COMMUNITY_Health Standards & Devices|Health Standards & Devices]]
- [[_COMMUNITY_Second Brain & PARA|Second Brain & PARA]]
- [[_COMMUNITY_SmartApps & Platform|SmartApps & Platform]]
- [[_COMMUNITY_SmartThings Dev Area|SmartThings Dev Area]]
- [[_COMMUNITY_Meeting Notes|Meeting Notes]]
- [[_COMMUNITY_Project Templates|Project Templates]]
- [[_COMMUNITY_MOC Templates|MOC Templates]]
- [[_COMMUNITY_Fleeting Notes|Fleeting Notes]]
- [[_COMMUNITY_Daily Notes|Daily Notes]]

## God Nodes (most connected - your core abstractions)
1. `Gclimb SmartThings Healthcare IoT Project` - 17 edges
2. `Healthcare IoT Area` - 11 edges
3. `Healthcare IoT MOC` - 10 edges
4. `Z-Wave Protocol Resource` - 9 edges
5. `gclimb Healthcare IoT Hub Project` - 9 edges
6. `Z-Wave Protocol` - 8 edges
7. `Second Brain Home Dashboard` - 8 edges
8. `SmartThings MOC` - 6 edges
9. `Resources MOC` - 6 edges
10. `Zigbee Protocol Resource` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Ambient Assisted Living (AAL)` --semantically_similar_to--> `Remote Patient Monitoring`  [INFERRED] [semantically similar]
  CLAUDE.md → second-brain/07-MOCs/Healthcare IoT MOC.md
- `Gclimb SmartThings Healthcare IoT Project` --references--> `Gclimb Repository`  [INFERRED]
  CLAUDE.md → README.md
- `Gclimb SmartThings Healthcare IoT Project` --conceptually_related_to--> `gclimb Healthcare IoT Hub Project`  [INFERRED]
  CLAUDE.md → second-brain/01-Projects/gclimb - Healthcare IoT Hub.md
- `Zigbee Protocol` --conceptually_related_to--> `Zigbee Protocol Resource`  [INFERRED]
  CLAUDE.md → second-brain/03-Resources/Zigbee Protocol.md
- `Healthcare IoT Area` --references--> `Glucose Meter Device`  [EXTRACTED]
  second-brain/02-Areas/Healthcare-IoT/Overview.md → CLAUDE.md

## Hyperedges (group relationships)
- **Healthcare IoT Integration Stack** — claude_device_handler, resource_zwave_protocol, resource_zigbee_protocol, resource_smartthings_platform [INFERRED 0.88]
- **Healthcare Standards Compliance Framework** — claude_hl7_fhir, claude_ieee11073, claude_continua [INFERRED 0.82]
- **Gclimb Knowledge Management System** — claude_second_brain, home_para, template_healthcare_device, project_gclimb_hub [EXTRACTED 0.90]

## Communities

### Community 0 - "Device Protocols & Handlers"
Cohesion: 0.42
Nodes (9): Ambient Assisted Living (AAL), SmartThings Device Handler, Fall Detector Device, Zigbee Protocol, Z-Wave Protocol, Z-Wave S0 Secure Encapsulation, Z-Wave COMMAND_CLASS_SECURITY, Z-Wave Protocol Resource (+1 more)

### Community 1 - "Gclimb Project & CI"
Cohesion: 0.33
Nodes (7): CodeNarc Groovy Linting, Gclimb SmartThings Healthcare IoT Project, GitHub Actions CI, Glucose Meter Device, Medication Dispenser Device, Sleep Tracker Device, Gclimb Repository

### Community 2 - "Healthcare IoT Knowledge"
Cohesion: 0.47
Nodes (6): Remote Patient Monitoring, Healthcare IoT MOC, Resources MOC, Zigbee Healthcare Devices, Zigbee Protocol Resource, Z-Wave Healthcare Devices

### Community 3 - "Health Standards & Devices"
Cohesion: 0.6
Nodes (5): Healthcare IoT Area, Continua Health Alliance, HL7 FHIR, IEEE 11073, Vital Sign Monitor Device

### Community 4 - "Second Brain & PARA"
Cohesion: 0.67
Nodes (4): Second Brain Obsidian Vault, PARA Method, Second Brain Home Dashboard, Inbox

### Community 5 - "SmartApps & Platform"
Cohesion: 0.5
Nodes (4): SmartApp, Projects MOC, gclimb Healthcare IoT Hub Project, SmartThings Platform Resource

### Community 6 - "SmartThings Dev Area"
Cohesion: 0.67
Nodes (3): SmartThings Development Area, Areas MOC, SmartThings MOC

### Community 7 - "Meeting Notes"
Cohesion: 1.0
Nodes (1): Meeting Note Template

### Community 8 - "Project Templates"
Cohesion: 1.0
Nodes (1): Project Template

### Community 9 - "MOC Templates"
Cohesion: 1.0
Nodes (1): MOC Template

### Community 10 - "Fleeting Notes"
Cohesion: 1.0
Nodes (1): Fleeting Note Template

### Community 11 - "Daily Notes"
Cohesion: 1.0
Nodes (1): Daily Note Template

## Knowledge Gaps
- **7 isolated node(s):** `Gclimb Repository`, `Meeting Note Template`, `Project Template`, `MOC Template`, `Fleeting Note Template` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Meeting Notes`** (1 nodes): `Meeting Note Template`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Project Templates`** (1 nodes): `Project Template`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `MOC Templates`** (1 nodes): `MOC Template`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Fleeting Notes`** (1 nodes): `Fleeting Note Template`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Daily Notes`** (1 nodes): `Daily Note Template`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Gclimb SmartThings Healthcare IoT Project` connect `Gclimb Project & CI` to `Device Protocols & Handlers`, `Health Standards & Devices`, `Second Brain & PARA`, `SmartApps & Platform`?**
  _High betweenness centrality (0.274) - this node is a cross-community bridge._
- **Why does `Healthcare IoT MOC` connect `Healthcare IoT Knowledge` to `Device Protocols & Handlers`, `Health Standards & Devices`, `Second Brain & PARA`, `SmartApps & Platform`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Why does `Healthcare IoT Area` connect `Health Standards & Devices` to `Device Protocols & Handlers`, `Gclimb Project & CI`, `Healthcare IoT Knowledge`, `SmartApps & Platform`, `SmartThings Dev Area`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Gclimb SmartThings Healthcare IoT Project` (e.g. with `Gclimb Repository` and `gclimb Healthcare IoT Hub Project`) actually correct?**
  _`Gclimb SmartThings Healthcare IoT Project` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Gclimb Repository`, `Meeting Note Template`, `Project Template` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._