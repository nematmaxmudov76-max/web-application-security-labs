# A12: Veb ilovalar xavfsizligini kompleks tahlil qilish va himoyalash usullari
## 1-VARIANT: “Talaba qaydlari” (Student Notes) ilovasining yakuniy xavfsizlik auditi

---

## MUNDARIJA
1. [Mavzuning maqsadi va konseptual mohiyati](#1-mavzuning-maqsadi-va-konseptual-mohiyati)
2. [Maxsus ish muhiti: Shaxsiy Wi-Fi va Ubuntu Host + VMware arxitekturasi](#2-maxsus-ish-muhiti-shaxsiy-wi-fi-va-ubuntu-host--vmware-arxitekturasi)
3. [Mavzular bo'yicha to'liq nazariy va amaliy qo'llanma](#3-mavzular-boyicha-toliq-nazariy-va-amaliy-qollanma)
   - 3.1. Audit doirasi (Scope), aktivlar va ishonch chegaralari (Trust Boundaries) — Dalil D1
   - 3.2. Muhitni tayyorlash va xizmatni ishga tushirish — Dalil D2
   - 3.3. Obyekt darajasidagi kirish nazorati buzilishi (IDOR / BOLA) — Dalil D3 / Topilma F01
   - 3.4. Qidiruvdagi SQL inyeksiyasi (SQL Injection) — Dalil D4 / Topilma F02
   - 3.5. Aks etuvchi XSS (Reflected XSS) va xavfsizlik sarlavhalari — Dalil D5 / Topilma F03–F04
   - 3.6. Himoyani qo'llash va avtomatlashtirilgan regressiya sinovlari — Dalil D6
   - 3.7. Xavflarni baholash (Risk Matrix) va OWASP Top 10:2025 xaritasi — Dalil D7
   - 3.8. Xavfsiz dasturiy ta'minot yaratish (SSDLC / NIST SSDF) va reliz qarori — Dalil D8
   - 3.9. Nazorat savollari va ularning chuqur tahliliy javoblari
4. [Mashqni ketma-ket bajarish bo'yicha amaliy yo'riqnoma](#4-mashqni-ketma-ket-bajarish-boyicha-amaliy-yoriqnoma)
5. [CLI buyruqlar ensiklopediyasi (Har bir buyruq va flag tahlili)](#5-cli-buyruqlar-ensiklopediyasi-har-bir-buyruq-va-flag-tahlili)
6. [Ilovaning to'liq manba kodlari (app.py va audit.py)](#6-ilovaning-toliq-manba-kodlari-apppy-va-auditpy)
7. [Foydalanilgan rasmiy va me'yoriy manbalar](#7-foydalanilgan-rasmiy-va-meoriy-manbalar)

---

## 1. MAVZUNING MAQSADI VA KONSEPTUAL MOHIYATI

### 1.1. Mashg'ulot maqsadi
Ushbu mashg'ulotning asosiy maqsadi — avvalgi amaliy darslarda alohida-alohida o'rganilgan veb-zaifliklarni (avtorizatsiyaning buzilishi, SQL inyeksiya, XSS, xavfsizlik sarlavhalarining yetishmasligi) **yagona, kompleks xavfsizlik auditi (comprehensive security audit)** jarayoniga birlashtirishdan iborat.

Audit jarayoni quyidagi qat'iy tizimli zanjir asosida quriladi:
```
[Doirani belgilash (Scope)] 
          ↓
[Zaiflikni qayta hosil qilish (Reproduce Vulnerability)] 
          ↓
[Ildiz sababni manba koddan aniqlash (Root Cause in Code)] 
          ↓
[Xavfni baholash va ustuvorlashtirish (Risk Scoring)] 
          ↓
[Himoya mexanizmini joriy etish (Remediation)] 
          ↓
[Qayta sinov va regressiya tekshiruvi (Retest & Regression)] 
          ↓
[Dalillarni saqlash va Reliz qarori (Release Decision & Integrity)]
```

### 1.2. Kutiladigan natijalar
Mazkur laboratoriya ishini muvaffaqiyatli yakunlagan talaba:
1. **Audit doirasi va ishonch chegaralarini** aniq ajrata oladi;
2. **IDOR (BOLA)**, **SQL inyeksiya** va **Reflected XSS** zaifliklarining yuzaga kelish sabablarini va ularning o'zaro farqlarini chuqur tushunadi;
3. HTTP xavfsizlik sarlavhalari (`Content-Security-Policy`, `X-Content-Type-Options`) himoyaning asosiy vositasi emas, balki chuqur himoyalanish (Defense-in-Depth) qatlami ekanini anglaydi;
4. **"Topildi — Sababi topildi — Tuzatildi — Qayta tekshirildi"** metodologiyasiga muvofiq, o'zgarishlar qonuniy (biznes-mantiq) funksionallikni buzmaganini (regressiya yo'qligini) isbotlaydi;
5. NIST SSDF va OWASP standartlariga tayangan holda dasturni ishlab chiqarishga (production) chiqarish yoki chiqarmaslik bo'yicha asosli texnik xulosa beradi.

---

## 2. MAXSUS ISH MUHITI: SHAXSIY WI-FI VA UBUNTU HOST + VMWARE ARXITEKTURASI

Sizning ish muhitingiz bo'yicha qo'yilgan talablar va uning texnik tahlili:

### 2.1. Shaxsiy lokal Wi-Fi (Uy/Shaxsiy tarmoq) masalasi
* **Xavotirga o'rin yo'q:** Laboratoriya ishi metodik qo'llanmasiga ko'ra, audit obyekti bo'lgan xizmat faqat **Loopback (127.0.0.1:8012)** manzilida tinglaydi (`bind`).
* Ilova ommaviy tarmoqqa yoki Wi-Fi interfeysiga ochilmaydi.
* Wi-Fi tarmog'ingiz faqat dastlabki bosqichda kerakli paketlarni o'rnatish (`sudo apt update && sudo apt install ...`) uchun internet ta'minlaydi.
* Barcha sinovlar, zaifliklarni ekspluatatsiya qilish va avtomatlashtirilgan audit VM ichidagi lokal manzil (`127.0.0.1`) doirasida amalga oshiriladi. Shu sababli universitet tarmog'i bo'lmagani tajribaga hech qanday salbiy ta'sir ko'rsatmaydi va uyingizdagi Wi-Fi xavfsizligiga xatar tug'dirmaydi.

### 2.2. Operatsion tizim va virtualizatsiya arxitekturasi
Sizda asosiy operatsion tizim (Host OS) — **Ubuntu**, virtualizatsiya vositasi — **VMware Workstation/Player (Linux versiyasi)**.

Ushbu arxitektura bo'yicha mashqni bajarishning 3 ta qulay stsenariysi mavjud:

```
Variant A (Tavsiya etiladi - Standart VM):
Ubuntu (Host) ──► VMware ──► Ubuntu Desktop VM (24.04 LTS)
                               ├── Terminal 1: python3 app.py (127.0.0.1:8012)
                               ├── Terminal 2: curl, audit.py, sha256sum
                               └── GUI: Firefox brauzeri (XSS ko'rish uchun)

Variant B (Agar VM Ubuntu Server bo'lsa - GUI yo'q):
Ubuntu (Host) ──► VMware ──► Ubuntu Server VM (GUI-siz)
                               ├── Terminal 1 & 2: app.py va audit.py
                               └── XSS tekshirish uchun:
                                   SSH Port-forwarding orqali Host (Ubuntu)dagi 
                                   yoki VMware ichidagi Windows 11 Desktop brauzeridan ochish:
                                   ssh -L 8012:127.0.0.1:8012 user@<VM_IP>

Variant C (To'g'ridan-to'g'ri Ubuntu Hostning o'zida bajarish):
Ubuntu (Host) ──► To'g'ridan-to'g'ri terminal va Firefox (VM shart bo'lmagan holatda)
```

> [!IMPORTANT]
> **Windows 11 VM dan qachon foydalaniladi?**
> Agar siz VMware ichida Ubuntu Server (GUI-siz) o'rnatgan bo'lsangiz va terminalda brauzer bo'lmasa, XSS hujumida sahifa sarlavhasi (Document Title) o'zgarishini vizual ko'rish uchun VMware ichidagi tayyor **Windows 11 Desktop VM** yoki **Ubuntu Host** brauzeridan foydalanishingiz mumkin.
> Buning uchun Ubuntu Server VM-ga SSH orqali portni yo'naltirasiz (`ssh -L 8012:127.0.0.1:8012 <server_user>@<server_ip>`), so'ngra Windows 11 yoki Ubuntu Host brauzerida `http://127.0.0.1:8012/preview?...` manzilini ochasiz.

---

## 3. MAVZULAR BO'YICHA TO'LIQ NAZARIY VA AMALIY QO'LLANMA

### 3.1. Audit doirasi, aktivlar va ishonch chegaralari (Dalil D1)
Audit o'tkazishdan oldin tizimning arxitekturasi va ruxsat berilgan chegaralar qat'iy belgilanadi.

#### Obyektlar va yo'llar xaritasi
| Endpoint (Yo'l) | Kirish sharti (Auth) | Kutiladigan qonuniy xatti-harakat |
| :--- | :--- | :--- |
| `/health` | Ochiq (Anonim) | HTTP 200; Tizim holati va faol rejim (`secure: false/true`) |
| `/api/note?id=…` | Demo token (`X-Lab-Token`) | HTTP 200; Faqat token egasiga tegishli 1 dona qayd |
| `/api/search?q=…` | Demo token (`X-Lab-Token`) | HTTP 200; Faqat token egasiga tegishli qaydlar ro'yxati |
| `/preview?text=…` | Ochiq (Anonim) | HTTP 200; Kiritilgan matn xavfsiz HTML ko'rinishida chiqariladi |

#### Tizimdagi boshlang'ich ma'lumotlar (In-memory SQLite)
| ID | Egasi (Owner) | Mazmuni (Title) | Maxfiylik talabi |
| :---: | :---: | :--- | :--- |
| **1** | `alice` | Alice plan | Faqat Alice o'qiy oladi |
| **2** | `bob` | Bob private | Faqat Bob o'qiy oladi (Maxfiy) |
| **3** | `alice` | Alice report | Faqat Alice o'qiy oladi |

#### Ishonch chegaralari (Trust Boundaries):
1. **1-chegara (Mijoz ↔ Server):** URL parametrlari (`id`, `q`, `text`) va HTTP sarlavhalari (`X-Lab-Token`). Mijozdan kelgan har qanday ma'lumot potentsial xavfli hisoblanadi.
2. **2-chegara (Autentifikatsiya ↔ Ma'lumot egasi):** Server aniqlangan foydalanuvchi (`alice` yoki `bob`) faqat o'ziga tegishli obyektlarga murojaat qilayotganini tekshirishi shart.
3. **3-chegara (Server ↔ Brauzer):** Serverdan qaytgan matn foydalanuvchi brauzerida HTML DOM sifatida talqin qilinadi. Brauzer matn va bajariluvchi skriptni farqlay olishi uchun ma'lumot to'g'ri kodlanishi kerak.

---

### 3.2. Muhitni tayyorlash va xizmatni ishga tushirish (Dalil D2)
* Python 3 ning standart kutubxonasidagi `http.server` moduli orqali minimal veb-server ishga tushiriladi.
* Tashqi `pip` paketlariga (masalan, Flask, Django, Requests) ehtiyoj yo'q. Standart `urllib`, `sqlite3`, `html`, `json` yetarli.
* Ishchi katalog: `~/a12-lab/`.
* Fayl xavfsizligi: `umask 077` buyrug'i orqali yaratiladigan barcha fayllar faqat joriy foydalanuvchi uchun o'qish/yozish huquqiga ega bo'ladi (boshqa foydalanuvchilarga ruxsat berilmaydi).
* Dastlabki nazorat: Xizmat porti (8012) ochiqligi, `/health` endpointi orqali `secure=false` ekani va tokensiz so'rovga `401 Unauthorized` qaytishi tekshiriladi.

---

### 3.3. Obyekt darajasidagi kirish nazorati buzilishi (IDOR / BOLA) — F01
* **OWASP Tasnifi:** A01:2025 — Broken Access Control (yoki API xavfsizligida BOLA).
* **Zaiflik mexanizmi:** Alice tizimga o'zining qonuniy tokeni (`X-Lab-Token: demo-alice`) bilan kiradi. U `id=1` qaydini so'raganda o'z ma'lumotini ko'radi. Agar Alice so'rovda shunchaki `id=2` deb yozsa va server obyekt egasini tekshirmasa, Bobning maxfiy qaydi (`Bob private`) Alicega qaytadi.
* **Kod darajasidagi zaiflik sababi:**
  ```python
  # ZAIF KOD (app.py):
  def get_note(owner, note_id):
      # note_id parametrli berilgan, lekin egasi (owner) tekshirilmaydi!
      return DB.execute('SELECT * FROM notes WHERE id=?', (note_id,)).fetchone()
  ```
* **Ildiz sabab (Root Cause):** Parametrli so'rov SQL inyeksiyani bartaraf etadi, ammo avtorizatsiyani ta'minlamaydi. Obyektning mavjudligi tekshiriladi, ammo unga murojaat qilayotgan subyektning huquqi tekshirilmaydi.
* **Tuzatish (Remediation):**
  ```python
  # HIMOYALANGAN KOD:
  def get_note(owner, note_id):
      return DB.execute('SELECT * FROM notes WHERE id=? AND owner=?', 
                        (note_id, owner)).fetchone()
  ```
  `owner` qiymati foydalanuvchi so'rov parametridan emas, serverdagi sessiya/token xaritasidan olinadi. Agar yozuv topilmasa, begona foydalanuvchiga ham, mavjud bo'lmagan ID ga ham bir xil `404 Not Found` qaytariladi (ma'lumot sizib chiqishini oldini olish uchun).

---

### 3.4. Qidiruvdagi SQL inyeksiyasi (SQL Injection) — F02
* **OWASP Tasnifi:** A05:2025 — Injection.
* **Zaiflik mexanizmi:** Qidiruv endpointi (`/api/search?q=...`) foydalanuvchi kiritgan satrni to'g'ridan-to'g'ri SQL so'roviga satrlar qo'shish (string concatenation) orqali birlashtiradi.
* **Hujum vektori (Payload):**
  ```sql
  ' OR 1=1-- 
  ```
* **Zaif SQL shakllanishi:**
  ```sql
  SELECT * FROM notes WHERE owner='alice' AND title LIKE '%' OR 1=1-- %'
  ```
  Mantiqiy amallar ustuvorligi bo'yicha `AND` amali `OR` amalidan oldin bajariladi:
  ` (owner='alice' AND title LIKE '%')  OR  (1=1) `
  Natijada `1=1` doimo rost (TRUE) bo'lgani uchun, `WHERE` sharti barcha yozuvlar uchun qanoatlantiriladi va Bobning ham ma'lumotlari Alicega qaytadi!
* **Tuzatish (Remediation):**
  Parametrlangan so'rov (Prepared Statement) qo'llash:
  ```python
  # HIMOYALANGAN KOD:
  return DB.execute('SELECT * FROM notes WHERE owner=? AND title LIKE ?', 
                    (owner, '%' + term + '%'))
  ```
  Endi `' OR 1=1-- ` sintaktik buyruq emas, oddiy qidiruv matni sifatida qabul qilinadi va hech qanday ortiqcha ma'lumot chiqmaydi (`notes: []`).

---

### 3.5. Aks etuvchi XSS (Reflected XSS) va xavfsizlik sarlavhalari — F03 va F04
* **OWASP Tasnifi:** F03 — A05:2025 (Injection / XSS), F04 — A02:2025 (Security Misconfiguration).
* **Zaiflik mexanizmi:** `/preview?text=...` manziliga yuborilgan matn hech qanday zararsizlantirishsiz (sanitization/encoding) to'g'ridan-to'g'ri HTML DOM ga qo'shiladi:
  ```html
  <div><script>document.title="A12-XSS"</script></div>
  ```
* **curl vs Brauzer farqi:**
  `curl` utilitasi faqat HTTP javob matnini yuklab oladi, lekin uning ichidagi JavaScript kodini bajarmaydi. Brauzer esa HTML parserga ega bo'lib, `<script>` tegini ko'rganda uni ishga tushiradi va sahifa sarlavhasini (tab nomini) `A12-XSS` ga o'zgartiradi.
* **Tuzatish (Ildiz sababni yo'qotish):**
  HTML kontekstiga mos kodlash (HTML Entity Encoding):
  ```python
  value = html.escape(text, quote=True)
  ```
  Natijada `<` belgisi `&lt;` ga, `>` esa `&gt;` ga aylanadi. Brauzer buni kod emas, oddiy matn deb biladi.
* **Qo'shimcha himoya qatlami (Defense-in-Depth - F04):**
  1. `X-Content-Type-Options: nosniff` — Brauzer MIME turini o'zboshimchalik bilan o'zgartirishini (MIME sniffing) taqiqlaydi.
  2. `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'` — Sahifada har qanday begona yoki inline skriptlar, freymlar va forma amallarini qat'iy bloklaydi.

---

### 3.6. Himoyani qo'llash va avtomatlashtirilgan regressiya sinovlari (Dalil D6)
* `audit.py` skripti 12 ta avtomatlashtirilgan sinovdan iborat (T01 dan T12 gacha).
* **Zaif rejimda (`secure=false`):** 8 / 12 PASS, 4 ta test FAIL (T05, T07, T08, T09). Chiqish kodi (Exit code): `1`.
* **Himoyalangan rejimda (`--secure`):** 12 / 12 PASS, 0 ta test FAIL. Chiqish kodi: `0`.
* **Regressiya nazorati:** T02, T03 va T06 testlari qonuniy foydalanuvchilar (Alice va Bob) ning o'z ma'lumotlarini normal o'qishi va qidirishi himoyadan keyin ham buzilmaganini tasdiqlaydi.

---

### 3.7. Xavflarni baholash (Risk Assessment) va OWASP Top 10:2025 qamrovi (Dalil D7)

#### Sodda xavf matritsasi (Ehtimollik × Ta'sir = Ball)
* **Ehtimollik (E):** 1 — Murakkab shartlar; 2 — Qo'shimcha imkoniyat; 3 — Oddiy mijoz so'rovi yetarli.
* **Ta'sir (T):** 1 — Kichik cheklov; 2 — Bitta foydalanuvchi doirasida; 3 — Ma'lumotlar maxfiyligi/butunligi buzilishi.
* **Daraja:** 1–2: Past, 3–4: O'rta, 6–9: Yuqori.

| ID | Zaiflik nomi | E | T | Ball (E×T) | Ustuvorlik | Asos va real ta'sir |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **F01** | IDOR (Obyektga ruxsatsiz kirish) | 3 | 3 | **9** | **Yuqori** | Alice oddiy ID almashtirish orqali Bobning maxfiy qaydini o'qiy oladi. |
| **F02** | Qidiruvdagi SQL inyeksiya | 3 | 3 | **9** | **Yuqori** | Maxsus belgi kiritib, boshqa foydalanuvchilar ma'lumotlarini to'liq chiqarib olish mumkin. |
| **F03** | Reflected XSS | 3 | 2 | **6** | **Yuqori** | Foydalanuvchini aldab maxsus URL ochtirilsa, uning sessiyasi nomidan skript bajarilishi mumkin. |
| **F04** | Xavfsizlik sarlavhalari yo'qligi | 2 | 1 | **2** | **Past** | Chuqur himoya (Defense-in-Depth) qatlamining yo'qligi. |

#### OWASP Top 10:2025 Qamrov tahlili
* **A01: Broken Access Control** — F01 orqali to'liq tekshirildi va tuzatildi.
* **A02: Security Misconfiguration** — F04 doirasida javob sarlavhalari tekshirildi.
* **A03: Software Supply Chain Failures** — Ushbu laboratoriyada tekshirilmadi.
* **A04: Cryptographic Failures** — Ushbu laboratoriyada tekshirilmadi (HTTPS/TLS qo'llanilmadi).
* **A05: Injection** — F02 (SQLi) va F03 (XSS) orqali tekshirildi va tuzatildi.
* **A06: Insecure Design** — Doira va ruxsat talablari o'rganildi.
* **A07: Authentication Failures** — Tekshirilmadi (demo tokenlar haqiqiy auth emas).
* **A08: Software or Data Integrity Failures** — Manba kod xeshlari orqali tekshirildi.
* **A09: Security Logging & Alerting Failures** — Minimal Request-ID log mosligi tekshirildi.
* **A10: Mishandling of Exceptional Conditions** — Noto'g'ri ID tekshirildi.

---

### 3.8. Xavfsiz dasturiy ta'minot yaratish (SSDLC) va reliz qarori (Dalil D8)

#### NIST SP 800-218 (SSDF v1.1) asosidagi bosqichlar:
1. **Talab va Dizayn:** Boshidanoq "faqat o'z qaydini o'qish" talabi arxitekturaga kiritiladi.
2. **Xavfsiz kod yozish:** Parametrli so'rovlar, qat'iy kirish nazorati, kontekstli kodlash.
3. **Avtomatlashtirilgan sinov (CI/CD):** Har bir commitda `audit.py` kabi regressiya testlarini yurgizish.
4. **Reliz (Chiqarish) qarori:** Barcha kritik va yuqori xavfli topilmalar bartaraf etilmaguncha relizga ruxsat berilmaydi.
5. **Ekspluatatsiya va monitoring:** Server loglarida noan'anaviy xatti-harakatlarni tahlil qilish.

#### Reliz qarori xulosasi (Release Decision):
> **QAROR: ISHLAB CHIQARISHGA (PRODUCTION) CHIQARISH TAQIQLANADI!**
> **Sababi:** Garchi o'quv muhitida F01–F04 muammolari tuzatilib, audit natijasi 12/12 bo'lsa-da:
> 1. `demo-alice` / `demo-bob` tokenlari ochiq matnli o'quv belgilari bo'lib, haqiqiy xavfsiz autentifikatsiya, parollarni xeshlash va sessiya boshqaruvi mavjud emas;
> 2. Aloqa shifrlanmagan (oddiy HTTP, TLS/HTTPS yo'q);
> 3. Python `http.server` moduli ishlab chiqaruvchilar tomonidan faqat test uchun tavsiya etilgan, u yuqori yuklama, DoS hujumlariga bardosh bera olmaydi;
> 4. Ma'lumotlar bazasi faqat xotirada (`:memory:`) vaqtinchalik saqlanadi.

---

### 3.9. Nazorat savollari va ularning chuqur tahliliy javoblari

#### 1-savol: Nega parametrli SELECT mavjud bo'lsa ham IDOR (BOLA) yuz berishi mumkin?
**Javob:** Chunki SQL so'rovini parametrlash faqat **sintaktik xavfsizlikni** ta'minlaydi (ya'ni foydalanuvchi kiritgan qiymat SQL buyrug'iga aylanib ketmasligini kafolatlaydi). Ammo u **avtorizatsiya mantiqini** bilmaydi. Agar SQL so'rovida `WHERE id=?` deb yozilsa, ma'lumotlar bazasi so'ralgan `id` dagi yozuvni to'g'ri qaytarib beradi. Ammo bu yozuv ayni paytda so'rov yuborgan foydalanuvchiga tegishlimi yoki yo'qmi — buni faqat dastur kodidagi avtorizatsiya filtri (`AND owner=?`) hal qilishi kerak. Shuning uchun parametrli so'rov IDOR dan himoya qila olmaydi.

#### 2-savol: SQLi natijasida uchala yozuv chiqishiga qaysi mantiqiy shart sabab bo'ldi?
**Javob:** Mantiqiy operatorlarning ustuvorlik tartibi (Operator Precedence) sabab bo'ldi. SQL tilida `AND` operatori `OR` operatoriga nisbatan yuqoriroq ustuvorlikka ega. Kiritilgan `' OR 1=1-- ` qiymati natijasida so'rov quyidagicha shakllandi:
`WHERE (owner='alice' AND title LIKE '%') OR (1=1)`
Bu yerda `(1=1)` sharti har qanday qatorda doimo ROST (TRUE) natija beradi. `OR` amali bo'lgani uchun butun qatordagi shart rostga aylanadi va `owner='alice'` cheklovi bekor bo'lib, bazadagi barcha yozuvlar (shu jumladan Bobning yozuvi) chiqib keladi.

#### 3-savol: curl orqali topilgan `<script>` bilan brauzerda bajarilgan skript dalili nimasi bilan farq qiladi?
**Javob:** `curl` — bu shunchaki HTTP mijoz. U serverdan kelgan baytlarni qanday bo'lsa shundayligicha qabul qiladi va konsolga chiqaradi. U DOM tuzmaydi va JavaScript dvigateliga ega emas. Shu sababli `curl` orqali faqat server javobida `<script>` tegi borligi (potensial XSS) ko'rinadi, lekin skript real ishlaydimi-yo'qmi isbotlanmaydi. 
Brauzer esa to'liq HTML parser va JS dvigateliga ega. Brauzer sahifani render qilganda skriptni bajaradi va natijada DOM o'zgaradi (masalan, `document.title` `A12-XSS` ga aylanadi). Demak, brauzerdagi dalil — bu zaiflikning amalda muvaffaqiyatli ekspluatatsiya qilinganining yakuniy va inkor etib bo'lmas isbotidir.

#### 4-savol: 12/12 natijasi nega ASVSga to'liq muvofiqlik yoki ishlab chiqarishga tayyorlik degani emas?
**Javob:** Chunki `audit.py` skriptidagi 12 ta test faqat belgilangan kichik o'quv doirasini (IDOR, 1 ta SQLi, 1 ta reflected XSS va 2 ta sarlavha) tekshiradi xolos. OWASP ASVS (Application Security Verification Standard) esa yuzlab qat'iy talablarni o'z ichiga oladi (masalan: parollar siyosati, brute-force himoyasi, ko'p faktorli autentifikatsiya, sessiyalarni xavfsiz boshqarish, kriptografik kalitlar xavfsizligi, CSRF, SSRF, audit jurnallari xavfsizligi, DoS ga chidamlilik va b.). 12/12 natijasi faqat berilgan o'quv laboratoriyasining 4 ta topilmasi to'g'ri tuzatilganini bildiradi, xolos.

---

## 4. MASHQNI BOSQICHMA-BOSQICH BAJARISH BO'YICHA AMALIY YO'RIQNOMA

Ushbu qismda siz barcha amallarni o'z Ubuntu tizimingizda (yoki VMware ichidagi Ubuntu VM da) bosqichma-bosqich bajarasiz.

### 1-QADAM: Ishchi katalogni tayyorlash va paketlarni o'rnatish
1-terminalni oching:
```bash
sudo apt update
sudo apt install -y python3 curl nano firefox
umask 077
mkdir -p ~/a12-lab
cd ~/a12-lab
```

### 2-QADAM: app.py va audit.py fayllarini yaratish
Ushbu hujjatning [6-bo'limida](#6-ilovaning-toliq-manba-kodlari-apppy-va-auditpy) keltirilgan to'liq kodlarni `nano` muharriri orqali saqlang:
```bash
nano app.py
# Kodni qo'yib, Ctrl+O, Enter, Ctrl+X bosing

nano audit.py
# Kodni qo'yib, Ctrl+O, Enter, Ctrl+X bosing
```

Fayllarni kompilyatsiya qilish va dastlabki xeshlarini saqlash:
```bash
python3 -m py_compile app.py audit.py
python3 --version
curl --version
sha256sum app.py audit.py > source.sha256
```

### 3-QADAM: Zaif rejimda serverni ishga tushirish (1-terminal)
```bash
python3 -u app.py > before-server.log 2>&1
```
*(Ushbu terminal server ishlab turgani sababli ochiq qoladi)*.

### 4-QADAM: Boshlang'ich nazorat va Dalil D2 (2-terminal)
Yangi 2-terminal oching:
```bash
cd ~/a12-lab
U=http://127.0.0.1:8012
ss -ltn | grep ":8012"
curl --noproxy "*" -i "$U/health"
curl --noproxy "*" -i "$U/api/note?id=1"
curl --noproxy "*" -i "$U/api/note?id=1" -H "X-Lab-Token: demo-alice"
```

### 5-QADAM: IDOR (BOLA) zaifligini tekshirish — Dalil D3 / F01
Alice nomidan Bobning `id=2` qaydini so'rang:
```bash
curl --noproxy "*" -s -i "$U/api/note?id=2" \
  -H "X-Lab-Token: demo-alice" | tee f01-before.txt
curl --noproxy "*" -i "$U/api/note?id=2" \
  -H "X-Lab-Token: demo-bob"
```
*(Natijada Alice tokeni bilan Bobning maxfiy xati ko'rinadi — bu zaiflik dalili!)*

### 6-QADAM: SQL inyeksiyani tekshirish — Dalil D4 / F02
Qonuniy qidiruv va SQL inyeksiya sinovi:
```bash
curl --noproxy "*" -s -G "$U/api/search" \
  -H "X-Lab-Token: demo-alice" --data-urlencode "q=Alice"

curl --noproxy "*" -s -i -G "$U/api/search" \
  -H "X-Lab-Token: demo-alice" \
  --data-urlencode "q=' OR 1=1-- " | tee f02-before.txt
```
*(Natijada Alice qidiruvida Bobning ham qaydi chiqadi — bu SQL inyeksiya dalili!)*

### 7-QADAM: Reflected XSS va Sarlavhalarni tekshirish — Dalil D5 / F03–F04
```bash
P='<script>document.title="A12-XSS"</script>'
curl --noproxy "*" -s -i -G "$U/preview" \
  --data-urlencode "text=$P" | tee f03-before.txt
```
Brauzerda (Firefox) tekshirish:
Brauzer manzil satriga quyidagi URLni kiriting:
`http://127.0.0.1:8012/preview?text=%3Cscript%3Edocument.title%3D%22A12-XSS%22%3C%2Fscript%3E`
*(Brauzer tab nomi "A12-XSS" ga o'zgarganini ko'ring va skrinshot oling).*

### 8-QADAM: Himoyadan oldingi avtomatlashtirilgan audit
```bash
python3 audit.py > before.txt 2>&1
BEFORE_RC=$?
cat before.txt
echo "Chiqish kodi: $BEFORE_RC"
```
*(Kutilgan natija: SUMMARY 8 / 12, chiqish kodi 1).*

### 9-QADAM: Himoyani yoqish (--secure) va qayta sinov — Dalil D6
1-terminalga o'ting va `Ctrl+C` bosing. So'ngra serverni himoyalangan rejimda qayta ishga tushiring:
```bash
python3 -u app.py --secure > after-server.log 2>&1
```

2-terminalga qaytib, qayta sinovlarni o'tkazing:
```bash
curl --noproxy "*" -s "$U/health"

# Qo'lda qayta tekshiruvlar:
curl --noproxy "*" -s -i "$U/api/note?id=2" \
  -H "X-Lab-Token: demo-alice" | tee f01-after.txt

curl --noproxy "*" -s -i -G "$U/api/search" \
  -H "X-Lab-Token: demo-alice" \
  --data-urlencode "q=' OR 1=1-- " | tee f02-after.txt

curl --noproxy "*" -s -i -G "$U/preview" \
  --data-urlencode "text=$P" | tee f03-after.txt

# Avtomatlashtirilgan qayta audit:
python3 audit.py > after.txt 2>&1
AFTER_RC=$?
cat after.txt
echo "Chiqish kodi: $AFTER_RC"

# Farqlarni solishtirish:
diff -u before.txt after.txt
```
*(Kutilgan natija: SUMMARY 12 / 12, chiqish kodi 0).*

Brauzer sahifasini yangilang (F5) — endi tab nomi "A12 Preview" bo'lib qoladi, skript matn sifatida ko'rinadi!

### 10-QADAM: Jurnallarni bog'lash va Dalillar arxivini muhrlash (Dalil D8)
Server logidan so'rov ID sini topish:
```bash
# f01-after.txt ichidagi X-Request-ID qiymatini oling (masalan, 4a2b...)
grep -F "SIZNING_REQUEST_ID" after-server.log
```

Dalillarni arxivlash va butunlik xeshlarini yaratish:
```bash
CASE_DIR="evidence-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -m 700 "$CASE_DIR"
cp app.py audit.py source.sha256 before.txt after.txt \
   before-server.log after-server.log f0*-*.txt "$CASE_DIR/"
(cd "$CASE_DIR" && sha256sum * > SHA256SUMS)
(cd "$CASE_DIR" && sha256sum -c SHA256SUMS)
chmod 400 "$CASE_DIR"/*
```

---

## 5. CLI BUYRUQLAR ENSIKLOPEDIYASI (HAR BIR BUYRUQ VA FLAG TAHLILI)

Ushbu bo'limda laboratoriyada ishlatilgan har bir buyruq, uning vazifasi va har bir argumentining mohiyati batafsil tushuntirilgan:

### 1. `sudo apt update`
* **Vazifasi:** Ubuntu paketlar ombori (repository) indekslarini yangilaydi.
* `sudo` — superuser (root) vakolati bilan bajarish.
* `apt` — Advanced Package Tool (Ubuntu paket menejeri).
* `update` — `/etc/apt/sources.list` dagi omborlardan eng so'nggi dasturlar ro'yxatini yuklab oladi.

### 2. `sudo apt install -y python3 curl nano firefox`
* **Vazifasi:** Laboratoriya uchun zarur vositalarni o'rnatadi.
* `install` — ko'rsatilgan paketlarni yuklab olib o'rnatish.
* `-y` (`--yes`) — o'rnatish jarayonidagi tasdiqlash savollariga avtomatik "Ha" (Yes) deb javob berish.
* `python3` — Python tili interpretatori.
* `curl` — HTTP so'rovlarini yuborish uchun tarmoq utilitasi.
* `nano` — konsol matn muharriri.
* `firefox` — GUI veb-brauzeri (XSS ni tekshirish uchun).

### 3. `umask 077`
* **Vazifasi:** Yangi yaratiladigan fayl va papkalar uchun birlamchi ruxsat huquqlarini (permissions mask) cheklaydi.
* `077` niqobi yangi fayllardan guruh (group) va boshqa barcha foydalanuvchilar (others) ning barcha ruxsatlarini (o'qish, yozish, bajarish) olib tashlaydi. Faqat joriy foydalanuvchi (`rwx------`) to'liq huquqqa ega bo'ladi. Bu audit fayllarini boshqalardan himoyalaydi.

### 4. `mkdir -p ~/a12-lab`
* **Vazifasi:** Yangi ishchi katalog yaratish.
* `mkdir` — make directory (papka yaratish).
* `-p` (`--parents`) — agar ota kataloglar mavjud bo'lmasa ularni ham yaratadi va agar papka allaqachon mavjud bo'lsa xato qaytarmaydi.
* `~/a12-lab` — joriy foydalanuvchining uy papkasidagi (`/home/<user>/a12-lab`) manzil.

### 5. `cd ~/a12-lab`
* **Vazifasi:** Change directory — ko'rsatilgan `~/a12-lab` katalogiga o'tish.

### 6. `python3 -m py_compile app.py audit.py`
* **Vazifasi:** Python skriptlarining sintaksisini kodni bajarmasdan oldindan tekshirish (kompilyatsiya qilish).
* `-m py_compile` — Pythonning ichki `py_compile` modulini chaqirish. Agar kodda sintaktik xato yoki noto'g'ri bo'shliqlar (IndentationError) bo'lsa, xatoni darhol ko'rsatadi.

### 7. `python3 --version` va `curl --version`
* **Vazifasi:** Tizimda o'rnatilgan Python va curl versiyalarini tekshirish (audit hisobotidagi muhit ma'lumotlari uchun).

### 8. `sha256sum app.py audit.py > source.sha256`
* **Vazifasi:** Manba kodlarning SHA-256 kriptografik xesh-summalarini hisoblab, `source.sha256` fayliga yozish.
* `sha256sum` — faylning har bir baytiga asoslangan 256-bitli noyob xesh hisoblaydi.
* `>` — natijani faylga yo'naltirish (mavjud bo'lsa ustidan yozish). Bu kelgusida kod o'zgarmaganini isbotlash uchun dalil (integrity proof) hisoblanadi.

### 9. `python3 -u app.py > before-server.log 2>&1`
* **Vazifasi:** Serverni fonda/alohida terminalda ishga tushirib, barcha chiqishlarni jurnal fayliga yo'naltirish.
* `-u` (`unbuffered`) — Python standart chiqish (stdout va stderr) oqimlarini xotirada ushlab turmasdan (buferlamasdan), darhol diskka yozishni ta'minlaydi.
* `> before-server.log` — standart chiqishni (stdout, fayl deskriptori 1) `before-server.log` ga yo'naltirish.
* `2>&1` — xatoliklar chiqishini ham (stderr, fayl deskriptori 2) standart chiqish bilan bir xil joyga (`&1`) yo'naltirish.

### 10. `ss -ltn | grep ":8012"`
* **Vazifasi:** 8012-portda veb-server ishlayotganini (tinglayotganini) tekshirish.
* `ss` — socket statistics (tarmoq ulanishlarini ko'rish).
* `-l` (`--listening`) — faqat ulanish kutayotgan (tinglovchi) portlarni ko'rsatish.
* `-t` (`--tcp`) — faqat TCP ulanishlarni ko'rsatish.
* `-n` (`--numeric`) — port va IP nomlarini matnga (DNS) aylantirmasdan, sonlar ko'rinishida chiqarish (tezroq ishlaydi).
* `|` (pipe) — birinchi buyruq natijasini ikkinchisiga uzatish.
* `grep ":8012"` — ro'yxat ichidan aynan `:8012` yozuvi bor qatorni filtrlab olish.

### 11. `curl --noproxy "*" -i "$U/health"`
* **Vazifasi:** `/health` manziliga dastlabki HTTP so'rovini yuborish.
* `--noproxy "*"` — har qanday tizim proksi sozlamalarini chetlab o'tib, to'g'ridan-to'g'ri `127.0.0.1` ga ulanish.
* `-i` (`--include`) — server qaytargan HTTP sarlavhalari (HTTP status kodi, Content-Type va b.) ni javob tanasi bilan birga ko'rsatish.
* `"$U/health"` — `$U` o'zgaruvchisidagi URL ga qo'shilgan yo'l (`http://127.0.0.1:8012/health`).

### 12. `curl --noproxy "*" -i "$U/api/note?id=1" -H "X-Lab-Token: demo-alice"`
* **Vazifasi:** Maxsus sarlavha bilan avtorizatsiyalangan so'rov yuborish.
* `-H` (`--header`) — HTTP so'roviga maxsus sarlavha qo'shish. Bu yerda `X-Lab-Token: demo-alice` Alice nomidan kirishni ta'minlaydi.

### 13. `curl ... | tee f01-before.txt`
* **Vazifasi:** So'rov natijasini ekranda ko'rsatish bilan birga faylga saqlash.
* `tee` — kiritilgan oqimni ikkiga bo'ladi: birini ekranga (terminalga) chiqaradi, ikkinchisini ko'rsatilgan faylga yozadi. Bu audit dalillarini darhol qayd etish uchun qulay.

### 14. `curl --noproxy "*" -s -G "$U/api/search" --data-urlencode "q=Alice"`
* **Vazifasi:** Qidiruv endpointiga xavfsiz URL-kodlangan GET so'rov yuborish.
* `-s` (`--silent`) — ortiqcha yuklanish indikatorlari va xabarlarni yashirish.
* `-G` (`--get`) — yuborilayotgan ma'lumotlarni POST so'rovi tanasida emas, GET so'rovining URL manziliga (`?q=...`) joylash.
* `--data-urlencode` — parametr qiymatini avtomatik ravishda URL-encoding (masalan, bo'sh joylarni `%20` ga, qo'shtirnoqlarni `%27` ga) aylantirish.

### 15. `curl ... --data-urlencode "q=' OR 1=1-- "`
* **Vazifasi:** Qidiruv maydoniga SQL inyeksiya payloadini jo'natish.
* `'` — SQL satrini yopish;
* `OR 1=1` — shartni doimo rost qilish;
* `-- ` — so'rovning qolgan qismini izohga aylantirish (SQLite sintaksisi).

### 16. `python3 audit.py > before.txt 2>&1` va `echo "$BEFORE_RC"`
* **Vazifasi:** Avtomatlashtirilgan audit testlarini ishga tushirish va uning natijasi hamda chiqish kodini tekshirish.
* `BEFORE_RC=$?` — oldingi bajarilgan buyruqning chiqish kodini (Exit Status) o'zgaruvchiga saqlash.
* Chiqish kodi `0` bo'lsa — muvaffaqiyatli, `0` dan farqli bo'lsa — xatolik yoki testlarning yiqilganini (FAIL) bildiradi.

### 17. `python3 -u app.py --secure > after-server.log 2>&1`
* **Vazifasi:** Serverni tuzatilgan (himoyalangan) rejimda ishga tushirish.
* `--secure` — `app.py` ichidagi `SECURE` o'zgaruvchisini `True` ga aylantiradi va barcha xavfsizlik choralarini (parametrli SQL, egasini tekshirish, HTML escaping, CSP sarlavhalari) faollashtiradi.

### 18. `diff -u before.txt after.txt`
* **Vazifasi:** Himoyadan oldingi (`before.txt`) va himoyadan keyingi (`after.txt`) test natijalari orasidagi farqni unifikatsiyalangan formatda ko'rsatish.
* `-u` (`--unified`) — o'zgargan qatorlarni `+` (qo'shilgan) va `-` (o'chirilgan) belgilari bilan aniq ko'rsatish.

### 19. `grep -F "SIZNING_REQUEST_ID" after-server.log`
* **Vazifasi:** Server jurnalidan aniq bir so'rovga tegishli yozuvni topish.
* `grep` — global regular expression print (matndan qidirish).
* `-F` (`--fixed-strings`) — qidirilayotgan satrni regex sifatida emas, oddiy qat'iy matn sifatida qidirish (tezroq va xatosiz).

### 20. `CASE_DIR="evidence-$(date -u +%Y%m%dT%H%M%SZ)"`
* **Vazifasi:** Xalqaro UTC vaqti bilan nomlangan yangi dalillar papkasi nomini o'zgaruvchiga yuklash.
* `$(date -u +%Y%m%dT%H%M%SZ)` — masalan: `evidence-20261112T115500Z` ko'rinishidagi ISO-8601 standartidagi vaqt tamg'asi.

### 21. `mkdir -m 700 "$CASE_DIR"`
* **Vazifasi:** Dalillar papkasini faqat egasi o'qiy oladigan va kiradigan qilib yaratish.
* `-m 700` (`--mode=700`) — papkaga `rwx------` huquqini o'rnatish.

### 22. `(cd "$CASE_DIR" && sha256sum * > SHA256SUMS)`
* **Vazifasi:** Subshell (qavs ichida) orqali dalillar papkasiga kirib, undagi barcha fayllarning SHA256 xeshini `SHA256SUMS` manifest fayliga yozish. Qavslar asosiy terminalning joriy katalogini o'zgartirmaydi.

### 23. `(cd "$CASE_DIR" && sha256sum -c SHA256SUMS)`
* **Vazifasi:** Manifestdagi xeshlarni fayllar bilan solishtirib chiqish.
* `-c` (`--check`) — ko'rsatilgan ro'yxat bo'yicha har bir faylning xeshini tekshirib, yoniga `OK` yoki `FAILED` yozuvini chiqarish.

### 24. `chmod 400 "$CASE_DIR"/*`
* **Vazifasi:** Dalil fayllarini faqat o'qish (Read-Only) rejimiga o'tkazish.
* `400` — egasi uchun faqat o'qish (`r--------`), yozish yoki o'chirish taqiqlanadi. Bu dalillar tasodifan o'zgartirib yuborilishining oldini oladi.

---

## 6. ILOVANING TO'LIQ MANBA KODLARI (APP.PY VA AUDIT.PY)

Quyidagi kodlarni to'liq holda ko'chirib, tegishli fayllarga saqlashingiz mumkin.

### 1. `~/a12-lab/app.py` faylining to'liq kodi
```python
import argparse, html, json, sqlite3, time, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit, parse_qs

# Buyruqlar qatoridan argumentlarni o'qish
parser = argparse.ArgumentParser()
parser.add_argument('--secure', action='store_true', help='Xavfsiz rejimni faollashtirish')
SECURE = parser.parse_args().secure

# O'quv tokenlari (haqiqiy production uchun emas!)
TOKENS = {'demo-alice': 'alice', 'demo-bob': 'bob'}

# Xotirada SQLite bazasini yaratish
DB = sqlite3.connect(':memory:')
DB.row_factory = sqlite3.Row
DB.execute('CREATE TABLE notes(id INTEGER, owner TEXT, title TEXT)')
DB.executemany('INSERT INTO notes VALUES(?,?,?)', [
    (1, 'alice', 'Alice plan'),
    (2, 'bob', 'Bob private'),
    (3, 'alice', 'Alice report')
])

def get_note(owner, note_id):
    """Bitta qaydni ID bo'yicha olish"""
    if SECURE:
        # Xavfsiz: ID va Owner birga tekshiriladi (IDOR dan himoyalangan)
        return DB.execute('SELECT * FROM notes WHERE id=? AND owner=?', 
                          (note_id, owner)).fetchone()
    # Zaif: Faqat ID tekshiriladi, egasi tekshirilmaydi (IDOR mavjud!)
    return DB.execute('SELECT * FROM notes WHERE id=?', (note_id,)).fetchone()

def search(owner, term):
    """Qaydlar ichidan qidirish"""
    if SECURE:
        # Xavfsiz: Parametrli so'rov (SQL Inyeksiyadan himoyalangan)
        return DB.execute('SELECT * FROM notes WHERE owner=? AND title LIKE ?', 
                          (owner, '%' + term + '%'))
    # Zaif: Satrlarni qo'shish (SQL Inyeksiya mavjud!)
    sql = ("SELECT * FROM notes WHERE owner='" + owner + 
           "' AND title LIKE '%" + term + "%'")
    return DB.execute(sql)

def preview(text):
    """Matnni ko'rish (preview) HTML sahifasi"""
    # Xavfsiz rejimda HTML belgilar entityga aylantiriladi
    value = html.escape(text, quote=True) if SECURE else text
    return ('<!doctype html><meta charset="utf-8">'
            '<title>A12 Preview</title><h1>Preview</h1>'
            '<div>' + value + '</div>')

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        # Birlamchi konsol loglarini o'chirish
        pass

    def reply(self, status, obj, is_html=False):
        rid = uuid.uuid4().hex
        body = (obj if is_html else json.dumps(obj)).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',
                         'text/html; charset=utf-8' if is_html
                         else 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Request-ID', rid)
        
        # Himoyalangan rejimda xavfsizlik sarlavhalari qo'shiladi
        if SECURE:
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy',
                             "default-src 'none'; frame-ancestors 'none'; "
                             "base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)
        
        # Audit jurnali (JSON formatida)
        print(json.dumps({'ts': time.time(), 'request_id': rid,
                          'path': urlsplit(self.path).path,
                          'status': status, 'secure': SECURE}), flush=True)

    def do_GET(self):
        try:
            path = urlsplit(self.path).path
            qs = parse_qs(urlsplit(self.path).query,
                          keep_blank_values=True, max_num_fields=10)
            
            # Health endpoint
            if path == '/health':
                return self.reply(200, {'ok': True, 'secure': SECURE})
            
            # Preview endpoint (XSS tekshiruvi uchun)
            if path == '/preview':
                text = qs.get('text', [''])[0]
                if len(text) > 500:
                    return self.reply(400, {'error': 'bad_input'})
                return self.reply(200, preview(text), True)
            
            # API yo'llarini tekshirish
            if path not in ('/api/note', '/api/search'):
                return self.reply(404, {'error': 'not_found'})
            
            # Token orqali egasini aniqlash
            owner = TOKENS.get(self.headers.get('X-Lab-Token'))
            if owner is None:
                return self.reply(401, {'error': 'unauthorized'})
            
            # Note API
            if path == '/api/note':
                note_id = qs.get('id', [''])[0]
                if not note_id.isascii() or not note_id.isdecimal():
                    return self.reply(400, {'error': 'bad_input'})
                row = get_note(owner, note_id)
                if row is None:
                    return self.reply(404, {'error': 'not_found'})
                return self.reply(200, dict(row))
            
            # Search API
            term = qs.get('q', [''])[0]
            if len(term) > 100:
                return self.reply(400, {'error': 'bad_input'})
            rows = [dict(r) for r in search(owner, term)]
            return self.reply(200, {'notes': rows})
            
        except (ValueError, sqlite3.Error):
            return self.reply(400, {'error': 'bad_input'})

print('A12 127.0.0.1:8012 secure=' + str(SECURE), flush=True)
server = HTTPServer(('127.0.0.1', 8012), Handler)
server.timeout = 2
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
    DB.close()
```

---

### 2. `~/a12-lab/audit.py` faylining to'liq kodi
```python
import html, json, sys
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError
from urllib.parse import urlencode

BASE = 'http://127.0.0.1:8012'
client = build_opener(ProxyHandler({}))
results = []

def get(path, token='demo-alice'):
    headers = {'X-Lab-Token': token} if token else {}
    try:
        response = client.open(Request(BASE + path, headers=headers), timeout=5)
    except HTTPError as error:
        response = error
    with response:
        return response.code, response.headers, response.read().decode()

def check(name, passed):
    results.append(bool(passed))
    print(('PASS ' if passed else 'FAIL ') + name)

# Testlar ro'yxati:
s, h, b = get('/health')
check('T01 health', s == 200 and json.loads(b)['ok'])

s, h, b = get('/api/note?id=1')
check('T02 own_note', s == 200 and json.loads(b)['owner'] == 'alice')

s, h, b = get('/api/note?id=2', 'demo-bob')
check('T03 bob_own_note', s == 200 and json.loads(b)['owner'] == 'bob')

s, h, b = get('/api/note?id=1', None)
check('T04 no_token', s == 401)

s, h, b = get('/api/note?id=2')
check('T05 foreign_note', s == 404 and 'Bob private' not in b)

s, h, b = get('/api/search?' + urlencode({'q': 'Alice'}))
check('T06 normal_search', s == 200 and
      [n['id'] for n in json.loads(b)['notes']] == [1, 3])

s, h, b = get('/api/search?' + urlencode({'q': "' OR 1=1-- "}))
check('T07 sql_input', s == 200 and json.loads(b)['notes'] == [])

payload = '<script>document.title="A12-XSS"</script>'
s, h, b = get('/preview?' + urlencode({'text': payload}))
check('T08 output_encoding', s == 200 and html.escape(payload) in b
      and payload not in b)

check('T09 headers', h.get('X-Content-Type-Options') == 'nosniff'
      and h.get('Content-Security-Policy') ==
      "default-src 'none'; frame-ancestors 'none'; "
      "base-uri 'none'; form-action 'none'")

s, h, b = get('/api/note?id=xyz')
check('T10 invalid_id', s == 400 and 'Traceback' not in b)

s, h, b = get('/api/note?id=999')
check('T11 missing_note', s == 404)

s, h, b = get('/preview?' + urlencode({'text': 'Salom & <kitob>'}))
check('T12 normal_text', s == 200 and 'Salom' in b)

print('SUMMARY', sum(results), '/', len(results))
sys.exit(0 if all(results) else 1)
```

---

## 7. FOYDALANILGAN RASMIY VA ME'YORIY MANBALAR

Laboratoriya ishi doirasida foydalanilgan xalqaro standartlar, metodologiyalar va hujjatlar:

1. **OWASP Top 10:2025 Standard:**
   - A01: Broken Access Control (Kirish nazoratining buzilishi va IDOR);
   - A02: Security Misconfiguration (Xavfsizlik konfiguratsiyasidagi kamchiliklar);
   - A05: Injection (SQL inyeksiya va Cross-Site Scripting).
   - Manzil: [https://owasp.org/Top10/](https://owasp.org/Top10/)

2. **OWASP ASVS (Application Security Verification Standard) v5.0.0:**
   - V4: Access Control Verification Requirements;
   - V5: Malicious Input Handling and Injection Prevention;
   - V14: Configuration and HTTP Headers.
   - Manzil: [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/)

3. **OWASP Cheat Sheets Series:**
   - *Authorization Cheat Sheet* (Obyekt darajasidagi avtorizatsiyani to'g'ri loyihalash);
   - *SQL Injection Prevention Cheat Sheet* (Parametrlangan so'rovlar va ORM xavfsizligi);
   - *Cross-Site Scripting (XSS) Prevention Cheat Sheet* (Kontekstual HTML Entity Encoding va CSP qo'llash).
   - Manzil: [https://cheatsheetseries.owasp.org/](https://cheatsheetseries.owasp.org/)

4. **NIST SP 800-218 (Secure Software Development Framework - SSDF v1.1):**
   - Dasturiy ta'minotning butun hayotiy siklida (SDLC) xavfsizlikni ta'minlash, integratsiya sinovlari va chiqarish qarorlarini qabul qilish qoidalari.
   - Manzil: [https://csrc.nist.gov/publications/detail/sp/800-218/final](https://csrc.nist.gov/publications/detail/sp/800-218/final)

5. **Python Rasmiy Hujjatlari:**
   - Python `http.server` moduli xavfsizlik chegaralari va ogohlantirishlari (Module security considerations: Production uchun mo'ljallanmaganligi);
   - Python `sqlite3` xavfsiz parametrli so'rovlar (`?` placeholder) hujjatlari.
   - Manzil: [https://docs.python.org/3/library/http.server.html](https://docs.python.org/3/library/http.server.html)
