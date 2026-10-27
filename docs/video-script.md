# Four-minute demonstration script

Target: about 4 minutes, 720p or higher, MP4/MOV, within the portal's verified size limit. The user-provided brief says 80 MB; check the actual portal before export.

Do not record a concept animation as a live hardware demonstration. Use the conditional wording below according to the actual implementation.

## 0:00–0:30 — Problem

“Fixed cameras and manual patrols can leave gaps across large areas. Our Smart Surveillance Drone project explores mobile aerial monitoring with person and vehicle detection, so an authorized operator can review events sooner.”

Show a simple coverage illustration, using original graphics and no identifiable private location.

## 0:30–1:30 — Solution and architecture

“The proposed aircraft uses a Pixhawk flight controller, a Raspberry Pi and a camera. The flight controller manages aircraft control. The companion computer processes images and sends detection events to a ground dashboard. Video travels separately from the alert messages. A person or vehicle detection is a cue for human review, not proof of a threat.”

Show `architecture.md`. Clearly state which components are built and which remain proposed. If hardware is absent, say “This is currently a software/design prototype; flight integration is future work.”

## 1:30–3:30 — Actual demonstration

When software exists, record the actual application:

1. Identify whether the input is prerecorded, webcam or drone footage.
2. Show detections and their labels/confidence.
3. Show a matching dashboard event and capture timestamp.
4. Demonstrate one failure state, such as camera or network loss.
5. Present measured results with dataset size and hardware, if available.

The implemented offline demo can be recorded now: open `static/index.html`, load the sample session, inspect an event, mark it reviewed, filter the queue and export JSON. Say explicitly that these are synthetic events. Actual YOLO inference can be shown only after optional packages and trusted weights are installed and it is tested. Flight and browser video streaming are not implemented. A synthetic walkthrough does not fulfill a requirement for live hardware detection.

## 3:30–4:00 — Impact and next steps

“The intended benefits are wider monitoring coverage and faster operator awareness. We will evaluate accuracy, false alerts, end-to-end latency and payload flight time. Next steps are validating the software on authorized footage, benchmarking the selected hardware and testing flight integration in a simulator.”

Avoid invented cost savings, perfect accuracy or untested flight footage. End with the public repository URL.

## Prepared captioned walkthrough

`output/video/project-walkthrough.mp4` is a four-minute, 1280x720 silent captioned design/software explanation. Its illustrative content is labeled. It is not an actual detector/flight recording; use it as a concept walkthrough only if the portal permits that format. The script above guides the separate live demonstration once validated.
