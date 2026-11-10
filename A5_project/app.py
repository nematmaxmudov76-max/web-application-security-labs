import sqlite3
import mongomock
from flask import Flask, abort, jsonify, request
from sqlalchemy import create_engine, select, text
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import Session, mapped_column
from sqlalchemy.pool import StaticPool

# 1. Flask ilovasini yaratish va maksimal so'rov hajmini cheklash (4 KB)
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4096

# 2. Boshlang'ich test ma'lumotlari: 3 ta ochiq va 1 ta maxfiy tovar
DATA = [
    {'id': 1, 'name': 'Daftar', 'public': True},
    {'id': 2, 'name': 'Qalam', 'public': True},
    {'id': 3, 'name': "O'quv qo'llanma", 'public': True},
    {'id': 4, 'name': 'Ichki loyiha', 'public': False},
]
SQL = 'SELECT id, name, public FROM products '

# 3. SQLAlchemy ORM modelini ta'riflash
class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    public: Mapped[bool] = mapped_column(Boolean)

# 4. Xotiradagi (in-memory) SQLite ma'lumotlar bazasini initsializatsiya qilish
engine = create_engine(
    'sqlite://', poolclass=StaticPool,
    connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
with engine.begin() as conn:
    conn.execute(Product.__table__.insert(), DATA)

# 5. Xotiradagi mongomock NoSQL kolleksiyasini yaratish
collection = mongomock.MongoClient().a5.products
collection.insert_many([dict(row) for row in DATA])

# 6. Kiritma tekshiruvi: faqat 1..120 belgili matn bo'lishi shart
def scalar(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 120:
        abort(400, description='name: 1..120 belgili matn kerak')
    return value

# ==================== FUNKSIYALAR: ZAIF VA XAVFSIZ ====================

# [SQL ZAIF]: f-string orqali SQL tuzilgan (SQL Injection mavjud)
def sql_weak(name):
    with engine.connect() as conn:
        query = SQL + f"WHERE name = '{name}' AND public = 1"
        return conn.exec_driver_sql(query).mappings().all()

# [SQL XAVFSIZ]: Parametrli so'rov (? placeholder)
def sql_safe(name):
    with engine.connect() as conn:
        query = SQL + 'WHERE name = ? AND public = 1'
        return conn.exec_driver_sql(query, (name,)).mappings().all()

# [ORM ZAIF]: ORM sessiyasi ichida xom SQL matni ishlatilgan
def orm_weak(name):
    with Session(engine) as session:
        query = SQL + f"WHERE name = '{name}' AND public = 1"
        return session.execute(text(query)).mappings().all()

# [ORM XAVFSIZ]: Model obyektlari va where filtrlari
def orm_safe(name):
    with Session(engine) as session:
        stmt = select(Product).where(
            Product.name == name, Product.public.is_(True))
        return [dict(id=p.id, name=p.name, public=p.public)
                for p in session.scalars(stmt).all()]

# [NoSQL ZAIF]: JSONdagi obyekt to'g'ridan-to'g'ri filtrga berilgan (Operator Injection)
def nosql_weak(body):
    if not isinstance(body, dict) or 'name' not in body:
        abort(400, description='JSON obyektida name kerak')
    query = {'name': body['name'], 'public': True}
    return list(collection.find(query, {'_id': 0}))

# [NoSQL XAVFSIZ]: Maydonlar tekshirilgan, string qat'iy talab qilingan, $eq operatori
def nosql_safe(body):
    if not isinstance(body, dict) or set(body) != {'name'}:
        abort(400, description='Faqat name maydoni kerak')
    name = scalar(body['name'])
    query = {'name': {'$eq': name}, 'public': True}
    return list(collection.find(query, {'_id': 0}))

# Natijalarni tartiblab JSON formatida qaytarish
def result(rows):
    items = sorted([dict(row) for row in rows], key=lambda x: x['id'])
    for item in items:
        item['public'] = bool(item['public'])
    return jsonify(count=len(items), items=items)

# ==================== FLASK ENDPOINTLARI ====================

@app.get('/')
def home():
    return jsonify(lab='A5 / 1-variant',
                   endpoints=['/sql/weak', '/sql/safe',
                              '/orm/weak', '/orm/safe',
                              '/nosql/weak', '/nosql/safe'])

@app.get('/<kind>/<mode>')
def sql_route(kind, mode):
    funcs = {('sql', 'weak'): sql_weak,
             ('sql', 'safe'): sql_safe,
             ('orm', 'weak'): orm_weak,
             ('orm', 'safe'): orm_safe}
    if (kind, mode) not in funcs:
        abort(404)
    name = scalar(request.args.get('name'))
    from sqlalchemy.exc import SQLAlchemyError
    try:
        return result(funcs[kind, mode](name))
    except (SQLAlchemyError, sqlite3.Error):
        return jsonify(error='Sorov bajarilmadi'), 400

@app.post('/nosql/<mode>')
def nosql_route(mode):
    if mode not in ('weak', 'safe'):
        abort(404)
    body = request.get_json(silent=True)
    func = nosql_weak if mode == 'weak' else nosql_safe
    return result(func(body))

@app.errorhandler(400)
def bad_request(error):
    return jsonify(error=error.description), 400

if __name__ == '__main__':
    # Faqat lokal loopback manzilida ishga tushirish
    app.run(host='127.0.0.1', port=8005,
            debug=False, threaded=False)
