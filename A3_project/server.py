import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parent
FILES = {
    '/': ('index.html', 'text/html; charset=utf-8'),
    '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
    '/vendor.js': ('vendor.js', 'text/javascript; charset=utf-8')
}

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, kind):
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path in FILES:
            name, kind = FILES[url.path]
            return self.reply(200, (ROOT / name).read_bytes(), kind)

        if url.path == '/api/echo':
            q = parse_qs(url.query).get('q', [''])[0]
            status, data = 200, {'text': q}
            if not 1 <= len(q) <= 200:
                status, data = 400, {'error': '1-200 belgi kiriting.'}
            elif q == 'badshape':
                data = {'text': 123}
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            return self.reply(status, body, 'application/json; charset=utf-8')

        self.reply(404, b'Not found', 'text/plain; charset=utf-8')

if __name__ == '__main__':
    print('A3: http://127.0.0.1:8000/', flush=True)
    HTTPServer(('127.0.0.1', 8000), Handler).serve_forever()