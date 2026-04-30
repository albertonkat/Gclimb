# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Gclimb is a SmartThings repository for healthcare IoT device handlers and SmartApps. The primary goals are:
- Flat-file Groovy handlers (no legacy `.src`-nested structure)
- Clean separation between `official/` (SmartThings-certified) and `community/` (third-party) handlers
- GitHub Actions CI with CodeNarc linting on every push
- Healthcare-grade device coverage: vital sign monitors, glucose meters, fall detectors, sleep trackers, medication dispensers

## Planned Directory Layout

```
devicetypes/
  official/      # SmartThings-certified device handlers
  community/     # Community-contributed device handlers
smartapps/
  official/
  community/
.github/
  workflows/     # CI: compile + CodeNarc lint
docs/
```

Each Groovy file maps to one device type or SmartApp — no subdirectory nesting.

## Build & Lint Commands

> CI is configured via GitHub Actions. To run locally once CodeNarc is set up:

```bash
# Lint all Groovy files
./gradlew codenarcMain

# Lint a single file
./gradlew codenarcMain --include="**/MyDevice.groovy"
```

The CodeNarc ruleset lives at `config/codenarc/rules.groovy` (to be created).

## Deployment Branches

| Branch       | Environment |
|---|---|
| `main`       | Dev         |
| `staging`    | Staging     |
| `production` | Production  |

## SmartThings Groovy Patterns

### Device Handler skeleton

```groovy
metadata {
    definition(name: "Device Name", namespace: "gclimb", author: "Author",
               runLocally: true, executeCommandsLocally: true,
               minHubCoreVersion: "000.021.00001") {
        capability "TemperatureMeasurement"
        capability "Battery"
    }

    // Z-Wave fingerprint
    fingerprint mfr: "0086", prod: "0103", model: "0060", deviceJoinName: "Device Name"

    // Zigbee fingerprint
    // fingerprint profileId: "0104", inClusters: "0000,0001,0402",
    //             manufacturer: "ACME", model: "TH01", deviceJoinName: "Device Name"
}

def parse(String description) { ... }
def zwaveEvent(physicalgraph.zwave.commands.batteryv1.BatteryReport cmd) {
    def level = cmd.batteryLevel == 255 ? 1 : cmd.batteryLevel
    createEvent(name: "battery", value: level, unit: "%")
}
```

### Z-Wave secure encapsulation (S0)

```groovy
private secure(physicalgraph.zwave.Command cmd) {
    zwave.securityV1.securityMessageEncapsulation().encapsulate(cmd).format()
}
```

### Zigbee read/configure pattern

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

### Key SmartThings APIs

| Method | Context | Purpose |
|---|---|---|
| `sendEvent(name:, value:)` | Device Handler | Update device state |
| `createEvent(name:, value:)` | Device Handler | Return from `parse()` |
| `state.key = value` | Both | Persist data across calls |
| `subscribe(device, attr, handler)` | SmartApp | Listen to device events |
| `runIn(secs, method)` | SmartApp | Schedule future execution |
| `location.mode` | SmartApp | Current home mode |

Local execution requires `runLocally: true` + `executeCommandsLocally: true` in `definition()` and the handler to be whitelisted.

## Second Brain (Obsidian Vault)

`second-brain/` is a PARA-structured Obsidian vault that lives alongside the code. Keep it in sync when milestones are reached:

| Folder | Purpose |
|---|---|
| `00-Inbox/` | Capture first, file later |
| `01-Projects/` | Active work with a deadline |
| `02-Areas/` | Ongoing responsibilities |
| `03-Resources/` | Reference (protocols, APIs) |
| `05-Templates/` | Note templates |
| `07-MOCs/` | Maps of Content — index notes |

When adding a new device handler, update `second-brain/01-Projects/gclimb - Healthcare IoT Hub.md` task list and create a device note from `second-brain/05-Templates/Healthcare Device.md`.

## Healthcare Device Standards

Relevant to this project:
- **HL7 FHIR** — health data interoperability
- **IEEE 11073** — personal health device communication protocol
- **Continua Health Alliance** — interoperability guidelines for connected health devices

Protocol quick reference:
- **Z-Wave** (908.42 MHz US) — fall detectors, door/window sensors, ambient assisted living
- **Zigbee** (2.4 GHz, IEEE 802.15.4) — pulse oximeters, thermometers, environmental monitors

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
