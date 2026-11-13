# VEB DASTURLAR XAVFSIZLIGI — 5-SEMESTR
## A8-AMALIY MASHG'ULOT: API XAVFSIZLIGI VA ZAMONAVIY AUTENTIFIKATSIYA MEXANIZMLARI
### 1-VARIANT: O‘quv buyurtmalar API xizmatini himoyalash bo‘yicha to‘liq va batafsil qo‘llanma

---

## MUNDARIJA
1. [Laboratoriya tavsifi va Ishchi muhit arxitekturasi](#1-laboratoriya-tavsifi-va-ishchi-muhit-arxitekturasi)
2. [Mashg‘ulotning maqsadi va vazifalari](#2-mashgulotning-maqsadi-va-vazifalari)
3. [Nazariy asoslar va xavfsizlik tushunchalari](#3-nazariy-asoslar-va-xavfsizlik-tushunchalari)
   - 3.1. Autentifikatsiya va Avtorizatsiya farqi
   - 3.2. JSON Web Token (JWT) mexanizmi va xavfsizlik claimlari
   - 3.3. OWASP API1:2023 — BOLA (Broken Object Level Authorization)
   - 3.4. OWASP API5:2023 — BFLA (Broken Function Level Authorization)
   - 3.5. OWASP API4:2023 — Cheklanmagan resurs sarfi va Rate Limiting
   - 3.6. API Kalitlari (API Keys) va integratsiya xavfsizligi
   - 3.7. GraphQL so‘rovlarida avtorizatsiya va resurs nazorati
   - 3.8. OAuth 2.0 / OIDC va API Gateway o‘rni (Multi-worker arxitekturasi)
4. [Amaliy mashg‘ulotni bajarish bo‘yicha ketma-ket qadamlar (Har bir CLI buyruq tahlili bilan)](#4-amaliy-mashgulotni-bajarish-boyicha-ketma-ket-qadamlar)
   - 4.1. 1-qadam: Virtual muhit va bog‘liqliklarni o‘rnatish
   - 4.2. 2-qadam: Dastur fayllarini yaratish va sinovdan o‘tkazish (`issue.py`, `app.py`)
   - 4.3. 3-qadam: Serverni ishga tushirish va 1-nazorat so‘rovi (Dalil D1)
   - 4.4. 4-qadam: JWT autentifikatsiyasini 7 xil token bilan tekshirish (Dalil D2)
   - 4.5. 5-qadam: Obyekt darajasidagi avtorizatsiya — BOLA sinovi (Dalil D3)
   - 4.6. 6-qadam: Funksiya darajasidagi huquq (BFLA) va API Kaliti sinovi (Dalil D4)
   - 4.7. 7-qadam: Rate Limiting sinovi va zaifliklarni kodda tuzatish (Dalil D5)
   - 4.8. 8-qadam: Qo‘shimcha loyiha tahlili (GraphQL, API Gateway, Xavfsiz ma'lumot tiklash)
5. [Dalillar (Skrinshotlar) tizimi va Hisobot talablari](#5-dalillar-skrinshotlar-tizimi-va-hisobot-talablari)
   - 5.1. Skrinshotlarni nomlash va `images/` papkasiga saqlash tartibi
   - 5.2. D6 — Yakuniy natijalar taqqoslash jadvali
   - 5.3. Hisobotda nimalar bo‘lishi va nimalar kiritilmasligi kerak
6. [Nazorat savollari va ularning to‘liq ilmiy javoblari](#6-nazorat-savollari-va-ularning-toliq-ilmiy-javoblari)
7. [Baholash mezonlari (10 ballik tizim)](#7-baholash-mezonlari-10-ballik-tizim)
8. [Foydalanilgan rasmiy manbalar](#8-foydalanilgan-rasmiy-manbalar)
9. [ILOVALAR: To‘liq dasturiy kodlar](#9-ilovalari-toliq-dasturiy-kodlar)
   - 9.1. 1-ilova: `app.py` (To‘liq birlashtirilgan Flask server kodi)
   - 9.2. 2-ilova: `issue.py` (Lokal o‘quv token generatori kodi)

---

## 1. LABORATORIYA TAVSIFI VA ISHCHI MUHIT ARXITEKTURASI

Ushbu laboratoriya ishi zamonaviy veb-ilovalarda API (Application Programming Interface) xavfsizligini tahlil qilish, autentifikatsiya va avtorizatsiya mexanizmlaridagi zaifliklarni aniqlash hamda ularni amaliy tuzatishga bag‘ishlangan.

### Sizning ishchi muhitingiz bo‘yicha maxsus ko‘rsatmalar:
1. **Asosiy operatsion tizim (Host OS):** Ubuntu Linux.
2. **Virtualizatsiya:** VMware Workstation orqali ishga tushirilgan Ubuntu Server (yoki Ubuntu VM).
   > **DIQQAT: Windows 11 ga ehtiyoj yo‘q!**
   > Garchi topshiriq metodikasida umumiy kompyuter sinflari uchun Windows mezbon sifatida tilga olingan bo‘lsa-da, ushbu A8 laboratoriya ishidagi barcha komponentlar (Python 3.12, Flask 3.1.3, PyJWT 2.13.0, cURL, bash) **sof Linux muhitida** ishlaydi. Shuning uchun qo‘shimcha Windows 11 virtual mashinasini ochishingiz umuman shart emas. Barcha amallarni to‘g‘ridan-to‘g‘ri o‘zingizning Ubuntu Server VM terminalida bajarasiz.
3. **Tarmoq konfiguratsiyasi:** 
   - Siz **o‘zingizning shaxsiy/lokal Wi-Fi tarmog‘ingizdan** foydalanasiz (Universitet Wi-Fi tarmog‘i emas).
   - Bu shuni anglatadiki, sizga hech qanday universitet proksi-serveri (`proxy.tuit.uz`), maxsus ichki autentifikatsiya yoki qo‘shimcha SSL-sertifikatlar kerak emas.
   - VMware virtual mashinangiz tarmoq sozlamasi **NAT** holatida bo‘lishi kifoya. Tizim to‘g‘ridan-to‘g‘ri internetga chiqib, `apt` va `pip` paketlarini rasmiy repozitoriylardan yuklab oladi.
4. **Xizmatning tinglash chegarasi (Loopback):**
   - API server faqat virtual mashinaning ichki loopback manzilida: `http://127.0.0.1:8008` portida tinglaydi.
   - Tashqi tarmoqqa yoki LANga hech qanday port-forwarding qilish talab etilmaydi. Hamma so‘rovlar (mijoz `curl` buyruqlari) ayni shu Ubuntu VMning o‘zidan yuboriladi.

---

## 2. MASHG‘ULOTNING MAQSADI VA VAZIFALARI

### Asosiy maqsad:
REST API xizmatlarida **JWT (JSON Web Token)** orqali foydalanuvchini autentifikatsiya qilish, buyurtma egasini (obyekt darajasida) va administrator huquqlarini (funksiya darajasida) alohida nazorat qilish hamda autentifikatsiyadan o‘tgan mijoz uchun so‘rovlar tezligini (**Rate Limiting**) cheklashni amalda o‘rganish.

### Asosiy vazifalar:
1. **JWT tekshiruvini chuqur tahlil qilish:** Oddiy Base64url dekodlash bilan haqiqiy kriptografik imzo va xavfsizlik claimlarini (`sub`, `iss`, `aud`, `iat`, `exp`) tekshirish o‘rtasidagi farqni ajratish.
2. **BOLA (Broken Object Level Authorization) zaifligini tadqiq qilish:** Autentifikatsiyadan o‘tgan oddiy talaba (`ali`) tokeni bilan boshqa talabaning (`vali`) 202-raqamli buyurtmasiga noqonuniy kirishni ko‘rsatish va himoyalash.
3. **BFLA (Broken Function Level Authorization) zaifligini tadqiq qilish:** Oddiy talaba (`student` roli) imtiyozli administrator funksiyasi (`/admin/summary`) ga kirishini aniqlash va qat'iy rol tekshiruvini joriy etish.
4. **API Kaliti (API Key) integratsiyasini sinash:** Tizimlararo integratsiya uchun ishlatiladigan `X-API-Key` mexanizmini foydalanuvchi tokenlaridan (`Bearer JWT`) ajratish.
5. **Rate Limiting joriy etish:** DoS hujumlari va resurslarni suiiste'mol qilishning oldini olish uchun vaqtli sirpanuvchi oyna (sliding window) asosida so‘rovlar sonini cheklash (HTTP 429 Too Many Requests va `Retry-After`).
6. **Kod darajasida xavfsizlikni ta'minlash:** `app.py` ichidagi 3 ta zaif funksiyani (`order_weak`, `admin_weak`, `limit_weak`) himoyalangan funksiyalarga almashtirib, avvalgi endpointlarda xavfsizlikni qayta sinash.

### Kirish siyosati va Ruxsatlar matritsasi:
Tizimda 3 ta akkaunt mavjud bo‘lib, ularning huquqlari quyidagi jadval bilan qat'iy belgilangan:

| Akkaunt   | Rol (USERS) | 101-buyurtma (Daftar, egasi: ali) | 202-buyurtma (Kitob, egasi: vali) | Admin Summary (`/admin/summary`) |     |     |
| :-------- | :---------- | :-------------------------------- | :-------------------------------- | :------------------------------- | --- | --- |
| **ali**   | `student`   | **Ruxsat (200 OK)**               | **Rad (403 Forbidden)**           | **Rad (403 Forbidden)**          |     |     |
| **vali**  | `student`   | **Rad (403 Forbidden)**           | **Ruxsat (200 OK)**               | **Rad (403 Forbidden)**          |     |     |
| **admin** | `admin`     | **Ruxsat (200 OK)**               | **Ruxsat (200 OK)**               | **Ruxsat (200 OK)**              |     |     |

---

## 3. NAZARIY ASOSLAR VA XAVFSIZLIK TUSHUNCHALARI

### 3.1. Autentifikatsiya va Avtorizatsiya farqi
- **Autentifikatsiya (Authentication - AuthN):** "Siz kimsiz?" degan savolga javob beradi. Foydalanuvchining shaxsini tasdiqlaydi (masalan, login/parol orqali tekshirib, unga JWT berish).
- **Avtorizatsiya (Authorization - AuthZ):** "Siz nima qila olasiz?" degan savolga javob beradi. Autentifikatsiyadan o‘tgan shaxsning ayni obyekt (buyurtma, fayl) yoki amal ustida yetarli huquqi bor-yo‘qligini tekshiradi.
> **Xavfsizlik qoidasi:** To‘g‘ri imzolangan va haqiqiy JWT tokeniga ega bo‘lish foydalanuvchiga tizimdagi barcha resurslarni ko‘rish huquqini bermaydi!

### 3.2. JSON Web Token (JWT) mexanizmi va xavfsizlik claimlari
JWT (RFC 7519) — ixcham, xavfsiz URL-mos formatdagi ma'lumot uzatish vositasi. U nuqta bilan ajratilgan 3 qismdan iborat:
```
header.payload.signature
```
- **Header:** Token turi (`typ: "JWT"`) va imzolash algoritmi (`alg: "HS256"`).
- **Payload:** Foydalanuvchi ma'lumotlari (claimlar):
  - `sub` (subject) — foydalanuvchi identifikatori (masalan, `ali`).
  - `iss` (issuer) — tokenni bergan tomon (`a8-issuer`).
  - `aud` (audience) — tokenni qabul qiluvchi maqsadli API (`a8-api`).
  - `iat` (issued at) — token berilgan vaqt (Unix timestamp).
  - `exp` (expiration time) — tokenning amal qilish muddati tugash vaqti.
- **Signature (Imzo):** Header va Payload birlashtirilib, serverning maxfiy kaliti (`jwt.key`) bilan HMAC-SHA256 algoritmi orqali imzolanadi:
  $$\text{Signature} = \text{HMAC-SHA256}(\text{base64Url}(header) + "." + \text{base64Url}(payload), \text{SECRET\_KEY})$$

> **MUHIM:** Header va Payload faqat Base64url formatida kodlangan, ular shifrlanmagan! Har qanday shaxs ularni o‘qiy oladi. Lekin maxfiy kalitsiz imzoni soxtalashtira olmaydi.
> Server tokenni qabul qilganda faqat payloadni o‘qib qo‘ymasdan:
> 1. Algoritmni qat'iy tekshirishi kerak (`algorithms=['HS256']`). Hech qachon mijoz yuborgan headerdagi `none` yoki boshqa algoritmga ishonmaslik lozim!
> 2. `require: ['sub', 'iat', 'exp', 'iss', 'aud']` opsiyasi orqali `exp` mavjudligini majburiy talab qilishi lozim. Agar `exp` mavjudligi talab qilinmasa, muddatsiz tokenlar abadiy xavf tug‘diradi.

### 3.3. OWASP API1:2023 — BOLA (Broken Object Level Authorization)
BOLA (avvalgi nomi IDOR — Insecure Direct Object References) — API xavfsizligida 1-raqamli xavf hisoblanadi.
- **Mohiyati:** Server so‘rov yuboruvchining identifikatorini (masalan, `ali`) biladi, lekin URL orqali so‘ralgan obyekt (masalan, `/api/orders/202`) aynan shu foydalanuvchiga tegishlimi yoki yo‘qligini tekshirmaydi.
- **Zaiflik:** `ali` o‘z tokeni bilan 202-IDni yuborsa, tizim `vali`ning buyurtmasini qaytaradi.
- **Tuzatish:** Har bir obyekt qaytarilishidan oldin biznes-mantiq darajasida tekshiriladi:
  ```python
  if order['owner'] != user['sub'] and user['role'] != 'admin':
      abort(403)
  ```
  *(Bu yerda `AND` mantiqiy amali ishlatiladi: foydalanuvchi obyekt egasi bo‘lmasa HAMDA u administrator bo‘lmasa — qat'iy 403 Forbidden beriladi).*

### 3.4. OWASP API5:2023 — BFLA (Broken Function Level Authorization)
BFLA — API funksiyalariga kirish huquqlarining to‘g‘ri cheklanmasligi.
- **Mohiyati:** Ma'muriy yoki nozik amallar (masalan, `/admin/summary`, foydalanuvchini o‘chirish, hisobot olish) oddiy foydalanuvchilar uchun ochiq qoladi.
- **Zaiflik:** `ali` (`student` roli) ma'muriy endpointga so‘rov yuborganda, tizim faqat token borligini tekshiradi, lekin rolni tekshirmasdan 200 OK qaytaradi.
- **Tuzatish:**
  ```python
  if user['role'] != 'admin':
      abort(403)
  ```
  *(Rol mijoz bergan tokendan emas, serverdagi ishonchli `USERS` bazasidan olinadi).*

### 3.5. OWASP API4:2023 — Cheklanmagan resurs sarfi va Rate Limiting
- **Xavf:** Agar mijoz yuboradigan so‘rovlar soni cheklanmasa, tajovuzkor yoki nosoz skript server resurslarini (CPU, xotira, ma'lumotlar bazasi ulanishlari) to‘liq band qilib, DoS (Hizmat ko‘rsatishni rad etish) keltirib chiqaradi.
- **Yechim (Sliding Window — Sirpanuvchi oyna):**
  - Har bir foydalanuvchi (`sub`) uchun so‘rovlar vaqti saqlanadi.
  - Bizning laboratoriyada oyna `WINDOW = 10` soniya, ruxsat etilgan limit `LIMIT = 5` ta so‘rov.
  - Limit oshganda server **HTTP 429 Too Many Requests** qaytaradi va `Retry-After: <kutish_soniyasi>` sarlavhasini yuboradi.

### 3.6. API Kalitlari (API Keys) va Integratsiya xavfsizligi
- **API Kaliti:** Odatda foydalanuvchini emas, balki murojaat qilayotgan tashqi tizim yoki mikroxizmatni tanitadi (`lab-integration`).
- **Xavfsiz amaliyot:**
  - API kaliti URL parametrida (`?api_key=...`) uzatilmasligi kerak (chunki u server loglarida, brauzer tarixida va proksilarda saqlanib qoladi). U maxsus HTTP sarlavhasida (`X-API-Key`) uzatiladi.
  - Doimiy xavfsiz vaqt taqqoslash funksiyasi (`hmac.compare_digest`) orqali tekshiriladi (Timing Attack'dan himoya).
  - API kaliti foydalanuvchi o‘rnini bosuvchi yuqori huquqli token sifatida ishlatilmasligi kerak.

### 3.7. GraphQL so‘rovlarida avtorizatsiya va resurs nazorati
GraphQL REST'dan farqli ravishda yagona endpoint (`/graphql`) orqali ishlaydi va mijoz bir vaqtning o‘zida aliaslar yordamida bir nechta so‘rovni birlashtirishi mumkin:
```graphql
query {
  first: order(id: 101) { id item }
  second: order(id: 202) { id item }
}
```
- **Xavfsizlik muammosi:** Bitta HTTP so‘rovi uchun faqat kirish nuqtasida autentifikatsiya qilish yetarli emas. Har bir maydon (field/resolver) darajasida obyekt egasi tekshirilishi kerak (`order` resolveri ichida).
- **Resurs nazorati:** Mijoz bitta so‘rov ichida minglab resurslarni yoki cheksiz chuqurlikdagi (nested) so‘rovlarni so‘rashi mumkin. Shu sababli **Query Depth Limiting** va **Query Cost Analysis** (so‘rov murakkabligini baholash) joriy etilishi shart.

### 3.8. OAuth 2.0 / OIDC va API Gateway o‘rni (Multi-worker arxitekturasi)
- **OAuth 2.0 va OIDC:** O‘quv `issue.py` skripti o‘rnida real hayotda Keycloak, Auth0 yoki Google Identity kabi markaziy OAuth/OIDC provayderlari ishlaydi. Ular `Access Token` chiqaradi.
- **API Gateway:** Tarmoq chegarasida turadi; SSL terminatsiyasi, dastlabki token validatsiyasi va umumiy IP-kvotani boshqaradi. **Lekin API Gateway BOLA'dan himoya qila olmaydi**, chunki u buyurtma 101 aynan kimga tegishli ekanini bilmaydi — bu biznes-mantiq mikroxizmat ichida tekshiriladi.
- **Multi-worker muammosi:** Agar API bir nechta worker'da (masalan Gunicorn 4 ta jarayonda) ishlasa, Python xotirasidagi `BUCKETS` lug‘ati xotirada taqsimlanmagan bo‘ladi. Bir worker boshqasining hisoblagichini ko‘rmaydi. Yechim: **Redis** yoki **Memcached** kabi umumiy markazlashtirilgan kesh va atomar operatsiyalar (`INCR`, `EXPIRE`).

---

## 4. AMALIY MASHG‘ULOTNI BAJARISH BO‘YICHA KETMA-KET QADAMLAR
### (Har bir CLI buyruqning to‘liq tahlili va nima ish qilishi bilan)

Barcha amallarni o‘zingizning **Ubuntu terminalida** bajarasiz.

---

### 4.1. 1-qadam: Virtual muhit va bog‘liqliklarni o‘rnatish

Terminalni oching va quyidagi buyruqlarni ketma-ket bajaring:

#### 1-buyruq: Tizim paketlari indeksini yangilash
```bash
sudo apt update
```
- **Nima ish qiladi:** Ubuntu operatsion tizimining paket repozitoriylaridagi mavjud dasturlar ro‘yxati va yangi versiyalarini yangilaydi. Internetga ulanish to‘g‘ri ishlayotganini tekshiradi.

#### 2-buyruq: Kerakli tizim vositalarini o‘rnatish
```bash
sudo apt install -y python3 python3-venv python3-pip curl nano
```
- **Nima ish qiladi:**
  - `python3` — Python tili interpretatori.
  - `python3-venv` — Alohida izolyatsiyalangan virtual muhit yaratish moduli.
  - `python3-pip` — Python kutubxonalarini o‘rnatuvchi paket menejeri.
  - `curl` — Buyruqlar satri orqali HTTP so‘rovlarini yuboruvchi tarmoq mijozi.
  - `nano` — Terminal ichidagi qulay matn muharriri.
  - `-y` — O‘rnatish jarayonida foydalanuvchidan so‘raladigan barcha tasdiqlashlarga avtomatik "ha" (yes) deb javob beradi.

#### 3-buyruq: Laboratoriya ishchi papkasini yaratish va unga o‘tish
```bash
mkdir -p ~/a8-lab
cd ~/a8-lab
```
- **Nima ish qiladi:**
  - `mkdir -p ~/a8-lab` — Foydalanuvchining uy papkasida (`~`) `a8-lab` nomli yangi katalog yaratadi (`-p` agar katalog mavjud bo‘lsa xatolik bermaydi).
  - `cd ~/a8-lab` — Yaratilgan ishchi katalogga kiradi.

#### 4-buyruq: Python virtual muhitini yaratish va faollashtirish
```bash
python3 -m venv .venv
source .venv/bin/activate
```
- **Nima ish qiladi:**
  - `python3 -m venv .venv` — Tizim Python'iga daxl qilmasdan, loyiha uchun izolyatsiyalangan `.venv` virtual muhitini barpo etadi.
  - `source .venv/bin/activate` — Mazkur virtual muhitni joriy terminal sessiyasida faollashtiradi (terminal boshida `(.venv)` paydo bo‘ladi).

#### 5-buyruq: Laboratoriya uchun talab qilingan aniq versiyadagi paketlarni o‘rnatish
```bash
python -m pip install Flask==3.1.3 PyJWT==2.13.0
```
- **Nima ish qiladi:**
  - `Flask==3.1.3` — API serverni qurish uchun yengil veb-freymvork.
  - `PyJWT==2.13.0` — JSON Web Tokenlarni generatsiya qilish, imzolash va dekodlash kutubxonasi.
  - Versiyalarning aniq ko‘rsatilishi muhit barqarorligini ta'minlaydi.

#### 6-buyruq: O‘rnatilgan paketlar ro‘yxatini qulflash
```bash
python -m pip freeze > requirements-lock.txt
```
- **Nima ish qiladi:** Virtual muhitdagi barcha o‘rnatilgan paketlar va ularning bog‘liqliklarini versiyalari bilan `requirements-lock.txt` fayliga yozib qo‘yadi (bu hisobotga ilova qilinadigan majburiy fayl).

---

### 4.2. 2-qadam: Dastur fayllarini yaratish va sinovdan o‘tkazish (`issue.py`, `app.py`)

Ushbu qadamda laboratoriya dasturlarining boshlang‘ich kodlari yaratiladi.

#### 1. `issue.py` faylini yaratish:
Terminalda buyruq bering:
```bash
nano issue.py
```
Va ichiga ushbu qo‘llanmaning **9.2-ilovasida** keltirilgan `issue.py` kodini to‘liq nusxalab joylashtiring. Faylni saqlash uchun: `Ctrl+O`, `Enter`, chiqish uchun: `Ctrl+X`.

#### 2. `app.py` faylini yaratish:
Terminalda buyruq bering:
```bash
nano app.py
```
Va ichiga ushbu qo‘llanmaning **9.1-ilovasida** keltirilgan birlashtirilgan `app.py` kodini to‘liq nusxalab joylashtiring. Saqlab chiqing (`Ctrl+O`, `Enter`, `Ctrl+X`).

#### 3. Sintaksis va xatoliklarni tekshirish (Kompilyatsiya):
```bash
python -m py_compile app.py issue.py
```
- **Nima ish qiladi:** Python fayllarida indentatsiya (bo‘sh joylar), qavslar yoki sintaktik xatolar yo‘qligini tekshiradi. Agar hech qanday xatolik chiqmasa, kod toza tuzilgan.

#### 4. Tokenlar va maxfiy kalitlarni generatsiya qilish:
```bash
python issue.py
```
- **Nima ish qiladi:**
  - Loyiha papkasida `jwt.key` (32 baytli kriptografik maxfiy kalit) va `api.key` fayllarini yaratadi va ularga faqat joriy foydalanuvchi o‘qishi uchun qat'iy `0600` huquqini beradi.
  - Turli sinovlar uchun 7 xil JWT tokenlarini va API kalitini yaratib, ularni `tokens.env` fayliga eksport qiladi:
    - `ALI`, `VALI`, `ADMIN` — Qonuniy tokenlar (amal qilish muddati 2 soat).
    - `EXPIRED` — Muddati o‘tgan token.
    - `WRONG_AUD` — Auditoriyasi noto‘g‘ri (`other-api`).
    - `WRONG_ISS` — Beruvchisi noto‘g‘ri (`other-issuer`).
    - `NO_EXP` — `exp` claimi olib tashlangan token.
    - `TAMPERED` — Subyekti `admin`ga o‘zgartirilgan, lekin imzosi buzilgan qalbaki token.
    - `API_KEY` — Tizimlararo integratsiya kaliti.
- **Kutiladigan chiqish:** `A8 tokens.env tayyor; amal qilish muddati: 2 soat`

#### 5. Boshlang‘ich kod nusxasini saqlab qo‘yish:
```bash
cp app.py app_before.py
```
- **Nima ish qiladi:** Tuzatish kiritishdan oldingi asl (zaif) holatni keyinchalik taqqoslash uchun `app_before.py` nomida saqlaydi.

---

### 4.3. 3-qadam: Serverni ishga tushirish va 1-nazorat so‘rovi (Dalil D1)

Laboratoriyada ishlash uchun **ikkita alohida terminal oynasi** kerak bo‘ladi:
- **1-terminal:** API server ishlaydigan fon terminali.
- **2-terminal:** Mijoz sifatida `curl` so‘rovlarini yuboradigan terminal.

#### 1-terminalda: Serverni ishga tushirish
```bash
python app.py
```
- **Nima ish qiladi:** Flask API serverini `127.0.0.1:8008` manzilida ishga tushiradi.
- **Kutiladigan natija:**
  ```text
  * Serving Flask app 'app'
  * Debug mode: off
  WARNING: This is a development server. Do not use it in a production deployment.
  * Running on http://127.0.0.1:8008
  Press CTRL+C to quit
  ```
  *(Bu terminalni yopmang va `Ctrl+C` bosmang, server doimiy ishlab turishi kerak).*

---

#### 2-terminalda: Mijoz muhitini tayyorlash va D1 dalilini olish

Yangi terminal oynasini oching va buyruqlarni kiriting:

```bash
cd ~/a8-lab
source .venv/bin/activate
source tokens.env
BASE=http://127.0.0.1:8008
```
- **Har bir buyruq tahlili:**
  - `cd ~/a8-lab` — Ishchi papkaga o‘tish.
  - `source .venv/bin/activate` — Virtual muhitni yoqish.
  - `source tokens.env` — `tokens.env` faylidagi barcha tokenlarni (`$ALI`, `$VALI`, `$ADMIN`, `$EXPIRED`, `$API_KEY` va h.k.) joriy terminalning muhit o‘zgaruvchilariga yuklaydi.
  - `BASE=http://127.0.0.1:8008` — Server manzilini qisqa o‘zgaruvchiga oladi.

#### Nazorat so‘rovlarini yuborish:
```bash
curl -i "$BASE/"
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/me"
```
- **CLI bayroqlari tahlili:**
  - `curl` — URLga so‘rov yuborish vositasi.
  - `-i` (include) — Server qaytargan HTTP sarlavhalarini (Status code, Content-Type, Cache-Control va h.k.) ham konsolda ko‘rsatadi.
  - `-H "Authorization: Bearer $ALI"` — So‘rov sarlavhasiga (Header) Bearer token formatida `ali` foydalanuvchisining JWT tokenini qo‘shadi.
- **Kutiladigan natija:**
  - 1-so‘rov: `HTTP/1.1 200 OK`, JSON javob: `{"lab":"A8 / 1-variant","port":8008}`
  - 2-so‘rov: `HTTP/1.1 200 OK`, JSON javob: `{"role":"student","sub":"ali"}`

> **📸 DALIL D1 (Skrinshot):**
> 2-terminalda tizim ma'lumotlari (`uname -a`, `python3 --version`), serverning 8008 portda javob bergani va `ali` uchun `/api/me` so‘rovining 200 OK javobi ko‘ringan skrinshotni oling va `images/1_d1_muhit.png` nomi bilan saqlang.

---

### 4.4. 4-qadam: JWT autentifikatsiyasini 7 xil token bilan tekshirish (Dalil D2)

Ushbu bosqichda bir xil `/api/me` endpointiga 7 xil holatdagi tokenlar yuboriladi va server qanday javob berishi sinovdan o‘tkaziladi:

```bash
# 1. Tokensiz so'rov
curl -i "$BASE/api/me"

# 2. To'g'ri va haqiqiy token (ALI)
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/me"

# 3. O'zgartirilgan, soxta token (TAMPERED)
curl -i -H "Authorization: Bearer $TAMPERED" "$BASE/api/me"

# 4. Muddati o'tgan token (EXPIRED)
curl -i -H "Authorization: Bearer $EXPIRED" "$BASE/api/me"

# 5. Auditoriyasi noto'g'ri token (WRONG_AUD)
curl -i -H "Authorization: Bearer $WRONG_AUD" "$BASE/api/me"

# 6. Beruvchisi noto'g'ri token (WRONG_ISS)
curl -i -H "Authorization: Bearer $WRONG_ISS" "$BASE/api/me"

# 7. Amal qilish muddati (exp) maydoni bo'lmagan token (NO_EXP)
curl -i -H "Authorization: Bearer $NO_EXP" "$BASE/api/me"
```

#### Har bir sinov natijasi va tahlili:
1. **Tokensiz:** `HTTP/1.1 401 Unauthorized` va `WWW-Authenticate: Bearer`. Server autentifikatsiya sarlavhasi yo‘qligi sababli so‘rovni darhol rad etdi.
2. **ALI:** `HTTP/1.1 200 OK`. Imzo to‘g‘ri, barcha talab qilingan claimlar mos keldi, `{"role":"student","sub":"ali"}` qaytdi.
3. **TAMPERED:** `HTTP/1.1 401 Unauthorized`. Tajovuzkor payload ichidagi `sub`ni `admin`ga o‘zgartirgan, biroq maxfiy kalitni bilmagani uchun imzoni qayta hosil qila olmagan. Server imzoni tekshirganda nomuvofiqlikni aniqlab, tokenni rad etdi (`SignatureVerificationError`).
4. **EXPIRED:** `HTTP/1.1 401 Unauthorized`. Imzo to‘g‘ri, lekin `exp` vaqti serverning joriy vaqtidan o‘tib ketgan (`ExpiredSignatureError`).
5. **WRONG_AUD:** `HTTP/1.1 401 Unauthorized`. Imzo to‘g‘ri, ammo `aud` claimi kutilgan `a8-api` emas, `other-api` bo‘lgani uchun rad etildi (`InvalidAudienceError`).
6. **WRONG_ISS:** `HTTP/1.1 401 Unauthorized`. Imzo to‘g‘ri, biroq `iss` claimi kutilgan `a8-issuer` emas, `other-issuer` bo‘lgani uchun rad etildi (`InvalidIssuerError`).
7. **NO_EXP:** `HTTP/1.1 401 Unauthorized`. Imzo to‘g‘ri, lekin server `options={'require': ['sub', 'iat', 'exp', ...']}` orqali `exp` bo‘lishini majburiy talab qilgan. Token ichida `exp` yo‘qligi sababli rad etildi (`MissingRequiredClaimError`).

> **📸 DALIL D2 (Skrinshot):**
> 7 ta so‘rov va ularning HTTP statuslari ketma-ket chiqqan terminal skrinshotini oling va `images/2_d2_jwt.png` nomi bilan saqlang.

---

### 4.5. 5-qadam: Obyekt darajasidagi avtorizatsiya — BOLA sinovi (Dalil D3)

Foydalanuvchi `ali` identifikatoriga ega. Tizimda ikkita buyurtma bor:
- 101-buyurtma: egasi `ali` (Daftar).
- 202-buyurtma: egasi `vali` (Kitob).

#### 2-terminalda quyidagi so‘rovlarni bajaring:

```bash
# 1. ALI o'zining 101-buyurtmasini so'raydi (Zaif endpoint)
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/orders/101"

# 2. ALI o'z tokeni bilan boshqa talabaning (VALI) 202-buyurtmasini so'raydi (BOLA ZAIFLIGI!)
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/orders/202"

# 3. ALI himoyalangan endpoint orqali VALIning 202-buyurtmasini so'raydi
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/safe/orders/202"

# 4. VALI o'zining 202-buyurtmasini so'raydi (Qonuniy kirish)
curl -i -H "Authorization: Bearer $VALI" "$BASE/api/safe/orders/202"

# 5. ADMIN 202-buyurtmani so'raydi (Administratorga ruxsat berilgan)
curl -i -H "Authorization: Bearer $ADMIN" "$BASE/api/safe/orders/202"

# 6. ALI mavjud bo'lmagan 999-buyurtmani so'raydi
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/safe/orders/999"
```

#### Natijalar tahlili:
- 1-so‘rov: `200 OK` — `ali` o‘z buyurtmasini oldi (`{"id":101,"item":"Daftar","owner":"ali"}`).
- 2-so‘rov: `200 OK` — **BOLA DALILI!** Zaif endpointda `ali` hech qanday to‘siqsiz `vali`ga tegishli buyurtmani ko‘ra oldi (`{"id":202,"item":"Kitob","owner":"vali"}`).
- 3-so‘rov: `403 Forbidden` — Himoyalangan endpointda `order_safe()` funksiyasi `order['owner'] != user['sub']` ekanini aniqlab, kirishni qat'iy taqiqladi.
- 4-so‘rov: `200 OK` — `vali` o‘z buyurtmasiga qonuniy kirdi.
- 5-so‘rov: `200 OK` — Administrator tizim siyosatiga ko‘ra har qanday buyurtmani ko‘rish huquqiga ega.
- 6-so‘rov: `404 Not Found` — Mavjud bo‘lmagan obyekt uchun `404` qaytishi boshqa birovning mavjud obyektiga qo‘yilgan `403` cheklovidan aniq farqlanadi.

> **📸 DALIL D3 (Skrinshot):**
> Zaif endpointda `owner=vali` ma'lumoti `ali` tokeni bilan olingani va xavfsiz endpointda `403 Forbidden` qaytgani aks etgan skrinshotni `images/3_d3_bola.png` nomi bilan saqlang.

---

### 4.6. 6-qadam: Funksiya darajasidagi huquq (BFLA) va API Kaliti sinovi (Dalil D4)

#### A) BFLA sinovi:
```bash
# 1. ALI (oddiy talaba) administrator funksiyasini chaqiradi (Zaif endpoint)
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/admin/summary"

# 2. ALI xavfsiz administrator funksiyasini chaqiradi
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/safe/admin/summary"

# 3. ADMIN xavfsiz administrator funksiyasini chaqiradi (Qonuniy kirish)
curl -i -H "Authorization: Bearer $ADMIN" "$BASE/api/safe/admin/summary"
```
- **Natija:**
  - 1-so‘rov: `200 OK` — **BFLA DALILI!** Oddiy talaba `ali` tokeni orqali maxfiy `marker: "A8-ADMIN"` va umumiy buyurtmalar sonini ko‘rdi.
  - 2-so‘rov: `403 Forbidden` — `admin_safe()` funksiyasi `user['role'] != 'admin'` ekanini tekshirib, rad etdi.
  - 3-so‘rov: `200 OK` — Administrator to‘liq ma'lumotni oldi.

#### B) Integratsiya uchun API Kaliti sinovi:
```bash
# 1. API kalitsiz so'rov
curl -i "$BASE/api/integration/ping"

# 2. To'g'ri X-API-Key sarlavhasi bilan so'rov
curl -i -H "X-API-Key: $API_KEY" "$BASE/api/integration/ping"

# 3. Foydalanuvchi JWT tokeni bilan integratsiya manziliga so'rov
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/integration/ping"

# 4. API kalitini Bearer sifatida /api/me manziliga yuborish
curl -i -H "Authorization: Bearer $API_KEY" "$BASE/api/me"
```
- **Natija:**
  - 1-so‘rov: `401 Unauthorized` va `WWW-Authenticate: ApiKey`. Kalit yo‘qligi sabab rad etildi.
  - 2-so‘rov: `200 OK` — `{"client":"lab-integration","status":"ok"}`. Tizim mijozi muvaffaqiyatli tanildi.
  - 3-so‘rov: `401 Unauthorized`. Foydalanuvchi tokeni tizimlararo integratsiya kaliti o‘rniga o‘tmaydi!
  - 4-so‘rov: `401 Unauthorized`. API kaliti foydalanuvchi shaxsini ifodalovchi JWT token o‘rniga o‘tmaydi!

> **📸 DALIL D4 (Skrinshot):**
> BFLA zaifligi (ALI uchun 200 vs 403) va API kalitining 4 ta holati ko‘ringan skrinshotni `images/4_d4_bfla_apikey.png` nomi bilan saqlang.

---

### 4.7. 7-qadam: Rate Limiting sinovi va zaifliklarni kodda tuzatish (Dalil D5)

#### A) Dastlabki Rate Limiting sinovi (Bash sikli orqali):
```bash
for mode in weak safe; do
    echo "Rejim: $mode"
    for i in 1 2 3 4 5 6; do
        curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $ALI" "$BASE/api/$mode/catalog"
    done
done
```
- **CLI bayroqlari tahlili:**
  - `-s` (silent) — Progres-barni ko‘rsatmaydi.
  - `-o /dev/null` — Serverning JSON javob tanasini ekranga chiqarmaydi, yutib yuboradi.
  - `-w "%{http_code}\n"` — Faqat HTTP javob kodini (masalan, 200 yoki 429) yangi qatordan chiqaradi.
- **Kutiladigan natija:**
  - `weak` rejimida: 6 ta ketma-ket `200` (Cheklov yo‘q).
  - `safe` rejimida: 5 ta `200`, 6-so‘rovda esa `429` (Limit ishladi!).

Darhol `curl -i` bilan tekshirib ko‘ring:
```bash
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/safe/catalog"
```
- Javob: `HTTP/1.1 429 Too Many Requests` va `Retry-After: <soniya>` sarlavhasi keladi.

Ayni shu paytda boshqa foydalanuvchi (`VALI`) uchun so‘rov yuboring:
```bash
curl -i -H "Authorization: Bearer $VALI" "$BASE/api/safe/catalog"
```
- Javob: `HTTP/1.1 200 OK`! Chunki kvota umumiy IP bo‘yicha emas, aynan autentifikatsiyadan o‘tgan subyekt (`sub`) bo‘yicha alohida yuritiladi.

`Retry-After`da ko‘rsatilgan soniya o‘tgach, `ALI` bilan qayta so‘rov yuborsangiz yana `200 OK` qaytadi.

---

#### B) `app.py` ichidagi 3 ta zaif funksiyani tuzatish:

1. **1-terminalda:** `Ctrl+C` bosib serverni to‘xtating.
2. **2-terminalda:** `app.py` faylini tahrirlang:
   ```bash
   nano app.py
   ```
3. Fayl ichidagi quyidagi 3 ta funksiya tanasini toping va o‘zgartiring:

**Oldingi holat (Zaif):**
```python
def order_weak(user, order):
    return order

def admin_weak(user):
    return None

def limit_weak(sub):
    return None
```

**Yangi holat (Tuzatilgan):**
```python
def order_weak(user, order):
    return order_safe(user, order)

def admin_weak(user):
    return admin_safe(user)

def limit_weak(sub):
    return limit_safe(sub)
```
Faylni saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`).

4. Sintaksisni tekshiring va serverni qayta ishga tushiring:
   ```bash
   python -m py_compile app.py
   python app.py
   ```

---

#### C) Tuzatilgan `/weak` endpointlarini qayta sinash:

2-terminalda quyidagi buyruqlarni bajaring:
```bash
# 1. Endi /weak/orders/202 ALI uchun 403 berishi kerak!
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/orders/202"

# 2. Endi /weak/admin/summary ALI uchun 403 berishi kerak!
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/admin/summary"

# 3. ALI o'z buyurtmasiga qonuniy 200 olishi kerak
curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/orders/101"

# 4. ADMIN administrator summaryga 200 olishi kerak
curl -i -H "Authorization: Bearer $ADMIN" "$BASE/api/weak/admin/summary"

# 5. /weak/catalog endi 6-so'rovda 429 berishi kerak
for i in 1 2 3 4 5 6; do
    curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $ALI" "$BASE/api/weak/catalog"
done
```
- **Kutiladigan natija:**
  - 1-so‘rov: `403 Forbidden` (BOLA bartaraf etildi!).
  - 2-so‘rov: `403 Forbidden` (BFLA bartaraf etildi!).
  - 3-so‘rov: `200 OK` (Qonuniy kirish saqlandi).
  - 4-so‘rov: `200 OK` (Admin huquqi saqlandi).
  - 5-so‘rov (sikl): 5 ta `200` va 1 ta `429` (Rate limiting `/weak`da ham ishladi!).

> **📸 DALIL D5 (Skrinshot):**
> Tuzatishdan keyin `/weak` endpointlarida `ALI` uchun 403 qaytgani, qonuniy 200lar va 6-so‘rovda 429 chiqqani aks etgan skrinshotni `images/5_d5_tuzatish.png` nomi bilan saqlang.

---

### 4.8. 8-qadam: Qo‘shimcha topshiriqlar tahlili

Metodika talablariga ko‘ra hisobotda quyidagi uchta qo‘shimcha mavzu bo‘yicha professional tahlil berilishi shart:

#### 1. GraphQL so‘rovlarida ruxsatni tekshirish rejasi:
Quyidagi so‘rov berilgan deb faraz qilaylik:
```graphql
query {
  first: order(id: 101) { id item }
  second: order(id: 202) { id item }
}
```
- **Ruxsat tekshiruvi:** GraphQL'da barcha so‘rovlar bitta HTTP POST `/graphql` endpointiga keladi va HTTP darajasida deyarli har doim `200 OK` qaytadi. Shuning uchun HTTP statusiga qarab huquqni baholab bo‘lmaydi!
- Ruxsat nazorati har bir maydonning **resolver funksiyasi** ichida amalga oshiriladi:
  ```python
  def resolve_order(parent, info, id):
      user = info.context['user'] # Autentifikatsiyadan olingan user
      order = get_order_by_id(id)
      if order['owner'] != user['sub'] and user['role'] != 'admin':
          raise GraphQLError("Forbidden: Sizda bu buyurtmaga ruxsat yo'q")
      return order
  ```
- Natijada mijozga javob quyidagicha qisman muvaffaqiyat bilan qaytadi:
  - `data: {"first": {"id": 101, "item": "Daftar"}, "second": null}`
  - `errors: [{"message": "Forbidden...", "path": ["second"]}]`
- **Resurs nazorati:** Mijoz bitta so‘rov ichida yuzlab aliaslar yozishi mumkin. Buning oldini olish uchun **Query Cost Analysis** (har bir maydonga og‘irlik berish va umumiy balni cheklash) hamda **Depth Limiting** o‘rnatiladi.

#### 2. Multi-worker arxitekturasida Rate Limiting muammosi va Yechim:
- **Muammo:** Hozirgi `app.py` kodidagi `BUCKETS = defaultdict(deque)` xotiradagi o‘zgaruvchidir. Agar Flask ilovasi Gunicorn yoki uWSGI yordamida 4 ta mustaqil worker jarayonida ishga tushirilsa, har bir worker o‘zining alohida xotirasiga ega bo‘ladi. Natijada mijoz 5 ta emas, 20 tagacha so‘rov yuborishi mumkin (chunki so‘rovlar turli workerlarga tushadi).
- **Yechim:** Workerlar o‘rtasida taqsimlangan markaziy kesh — **Redis** ishlatiladi.
  - Redis ichida har bir foydalanuvchi uchun kalit: `rate:user:{sub}`.
  - Redis'ning `INCR` (qiymatni 1 ga oshirish) va `EXPIRE` (yashash vaqtini belgilash) atomar buyruqlari yoki Lua skripti orqali poyga holatisiz (race-condition) aniq 10 soniyada 5 ta so‘rov chegarasi barcha workerlar uchun yagona qilib ta'minlanadi.

#### 3. Qo‘shimcha topshiriq: Xavfsiz ma'lumotlarni tiklash (Disaster Recovery & Backup)
API xizmatlari va ma'lumotlar bazalarida nosozlik yuz berganda xizmatni xavfsiz tiklash talablari:
1. **Zaxiralash (Backup) shifrlanishi:** Ma'lumotlar bazasi va kalitlar zaxirasi saqlash omborida (GCS, AWS S3 yoki lokal) AES-256 bilan shifrlangan bo‘lishi lozim.
2. **Kalitlar boshqaruvi (KMS):** Zaxira nusxalarini shifrlash kalitlari ma'lumotlar bilan bir joyda saqlanmasligi, HashiCorp Vault yoki Cloud KMS orqali boshqarilishi kerak.
3. **Tiklash jarayonini izolyatsiyalash:** Ma'lumotlar tiklanayotganda avval izolyatsiyalangan test (staging) muhitida tekshiriladi, tokenlar va parollar tiklanish jarayonida majburiy rotatsiya qilinadi.

---

## 5. DALILLAR (SKRINSHOTLAR) TIZIMI VA HISOBOT TALABLARI

### 5.1. Skrinshotlarni nomlash va `images/` papkasiga saqlash tartibi
Amaliy ishni bajarish jarayonida barcha skrinshotlarni aniq tartibda quyidagi nomlar bilan `images/` papkasiga joylang:

1. `images/1_d1_muhit.png` — **Dalil D1:** VM muhiti, Python va Flask/PyJWT versiyalari, server ishga tushgani va `ali` uchun `/api/me` so‘rovining 200 OK javobi.
2. `images/2_d2_jwt.png` — **Dalil D2:** 7 xil token bilan `/api/me` ga yuborilgan so‘rovlar va ularning status kodlari (401 va 200).
3. `images/3_d3_bola.png` — **Dalil D3:** `ali` tokeni bilan zaif endpointda `owner=vali` (202-buyurtma) olingani va xavfsiz endpointda `403 Forbidden` qaytgani.
4. `images/4_d4_bfla_apikey.png` — **Dalil D4:** `ali` uchun zaif admin summary 200 qaytgani va xavfsizda 403 bo‘lgani; API kaliti bilan 4 ta sinov natijalari.
5. `images/5_d5_tuzatish.png` — **Dalil D5:** Rate limiting sinovi (200 x 5, 429), `Retry-After`, `VALI` uchun 200; hamda `app.py` tuzatilgandan so‘ng `/weak` endpointlarining 403 va 429 qaytargani.

---

### 5.2. D6 — Yakuniy natijalar taqqoslash jadvali

Ushbu jadval hisobotning eng muhim xulosa qismi bo‘lib, olingan amaliy natijalarni jamlaydi:

| Sinov / So‘rov holati | Oldin (`/weak`) | Keyin (Tuzatilgan `/weak`) | Amaldagi dalil (Rasm) | Texnik izoh |
| :--- | :--- | :--- | :--- | :--- |
| **ALI → `/api/me`** | `200 OK` | `200 OK` | `images/1_d1_muhit.png` | Autentifikatsiya to‘g‘ri, claimlar mos |
| **JWT: TAMPERED, EXPIRED** | `401; 401` | `401; 401` | `images/2_d2_jwt.png` | Imzo buzilgan va muddati o‘tgan |
| **JWT: aud/iss xato; exp yo‘q**| `401; 401; 401` | `401; 401; 401` | `images/2_d2_jwt.png` | Majburiy claimlar talabiga mos emas |
| **ALI → `orders/101`** | `200 OK` | `200 OK` | `images/3_d3_bola.png` | O‘zining qonuniy buyurtmasi |
| **ALI → `orders/202`** | `200 OK (owner=vali)`| `403 Forbidden` | `images/3_d3_bola.png` | BOLA bartaraf etildi |
| **VALI → `orders/202`** | `200 OK` | `200 OK` | `images/3_d3_bola.png` | O‘zining qonuniy buyurtmasi |
| **ALI → `admin/summary`** | `200 OK (A8-ADMIN)` | `403 Forbidden` | `images/4_d4_bfla_apikey.png` | BFLA bartaraf etildi |
| **ADMIN → `admin/summary`** | `200 OK` | `200 OK` | `images/4_d4_bfla_apikey.png` | Administrator huquqi tasdiqlandi |
| **ALI → `catalog` (6 so‘rov)**| `200 × 6` | `200 × 5; 429` | `images/5_d5_tuzatish.png` | Rate limiting cheklovi ishladi |
| **VALI → `catalog` (1 so‘rov)**| `200 OK` | `200 OK` | `images/5_d5_tuzatish.png` | Har bir foydalanuvchi kvotasi alohida |
| **Retry-After kutib ALI** | `200 OK` | `200 OK` | `images/5_d5_tuzatish.png` | Oyna yangilanishidan so‘ng xizmat tiklandi |

---

### 5.3. Hisobotda nimalar bo‘lishi va nimalar kiritilmasligi kerak
- **Kiritilishi kerak:**
  1. Titul varag‘i: Fan nomi, 5-semestr, A8-mavzu, 1-variant, Talaba F.I.Sh., guruhi, sana.
  2. Ishchi muhit parametrlari (Ubuntu versiyasi, Python 3.12, Flask 3.1.3, PyJWT 2.13.0).
  3. D1–D5 skrinshotlari va har biriga 1–2 gapdan tushuntirish.
  4. Uchta zaif funksiyaning oldingi va keyingi kodlari.
  5. D6 yakuniy jadvali va 5–7 gapdan iborat xulosa.
  6. Nazorat savollariga to‘liq javoblar.
- **KIRITILMASLIGI KERAK (Qat'iy xavfsizlik talabi):**
  - `jwt.key` va `api.key` fayllarining to‘liq maxfiy kalit qiymatlari.
  - `tokens.env` ichidagi to‘liq tokenlar.
  - Skrinshotlarda kalitlar va to‘liq tokenlar yashirilgan (kesilgan) bo‘lishi shart.

---

## 6. NAZORAT SAVOLLARI VA ULARNING TO‘LIQ ILMIY JAVOBLARI

### 20-savol: Nega JWT imzosi to‘g‘riligi 202-buyurtmaga ruxsat borligini anglatmaydi?
**Javob:**
Chunki JWT imzosi faqat **Autentifikatsiyani** (token aynan server tomonidan berilgani va yo‘lda o‘zgartirilmaganini) tasdiqlaydi, lekin u **Avtorizatsiyani** (ushbu foydalanuvchining aynan 202-IDli resurs ustidan egalik huquqini) anglatmaydi. `ali` to‘g‘ri imzolangan haqiqiy tokenga ega bo‘lsa ham, 202-buyurtmaning egasi `vali` hisoblanadi. Shuning uchun server biznes-mantiq qatlamida obyekt egasi (`order['owner']`) bilan tokendagi subyektni (`user['sub']`) solishtirishi shart.

### 21-savol: `exp`ni tekshirish va uning mavjudligini talab qilish qanday farqlanadi?
**Javob:**
Oddiy tekshirishda, agar tokenda `exp` claimi mavjud bo‘lsa, kutubxona uning muddati o‘tmaganini tekshiradi. Ammo tokenda `exp` maydoni umuman bo‘lmasa, oddiy tekshiruv xatolik bermaydi va tokenni cheksiz amal qiluvchi deb qabul qiladi. `options={'require': ['exp']}` sozlamasi esa tokenda `exp` maydonining mavjud bo‘lishini majburiy talab qiladi va `exp` maydoni yo‘q har qanday tokenni darhol rad etadi (`MissingRequiredClaimError`).

### 22-savol: BOLA va BFLA uchun bu laboratoriyadagi qaysi ikkita so‘rov dalil bo‘ldi?
**Javob:**
1. **BOLA dalili:** `ali` o‘z tokeni bilan boshqa talabaning buyurtmasini olgan so‘rov:
   `curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/orders/202"` (Natija `200 OK` va `owner=vali` qaytgani).
2. **BFLA dalili:** Oddiy talaba (`ali`) administrator funksiyasini chaqirgan so‘rov:
   `curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/admin/summary"` (Natija `200 OK` va `marker=A8-ADMIN` qaytgani).

### 23-savol: Nega API kalitini Bearer JWT o‘rniga qo‘yib bo‘lmaydi?
**Javob:**
Chunki ularning vazifasi va semantikasi tubdan farq qiladi:
- **API Kaliti:** Muayyan xizmat yoki dasturiy integratsiyani (`lab-integration`) aniqlaydi. Unda foydalanuvchi identifikatori (`sub`), amal qilish muddati (`exp`) yoki dinamik claimlar mavjud bo‘lmaydi.
- **Bearer JWT:** Tizimga kirgan aniq foydalanuvchi shaxsini (`sub=ali`, `role=student`) va uning sessiyasini ifodalaydi. API kalitini JWT o‘rniga qo‘yish foydalanuvchi kontekstini yo‘qotadi va barcha so‘rovlar bitta anonim xizmat nomidan bajarilishiga olib keladi.

### 24-savol: 429dan keyin xizmat qayta ishlashi va VALI kvotasi nega tekshiriladi?
**Javob:**
- **Qayta ishlashni tekshirish:** `Retry-After` vaqti o‘tgach tizim qonuniy mijozga xizmat ko‘rsatishni davom ettirishini (server doimiy blokirovkaga tushib qolmaganini) tasdiqlash uchun kerak.
- **VALI kvotasini tekshirish:** Cheklov butun API server yoki umumiy IP-manzilga emas, balki aynan qonunbuzar subyekt (`ali`) bo‘yicha individual qo‘llanilganini va boshqa begunoh foydalanuvchilar (`vali`) bundan aziyat chekmayotganini isbotlash uchun tekshiriladi.

### 25-savol: GraphQL aliaslari va bir nechta worker holatida qaysi qo‘shimcha nazoratlar kerak?
**Javob:**
1. **GraphQL aliaslari uchun:** Yagona HTTP so‘rovi ichida ko‘plab aliaslar orqali resurslarni suiiste'mol qilishning oldini olish uchun so‘rov chuqurligi chegarasi (**Depth Limiting**), so‘rov murakkabligi tahlili (**Query Cost Analysis**) va har bir resolver darajasida obyektga egalik huquqini tekshirish zarur.
2. **Bir nechta worker uchun:** Xotiradagi lokal o‘zgaruvchilar o‘rniga barcha workerlar uchun yagona bo‘lgan markazlashtirilgan kesh (**Redis**) va atomar operatsiyalar (`INCR` + `EXPIRE` yoki Lua skripti) orqali taqsimlangan Rate Limiting joriy etilishi kerak.

---

## 7. BAHOLASH MEZONLARI (10 BALLIK TIZIM)

| Mezon | Ball | Bajarilishi lozim bo‘lgan shartlar |
| :--- | :---: | :--- |
| **Muhit, ruxsat siyosati va D1** | **1 ball** | Virtual muhit to‘g‘ri sozlangani, paketlar o‘rnatilgani, D1 skrinshoti va 8008 portdagi javob. |
| **JWT: 7 holat, imzo va claim xatosi farqi** | **2 ball** | 7 ta token bilan so‘rov yuborilgani, statuslar tahlili, D2 skrinshoti va TAMPERED/EXPIRED farqi izohlanganligi. |
| **BOLA: boshqa obyekt rad etilishi, egasi kira olishi** | **2 ball** | Zaif endpointda 202-buyurtma olingani, xavfsizda 403 bo‘lgani, o‘z egasi va admin kira olgani, D3 skrinshoti. |
| **BFLA va API kaliti: rol hamda credential farqi** | **2 ball** | Student va admin uchun natijalar, API kaliti bo‘yicha 4 ta holatning to‘liq tahlili, D4 skrinshoti. |
| **Limit, Retry-After va 3 ta tuzatishdan keyingi sinov** | **2 ball** | 5 ta 200 va 1 ta 429 olingani, `Retry-After`, VALI kvotasi, `app.py`dagi 3 ta funksiyaning tuzatilgani va D5 skrinshoti. |
| **Hisobot, dalillar va nazorat savollariga javob** | **1 ball** | D6 jadvali to‘liq to‘ldirilgani, 6 ta nazorat savoliga mukammal javob, toza formatdagi hisobot. |
| **JAMI** | **10 ball** | **Maksimal natija** |

---

## 8. FOYDALANILGAN RASMIY MANBALAR

1. **[OWASP API Security Top 10 (2023)]:**
   - API1:2023 — Broken Object Level Authorization (BOLA): https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
   - API4:2023 — Unrestricted Resource Consumption: https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
   - API5:2023 — Broken Function Level Authorization (BFLA): https://owasp.org/API-Security/editions/2023/en/0xa5-broken-function-level-authorization/
2. **[RFC 7519]:** JSON Web Token (JWT) spetsifikatsiyasi: https://datatracker.ietf.org/doc/html/rfc7519
3. **[PyJWT Documentation]:** API Reference (decode, algorithms, require options): https://pyjwt.readthedocs.io/
4. **[OWASP Cheat Sheet Series]:**
   - REST Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
   - GraphQL Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html
5. **[OpenID Connect Core 1.0]:** Authentication and Token Specifications: https://openid.net/specs/openid-connect-core-1_0.html

---

## 9. ILOVALAR: TO‘LIQ DASTURIY KODLAR

### 9.1. 1-ilova: `app.py` (To‘liq birlashtirilgan Flask server kodi)
Faylni `~/a8-lab/app.py` nomida saqlang:

```python
import hmac
import math
import time
from collections import defaultdict, deque
from pathlib import Path
from threading import Lock
import jwt
from flask import Flask, abort, jsonify, request
from werkzeug.exceptions import HTTPException

ROOT = Path(__file__).resolve().parent
KEY = (ROOT / 'jwt.key').read_text().strip()
API_KEY = (ROOT / 'api.key').read_text().strip()
ISSUER, AUDIENCE = 'a8-issuer', 'a8-api'

# Foydalanuvchilar va ularning rollari
USERS = {'ali': 'student', 'vali': 'student', 'admin': 'admin'}

# O'quv buyurtmalari bazasi
ORDERS = {
    101: {'id': 101, 'owner': 'ali', 'item': 'Daftar'},
    202: {'id': 202, 'owner': 'vali', 'item': 'Kitob'},
}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8192

# Rate limiting parametrlari (10 soniyada 5 ta so'rov)
WINDOW, LIMIT = 10, 5
BUCKETS = defaultdict(deque)
LOCK = Lock()

def identity():
    """JWT tokenni tekshirish va shaxsni aniqlash funksiyasi"""
    parts = request.headers.get('Authorization', '').split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        abort(401)
    try:
        claims = jwt.decode(
            parts[1], KEY, algorithms=['HS256'],
            issuer=ISSUER, audience=AUDIENCE,
            options={'require': ['sub', 'iat', 'exp', 'iss', 'aud']}
        )
    except jwt.InvalidTokenError:
        abort(401)
    
    sub = claims['sub']
    if not isinstance(sub, str) or sub not in USERS:
        abort(401)
    return {'sub': sub, 'role': USERS[sub]}

def valid_mode(mode):
    if mode not in ('weak', 'safe'):
        abort(404)

# ================= ZAIF VA XAVFSIZ FUNKSIYALAR =================

def order_weak(user, order):
    """BOLA zaifligi mavjud bo'lgan funksiya"""
    return order

def order_safe(user, order):
    """BOLA dan himoyalangan funksiya"""
    if order['owner'] != user['sub'] and user['role'] != 'admin':
        abort(403)
    return order

def admin_weak(user):
    """BFLA zaifligi mavjud bo'lgan funksiya"""
    return None

def admin_safe(user):
    """BFLA dan himoyalangan funksiya"""
    if user['role'] != 'admin':
        abort(403)

def limit_weak(sub):
    """Rate limiting mavjud bo'lmagan zaif funksiya"""
    return None

def limit_safe(sub):
    """Sliding window asosidagi xavfsiz rate limiting funksiyasi"""
    now = time.monotonic()
    with LOCK:
        bucket = BUCKETS[sub]
        while bucket and now - bucket[0] >= WINDOW:
            bucket.popleft()
        if len(bucket) >= LIMIT:
            wait = max(1, math.ceil(WINDOW - (now - bucket[0])))
            response = jsonify(error='Too Many Requests')
            response.status_code = 429
            response.headers['Retry-After'] = str(wait)
            return response
        bucket.append(now)
    return None

# ================= ENDPOINTLAR (MARSHRUTLAR) =================

@app.get('/')
def home():
    return jsonify(lab='A8 / 1-variant', port=8008)

@app.get('/api/me')
def me():
    return jsonify(identity())

@app.get('/api/<mode>/orders/<int:order_id>')
def order_route(mode, order_id):
    valid_mode(mode)
    user = identity()
    order = ORDERS.get(order_id)
    if order is None:
        abort(404)
    func = order_weak if mode == 'weak' else order_safe
    return jsonify(func(user, order))

@app.get('/api/<mode>/admin/summary')
def admin_route(mode):
    valid_mode(mode)
    user = identity()
    func = admin_weak if mode == 'weak' else admin_safe
    func(user)
    return jsonify(marker='A8-ADMIN', orders=len(ORDERS))

@app.get('/api/<mode>/catalog')
def catalog(mode):
    valid_mode(mode)
    user = identity()
    func = limit_weak if mode == 'weak' else limit_safe
    response = func(user['sub'])
    if response is not None:
        return response
    return jsonify(items=['Daftar', 'Kitob'])

@app.get('/api/integration/ping')
def integration():
    supplied = request.headers.get('X-API-Key', '')
    if not hmac.compare_digest(supplied.encode(), API_KEY.encode()):
        abort(401)
    return jsonify(client='lab-integration', status='ok')

@app.errorhandler(HTTPException)
def errors(error):
    response = jsonify(error=error.name)
    response.status_code = error.code
    if error.code == 401:
        scheme = 'ApiKey' if request.path.startswith('/api/integration/') else 'Bearer'
        response.headers['WWW-Authenticate'] = scheme
    return response

@app.after_request
def response_headers(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8008, debug=False)
```

---

### 9.2. 2-ilova: `issue.py` (Lokal o‘quv token generatori kodi)
Faylni `~/a8-lab/issue.py` nomida saqlang:

```python
import base64
import json
import secrets
import time
from pathlib import Path
import jwt

root = Path(__file__).resolve().parent

# Maxfiy kalitlar faqat yo'q bo'lsa yaratiladi
for name in ('jwt.key', 'api.key'):
    path = root / name
    if not path.exists():
        path.write_text(secrets.token_hex(32))
        path.chmod(0o600)

key = (root / 'jwt.key').read_text().strip()
now = int(time.time())
base = dict(iss='a8-issuer', aud='a8-api', iat=now, exp=now + 7200)
tokens = {}

# Qonuniy foydalanuvchilar tokenlari (2 soat)
for name in ('ali', 'vali', 'admin'):
    tokens[name.upper()] = jwt.encode(
        dict(base, sub=name), key, algorithm='HS256'
    )

# Maxsus xato tokenlar (Sinovlar uchun)
for label, changes in (
    ('EXPIRED', dict(iat=now - 120, exp=now - 60)),
    ('WRONG_AUD', dict(aud='other-api')),
    ('WRONG_ISS', dict(iss='other-issuer')),
):
    claims = dict(base, sub='ali')
    claims.update(changes)
    tokens[label] = jwt.encode(claims, key, algorithm='HS256')

# exp maydoni bo'lmagan token
missing = dict(base, sub='ali')
del missing['exp']
tokens['NO_EXP'] = jwt.encode(missing, key, algorithm='HS256')

# Qalbakilashtirilgan token (TAMPERED)
head, payload, sig = tokens['ALI'].split('.')
forged = json.dumps(dict(base, sub='admin')).encode()
encoded = base64.urlsafe_b64encode(forged).rstrip(b'=').decode()
tokens['TAMPERED'] = '.'.join((head, encoded, sig))

# API kaliti
tokens['API_KEY'] = (root / 'api.key').read_text().strip()

# tokens.env fayliga saqlash
target = root / 'tokens.env'
target.write_text(''.join(f"{k}='{v}'\n" for k, v in tokens.items()))
target.chmod(0o600)

print('A8 tokens.env tayyor; amal qilish muddati: 2 soat')
```
