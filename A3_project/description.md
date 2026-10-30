# Veb Dasturlar Xavfsizligi: A3 Amaliy Mashg‘ulot Qo‘llanmasi
**Mavzu:** A3. Mijoz tomoni dasturlash xavfsizligi: JavaScript, DOM va Browser API  
**Variant:** 1-VARIANT — DOMga xavfsiz chiqarish, Fetch API javoblari va brauzer saqlash vositalarini tekshirish  

---

## 1. MAVZUNING MAQSADI VA KUTILADIGAN NATIJALAR

### 1.1. Asosiy maqsad
Ushbu laboratoriya mashg‘ulotining asosiy maqsadi — talabalarda zamonaviy veb-ilovalarning mijoz tomoni (Client-side / Front-end) arxitekturasi va undagi xavfsizlik xatarlarini amaliy tushunish ko‘nikmalarini shakllantirishdir:
1. **Foydalanuvchi ma’lumotlari oqimini kuzatish:** Matn yoki parametrlar mijoz tomonida qanday qabul qilinishi va Document Object Model (DOM) daraxtiga qanday joylashtirilishini tahlil qilish.
2. **Zaif chiqarish nuqtalarini (Sink) topish va tuzatish:** Xavfli usullar (`innerHTML`) orqali yuzaga keladigan DOM XSS zaifligini amalda ko‘rish hamda uni xavfsiz matn chiqarish vositalari (`textContent`) yordamida bartaraf etish.
3. **Fetch API va asinxron javoblarni xavfsiz qayta ishlash:** Serverdan kelayotgan javob statusi (`response.ok`), sarlavhalar (`Content-Type`), MIME turlari va ma’lumotlar sxemasi/tuzilmasini (`typeof`) qat’iy tekshirish.
4. **Brauzer xotirasi xususiyatlari va xavfsizlik chegaralari:** `localStorage` va `sessionStorage` vositalarining Origin bo‘yicha ajratilishi, tablar aro izolyatsiyasi hamda ulardagi ma’lumotlarning JavaScript (XSS) hujumlariga nisbatan zaifligini amaliy isbotlash.
5. **Uchinchi tomon skriptlari xatari:** Tashqi kutubxonalar (`<script src="...">`) sahifa kontekstida to‘liq vakolatga ega bo‘lishini va bu tahdidni cheklash choralarini (SRI va boshqalar) tahlil qilish.

### 1.2. Kutiladigan natijalar
* Talaba DOM-based XSS zaifligini nazorat yozuvi (`flag` markeri: `TAYYOR` -> `DOM-XSS`) orqali isbotlaydi.
* Kodni `textContent` yordamida to‘g‘rilab, qayta sinovdan o‘tkazadi (regressiya testi).
* HTTP 400, noto‘g‘ri MIME turi, noto‘g‘ri JSON strukturasi (`badshape`) va tarmoq uzilishida mijoz dasturi to‘xtab qolmasdan xatolarni to‘g‘ri ushlashini ta’minlaydi.
* Brauzerda saqlangan tokenlar nima sababdan JavaScriptdan himoyalanmaganini, Base64 kodlash yoki o‘zgaruvchi nomini yashirish xavfsizlik bermasligini amaliy dalillar bilan ko‘rsatib beradi.

### 1.3. Mashg‘ulot parametrlari
* **Tavsiya etilgan vaqt:** 80 daqiqa (asosiy laboratoriya ishi).
* **Tarmoq muhiti:** Shaxsiy Wi-Fi (NAT / to‘g‘ridan-to‘g‘ri internet) — hech qanday universitet proksisi yoki murakkab tarmoq sozlamalari talab etilmaydi.
* **Ishchi papka:** `A3_project` katalogining o‘zida barcha fayllar saqlanadi va `uv` orqali virtual muhitda yuritiladi.
* **Laboratoriya manzili:** `http://127.0.0.1:8003/` (mahalliy loopback).
* **Baholash:** Jami 10 ball (D1, D2, D3, D4 dalillari asosida).

---

## 2. FAYLDA KELTIRILGAN BARCHA MAVZULAR BO‘YICHA TO‘LIQ QO‘LLANMA

