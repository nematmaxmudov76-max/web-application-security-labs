import json
import time
import threading
from pathlib import Path
from http.client import HTTPConnection
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

CFG = json.loads(Path(__file__).with_name('settings.json').read_text())
CACHE = {}
PUBLIC = 'public, max-age=300'
PRIVATE = 'private, no-store'

def reply(handler, status, headers, body):
    handler.send_response(status)
    for key, value in headers.items():
        handler.send_header(key, value)
    handler.send_header('Content-Length', str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)

class Origin(BaseHTTPRequestHandler):
    count = 0
    def do_GET(self):
        Origin.count += 1
        path = urlsplit(self.path).path
        status, cc, mime = 200, PRIVATE, 'text/plain'
        if path == '/public':
            banner = self.headers.get('X-Lab-Banner', 'NORMAL')
            body, cc = 'PUBLIC banner=' + banner, PUBLIC
        elif path == '/assets/app.css':
            body, cc, mime = 'body {color: navy}', PUBLIC, 'text/css'
        elif path == '/account' or (
            CFG['loose_routes'] and path.startswith('/account/')
        ):
            cookies = SimpleCookie()
            cookies.load(self.headers.get('Cookie', ''))
            who = cookies['lab_user'].value if 'lab_user' in cookies else ''
            if who in ('alice', 'bob'):
                body = 'PRIVATE user=' + who + ' code=DEMO-' + who.upper()
            else:
                status, body = 401, 'LOGIN REQUIRED'
        else:
            status, body = 404, 'NOT FOUND'
        headers = {'Content-Type': mime, 'Cache-Control': cc,
                   'X-Origin-Id': str(Origin.count)}
        reply(self, status, headers, (body + '\n').encode())

class Edge(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        key = ('GET', self.headers.get('Host', ''), self.path)
        if CFG['safe_cache']:
            eligible = path in ('/public', '/assets/app.css') and not (
                self.headers.get('Cookie') or self.headers.get('Authorization')
            )
        else:
            eligible = path == '/public' or path.endswith('.css')
        item = CACHE.get(key) if eligible else None
        if item and time.monotonic() - item[0] < 300:
            saved, status, headers, body = item
            headers = dict(headers, **{'X-Lab-Cache': 'HIT',
                                       'Age': str(int(time.monotonic() - saved))})
            reply(self, status, headers, body)
            return
        forwarded = {}
        for name in ('Cookie', 'Authorization'):
            if self.headers.get(name):
                forwarded[name] = self.headers[name]
        if CFG['trust_banner'] and self.headers.get('X-Lab-Banner'):
            forwarded['X-Lab-Banner'] = self.headers['X-Lab-Banner']
        conn = HTTPConnection('127.0.0.1', 8010, timeout=3)
        conn.request('GET', self.path, headers=forwarded)
        response = conn.getresponse()
        status, body = response.status, response.read()
        headers = {name: response.getheader(name) for name in
                   ('Content-Type', 'Cache-Control', 'X-Origin-Id')}
        conn.close()
        store = eligible and status == 200
        if CFG['safe_cache']:
            store = store and headers['Cache-Control'] == PUBLIC
        if store:
            CACHE[key] = (time.monotonic(), status, dict(headers), body)
        headers['X-Lab-Cache'] = 'MISS' if store else 'BYPASS'
        if store:
            headers['Age'] = '0'
        reply(self, status, headers, body)

if __name__ == '__main__':
    origin = HTTPServer(('127.0.0.1', 8010), Origin)
    edge = HTTPServer(('127.0.0.1', 8080), Edge)
    threading.Thread(target=origin.serve_forever, daemon=True).start()
    print('A10: origin=8010 edge=8080; config=', CFG, flush=True)
    try:
        edge.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        edge.server_close()
        origin.shutdown()
        origin.server_close()
