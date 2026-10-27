# Test cases

Hardware/model cases below remain planned. The automated core and HTTP-handler suite has 13 passing tests; see `docs/validation.md` for exact scope. Update acceptance results only after running the corresponding integration scenario.

| ID | Input / trigger | Expected behavior | Result |
| --- | --- | --- | --- |
| T01 | Authorized labeled person/vehicle clip | Valid boxes/classes; record precision and recall | Not run |
| T02 | Clip without target classes | Count false alerts; no assumed perfect score | Not run |
| T03 | Detection below confidence threshold | Event filtered | Not run |
| T04 | Repeated detections during cooldown | Rate limited according to documented rule | Not run |
| T05 | Camera disconnect or corrupt video | Visible unavailable state; bounded retry | Not run |
| T06 | Broker disconnect and reconnect | Bounded queue; retry; historical events labeled | Not run |
| T07 | Same event delivered twice | One dashboard entry for the same event ID | Automated store/handler check passed |
| T08 | Invalid JSON, label, confidence or box | Event rejected; service remains available | Schema/handler checks passed for covered malformed objects; live server pending |
| T09 | Telemetry stops updating | Last timestamp and stale status shown | Not run |
| T10 | Real capture-to-render timestamps | Record latency median and p95 with sample count | Not run |
| T11 | Sustained inference on target compute | Record FPS, dropped frames, temperature and power | Not run |
| T12 | Companion offline in flight simulator | Configured flight-controller failsafe behavior verified | Not run |
| T13 | Missing ingestion token / cross-origin mutation | Protected ingestion or mutation rejected | Handler checks passed; read/review endpoints are local and unauthenticated |
| T14 | Synthetic sample loaded | Demo label visible; excluded from evaluation metrics | DOM workflow check passed; browser visual QA pending |

## Result record

For each executed case record: date, commit, hardware, software/model versions, input provenance, exact steps, expected/actual outcome, pass/fail, and evidence path. An empty result is not a pass. Do not use a real aircraft to test failure behavior before simulator validation and a qualified safety review.
