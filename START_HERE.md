# Open the project

1. Open `Open dashboard.html` in a browser.
2. Choose **Load sample events**.
3. Choose **Inspect**, then **Mark reviewed** on an event.
4. Filter to **Needs review**, then choose **Export events**.

This standalone mode runs without installation or a local server and uses labeled synthetic data.

For the Python service or optional YOLO video/webcam adapter, follow README.md.

## Prepared uploads

- `output/pdf/design-document.pdf`: four-page design document with architecture, flow and wireframe.
- `output/video/project-walkthrough.mp4`: four-minute silent, captioned 720p design/software walkthrough, about 1.1 MB. It is not a recording of a real detector or flight and must not be submitted as proof of a live hardware demo.
- `data/synthetic-scene.png` and `data/synthetic-scene.mp4`: original synthetic fixtures, not real detection data.
- `docs/submission.md`: title, theme suggestion, SDG alignment, statements and remaining checklist.

## Repository and future updates

The project is published at:
https://github.com/supriyachann/smart-surveillance-drone

Future updates must be published using an account with write access to this repository. Keep `.env`, private recordings and credentials out of commits. Do not upload only the ZIP: preserve source files and folders.

## Work requiring real-world evidence

Run actual YOLO inference with trusted weights and authorized footage, complete live-server/browser checks on a normal host, and validate aircraft integration before making performance or flight claims. Obtain the real institutional signatures and stamp on the portal's exact declaration template. A generated walkthrough cannot substitute for those requirements.
