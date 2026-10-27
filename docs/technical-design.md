# Technical design

## 1. Scope and status

Proposed prototype for authorized monitoring with person and vehicle detection. The dashboard, local HTTP event service, offline synthetic mode and optional YOLO adapter are implemented. Hardware integration, GPS missions and browser video streaming remain pending. The adapter has been tested with a model-result fixture; actual inference remains unverified. There are no measured performance or cost claims.

## 2. Proposed components

| Component | Responsibility | Open decision |
| --- | --- | --- |
| Pixhawk | Stabilization, mission execution and flight failsafes | Board, firmware and tested configuration |
| Raspberry Pi | Camera capture and companion processing | Model, cooling, power budget and inference feasibility |
| Camera | Video frames | Interface, field of view and image resolution |
| Detector | Person / vehicle bounding boxes | Model version, license, confidence and benchmark |
| MQTT broker | Small event delivery | Deployment, TLS and account configuration |
| Flask service | Receive events and serve dashboard | Authentication, persistence and video protocol |
| Browser dashboard | Video, status and human alert review | Implement from the supplied wireframe |

Python, OpenCV and a YOLO-family detector are candidate tools. The submission draft mentions YOLOv8, but dependencies and model licensing must be confirmed against the actual implementation before installation or distribution.

## 3. Detection event contract

See `data/sample-events.json` for synthetic examples. Suggested fields:

- `schema_version`: integer, initially 1.
- `event_id`: unique stable identifier; use it to deduplicate retries.
- `timestamp`: UTC capture time in ISO 8601 format.
- `source_id`: non-sensitive camera alias, not a private location.
- `label`: allowed model class such as `person` or `car`.
- `confidence`: number in [0, 1]; not a probability of danger.
- `bbox_normalized`: `[x_min, y_min, x_max, y_max]` in [0, 1], with increasing corners.
- `synthetic`: true for supplied examples; exclude these from measured results.

Validate payload size, types, timestamps, allowed classes and coordinates. Reject malformed events. Preserve capture time when retrying; show delayed events as historical, not live.

## 4. Implemented configuration and transport

The working prototype uses Python's standard-library HTTP server, not Flask or MQTT. It polls events every two seconds, keeps the latest 200 events in memory and supports per-event review and JSON export. The detector posts validated JSON to the loopback server. It stops on delivery failure; a retry queue has not been implemented.

Supported environment variables are `PORT`, `DETECTION_CONFIDENCE`, `ALERT_COOLDOWN_SECONDS` and optional `INGEST_TOKEN`. Exact defaults and commands are in README.md and `.env.example`. The latter is documentation only: export variables in the shell. No camera source or model-path environment variable is implemented; use CLI arguments.

Core software has no external dependencies. Optional detector packages are listed with compatibility ranges in `requirements-detector.txt`; this is not a locked or hardware-benchmarked environment. No weights are distributed. Remote broker/TLS/authenticated dashboard deployment remain future work.

## 5. Dashboard behavior

The implemented dashboard displays service availability and a reviewable event list. Its scene is explicitly an illustration, with normalized boxes for selected events. It does not display a live camera stream. Future streaming should show camera availability, update timestamps and freshness. Telemetry is always shown as unavailable in this prototype. Distinguish demo data from live data on every screen. Do not show invented battery, GPS or flight values. Dashboard wireframe is a design illustration only.

## 6. Failure handling

- Current detector: stops when input ends or becomes unavailable; no stale frame is presented as live in the browser.
- Current HTTP delivery failure: detector exits with an error. Future ground-link integration needs a bounded queue, retries and event expiry.
- Duplicate delivery: deduplicate by event ID.
- Inference overload: measure processing rate; reduce load or change compute design.
- Companion failure: flight controller retains configured stabilization and failsafes.
- Stale telemetry: label it stale and display its last timestamp.

Exact flight failsafe behavior must be configured and validated with the selected firmware in a simulator and controlled tests. This document does not certify flight readiness.

## 7. Evaluation

Record model, hardware, resolution, dataset split and test conditions with every result. Use held-out, manually labeled footage. Report precision and recall by class with counts; report false alerts per minute, capture-to-dashboard latency (median and p95), processing FPS and dropped frames. Measure flight duration separately with the actual payload and battery. Leave results as **not measured** until evidence exists.

## 8. Privacy and release

Collect the minimum footage needed with permission. Prefer non-identifiable scenes. Keep original recordings private unless publication is authorized. Strip GPS and identifying metadata from shared samples. Use authenticated TLS connections and short retention. Confirm third-party asset and model licenses before release.