### 2.1. JavaScript, DOM va Ishonch chegarasi (Trust Boundary)
* **Qayerda qo‘llaniladi?** Veb-brauzerda dinamik foydalanuvchi interfeyslarini yaratishda.
* **Maqsadi va mohiyati:**
  * **DOM (Document Object Model):** Brauzer HTML kodni o‘qib, uni xotirada daraxtsimon obyektlar tuzilmasi ko‘rinishida saqlaydi. Har bir HTML tegi DOM tuguni (Node) hisoblanadi.
  * **Ishonch chegarasi:** Foydalanuvchi klaviaturadan kiritgan matn (`textarea.value`), URL parametrlari, HTTP so‘rov javoblari yoki brauzer omboridagi qiymatlar — bularning barchasi **tashqi va ishonchsiz ma’lumotlar** hisoblanadi.
  * Agar ishonchsiz ma’lumot brauzer tomonidan dastur kodi sifatida talqin qilinsa, xavfsizlik chegarasi buziladi.

---

### 2.2. Source (Manba) va Sink (Chiqarish nuqtasi)
* **Qayerda qo‘llaniladi?** Mijoz tomoni ma’lumotlar oqimi (Taint Analysis / Data Flow) xavfsizlik auditida.
* **Tushunchalar:**
  * **Source (Manba):** Dasturga tashqaridan keladigan, buzg‘unchi manipulyatsiya qilishi mumkin bo‘lgan kiritma nuqtasi (masalan, `textarea.value`, `location.search`, `location.hash`, `document.referrer`).
  * **Sink (Chiqarish nuqtasi):** Olingan qiymatni brauzerga HTML, skript yoki bajariluvchi buyruq sifatida uzatuvchi xavfli funksiya yoki xususiyat (masalan, `innerHTML`, `outerHTML`, `document.write()`, `eval()`, `setTimeout()`).
* **Ushbu laboratoriyadagi zanjir:**  
  `textarea.value` (Source) $\longrightarrow$ `preview.innerHTML` (Sink) $\longrightarrow$ HTML Parser $\longrightarrow$ XSS bajarilishi.

---

### 2.3. `innerHTML` va `textContent` farqi
* **Qayerda qo‘llaniladi?** DOM elementlariga matn yoki kontent chiqarishda.
* **Taqqoslash va xavfsizlik xususiyati:**
  * `element.innerHTML = value`: Kiritilgan qiymatni to‘liq HTML kodi deb hisoblaydi va HTML parser orqali tahlil qiladi. Agar matnda teglar (`<img>`, `<svg>`, `<script>`) yoki hodisalar (`onerror`, `onload`) bo‘lsa, ularni yaratadi va ishga tushiradi. Bu o‘ta xavfli hisoblanadi.
  * `element.textContent = value`: Kiritilgan qiymatni faqat **oddiy matn tuguni (Text Node)** sifatida qo‘shadi. Undagi `<` belgisi ekranda shunchaki matn sifatida chiqadi, teglar bajarilmaydi, brauzer uni kod deb emas, shunchaki xom matn deb biladi.
* **Muhim qoida:** Foydalanuvchi kiritgan ma’lumotlarni matn sifatida chiqarishda har doim `textContent` ishlatilishi shart.

---

### 2.4. DOM-based XSS (Cross-Site Scripting)
* **Qayerda qo‘llaniladi va maqsadi nima?** Buzg‘unchi foydalanuvchi nomidan jabrlanuvchining brauzerida ixtiyoriy JavaScript kodini ishga tushirish uchun ushbu zaiflikdan foydalanadi.
* **Xususiyati:** Stored yoki Reflected XSSdan farqli ravishda, DOM XSSda zararli payload server bazasiga saqlanmasligi yoki serverdan qaytmasligi mumkin. Hujum to‘liq jabrlanuvchining brauzeri ichidagi zaif JavaScript kodi orqali amalga oshadi.
* **Nega `<script>` emas, aynan `<img src="..." onerror="...">` ishlatiladi?**  
  HTML5 spetsifikatsiyasiga ko‘ra, `innerHTML` orqali dinamik qo‘shilgan `<script>` teglari xavfsizlik yuzasidan brauzer tomonidan **avtomatik bajarilmaydi**. Ammo `<img>`, `<svg>`, `<iframe>` kabi elementlar yuklanishda xatoga uchrasa (`onerror`) yoki yuklansa (`onload`), ularning inline hodisa atributlaridagi JavaScript kodi darhol ishga tushadi. Shu sababli DOM XSS sinovlarida hodisa atributli teglar qo‘llaniladi.

---

