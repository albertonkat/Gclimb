---
tags: [resource, hermes, notifications, integration, healthcare]
---

# Hermes App

## Overview
Hermes is a healthcare-focused alerting and notification platform designed to bridge IoT device events with clinicians, caregivers, and patients. Connecting the gclimb SmartThings hub to Hermes enables intelligent, HIPAA-aware messaging across care teams.

## Benefits of Connecting

### 1. Real-Time Clinical Alerts
Device events (fall detection, abnormal vitals, missed medication) are forwarded to Hermes within seconds, enabling faster clinical response compared to polling-based systems.

### 2. Multi-Channel Delivery
Hermes routes notifications through SMS, email, push, and voice — ensuring alerts reach the right person on their preferred channel without custom per-channel code in the SmartApp.

### 3. Role-Based Escalation
Unanswered alerts automatically escalate through a configurable on-call chain (patient → caregiver → nurse → physician), reducing missed events without manual follow-up logic.

### 4. HIPAA-Compliant Messaging
All messages are encrypted in transit and at rest. Hermes maintains an audit log of every notification sent, acknowledged, and escalated — satisfying CMS documentation requirements out of the box.

### 5. Threshold & Rule Engine
Clinical thresholds (e.g. SpO2 < 92%, systolic BP > 180 mmHg) can be configured in Hermes without deploying new SmartApp code, enabling non-developer care teams to tune alerting logic.

### 6. Device-Agnostic Ingestion
Hermes accepts a standard JSON event payload, so any device handler in gclimb can push to the same endpoint regardless of protocol (Z-Wave, Zigbee, LAN).

### 7. Analytics & Reporting
Aggregated event data in Hermes feeds dashboards for trend analysis, compliance reporting, and device reliability tracking — data that SmartThings alone does not retain long-term.

## Integration Pattern

```groovy
// SmartApp snippet — forward events to Hermes webhook
def deviceEventHandler(evt) {
    def payload = [
        deviceId  : evt.deviceId,
        attribute : evt.name,
        value     : evt.value,
        unit      : evt.unit,
        timestamp : evt.isoDate
    ]
    httpPostJson([
        uri  : settings.hermesWebhookUrl,
        body : payload
    ]) { resp -> log.debug "Hermes: ${resp.status}" }
}
```

## Configuration
| Setting | Description |
|---|---|
| `hermesWebhookUrl` | Hermes inbound webhook endpoint (per-tenant) |
| `hermesApiKey` | Bearer token for webhook authentication |
| `alertSeverity` | Minimum severity level to forward (`info`, `warn`, `critical`) |

## Related
- [[03-Resources/SmartThings Platform]]
- [[02-Areas/Healthcare-IoT/Overview]]
- [[01-Projects/gclimb - Healthcare IoT Hub]]
