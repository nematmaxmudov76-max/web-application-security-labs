import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

HTML = """<!doctype html>
<html lang="uz">
<head>
    <meta charset="utf-8">
    <title>A1 - Brauzer laboratoriyasi</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <h1 id="title">A1: veb arxitektura</h1>
    <p id="inline">Inline: bajarilmadi</p>
    <p id="external">Tashqi JS: bajarilmadi</p>
    <button id="same">Bir xil origin</button>
    <button id="cross">Boshqa origin</button>
    <button id="cookie">Cookie o'rnatish</button>
    <pre id="result">Natija shu yerda chiqadi.</pre>
    <script>document.getElementById('inline').textContent = 'Inline: ishladi';</script>
    <script src="/app.js"></script>
</body>
</html>"""

JS = """const out = document.getElementById('result');
document.getElementById('external').textContent = 'Tashqi JS: ishladi';
async function run(url) {
  try {
    const r = await fetch(url);
    const data = await r.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = 'Xato: ' + e.message;
    console.error(e);
  }
}
document.getElementById('same').addEventListener('click',
  () => run('/api/info'));
document.getElementById('cross').addEventListener('click',
  () => run('http://127.0.0.1:8001/api/info'));
document.getElementById('cookie').addEventListener('click',
  () => run('/cookie'));"""

CSS = "body{font:18px sans-serif;margin:40px}button{margin:6px}"

CSP = ("default-src 'self'; script-src 'self'; "
       "style-src 'self'; connect-src 'self' http://127.0.0.1:8001; "
       "object-src 'none'; base-uri 'none'; frame-ancestors 'none'")

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, required=True)
parser.add_argument('--cors-origin', default='')
parser.add_argument('--csp', action='store_true')
args = parser.parse_args()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        headers = {}
        status = 200
        content_type = 'application/json; charset=utf-8'
        if path == '/':
            body = HTML
            content_type = 'text/html; charset=utf-8'
        elif path == '/app.js':
            body = JS
            content_type = 'text/javascript; charset=utf-8'
        elif path == '/style.css':
            body = CSS
            content_type = 'text/css; charset=utf-8'
        elif path == '/api/info':
            body = json.dumps({
                'course': 'Veb dasturlar xavfsizligi',
                'port': self.server.server_port,
                'origin_received': self.headers.get('Origin', '(yoq)'),
                'cookie_received': bool(self.headers.get('Cookie'))
            })
            if args.cors_origin:
                headers['Access-Control-Allow-Origin'] = args.cors_origin
        elif path == '/cookie':
            headers['Set-Cookie'] = (
                'lab_session=A1-DEMO; Path=/; HttpOnly; SameSite=Lax')
            body = json.dumps({'message': 'Demo cookie ornatildi'})
        else:
            status = 404
            body = json.dumps({'error': 'Topilmadi'})
        data = body.encode('utf-8')

        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if args.csp:
            self.send_header('Content-Security-Policy', CSP)
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'A1: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
