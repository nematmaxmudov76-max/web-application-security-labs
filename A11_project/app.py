import json
import math
import os
import re
import time
import uuid
import hmac
from collections import defaultdict, deque
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'policy.json').read_text())
BUCKETS = defaultdict(deque)
CLOCK = time.monotonic
os.umask(0o077)
LOG = ROOT / 'events.jsonl'
# Synthetic fixture only; no session or real password database.
DEMO_PASSWORD = 'Lab11-Only!'

def retry_after(ip, user):
    now, window = CLOCK(), CFG['window_seconds']
    pairs = [(('ip', ip), CFG['ip_limit']),
             (('account', user), CFG['account_limit'])]
    waits = []
    for key, limit in pairs:
        queue = BUCKETS[key]
        while queue and queue[0] <= now - window:
            queue.popleft()
        if len(queue) >= limit:
            waits.append(queue[0] + window - now)
    if waits:
        return max(1, math.ceil(max(waits)))
    for key, limit in pairs:
        BUCKETS[key].append(now)
    return 0

class App(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_result(self, status, event, user='-', retry=0):
        rid = uuid.uuid4().hex
        record = dict(ts=round(time.time(), 3), request_id=rid,
                      ip=self.client_address[0], user=user,
                      event=event, status=status)
        with LOG.open('a', encoding='utf-8') as out:
            out.write(json.dumps(record) + '\n')
        body = json.dumps({'result': event, 'request_id': rid}).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Request-ID', rid)
        if retry:
            self.send_header('Retry-After', str(retry))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            self.send_result(200, 'health_ok')
        else:
            self.send_result(404, 'not_found')

    def do_POST(self):
        if self.path != '/login':
            return self.send_result(404, 'not_found')
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 1024:
                return self.send_result(413, 'invalid_size')
            data = json.loads(self.rfile.read(length))
            user = data.get('username', '').strip().lower()
            password = data.get('password')
            if not re.fullmatch(r'[a-z0-9_]{1,24}', user):
                raise ValueError('invalid username')
            if not isinstance(password, str) or len(password) > 128:
                raise ValueError('invalid password')
        except (ValueError, AttributeError, TypeError):
            return self.send_result(400, 'invalid_input')
        wait = retry_after(self.client_address[0], user) if (
            CFG['rate_limit']) else 0
        if wait:
            return self.send_result(429, 'rate_limited', user, wait)
        valid = hmac.compare_digest(password.encode(), DEMO_PASSWORD.encode())
        valid = valid and user == 'alice'
        self.send_result(200 if valid else 401,
                         'login_ok' if valid else 'login_failed', user)

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8011), App)
    print('A11 127.0.0.1:8011; policy=', CFG, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