### 2.5. Fetch API va Asinxron Javoblarni Tekshirish
* **Qayerda qo‘llaniladi?** Sahifani qayta yuklamasdan server bilan ma’lumot almashishda (AJAX).
* **Maqsadi va xavfsiz qayta ishlash qoidalari:**
  1. **HTTP Status tekshiruvi (`response.ok`):** `fetch()` funksiyasi faqat tarmoq butunlay uzilgandagina Promise’ni rad etadi (`catch`). Server `400 Bad Request`, `404 Not Found` yoki `500 Server Error` qaytarsa ham `fetch` buni muvaffaqiyatli so‘rov deb biladi. Shu sababli dasturchi alohida `if (!response.ok)` sharti orqali statusni tekshirishi shart.
  2. **MIME turi (`Content-Type`) tekshiruvi:** Serverdan JSON kutilganda, uning sarlavhasi `application/json` ekanligi tekshirilishi lozim. Server kutilmaganda HTML yoki matn qaytarsa, `response.json()` sintaksis xatosiga uchraydi.
  3. **Ma’lumot tuzilmasi tekshiruvi:** Status 200 bo‘lsa ham, server yuborgan ma’lumot formati kutilganidek bo‘lmasligi mumkin (masalan, string o‘rniga number yoki bo‘sh obyekt). Shu sababli `typeof data.text !== 'string'` kabi tekshiruvlar talab etiladi.
  4. **Kutish chegarasi (`AbortController`):** Tarmoq sekinlashganda yoki server javob bermay qotib qolganda so‘rov abadiy osilib qolmasligi uchun `AbortController` yordamida timeout (masalan, 3 soniya) o‘rnatiladi.
  5. **`finally` bloki:** Har qanday holatda (muvaffaqiyat yoki xatolik) bloklangan tugmani qayta faollashtirish (`button.disabled = false`) uchun qo‘llaniladi.

---

### 2.6. Brauzer Omborlari: `localStorage` va `sessionStorage`
* **Qayerda qo‘llaniladi?** Mijoz tomonida sozlamalar, sessiya holatlari va kesh ma’lumotlarini saqlashda.
* **Taqqoslash:**

| Xususiyat | `localStorage` | `sessionStorage` |
| :--- | :--- | :--- |
| **Izolyatsiya (Scoping)** | Same-Origin bo‘yicha | Same-Origin + joriy Tab/Oyna sessiyasi bo‘yicha |
| **Saqlanish muddati** | Doimiy (brauzer yopilsa ham o‘chmaydi) | Faqat tab ochiq turguncha (tab yopilsa o‘chadi) |
| **Yangi tab ochilganda** | Qiymatlar yangi tabda ham ko‘rinadi | Yangi mustaqil tabda qiymat mavjud bo‘lmaydi (`null`) |
| **XSS hujumiga munosabati** | **Zaif!** JavaScript erkin o‘qiy oladi | **Zaif!** Shu tabda ishlayotgan JavaScript o‘qiy oladi |

* **Xavfsizlik xulosasi:**
  * Hech qachon maxfiy autentifikatsiya tokenlarini (JWT, Session ID) `localStorage` yoki `sessionStorage`da saqlamaslik kerak.
  * Ularni Base64 kodlash yoki o‘zgaruvchi nomini chalg‘ituvchi qilib yozish XSSdan himoya qilmaydi.
  * To‘g‘ri yechim — sessiya identifikatorlarini `HttpOnly`, `Secure`, `SameSite` bayroqlari o‘rnatilgan Cookie fayllarida saqlashdir (`HttpOnly` kuki JavaScript orqali o‘qilishining oldini oladi).

---

### 2.7. Uchinchi tomon skriptlari (Third-Party Scripts) va SRI
* **Qayerda qo‘llaniladi?** Sahifaga tashqi kutubxonalar (jQuery, Bootstrap, tahliliy vositalar) ulashda.
* **Xatarlar:**
  * Oddiy `<script src="vendor.js">` orqali yuklangan har qanday kod asosiy sahifaning to‘liq huquqli JavaScript kontekstida bajariladi.
  * Uchinchi tomon skripti DOMni o‘zgartirishi yoki `localStorage`dagi ma’lumotlarni erkin o‘qishi mumkin.
* **SRI (Subresource Integrity):**
  * `<script src="..." integrity="sha384-..." defer></script>`
  * **Maqsadi:** Faylning kriptografik xeshini tekshirish. Agar faylga o‘zgartirish kiritilgan bo‘lsa, brauzer uni bajarishdan bosh tortadi.
  * **Cheklovi:** SRI skriptning boshlang‘ich logikasi xavfsiz ekanini kafolatlamaydi, u faqat fayl uzatish davomida o‘zgarmaganini tekshiradi.

---

## 3. VAZIFANI BOSQICHMA-BOSQICH BAJARISH TARTIBI

### 0-BOSQICH: Tarmoq va ishchi muhit (O‘z Wi-Fi tarmog‘ingizda)

