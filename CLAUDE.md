# CLAUDE.md — Gclimb Healthcare IoT Hub

## What This Repo Is
SmartThings device handlers and SmartApps for healthcare IoT devices. The goal is a clean, flat-file structure (no legacy `.src` nesting) with CI and linting from day one.

Primary protocols: **Z-Wave** (908.42 MHz US) and **Zigbee** (IEEE 802.15.4, 2.4 GHz).
Language: **Groovy** (SmartThings Groovy DSL).

---

## Folder Structure
```
devicetypes/
  official/     # Handlers vetted and tested by the core team
  community/    # Community-contributed handlers (lower stability bar)
smartapps/
  official/
  community/
docs/           # Extended documentation
second-brain/   # Obsidian knowledge vault — not deployed, context only
```

---

## Common Commands

| Task | Command |
|---|---|
| Lint all Groovy files | `./gradlew codenarc` |
| Compile check | `./gradlew compileGroovy` |
| Run all checks (CI equivalent) | `./gradlew check` |

CI runs on every push via GitHub Actions (`.github/workflows/`).

---

## Device Handler Conventions

### File structure (in order)
```groovy
metadata {
    definition(name:, namespace:, author:, ocfDeviceType:) {
        capability "..."
        attribute  "...", "string"
        command    "..."
        fingerprint mfr: "XXXX", prod: "XXXX", model: "XXXX", deviceJoinName: "..."
    }
    tiles { ... }
}

def installed()  { configure() }
def updated()    { configure() }
def configure()  { /* send config commands, return cmd list */ }
def parse(String description) { /* dispatch to zwaveEvent/zigbee helpers */ }
// zwaveEvent() overloaded per command class
// zigbee cluster handlers as needed
```

### Z-Wave patterns
```groovy
// Battery report
def zwaveEvent(physicalgraph.zwave.commands.batteryv1.BatteryReport cmd) {
    def level = cmd.batteryLevel == 255 ? 1 : cmd.batteryLevel
    createEvent(name: "battery", value: level, unit: "%")
}

// S0 secure encapsulation
private secure(physicalgraph.zwave.Command cmd) {
    zwave.securityV1.securityMessageEncapsulation().encapsulate(cmd).format()
}
```

### Zigbee patterns
```groovy
import physicalgraph.zigbee.zcl.DataType

def refresh() {
    zigbee.readAttribute(0x0402, 0x0000) +  // temperature
    zigbee.readAttribute(0x0001, 0x0020)     // battery voltage
}

def configure() {
    zigbee.configureReporting(0x0402, 0x0000, DataType.INT16, 30, 3600, 50)
}
```

---

## SmartApp Conventions

```groovy
definition(name:, namespace:, author:, description:, iconUrl:, iconX2Url:) { ... }

preferences { section { input ... } }

def installed()  { initialize() }
def updated()    { unsubscribe(); initialize() }
def initialize() { subscribe(device, "attribute", handlerMethod) }
```

Always call `unsubscribe()` before re-subscribing in `updated()` to avoid duplicate handlers.

---

## Healthcare Device Categories
- Vital sign monitors — blood pressure, SpO2, heart rate
- Glucose monitors
- Fall detectors (Z-Wave motion/accelerometer)
- Sleep trackers
- Medication dispensers

---

## Integrations

### Hermes (notification platform)
Forward device events to Hermes via webhook for HIPAA-compliant alerting and escalation.
See `second-brain/03-Resources/Hermes App.md` for full details and integration snippet.

Required SmartApp settings:
- `hermesWebhookUrl` — per-tenant inbound endpoint
- `hermesApiKey` — bearer token
- `alertSeverity` — `info | warn | critical`

---

## Healthcare Standards Context
- **HL7 FHIR** — data interoperability for health records
- **IEEE 11073** — personal health device communication
- **Continua Health Alliance** — device interoperability guidelines

These inform data modeling in SmartApps but are not enforced by the SmartThings platform itself.

---

## Key Groovy/SmartThings Gotchas
- `state` persists across executions but is a simple map — don't store large objects
- `sendEvent` fires immediately; `createEvent` returns a map for `parse()` to return
- Device handlers run on the hub (local execution) only when whitelisted by SmartThings
- `runIn` scheduling is approximate (±seconds); don't use for precise clinical timing
- Always return a list from `configure()` even if it's a single command: `[cmd.format()]`

---

## Second-Brain Vault
`second-brain/` is an Obsidian vault for project knowledge — not deployed code.
Useful files:
- `03-Resources/SmartThings Platform.md` — API quick-reference
- `03-Resources/Z-Wave Protocol.md` — command classes, fingerprint format
- `03-Resources/Zigbee Protocol.md` — cluster IDs, helper patterns
- `03-Resources/Hermes App.md` — notification integration
- `01-Projects/gclimb - Healthcare IoT Hub.md` — task tracker and goals
