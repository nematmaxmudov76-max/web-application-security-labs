# A6. XSS, CSRF va Brauzer Xavfsizlik Siyosatlari
## 1-Variant: Izohlar va Profil Sahifasida XSS hamda CSRFni Aniqlash va Tuzatish

---

> **Muhit bo‘yicha muhim eslatma:**
> 1. **Tarmoq (Wi-Fi):** Ushbu qo‘llanma **shaxsiy / lokal Wi-Fi** (to‘g‘ridan-to‘g‘ri internetga chiqish) uchun moslashtirilgan. Universitetning SMB fayl serveri (`\\172.18.233.234\files`), universitet proksi serveri (`172.18.1.1:2500`), APT proksi fayllari (`/etc/apt/apt.conf.d/99proxy`) va snapd proksi sozlamalari talab etilmaydi! Barcha paketlar to‘g‘ridan-to‘g‘ri internetdan o‘rnatiladi.
> 2. **Operatsion tizim va virtualizatsiya:** Barcha amallar **Host OS sifatida Ubuntu** va uning ichida ishlaydigan **VMware (Workstation / Player)** orqali boshqariladigan **Ubuntu (Desktop yoki Server)** virtual mashinalarida bajariladi. Windowsga oid komandalar (masalan, `Win+R`, `D:\...`, `VMware.exe`) butunlay chiqarib tashlangan va faqat toza Linux/Bash CLI buyruqlari keltirilgan.
> 3. **Buyruqlar tushuntirilishi:** Har bir CLI buyruq qanday vazifani bajarishi, har bir kalit (flag/parameter) nimani anglatishi alohida tushuntirib o‘tilgan.

---

## MUNDARIJA

