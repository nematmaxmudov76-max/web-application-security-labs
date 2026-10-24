import argparse
import re
import unicodedata
import uuid

import nh3
from flask import Flask, render_template_string, request
from markupsafe import Markup
from werkzeug.exceptions import HTTPException

# ==============================================================================
# A QISM — Importlar, shablonlar (FORM, RESULT, ERROR) va yordamchi funksiyalar
# ==============================================================================

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8192  # 8 KB — DoS hujumlaridan himoya (Payload limit)
app.config['LAB_MODE'] = 'safe'

MIN_AGE, MAX_AGE = 16, 80

# Mijoz tekshiruvi bilan boyitilgan boshlang'ich forma (UX uchun)
FORM = '''<!doctype html><html lang="uz"><meta charset="utf-8">
<title>A2 - Kiritmalar</title><h1>A2: profilni tekshirish</h1>
<p>Rejim: {{ mode }}</p>
<form method="post" action="/preview">
<p>Ism: <input name="name" required minlength="2"
maxlength="40" value="Ali"></p>
<p>Yosh: <input name="age" type="number" required
min="16" max="80" value="20"></p>
<p>Izoh: <textarea name="comment" required
maxlength="200">Salom</textarea></p>
<button type="submit">Tekshirish</button></form></html>'''

# Natija shabloni — Plain text, Rich text va tozalangan kod ko'rinishi
RESULT = '''<!doctype html><html lang="uz"><meta charset="utf-8">
<title>A2 - Natija</title><h1>Tekshiruv natijasi</h1>
<p>Rejim: {{ mode }}</p><p>Ism: {{ name }}</p>
<p>Yosh: {{ age }}</p><h2>Oddiy matn sifatida</h2>
<pre id="plain">{{ plain }}</pre>
<h2>Cheklangan HTML sifatida</h2><div id="rich">{{ rich }}</div>
<h2>Sanitizatsiyadan keyingi HTML kodi</h2>
<pre id="clean-source">{{ clean_source }}</pre>
<p><a href="/">Formaga qaytish</a></p></html>'''

# Xatolik shabloni
ERROR = '''<!doctype html><meta charset="utf-8"><title>A2 - Xato</title>
<h1>So'rov bajarilmadi</h1><p id="error">{{ message }}</p>
<p><a href="/">Formaga qaytish</a></p>'''

# O'zbek tili tutuq belgilari va turli apostroflarni standart ASCII ' belgisiga keltirish jadvali
APOSTROPHES = str.maketrans({c: "'" for c in "‘’ʻʼ"})


def normal_name(value):
    """
    Ismni Unicode NFC kanonik shaklga keltiradi, apostroflarni unifikatsiya qiladi
    va chetdagi ortiqcha bo'sh joylarni olib tashlaydi.
    """
    return unicodedata.normalize('NFC', value).translate(APOSTROPHES).strip()


def fail(message, status=400):
    """Xatolik xabarini ERROR shabloni orqali mos HTTP status bilan qaytaradi."""
    return render_template_string(ERROR, message=message), status


# ==============================================================================
# B QISM — Server tekshiruvi mantig'i, /preview marshruti va HTML sanitizatsiyasi
# ==============================================================================


@app.after_request
def headers(response):
    """Xavfsizlik va keshni boshqarish sarlavhalari (no-store, nosniff)."""
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.get('/')
def index():
    """Bosh sahifa: Profil kiritish formasini chiqaradi."""
    return render_template_string(FORM, mode=app.config['LAB_MODE'])


