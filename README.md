# Smart Surveillance Drone

A web monitoring dashboard and Python software prototype for Smart Surveillance Drone: inspect person/vehicle events, review alerts, filter detections and export results. Aircraft integration is a proposed design and has not been flight-tested.

Repository: https://github.com/supriyachann/smart-surveillance-drone

## Web dashboard included

The project includes a working **browser dashboard**, not just documentation. Download the repository and open the [standalone dashboard file](Open%20dashboard.html) locally. It needs no installation and includes a clearly labeled synthetic sample session. The Python service and optional YOLO adapter provide the separate detector-event path.

A GitHub Pages workflow is included to publish the sample dashboard at:
https://supriyachann.github.io/smart-surveillance-drone/

Deployment setup: in repository **Settings > Pages**, select **GitHub Actions** as the publishing source, then run **Publish web dashboard** from the Actions tab if it has not already started. The URL is available after a successful deployment. The hosted site runs synthetic events in browser memory; it does not run Python, process camera input or control an aircraft.

## Implemented

- Responsive monitoring dashboard: inspect events, review alerts, filter synthetic/detector events and export JSON.
- Offline synthetic session that works by opening an HTML file.
- Python HTTP server with validated ingestion, deduplication, bounded memory and an optional ingestion token.
- Optional YOLO adapter for local video/webcam input, with an annotated OpenCV preview. Event conversion is tested; actual inference needs optional dependencies and local weights.
- Architecture, flowchart, technical design, test cases, sample data, submission draft and video script.

**No aircraft has been connected or flight-tested.** MQTT, GPS missions, browser video streaming and remote deployment authentication are future work. The illustrative scene and synthetic events are labeled. No accuracy, flight-time or cost claims have been measured.

## Quick start: no installation

Open `Open dashboard.html` in a browser (or `static/index.html` with its companion CSS/JS files). Click **Load sample events**, **Inspect**, **Mark reviewed**, then **Export events**. Offline mode uses synthetic events only and resets on reload. No server or internet connection is needed.

## Python dashboard

Use Python 3.11 or newer. Core software and tests need no external packages.

```sh
python3 app.py
```

Open http://127.0.0.1:8000. Press Ctrl+C to stop. For a different port:

```sh
python3 app.py --port 8080
```

The latest 200 events are held in memory and reset on restart. Duplicate IDs are ignored while retained. Export important events before restarting. The server binds only to loopback; it is a local prototype, not an internet-ready service.

## Optional real detection

Use Python 3.11 or 3.12 for machine-learning package compatibility:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-detector.txt
```

Supply trusted local YOLOv8-compatible weights, for example `models/yolov8n.pt`, obtained from the official provider after reviewing its license. Weights and third-party datasets are not bundled. See the [Ultralytics prediction API](https://docs.ultralytics.com/modes/predict/) and [installation guidance](https://docs.ultralytics.com/quickstart/).

Start the server in one terminal. In a second terminal, activate the same environment and run:

```sh
python detector.py --source /path/to/authorized-video.mp4 --model models/yolov8n.pt --show
```

For a webcam use `--source 0`; grant camera permission when your OS requests it. The `--show` option opens an annotated video window; press Q to stop. Dashboard events appear under **Detector events**. A prerecorded video is processed as fast as inference permits, not at guaranteed real-time speed. Event timestamps indicate when frames were read for inference, not their original recording time.

The browser projects event boxes onto an illustration. Original annotated frames appear in the detector window. Browser video streaming is not implemented. A per-class cooldown limits repeated alerts; multiple people within that interval may produce one person event. This is not object tracking or anomaly detection. On link failure, the detector stops with an error rather than silently losing events; buffering is future work.

## Environment variables

`.env.example` documents supported settings. It is not automatically loaded; export values in your shell.

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `8000` | Server/detector port; CLI takes priority |
| `DETECTION_CONFIDENCE` | `0.5` | Detector threshold |
| `ALERT_COOLDOWN_SECONDS` | `5` | Detector cooldown per class |
| `INGEST_TOKEN` | empty | Optional shared bearer token for ingestion |

If using a token, export the same value in both terminals. Never commit real tokens. Read, review and sample endpoints are local-only and unauthenticated. The ingest token does not make this a production service.

## Verification

```sh
python3 -m unittest discover -s tests -v
python3 scripts/smoke_server.py
```

The first command tests schema validation, bounded storage, the detector-result adapter and HTTP handlers using in-memory HTTP requests. The second opens a real local port for an integration check. See [validation results](docs/validation.md) for executed checks and limits. GitHub CI [passed](https://github.com/supriyachann/smart-surveillance-drone/actions/runs/40549294194), including the live-server smoke check and offline dashboard workflow. Local browser visual QA and actual model inference remain unverified.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Local service status; flight connection is false |
| GET | `/api/events` | Current event/review data |
| POST | `/api/events` | Validated ingestion; optional bearer token |
| POST | `/api/demo` | Load synthetic fixtures without duplicates |
| POST | `/api/review` | Mark `{"event_id":"..."}` reviewed |

POST requests require `Content-Type: application/json` and a body at most 16 KiB. The schema is illustrated in [sample events](data/sample-events.json).

## Project documents

- [Architecture and flow](docs/architecture.md)
- [Technical design](docs/technical-design.md)
- [Dashboard wireframe](docs/dashboard-wireframe.svg)
- [Test cases](tests/test-plan.md)
- [Sample data/provenance](data/README.md)
- [Video script](docs/video-script.md)
- [Submission draft](docs/submission.md)
- [Design PDF](output/pdf/design-document.pdf)
- [Four-minute captioned project walkthrough](output/video/project-walkthrough.mp4) - silent design/software explanation, not a live flight demonstration

## Responsible use and license

Use authorized footage and locations. Detection is a cue for human review, not proof of dangerous intent. Do not publish private footage, identifiable bystanders, GPS routes or credentials. A qualified operator and flight controller retain aircraft safety responsibilities.

Original code and documentation use the [MIT License](LICENSE). Third-party packages, datasets and weights retain their own licenses. Ultralytics has separate licensing terms; review them before combining or distributing the optional detector.

## Rebuilding presentation assets

Optional authoring scripts `scripts/create_assets.py` and `scripts/create_walkthrough.py` use Pillow, reportlab, PyMuPDF and FFmpeg. These tools are not needed to run the dashboard. The generated sample clip and walkthrough are explicitly synthetic/design material; record an actual detector/flight demonstration where the portal requires one.
