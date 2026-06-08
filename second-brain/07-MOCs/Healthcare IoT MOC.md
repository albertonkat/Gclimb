---
tags: [moc, healthcare, iot]
---

# Healthcare IoT MOC

## Projects
- [[01-Projects/gclimb - Healthcare IoT Hub]]

## Devices
- [[03-Resources/Z-Wave Healthcare Devices]]
- [[03-Resources/Zigbee Healthcare Devices]]

## Protocols
- [[03-Resources/Z-Wave Protocol]]
- [[03-Resources/Zigbee Protocol]]

## Areas
- [[02-Areas/Healthcare-IoT/Overview]]

## Key Concepts
- Remote patient monitoring (RPM)
- Vital sign sensors — heart rate, SpO2, blood pressure, glucose
- Medication adherence tracking and smart dispensers
- Fall detection — passive IR, accelerometer, radar (Vayyar)
- Ambient assisted living (AAL) — sleep, activity, presence

## Standards & Interoperability
- **HL7 FHIR** — health data format and API standard for data exchange
- **IEEE 11073** — personal health device communication (PHD)
- **Continua Health Alliance** — end-to-end interoperability guidelines
- **Zigbee Health Care profile (0x0108)** — Zigbee cluster standard for medical devices

## Open Questions
- Which vital sign monitor should be the first device handler? (glucose vs blood pressure)
- How to map IEEE 11073 PHD data observations into FHIR Observation resources?
- Is S2 security mandatory for SmartThings healthcare handlers, or is S0 acceptable?
- Can SmartThings Cloud-to-Cloud integration reach Dexcom / Withings APIs directly?

## Sessions
- [[06-Sessions/]] — all agent sessions tagged with healthcare topics

## Related Resources
- [[03-Resources/agent-guide]] — how agents navigate and write to this vault
- [[03-Resources/past-data-import]] — how to import past Hermes/Claude.ai sessions
