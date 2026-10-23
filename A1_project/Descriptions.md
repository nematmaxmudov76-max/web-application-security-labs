# Veb Dasturlar Xavfsizligi — A1 Laboratoriya Ishi: To'liq Qo'llanma

**Mavzu:** Veb texnologiyalar arxitekturasi va brauzer xavfsizlik modeli  
**Variant:** 1-VARIANT — Ikki originli veb laboratoriyada HTTP, DOM, cookie, SOP, CORS va CSP ni tekshirish  
**Moslashtirilgan muhit:** Ubuntu Host tizimi + VM ichida Ubuntu Live Server (yoki to'g'ridan-to'g'ri Ubuntu muhiti)

---

## Kirish: Laboratoriya Ishining Mohiyati va Muhit Tahlili

Universitet tomonidan berilgan asl topshiriqda Windows 11 operatsion tizimi, VMware Workstation va SMB fayl serveri (`\\172.18.233.234\files`) orqali Desktop obrazini yuklab olish ko'rsatilgan. 

Biroq, siz **Ubuntu muhitida** ishlayotganingiz va vazifalarni **VM ichida Ubuntu Live Server** (GUI interfeysga ega bo'lmagan, faqat terminal/CLI bilan ishlovchi server) orqali bajarmoqchi bo'lganingiz sababli, quyidagi asosiy masalani to'g'ri anglash muhim:

> **Muhim arxitekturaviy eslatma:**  
> Ushbu laboratoriya ishining asosiy o'rganish obyekti **brauzer xavfsizlik modeli** hisoblanadi (DOM manipulyatsiyasi, DevTools Inspector, Network, Storage tablari, Console xatolari, SOP va CSP cheklovlari).  
> Ubuntu Live Server'da grafik interfeys (GUI) va brauzer (Firefox/Chrome) mavjud emas. Shuning uchun, vazifani bajarishda **eng professional va qulay usul**:
> 1. Python veb-serverlarini (`127.0.0.1:8000` va `127.0.0.1:8001`) VM ichidagi **Ubuntu Live Server**da yurgizish.
> 2. Ushbu portlarni SSH port-forwarding orqali o'zingizning **Ubuntu Host** tizimingizga yo'naltirish (yoki laboratoriyani to'g'ridan-to'g'ri o'zingizning Ubuntu tizimingizda yurgizish).
> 3. Brauzer tajribalarini (Firefox + F12 DevTools) o'z tizimingizdagi Firefox orqali o'tkazish.

Quyida barcha talab qilingan 4 ta bo'lim batafsil yoritilgan.

---

## *0* Kerakli Vositalar (Tools) va Ularni O'rnatish

Laboratoriyani boshlashdan oldin talab qilinadigan barcha operatsion tizim vositalarini o'rnatib olishimiz zarur.

### 0.1. Agar vazifani VM ichidagi Ubuntu Live Server'da bajarsangiz:

Serveringiz terminaliga (SSH yoki VM konsoliga) kiring va quyidagi buyruqlarni bajaring:

```bash
# 1. Paketlar ro'yxatini yangilash
sudo apt update

# 2. Asosiy dasturlarni o'rnatish:
# - python3: server dasturini ishga tushirish uchun
# - curl: HTTP so'rovlarini terminal orqali jo'natish va taqqoslash uchun
# - nano: kod va konfiguratsiyalarni tahrirlash uchun
# - iproute2: portlarni kuzatish uchun (ss buyrug'i)
# - openssh-server: Host tizimidan portlarni yo'naltirish uchun
sudo apt install -y python3 curl nano iproute2 openssh-server

# 3. O'rnatilgan versiyalarni tekshirish
python3 --version
curl --version
ss --version
```

### 0.2. Sizning asosiy tizimingizda (Ubuntu Host) kerakli vositalar:

Brauzer tajribalari va DevTools uchun asosiy Ubuntu tizimingizda Firefox (yoki Chromium) bo'lishi shart:

```bash
# Firefox o'rnatilganligini tekshirish
firefox --version

# Agar o'rnatilmagan bo'lsa:
sudo snap install firefox
# yoki:
# sudo apt install -y firefox
```

### 0.3. Ubuntu Live Server portlarini Host tizimiga bog'lash (SSH Port-Forwarding):

Laboratoriya kodi `127.0.0.1` (loopback) manziliga bog'langan. Ubuntu Live Server ichidagi portlarni asosiy tizimingiz brauzerida xuddi o'z kompyuteringizdek ochish uchun, Host kompyuteringiz terminalida ushbu buyruqni bering:

```bash
# <server_ip> o'rniga VM ning IP manzilini, <username> o'rniga server foydalanuvchi nomini yozing
ssh -L 8000:127.0.0.1:8000 -L 8001:127.0.0.1:8001 <username>@<server_ip>
```
*Bu buyruq VM ichidagi `127.0.0.1:8000` va `8001` portlarini Host tizimingizdagi `127.0.0.1:8000` va `8001` ga xavfsiz ulab beradi.*

---

## *1* Mavzuning To'liq Nazariy Qo'llanmasi

Ushbu laboratoriya zamonaviy veb arxitekturasining poydevori va brauzer darajasidagi xavfsizlik cheklovlarini o'rganishga bag'ishlangan.

### 1.1. Veb Texnologiyalar Arxitekturasi
Klassik veb ilovalar 3 ta asosiy qatlamdan tashkil topadi:
1. **Mijoz (Brauzer):** Foydalanuvchiga interfeysni ko'rsatadi, JavaScript dastur kodini ishga tushiradi, foydalanuvchi harakatlarini boshqaradi.
2. **Veb Server (Origin A — `127.0.0.1:8000`):** Asosiy statik resurslarni (`index.html`, `style.css`, `app.js`) yetkazib beradi.
3. **API Server (Origin B — `127.0.0.1:8001`):** Dinamik ma'lumotlarni JSON formatida taqdim etuvchi xizmat.

Ushbu qatlamda ishlatiladigan texnologiyalar vazifasi:
* **HTML (HyperText Markup Language):** Sahifaning strukturasi va semantik skeletini belgilaydi.
* **CSS (Cascading Style Sheets):** Sahifaning vizual ko'rinishi, shriftlar, ranglar va joylashuv tartibini ta'minlaydi.
* **JavaScript:** Sahifani dinamik qiladi, DOM obyektlarini o'zgartiradi va serverdan asinxron tarzda (`fetch()`) ma'lumot yuklaydi.
* **DOM (Document Object Model):** Brauzer xotirasida HTML hujjatining daraxtsimon (tree) obyekt modeli. JavaScript aynan shu model orqali elementlarni boshqaradi.

---

### 1.2. Origin (Manba) Chegarasi nima?

Xavfsizlik siyosatlarini tushunish uchun **Origin** nimaligini aniq bilish shart.
Origin 3 ta komponentdan tashkil topadi:
$$\text{Origin} = \text{Sxema (Protokol)} + \text{Host (Domen yoki IP)} + \text{Port}$$

Agar ushbu 3 ta komponentdan bittasi ham farq qilsa, brauzer ularni **BOSHQACHA ORIGIN (Cross-Origin)** deb hisoblaydi! URL manzildagi yo'l (path, masalan `/api/info`, `/profile`) origin hisobiga kirmaydi.

#### 3.2-jadval tahlili (Tayanch origin: `http://127.0.0.1:8000`):
| Taqqoslanadigan URL             | Bir xilmi? (Same-origin?) | Sabab                                                                                                                     |
| :------------------------------ | :------------------------ | :------------------------------------------------------------------------------------------------------------------------ |
| `http://127.0.0.1:8000/profile` | **HA (Bir xil)**          | Sxema (`http`), Host (`127.0.0.1`) va Port (`8000`) bir xil. Faqat URL yo'li farq qiladi, yo'l origin tarkibiga kirmaydi. |
| `http://127.0.0.1:8001/`        | **YO'Q (Farqli)**         | Port farq qiladi (`8000` emas, `8001`). Port farq qilishi alohida origin yaratadi.                                        |
| `http://localhost:8000/`        | **YO'Q (Farqli)**         | Host satri farq qiladi (`127.0.0.1` bilan `localhost` brauzer uchun har xil host nomlari).                                |
| `https://127.0.0.1:8000/`       | **YO'Q (Farqli)**         | Sxema (protokol) farq qiladi (`http` emas, `https`).                                                                      |
| `http://127.0.0.1/`             | **YO'Q (Farqli)**         | Ochiq ko'rsatilmagan HTTP porti sukut bo'yicha `80` hisoblanadi (`8000` != `80`).                                         |

---

### 1.3. SOP (Same-Origin Policy — Bir Xil Manba Siyosati)
* **Maqsadi:** Zararli saytlardagi skriptlar foydalanuvchining boshqa saytlardagi (masalan, bank yoki pochta) shaxsiy ma'lumotlarini o'qib olishini taqiqlash.
* **Eng muhim tamoyil:** SOP brauzerning tarmoq so'rovini yuborishiga to'sqinlik qilmaydi (ko'pincha so'rov serverga boradi va server HTTP 200 javob qaytaradi). SOP brauzer ichidagi **JavaScript kodiga qaytgan javobni O'QISHGA ruxsat bermaydi**!
* **Nega `curl` javobni ko'radi, brauzer esa xato beradi?**  
  `curl` — bu brauzer emas, shunchaki buyruqlar satri mijozi. Unda SOP, CORS va brauzer xavfsizlik dvigateli mavjud emas. U to'g'ridan-to'g'ri TCP soket orqali ma'lumotni o'qiydi. Brauzer esa xavfsizlik devori sifatida ishlaydi.

---

### 1.4. CORS (Cross-Origin Resource Sharing — Manbalararo Resurs Almashish)
Agar bir xizmat boshqa origin bilan ma'lumot almashishi zarur bo'lsa (masalan, frontend `8000` portda, backend API `8001` portda), server javobida maxsus sarlavha orqali ruxsat beradi:
* `Access-Control-Allow-Origin: http://127.0.0.1:8000`
* Agar bu sarlavha javobda bo'lmasa yoki undagi origin so'rov yuborgan origin bilan mos kelmasa (masalan, API faqat `8002` ga ruxsat bergan bo'lsa), brauzer JavaScript'iga javobni berishdan bosh tortadi va Console'da CORS xatosini chiqaradi.

---

### 1.5. Cookie va `HttpOnly` Bayrog'i
* **Cookie:** Server tomonidan `Set-Cookie` sarlavhasi orqali brauzerga saqlash uchun yuboriladigan kalit-qiymat ma'lumoti. Keyingi har bir mos so'rovda brauzer avtomatik ravishda `Cookie` sarlavhasini qo'shib yuboradi.
* **`HttpOnly` atributi:** Cookieni faqat HTTP so'rovlariga xos qiladi. Bu atribut qo'yilganda, brauzer ichidagi JavaScript kodi (`document.cookie`) orqali ushbu cookieni o'qib bo'lmaydi.
  * **Himoya vazifasi:** Agar veb-sahifada XSS (Cross-Site Scripting) zaifligi bo'lsa ham, tajovuzkor `document.cookie` orqali foydalanuvchining sessiya kalitini o'g'irlay olmaydi.
  * **DevTools vs `document.cookie`:** DevTools (Storage bo'limi) brauzerning o'z ma'muriy boshqaruv paneli bo'lgani uchun HttpOnly cookielarni ko'rsatadi, ammo veb sahifa ichidagi JavaScript uchun u ko'rinmas bo'ladi.
* **Muhim farq:** Cookie port bo'yicha ajratilmaydi! Cookie domen (host) bo'yicha ajratiladi.

---

### 1.6. CSP (Content Security Policy — Tarkib Xavfsizligi Siyosati)
* **Maqsadi:** Sahifaga qayerdan skriptlar, stillar yoki ulanishlar yuklanishi mumkinligini qat'iy nazorat qilish orqali XSS va ma'lumot sizib chiqishini to'xtatish.
* Laboratoriyadagi CSP qoidasi:
  ```http
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self' http://127.0.0.1:8001; object-src 'none'; base-uri 'none'; frame-ancestors 'none'
  ```
  * `script-src 'self'`: Skriptlar faqat sahifaning o'z originidan yuklangan tashqi fayllar (`/app.js`) orqali bajarilishi mumkin. HTML teglari orasiga to'g'ridan-to'g'ri yozilgan `<script>...</script>` (inline skriptlar) qat'iyan bloklanadi!
  * `connect-src 'self' http://127.0.0.1:8001`: `fetch()` orqali faqat o'ziga va `8001` portdagi API ga ulanishga ruxsat etiladi.

---

### 1.7. HTTP va HTTPS Farqi
* **HTTP:** Ma'lumotlarni ochiq matn (plaintext) shaklida uzatadi. Tarmoq oralig'idagi har qanday vositachi (provayder, xaker, sniffer) trafikni ko'rishi va o'zgartirishi mumkin.
* **HTTPS:** HTTP ustiga TLS (Transport Layer Security) shifrlash qatlamini qo'shadi. U 3 ta asosiy himoyani beradi:
  1. *Maxfiylik (Confidentiality)* — trafik shifrlanadi.
  2. *Yaxlitlik (Integrity)* — ma'lumot yo'lda buzilmagani kafolatlanadi.
  3. *Autentifikatsiya (Authentication)* — raqamli sertifikat orqali siz aynan kerakli serverga ulanganingiz tekshiriladi.
* **Eslatma:** `127.0.0.1` loopback manzilida ishlash protokolni HTTPS qilib qo'ymaydi, u hamon oddiy HTTP bo'lib qoladi.

---

## *2* Vazifani Bajarishning To'liq Qadamba-Qadam Ketma-ketligi

Quyidagi amallarni ketma-ketlik bilan bajaring.

### 2.1-Qadam: Ishchi Katalogni Yaratish va Kodni Tayyorlash

Ubuntu terminalida:
```bash
# Laboratoriya papkasini yaratish va unga o'tish
mkdir -p ~/websec/A1
cd ~/websec/A1

# a1_lab.py faylini yaratish
nano a1_lab.py
```
*(Fayl ichiga quyidagi to'liq kodni joylashtiring va Ctrl+O, Enter, Ctrl+X bilan saqlang)*

```python
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
```

Kodni sintaktik xatolarga tekshirish:
```bash
python3 -m py_compile a1_lab.py
```
*(Hech qanday xato chiqmasligi lozim).*

---

### 2.2-Qadam: Ikki Xizmatni Ishga Tushirish

Ikkita alohida terminal oching:
* **Terminal 1 (T1 — Veb Server):**
  ```bash
  cd ~/websec/A1
  python3 a1_lab.py --port 8000
  ```
* **Terminal 2 (T2 — API Server):**
  ```bash
  cd ~/websec/A1
  python3 a1_lab.py --port 8001
  ```

Uchinchi terminalda (T3) ikkala port tinglayotganini tekshiring:
```bash
ss -ltnp | grep -E ':8000|:8001'
```
*(Chiqishda `127.0.0.1:8000` va `127.0.0.1:8001` LISTEN holatida bo'lishi kerak).*

---

### 2.3-Qadam: HTTP Almashinuvini DevTools Orqali Tekshirish

1. Brauzerda (Firefox) `http://127.0.0.1:8000/` manzilini oching.
2. Sahifada quyidagi yozuvlarni ko'rasiz:
   * `Inline: ishladi`
   * `Tashqi JS: ishladi`
3. `F12` tugmasini bosing va **Network (Tarmoq)** paneliga o'ting. "Disable Cache" (Keshni o'chirish) belgilab, `Ctrl+R` bosing.
4. Yuklangan resurslar:
   * `/` (HTML hujjat) — Status: 200, Content-Type: `text/html; charset=utf-8`
   * `/style.css` — Status: 200, Content-Type: `text/css; charset=utf-8`
   * `/app.js` — Status: 200, Content-Type: `text/javascript; charset=utf-8`
5. **"Bir xil origin"** tugmasini bosing.
   * `result` blokida JSON chiqadi:
     ```json
     {
       "course": "Veb dasturlar xavfsizligi",
       "port": 8000,
       "origin_received": "(yoq)",
       "cookie_received": false
     }
     ```
6. cURL orqali ham tekshirib ko'ring:
   ```bash
   curl --noproxy "*" -i http://127.0.0.1:8000/api/info
   ```

---

### 2.4-Qadam: DOM Manipulyatsiyasini Ko'rish

1. DevTools'da **Inspector (Tadqiqotchi)** bo'limiga o'ting.
2. `<h1 id="title">A1: veb arxitektura</h1>` elementini toping.
3. Sichqoncha bilan ikki marta bosib, matnni o'z **F.I.Sh.**ingizga o'zgartiring (masalan: `h1: Nematov Azizbek`).
4. O'ng tarafdagi CSS styles bo'limida `color: red;` qo'shing.
5. **Kuzatuv:** Ekrandagi DOM modeli darhol o'zgaradi.
6. Brauzerni `Ctrl+R` bilan yangilang.
7. **Natija:** Sarlavha yana avvalgi "A1: veb arxitektura" holatiga qaytadi.
   * *Xulosa:* DOM brauzerning tezkor xotirasidagi nusxasi xolos. U yerda qilingan o'zgarishlar serverdagi faylni o'zgartirmaydi. Sahifa qayta yuklanganda serverdan asl HTML yana tortib olinadi.

---

### 2.5-Qadam: SOP va CORS Cheklovini Tekshirish (CORSsiz holat)

1. Sahifadagi **"Boshqa origin"** tugmasini bosing.
2. Sahifada quyidagi xato paydo bo'ladi:
   `Xato: NetworkError when attempting to fetch resource.`
3. **Console** bo'limini oching. Qizil rangli xato xabari:
   `Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at http://127.0.0.1:8001/api/info. (Reason: CORS header 'Access-Control-Allow-Origin' missing).`
4. Endi **T2 terminaliga** qarang:
   Terminalda `127.0.0.1 - - "GET /api/info HTTP/1.1" 200 -` yozuvi paydo bo'lgan!
   *Ya'ni so'rov serverga BORGAN va server 200 qaytargan!*
5. Terminalda cURL orqali so'rov yuboring:
   ```bash
   curl --noproxy "*" -i http://127.0.0.1:8001/api/info
   ```
   *cURL hech qanday xatosiz JSONni qaytaradi!*
   * *Katta xulosa:* SOP va CORS serverni emas, brauzerdagi JavaScriptni cheklaydi!

---

### 2.6-Qadam: CORS Ruxsatini Berish va Nosozlikni Boshqarish

#### 1. To'g'ri CORS sozlamasi:
T2 terminalida `Ctrl+C` bosing va serverni quyidagicha qayta ishga tushiring:
```bash
python3 a1_lab.py --port 8001 --cors-origin http://127.0.0.1:8000
```
Brauzerga qaytib, **"Boshqa origin"** tugmasini bosing.
* **Natija:** Endi xato yo'q! JSON ma'lumotlari chiqadi, unda `"port": 8001` aks etadi.
* Network panelida `/api/info` so'rovining Response Headers qismida:
  `Access-Control-Allow-Origin: http://127.0.0.1:8000` mavjudligini ko'rasiz.

#### 2. Noto'g'ri CORS sozlamasi (Nosozlik yaratish):
T2 terminalida yana `Ctrl+C` bosing va ataylab portni `8002` qilib ishga tushiring:
```bash
python3 a1_lab.py --port 8001 --cors-origin http://127.0.0.1:8002
```
Brauzerda **"Boshqa origin"** tugmasini bosing:
* Qayta CORS xatosi chiqadi! Chunki so'rov kelgan origin `http://127.0.0.1:8000`, server ruxsat bergan origin esa `http://127.0.0.1:8002`. Ular mos emas.

#### 3. Xatoni tuzatish:
T2 ni to'xtatib, yana `--cors-origin http://127.0.0.1:8000` bilan ishga tushiring. Tugma yana muvaffaqiyatli ishlaydi.

---

### 2.7-Qadam: Cookie va `HttpOnly` ni Tekshirish

1. Sahifadagi **"Cookie o'rnatish"** tugmasini bosing.
2. DevTools **Network** panelida `/cookie` so'roviga qarang:
   Response Headers:
   `Set-Cookie: lab_session=A1-DEMO; Path=/; HttpOnly; SameSite=Lax`
3. DevTools'da **Storage (Xotira)** -> **Cookies** -> `http://127.0.0.1:8000` bandini oching:
   * Cookie nomi: `lab_session`
   * Qiymati: `A1-DEMO`
   * HttpOnly: `true` (belgilangan)
   * SameSite: `Lax`
4. DevTools **Console** panelini oching va quyidagi buyruqni qo'lda yozing:
   ```javascript
   document.cookie
   ```
   * **Natija:** `""` (bo'sh satr qaytadi!). Cookie brauzerda bor bo'lsa-da, JavaScript undan bexabar!
5. Endi yana sahifadagi **"Bir xil origin"** tugmasini bosing:
   * `result` maydonida:
     `"cookie_received": true`
   * Network panelida `/api/info` Request Headers qismida:
     `Cookie: lab_session=A1-DEMO`
   * *Xulosa:* `HttpOnly` cookieni faqat JavaScriptdan himoya qiladi (XSS ga qarshi), ammo brauzer HTTP so'rovlariga uni avtomatik qo'shishda davom etadi.

---

### 2.8-Qadam: CSP (Content Security Policy) ni Yoqish

1. T1 terminalida `Ctrl+C` bosing va serverni `--csp` bayrog'i bilan ishga tushiring:
   ```bash
   python3 a1_lab.py --port 8000 --csp
   ```
2. Brauzer sahifasini `Ctrl+R` bilan yangilang.
3. **Kuzatuv:**
   * Ekranda: `Inline: bajarilmadi`
   * Ekranda: `Tashqi JS: ishladi`
4. DevTools **Console** bo'limida qizil xabar:
   `Content-Securit![[Screenshot from 2026-10-23 17-34-28.png]]y-Policy: The page’s settings blocked the loading of a resource (script-src) at inline (“default-src”).`
5. **Nega bunday bo'ldi?**
   Chunki server yuborgan sarlavhada `script-src 'self'` ko'rsatilgan. Bu degani: "Skriptlarni faqat alohida fayl ko'rinishida (`/app.js`) shu serverdan yuklash mumkin, HTML kodi ichidagi inline skriptlarni ishga tushirish taqiqlanadi!".
6. Sahifadagi **"Boshqa origin"** tugmasini bosing:
   * Tugma ishlaydi va JSON qaytadi! Chunki CSP qoidasida `connect-src 'self' http://127.0.0.1:8001;` orqali 8001 portga ulanishga aniq ruxsat berilgan.

---

### 2.9-Qadam: Laboratoriyadagi Hisobot Jadvallari Yechimi

#### 3.1. HTTP Resurslari Jadvali
| Resurs | Metod / Status | Content-Type | Brauzerdagi vazifasi |
| :--- | :--- | :--- | :--- |
| `/` | `GET` / `200` | `text/html; charset=utf-8` | Asosiy sahifa skeleti, tuzilishi va boshlang'ich DOM elementlarini yetkazish. |
| `/style.css` | `GET` / `200` | `text/css; charset=utf-8` | Elementlarga vizual dizayn, shrift, margin va o'lchamlarni berish. |
| `/app.js` | `GET` / `200` | `text/javascript; charset=utf-8` | Tugmalar bosilishini eshitish, API ga `fetch()` so'rovlari yuborish va DOMni yangilash. |
| `/api/info (8000)` | `GET` / `200` | `application/json; charset=utf-8` | Bir xil origindan server holati va cookie mavjudligini JSON shaklida olish. |

---

#### 3.3. Tajriba Natijalari (S1 — S10)
| Sinov | Kutiladigan holat | Haqiqiy natija va dalil |
| :--- | :--- | :--- |
| **S1: 8000 -> 8000 API** | JSON o'qiladi; port 8000 | Muvaffaqiyatli o'qildi, UI da JSON chiqdi (`"port": 8000`). |
| **S2: 8000 -> 8001, CORS yo'q** | GET serverga yetadi; JS o'qiy olmaydi | UI da `Xato: NetworkError...`, Console'da CORS xatosi, T2 terminalida esa 200 jurnali qayd etildi. |
| **S3: curl -> 8001, CORS yo'q** | 200 va JSON olinadi | curl orqali to'liq HTTP 200 va JSON javobi terminalga chiqdi (curl SOP ga bo'ysunmaydi). |
| **S4: CORS origin 8000** | JSON o'qiladi; port 8001 | Muvaffaqiyatli o'qildi. Response Headers'da `Access-Control-Allow-Origin: http://127.0.0.1:8000` tasdiqlandi. |
| **S5: CORS origin 8002** | Javobni JS o'qiy olmaydi | Origin mos kelmagani sababli Console'da yana CORS bloklash xatosi chiqdi. |
| **S6: CORS yana 8000** | JSON qayta o'qiladi | Xato tuzatildi, ma'lumotlar yana UI da muvaffaqiyatli chiqdi. |
| **S7: HttpOnly cookie** | Storage: bor; document.cookie: yo'q | Storage oynasida `lab_session` ko'rindi; Console'da `document.cookie` chaqirilganda bo'sh satr qaytdi. |
| **S8: Cookie bilan /api/info** | Cookie sarlavhasi; cookie_received: true | So'rov sarlavhasida `Cookie: lab_session=A1-DEMO` ketdi, javobda `"cookie_received": true` bo'ldi. |
| **S9: CSP yo'q** | Inline va tashqi JS ishlaydi | Ekranda ikkalasi ham: `Inline: ishladi` va `Tashqi JS: ishladi` deb chiqdi. |
| **S10: CSP bor** | Inline bloklanadi; tashqi JS va API ishlaydi | Ekranda `Inline: bajarilmadi` bo'lib qoldi, Console'da CSP inline bloklash xabari chiqdi, lekin `/app.js` va API ishladi. |

---

## *3* Qo'shimcha Kutubxonalar, Ularning Vazifasi va O'rnatish CLI Buyruqlari

Ushbu laboratoriyaning eng e'tiborli jihati uning arxitekturasida:

### 3.1. Python Kutubxonalari Tahlili:
Laboratoriyaning Python kodi (`a1_lab.py`) uchun **HECH QANDAY TASHQI KUTUBXONA (third-party package) TALAB QILINMAYDI**! `pip install` buyrug'ini bajarish shart emas.

Kod to'liq Pythonning o'z ichki (standart) kutubxonalari yordamida tuzilgan:
1. **`http.server` (`BaseHTTPRequestHandler`, `ThreadingHTTPServer`):**
   * *Maqsadi:* Qo'shimcha Apache, Nginx yoki Flask o'rnatmasdan, sof Python vositasida ko'p oqimli (multithreaded) HTTP veb-server va API yaratish.
   * *Vazifasi:* HTTP GET so'rovlarini qabul qilish, sarlavhalarni (`Content-Type`, `Set-Cookie`, `CORS`, `CSP`) dinamik shakllantirish va javob qaytarish.
2. **`argparse`:**
   * *Maqsadi:* Buyruqlar satridan berilgan argumentlarni parse qilish.
   * *Vazifasi:* `--port`, `--cors-origin` va `--csp` parametrlarini qabul qilib, server xatti-harakatini boshqarish.
3. **`json`:**
   * *Maqsadi:* JavaScript Object Notation ma'lumotlarini qayta ishlash.
   * *Vazifasi:* Lug'at (dictionary) ma'lumotlarini JSON satriga aylantirib mijozga uzatish (`json.dumps()`).
4. **`urllib.parse` (`urlsplit`):**
   * *Maqsadi:* URL manzilni qismlarga ajratish.
   * *Vazifasi:* Kelgan so'rov yo'lini (`path`) ajratib olib, `/`, `/style.css`, `/app.js`, `/api/info` kabi yo'nalishlarni aniqlash.

---

### 3.2. Operatsion Tizim Dasturlari (OS-level Tools) va Ularning CLI Buyruqlari:

| Dastur / Vosita | Maqsadi va Laboratoriyadagi Vazifasi | O'rnatish CLI Buyrug'i |
| :--- | :--- | :--- |
| **`python3`** | `a1_lab.py` server skriptini ishga tushirish uchun dasturlash muhiti va runtime. | `sudo apt install -y python3` |
| **`curl`** | HTTP so'rovlarini brauzersiz yuborish. SOP va CORS faqat brauzerda ishlashini, `curl` esa javobni erkin olishini isbotlash uchun ishlatiladi. | `sudo apt install -y curl` |
| **`nano`** | Buyruqlar satrida `a1_lab.py` kodini va konfiguratsiya fayllarini yaratish/tahrirlash uchun qulay matn muharriri. | `sudo apt install -y nano` |
| **`iproute2` (`ss` buyrug'i)** | Tizimda 8000 va 8001 portlari haqiqatan `127.0.0.1` manzilida ochilganini tekshirish (`ss -ltnp`). | `sudo apt install -y iproute2` |
| **`firefox`** | Grafik mijoz. DevTools (F12) orqali Network, Console, Storage, Inspector oynalarida brauzer xavfsizlik siyosatlarini ko'rish uchun. | `sudo snap install firefox`<br>yoki `sudo apt install -y firefox` |
| **`openssh-server` & `openssh-client`** | Ubuntu Live Server VM ichidagi portlarni Host brauzeriga xavfsiz yo'naltirish (port forwarding) uchun. | `sudo apt install -y openssh-server openssh-client` |

---

## 7. Himoya Savollari va Aniq Qisqa Javoblar (Imtihon/Himoya uchun)

1. **8000 va 8001 portlar bitta IPda (`127.0.0.1`) bo'lsa ham nega boshqa origin hisoblanadi?**  
   *Javob:* Chunki origin qoidasiga ko'ra origin = sxema + host + port. Port originning ajralmas qismidir. Portlar har xil bo'lishi brauzer uchun ularni ikki xil mustaqil xizmat deb hisoblashiga sabab bo'ladi.
2. **Nega `curl` JSONni ko'radi, brauzerdagi `fetch` esa CORS xatosini oladi?**  
   *Javob:* Chunki CORS va SOP serverning emas, **brauzerning** xavfsizlik siyosatidir. Server so'rovni qabul qilib 200 javob qaytaradi. Brauzer javobdagi CORS ruxsatini tekshirib, JavaScriptga o'qishni taqiqlaydi. `curl` esa brauzer emas va bu siyosatlarga bo'ysunmaydi.
3. **`HttpOnly` cookie nega DevTools'da bor, `document.cookie` ichida esa yo'q?**  
   *Javob:* Chunki `HttpOnly` atributining maqsadi cookieni XSS hujumlarida JavaScript orqali o'g'irlanishidan himoya qilishdir. DevTools esa brauzerning ichki ma'muriy vositasi bo'lib, sahifadagi JavaScript kontekstida ishlamaydi.
4. **`script-src 'self'` mavjud bo'lganda nega `/app.js` ishlaydi, inline kod ishlamaydi?**  
   *Javob:* Chunki `script-src 'self'` faqat shu manbadan yuklangan tashqi `.js` fayllarga ruxsat beradi. HTML teglari orasiga to'g'ridan-to'g'ri yozilgan inline skriptlar esa XSS hujumlarining asosiy manbai bo'lgani sababli CSP tomonidan bloklanadi.
5. **HTTPS protokoli CORS, avtorizatsiya yoki XSSdan himoyaning o'rnini bosa oladimi? Nega?**  
   *Javob:* Yo'q, bosa olmaydi. HTTPS faqat tarmoq uzatish paytidagi ma'lumotlar maxfiyligi va yaxlitligini (TLS) ta'minlaydi. CORS esa ilova darajasidagi resurs almashish, XSS esa brauzer ichidagi kod xavfsizligi masalasidir.