Bu ish uchun hech qanday universitet proksisi yoki murakkab tarmoq yo‘riqnomalari kerak emas.
1. O‘zingizning Wi-Fi (yoki oddiy NAT) ulanishingiz yetarli.
2. Tizimda Python 3, `curl` va `uv` mavjud bo‘lsa bas.

---

### 1-BOSQICH: `A3_project` papkasida `uv` orqali muhit yaratish va fayllarni joylashtirish

Barcha 4 ta kod fayli aynan shu loyiha papkasining o‘ziga (`A3_project`) joylashtiriladi:
* `server.py`
* `index.html`
* `app.js`
* `vendor.js`

#### 1. Loyiha papkasiga o‘tish va `uv` orqali virtual muhit (`.venv`) yaratish:
Terminalda quyidagi buyruqlarni bajaring:
```bash
cd /home/maxfull/Downloads/507-LAB/projects/web-application-security-labs/A3_project

# uv orqali .venv yaratish
uv venv

# Virtual muhitni faollashtirish
source .venv/bin/activate
```
> **Izoh:** Ushbu loyihada `server.py` faqat Pythonning standart kutubxonalaridan (`http.server`, `json`, `urllib.parse`, `pathlib`) foydalanadi, shuning uchun qo‘shimcha pip paketlari o‘rnatish shart emas. `uv venv` orqali ishlash tizim Python muhitini toza va xavfsiz saqlash imkonini beradi.

---

#### 2. Fayllarni yaratish va to‘liq kodlarini joylashtirish:

Ushbu papka (`A3_project`) ichida 4 ta faylni quyidagi kodlar bilan yarating:

##### A. `server.py` fayli:
```python
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
    print('A3: http://127.0.0.1:8003/', flush=True)
    HTTPServer(('127.0.0.1', 8003), Handler).serve_forever()
```

##### B. `index.html` fayli:
```html
<!doctype html>
<html lang="uz">
<head>
    <meta charset="utf-8">
    <title>A3: mijoz tomoni xavfsizligi</title>
    <style>
        body {font: 18px sans-serif; max-width: 850px; margin: 30px auto;}
        textarea {width: 95%; height: 75px;}
        section {border: 1px solid #aaa; padding: 15px; margin: 15px 0;}
        pre {white-space: pre-wrap; overflow-wrap: anywhere;}
        button {margin: 4px; padding: 8px;}
    </style>
</head>
<body>
    <h1>A3: DOM, Fetch va Web Storage</h1>
    <p>Faqat mahalliy o'quv tajribasi. Haqiqiy token kiritmang.</p>
    <label for="input">Sinov matni:</label><br>
    <textarea id="input">Salom, A3!</textarea>

    <section>
        <h2>1. DOM</h2>
        <button id="weak">Zaif chiqarish</button>
        <button id="safe">Xavfsiz chiqarish</button>
        <button id="reset">DOMni tozalash</button>
        <p>Marker: <strong id="flag">TAYYOR</strong></p>
        <div id="preview"></div>
    </section>

    <section>
        <h2>2. Fetch API</h2>
        <button id="fetch">API so'rovi</button>
        <p id="status">So'rov yuborilmadi.</p>
        <pre id="api"></pre>
    </section>

    <section>
        <h2>3. Uchinchi tomon skripti maketi</h2>
        <p id="vendor">Skript hali ishlamadi.</p>
    </section>

    <script src="app.js" defer></script>
    <script src="vendor.js" defer></script>
</body>
</html>
```

##### C. `vendor.js` fayli:
```javascript
'use strict';
// Local mock: no network request and no real credential.
const demo = localStorage.getItem('a3_demo_token');
document.getElementById('vendor').textContent =
    "Vendor skripti o‘qigan qiymat: " + (demo || 'YOQ');
```

##### D. `app.js` fayli (Boshlang‘ich, zaif versiya):
```javascript
'use strict';
const byId = id => document.getElementById(id);
const input = byId('input');
const preview = byId('preview');

function resetDOM() {
    preview.replaceChildren();
    byId('flag').textContent = 'TAYYOR';
}

byId('weak').addEventListener('click', () => {
    resetDOM();
    preview.innerHTML = input.value; // Deliberately unsafe lab sink.
});

byId('safe').addEventListener('click', () => {
    resetDOM();
    preview.textContent = input.value;
});

byId('reset').addEventListener('click', resetDOM);

async function loadAPI() {
    const button = byId('fetch');
    button.disabled = true;
    byId('api').textContent = '';
    byId('status').textContent = 'Yuklanmoqda...';
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 3000);

    try {
        const params = new URLSearchParams({q: input.value});
        const response = await fetch('/api/echo?' + params, {
            signal: controller.signal, credentials: 'omit', cache: 'no-store'
        });
        if (!response.ok) throw new Error('HTTP ' + response.status);

        const kind = (response.headers.get('Content-Type') || '')
            .split(';')[0].trim().toLowerCase();
        if (kind !== 'application/json') {
            throw new Error('JSON javob kutilgan edi.');
        }

        const data = await response.json();
        if (!data || typeof data.text !== 'string') {
            throw new Error("Javob tuzilmasi noto‘g‘ri.");
        }

        byId('api').textContent = data.text;
        byId('status').textContent = 'Muvaffaqiyat: HTTP 200';
    } catch (error) {
        const message = error.name === 'AbortError'
            ? 'Kutish vaqti tugadi.' : error.message;
        byId('status').textContent = 'Xato: ' + message;
    } finally {
        clearTimeout(timer);
        button.disabled = false;
    }
}

byId('fetch').addEventListener('click', loadAPI);
```

