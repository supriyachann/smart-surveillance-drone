# Proposed architecture

## Implemented software path

```mermaid
flowchart LR
    S[Synthetic sample events] --> H[Python HTTP event service]
    V[Authorized local video or webcam] --> Y[Optional YOLO adapter]
    Y -->|Validated JSON over local HTTP| H
    Y --> P[Annotated OpenCV preview]
    H --> Q[In-memory event queue]
    Q --> D[Browser dashboard]
    D --> R[Human review and JSON export]
```

Offline mode runs the same dashboard UI with browser-memory synthetic events. The optional detector requires third-party packages and local weights; inference has not been run in the restricted build environment. The implemented software does not command an aircraft.

## Proposed aircraft integration

The components below are future hardware design, not evidence of implementation.

```mermaid
flowchart LR
    OP[Operator and mission planner] -->|Approved mission| FC[Pixhawk flight controller]
    GPS[GPS and flight sensors] --> FC
    FC --> MOT[Motors via ESCs]
    RC[Independent pilot control] --> FC
    CAM[Camera] --> PI[Raspberry Pi companion computer]
    PI --> DET[Person and vehicle detector]
    DET --> RULE[Confidence filter and event cooldown]
    RULE -->|MQTT detection events| BROKER[Authenticated ground broker]
    BROKER --> WEB[Flask dashboard service]
    PI -->|Separate video transport| WEB
    FC -->|Read-only telemetry| PI
    WEB --> DASH[Operator dashboard]
    DASH --> REVIEW[Human review and response]
```

The Pixhawk handles aircraft stabilization and configured flight failsafes. Camera processing, dashboard availability and alert delivery must not be prerequisites for maintaining stable flight. Telemetry integration and mission execution depend on the selected firmware and interface. This design does not include autonomous pursuit or identification of individuals.

## Processing flow

```mermaid
flowchart TD
    START[Start authorized monitoring session] --> CHECK[Check camera and configuration]
    CHECK --> FRAME{Frame available?}
    FRAME -->|No| STALE[Show camera unavailable; retry with bounded delay]
    STALE --> FRAME
    FRAME -->|Yes| INFER[Run object detection]
    INFER --> FILTER{Allowed class and confidence threshold met?}
    FILTER -->|No| FRAME
    FILTER -->|Yes| COOL{Outside event cooldown?}
    COOL -->|No| FRAME
    COOL -->|Yes| EVENT[Create timestamped detection event]
    EVENT --> LINK{Ground link available?}
    LINK -->|Yes| SEND[Publish event and show for human review]
    LINK -->|No| QUEUE[Retain bounded local queue; show link status]
    SEND --> FRAME
    QUEUE --> FRAME
```

An object detection is not a threat assessment. If a restricted-zone rule is added later, document the zone, authorization, false-positive behavior and test cases separately.

## Interfaces

| Path | Proposed interface | Validation required |
| --- | --- | --- |
| Camera to companion | Camera driver / OpenCV capture | Frame timestamps, resolution, dropped frames |
| Flight controller to companion | Read-only telemetry over selected MAVLink transport | Units, message age, firmware compatibility |
| Companion to ground | MQTT over TLS | Authentication, delivery, duplicate handling |
| Camera video to dashboard | Separate transport, to be selected | Bandwidth, end-to-end delay, disconnect behavior |
| Dashboard to operator | Browser UI | Stale-state visibility, event history, human review |

MQTT carries small detection events, not the primary video stream. Video protocol, storage, retention and deployment details remain implementation decisions.