@app.post('/preview')
def preview():
    form = request.form
    if app.config['LAB_MODE'] == 'weak':
        # Zaif rejim: Serverda deyarli hech qanday tekshiruv yo'q,
        # izoh esa Markup() orqali tekshirilmasdan xavfsiz deb e'lon qilinadi (XSS xavfi).
        name = form.get('name', '')
        age = int(form.get('age', ''))
        comment = form.get('comment', '')
        clean = comment
        plain = Markup(comment)  # Deliberately unsafe lab mode.
    else:
        # Xavfsiz (safe) rejim:
        # 1. So'rov strukturasi tekshiruvi (Parameter Pollution / Kutilmagan maydonlardan himoya)
        fields = {'name', 'age', 'comment'}
        if set(form) != fields or any(
            len(form.getlist(k)) != 1 for k in fields
        ):
            return fail('Uchta maydonni aynan bir martadan yuboring.')

        # 2. Me'yorlashtirish (Normalization)
        name = normal_name(form['name'])
        age_text = form['age'].strip()
        comment = unicodedata.normalize('NFC', form['comment']).strip()

        # 3. Ism sintaktik tekshiruvi (uzunlik va ruxsat berilgan belgilar)
        if (
            not (2 <= len(name) <= 40)
            or not all(
                c.isalpha()
                or unicodedata.category(c).startswith('M')
                or c in " '-"
                for c in name
            )
            or not any(c.isalpha() for c in name)
        ):
            return fail('Ism 2-40 belgi: harf, boshliq, apostrof, defis.')

        # 4. Yosh sintaktik (ASCII raqamlar) va semantik (16-80 oraliq) tekshiruvi
        if not re.fullmatch(r'[0-9]{1,3}', age_text):
            return fail('Yosh ASCII raqamlari bilan yozilishi kerak.')
        age = int(age_text)
        if not MIN_AGE <= age <= MAX_AGE:
            return fail('Yosh 16-80 oraligida bolishi kerak.')

        # 5. Izoh sintaktik tekshiruvi (uzunlik va xavfli boshqaruv belgilari)
        if not 1 <= len(comment) <= 200 or any(
            unicodedata.category(c).startswith('C') and c not in '\n\t'
            for c in comment
        ):
            return fail('Izoh 1-200 belgi; boshqaruv belgilarisiz.')

        # 6. Ruxsat ro'yxati (Allowlist) asosida HTML sanitizatsiyasi
        # Faqat 'b', 'em', 'p', 'br' teglariga ruxsat beriladi, barcha atributlar o'chiriladi.
        clean = nh3.clean(
            comment,
            tags={'b', 'em', 'p', 'br'},
            attributes={},
            strip_comments=True,
        )
        plain = comment  # Oddiy matn konteksti: Jinja shablon dvijogi buni avtomatik escape qiladi.

    return render_template_string(
        RESULT,
        mode=app.config['LAB_MODE'],
        name=name,
        age=age,
        plain=plain,
        rich=Markup(clean),  # Faqat tozalangan HTML Markup() orqali uzatiladi
        clean_source=clean,
    )


# ==============================================================================
# C QISM — Xatoliklarni xavfsiz boshqarish va ilovani ishga tushirish
# ==============================================================================


@app.get('/lab-error')
def lab_error():
    """Diagnostik sun'iy xatolik chiqaruvchi test endpointi."""
    raise RuntimeError('A2 controlled diagnostic error')


@app.errorhandler(HTTPException)
def http_error(error):
    """Mijoz tomonidan yuborilgan noto'g'ri HTTP so'rovlar uchun umumiy ishlov beruvchi."""
    return fail(
        'Sorov formati, hajmi, manzili yoki metodi notogri.', error.code or 500
    )


@app.errorhandler(Exception)
def internal_error(error):
    """
    Ichki server xatolari (500) uchun xavfsiz ishlov beruvchi:
    Traceback va maxfiy ma'lumotlarni foydalanuvchiga ko'rsatmaydi (Information Disclosure himoyasi).
    Foydalanuvchiga faqat 12 xonali tracking ID beradi, to'liq logni serverda qayd etadi.
    """
    reference = uuid.uuid4().hex[:12]
    app.logger.exception('A2 internal error id=%s', reference)
    return fail('Ichki xato. Qayd raqami: ' + reference, 500)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['weak', 'safe'], default='safe')
    parser.add_argument('--port', type=int, default=8000, help='Server porti (standart: 8000)')
    parser.add_argument('--host', default='127.0.0.1', help='Server host manzili (standart: 127.0.0.1)')
    args = parser.parse_args()
    app.config['LAB_MODE'] = args.mode
    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)
