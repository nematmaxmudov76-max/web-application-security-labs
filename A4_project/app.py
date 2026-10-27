import argparse
import secrets
import time
from flask import Flask, request, jsonify, make_response, render_template
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=4096, TTL=1200, WEAK_AUTHZ=False)
COOKIE = 'a4_sid'
SESSIONS = {}
USERS = {
    'ali': {'id': 1, 'role': 'student',
            'hash': generate_password_hash('Ali-A4-Only!')},
    'vali': {'id': 2, 'role': 'student',
             'hash': generate_password_hash('Vali-A4-Only!')},
    'admin': {'id': 3, 'role': 'admin',
              'hash': generate_password_hash('Admin-A4-Only!')}
}
DUMMY_HASH = generate_password_hash('Unused-A4-Value!')
DOCS = {101: {'owner': 1, 'text': 'Alining oquv hujjati'},
        102: {'owner': 2, 'text': 'Valining oquv hujjati'}}

def get_session():
    sid = request.cookies.get(COOKIE, '')
    record = SESSIONS.get(sid)
    if record and time.monotonic() >= record['expires']:
        SESSIONS.pop(sid, None)
        record = None
    return sid, record

def issue_session(username=None):
    now = time.monotonic()
    for key in list(SESSIONS):
        if SESSIONS[key]['expires'] <= now:
            SESSIONS.pop(key, None)
    sid = secrets.token_urlsafe(32)
    record = dict(username=username, csrf=secrets.token_urlsafe(32),
                  expires=now + app.config['TTL'])
    SESSIONS[sid] = record
    return sid, record

def attach_cookie(response, sid):
    response.set_cookie(COOKIE, sid, httponly=True, samesite='Lax',
                        secure=False, path='/')  # Local HTTP only.
    return response

def fail(status, message):
    return jsonify(error=message), status

def valid_csrf(record):
    token = request.headers.get('X-CSRF-Token') or request.form.get('csrf', '')
    return bool(record and token and
                secrets.compare_digest(record['csrf'].encode(), token.encode()))

def current_user():
    _, record = get_session()
    return USERS.get(record['username']) if record else None

@app.after_request
def headers(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.get('/')
@app.get('/api/csrf')
def entry():
    sid, record = get_session()
    if not record:
        sid, record = issue_session()
    if request.path == '/api/csrf':
        response = jsonify(csrf=record['csrf'])
    else:
        response = make_response(render_template('index.html',
            csrf=record['csrf'], username=record['username']))
    return attach_cookie(response, sid)

@app.post('/login')
def login():
    sid, record = get_session()
    if not valid_csrf(record):
        return fail(403, 'CSRF tekshiruvi bajarilmadi.')
    name = request.form.get('username', '')
    password = request.form.get('password', '')
    user = USERS.get(name)
    stored_hash = user['hash'] if user else DUMMY_HASH
    password_ok = check_password_hash(stored_hash, password)
    if not user or not password_ok:
        return fail(401, 'Login yoki parol xato.')
    SESSIONS.pop(sid, None)
    new_sid, _ = issue_session(name)
    response = jsonify(message='Kirish bajarildi.', role=user['role'])
    return attach_cookie(response, new_sid)

@app.get('/api/me')
def me():
    user = current_user()
    if not user:
        return fail(401, 'Avval tizimga kiring.')
    return jsonify(id=user['id'], role=user['role'])

@app.get('/api/admin')
def admin():
    user = current_user()
    if not user:
        return fail(401, 'Avval tizimga kiring.')
    if user['role'] != 'admin':
        return fail(403, 'Administrator huquqi kerak.')
    return jsonify(message='Administrator hisoboti', users=len(USERS))

@app.get('/api/docs/<int:doc_id>')
def document(doc_id):
    user = current_user()
    if not user:
        return fail(401, 'Avval tizimga kiring.')
    doc = DOCS.get(doc_id)
    if not doc:
        return fail(404, 'Hujjat topilmadi.')
    allowed = user['role'] == 'admin' or doc['owner'] == user['id']
    if not app.config['WEAK_AUTHZ'] and not allowed:
        return fail(403, 'Bu hujjatga ruxsat yoq.')
    return jsonify(id=doc_id, **doc)

@app.post('/api/logout')
def logout():
    sid, record = get_session()
    if not record or not record['username']:
        return fail(401, 'Faol sessiya yoq.')
    if not valid_csrf(record):
        return fail(403, 'CSRF tekshiruvi bajarilmadi.')
    SESSIONS.pop(sid, None)
    response = jsonify(message='Sessiya bekor qilindi.')
    response.delete_cookie(COOKIE, path='/')
    return response

@app.errorhandler(HTTPException)
def http_error(error):
    return fail(error.code or 500, 'Sorov bajarilmadi.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weak-authz', action='store_true')
    parser.add_argument('--ttl', type=int, default=1200)
    args = parser.parse_args()
    if args.ttl < 1:
        parser.error('--ttl musbat son bolishi kerak')
    app.config.update(WEAK_AUTHZ=args.weak_authz, TTL=args.ttl)
    app.run(host='127.0.0.1', port=8004, debug=False,
            use_reloader=False, threaded=False)