---

#### 3. Serverni `uv` yordamida ishga tushirish va tekshirish:
```bash
# Serverni ishga tushirish (ikkala usul ham ishlaydi):
uv run python server.py
# Yoki faollashtirilgan .venv muhitida:
python server.py
```
Server terminalida `A3: http://127.0.0.1:8003/` xabari chiqadi. Uni ochiq qoldiring.

Ikkinchi terminal ochib, HTTP javoblarni tekshiring:
```bash
curl -i http://127.0.0.1:8003/
curl -i "http://127.0.0.1:8003/api/echo?q=Salom"
```
*(Kutilgan natija: ikkala so‘rovda status 200 OK, API javobi esa `{"text": "Salom"}` bo‘ladi).*

Brauzerda (Firefox yoki Chrome) `http://127.0.0.1:8003/` manzilini oching. F12 tugmasini bosib Developer Tools oynasini oching va Network bo‘limida **Disable Cache** bandini yoqing.

---

### 2-BOSQICH: DOMga zaif va xavfsiz chiqarishni taqqoslash (D1 dalili)

1. Textarea maydoniga `Salom, A3!` deb yozing.
   * **"Zaif chiqarish"** va **"Xavfsiz chiqarish"** tugmalarini navbat bilan bosing. Natija oddiy matnda bir xil chiqadi.
2. Endi textarea maydoniga HTML tegli matn kiriting: `<b>A3</b>`
   * **"Zaif chiqarish"** tugmasini bosing: Matn qalin (**A3**) ko‘rinadi.
   * **"Xavfsiz chiqarish"** tugmasini bosing: Teglar matn sifatida ko‘rinadi (`<b>A3</b>`).
   * F12 -> **Inspector** bo‘limida tekshiring: 1-holatda DOM ichida haqiqiy `<b>` elementi paydo bo‘ladi, 2-holatda esa shunchaki matn tuguni (Text Node) turadi.

---

### 3-BOSQICH: DOM XSS zaifligini aniqlash (D1 dalili davomi)

1. Textarea ichiga quyidagi bir qatorli zararli test matnini kiriting:
   ```html
   <img src="/a3-missing.png" onerror="document.getElementById('flag').textContent='DOM-XSS'">
   ```
2. **"Zaif chiqarish"** tugmasini bosing:
   * Brauzer `/a3-missing.png` faylini yuklashga urinadi va topolmay 404 xatolik oladi (bu Network oynasida ko‘rinadi va kutilgan holat).
   * Rasm yuklanmagani sababli uning `onerror` hodisasi ishga tushadi.
   * **Natija:** Sahifadagi `Marker: TAYYOR` yozuvi `DOM-XSS` ga aylanadi! Bu DOM XSS zaifligi muvaffaqiyatli sodir bo‘lganini isbotlaydi.
3. Ayni shu matn turgan holatda **"Xavfsiz chiqarish"** tugmasini bosing:
   * `resetDOM` funksiyasi eski elementni tozalaydi, marker yana `TAYYOR` holatiga qaytadi.
   * Textarea matni to‘lig‘icha oddiy matn sifatida ekranda chiqadi, yangi `<img>` tegi yaratilmaydi va tarmoqda yangi 404 xatosi chiqmaydi.
4. **Mustaqil tekshiruv:** `A & B < C` matnini yuborib ko‘ring. Xavfsiz rejimda belgilar yo‘qolmasdan to‘liq matn bo‘lib chiqishini kuzating.
> **Hisobot uchun D1 dalili:** Zaif holatda marker `DOM-XSS` bo‘lgani va xavfsiz holatda `TAYYOR` qolgani hamda Inspector ko‘rinishlarini skrinshot qilib oling.

---

