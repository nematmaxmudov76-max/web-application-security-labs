# A2: Veb Ilovalarda Foydalanuvchi Kiritgan Ma’lumotlarini Xavfsiz Qayta Ishlash

Ushbu hujjat **A2_Veb_dasturlar_xavfsizligi_VMware_proxy.pdf** laboratoriya ishi qo‘llanmasi asosida tayyorlangan bo‘lib, veb ilovalarda kiritilgan ma’lumotlarni xavfsiz qabul qilish, me’yorlashtirish (normalization), tekshirish (validation), xavfsiz chiqarish (output encoding) va HTML sanitizatsiyasi bo‘yicha to‘liq nazariy hamda amaliy qo‘llanmani o‘z ichiga oladi.

---

## MUNDARIJA

1. [Mavzuning Maqsadi va Dolzarbligi](#1-mavzuning-maqsadi-va-dolzarbligi)
2. [Mavzu Haqida To‘liq Tushunchalar](#2-mavzu-haqida-toliq-tushunchalar)
   - 2.1. Foydalanuvchi kiritmalariga ishonchsizlik tamoyili (Zero Trust Input)
   - 2.2. Mijoz (Client-side) va Server (Server-side) tekshiruvi farqi
   - 2.3. Sintaktik va Semantik tekshiruv
   - 2.4. Ma’lumotlarni me’yorlashtirish (Normalization & Unicode NFC)
   - 2.5. Kodlash (Encoding/Escaping) va Sanitizatsiya (Sanitization) farqi
   - 2.6. Xavfli `Markup()` funksiyasi va Jinja avtomatik kodlashi
   - 2.7. Ruxsat ro‘yxati (Allowlist) asosida sanitizatsiya (`nh3` kutubxonasi)
   - 2.8. Xatoliklarni xavfsiz boshqarish (Information Disclosure / 500 Error Handling)
   - 2.9. So‘rov hajmini cheklash (DoS himoyasi va Payload Limits)
3. [Vazifani Bajarish Tartibi](#3-vazifani-bajarish-tartibi)
   - 3.1. Dastur nima vazifani bajaradi?
   - 3.2. Qayerlarda va qanday tizimlarda qo‘llash mumkin?
   - 3.3. Kerakli vositalar va qo‘shimcha kutubxonalar (Libraries)
   - 3.4. Bosqichma-bosqich amaliy ko‘rsatmalar (Laboratoriyani bajarish)
   - 3.5. Natijalar jadvali (Kutiladigan va amaliy natijalar)
   - 3.6. Topshiriladigan dalillar (D1 — D5)
   - 3.7. Himoya savollari va ularning javoblari

---

## 1. MAVZUNING MAQSADI VA DOLZARBLIGI

### 1.1. Asosiy maqsad
Laboratoriya ishining asosiy maqsadi — talabaga veb-ilovalarda foydalanuvchi tomonidan yuborilgan har qanday ma’lumotga server tomonida qat’iy ishonchsizlik bilan yondashish madaniyatini singdirishdir. Amaliy tajriba orqali:
1. Brauzerdagi forma tekshiruvlari (HTML5 `required`, `min`, `max`, `pattern`) faqat foydalanuvchi qulayligi (UX) uchun ekanligini, xavfsizlik chegarasi (security boundary) bo‘la olmasligini ko‘rsatish;
2. Server tomonida sintaktik va semantik tekshiruvlarni to‘g‘ri tashkil etish;
3. Matnlarni qayta ishlashdan oldin kanonik ko‘rinishga keltirish (Unicode NFC me’yorlashtirish);
4. Oddiy matn (Plain text) va boyitilgan matn (Rich text / HTML) kontekstlari uchun turli xil himoya choralarini (avtomatik HTML-escaping va ruxsat ro‘yxatiga asoslangan sanitizatsiya) qo‘llash;
5. Ichki server xatoliklarida tizim tafsilotlari (traceback, fayl yo‘llari) sizib chiqishini oldini olgan holda xavfsiz xatolik boshqaruvini yo‘lga qo‘yish.

### 1.2. Kutiladigan natijalar
- Talaba brauzer cheklovlarini chetlab o‘tib (masalan, `curl` yordamida yoki brauzer DevTools orqali DOM atributlarini o‘chirib) so‘rov yuborishni o‘rganadi;
- Zaif (`weak`) va himoyalangan (`safe`) rejimlar orasidagi tub farqni amalda ko‘radi;
- XSS (Cross-Site Scripting) kabi hujumlarning oldini olishda `Markup()` funksiyasining noto‘g‘ri ishlatilish xavfini va `nh3` yordamida tozalash mexanizmini tushunadi.

---

## 2. MAVZU HAQIDA TO‘LIQ TUSHUNCHALAR

### 2.1. Foydalanuvchi kiritmalariga ishonchsizlik tamoyili (Zero Trust Input)
Veb xavfsizligida oltin qoida mavjud: **"Never trust user input"** (Foydalanuvchi kiritgan hech bir ma’lumotga ishonma). Foydalanuvchi deb nafaqat oddiy mehribon tashrif buyuruvchi, balki veb-ilovani tekshirayotgan tajovuzkor, avtomatlashtirilgan botlar yoki skriptlar ham tushuniladi. Foydalanuvchidan keladigan HTTP sarlavhalari (headers), forma maydonlari (POST body), URL parametrlari (query string) va hatto yuklanayotgan fayllar ham potentsial xavf manbaidir.

### 2.2. Mijoz (Client-side) va Server (Server-side) tekshiruvi farqi
- **Mijoz tekshiruvi (Client-side validation):** Brauzerda JavaScript yoki HTML5 atributlari (`required`, `type="number"`, `min="16"`, `max="80"`, `maxlength="40"`) orqali amalga oshiriladi.
  - *Vazifasi:* Foydalanuvchiga xatoni forma yuborilishidan oldin tez ko‘rsatish, serverga keraksiz noto‘g‘ri so‘rovlar oqimini kamaytirish va foydalanuvchi tajribasini (UX) oshirish.
  - *Chegarasi:* Mijoz kodi to‘liq foydalanuvchi nazorati ostida bo‘ladi. Uni F12 (DevTools) orqali osongina tahrirlash, o‘chirib tashlash yoki brauzerni umuman chetlab o‘tib, to‘g‘ridan-to‘g‘ri `curl`, `Postman` yoki Python skript orqali istalgan qiymatni POST qilish mumkin. **Mijoz tekshiruvi hech qachon xavfsizlik mexanizmi hisoblanmaydi!**
- **Server tekshiruvi (Server-side validation):** Serverga HTTP orqali kelib tushgan har bir so‘rov uchun backend dasturida (masalan, Python Flask) bajariladigan majburiy tekshiruv.
  - *Vazifasi:* Ilovaning yaxlitligini, biznes mantiqini va xavfsizligini ta’minlash. Faqat server tekshiruvigina haqiqiy xavfsizlik chegarasini hosil qiladi.

### 2.3. Sintaktik va Semantik tekshiruv
Serverga kelgan ma’lumot ikki bosqichda tekshirilishi lozim:
1. **Sintaktik tekshiruv (Format tekshiruvi):**
   - Ma’lumot kutilgan format, uzunlik va belgilardan iboratmi?
   - *Misol:* `age` maydonida faqat ASCII raqamlari (`r'^[0-9]{1,3}$'`) bormi? Harflar yoki maxsus belgilar yo‘qmi?
2. **Semantik tekshiruv (Mantiqiy/Biznes tekshiruv):**
   - Ma’lumot mantiqan to‘g‘rimi va ruxsat etilgan oraliqdami?
   - *Misol:* `age` formati to‘g‘ri butun son bo‘lsa ham, u 16 dan 80 gacha bo‘lgan oraliqqa (`MIN_AGE <= age <= MAX_AGE`) tushadimi? 150 yoki -5 kabi sonlar semantik jihatdan noto‘g‘ridir.

### 2.4. Ma’lumotlarni me’yorlashtirish (Normalization & Unicode NFC)
Unicode tizimida bir xil ko‘rinishdagi belgilar turli xil kod nuqtalari (code points) orqali ifodalanishi mumkin. Masalan, "é" harfi:
- Bitta mustaqil belgi sifatida: `\u00E9` (precomposed).
- Ikki belgi birikmasi sifatida: oddiy `e` (`\u0065`) + tepasidagi urg‘u belgisi `\u0301` (combining accent).

Agar kiritma me’yorlashtirilmasa:
- Filtrlash qoidalari chetlab o‘tilishi mumkin (WAF bypass);
- Uzunlikni hisoblash (`len()`) adashadi;
- Bazada qidiruv va solishtirish xatoliklarga olib keladi.

**NFC (Normalization Form C):** Belgilarni kanonik (kanonik kompozitsiya) shaklga keltiradi, ya’ni birikuvchi belgilarni yagona belgiga aylantiradi.
- Ushbu laboratoriyada o‘zbek tilidagi tutuq belgisi va apostroflarning har xil ko‘rinishlari (`‘`, `’`, `ʻ`, `ʼ`) standart ASCII apostrofga (`'`) almashtiriladi hamda chetdagi ortiqcha bo‘sh joylar (`strip()`) olib tashlanadi.

### 2.5. Kodlash (Encoding/Escaping) va Sanitizatsiya (Sanitization) farqi
Bu veb xavfsizligining eng muhim farqlaridan biridir:

| Xususiyat | Avtomatik Kodlash (HTML Escaping) | Sanitizatsiya (HTML Sanitization) |
| :--- | :--- | :--- |
| **Maqsad** | Kiritmani **oddiy matn (plain text)** deb qabul qilib, brauzer uni HTML kodi sifatida talqin qilmasligini ta’minlash. | Kiritma ichida **xavfsiz HTML teglariga (rich text)** ruxsat berish, xavfli teglarni tozalash. |
| **Qanday ishlaydi?** | Xavfli belgilar HTML entitilariga almashtiriladi: `<` &rarr; `&lt;`, `>` &rarr; `&gt;`, `&` &rarr; `&amp;`, `"` &rarr; `&quot;`, `'` &rarr; `&#39;`. | HTML daraxti (DOM parse) tahlil qilinadi, faqat ruxsat etilgan teg va atributlar qoldiriladi. |
| **Natija** | Foydalanuvchi `<b>Salom</b>` yozsa, ekranda aynan `<b>Salom</b>` matni ko‘rinadi. Matn qalinlashmaydi. | Foydalanuvchi `<b>Salom</b>` yozsa, u qalin **Salom** bo‘lib chiqadi. Lekin `<script>` yoki `onclick` bo‘lsa, ular o‘chirib yuboriladi. |
| **Qo‘llaniladigan vosita** | Jinja shablon dvijogi (`autoescape=True`). | Maxsus parser kutubxonasi (`nh3`, `Bleach` va h.k.). |

### 2.6. Xavfli `Markup()` funksiyasi va Jinja avtomatik kodlashi
- Flask va Jinja shablonlarida `{{ o'zgaruvchi }}` ishlatilganda, Jinja avtomatik ravishda barcha maxsus HTML belgilarini kodlaydi (`escape` qiladi). Bu XSS dan ishonchli himoya hisoblanadi.
- Ammo dasturchi `Markup(matn)` funksiyasini chaqirsa, u Jinjaga: *"Bu matn allaqachon xavfsiz HTML, uni qayta tekshirma yoki kodlama!"* deb buyruq beradi.
- Agar `Markup()` funksiyasiga tozalangan HTML emas, balki foydalanuvchidan to‘g‘ridan-to‘g‘ri olingan xom kiritma berilsa (`Markup(comment)`), ilovada **og‘ir XSS (Cross-Site Scripting)** zaifligi paydo bo‘ladi.

### 2.7. Ruxsat ro‘yxati (Allowlist) asosida sanitizatsiya (`nh3` kutubxonasi)
HTMLni regex (muntazam ifodalar) yoki oddiy `replace("<script>", "")` orqali tozalashga urinish mutlaqo noto‘g‘ri va xavflidir (tajovuzkor `<scr<script>ipt>` yoki `<img src=x onerror=...>` kabi minglab usullar bilan aylanib o‘tishi mumkin).
To‘g‘ri usul — **Ruxsat ro‘yxati (Allowlist)** asosida ishlaydigan HTML parseridan foydalanishdir.
- Ushbu laboratoriyada Rust asosidagi ultra-tezkor va xavfsiz **`nh3`** kutubxonasi ishlatiladi.
- Sozlama: Faqat xavfsiz formatlash teglari ruxsat etiladi: `tags={'b', 'em', 'p', 'br'}`.
- Barcha atributlar (shu jumladan `onclick`, `onload`, `onerror`, `style`, `href`) to‘liq taqiqlanadi: `attributes={}`.
- Natijada: `<b onclick="alert(1)">Salom</b><img src=x>` kiritilsa, `nh3` uni tozalab, faqat `<b>Salom</b>` ko‘rinishida qoldiradi.

### 2.8. Xatoliklarni xavfsiz boshqarish (Information Disclosure / 500 Error Handling)
- Ishlab chiqish (`debug=True`) rejimida xato yuz berganda Flask ekranga to‘liq kod matni, fayl yo‘llari, kutubxonalar versiyalari va o‘zgaruvchilar qiymatlarini chiqaradi. Tajovuzkor uchun bu eng qimmatli razvedka ma’lumotidir.
- Ishlab chiqarish (Production) rejimida `debug=False` bo‘lishi shart.
- Foydalanuvchiga faqat umumiy xabar va noyob kuzatuv identifikatori (masalan, 12 belgili UUID: `reference = uuid.uuid4().hex[:12]`) ko‘rsatiladi.
- To‘liq xatolik tafsilotlari (traceback) esa faqat serverning ichki xavfsiz loglariga (`app.logger.exception`) yoziladi. Foydalanuvchi ma’muriyatga faqat shu qayd raqamini taqdim etadi.

### 2.9. So‘rov hajmini cheklash (DoS himoyasi va Payload Limits)
Agar serverga yuboriladigan HTTP so‘rovining maksimal hajmi cheklanmasa, tajovuzkor gigabaytlab ma’lumot yuborib server xotirasini to‘ldirishi va tizimni ishdan chiqarishi mumkin (Denial of Service — DoS).
- `app.config['MAX_CONTENT_LENGTH'] = 8192` (8 KB) sozlamasi orqali so‘rov hajmi cheklanadi. Agar kiritma hajmi bundan oshsa, server darhol `413 Payload Too Large` xatosini qaytaradi.

---

## 3. VAZIFANI BAJARISH TARTIBI

### 3.1. Dastur nima vazifani bajaradi?
Mazkur laboratoriya dasturi (`a2_app.py`) foydalanuvchidan uchta maydonni qabul qiluvchi o‘quv profil formasini taqdim etadi:
1. **Ism (`name`)**: Foydalanuvchi ismi (2–40 belgi).
2. **Yosh (`age`)**: Foydalanuvchi yoshi (16–80 oralig‘idagi butun son).
3. **Izoh (`comment`)**: Foydalanuvchi qoldirgan izoh (1–200 belgi).

Dastur 2 xil rejimda ishlay oladi:
- **`--mode weak` (Zaif rejim):** Server tekshiruvi yetarli emas, faqat mijoz tekshiruviga tayanadi. Kiritilgan izohni to‘g‘ridan-to‘g‘ri `Markup()` orqali xavfsiz deb e’lon qilib, HTMLga chiqaradi.
- **`--mode safe` (Himoyalangan rejim):**
  - So‘rov tarkibi qat’iy tekshiriladi (aynan 3 ta maydon bo‘lishi shart, takroriy maydonlar taqiqlanadi);
  - Ma’lumotlar me’yorlashtiriladi (NFC, apostroflar, bo‘sh joylar);
  - Yosh va ism formati hamda chegaralari tekshiriladi;
  - Izoh oddiy matn sifatida avtomatik kodlanadi, cheklangan HTML sifatida esa `nh3` orqali tozalanib chiqariladi;
  - Xatoliklar (400 va 500) xavfsiz tarzda boshqariladi.

### 3.2. Qayerlarda va qanday tizimlarda qo‘llash mumkin?
Ushbu laboratoriyada o‘rganiladigan prinsiplar veb-ishlab chiqishning deyarli barcha sohalarida majburiy standart hisoblanadi:
1. **Foydalanuvchi profili va ro‘yxatdan o‘tish formalari:** Shaxsiy ma’lumotlar (ism, familiya, yosh, telefon) bazaga xavfsiz yozilishi va to‘g‘ri formatda bo‘lishi uchun.
2. **Bloglar, forumlar va izohlar tizimi:** Foydalanuvchilarga matnni formatlash (qalin, qiya matn) imkoniyatini berishda XSS va zararli JavaScript kiritilishini bloklash uchun (masalan, Markdown parserlari yoki WYSIWYG muharrirlari).
3. **Elektron tijorat (E-commerce) va to‘lov tizimlari:** Narxlar, mahsulot miqdori va chegirmalar mijoz tomonida o‘zgartirilib yuborilishining oldini olish uchun (parametrlar manipulyatsiyasi).
4. **API Gateway va Mikroxizmatlar:** So‘rovlar hajmini cheklash, HTTP parametrlarini ifloslantirish (HTTP Parameter Pollution) hujumlaridan himoyalanish.
5. **Bank va korporativ ilovalar:** Tizim xatoliklarida ichki arxitektura va ma’lumotlar bazasi xatolarini foydalanuvchidan yashirish (Information Leakage himoyasi).

### 3.3. Kerakli vositalar va qo‘shimcha kutubxonalar (Libraries)
Vazifani bajarishda quyidagi ochiq manbali kutubxonalar va dasturlar o‘rnatiladi hamda ishlatiladi:

| Dastur / Kutubxona | Versiya | Vazifasi va O‘rni |
| :--- | :--- | :--- |
| **Python 3** | 3.12+ | Asosiy dasturlash tili va standart modullar (`unicodedata`, `re`, `uuid`, `argparse`). |
| **python3-venv** | - | Loyihaning mustaqil, izolyatsiyalangan virtual paketlar muhitini yaratish. |
| **Flask** | `3.1.3` | WSGI veb-freymvorki; HTTP so‘rovlarini qabul qilish, marshrutlash (routing) va shablonlarni vizuallashtirish. |
| **nh3** | `0.3.7` | Ammonia (Rust) asosidagi xavfsiz HTML sanitizatsiya kutubxonasi. HTML teg va atributlarini allowlist asosida tozalaydi. |
| **MarkupSafe** | (Flask bilan keladi) | Matnlarni xavfsiz HTML belgisi sifatida tamg‘alash (`Markup`) va avtomatik kodlash mexanizmi. |
| **Werkzeug** | (Flask bilan keladi) | HTTP istisnolari (`HTTPException`), so‘rovlarni tahlil qilish va xavfsizlik sarlavhalari. |
| **curl** | - | Buyruqlar satri orqali HTTP so‘rovlarini brauzersiz, to‘g‘ridan-to‘g‘ri yuborish va sinash vositasi. |
| **Firefox + DevTools** | - | Brauzer F12 paneli (Network, Inspector, Console) orqali so‘rovlar, DOM daraxti va HTML kodini tahlil qilish. |

---

### 3.4. Bosqichma-bosqich amaliy ko‘rsatmalar

#### 1-qadam: Virtual muhitni yaratish va kutubxonalarni o‘rnatish
Terminalda loyiha katalogini oching va kerakli paketlarni o‘rnating:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl nano
mkdir -p ~/websec/A2
cd ~/websec/A2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Flask==3.1.3 nh3==0.3.7
python -m pip freeze > requirements-lock.txt
python -m pip show Flask nh3
```

#### 2-qadam: Laboratoriya kodini (`a2_app.py`) yaratish
`nano a2_app.py` orqali fayl ochiladi va laboratoriya kodi yoziladi:
- **A qism:** Importlar, shablonlar (`FORM`, `RESULT`, `ERROR`), `normal_name` yordamchi funksiyasi.
- **B qism:** Server tekshiruvi mantig‘i, `/preview` marshruti (weak va safe tarmoqlari), `nh3.clean` sanitizatsiyasi.
- **C qism:** Xatoliklarni ushlash (`/lab-error`, `http_error`, `internal_error`), argumentlarni o‘qish va ilovani ishga tushirish.

Kodni sintaksisini tekshirish:
```bash
python -m py_compile a2_app.py
```
*(Hech qanday xatolik chiqmasligi kerak).*

---

#### 3-qadam: `weak` rejimida ishga tushirish va mijoz cheklovini aylanib o‘tish
1. Serverni ishga tushiring:
   ```bash
   python a2_app.py --mode weak
   ```
2. Brauzerda `http://127.0.0.1:8002/` manzilini oching.
3. Formada Ism: `Ali`, Yosh: `20`, Izoh: `Salom` kiritib, F12 Network panelini ochgan holda **Tekshirish** tugmasini bosing. 200 OK statusini kuzating.
4. Yoshni `150` qilib yuborishga urining. Brauzer `max="80"` tufayli formani yubormaydi va xabar chiqaradi.
5. Endi ikkinchi terminalni ochib, `curl` orqali xuddi shu so‘rovni to‘g‘ridan-to‘g‘ri yuboring:
   ```bash
   curl --noproxy "*" -i http://127.0.0.1:8002/preview \
     --data-urlencode "name=Ali" \
     --data-urlencode "age=150" \
     --data-urlencode "comment=Salom"
   ```
   **Natija:** Server `200 OK` qaytaradi va sahifada `Yosh: 150` deb yoziladi! Bu mijoz tekshiruvi serverni himoya qila olmasligini isbotlaydi (**Dalil D1**).

---

#### 4-qadam: `weak` rejimida tekshirilmagan HTML kiritish (XSS xavfi)
`weak` rejimida izohga quyidagini kiriting:
```html
<b>A2</b>
```
- Ekranda A2 qalin (bold) bo‘lib chiqadi. Inspector orqali `plain` elementi ichida haqiqiy `<b>` tegi paydo bo‘lganini ko‘rasiz.
- Sababi: `plain = Markup(comment)` satri sababli Jinja avtomatik kodlashni bekor qilgan. Foydalanuvchi kiritmasi to‘g‘ridan-to‘g‘ri HTML sifatida talqin qilingan.

---

#### 5-qadam: `safe` rejimiga o‘tish va chegara qiymatlarini sinash
1. Server terminalida `Ctrl+C` bosing va dasturni xavfsiz rejimda ishga tushiring:
   ```bash
   python a2_app.py --mode safe
   ```
2. Yuqoridagi `age=150` so‘rovini `curl` bilan qayta yuboring. Endi server `400 Bad Request` ("Yosh 16-80 oraligida bolishi kerak.") qaytaradi.
3. Chegara qiymatlarini sikl yordamida tekshiring:
   ```bash
   for age in 15 16 80 81 abc 20.0; do
     printf "age=%s status=" "$age"
     curl --noproxy "*" -s -o /dev/null -w "%{http_code}\n" \
       http://127.0.0.1:8002/preview \
       --data-urlencode "name=Ali" \
       --data-urlencode "age=$age" \
       --data-urlencode "comment=Salom"
   done
   ```
   **Kutiladigan HTTP statuslar ketma-ketligi:**
   - `age=15` &rarr; `400` (semantik chegaradan kichik)
   - `age=16` &rarr; `200` (ruxsat etilgan quyi chegara)
   - `age=80` &rarr; `200` (ruxsat etilgan yuqori chegara)
   - `age=81` &rarr; `400` (semantik chegaradan katta)
   - `age=abc` &rarr; `400` (sintaktik xato: raqam emas)
   - `age=20.0` &rarr; `400` (sintaktik xato: faqat butun son qabul qilinadi)

---

#### 6-qadam: Ismni me’yorlashtirish va takroriy maydonlarni tekshirish
1. Ism boshida va oxirida bo‘sh joylar hamda `U+02BB` o‘zbek tutuq belgisi bilan so‘rov yuborish:
   ```bash
   curl --noproxy "*" -i http://127.0.0.1:8002/preview \
     --data-urlencode "name=  Oʻtkir  " \
     --data-urlencode "age=20" \
     --data-urlencode "comment=Salom"
   ```
   **Natija:** `200 OK`. Server ismni `O'tkir` ko‘rinishiga me’yorlashtiradi (bo‘sh joylar o‘chirilgan, apostrof unifikatsiya qilingan).
2. Xato ismlar sinovi:
   - `name=Ali7` &rarr; `400` (raqam taqiqlangan).
   - `name=A` &rarr; `400` (kamida 2 ta belgi bo‘lishi shart).
3. Takroriy parametr (HTTP Parameter Pollution):
   ```bash
   curl --noproxy "*" -i http://127.0.0.1:8002/preview \
     -d "name=Ali&age=20&age=150&comment=Salom"
   ```
   **Natija:** `400 Bad Request` ("Uchta maydonni aynan bir martadan yuboring."). Server noaniq so‘rovlarni qabul qilmaydi.

---

#### 7-qadam: Oddiy matn va HTML sanitizatsiyasini solishtirish
`safe` rejimida izohga quyidagi hujum/tekshiruv fragmentini yuboring:
```html
<b onclick="void(0)">Salom</b><img src=x>
```
Natija sahifasida 3 ta bo‘limni tahlil qiling:
1. **Oddiy matn sifatida (`#plain`):** Barcha belgilar matn sifatida ko‘rsatiladi (`&lt;b onclick...`). Hech qanday HTML ishlamaydi.
2. **Cheklangan HTML sifatida (`#rich`):** Faqat `<b>Salom</b>` qolgan! Xavfli `onclick` atributi va ruxsat berilmagan `<img>` tegi `nh3` tomonidan to‘liq olib tashlangan.
3. **Sanitizatsiyadan keyingi HTML kodi (`#clean-source`):** Tozalangan kod `<b>Salom</b>` ekanligi ko‘rsatiladi (**Dalil D4**).

Mustaqil sinov:
- `<em>Sinov</em>` yuborilsa &rarr; qiya (italic) matn saqlanadi (chunki `em` allowlistda bor).
- `<u>Sinov</u>` yuborilsa &rarr; tagchiziq yo‘qoladi, oddiy matn bo‘lib qoladi (chunki `u` ruxsat ro‘yxatida yo‘q).

---

#### 8-qadam: Xatoliklarni xavfsiz boshqarish (500 Internal Error)
Ichki xatolik yuz berganda server o‘zini qanday tutishini tekshirish:
```bash
curl --noproxy "*" -i http://127.0.0.1:8002/lab-error
```
- **HTTP status:** `500 Internal Server Error`.
- **Foydalanuvchi ko‘radigan javob:** "Ichki xato. Qayd raqami: 3a7b9c1d2e4f" (12 xonali tasodifiy hex). Hech qanday fayl yo‘li yoki traceback yo‘q!
- **Server terminalida:** Xuddi shu `id=3a7b9c1d2e4f` bilan to‘liq traceback jurnali (log) paydo bo‘ladi.

---

#### 9-qadam: Boshqariladigan nosozlik (MAX_AGE buzilishi va tiklash)
1. Serverdagi qoidani sun’iy buzib ko‘rish: `a2_app.py` da `MAX_AGE = 800` qilib o‘zgartiring va serverni qayta ishga tushiring.
2. `curl` orqali `age=150` yuboring &rarr; `200 OK` chiqadi.
   - Brauzer formasida `max="80"` turgani bilan, server qoidasi noto‘g‘ri bo‘lsa tizim zaif bo‘lib qolishi isbotlanadi.
3. `MAX_AGE = 80` qiymatini asl holiga qaytaring va qayta tekshiring:
   - `age=80` &rarr; `200`
   - `age=81` &rarr; `400`
   - `age=150` &rarr; `400`

---

#### 10-qadam: HTTP so‘rov hajmini cheklash (Ixtiyoriy)
8192 baytlik cheklovni tekshirish uchun Python orqali 9000 baytli so‘rov yuboriladi:
```bash
python3 - <<'PYCODE'
import urllib.parse, urllib.request, urllib.error
data = urllib.parse.urlencode(
    dict(name='Ali', age='20', comment='A' * 9000)).encode()
try:
    urllib.request.urlopen('http://127.0.0.1:8002/preview', data=data)
except urllib.error.HTTPError as e:
    print("Qaytgan status kodi:", e.code)
PYCODE
```
**Natija:** `413` (Payload Too Large).

---

### 3.5. Natijalar Jadvali

| Sinov | Rejim | Kutiladigan natija | Haqiqiy natija va Izoh |
| :--- | :--- | :--- | :--- |
| **Brauzer: age=150** | `weak` | POST yuborilmaydi | Brauzer `max="80"` sababli xabar beradi, tarmoqqa so‘rov chiqmaydi |
| **curl: age=150** | `weak` | 200, qiymat qabul | HTTP 200 OK, `Yosh: 150` qabul qilindi (mijoz cheklovi chetlab o‘tildi) |
| **age=15 / 16** | `safe` | 400 / 200 | 15 rad etildi (400), 16 qabul qilindi (200) |
| **age=80 / 81** | `safe` | 200 / 400 | 80 qabul qilindi (200), 81 rad etildi (400) |
| **age=abc / 20.0** | `safe` | 400 / 400 | Ikkalasi ham 400 (faqat ASCII butun sonlar qabul qilinadi) |
| **name=  Oʻtkir  ** | `safe` | 200, O'tkir | 200 OK, bo‘sh joylar qirqildi, apostrof `'` ga keltirildi |
| **name=Ali7 / A** | `safe` | 400 / 400 | 400 (Ali7 da raqam bor, A esa 2 belgidan kam) |
| **age ikki marta** | `safe` | 400 | 400 Bad Request (HTTP Parameter Pollution bloklandi) |
| **comment=`<b>A2</b>`** | `safe` | Plain: literal; rich: qalin | Plain da `<b>A2</b>` matn bo‘lib chiqdi; Rich da esa qalin matn |
| **onclick + img fragmenti** | `safe` | Rich: faqat `<b>Salom</b>` | `onclick` va `<img>` olib tashlandi, faqat xavfsiz `<b>` qoldi |
| **/lab-error** | `safe` | 500, qayd raqami bor | 500, ekranda faqat 12 xonali ID, terminalda traceback |
| **MAX_AGE=800; age=150** | `safe` | 200 — noto‘g‘ri qoida | 200 OK (serverdagi noto‘g‘ri biznes qoidasi oqibati) |
| **Tiklangan; age=80 / 81** | `safe` | 200 / 400 | 80 ga 200 OK, 81 ga 400 Bad Request (qoida tiklandi) |

---

### 3.6. Topshiriladigan Dalillar (D1 — D5)

Hisobot (`A2_1_Guruh_Familiya.docx`) tayyorlashda quyidagi skrinshot va terminal dalillari kiritilishi shart:
- **D1:** Dastur va paket versiyalari (`python -m pip show Flask nh3`); `weak` rejimida brauzer `age=150` ni to‘xtatgani va `curl` orqali aynan shu qiymat `200 OK` olgani.
- **D2:** `safe` rejimida chegara sinovlari (`15, 16, 80, 81, abc, 20.0`), apostrof va bo‘sh joylarning to‘g‘rilanishi, takroriy maydon uchun `400` xatosi.
- **D3:** `<b>A2</b>` kiritmasining `weak` va `safe` rejimlaridagi farqi; DevTools Inspector orqali `plain` va `rich` elementlari DOM tuzilishi.
- **D4:** `<b onclick="void(0)">Salom</b><img src=x>` kiritilganda `rich` ichida atribut va ruxsat etilmagan teglar olib tashlangani; `<em>` saqlanib, `<u>` o‘chirilgani.
- **D5:** `/lab-error` chaqirilganda brauzerdagi 12 xonali qayd raqami va unga mos server terminalidagi log yozuvi; `MAX_AGE=800` qilingandagi va qayta 80 ga tiklangandagi statuslar.

---

### 3.7. Himoya Savollari va Ularning Javoblari

1. **Nega HTMLdagi `max="80"` atributi server tekshiruvining o‘rnini bosa olmaydi?**
   - *Javob:* Chunki HTML atributlari faqat mijoz brauzerida ishlaydi. Tajovuzkor brauzer DevTools orqali bu atributni osongina o‘chirib tashlashi yoki `curl`, Python skript kabi vositalar bilan to‘g‘ridan-to‘g‘ri serverga istalgan qiymatdagi POST so‘rovini yuborishi mumkin. Server mijozdan kelgan har bir so‘rovni mustaqil tekshirishi shart.

2. **`age=abc` va `age=81` rad etilishi qaysi ikki xil tekshiruvga misol bo‘ladi?**
   - *Javob:* `age=abc` — **sintaktik** (format) tekshiruviga misol (kiritma butun son emas). `age=81` esa — **semantik** (biznes mantiq) tekshiruviga misol (format to‘g‘ri son, lekin ruxsat etilgan 16–80 oralig‘idan tashqarida).

3. **NFC bilan apostrofni almashtirish orasida qanday farq bor?**
   - *Javob:* NFC — bu Unicode xalqaro standarti bo‘lib, u birikuvchi belgilar va asosiy harflarni yagona kanonik kompozitsiyaga keltiradi. Apostroflarni (`‘`, `’`, `ʻ`, `ʼ`) standart ASCII `'` belgisiga almashtirish esa NFC ning natijasi emas, balki laboratoriya biznes qoidasi doirasida maxsus yozilgan dasturiy almashtirishdir (`str.maketrans`).

4. **Nega `<b>A2</b>` kodi `plain` ichida oddiy matn, `rich` ichida esa format (qalin matn) sifatida chiqadi?**
   - *Javob:* `plain` qismi shablonga oddiy satr sifatida beriladi va Jinja uni avtomatik kodlaydi (`&lt;b&gt;...`), natijada brauzer uni matn deb tushunadi. `rich` qismi esa avval `nh3` orqali xavfsiz teglarga tekshirilib, so‘ng `Markup(clean)` orqali Jinjaga "ishonchli HTML" sifatida uzatiladi, shu sababli brauzer uni haqiqiy HTML elementi deb chizadi.

5. **`Markup()` funksiyasi sanitizatsiya qiladimi? Uni qaysi qiymatga qo‘llash mumkin?**
   - *Javob:* Yo‘q, `Markup()` hech qanday sanitizatsiya qilmaydi! U shunchaki matnni "xavfsiz" deb belgilab, Jinjaning avtomatik kodlashini o‘chirib qo‘yadi. Uni faqat va faqat qat’iy tekshirilgan yoki `nh3` kabi maxsus vositalar bilan tozalangan (sanitizatsiya qilingan) ma’lumotlarga nisbatan qo‘llash mumkin.

6. **Nega 500 ichki xatolik yuz berganda ekranga traceback emas, qayd raqami (tracking ID) beriladi?**
   - *Javob:* Axborot sizib chiqishining (Information Disclosure) oldini olish uchun. Traceback ichida fayl yo‘llari, baza parollari, kutubxona versiyalari kabi maxfiy ma’lumotlar bo‘ladi. Foydalanuvchiga faqat tasodifiy tracking ID beriladi, dasturchi esa serverdagi xavfsiz loglardan ushbu ID orqali asl muammoni topib o‘rganadi.
