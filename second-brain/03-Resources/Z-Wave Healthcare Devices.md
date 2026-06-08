---
created: 2026-06-08
tags: [z-wave, healthcare, devices, reference]
---

# Z-Wave Healthcare Devices

Reference for Z-Wave-based healthcare and wellness devices compatible with SmartThings.

## Device Categories

### Vital Sign Monitors
- **Blood pressure cuffs** — Z-Wave Plus, report using Basic CC or proprietary clusters
- **Pulse oximeters (SpO2)** — typically Zigbee; Z-Wave variants rare
- **Weight scales** — Withings, Omron; use Z-Wave Health CC (0x86) when available

### Fall Detection
- **Motion + accelerometer sensors** — Fibaro Motion Sensor (FGMS-001), Aeotec MultiSensor 7
- **Dedicated fall detectors** — Vayyar Home (radar-based, Z-Wave gateway), Alert1

### Medication Management
- **Smart pill dispensers** — Hero Health, MedMinder (Z-Wave gateway integration)
- **Door/drawer sensors on med cabinets** — any Z-Wave contact sensor

### Sleep Trackers
- **Under-mattress sensors** — Withings Sleep Analyzer (Wi-Fi, not Z-Wave natively)
- **Bed occupancy** — FortrezZ door sensor repurposed under mattress pad

## Z-Wave Fingerprint Format

SmartThings identifies Z-Wave devices by:
```groovy
fingerprint mfr: "0086", prod: "0002", model: "0064"
//                ^^^         ^^^           ^^^
//           Manufacturer  Product    Model (all hex)
// Profile 0x0104 = Home Automation
```

Key manufacturer IDs:
| Manufacturer | mfr hex |
|---|---|
| Aeotec (Aeon Labs) | 0x0086 |
| Fibaro | 0x010F |
| Z-Wave.Me | 0x0115 |
| Fortrezz | 0x0084 |
| Zooz | 0x027A |

## Command Classes Relevant to Healthcare

| CC | Hex | Purpose |
|---|---|---|
| Sensor Multilevel | 0x31 | Temperature, humidity, luminance |
| Notification | 0x71 | Access control, smoke, fall events |
| Battery | 0x80 | Battery level reporting |
| Wake Up | 0x84 | Battery device polling interval |
| Health | 0x86 | Blood pressure, weight (limited adoption) |
| Association | 0x85 | Direct device-to-device triggers |

## Security

Healthcare devices should use **S2 security** (Z-Wave Plus gen 2):
- S2 Authenticated (QR code pairing)
- S2 Access Control (highest — for medical)
- Legacy S0 only if S2 unavailable

## SmartThings Integration Notes

- Flat file structure: handler goes in repo root as `DeviceName.groovy`
- Simulator section required for local testing
- Use `zwaveEvent` handler pattern for command class parsing
- Always include `fingerprint` in `metadata { definition {} }` block

## Cross-references
- [[03-Resources/Z-Wave Protocol]]
- [[02-Areas/Healthcare-IoT/Overview]]
- [[01-Projects/gclimb - Healthcare IoT Hub]]