### 4-BOSQICH: Fetch API javoblari va xatoliklarni sinash (D2 dalili)

1. **"DOMni tozalash"** tugmasini bosing.
2. Sinov matniga `<b>A3</b>` yozib, **"API so'rovi"** tugmasini bosing:
   * Status: `HTTP 200`. Natija `textContent` orqali chiqarilgani sababli `<b>A3</b>` oddiy matn bo‘lib turadi.
3. DOM XSS matnini (`<img src=... onerror=...>`) API orqali yuboring:
   * Marker `TAYYOR` bo‘lib qoladi, kod bajarilmaydi.
4. **Xatolik ssenariylari:**
   * **Bo‘sh kiritma:** Textareadagi hamma narsani o‘chirib bo‘sh qoldiring va **"API so'rovi"** tugmasini bosing.  
     *Natija:* Status `HTTP 400`, interfeysda `Xato: HTTP 400` chiqadi.
   * **Noto‘g‘ri ma’lumot tuzilmasi (badshape):** Textareaga `badshape` deb yozib, tugmani bosing.  
     *Natija:* Server `{"text": 123}` (satr emas, raqam) qaytaradi. `typeof data.text !== 'string'` sharti ishlab, interfeysda `Xato: Javob tuzilmasi noto‘g‘ri.` xabari ko‘rinadi.
   * **Server uzilishi (Network failure):** Terminalda `Ctrl+C` bosib Python serverni to‘xtatib qo‘ying. Sahifani yangilamasdan brauzerdagi **"API so'rovi"** tugmasini bosing.  
     *Natija:* Tarmoq xatosi chiqadi va tugma qayta faollashadi. So‘ng serverni yana qayta ishga tushiring (`uv run python server.py`).

---

### 5-BOSQICH: Boshqariladigan nosozlik — MIME turini buzish (D2 dalili davomi)

1. `server.py` faylidan nusxa oling:
   ```bash
   cp server.py server.original.py
   ```
2. `server.py` faylidagi `/api/echo` qismida javob sarlavhasini vaqtincha o‘zgartiring:
   * Eski: `return self.reply(status, body, 'application/json; charset=utf-8')`
   * Yangi: `return self.reply(status, body, 'text/plain; charset=utf-8')`
3. Serverni qayta ishga tushiring.
4. Brauzerda `Salom` deb yozib, **"API so'rovi"** tugmasini bosing:
   * Status 200 bo‘lsa ham, sarlavha `text/plain` bo‘lgani sababli `app.js` uni rad etadi va `Xato: JSON javob kutilgan edi.` chiqadi.
5. Asl faylni tiklang:
   ```bash
   cp server.original.py server.py
   ```
   Serverni qayta ishga tushiring.
> **Hisobot uchun D2 dalili:** 200, 400, badshape, tarmoq xatosi va noto‘g‘ri Content-Type holatlari aks etgan skrinshotlarni saqlang.

---

### 6-BOSQICH: `localStorage` va `sessionStorage` bilan tajriba (D3 dalili)

1. Brauzerda F12 ni ochib, **Console** bo‘limiga kiring va quyidagi buyruqlarni bajaring:
   ```javascript
   localStorage.setItem('a3_theme', 'dark');
   sessionStorage.setItem('a3_tab', 'birinchi');
   localStorage.setItem('a3_demo_token', 'DEMO-A3-NOT-SECRET');
   localStorage.getItem('a3_theme');
   sessionStorage.getItem('a3_tab');
   ```
2. F12 ning **Storage** (Xotira) bo‘limiga o‘ting:
   * `Local Storage -> http://127.0.0.1:8003`: `a3_theme` va `a3_demo_token` saqlangan.
   * `Session Storage -> http://127.0.0.1:8003`: `a3_tab` saqlangan.
3. Joriy sahifani yangilang (`F5`): Har ikkala omborda qiymatlar saqlanib qoladi.
4. **Yangi mustaqil tab ochish:**
   * Brauzerda `Ctrl+T` bilan yangi tab oching (eski tabni nusxalamang/duplicate qilmang).
   * Manzil satriga yozing: `http://127.0.0.1:8003/`.
   * Yangi tab Console oynasida tekshiring:
     ```javascript
     localStorage.getItem('a3_theme');     // "dark" qaytadi (saqlangan)
     sessionStorage.getItem('a3_tab');      // null qaytadi (tab alohida!)
     localStorage.getItem('a3_demo_token'); // "DEMO-A3-NOT-SECRET" qaytadi
     ```

---

### 7-BOSQICH: Uchinchi tomon skriptining imkoniyatlari (D3 dalili davomi)

