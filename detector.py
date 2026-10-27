"""Optional YOLO detector: local video/webcam -> local dashboard events."""
import argparse
import json
import math
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from app import LABELS


def events_from_result(result, source_id, captured_at):
    """Convert a YOLO Results object to the dashboard's normalized event schema."""
    if result.boxes is None:
        return
    for box in result.boxes:
        label = result.names[int(box.cls[0])]
        if label not in LABELS:
            continue
        yield {
            'schema_version': 1, 'event_id': str(uuid.uuid4()),
            'timestamp': captured_at, 'source_id': source_id,
            'label': label, 'confidence': float(box.conf[0]),
            'bbox_normalized': [max(0.0, min(1.0, float(n))) for n in box.xyxyn[0]],
            'synthetic': False,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, help='Local video/image path, or webcam number such as 0')
    parser.add_argument('--model', required=True, help='Path to trusted local YOLO weights')
    parser.add_argument('--source-id', default='local-camera', help='Non-sensitive camera alias')
    parser.add_argument('--port', type=int, default=int(os.getenv('PORT', '8000')))
    parser.add_argument('--confidence', type=float, default=float(os.getenv('DETECTION_CONFIDENCE', '.5')))
    parser.add_argument('--cooldown', type=float, default=float(os.getenv('ALERT_COOLDOWN_SECONDS', '5')))
    parser.add_argument('--show', action='store_true', help='Show annotated frames in an OpenCV window')
    args = parser.parse_args()
    if not math.isfinite(args.confidence) or not math.isfinite(args.cooldown) or not 0 <= args.confidence <= 1 or args.cooldown < 0:
        parser.error('Confidence must be in [0,1] and cooldown must be nonnegative')
    if not Path(args.model).is_file():
        parser.error('Supply a trusted local model file; weights are not included')
    if not args.source.isdecimal() and not Path(args.source).is_file():
        parser.error('Source must be an existing local file or a webcam number')
    try:
        import cv2
        from ultralytics import YOLO
    except ImportError:
        parser.exit(1, 'Install optional packages: python -m pip install -r requirements-detector.txt\n')
    model = YOLO(args.model)
    capture = cv2.VideoCapture(int(args.source) if args.source.isdecimal() else args.source)
    if not capture.isOpened():
        parser.exit(1, 'Could not open input source\n')
    last_sent = {}
    sent = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                print('Input ended or became unavailable. No further events will be sent.')
                break
            captured_at = datetime.now(timezone.utc).isoformat()
            result = model.predict(frame, conf=args.confidence, verbose=False)[0]
            for event in events_from_result(result, args.source_id, captured_at):
                now = time.monotonic()
                if now - last_sent.get(event['label'], -float('inf')) < args.cooldown:
                    continue
                headers = {'Content-Type': 'application/json'}
                token = os.getenv('INGEST_TOKEN', '')
                if token:
                    headers['Authorization'] = f'Bearer {token}'
                request = Request(f'http://127.0.0.1:{args.port}/api/events', json.dumps(event).encode(), headers)
                try:
                    with urlopen(request, timeout=3) as response:
                        response.read()
                    last_sent[event['label']] = now
                    sent += 1
                except URLError:
                    parser.exit(1, 'Dashboard rejected the event or is unavailable. Check server, port and token.\n')
            if args.show:
                cv2.imshow('Authorized source - YOLO detections; Q to exit', result.plot())
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        capture.release()
        cv2.destroyAllWindows()
        print(f'Detector stopped. {sent} events sent. No flight commands were issued.')


if __name__ == '__main__':
    main()