1. [1-BO‘LIM: MAVZUNING MAQSADI VA KUTILADIGAN NATIJALAR](#1-bolim-mavzuning-maqsadi-va-kutiladigan-natijalar)
2. [2-BO‘LIM: NAZARIY VA AMALIY TUSHUNCHALAR BO‘YICHA TO‘LIQ QO‘LLANMA](#2-bolim-nazariy-va-amaliy-tushunchalar-boyicha-toliq-qollanma)
   - 2.1. XSS (Cross-Site Scripting) turlari va mexanizmi (Reflected, Stored, DOM-based)
   - 2.2. XSS dan himoyalanish: Chiqishni xavfsiz kodlash va kontekstlar
   - 2.3. CSRF (Cross-Site Request Forgery) hujumi mexanizmi
   - 2.4. Origin vs Site tushunchasi (Same-Site va Cross-Origin farqi)
   - 2.5. Cookie atributlari: SameSite va HttpOnly
   - 2.6. CORS (Cross-Origin Resource Sharing) va uning chegaralari
   - 2.7. CSP (Content Security Policy) va ramkalar (iframe) himoyasi
3. [3-BO‘LIM: FOYDALANILADIGAN BARCHA CLI BUYRUQLAR VA ULARNING TAVSIFI](#3-bolim-foydalaniladigan-barcha-cli-buyruqlar-va-ularning-tavsifi)
4. [4-BO‘LIM: MASHQNI BAJARISH KETMA-KETLIGI (BOSQICHMA-BOSQICH)](#4-bolim-mashqni-bajarish-ketma-ketligi-bosqichma-bosqich)
   - Bosqich 0: Virtual mashina va tizim paketlarini tayyorlash
   - Bosqich 1: Loyiha papkasi va Python virtual muhiti (venv)
   - Bosqich 2: Lokal domenlarni `/etc/hosts` ga kiritish
   - Bosqich 3: Boshlang‘ich dastur kodlarini yaratish
   - Bosqich 4: Ilovalarni ishga tushirish (8006 va 8007 portlar)
   - Bosqich 5: Zaifliklarni tekshirish va dastlabki dalillarni olish (D1–D5)
   - Bosqich 6: To‘rtta kod tuzatishini kiritish va regressiya sinovi (D6)
   - Bosqich 7: CSP va CORS siyosatlarini alohida tekshirish (D7)
5. [5-BO‘LIM: HISOBOT JADVALI VA MUAMMOLARNI BARTARAF ETISH (TROUBLESHOOTING)](#5-bolim-hisobot-jadvali-va-muammolarni-bartaraf-etish-troubleshooting)
   - 5.1. D1–D7 dalillarining solishtirma jadvali
   - 5.2. Ko‘p uchraydigan muammolar va yechimlar
   - 5.3. Nazorat savollariga tushuntirishli javoblar
6. [6-BO‘LIM: FOYDALANILGAN VA TAVSIYA ETILADIGAN MANBALAR](#6-bolim-foydalanilgan-va-tavsiya-etiladigan-manbalar)

---

## 1-BO‘LIM: MAVZUNING MAQSADI VA KUTILADIGAN NATIJALAR

### 1.1. Mashg‘ulot maqsadi
Ushbu laboratoriya ishining asosiy maqsadi veb-dasturlarda eng ko‘p uchraydigan mijoz tomonidagi (client-side) va so‘rovlar yaxlitligiga oid zaifliklarni o‘rganishdan iborat:
1. **XSS (Cross-Site Scripting)** ning uchta asosiy turini (**Reflected**, **Stored** va **DOM-based**) amalda ajrata bilish va ularning manbalari (sources) hamda xavfli tushish joylari (sinks) mexanizmini tahlil qilish.
2. Brauzer orqali bajariladigan begona zararli JavaScript kod (XSS) bilan foydalanuvchining vakolatidan foydalanib uning nomidan soxta so‘rov yuborish (**CSRF**) o‘rtasidagi prinsipial farqni tushunish.
3. Zaifliklarni bartaraf etish uchun **HTML chiqishini kodlash (context-aware output encoding)**, xavfsiz DOM xususiyatlari (`textContent`), **CSRF tokenlarini tekshirish** va **CSP (Content Security Policy)** sarlavhalaridan to‘g‘ri foydalanishni amalda o‘zlashtirish.
4. Zamonaviy brauzer himoya mexanizmlari: **SameSite**, **HttpOnly**, **Origin vs Site**, **CORS** va **CSP** direktivalarining qachon ishlashi va qachon yordam bera olmasligini dalillar bilan asoslash.

### 1.2. Kutiladigan natijalar
Mashg‘ulot yakunida quyidagi amaliy natijalarga erishiladi:
* Talaba XSSning uchala turini zararsiz marker (sahifa sarlavhasini `document.title` orqali `A6-R`, `A6-S`, `A6-D` ga o‘zgartirish) yordamida namoyish etadi.
* Boshqa origindan (`evil.a6.test:8007`) yuborilgan tokensiz tashqi POST so‘rovi nishon ilovadagi (`app.a6.test:8006`) foydalanuvchi profilini (email manzilini) o‘zgartira olishini (CSRF) kuzatadi.
* Dastur kodlariga to‘rtta aniq tuzatish kiritadi (ikkita Jinja shablonida `|safe` ni olib tashlash, bitta DOM skriptida `textContent` ga o‘tish va bitta Flask backendida `check_csrf()` tekshiruvini faollashtirish).
* Tuzatishlardan so‘ng regressiya testini o‘tkazadi: qonuniy amallar (izoh qoldirish, profilni yangilash) to‘g‘ri ishlashini, noqonuniy kiritmalar esa oddiy matn sifatida zararsizlantirilishini va tokensiz so‘rovlar HTTP 403 Forbidden bilan to‘xtatilishini isbotlaydi.
* CSP yoqilganda inline skriptlarning to‘xtatilishi, `frame-ancestors 'none'` orqali clickjackingdan himoyalanish (iframe bloklanishi) va CORS orqali begona sahifa API javobini o‘qiy olmasligini Firefox Developer Tools orqali tekshiradi va D1–D7 dalillarini to‘playdi.

### 1.3. Asosiy parametrlar va muhit ko‘rsatkichlari

| Ko‘rsatkich | Qiymat / Tavsif |
| :--- | :--- |
| **Mavzu / Variant** | A6 / 1-variant (Izohlar va profil sahifasida XSS hamda CSRF) |
| **Asosiy operatsion tizim (Host)** | Ubuntu Desktop (Linux muhiti) |
| **Virtualizator** | VMware Workstation Pro / Player for Linux |
| **Virtual mashina (Guest VM)** | Ubuntu 24.04 LTS Desktop (yoki Ubuntu Server) |
| **Tarmoq holati** | Shaxsiy Wi-Fi tarmog‘i, VMware NAT rejimi (hech qanday proksisiz) |
| **Asosiy ilova (Target App)** | `http://app.a6.test:8006/` — Flask da yozilgan sun’iy Ali profili |
| **Tashqi tajriba sahifasi (Attacker)** | `http://evil.a6.test:8007/` — Python lokal statik HTTP server |
| **Asosiy vositalar** | Python 3, Flask 3.1.3, Firefox Developer Tools, curl, nano / bash |
| **Hisobot dalillari** | D1 dan D7 gacha bo‘lgan amaliy skrinshotlar va jurnal ma’lumotlari |

---

## 2-BO‘LIM: NAZARIY VA AMALIY TUSHUNCHALAR BO‘YICHA TO‘LIQ QO‘LLANMA

### 2.1. XSS (Cross-Site Scripting) turlari va mexanizmi

XSS zaifligi tajovuzkorga qonuniy foydalanuvchilarning brauzerida begona JavaScript kodlarini bajarish imkonini beradi. Brauzer sahifadagi skript nishon sayt dasturchisi tomonidan yozilganmi yoki tajovuzkor kiritganmi — ajrata olmaydi (Same-Origin Policy bu holatda sahifa ichidagi kodni o‘z originiga tegishli deb hisoblaydi).

Ushbu laboratoriyada XSS ning 3 ta ko‘rinishi o‘rganiladi:

```
+-----------------------------------------------------------------------------------+
|                                  XSS TURLARI                                      |
+-----------------------------------------------------------------------------------+
| 1. REFLECTED XSS:                                                                 |
|    URL so'rovi (?q=...) ----> Server (shablonga qo'shadi) ----> HTML javob (brauzer)  |
|    (Kiritilgan zahoti sahifada aks etadi, server bazasida saqlanmaydi)            |
+-----------------------------------------------------------------------------------+
| 2. STORED XSS:                                                                    |
|    Izoh yuborish (POST) ----> Server xotirasiga/bazasiga yoziladi                 |
|    Keyingi har qanday GET /notes ----> Barcha foydalanuvchilarga skript chiqadi   |
+-----------------------------------------------------------------------------------+
| 3. DOM-BASED XSS:                                                                 |
|    URL fragment (#payload) ----> Serverga UMUMAN bormaydi                         |
|    Mijoz brauzeridagi JS (location.hash) ----> innerHTML ga joylaydi (brauzer)    |
+-----------------------------------------------------------------------------------+
```

#### A. Reflected XSS (Qaytarilgan kiritma)
* **Manba (Source):** URL dagi qidiruv parametri: `GET /reflect?q=<payload>`.
* **Xavfli joy (Sink):** Server tomonidagi Jinja2 shablonidagi `{{ q|safe }}` filtri.
* **Xavf mohiyati:** Foydalanuvchi maxsus tayyorlangan havola (link) ustiga bosganda, so‘rov serverga boradi va server kiritmani filtrlamasdan to‘g‘ridan-to‘g‘ri HTML sahifa ichiga joylab javob qaytaradi. Brauzer sahifani yuklagan zahoti skript ishga tushadi.

#### B. Stored XSS (Doimiy / Saqlangan kiritma)
* **Manba (Source):** Foydalanuvchi kiritgan izoh formasi: `POST /notes` (note parametri).
* **Xavfli joy (Sink):** Xotiradagi `NOTES` ro‘yxatidan olingan ma’lumot shablonda `{{ note|safe }}` orqali chiqarilishi.
* **Xavf mohiyati:** Bu XSS ning eng xavfli turidir. Zararli kod server xotirasiga (yoki ma’lumotlar bazasiga) saqlanib qoladi. Keyinchalik har qanday foydalanuvchi (yoki administrator) `/notes` sahifasiga kirganida, saqlangan skript ularning brauzerida avtomatik ishga tushadi.

#### C. DOM-based XSS (Hujjat Ob’ekt Modeli orqali bajariluvchi XSS)
* **Manba (Source):** URL fragmenti: `location.hash` (ya’ni URL dagi `#` belgisidan keyingi qism).
* **Xavfli joy (Sink):** JavaScript da xom HTML yozuvchi DOM xususiyati: `output.innerHTML = value;`.
* **Muhim xususiyati:** Brauzerlar HTTP protokoli standartiga ko‘ra, URL dagi `#` belgisidan keyingi qismni (fragmentni) **serverga yubormaydi**! Serverning access loglarida bu payload ko‘rinmaydi. Hujum to‘liq mijoz tomonida (brauzer xotirasida) JavaScript kodi tomonidan amalga oshiriladi.

---

### 2.2. XSS dan himoyalanish: Chiqishni xavfsiz kodlash va kontekstlar

1. **Jinja2 Autoescaping:**
   Flask va Jinja shablon dvigatellari odatda barcha o‘zgaruvchilarni avtomatik tarzda HTML belgilariga kodlaydi (masalan, `<` belgisi `&lt;` ga, `>` belgisi `&gt;` ga aylantiriladi). 
   Biroq, `{{ q|safe }}` yoki `{{ note|safe }}` yozilganda, dasturchi shablon dvigateliga: *"Bu ma’lumot xavfsiz, uni kodlamasdan to‘g‘ridan-to‘g‘ri HTML sifatida brauzerga ber"* deb ko‘rsatma beradi. Himoyalanish uchun `|safe` filtri olib tashlanadi va shunchaki `{{ q }}` hamda `{{ note }}` qoldiriladi.

2. **DOM da `innerHTML` o‘rniga `textContent` dan foydalanish:**
   * `element.innerHTML = value;` — qiymatni HTML teglari sifatida tahlil qiladi (parse qiladi). Agar qiymatda `<img src=x onerror=...>` bo‘lsa, rasm tugunini yaratib, xatolik hodisasini (skriptni) darhol ishga tushiradi.
   * `element.textContent = value;` — qiymatni qat’iy ravishda oddiy matn (text node) sifatida joylashtiradi. Hech qanday HTML teglari tahlil qilinmaydi va skriptlar bajarilmaydi.

---

### 2.3. CSRF (Cross-Site Request Forgery) hujumi mexanizmi

**CSRF nima?**
CSRF — foydalanuvchi autentifikatsiyadan o‘tgan (tizimga kirgan) holatida, tajovuzkorning saytiga kirib qolishi oqibatida, foydalanuvchining ruxsatisiz va bexabar ravishda uning nomidan himoyalangan veb-ilovaga so‘rov yuborish hujumidir.

```
+------------------------------------------------------------------------------------+
|                                CSRF HUJUMI JARAYONI                                |
+------------------------------------------------------------------------------------+
| 1. Foydalanuvchi app.a6.test da tizimga kirgan (brauzerida a6_sid cookie bor).      |
| 2. Foydalanuvchi boshqa tabda evil.a6.test ga kiradi.                               |
| 3. evil.a6.test sahifasidagi forma app.a6.test/profile ga POST so'rov yuboradi.     |
| 4. Brauzer nishon domen (app.a6.test) cookielarini so'rovga AVTOMATIK qo'shadi!     |
| 5. Server: "Cookie to'g'ri, demak Ali so'rov yubordi" deb o'ylaydi va emailni      |
|    tajovuzkor xohlagan changed@lab.invalid ga o'zgartiradi!                         |
+------------------------------------------------------------------------------------+
```

#### Nega bu yuz beradi?
Brauzerlar HTTP so‘rov yuborilayotganda, agar nishon manzil uchun saqlangan cookie mavjud bo‘lsa, uni avtomatik tarzda `Cookie:` sarlavhasiga biriktirib jo‘natadi. Server faqat `a6_sid` cookie mavjudligiga qarab qaror qabul qilsa, so‘rov qaysi sahifadagi forma orqali yuborilganini bila olmaydi.

#### Himoya: Anti-CSRF Token
Har bir foydalanuvchi sessiyasiga bog‘langan kriptografik tasodifiy token (`csrf_token`) yaratiladi. Ushbu token qonuniy HTML formaga yashirin maydon (`<input type="hidden" name="csrf" value="...">`) sifatida kiritiladi.
Server POST so‘rovni qabul qilganda:
* Formadan kelgan `csrf` parametri bilan foydalanuvchi sessiyasidagi `session['csrf']` ni solishtiradi (`secrets.compare_digest`).
* Begona sayt (`evil.a6.test`) foydalanuvchining maxfiy tokenini bila olmaydi (chunki Same-Origin Policy begona sayt skriptlariga boshqa sayt DOMini o‘qishga ruxsat bermaydi).
* Natijada, begona saytdan yuborilgan so‘rovda token bo‘lmaydi (yoki noto‘g‘ri bo‘ladi) va server so‘rovni darhol **HTTP 403 Forbidden** bilan rad etadi.

---

### 2.4. Origin vs Site tushunchasi (Same-Site va Cross-Origin)

Ko‘pchilik dasturchilar **Origin** va **Site** tushunchalarini chalkashtiradilar. Ularning farqi juda muhim:

1. **Origin (Manba):**
   Origin uchta qismdan iborat: **Sxema (protokol) + To‘liq Xost (Host) + Port**.
   Agar ulardan birortasi farq qilsa — bu **Cross-Origin** hisoblanadi.
   * `http://app.a6.test:8006`
   * `http://evil.a6.test:8007`
   * Bu ikkisi mutlaqo **BOSHQA ORIGINLAR** (chunki host va portlari turli xil).

2. **Site (Sayt / eTLD+1):**
   Site tushunchasi ro‘yxatga olinadigan umumiy domen (eTLD+1) va sxemaga tayanadi.
   * Ikkala domen ham bir xil `http` sxemasi va `a6.test` yuqori darajali domeniga qarashli.
   * Shuning uchun ular bir-biriga nisbatan **SAME-SITE** hisoblanadi!

Ushbu laboratoriyada nima uchun `evil.a6.test` tanlangan?
Aynan **Same-Site bo‘lgan, lekin Cross-Origin bo‘lgan** vaziyatda `SameSite=Lax` atributining xatti-harakatini kuzatish uchun!

---

### 2.5. Cookie atributlari: SameSite va HttpOnly

Ilovada cookie quyidagicha sozlangan:
```python
SESSION_COOKIE_NAME='a6_sid',
SESSION_COOKIE_HTTPONLY=True,
SESSION_COOKIE_SAMESITE='Lax',
SESSION_COOKIE_SECURE=False
```

* **`HttpOnly=True`:**
  Ushbu atribut mijoz tomonidagi JavaScript kodlariga (`document.cookie`) cookieni o‘qishni taqiqlaydi. Bu XSS orqali sessiya o‘g‘irlanishining oldini oladi.
  **Lekin diqqat:** `HttpOnly` CSRF hujumidan asray olmaydi! Chunki CSRF hujumida JavaScript cookieni o‘qimaydi, balki brauzer HTTP so‘roviga cookieni avtomatik ravishda qo‘shib yuboradi.

* **`SameSite=Lax`:**
  Ushbu atribut boshqa saytlardan keluvchi so‘rovlarda cookieni yuborishni cheklaydi (masalan, begona saytdan oddiy `POST` so‘rovlariga cookie biriktirilmaydi).
  **Lekin nega bizning laboratoriyada `SameSite=Lax` bo‘lsa ham CSRF ishladi?**
  Chunki bizning ilovamiz (`app.a6.test:8006`) va hujumchi sahifasi (`evil.a6.test:8007`) **bir xil saytga (`a6.test`) tegishli (Same-Site)**! `SameSite` siyosati faqat *Cross-Site* holatlarida ishlaydi, *Same-Site, Cross-Origin* holatida esa brauzer cookieni erkin jo‘natadi. Shu sababli CSRF himoyasi uchun faqatgina `SameSite=Lax` ga tayanib bo‘lmaydi — qat’iy anti-CSRF tokenlari zarur!

---

### 2.6. CORS (Cross-Origin Resource Sharing) va uning chegaralari

Ko‘p hollarda noto‘g‘ri tushuncha mavjud: *"Agar CORS sozlanmagan bo‘lsa, boshqa saytdan POST yuborib bo‘lmaydi"*. Bu mutlaqo xato!

* **HTML Formasi:** Oddiy HTML formalar (`<form method="POST">`) CORS tekshiruviga tushmaydi. Ular bemalol cross-origin POST so‘rovlarini serverga yubora oladi (CSRF aynan shuning ustiga qurilgan).
* **CORS ning haqiqiy vazifasi:** Boshqa origindagi JavaScript kodiga (`fetch` yoki `XMLHttpRequest`) so‘rov javobini (Response body) **O‘QISHGA** ruxsat berish yoki bermaslikni nazorat qiladi.
* Agar `app.a6.test` javobida `Access-Control-Allow-Origin: http://evil.a6.test:8007` sarlavhasi bo‘lmasa, brauzer `evil.a6.test` sahifasidagi skriptga javobni o‘qishga yo‘l qo‘ymaydi, garchi server so‘rovni qabul qilib, HTTP 200 qaytargan bo‘lsa ham.

---

### 2.7. CSP (Content Security Policy) va ramkalar (iframe) himoyasi

CSP — bu veb-server tomonidan `Content-Security-Policy` HTTP javob sarlavhasi orqali yuboriladigan qoidalar to‘plami bo‘lib, brauzerga qaysi resurslarni yuklash va bajarish mumkinligini buyuradi.

Laboratoriyada qo‘llaniladigan CSP siyosati:
```http
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'
```

* **`default-src 'self'`:** Odatiy holda barcha resurslar (rasmlar, stillar) faqat o‘z originidan yuklansin.
* **`script-src 'self'`:** Skriptlar faqat o‘z originidagi alohida `.js` fayllardan yuklansin. Inline skriptlar (`<script>...</script>`) va HTML atributlaridagi hodisa ishlovchilari (`onerror=...`, `onclick=...`) qat’iyan **bloklanadi**!
* **`frame-ancestors 'none'`:** Ushbu sahifani hech qanday boshqa sahifa `<iframe>`, `<frame>` yoki `<object>` ichiga joylashtira olmaydi. Bu foydalanuvchini **Clickjacking (UI Redressing)** hujumlaridan to‘liq himoya qiladi.
* **`form-action 'self'`:** Sahifadagi formalar faqat o‘z originiga ma’lumot yuborishi mumkin.

---

## 3-BO‘LIM: FOYDALANILADIGAN BARCHA CLI BUYRUQLAR VA ULARNING TAVSIFI

Ushbu amaliyotda ishlatiladigan har bir Linux / Bash CLI buyrug‘i, uning vazifasi va kalitlari quyida batafsil izohlangan:

### 1. Tizim va tarmoq buyruqlari
* `sudo hostnamectl set-hostname veb-a6-lab`
  * **Vazifasi:** Virtual mashinaning kompyuter nomini (hostname) `veb-a6-lab` deb o‘zgartiradi.
  * **Kalitlar:** `sudo` — ma’mur (root) huquqi bilan bajarish; `set-hostname` — yangi tarmoq nomini o‘rnatish.
* `whoami`
  * **Vazifasi:** Joriy tizimga kirgan foydalanuvchi nomini (masalan, `maxfull` yoki `ubuntu`) ekranga chiqaradi.
* `id`
  * **Vazifasi:** Joriy foydalanuvchining UID (User ID), GID (Group ID) va u a’zo bo‘lgan barcha tizim guruhlarini (ayniqsa `sudo` guruhi borligini) ko‘rsatadi.
* `sudo -v`
  * **Vazifasi:** Sudo huquqini tekshiradi va parolni keshlaydi (keyingi komandalar parol so‘ramay tez bajarilishi uchun).
* `date -Is`
  * **Vazifasi:** Joriy tizim sanasi va vaqtini ISO-8601 xalqaro standart formatida (masalan, `2026-10-27T14:30:00+05:00`) ko‘rsatadi. Bu hisobotga aniq vaqtni yozish uchun zarur.
* `getent hosts app.a6.test evil.a6.test`
  * **Vazifasi:** Tizimning nomlar bazasidan (NSS / hosts) ko‘rsatilgan domenlar qaysi IP manzilga yo‘naltirilganini tekshiradi. Ikkala domen ham `127.0.0.1` qaytarishi shart.

### 2. Paketlar va virtual muhit buyruqlari
* `sudo apt update`
  * **Vazifasi:** Ubuntu paketlar ombori (repository) ro‘yxatini internetdagi rasmiy serverlardan yangilaydi.
* `sudo apt install -y python3 python3-venv python3-pip curl nano`
  * **Vazifasi:** Mashg‘ulot uchun zarur bo‘lgan tizim paketlarini o‘rnatadi:
    * `python3` — Python tili talqinchisi.
    * `python3-venv` — Python uchun izolyatsiyalangan virtual muhit yaratish moduli.
    * `python3-pip` — Python paketlar boshqaruvchisi.
    * `curl` — buyruqlar satridan HTTP so‘rovlar yuborish utilitasi.
    * `nano` — terminal ichidagi matn muharriri.
    * `-y` kaliti — o‘rnatish jarayonidagi barcha tasdiqlash savollariga avtomatik "ha" deb javob beradi.
* `mkdir -p ~/websec/A6/{templates,static,attack,evidence}`
  * **Vazifasi:** Bitta buyruq bilan barcha zarur papkalarni iyerarxik tarzda yaratadi:
    * `-p` (parents) — agar ota papkalar bo‘lmasa, ularni ham avtomatik yaratish va mavjud bo‘lsa xatolik bermaslik.
* `python3 -m venv .venv`
  * **Vazifasi:** Loyiha papkasida `.venv` nomli izolyatsiyalangan Python virtual muhitini hosil qiladi (tizim kutubxonalariga daxl qilmaslik uchun).
* `source .venv/bin/activate`
  * **Vazifasi:** Yaratilgan virtual muhitni joriy terminal sessiyasida faollashtiradi (terminal oldida `(.venv)` belgisi chiqadi).
* `python -m pip install Flask==3.1.3`
  * **Vazifasi:** Virtual muhit ichiga aynan Flask ning 3.1.3 versiyasini o‘rnatadi.
* `python -m pip freeze > requirements-lock.txt`
  * **Vazifasi:** O‘rnatilgan barcha Python kutubxonalarining aniq versiyalarini `requirements-lock.txt` fayliga yozib, qayd qilib qo‘yadi.
* `python -m py_compile app.py`
  * **Vazifasi:** `app.py` faylida sintaktik xatoliklar (SyntaxError) yo‘qligini tekshiradi va bayt-kodga o‘giradi.

### 3. Serverlarni ishga tushirish buyruqlari
* `A6_CSP=0 python app.py`
  * **Vazifasi:** Asosiy Flask ilovasini CSP o‘chirilgan holatda (`A6_CSP=0` muhit o‘zgaruvchisi bilan) 8006-portda ishga tushiradi.
* `A6_CSP=1 python app.py`
  * **Vazifasi:** Asosiy ilovani qat’iy CSP xavfsizlik sarlavhalari yoqilgan holatda (`A6_CSP=1`) ishga tushiradi.
* `python3 -m http.server 8007 --bind 127.0.0.1 --directory attack`
  * **Vazifasi:** Python ning ichki HTTP serveri orqali `attack` papkasini 8007-portda alohida veb-sayt sifatida taqdim etadi:
    * `8007` — tinglanadigan port.
    * `--bind 127.0.0.1` — faqat lokal kompyuter uchun ochish (tashqaridan ulanishni cheklash).
    * `--directory attack` — ildiz katalog sifatida faqat `attack` papkasini ko‘rsatish.

### 4. Tarmoq va diagnostika buyruqlari
* `curl --noproxy "*" -sS -G http://app.a6.test:8006/reflect --data-urlencode "q=<b>A6</b>"`
  * **Vazifasi:** Terminaldan turib Reflected XSS endpointiga sinov so‘rovi yuboradi:
    * `--noproxy "*"` — hech qanday proksi ishlatmasdan to‘g‘ridan-to‘g‘ri murojaat qilish.
    * `-sS` (silent/show-error) — ortiqcha progress barlarni ko‘rsatmaslik, faqat xatolik bo‘lsa chiqarish.
    * `-G` — so‘rovni GET metodi orqali yuborish.
    * `--data-urlencode` — kiritilayotgan parametrlarni to‘g‘ri URL-kodlash (URL-encoding) qilib yuborish.

---

## 4-BO‘LIM: MASHQNI BAJARISH KETMA-KETLIGI (BOSQICHMA-BOSQICH)

### Bosqich 0: Virtual mashina va tizimni tayyorlash (Ubuntu + VMware)

Foydalanuvchi asosiy tizim (Host) sifatida **Ubuntu** da ishlaydi va uning ichida **VMware** o‘rnatilgan.
Laboratoriyani bajarish uchun VMware ichidagi Ubuntu Desktop virtual mashinasi ishga tushiriladi.

> [!TIP]
> Agar sizda VMware ichida grafik interfeysli **Ubuntu Desktop** bo‘lsa, Firefox va terminallar to‘g‘ridan-to‘g‘ri VM ichida ishlatiladi.
> Agar siz faqat terminaldan iborat **Ubuntu Server** VM ishlatayotgan bo‘lsangiz, Flask dasturida `host='0.0.0.0'` qilib, Host Ubuntudagi `/etc/hosts` ga VM ning IP sini kiritishingiz yoki SSH orqali portlarni yo‘naltirishingiz (`ssh -L 8006:127.0.0.1:8006 -L 8007:127.0.0.1:8007 user@vm-ip`) mumkin. Biroq standart va eng qulay usul — **Ubuntu Desktop VM** ichida bajarishdir.

Virtual mashina terminalida quyidagi buyruqlarni bajaring:

```bash
# 1. Mashina nomini o'rnatish
sudo hostnamectl set-hostname veb-a6-lab

# 2. Foydalanuvchi ma'lumotlarini tekshirish
whoami
id
sudo -v
date -Is
```

### Bosqich 1: Paketlarni o‘rnatish va loyiha papkasini sozlash

Lokal Wi-Fi tarmog‘ida bo‘lganingiz sababli hech qanday proksi sozlamalari talab qilinmaydi. To‘g‘ridan-to‘g‘ri APT orqali paketlarni yangilang va o‘rnating:

```bash
# 1. Tizim paketlarini yangilash va o'rnatish
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl nano

# 2. Loyiha papkalari strukturasini yaratish
mkdir -p ~/websec/A6/{templates,static,attack,evidence}
cd ~/websec/A6

# 3. Python virtual muhitini yaratish va faollashtirish
python3 -m venv .venv
source .venv/bin/activate

# 4. Flask 3.1.3 ni o'rnatish va qulflash
python -m pip install Flask==3.1.3
python -m pip freeze > requirements-lock.txt
```

### Bosqich 2: Lokal domenlarni `/etc/hosts` fayliga biriktirish

Ushbu laboratoriyada Same-Site va Cross-Origin farqini modellashtirish uchun ikkita lokal domen ishlatiladi:
* `app.a6.test` — nishon asosiy ilova (8006 portda)
* `evil.a6.test` — tajovuzkorning tashqi sahifasi (8007 portda)

Terminalda hosts faylini oching:
```bash
sudo nano /etc/hosts
```
Faylning oxiriga quyidagi satrni qo‘shing va saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`):
```text
127.0.0.1 app.a6.test evil.a6.test
```

Domenlarning to‘g‘ri ulanganini tekshiring:
```bash
getent hosts app.a6.test evil.a6.test
```
*Kutiladigan natija:* Ikkala domen ro‘parasida ham `127.0.0.1` ko‘rinishi kerak.

---

### Bosqich 3: Boshlang‘ich dastur kodlarini yaratish

`~/websec/A6` papkasida turganingizga ishonch hosil qiling (`pwd`). To‘rtta faylni yaratamiz:

#### 1-fayl: `app.py` (Asosiy Flask ilovasi)
Quyidagi komanda orqali faylni yarating:
```bash
cat << 'EOF' > app.py
import os
import secrets
from flask import Flask, abort, jsonify, redirect
from flask import render_template, request, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_NAME='a6_sid',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
    MAX_CONTENT_LENGTH=4096
)
EMAIL = {'ali': 'ali@lab.invalid'}
NOTES = []
CSP_ON = os.environ.get('A6_CSP') == '1'

def current_user():
    if session.get('user') != 'ali':
        abort(401)
    return session['user']

def check_csrf():
    expected = session.get('csrf', '')
    received = request.form.get('csrf', '')
    if not expected or not secrets.compare_digest(
            expected.encode(), received.encode()):
        abort(403)

def page(kind, **data):
    return render_template('page.html', kind=kind, **data)

@app.get('/')
def home():
    return page('home')

@app.post('/start')
def start():
    session.clear()
    session['user'] = 'ali'
    session['csrf'] = secrets.token_hex(32)
    return redirect('/profile')

@app.get('/reflect')
def reflect():
    q = request.args.get('q', '')[:500]
    return page('reflect', q=q)

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    current_user()
    if request.method == 'POST':
        check_csrf()
        NOTES.append(request.form.get('note', '')[:500])
        return redirect('/notes')
    return page('notes', notes=NOTES)

@app.get('/dom')
def dom():
    return page('dom')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = current_user()
    if request.method == 'POST':
        # TODO: check_csrf() ni shu yerga qo'shing.
        email = request.form.get('email', '')
        if not 1 <= len(email) <= 120 or '@' not in email:
            abort(400)
        EMAIL[user] = email
        return redirect('/profile')
    return page('profile', email=EMAIL[user])

@app.get('/api/me')
def me():
    user = current_user()
    return jsonify(user=user, email=EMAIL[user])

@app.after_request
def headers(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    if CSP_ON:
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; "
            "object-src 'none'; base-uri 'none'; "
            "frame-ancestors 'none'; form-action 'self'")
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8006, debug=False)
EOF
```

#### 2-fayl: `templates/page.html` (Shablon fayli)
```bash
cat << 'EOF' > templates/page.html
<!doctype html>
<html lang="uz">
<meta charset="utf-8">
<title>A6 laboratoriya</title>
<h1>A6 / 1-variant</h1>
<nav>
  <a href="/">Bosh sahifa</a> |
  <a href="/reflect">Reflected</a> |
  <a href="/notes">Stored</a> |
  <a href="/dom">DOM</a> |
  <a href="/profile">Profil</a>
</nav>
<hr>
{% if kind == 'home' %}
<p>Sun'iy Ali akkaunti bilan lokal tajribani boshlang.</p>
<form method="post" action="/start">
  <button>Demo sessiyani boshlash</button>
</form>
{% elif kind == 'reflect' %}
<h2>Reflected XSS</h2>
<form method="get">
  <input name="q" placeholder="Qidiruv matni">
  <button>Ko'rsatish</button>
</form>
<p id="reflected">{{ q|safe }}</p>
{% elif kind == 'notes' %}
<h2>Saqlangan izohlar</h2>
<form method="post">
  <input type="hidden" name="csrf" value="{{ session.csrf }}">
  <textarea name="note" rows="3" cols="60"></textarea>
  <button>Saqlash</button>
</form>
{% for note in notes %}
<div>{{ note|safe }}</div>
{% endfor %}
{% elif kind == 'dom' %}
<h2>URL fragmentini ko'rsatish</h2>
<div id="output"></div>
<script src="/static/dom.js"></script>
{% elif kind == 'profile' %}
<h2>Ali profili</h2>
<p>Joriy email: <strong id="email">{{ email }}</strong></p>
<form method="post">
  <input type="hidden" name="csrf" value="{{ session.csrf }}">
  <input name="email" value="{{ email }}">
  <button>Yangilash</button>
</form>
{% endif %}
</html>
EOF
```

#### 3-fayl: `static/dom.js` (DOM skripti)
```bash
cat << 'EOF' > static/dom.js
const output = document.getElementById('output');
const value = decodeURIComponent(location.hash.slice(1));
output.innerHTML = value;
EOF
```

#### 4-fayl: `attack/index.html` (Tashqi hujum sahifasi)
```bash
cat << 'EOF' > attack/index.html
<!doctype html>
<html lang="uz">
<meta charset="utf-8">
<title>A6 tashqi sahifa</title>
<h1>Boshqa origin: evil.a6.test:8007</h1>
<p>Faqat o'z lokal A6 ilovangiz uchun tajriba.</p>
<form method="post" action="http://app.a6.test:8006/profile">
  <input type="hidden" name="email" value="changed@lab.invalid">
  <button>Tokensiz tashqi POST yuborish</button>
</form>
<h2>CORS orqali javobni o'qish sinovi</h2>
<button id="read">API javobini o'qish</button>
<pre id="result"></pre>
<h2>Iframe ichidagi profil</h2>
<iframe src="http://app.a6.test:8006/profile"
        width="700" height="250"></iframe>
<script>
document.getElementById('read').onclick = async () => {
  const output = document.getElementById('result');
  try {
    const r = await fetch('http://app.a6.test:8006/api/me',
                          {credentials: 'include'});
    output.textContent = await r.text();
  } catch (error) {
    output.textContent = 'Brauzer javobni o\'qishga ruxsat bermadi';
  }
};
</script>
</html>
EOF
```

Fayllarni tekshirish va zaxira (before) nusxalarini yaratish:
```bash
python -m py_compile app.py
cp app.py app_before.py
cp templates/page.html templates/page_before.html
cp static/dom.js static/dom_before.js
```

---

### Bosqich 4: Ilovalarni ishga tushirish

Laboratoriya ishlashi uchun **ikkita alohida terminal oynasi** kerak bo‘ladi:

* **1-Terminalda (Asosiy ilova):**
  ```bash
  cd ~/websec/A6
  source .venv/bin/activate
  A6_CSP=0 python app.py
  ```
  *(Dastur 127.0.0.1:8006 da ishga tushadi. `A6_CSP=0` dastlabki tajribalarda CSP ni o‘chirib turadi).*

* **2-Terminalda (Tashqi hujum serveri):**
  ```bash
  cd ~/websec/A6
  python3 -m http.server 8007 --bind 127.0.0.1 --directory attack
  ```
  *(Dastur 127.0.0.1:8007 da `attack/index.html` ni taqdim etadi).*

Har ikkala terminal ochiq holda qoldiriladi.

---

### Bosqich 5: Zaifliklarni tekshirish va dastlabki dalillarni olish (D1–D5)

Firefox brauzerini oching.

#### 1-qadam: Demo sessiyani boshlash (Dalil D1)
1. Brauzerda manzilni oching: `http://app.a6.test:8006/`
2. **"Demo sessiyani boshlash"** tugmasini bosing.
3. Sahifa avtomatik ravishda `/profile` ga yo‘naltiriladi va ekranda `ali@lab.invalid` ko‘rinadi.
4. **F12** tugmasini bosib Developer Tools ni oching:
   * **Network (Tarmoq)** bo‘limida `POST /start` (302 Found) va keyin `GET /profile` (200 OK) bo‘lganini ko‘ring. "Persist Logs" (yoki Preserve log) katakchasini belgilab qo‘ying.
   * **Storage (Xotira) -> Cookies -> http://app.a6.test:8006** bo‘limida `a6_sid` nomli cookie borligini tekshiring. Uning atributlarida `HttpOnly: true` va `SameSite: Lax` ekanini qayd eting (D1 dalili).

---

#### 2-qadam: Reflected XSS ni tekshirish (Dalil D2)
1. Yuqori menyudan **Reflected** havolasiga o‘ting (`http://app.a6.test:8006/reflect`).
2. Qidiruv maydoniga oddiy matn emas, quyidagi zararsiz XSS markerini kiriting:
   ```html
   <img src=/missing onerror="document.title='A6-R'">
   ```
3. **"Ko‘rsatish"** tugmasini bosing.
4. **Natijani kuzating:**
   * `/missing` manzili mavjud bo‘lmagani uchun brauzer rasmni yuklay olmaydi va `onerror` xatolik hodisasini chaqiradi.
   * Sahifaning sarlavhasi (ichki oyna / tab nomi) **`A6-R`** ga o‘zgaradi!
   * F12 orqali HTML manbasini ko‘rsangiz: `<p id="reflected"><img src=/missing onerror="document.title='A6-R'"></p>` bo‘lib tushgan.
   * **Sabab:** Shablon ichida `{{ q|safe }}` yozilgani sababli Jinja kiritmani filtrlamagan. (Dalil D2).

Terminaldan `curl` orqali tekshirish:
```bash
curl --noproxy "*" -sS -G http://app.a6.test:8006/reflect --data-urlencode "q=<b>A6</b>"
```
*Kutiladigan natija:* Javobda `<b>A6</b>` teglari kodlanmasdan, aynan xom HTML holatida qaytadi.

---

#### 3-qadam: Stored XSS ni tekshirish (Dalil D3)
1. Menyudan **Stored** havolasini oching (`http://app.a6.test:8006/notes`).
2. Izoh matn maydoniga quyidagi payloaddan foydalaning:
   ```html
   <img src=/missing onerror="document.title='A6-S'">
   ```
3. **"Saqlash"** tugmasini bosing.
4. Sahifa sarlavhasi **`A6-S`** ga aylanadi.
5. Endi brauzer manzil satriga qayta `http://app.a6.test:8006/notes` deb yozib kiring (yoki yangi tabda oching).
6. **Natijani kuzating:** Siz yangi GET so‘rovi yubordingiz, hech qanday payload yubormadingiz, ammo server o‘z xotirasidagi ro‘yxatdan o‘sha izohni `{{ note|safe }}` orqali yana chiqardi va tab sarlavhasi yana **`A6-S`** bo‘ldi. Bu saqlangan (Stored) XSS ekanini isbotlaydi (Dalil D3).

---

#### 4-qadam: DOM-based XSS ni tekshirish (Dalil D4)
1. Menyudan **DOM** havolasini oching (`http://app.a6.test:8006/dom`).
2. Brauzer manzil satriga quyidagi to‘liq URL manzilni kiriting va `Enter` ni bosing (so‘ng `Ctrl+R` bilan yangilang):
   ```text
   http://app.a6.test:8006/dom#%3Cimg%20src%3D%2Fmissing%20onerror%3D%22document.title%3D%27A6-D%27%22%3E
   ```
3. **Natijani tahlil qiling:**
   * Sahifa sarlavhasi **`A6-D`** ga o‘zgaradi.
   * **F12 -> Network:** `GET /dom` so‘rovining manziliga qarang: serverga `#` dan keyingi qism **UMUMAN YUBORILMAGAN**!
   * **F12 -> Inspector:** `<div id="output">` ichida `<img src="/missing" onerror="...">` tuguni paydo bo‘lgan.
   * **Sabab:** `static/dom.js` kodi `location.hash` dan fragmentni o‘qib, uni tekshirmasdan `output.innerHTML = value;` orqali DOM ga joylagan. (Dalil D4).

---

#### 5-qadam: CSRF hujumini tekshirish (Dalil D5)
1. Asosiy ilovada Profil sahifasini oching (`http://app.a6.test:8006/profile`). Joriy email: `ali@lab.invalid`.
2. Brauzerning **ikkinchi tabida** tajovuzkor sahifasini oching:
   ```text
   http://evil.a6.test:8007/
   ```
3. Ushbu sahifada quyidagilarni ko‘rasiz:
   * Iframe ichida Ali ning profili ko‘rinib turibdi.
   * **"Tokensiz tashqi POST yuborish"** tugmasi bor.
4. F12 -> Network bo‘limini yoqib, **"Tokensiz tashqi POST yuborish"** tugmasini bosing!
5. **Natijani kuzating:**
   * So‘rov `http://app.a6.test:8006/profile` manziliga yuboriladi.
   * Brauzer avtomatik ravishda Alining `a6_sid` cookiesini qo‘shib jo‘natadi.
   * Sahifa Alining profiliga o‘tadi va email manzil **`changed@lab.invalid`** ga o‘zgarib qoladi!
   * **Nega bu yuz berdi?**
     1. `app.py` da `/profile` POST metodi `check_csrf()` chaqirmagan (zaiflik).
     2. `SameSite=Lax` bo‘lsa-da, ikkala origin ham `a6.test` saytiga tegishli (Same-Site) bo‘lgani uchun cookie bloklanmagan.
     3. `HttpOnly` cookieni JS dan yashirgani bilan, brauzerning uni HTTP sarlavhasiga qo‘shishini to‘xtatmagan. (Dalil D5).

---

### Bosqich 6: To‘rtta kod tuzatishini kiritish va regressiya sinovi (Dalil D6)

1-terminalda ishlayotgan asosiy ilovani `Ctrl+C` bilan to‘xtating (2-terminaldagi 8007 server ishlayversin).

Endi dasturdagi 4 ta zaiflikni tuzatamiz:

#### Tuzatish 1 va 2: Shablonlarda xavfli `|safe` filtrlarini olib tashlash
`templates/page.html` faylini tahrirlang:
```bash
nano templates/page.html
```
Fayl ichidagi quyidagi ikki qatorni toping:
```html
<p id="reflected">{{ q|safe }}</p>
```
va
```html
<div>{{ note|safe }}</div>
```
Ularni `|safe` siz holatga keltiring:
```html
<p id="reflected">{{ q }}</p>
```
va
```html
<div>{{ note }}</div>
```
Faylni saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`).

#### Tuzatish 3: DOM skriptida `innerHTML` o‘rniga `textContent` qo‘llash
`static/dom.js` faylini tahrirlang:
```bash
nano static/dom.js
```
Uchinchi qatordagi `output.innerHTML = value;` ni quyidagiga almashtiring:
```javascript
output.textContent = value;
```
Faylni saqlang.

#### Tuzatish 4: `app.py` da Profil POST so‘roviga `check_csrf()` tekshiruvini qo‘shish
`app.py` faylini tahrirlang:
```bash
nano app.py
```
`profile()` funksiyasidagi `# TODO: check_csrf() ni shu yerga qo'shing.` izohini topib, uni `check_csrf()` funksiyasiga almashtiring:
```python
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = current_user()
    if request.method == 'POST':
        check_csrf()
        email = request.form.get('email', '')
        if not 1 <= len(email) <= 120 or '@' not in email:
            abort(400)
        EMAIL[user] = email
        return redirect('/profile')
    return page('profile', email=EMAIL[user])
```
Faylni saqlang.

Sintaksisni tekshiring va serverni qayta ishga tushiring:
```bash
python -m py_compile app.py
A6_CSP=0 python app.py
```

---

#### Regressiya sinovlari (Tuzatishlarni tekshirish):
1. Brauzerda bosh sahifaga o‘tib (`http://app.a6.test:8006/`), **"Demo sessiyani boshlash"** tugmasini qayta bosing (chunki server qayta ishga tushganda yangi sessiya kaliti yaratiladi).
2. **Reflected XSS qayta sinovi:**
   `/reflect` sahifasida o‘sha `<img src=/missing onerror="document.title='A6-R'">` payloadini kiriting.
   *Natija:* Sahifada teglar oddiy matn sifatida ko‘rinadi, rasm xatosi bo‘lmaydi, tab sarlavhasi o‘zgarmaydi!
3. **Stored XSS qayta sinovi:**
   `/notes` sahifasida o‘sha payloadni izoh qilib yuboring.
   *Natija:* Izoh oddiy matn sifatida chiqadi, tab sarlavhasi `A6-S` ga aylanmaydi.
4. **DOM-based XSS qayta sinovi:**
   `/dom#%3Cimg%20src%3D%2Fmissing%20onerror%3D%22document.title%3D%27A6-D%27%22%3E` manzilini oching.
   *Natija:* `<div id="output">` ichida matn tuguni paydo bo‘ladi, tab sarlavhasi o‘zgarmaydi.
5. **Qonuniy profil yangilash:**
   Profil sahifasida emailni `ali2@lab.invalid` qilib o‘zgartiring. Formadagi `csrf` token to‘g‘ri bo‘lgani uchun email muvaffaqiyatli yangilanadi.
6. **CSRF hujumini qayta sinash:**
   Ikkinchi tabdagi `http://evil.a6.test:8007/` sahifasiga o‘ting va yana **"Tokensiz tashqi POST yuborish"** tugmasini bosing!
   *Natija:* Server darhol **HTTP 403 Forbidden** xatosini qaytaradi va email manzili o‘zgarmay qoladi!
7. **Noto‘g‘ri token sinovi:**
   Profil sahifasidagi formani Inspect qilib, hidden `csrf` qiymatini `wrong` qilib yuborsangiz ham HTTP 403 qaytishini ko‘ring.
*(Bularning barchasi Dalil D6 hisoblanadi).*

---

### Bosqich 7: CSP va CORS siyosatlarini alohida tekshirish (Dalil D7)

1-terminaldagi serverni to‘xtatib, bu safar CSP ni yoqqan holda ishga tushiring:
```bash
A6_CSP=1 python app.py
```

Brauzerda bosh sahifaga kirib, demo sessiyani yangilang.

#### 1. CSP Header va DOM skriptining ishlashi:
* F12 -> Network da sahifaning Response Headers qismida quyidagi sarlavha borligini tekshiring:
  `Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'`
* `/dom#Salom` manzilini oching: `/static/dom.js` o‘z originidan yuklangani uchun qonuniy ishlaydi va ekranda "Salom" matni chiqadi.

#### 2. Clickjacking / Iframe himoyasi (`frame-ancestors 'none'`):
* `http://evil.a6.test:8007/` sahifasini yangilang (`Ctrl+R`).
* Sahifadagi `<iframe>` blokiga qarang: profil sahifasi o‘rniga bo‘sh joy yoki xatolik ko‘rinadi.
* F12 -> Console da quyidagiga o‘xshash xabarni ko‘rasiz:
  `Content-Security-Policy: The page's settings blocked the loading of a resource at http://app.a6.test:8006/profile ('frame-ancestors').`
* Bu `frame-ancestors 'none'` direktivasi sahifani begona ramkalar ichida ochishni taqiqlaganini bildiradi.

#### 3. CORS cheklovini tekshirish:
* O‘sha `evil.a6.test:8007` sahifasida **"API javobini o‘qish"** tugmasini bosing.
* JavaScript `fetch('http://app.a6.test:8006/api/me', {credentials: 'include'})` so‘rovini yuboradi.
* Sahifada: *"Brauzer javobni o'qishga ruxsat bermadi"* degan yozuv chiqadi.
* F12 -> Console da qizil CORS xatosi ko‘rinadi:
  `Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at http://app.a6.test:8006/api/me. (Reason: CORS header 'Access-Control-Allow-Origin' missing).`
* **Xulosa:** Server so‘rovni olgan bo‘lishi mumkin (va hatto 200 qaytargan bo‘lishi mumkin), lekin `Access-Control-Allow-Origin` sarlavhasi yo‘qligi sababli brauzer javob ma’lumotini begona skriptga o‘qishga ruxsat bermadi (Dalil D7).

---

## 5-BO‘LIM: HISOBOT JADVALI VA MUAMMOLARNI BARTARAF ETISH (TROUBLESHOOTING)

### 5.1. D1–D7 Dalillarining solishtirma jadvali

Laboratoriya hisobotini to‘ldirish uchun quyidagi yakuniy jadvaldan foydalaning:

| Dalil | Sinov nomi | Dastlabki zaif holat | Tuzatish / Himoyadan keyingi holat | Amaldagi dalil ko‘rsatkichi |
| :---: | :--- | :--- | :--- | :--- |
| **D1** | Demo sessiya va cookie parametrlari | `POST /start` (302) -> `/profile` (200) | Bir xil, sessiya yaratiladi | Storage da `a6_sid`: `HttpOnly=true`, `SameSite=Lax` |
| **D2** | Reflected XSS | Marker kiritilganda `A6-R` bajariladi | Kiritma oddiy matnga aylanadi | Tab sarlavhasi o‘zgarmaydi, xom HTML teglari yo‘q |
| **D3** | Stored XSS | Izoh saqlanadi, yangi GET da ham `A6-S` | Qayta saqlangan izoh zararsiz matn | Yangi so‘rovda ham XSS bajarilmaydi |
| **D4** | DOM-based XSS | Fragment orqali `innerHTML` ga tushadi, `A6-D` | `textContent` matn tuguni yaratadi | Fragment serverga bormaydi, sarlavha o‘zgarmaydi |
| **D5** | Tashqi tokensiz POST (CSRF) | Tashqi formadan POST emailni o‘zgartiradi | — (Hali zaif holat) | Email `changed@lab.invalid` ga aylanadi |
| **D6** | To‘rtta kod tuzatishi va regressiya | Profil tokensiz POST ni qabul qiladi | Tokensiz va noto‘g‘ri tokenli POST 403 oladi | Qonuniy POST ishlaydi, soxta POST rad etiladi (403) |
| **D7** | CSP, Iframe va CORS tekshiruvi | Iframe ochiladi, inline xavf bor | Iframe bloklanadi, CORS o‘qishni to‘xtatadi | Console da CSP frame-ancestors va CORS xatolari |

---

### 5.2. Ko‘p uchraydigan muammolar va yechimlar

1. **DNS yoki manzil ochilmasligi xatosi (`Could not resolve host: app.a6.test`):**
   * *Sabab:* `/etc/hosts` fayliga yozuv kiritilmagan yoki xato yozilgan.
   * *Yechim:* `sudo nano /etc/hosts` qilib `127.0.0.1 app.a6.test evil.a6.test` borligini tekshiring va `getent hosts app.a6.test` buyrug‘ini bajaring.
2. **HTTP 401 Unauthorized xatosi:**
   * *Sabab:* Server qayta ishga tushirilganda xotiradagi sessiya kaliti yangilangan, brauzerdagi eski cookie esa yaroqsiz bo‘lib qolgan.
   * *Yechim:* Bosh sahifaga o‘tib (`http://app.a6.test:8006/`), "Demo sessiyani boshlash" tugmasini qayta bosing.
3. **XSS payloadi ishlamayapti (tab sarlavhasi o‘zgarmayapti):**
   * *Sabab:* Server `A6_CSP=1` bilan ishlab turgan bo‘lishi mumkin (CSP inline `onerror` ni bloklaydi) yoki brauzer keshida eski sahifa qolgan.
   * *Yechim:* Serverni `A6_CSP=0 python app.py` bilan ishga tushirganingizga ishonch hosil qiling va sahifani `Ctrl+F5` bilan to‘liq yangilang.
4. **CSRF testi boshida ishlamadi:**
   * *Sabab:* Ikkala sahifa ikki xil brauzerda (yoki biri Private oynada) ochilgan bo‘lishi mumkin.
   * *Yechim:* Ikkala sahifani ham bitta oddiy Firefox oynasining ikki xil ichki oynasida (tabida) oching.

---

### 5.3. Nazorat savollariga tushuntirishli javoblar

1. **Reflected va Stored tajribalarida kiritma qayerda saqlanadi va qachon bajariladi?**
   * *Reflected:* Kiritma serverda saqlanmaydi, u faqat so‘rov vaqtida URL parametridan olinib, o‘sha zahotiyoq HTML javob shabloniga qo‘shib qaytariladi.
   * *Stored:* Kiritma server xotirasidagi ro‘yxatga (`NOTES`) saqlanadi va keyinchalik har qanday mijoz `/notes` sahifasini so‘raganida server javobiga qo‘shib yuboriladi.
2. **Nega DOM tajribasidagi fragment server jurnalida yo‘q, lekin brauzerda kod bajariladi?**
   * Brauzerlar URL fragmentlarini (`#...`) HTTP so‘rov sarlavhasida serverga jo‘natmaydi. Fragment faqat mijoz tomonida qoladi va sahifadagi `dom.js` uni `location.hash` orqali o‘qib, `innerHTML` ga uzatgani uchun brauzerda bajariladi.
3. **Nega bu HTML matn kontekstida `|safe` olib tashlandi? Boy HTML uchun qanday yondashuv kerak?**
   * Oddiy matn uchun `|safe` xavflidir, chunki u foydalanuvchi kiritgan har qanday HTML va JavaScript teglarni filtrsiz sahifaga joylaydi. `|safe` olib tashlansa, Jinja xavfli belgilarni (`<`, `>`, `&`) avtomatik kodlaydi. Agar tizim boy HTML (masalan, qalin matn, ranglar) qabul qilishi kerak bo‘lsa, chiqishda xavfsiz oq ro‘yxat (whitelist) asosida ishlaydigan HTML sanitizatorlari (masalan, Python da `bleach` yoki `nh3` kutubxonasi) ishlatilishi shart.
4. **Nega formadagi yashirin (hidden) token maydoni borligi profilni dastlab himoya qilmadi?**
   * HTML formasida `<input type="hidden" name="csrf" ...>` bo‘lishining o‘zi yetarli emas. Asosiy himoya server tomonida amalga oshiriladi: dastlab `profile()` funksiyasida kelgan tokenni sessiyadagi token bilan taqqoslovchi `check_csrf()` chaqiruvi yo‘q edi.
5. **SameSite=Lax, HttpOnly va CORS nega ushbu tashqi POSTni to‘xtata olmadi?**
   * `SameSite=Lax` to‘xtatmadi, chunki `app.a6.test` va `evil.a6.test` bir xil saytga tegishli (Same-Site).
   * `HttpOnly` to‘xtatmadi, chunki tajovuzkor cookieni skript bilan o‘g‘irlamadi, brauzer HTTP so‘rovga cookieni o‘zi qo‘shib yubordi.
   * `CORS` to‘xtatmadi, chunki oddiy HTML formalari orqali yuboriladigan POST so‘rovlari CORS qoidalariga bo‘ysunmaydi.
6. **CSP inline kodni bloklasa, zaif shablonni tuzatmaslik mumkinmi?**
   * Yo‘q, aslo mumkin emas! Bu "Defense in Depth" (Ko‘p bosqichli chuqur himoya) tamoyiliga ziddir. CSP qo‘shimcha himoya qatlami hisoblanadi. Agar kelajakda CSP sozlamasida xatolik ketsa yoki eskiroq brauzer ishlatilsa, kodlanmagan shablon to‘g‘ridan-to‘g‘ri XSS ga yo‘l ochadi. Asosiy himoya doimo chiqishni to‘g‘ri kodlash bo‘lib qolishi shart.
7. **Nega faqat HTTP 200 yoki 403 raqamining o‘zi yetarli xulosa emas?**
   * Chunki HTTP 200 muvaffaqiyatli hujumda ham, qonuniy amalda ham qaytishi mumkin. Masalan, CORS bloklaganda ham server 200 qaytarishi mumkin, lekin brauzer ma’lumotni o‘qishga ruxsat bermaydi. Yoki sessiya bo‘lmaganda 401 qaytishi mumkin, buni CSRF himoyasi ishladi deb yanglishmaslik kerak. Har doim so‘rov tanasi, sarlavhalari va ilova holati birgalikda tahlil qilinishi shart.

---

## 6-BO‘LIM: FOYDALANILGAN VA TAVSIYA ETILADIGAN MANBALAR

Mavzuni yanada chuqurroq o‘rganish va hisobotda ilmiy-texnik asos sifatida keltirish uchun rasmiy manbalar:

1. **OWASP (Open Web Application Security Project):**
   * [OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) — XSS dan himoyalanish, kontekstual kodlash va xavfsiz sinklar bo‘yicha asosiy qo‘llanma.
   * [OWASP Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) — CSRF tokenlari, SameSite va himoya strategiyalari.
   * [OWASP DOM based XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html) — DOM xavfsizligi, xavfli API lar (`innerHTML`, `document.write`) va ularning xavfsiz muqobillari.
2. **MDN Web Docs (Mozilla Developer Network):**
   * [Set-Cookie: SameSite](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite) — Cookie SameSite atributining Lax, Strict va None rejimlari tahlili.
   * [Understanding "same-site" and "same-origin"](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Same-site_and_same-origin) — Origin va Site tushunchalarining aniq farqlari.
   * [Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) — CORS mexanizmi, preflight so‘rovlar va ruxsat sarlavhalari.
   * [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) — CSP direktivalari: `script-src`, `frame-ancestors`, `default-src`.
3. **Framework va Standartlar:**
   * [Flask 3.1 Documentation — Security Considerations](https://flask.palletsprojects.com/en/stable/security/) — Flask dasturlarida xavfsizlik, sessiyalar va Jinja2 autoescaping qoidalari.
   * [RFC 6265bis — Cookies: HTTP State Management Mechanism](https://datatracker.ietf.org/doc/html/draft-ietf-httpbis-rfc6265bis) — SameSite atributining xalqaro Internet standarti spetsifikatsiyasi.