1. Sahifani yangilang (`Ctrl+Shift+R`):
   * 3-bo‘limda **"Vendor skripti o‘qigan qiymat: DEMO-A3-NOT-SECRET"** ko‘rinadi.
   * Bu `vendor.js` sahifadagi `localStorage` ma’lumotlarini to‘siqsiz o‘qiy olishini ko‘rsatadi.
2. Tokenni o‘chirib, sahifani yangilang:
   ```javascript
   localStorage.removeItem('a3_demo_token');
   location.reload();
   ```
   * Endi vendor bo‘limida **"Vendor skripti o‘qigan qiymat: YOQ"** paydo bo‘ladi.
> **Hisobot uchun D3 dalili:** Yangi tabdagi `null` natijasi hamda vendor bo‘limida token o‘qilgan va o‘chirilgan holatlar skrinshotini saqlang.

---

### 8-BOSQICH: Zaif nuqtani tuzatish va qayta tekshirish (D4 dalili)

1. `app.js` faylini nusxalang va tahrirlang:
   ```bash
   cp app.js app.original.js
   nano app.js
   ```
2. `weak` tugmasi tinglovchisidagi zaif satrni almashtiring:
   * **Eski zaif satr:**
     ```javascript
     preview.innerHTML = input.value; // Deliberately unsafe lab sink.
     ```
   * **Yangi xavfsiz satr:**
     ```javascript
     preview.textContent = input.value;
     ```
