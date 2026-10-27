"""Local monitoring demo. Run with Python 3.11+; no packages needed."""
import argparse
import json
import math
import os
import threading
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
LABELS = {'person', 'car', 'truck', 'bus', 'motorcycle', 'bicycle'}


def validate_event(value):
    if not isinstance(value, dict):
        raise ValueError('Event must be a JSON object')
    for key in ('event_id', 'source_id'):
        if not isinstance(value.get(key), str) or not 1 <= len(value[key]) <= 100:
            raise ValueError(f'{key} must be a nonempty string of at most 100 characters')
    if not isinstance(value.get('label'), str) or value['label'] not in LABELS:
        raise ValueError('Unsupported detection label')
    confidence = value.get('confidence')
    if type(confidence) not in (int, float) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError('Confidence must be between 0 and 1')
    box = value.get('bbox_normalized')
    if not isinstance(box, list) or len(box) != 4 or any(
        type(n) not in (int, float) or not math.isfinite(n) or not 0 <= n <= 1 for n in box
    ) or box[0] >= box[2] or box[1] >= box[3]:
        raise ValueError('Bounding box must contain increasing normalized corners')
    if type(value.get('synthetic')) is not bool:
        raise ValueError('synthetic must be true or false')
    if type(value.get('schema_version')) is not int or value['schema_version'] != 1:
        raise ValueError('schema_version must be 1')
    try:
        timestamp = datetime.fromisoformat(value['timestamp'].replace('Z', '+00:00'))
        if timestamp.tzinfo is None or timestamp.utcoffset().total_seconds() != 0:
            raise ValueError()
    except (KeyError, TypeError, AttributeError, ValueError):
        raise ValueError('timestamp must be an ISO 8601 UTC time') from None
    return {key: value[key] for key in (
        'schema_version', 'event_id', 'timestamp', 'source_id', 'label',
        'confidence', 'bbox_normalized', 'synthetic'
    )}


class EventStore:
    def __init__(self, limit=200):
        self.events = deque(maxlen=limit)
        self.lock = threading.Lock()

    def add(self, event):
        clean = validate_event(event)
        with self.lock:
            if any(item['event_id'] == clean['event_id'] for item in self.events):
                return False
            clean.update(reviewed=False, received_at=datetime.now(timezone.utc).isoformat())
            self.events.appendleft(clean)
        return True

    def list(self):
        with self.lock:
            return [dict(event) for event in self.events]

    def review(self, event_id):
        with self.lock:
            for event in self.events:
                if event['event_id'] == event_id:
                    event['reviewed'] = True
                    return True
        return False


class Server(ThreadingHTTPServer):
    def __init__(self, address, store=None):
        super().__init__(address, Handler)
        self.store = store if store is not None else EventStore()
        self.token = os.getenv('INGEST_TOKEN', '')


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, content_type='application/json'):
        if content_type == 'application/json':
            body = json.dumps(body, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == '/api/events':
            return self.reply(200, {'events': self.server.store.list()})
        if route == '/api/health':
            return self.reply(200, {'status': 'ok', 'flight_connected': False,
                                    'storage': 'memory; last 200 events; resets on restart'})
        assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                  '/index.html': ('index.html', 'text/html; charset=utf-8'),
                  '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                  '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if route in assets:
            name, kind = assets[route]
            return self.reply(200, (ROOT / 'static' / name).read_bytes(), kind)
        return self.reply(404, {'error': 'Not found'})

    def do_POST(self):
        # Browser mutations must come from this origin; no cross-origin CORS.
        origin = self.headers.get('Origin')
        expected = f'http://127.0.0.1:{self.server.server_port}'
        localhost = f'http://localhost:{self.server.server_port}'
        if origin and origin not in (expected, localhost):
            return self.reply(403, {'error': 'Origin not allowed'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.reply(415, {'error': 'Use application/json'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 16384:
                raise ValueError('Payload must be between 1 and 16384 bytes')
            value = json.loads(self.rfile.read(size))
            route = urlsplit(self.path).path
            if route == '/api/events':
                if self.server.token and self.headers.get('Authorization') != f'Bearer {self.server.token}':
                    return self.reply(401, {'error': 'Ingest token required'})
                added = self.server.store.add(value)
                return self.reply(201 if added else 200, {'added': added})
            if route == '/api/demo':
                sample = json.loads((ROOT / 'data' / 'sample-events.json').read_text())
                count = sum(self.server.store.add(event) for event in sample)
                return self.reply(200, {'added': count})
            if route == '/api/review':
                if not isinstance(value, dict) or not isinstance(value.get('event_id'), str):
                    raise ValueError('event_id is required')
                found = self.server.store.review(value['event_id'])
                return self.reply(200 if found else 404, {'reviewed': found})
            return self.reply(404, {'error': 'Not found'})
        except (ValueError, UnicodeDecodeError) as error:
            return self.reply(400, {'error': str(error)})

    def log_message(self, format, *args):
        # Keep request payloads, tokens and private source names out of logs.
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=int(os.getenv('PORT', '8000')))
    args = parser.parse_args()
    server = Server(('127.0.0.1', args.port))
    print(f'Open http://127.0.0.1:{server.server_port} — local software demo', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
