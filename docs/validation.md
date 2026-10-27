# Validation record

Date: 2026-10-27. Core checks used Python 3.14.7 and Node.js on the build host.

| Check | Result | Scope |
| --- | --- | --- |
| Python automated suite | 13 tests passed | Event validation, bounded memory, duplicate handling, review, detector adapter and in-memory HTTP handler requests |
| JavaScript syntax | Passed | `node --check static/app.js` |
| Offline UI workflow harness | Passed | Load, inspect, review, filter, duplicate suppression and JSON export using a minimal DOM harness |
| Live HTTP integration | Passed in GitHub CI | Health, sample ingestion and event retrieval through a real local HTTP server; local build sandbox still blocks sockets |
| Browser visual QA | Blocked | Browser-control service connection returns `EPERM` |
| Actual YOLO inference | Not run | Optional packages and model weights are not installed |
| Flight integration | Not run | No aircraft connected |

The HTTP-handler tests exercise parsing/routing/responses without opening a socket. They do not prove live networking. The DOM harness exercises actual dashboard JavaScript without a rendering engine; it does not prove visual layout or browser compatibility.

Run on a normal host:

```sh
python3 -m unittest discover -s tests -v
node --check static/app.js
node scripts/test_dashboard.cjs
python3 scripts/smoke_server.py
```

Then open the dashboard at desktop and mobile sizes, navigate all controls using a keyboard, and exercise a real detector with authorized footage and a trusted model. Record model/software versions, hardware, clip provenance, detection metrics and latency separately. GitHub CI passed all checks for commit `37f239d`, including the live-server smoke test: [verified run](https://github.com/supriyachann/smart-surveillance-drone/actions/runs/40549294194).
