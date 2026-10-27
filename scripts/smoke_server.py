"""Live socket smoke check for a normal host or CI (not a restricted sandbox)."""
import json
import sys
import threading
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import Server

server = Server(('127.0.0.1', 0))
worker = threading.Thread(target=server.serve_forever, daemon=True)
worker.start()
try:
    base = f'http://127.0.0.1:{server.server_port}'
    with urlopen(base + '/api/health', timeout=3) as response:
        assert json.load(response)['status'] == 'ok'
    request = Request(base + '/api/demo', b'{}', {'Content-Type': 'application/json'})
    with urlopen(request, timeout=3) as response:
        assert response.status == 200
    with urlopen(base + '/api/events', timeout=3) as response:
        assert len(json.load(response)['events']) == 2
    print('Live HTTP smoke check passed')
finally:
    server.shutdown()
    server.server_close()
    worker.join()