3. Faylni saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`).
4. Brauzerda keshsiz yangilang (`Ctrl+Shift+R`).
5. **Qayta tekshirish (Regressiya testi):**
   * Textarea maydoniga yana o‘sha DOM XSS kodini kiriting:
     ```html
     <img src="/a3-missing.png" onerror="document.getElementById('flag').textContent='DOM-XSS'">
     ```
   * Aynan **"Zaif chiqarish"** tugmasini bosing!
   * **Natija:** Marker **TAYYOR** holatida o‘zgarmay qolishi kerak! Rasm kodi oddiy matn sifatida xavfsiz ko‘rinadi, `onerror` kodi mutlaqo bajarilmaydi.
> **Hisobot uchun D4 dalili:** `app.js`dagi o‘zgartirilgan kod hamda tuzatilgan tugmada XSS kodi oddiy matn bo‘lib chiqqani, marker `TAYYOR`ligicha qolgani skrinshotini oling.

---

### 9-BOSQICH (Ixtiyoriy qo‘shimcha): Subresource Integrity (SRI) sinovi

1. `vendor.js` faylining SHA-384 xeshini hisoblang:
   ```bash
   python3 - <<'PYHASH'
   from pathlib import Path
   import hashlib, base64
   digest = hashlib.sha384(Path('vendor.js').read_bytes()).digest()
   print('sha384-' + base64.b64encode(digest).decode())
    python3 - <<'PYHASH'
   from pathlib import Path
   import hashlib, base64
   digest = hashlib.sha384(Path('vendor.js').read_bytes()).digest()
   print('sha384-' + base64.b64encode(digest).decode())
   PYHASH  PYHASH
   ```
2. Chiqqan qiymatni nusxalab, `index.html`dagi skript tegiga yozing:
   ```html
   <script src="vendor.js" integrity="sha384-HISOBLANGAN_XESH" defer></script>
   ```
3. Brauzerni yangilang: skript xatosiz ishlaydi.
4. `vendor.js` fayli oxiriga bitta qator izoh qo‘shib o‘zgartiring:
   ```bash
   echo "// A3 change" >> vendor.js
   ```
5. Sahifani keshsiz yangilang (`Ctrl+Shift+R`):
   * Console oynasida qizil bilan **Integrity / Hash mismatch** xatosi chiqadi!
   * Brauzer o‘zgargan skriptni bloklaydi.
6. Sinov tugagach faylni tiklang: `git checkout vendor.js` yoki nusxasidan qaytaring.

---

### 10-BOSQICH: Tozalash va hisobotni yakunlash

1. Brauzer konsolida test ma’lumotlarini tozalang:
   ```javascript
   localStorage.removeItem('a3_theme');
   sessionStorage.removeItem('a3_tab');
   localStorage.removeItem('a3_demo_token');
   ```
2. Serverni to‘xtating (`Ctrl+C`).
3. To‘plangan 4 ta dalil (D1, D2, D3, D4) skrinshotlari va tuzatilgan fayllar asosida hisobotni rasmiylashtiring.

---

## 4. TOPSHIRIQLAR NATIJA JADVALI

Laboratoriya tajribalari davomida olingan amaliy natijalar qaydnomasi:

|   №    | Sinov nomi                      | Kutiladigan natija                           | Amaldagi natija va dalil                                                  |
| :----: | ------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------- |
| **1**  | Boshlang‘ich sahifa va API      | HTTP 200; JS fayllari to‘liq yuklangan       | Status 200 OK; app.js va vendor.js xatosiz yuklandi                       |
| **2**  | `<b>A3</b>`: zaif / xavfsiz     | `<b>` elementi / oddiy matn tuguni           | Zaif tugmada A3 qalin ko‘rindi, xavfsiz tugmada teglar matn bo‘lib chiqdi |
| **3**  | DOM XSS: zaif tugma             | Marker `DOM-XSS` bo‘ladi; `<img>` yaratiladi | Marker `DOM-XSS`ga o‘zgardi, tarmoqda 404 xatosi chiqdi                   |
| **4**  | DOM XSS: xavfsiz tugma          | Marker `TAYYOR` qoladi; `<img>` yaratilmaydi | Marker `TAYYOR` holatida qoldi, matn oddiy ko‘rindi                       |
| **5**  | Fetch: DOM sinov matni          | 200 OK; matn chiqadi; kod bajarilmaydi       | Status 200; img kodi matn bo‘lib chiqdi, xavfsiz                          |
| **6**  | Fetch: bo‘sh kiritma            | 400 Bad Request; natija maydoni bo‘sh        | Interfeysda `Xato: HTTP 400` chiqdi, maydon tozalandi                     |
| **7**  | Fetch: `badshape`               | 200 OK; tuzilma xatosi                       | `Xato: Javob tuzilmasi noto‘g‘ri.` xabari chiqdi                          |
| **8**  | API MIME turini buzish          | 200 OK; JSON turi xatosi                     | `Xato: JSON javob kutilgan edi.` chiqdi                                   |
| **9**  | Serverni to‘xtatish / tiklash   | Tarmoq xatosi; tugma qayta faollashadi       | Xatolik chiqdi, tugma `finally` bloki orqali yana faollashdi              |
| **10** | Omborlar: yangi mustaqil tab    | local: `dark`; session: `null`               | Yangi tabda `localStorage` qiymati qoldi, `sessionStorage` null bo‘ldi    |
| **11** | Vendor: token bor / o‘chirilgan | `DEMO-A3-NOT-SECRET` / `YOQ`                 | Token mavjud paytda o‘qidi, `removeItem`dan so‘ng `YOQ` chiqdi            |
| **12** | Zaif sink tuzatilgandan keyin   | Marker `TAYYOR`; matn to‘liq chiqadi         | Zaif tugma bosilganda ham marker o‘zgarmadi (`TAYYOR`)                    |
| **13** | SRI: o‘zgargan / tiklangan fayl | Bloklanadi / ishlaydi (ixtiyoriy)            | Izoh qo‘shilganda brauzer skriptni blokladi                               |

---

## 5. QO‘SHIMCHA VA RASMIY FOYDALI MANBALAR

1. **OWASP DOM based XSS Prevention Cheat Sheet:**  
   [https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)  
   *DOMdagi manbalar, xavfli sinklar va ulardan xavfsiz qochish (escaping/encoding) qoidalari.*
2. **OWASP Cross Site Scripting Prevention Cheat Sheet:**  
   [https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)  
   *XSS turlari va kontekstual xavfsizlik choralari.*
3. **MDN Web Docs — Using the Fetch API:**  
   [https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)  
   *Asinxron so‘rovlar, Response statusi, sarlavhalar va AbortController qo‘llanilishi.*
4. **OWASP HTML5 Security Cheat Sheet:**  
   [https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)  
   *Web Storage (`localStorage`/`sessionStorage`), Web Workers va HTML5 API xavfsizlik chegaralari.*
5. **MDN Web Docs — Window: localStorage & sessionStorage:**  
   [https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)  
   [https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage)  
   *Brauzer omborlari arxitekturasi va Origin tushunchasi.*
6. **OWASP Third Party JavaScript Management:**  
   [https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html)  
   *Tashqi kutubxonalar xavfini kamaytirish va boshqarish usullari.*
7. **MDN Web Docs — Subresource Integrity (SRI):**  
   [https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Subresource_Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Subresource_Integrity)  
   *Tashqi CDN resurslarining yaxlitligini tekshirish uchun kriptografik xeshlar bilan ishlash.*
8. **Python rasmiy hujjati — `http.server` moduli:**  
   [https://docs.python.org/3/library/http.server.html](https://docs.python.org/3/library/http.server.html)  
   *Lokal sinovlar uchun BaseHTTPRequestHandler va HTTPServer sozlash.*
