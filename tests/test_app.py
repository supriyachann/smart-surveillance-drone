import json
import io
import unittest
from pathlib import Path
from types import SimpleNamespace

from app import EventStore, Handler, validate_event
from detector import events_from_result

SAMPLES = json.loads((Path(__file__).resolve().parents[1] / 'data/sample-events.json').read_text())


class ValidationTests(unittest.TestCase):
    def test_sample_is_valid(self):
        self.assertEqual(validate_event(SAMPLES[0])['label'], 'person')

    def test_rejects_malformed_fields(self):
        for field, bad in [('confidence', True), ('confidence', float('nan')),
                           ('confidence', 1.1), ('bbox_normalized', [0.8, 0, 0.2, 1]),
                           ('bbox_normalized', [0, 0, 2, 1]), ('synthetic', 'false'),
                           ('timestamp', 'yesterday'), ('timestamp', '2026-01-01T12:00:00'),
                           ('schema_version', True), ('label', 'threat'), ('label', [])]:
            with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                validate_event(dict(SAMPLES[0], **{field: bad}))

    def test_rejects_non_object(self):
        with self.assertRaises(ValueError):
            validate_event([])

    def test_deduplicates_and_reviews(self):
        store = EventStore()
        self.assertTrue(store.add(SAMPLES[0]))
        self.assertFalse(store.add(SAMPLES[0]))
        self.assertTrue(store.review(SAMPLES[0]['event_id']))
        self.assertTrue(store.list()[0]['reviewed'])
        self.assertFalse(store.review('missing'))

    def test_storage_is_bounded(self):
        store = EventStore(limit=1)
        for sample in SAMPLES:
            store.add(sample)
        self.assertEqual(len(store.list()), 1)
        self.assertEqual(store.list()[0]['event_id'], SAMPLES[-1]['event_id'])

    def test_detector_adapter_filters_classes(self):
        class Box:
            cls = [0]
            conf = [.9]
            xyxyn = [[.1, .2, .4, .8]]
        class Result:
            boxes = [Box()]
            names = {0: 'person'}
        event = list(events_from_result(Result(), 'test-camera', '2026-01-01T00:00:00Z'))[0]
        self.assertFalse(validate_event(event)['synthetic'])
        Result.names = {0: 'dog'}
        self.assertEqual(list(events_from_result(Result(), 'test', event['timestamp'])), [])


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.server = SimpleNamespace(store=EventStore(), token='', server_port=8000)

    def raw_call(self, path, value=None, headers=None):
        request_headers = {'Content-Type': 'application/json'}
        request_headers.update(headers or {})
        body = json.dumps(value).encode() if value is not None else b''
        request_headers['Content-Length'] = str(len(body))
        method = 'POST' if value is not None else 'GET'
        request = f'{method} {path} HTTP/1.0\r\n'
        request += ''.join(f'{key}: {val}\r\n' for key,val in request_headers.items())
        class Connection:
            output = bytearray()
            def makefile(self, *args):
                return io.BytesIO(request.encode() + b'\r\n' + body)
            def sendall(self, data):
                self.output.extend(data)
        connection = Connection()
        Handler(connection, ('127.0.0.1', 12345), self.server)
        head, response_body = bytes(connection.output).split(b'\r\n\r\n', 1)
        return int(head.split()[1]), response_body

    def call(self, path, value=None, headers=None):
        status, body = self.raw_call(path, value, headers)
        return status, json.loads(body)

    def test_complete_review_flow(self):
        self.assertEqual(self.call('/api/demo', {})[1]['added'], 2)
        self.assertEqual(self.call('/api/demo', {})[1]['added'], 0)
        events = self.call('/api/events')[1]['events']
        self.assertEqual(len(events), 2)
        self.assertTrue(all(e['synthetic'] for e in events))
        self.assertEqual(self.call('/api/review', {'event_id': events[0]['event_id']})[0], 200)
        self.assertTrue(self.call('/api/events')[1]['events'][0]['reviewed'])

    def test_ingest_and_duplicate(self):
        self.assertEqual(self.call('/api/events', SAMPLES[0])[0], 201)
        self.assertEqual(self.call('/api/events', SAMPLES[0])[1], {'added': False})

    def test_rejects_invalid_event(self):
        self.assertEqual(self.call('/api/events', {'label': 'person'})[0], 400)
        self.assertEqual(self.call('/api/events', [1])[0], 400)

    def test_rejects_cross_origin_mutation(self):
        self.assertEqual(self.call('/api/demo', {}, {'Origin':'https://unrelated.example'})[0], 403)

    def test_ingest_token(self):
        self.server.token = 'test-only-token'
        self.assertEqual(self.call('/api/events', SAMPLES[0])[0], 401)
        self.assertEqual(self.call('/api/events', SAMPLES[0], {'Authorization':'Bearer test-only-token'})[0], 201)

    def test_unknown_route_and_missing_review(self):
        self.assertEqual(self.call('/missing')[0], 404)
        self.assertEqual(self.call('/api/review', {'event_id':'missing'})[0], 404)

    def test_static_assets_and_traversal(self):
        for path in ['/', '/app.js', '/style.css']:
            status, body = self.raw_call(path)
            self.assertEqual(status, 200)
            self.assertGreater(len(body), 100)
        self.assertEqual(self.call('/../app.py')[0], 404)


if __name__ == '__main__':
    unittest.main()
