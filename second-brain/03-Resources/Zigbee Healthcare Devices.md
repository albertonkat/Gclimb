---
created: 2026-06-08
tags: [zigbee, healthcare, devices, reference]
---

# Zigbee Healthcare Devices

Reference for Zigbee-based healthcare and wellness devices compatible with SmartThings.

## Device Categories

### Vital Sign Monitors
- **Pulse oximeters** — Masimo, Nonin (Zigbee Health Care profile 0x0108)
- **Blood pressure** — A&D Medical UA-651BLE (BLE bridge to Zigbee hub)
- **Glucose monitors** — Dexcom G7 (BLE), Contour Next (USB bridge); Zigbee direct rare

### Environmental Monitoring
- **Air quality (CO2, VOC, PM2.5)** — Aqara TVOC sensor, Xiaomi Mijia
- **Temperature/Humidity** — Aqara TH, Sonoff SNZB-02
- **Smart thermostats** — Centralite, Stelpro (relevant for patient comfort)

### Fall Detection / Presence
- **Motion sensors** — Aqara P1, SmartThings Motion Sensor (Zigbee HA profile)
- **Contact sensors** — used for bed exit, door open monitoring
- **Pressure mats** — Emfit QS (Wi-Fi), ŌURA ring (BLE)

### Medication Management
- **Door/cabinet sensors** — any Zigbee contact sensor on med cabinet
- **Smart buttons** — Ikea TRÅDFRI button, Aqara D1 — trigger medication reminders

## Zigbee Fingerprint Format

SmartThings identifies Zigbee devices by endpoint clusters:
```groovy
fingerprint profileId: "0104", deviceId: "0402",
            inClusters:  "0000,0001,0003,0402,0500",
            outClusters: "0019",
            manufacturer: "LUMI", model: "lumi.motion"
```

Key profileIds:
| Profile | ID | Purpose |
|---|---|---|
| Home Automation | 0x0104 | Most consumer devices |
| Zigbee Health Care | 0x0108 | Medical devices (blood pressure, weight) |
| Smart Energy | 0x0109 | Energy monitoring |

## Cluster IDs Relevant to Healthcare

| Cluster | Hex | Purpose |
|---|---|---|
| Basic | 0x0000 | Device info, manufacturer, model |
| Power Configuration | 0x0001 | Battery level |
| Identify | 0x0003 | Blink for pairing |
| Temperature | 0x0402 | Temperature measurement |
| Relative Humidity | 0x0405 | Humidity measurement |
| Occupancy Sensing | 0x0406 | Motion/presence |
| IAS Zone | 0x0500 | Alarm/contact sensors |
| Body Measurement | 0x0300+ | Health Care profile clusters |

## Security

Zigbee uses **AES-128** encryption at the network layer.
- Network key: shared across all devices on the hub
- Link key: device-specific (more secure for medical devices)
- Zigbee 3.0: unified security model, backward-compatible with HA

## SmartThings Integration Notes

- Use `zigbee.parseDescriptionAsMap(description)` to decode incoming messages
- `catchall` events: handle unexpected cluster data
- `read attr` events: attribute reports from device
- Healthcare profile (0x0108) requires explicit cluster handling — not auto-parsed
- Always test pairing with `zigbee.enrollResponse()` for IAS Zone devices

## Zigbee Health Care Profile (0x0108) Notes

The Zigbee Health Care profile defines clusters for:
- Blood Pressure Measurement (0x0404)
- Body Temperature (0x0401)
- Body Mass (weight) (0x0406)
- Body Fat (0x0407)

Most consumer Zigbee medical devices do NOT implement this profile — they use HA (0x0104) with proprietary clusters. Always check manufacturer documentation.

## Cross-references
- [[03-Resources/Zigbee Protocol]]
- [[02-Areas/Healthcare-IoT/Overview]]
- [[01-Projects/gclimb - Healthcare IoT Hub]]
- [[03-Resources/Z-Wave Healthcare Devices]]
