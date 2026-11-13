# A7 Laboratoriya Mashg‘uloti: Talabnoma va Amaliy Yo‘riqnoma

Ushbu hujjat **A7: Fayllar bilan ishlash va server tomon zaifliklari (1-variant)** mavzusidagi laboratoriya ishini mustaqil bajarish, har bir qadam bo‘yicha aniq dalillar (skrinshotlar) to‘plash va yakunda 100% talabga javob beruvchi **`hisobot.docx`** faylini tayyorlash uchun mo‘ljallangan.

---

## 📌 Ish printsipi va o‘zaro hamkorlik tartibi

1. **Siz bajarasiz:** Quyida qadamma-qadam keltirilgan Linux terminal buyruqlarini bajarasiz va belgilangan 11 ta skrinshotni olib, **`images/`** papkasiga ko‘rsatilgan nom bilan saqlaysiz.
2. **Men bajaraman:** Siz rasmlarni `images/` papkasiga joylab xabar berganingizdan so‘ng, men barcha amaliy natijalar, kodlar, D1–D6 dalillar jadvallari, nazorat savollari va manbalar asosida mukammal **`hisobot.docx`** hujjatini generatsiya qilib beraman.

---

## 📷 Skrinshotlar Xaritasi (`images/` papkasi uchun)

Barcha rasmlar `A7_project/images/` papkasiga PNG yoki JPG formatida saqlanishi kerak:

| Rasm fayl nomi | Tegishli dalil | Bosqich / Mavzu | Skrinshotda nimalar aniq ko‘rinishi shart? |
| :--- | :---: | :--- | :--- |
| **`1.png`** | **D1** | Muhit va 3 ta xizmat tekshiruvi | 3 ta `curl` buyrug‘i va ularning `HTTP 200` javoblari (8007, 8017 `/card` [Daftar], 8018 `/status` [A7-INTERNAL]). |
| **`2.png`** | **D2 (1-qism)** | PNG yuklash: Zaif vs Xavfsiz | `good.png` va `fake.png` zaif endpointda `201` bo‘lib saqlangani, lekin `fake.png` xavfsiz endpointda `415` bilan rad etilgani. |
| **`3.png`** | **D2 (2-qism)** | Mazmun, hajm, piksel va xesh | Xavfsiz endpointda `signature.png` (415), `big.png` (413), `pixels.png` (413), `good.png` (201) va `sha256sum storage/<id>` tekshiruvi. |
| **`4.png`** | **D3 (1-qism)** | Path Traversal: Katalog chegarasi | `/read/weak` orqali `guide.txt` (200) va `../internal/demo.txt` (200 A7-PRIVATE-FILE zaiflik!), hamda `/read/safe` da 403 bloklanishi. |
| **`5.png`** | **D3 (2-qism)** | Path Traversal: Symlink sinovi | `ln -s ../internal/demo.txt files/link.txt` yaratilishi, safe orqali `403` rad etilishi va symlink o‘chirilishi (`rm`). |
| **`6.png`** | **D4 (1-qism)** | SSRF sinovlari (Mijoz terminali) | `/fetch/weak` orqali 8017 (200) va 8018 (200 A7-INTERNAL zaiflik!), hamda `/fetch/safe` orqali 8018 ning `403` rad etilishi. |
| **`7.png`** | **D4 (2-qism)** | SSRF jurnali (Backend terminali) | 2-terminalda `services.py` jurnali: zaif so‘rovda GET kelgani, safe so‘rovida esa 8018 ga hech qanday GET kelmaganligi. |
| **`8.png`** | **D5 (1-qism)** | Kodni tuzatish (Diff/Kod ko‘rinishi) | `app.py` dagi 3 ta funksiya (`upload_weak`, `read_weak`, `fetch_weak`) tuzatilgani yoki `diff -u app_before.py app.py` natijasi. |
| **`9.png`** | **D5 (2-qism)** | Regressiya sinovlari (/weak manzillari) | Tuzatishdan so‘ng `/weak` endpointlarida: soxta fayl (415), traversal (403), ichki URL (403) va qonuniylar (201, 200). |
| **`10.png`** | **Qo‘shimcha** | Xavfsiz ma’lumot tiklash (JSON) | `/preferences` endpointiga 3 ta so‘rov: to‘g‘ri (200), noto‘g‘ri tur (400), ortiqcha `admin` maydoni (400). |
| **`11.png`** | **D6 / Yakun** | Loyiha katalogi va fayllar tuzilmasi | `ls -la ~/websec/A7/` va `ls -la storage/` ro‘yxati (fayllar, `.venv`, `requirements-lock.txt`). |

---

## 🚀 Bosqichma-bosqich Amaliy Ko‘rsatma (CLI Buyruqlari)

Har bir bosqichni terminalda ketma-ket bajaring va kerakli o‘rinda skrinshot oling.

---

### 0-BOSQICH: Ishchi muhit va virtual muhitni tayyorlash

Ubuntu terminalida quyidagi buyruqlarni bajaring:

```bash
# 1. Tizim va shaxsiy identifikatsiya (majburiy ko‘rsatkichlar)
sudo hostnamectl set-hostname veb-a7-lab
whoami
id
date -Is

# 2. Zarur paketlarni o‘rnatish va loyiha papkasini ochish
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl nano
mkdir -p ~/websec/A7/evidence
cd ~/websec/A7

# 3. Python virtual muhitini yaratish va kutubxonalarni o‘rnatish
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Flask==3.1.3 Pillow==11.3.0
python -m pip freeze > requirements-lock.txt
```

#### Dastlabki kod fayllarini yaratish:
`~/websec/A7` papkasida 3 ta fayl yaratiladi: `app.py`, `services.py` va `prepare.py`.
*(Kodlar to‘liq ko‘rinishi ushbu yo‘riqnomaning [ILOVALAR](#ilovalar-dastlabki-kodlar) bo‘limida keltirilgan).*

Fayllar yaratilgach, ularni kompilyatsiya qilib, sinov fayllarini yarating va nusxasini saqlang:
```bash
python -m py_compile app.py services.py prepare.py
python prepare.py
cp app.py app_before.py
umask 077
```

---

### 1-BOSQICH: Xizmatlarni ishga tushirish va tekshirish (D1 Dalili)

Sizga **3 ta alohida terminal oynasi** kerak bo‘ladi:

* **1-Terminalda (Asosiy ilova - 8007-port):**
  ```bash
  cd ~/websec/A7
  source .venv/bin/activate
  python app.py
  ```
  *(Bu oyna yopilmaydi, doim ishlab turadi)*

* **2-Terminalda (O‘quv xizmatlari - 8017 va 8018-portlar):**
  ```bash
  cd ~/websec/A7
  source .venv/bin/activate
  python services.py
  ```
  *(Bu oyna ham yopilmaydi, backend jurnali shu yerda ko‘rinadi)*

* **3-Terminalda (Sinov mijozi - curl so‘rovlari):**
  ```bash
  cd ~/websec/A7
  curl --noproxy "*" -i http://127.0.0.1:8007/
  curl --noproxy "*" -i http://127.0.0.1:8017/card
  curl --noproxy "*" -i http://127.0.0.1:8018/status
  ```

> 📸 **SKRINSHOT 1 (`images/1.png`):**
> 3-terminalda yuqoridagi 3 ta curl buyrug‘i va ularning `HTTP 200` javoblari ko‘ringan holatni rasmga oling. (Javobda: `A7 / 1-variant`, `Daftar` va `A7-INTERNAL` yozuvlari bo‘lishi kerak).

---

### 2-BOSQICH: PNG yuklash sinovlari — Zaif vs Xavfsiz (D2 Dalili)

3-terminalda davom etasiz:

#### A) Qonuniy va soxta faylni solishtirish:
```bash
# 1. Haqiqiy rasmni zaif endpointga yuklash (HTTP 201)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/weak -F "file=@samples/good.png;type=image/png"

# 2. Soxta PNG (aslida matn)ni zaif endpointga yuklash (HTTP 201 - ZAIFLIK!)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/weak -F "file=@samples/fake.png;type=image/png"

# 3. Aynan shu soxta faylni xavfsiz endpointga yuklash (HTTP 415 - HIMOYA!)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe -F "file=@samples/fake.png;type=image/png"
```

> 📸 **SKRINSHOT 2 (`images/2.png`):**
> Ushbu 3 ta buyruq natijasi: `good.png` (201), `fake.png` zaifda (201, 9 bayt) saqlangani va xavfsizda (415) rad etilgani ko‘ringan holat.

#### B) Maxsus hujum namunalari va xesh yaxlitligi:
```bash
# 4. Faqat imzo (Magic bytes) bor, buzilgan rasm (HTTP 415)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe -F "file=@samples/signature.png;type=image/png"

# 5. Katta bayt hajmli fayl - limit 256 KB (HTTP 413)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe -F "file=@samples/big.png;type=image/png"

# 6. Katta piksel o‘lchami (1001x1000 = 1 001 000 px > 1M px) (HTTP 413)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe -F "file=@samples/pixels.png;type=image/png"

# 7. Qonuniy rasmni xavfsiz endpointga yuklash (HTTP 201)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe -F "file=@samples/good.png;type=image/png"

# 8. Saqlangan faylning xeshini tekshirish (qaytgan id nomini qo‘ying):
ls -la storage/
sha256sum storage/*.png
```

> 📸 **SKRINSHOT 3 (`images/3.png`):**
> `signature.png` (415), `big.png` (413), `pixels.png` (413), `good.png` (201) va `storage/` dagi fayllar xeshi (`sha256sum`) ko‘ringan ekran.

---

### 3-BOSQICH: Path Traversal sinovlari va Symlink (D3 Dalili)

3-terminalda fayl o‘qish endpointlarini sinang:

#### A) Ochiq va maxfiy fayllarni o‘qish:
```bash
# 1. Ruxsat etilgan ochiq faylni o‘qish (HTTP 200: A7-PUBLIC)
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/weak --data-urlencode "name=guide.txt"

# 2. Katalogdan chiqib maxfiy faylni o‘qish (HTTP 200: A7-PRIVATE-FILE - ZAIFLIK!)
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/weak --data-urlencode "name=../internal/demo.txt"

# 3. Aynan shu buzg‘unchi yo‘lni xavfsiz endpointda sinash (HTTP 403 - HIMOYA!)
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/safe --data-urlencode "name=../internal/demo.txt"

# 4. Qonuniy faylni xavfsiz endpointda o‘qish (HTTP 200: A7-PUBLIC)
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/safe --data-urlencode "name=guide.txt"
```

> 📸 **SKRINSHOT 4 (`images/4.png`):**
> Zaif endpointda `../internal/demo.txt` o‘qilib `A7-PRIVATE-FILE` chiqqani, xavfsiz endpointda esa unga `403` qaytgani va `guide.txt` 200 bo‘lgani.

#### B) Ramziy bog‘lama (Symlink) orqali tekshiruv:
```bash
# Symlink yaratish, sinash va o‘chirish
ln -s ../internal/demo.txt files/link.txt
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/safe --data-urlencode "name=link.txt"
rm files/link.txt
```

> 📸 **SKRINSHOT 5 (`images/5.png`):**
> `files/link.txt` orqali murojaat qilinganda xavfsiz endpoint `resolve()` orqali nishonni fosh qilib `403` qaytargani va `rm files/link.txt` buyrug‘i.

---

### 4-BOSQICH: SSRF sinovlari va Backend jurnali (D4 Dalili)

#### A) 3-terminalda so‘rovlar yuborish:
```bash
# 1. Qonuniy katalog xizmatini chaqirish (HTTP 200: catalog / Daftar)
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/weak --data-urlencode "url=http://127.0.0.1:8017/card"

# 2. Ichki yopiq ma’muriy xizmatni chaqirish (HTTP 200: A7-INTERNAL - ZAIFLIK!)
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/weak --data-urlencode "url=http://127.0.0.1:8018/status"

# 3. Aynan shu ichki manzilni xavfsiz endpoint orqali chaqirish (HTTP 403 - HIMOYA!)
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/safe --data-urlencode "url=http://127.0.0.1:8018/status"

# 4. Qonuniy URL xavfsiz endpointda ham ishlashini tasdiqlash (HTTP 200)
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/safe --data-urlencode "url=http://127.0.0.1:8017/card"
```

> 📸 **SKRINSHOT 6 (`images/6.png`):**
> 3-terminalda: zaif endpoint orqali ichki `8018/status` o‘qilib `A7-INTERNAL` qaytgani, xavfsiz endpointda esa `403` bilan bloklangani.

#### B) 2-terminaldagi jurnalni tekshirish:
> 📸 **SKRINSHOT 7 (`images/7.png`):**
> 2-terminaldagi (`python services.py`) konsol yozuvlari skrinshoti: zaif so‘rov vaqtida `GET /status` kelgani, lekin xavfsiz (`/fetch/safe`) so‘rovi berilganda 8018 ga umuman so‘rov yetib bormagani (ilova darajasida to‘xtatilgani) ko‘rinsin.

---

### 5-BOSQICH: Uchta kod tuzatishi va regressiya sinovlari (D5 Dalili)

#### A) Kodni to‘g‘rilash:
1-terminaldagi asosiy serverni `Ctrl+C` bilan to‘xtating.
`nano app.py` orqali faylni ochib, quyidagi 3 ta funksiyani almashtiring:

1. **Fayl mazmunini tekshirish:**
```python
def upload_weak(raw):
    return png_content(raw)
```

2. **Katalog chegarasini to‘g‘rilash:**
```python
def read_weak(name):
    target = (FILES / name).resolve()
    if not target.is_relative_to(FILES.resolve()):
        abort(403)
    return read_text(target)
```

3. **URL Allowlist qo‘llash:**
```python
def fetch_weak(url):
    if url != PUBLIC_URL:
        abort(403)
    return lab_fetch(url)
```

O‘zgarishlarni tekshiring:
```bash
diff -u app_before.py app.py
python -m py_compile app.py
```

> 📸 **SKRINSHOT 8 (`images/8.png`):**
> `diff -u app_before.py app.py` buyrug‘i natijasi yoki `app.py` dagi tuzatilgan 3 ta funksiya matni.

#### B) Serverni qayta ishga tushirib, regressiya sinovlarini o‘tkazish:
1-terminalda qayta ishga tushiring:
```bash
python app.py
```

3-terminalda **faqat `/weak` manzillarini** qayta sinang (ular endi mustahkamlangan):
```bash
# 1. Soxta rasm endi zaif endpointda ham 415 berishi kerak:
curl --noproxy "*" -i http://127.0.0.1:8007/upload/weak -F "file=@samples/fake.png;type=image/png"

# 2. ../ orqali chiqish endi zaif endpointda ham 403 berishi kerak:
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/weak --data-urlencode "name=../internal/demo.txt"

# 3. Ichki 8018 manzil endi zaif endpointda ham 403 berishi kerak:
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/weak --data-urlencode "url=http://127.0.0.1:8018/status"

# 4. Qonuniy so‘rovlar hali ham 201 va 200 berishi kerak:
curl --noproxy "*" -i http://127.0.0.1:8007/upload/weak -F "file=@samples/good.png;type=image/png"
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/weak --data-urlencode "name=guide.txt"
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/weak --data-urlencode "url=http://127.0.0.1:8017/card"
```

> 📸 **SKRINSHOT 9 (`images/9.png`):**
> Yuqoridagi regressiya sinovlari: `/weak` endpointlarida buzg‘unchi so‘rovlar (415, 403, 403) rad etilgani va qonuniylar (201, 200, 200) muvaffaqiyatli ishlagani.

---

### 6-BOSQICH: Qo‘shimcha topshiriq — Xavfsiz ma’lumot tiklash (JSON Sxema)

3-terminalda `/preferences` endpointini 3 xil so‘rov bilan sinang:

```bash
# 1. Qonuniy JSON (HTTP 200)
curl --noproxy "*" -i http://127.0.0.1:8007/preferences \
  -H 'Content-Type: application/json' -d '{"theme":"dark"}'

# 2. Qiymat turi noto‘g‘ri (satr o‘rniga obyekt kiritildi) (HTTP 400)
curl --noproxy "*" -i http://127.0.0.1:8007/preferences \
  -H 'Content-Type: application/json' -d '{"theme":{"name":"dark"}}'

# 3. Ruxsat berilmagan ortiqcha parametr qo‘shildi (admin: true) (HTTP 400)
curl --noproxy "*" -i http://127.0.0.1:8007/preferences \
  -H 'Content-Type: application/json' -d '{"theme":"dark","admin":true}'
```

> 📸 **SKRINSHOT 10 (`images/10.png`):**
> 3 ta curl so‘rovi: 1-holatda `200`, 2- va 3-holatlarda esa `400 Bad Request` qaytgani.

---

### 7-BOSQICH: Katalog tuzilishi va yakuniy holat (D6 Dalili)

Sinovlar tugagach:
```bash
ls -la ~/websec/A7/
ls -la ~/websec/A7/storage/
cat requirements-lock.txt
```

> 📸 **SKRINSHOT 11 (`images/11.png`):**
> `~/websec/A7/` papkasi tarkibi, `storage/` dagi saqlangan rasmlar va `requirements-lock.txt` ko‘rinishi.

---

## 📊 D6 — Yakuniy Solishtirma Natijalar Jadvali (1.7-band)

Hisobotda va og‘zaki himoyada aks etadigan to‘liq D6 jadvali:

| № | Sinov harakati va yuborilgan namuna | Oldin (`/weak` dastlabki) | Keyin (`/weak` tuzatilgach) | Amaldagi dalil va izoh |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `good.png` yuklash (32x32 qonuniy PNG) | **HTTP 201**; saqlandi | **HTTP 201**; qayta kodlanib saqlandi | Toza rasm har ikki holatda qabul qilindi. |
| **2** | `fake.png` yuklash (NOT-A-PNG matni) | **HTTP 201**; 9 bayt saqlandi (Xato!) | **HTTP 415**; yangi fayl yo‘q | Soxta rasm aniqlanib, rad etildi. |
| **3** | `signature.png` yuklash (faqat PNG imzosi) | **HTTP 201**; saqlandi (Xato!) | **HTTP 415**; ochilmadi | Magic bytes aldovi to‘liq dekodlashda fosh bo‘ldi. |
| **4** | `big.png` yuklash (256 KB dan ortiq hajm) | **HTTP 413**; rad etildi | **HTTP 413**; rad etildi | Bayt hajmi chegarasi buzilmadi. |
| **5** | `pixels.png` yuklash (1001x1000 = 1 001 000 px) | **HTTP 201**; saqlandi (Xato!) | **HTTP 413**; Piksel limiti oshdi | Dekompressiya bombasi (Pixel Flood) to‘xtatildi. |
| **6** | `guide.txt` o‘qish (qonuniy ochiq fayl) | **HTTP 200**; `A7-PUBLIC` | **HTTP 200**; `A7-PUBLIC` | Qonuniy faylga kirish saqlanib qoldi. |
| **7** | `../internal/demo.txt` (Path Traversal) | **HTTP 200**; `A7-PRIVATE-FILE` (Zaiflik!)| **HTTP 403**; Forbidden | FILES katalogi chegarasidan chiqish to‘xtatildi. |
| **8** | `8017/card` resursi (Qonuniy katalog URL) | **HTTP 200**; `catalog` / `Daftar` | **HTTP 200**; `catalog` / `Daftar` | Biznes talabidagi tashqi chaqiruv ishladi. |
| **9** | `8018/status` resursi (Ichki yopiq ma’muriy URL)| **HTTP 200**; `A7-INTERNAL` (SSRF!) | **HTTP 403**; Backend GET yo‘q | Server faqat ruxsat etilgan URLga ulandi. |
| **10**| `/preferences` JSON sxema tekshiruvi | — | **200** (to‘g‘ri), **400** (xato tur/ortiqcha) | Noto‘g‘ri ma’lumotlar ob’yektga tiklanmadi. |

---

## ❓ Nazorat Savollari va Ilmiy-Amaliy Javoblar (1.8-band)

Hisobotda to‘liq yoritilishi shart bo‘lgan 7 ta nazorat savolining mukammal javoblari:

### 1-savol: Nega `.png` kengaytmasi va `image/png` MIME turi fayl mazmunini isbotlamaydi?
> **Javob:** Fayl kengaytmasi (masalan, `shell.php.png`) faqat operatsion tizim yoki mijoz dasturi uchun yorliqdir; HTTP sarlavhasidagi `Content-Type: image/png` esa mijoz (brauzer yoki `curl`) tomonidan to‘liq nazorat qilinadi va osonlikcha soxtalashtiriladi. Hujumchi ixtiyoriy zararli skript (masalan, PHP, JSP, ELF) fayliga `.png` nomini va MIME turini berib yuborishi mumkin. Server fayl nomiga emas, uning ichki baytlariga qarashi shart.

### 2-savol: PNG imzosi (Magic Bytes) bor fayl nega baribir rasm sifatida ochilmasligi mumkin?
> **Javob:** PNG standarti bo‘yicha fayl boshi 8 baytlik sehrli imzo (`\x89PNG\r\n\x1a\n`) bilan boshlanadi. Hujumchi ixtiyoriy matn yoki zararli kod boshiga shu 8 baytni yopishtirib qo‘yishi mumkin (`signature.png` misoli). Agar server faqat boshlang‘ich baytlarni tekshirsa, fayl rasm deb o‘ylaydi. Biroq grafik kutubxona (masalan, Pillow) rasmning IHDR, IDAT, IEND chunklarini, siqish jadvalini va CRC nazorat summasini o‘qishga uringanda xatolik yuz beradi va rasm ochilmaydi. Shuning uchun faylni haqiqiy parser orqali to‘liq tekshirish (`im.verify()`, `im.load()`) shart.

### 3-savol: Fayl bayt hajmi va piksel soni nega ikki alohida limit sifatida tekshiriladi?
> **Javob:** Faylning diskdagi bayt hajmi siqilgan (compressed) holatni bildiradi, operativ xotiradagi (RAM) o‘lchami esa piksellar soniga (`width * height * channels`) bog‘liq. **Decompression Bomb (Pixel Flood)** hujumida juda yaxshi siqiluvchi 100 000 × 100 000 o‘lchamli bir xil rangli rasm diskda bor-yo‘g‘i 50 KB joy olishi mumkin. Ammo server uni xotirada dekodlaganda ~30–40 Gigabayt RAM talab qiladi va server Out-Of-Memory (OOM) bilan yiqiladi (DoS hujumi). Shu bois, ham bayt hajmi (masalan, 256 KB), ham piksellar soni (masalan, 1 000 000 px) mustaqil ikki qatlamli limit sifatida tekshiriladi.

### 4-savol: `resolve()` va `is_relative_to()` qanday turli vazifalarni bajaradi?
> **Javob:** 
> - `resolve()`: Nisbiy yo‘llarni (`../`, `./`) va ramziy bog‘lamalarni (symlink) to‘liq hisoblab, fayl tizimidagi mutlaq, haqiqiy kanonik yo‘lni (canonical path) hosil qiladi.
> - `is_relative_to(base)`: Mazkur kanonik yo‘l ko‘rsatilgan ruxsat etilgan asosiy katalog (`base`) ichida joylashganmi yoki yo‘qligini mantiqiy (`True`/`False`) tekshiradi.
> 
> *Muhim saboq:* Agar chegara sifatida butun loyiha ildizi (`ROOT`) olinsa, `../internal/demo.txt` uning ichida qolib ketadi va zaiflik yuzaga keladi. To‘g‘ri chegara faqat ruxsat etilgan quyi papka — `FILES.resolve()` bo‘lishi shart.

### 5-savol: SSRF so‘rovi backendga ulanishdan oldin rad etilganini qanday bilasiz?
> **Javob:** Asosiy ilova foydalanuvchidan kelgan URL manzilini HTTP ulanish (`http.client.HTTPConnection`) ochishdan avval tekshiradi (`if url != PUBLIC_URL: abort(403)`). Bu holat amalda 2-terminaldagi `services.py` backend konsol jurnali orqali isbotlanadi: zaif endpointda so‘rov berilganda backend jurnalida darhol `GET /status 200` yozuvi paydo bo‘ladi, xavfsiz endpointda esa mijoz `403 Forbidden` oladi va backend konsolida hech qanday yangi `GET` so‘rovi qayd etilmaydi.

### 6-savol: Nega bu tajribadagi matn o‘qish LFI, HTTP javob olish esa RFI deb atalmasligi kerak?
> **Javob:** 
> - **LFI (Local File Inclusion)** va **RFI (Remote File Inclusion)** zaifliklarida o‘qilgan yoki tashqaridan olingan fayl dasturlash tili interpretatori (masalan, PHP `include()`, Python `exec()`) tomonidan kod sifatida bajariladi.
> - Bu tajribada esa fayl faqat passiv matn ko‘rinishida o‘qiladi (`read_text`) yoki HTTP orqali ma’lumot olib beriladi (`fetch`). Server hech qanday faylni skript sifatida ishga tushirmaydi. Shuning uchun bu holatlar aniq ilmiy tilda **Path Traversal (Katalog chegarasidan chiqish)** va **SSRF (Server-Side Request Forgery)** deb ataladi.

### 7-savol: JSON sxemasini tekshirish va ishonchsiz `pickle`dan voz kechish qaysi xavflarni kamaytiradi?
> **Javob:** Pythonning standart `pickle` moduli o‘zboshimchalik bilan yozilgan obyektlarni deserializatsiya qilish jarayonida `__reduce__` metodi orqali operatsion tizim buyruqlarini avtomatik bajarish (`os.system`) imkonini beradi, bu esa to‘g‘ridan-to‘g‘ri Masofaviy Kod Bajarish (RCE) zaifligiga olib keladi. Matnli JSON formatiga o‘tish va qat’iy sxema (faqat kerakli maydonlar ro‘yxati, to‘g‘ri ma’lumot turlari, qiymatlar diapazoni) qo‘llash Mass Assignment (ortiqcha vakolat olish) va kod inyeksiya xavfini butunlay yo‘q qiladi.

---

## 📚 Foydalanilgan Rasmiy Manbalar (1.8-band)

1. **[1] OWASP** — *File Upload Cheat Sheet*: Xavfsiz fayl yuklash, kengaytma va MIME cheklovlari, qayta kodlash arxitekturasi.
2. **[2] OWASP** — *Path Traversal*: Yo‘l orqali katalog chegarasidan chiqish xavfi va kanonik yo‘l tekshiruvi.
3. **[3] OWASP** — *SSRF Prevention Cheat Sheet*: Server-Side Request Forgery xavfini oldini olish va qat’iy Allowlist mexanizmi.
4. **[4] Pillow Documentation** — *Image module: open, verify, load and limits*: Rasmlarni xavfsiz tekshirish va Dekompressiya bombasidan himoyalanish.
5. **[5] Python Standard Library** — *pathlib: Path.resolve and Path.is_relative_to*: Fayl tizimi yo‘llarini xavfsiz boshqarish.
6. **[6] OWASP Web Security Testing Guide (WSTG)** — *WSTG-INPV-04: Testing for Local File Inclusion*: LFI va Path Traversal chegaralari.
7. **[7] OWASP Web Security Testing Guide (WSTG)** — *WSTG-INPV-05: Testing for Remote File Inclusion*: RFI xususiyatlari.
8. **[8] Python Standard Library** — *http.client: HTTP and HTTPS client protocols*: Loopback transport va so‘rovlar cheklovi.
9. **[9] Python Standard Library** — *pickle: Security considerations*: Ishonchsiz deserializatsiya xavfi va ogohlantirishlar.

---

## 🏆 1.8 Baholash Mezonlari (10 Ballik Tizim Bo‘yicha)

| № | Baholash mezoni | Ajratilgan ball | Qanday ta’minlanadi? |
| :-: | :--- | :---: | :--- |
| **1** | **Muhit va nazorat so‘rovlari to‘g‘ri** | **1 ball** | D1 dalili: 8007, 8017 va 8018 xizmatlari loopbackda ishga tushishi va dastlabki tekshiruv. |
| **2** | **PNG sinovlari to‘liq va asoslangan** | **2 ball** | D2 dalili: fake.png, signature.png, big.png, pixels.png, good.png va sha256sum tahlili. |
| **3** | **Path Traversal sababi va katalog chegarasi** | **2 ball** | D3 dalili: `guide.txt`, `../internal/demo.txt` va `link.txt` symlink tahlili, FILES chegarasi. |
| **4** | **SSRF marker, backend jurnal va rad etish vaqti** | **2 ball** | D4 dalili: 8017/8018 chaqiruvlari, 2-terminal jurnali tahlili va ulanishdan oldin to‘xtatish. |
| **5** | **Uchta kod tuzatishi va regressiya sinovlari** | **2 ball** | D5 dalili: `app.py` dagi 3 ta funksiya o‘zgarishi (`diff`) va `/weak` da regressiya tekshiruvi. |
| **6** | **Hisobot, D6 jadvali va nazorat savollari** | **1 ball** | D6 to‘liq solishtirma jadvali, 7 ta nazorat savoliga ilmiy javoblar, xulosalar va manbalar. |
| — | **JAMI** | **10 ball** | **100% to‘liq qoniqtirilgan hisobot.** |

---

## 📝 Keyingi Qadam: Hisobotni Yaratish

Amallarni bajarib, `images/` papkasiga rasmlarni (`1.png`, `2.png`, ... `11.png`) saqlaganingizdan so‘ng:

> **"Rasmlarni images papkasiga joyladim, hisobot.docx ni yarat"** deb xabar yozing.

Men darhol yuqoridagi barcha dalillar, rasmlar, jadvallar, kod bloklari va savol-javoblarni o‘z ichiga olgan mukammal **`hisobot.docx`** faylini tayyorlab beraman!

---

<a name="ilovalar-dastlabki-kodlar"></a>
## 📂 ILOVALAR: Dastlabki Kodlar (Nusxalash uchun qulay)

<details>
<summary><b>▶ 1. app.py (Asosiy ilova kodi - bosish orqali oching)</b></summary>

```python
import hashlib
import http.client
import io
import uuid
from pathlib import Path
from urllib.parse import urlsplit
from flask import Flask, abort, jsonify, request
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 320 * 1024

ROOT = Path(__file__).resolve().parent
FILES = ROOT / 'files'
STORE = ROOT / 'storage'
STORE.mkdir(exist_ok=True)
MAX_FILE = 256 * 1024
PUBLIC_URL = 'http://127.0.0.1:8017/card'

def png_content(raw):
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.format != 'PNG':
                abort(415, description='PNG mazmuni kerak')
            if im.width * im.height > 1_000_000:
                abort(413, description='Piksel limiti oshdi')
            im.verify()
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            out = io.BytesIO()
            im.convert('RGBA').save(out, format='PNG')
        clean = out.getvalue()
        if len(clean) > 1024 * 1024:
            abort(413, description='Natija hajmi oshdi')
        return clean
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        abort(415, description='Rasm ochilmadi')
    except Image.DecompressionBombError:
        abort(413, description='Piksel limiti oshdi')

def upload_weak(raw):
    return raw

def upload_safe(raw):
    return png_content(raw)

def read_weak(name):
    target = (FILES / name).resolve()
    if not target.is_relative_to(ROOT):
        abort(403)
    return read_text(target)

def read_safe(name):
    target = (FILES / name).resolve()
    if not target.is_relative_to(FILES.resolve()):
        abort(403)
    return read_text(target)

def read_text(target):
    if not target.is_file():
        abort(404)
    if target.suffix != '.txt':
        abort(415)
    with target.open('rb') as stream:
        raw = stream.read(4097)
    if len(raw) > 4096:
        abort(413)
    return raw.decode('utf-8')

def lab_fetch(url):
    try:
        u = urlsplit(url)
        port = u.port
    except ValueError:
        abort(400)
    if (u.scheme != 'http' or u.hostname != '127.0.0.1'
            or port not in (8017, 8018)
            or u.username or u.password or u.fragment):
        abort(403)
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=2)
    try:
        path = u.path or '/'
        if u.query:
            path += '?' + u.query
        conn.request('GET', path)
        response = conn.getresponse()
        raw = response.read(4097)
        if response.status != 200 or len(raw) > 4096:
            abort(502)
        return raw.decode('utf-8')
    except (OSError, http.client.HTTPException, ValueError):
        abort(502)
    finally:
        conn.close()

def fetch_weak(url):
    return lab_fetch(url)

def fetch_safe(url):
    if url != PUBLIC_URL:
        abort(403)
    return lab_fetch(url)

@app.get('/')
def home():
    return jsonify(lab='A7 / 1-variant', services=[8017, 8018], modes=['weak', 'safe'])

@app.post('/upload/<mode>')
def upload(mode):
    if mode not in ('weak', 'safe'):
        abort(404)
    item = request.files.get('file')
    if item is None or not item.filename:
        abort(400)
    if Path(item.filename).suffix.lower() != '.png' or item.mimetype != 'image/png':
        abort(415)
    raw = item.stream.read(MAX_FILE + 1)
    if not raw:
        abort(400)
    if len(raw) > MAX_FILE:
        abort(413)
    data = upload_weak(raw) if mode == 'weak' else upload_safe(raw)
    ident = uuid.uuid4().hex + '.png'
    (STORE / ident).write_bytes(data)
    return jsonify(id=ident, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()), 201

@app.get('/read/<mode>')
def read(mode):
    if mode not in ('weak', 'safe'):
        abort(404)
    name = request.args.get('name', '')
    func = read_weak if mode == 'weak' else read_safe
    return jsonify(text=func(name))

@app.get('/fetch/<mode>')
def fetch(mode):
    if mode not in ('weak', 'safe'):
        abort(404)
    url = request.args.get('url', '')
    func = fetch_weak if mode == 'weak' else fetch_safe
    return jsonify(body=func(url))

@app.post('/preferences')
def preferences():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or set(data) != {'theme'}:
        abort(400)
    if not isinstance(data['theme'], str):
        abort(400)
    if data['theme'] not in ('light', 'dark'):
        abort(400)
    return jsonify(theme=data['theme'])

@app.errorhandler(HTTPException)
def errors(error):
    return jsonify(error=error.name), error.code

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8007, debug=False)
```
</details>

<details>
<summary><b>▶ 2. services.py (O‘quv xizmatlari kodi - bosish orqali oching)</b></summary>

```python
from threading import Thread
from flask import Flask, jsonify
from werkzeug.serving import make_server

public = Flask('public')
internal = Flask('internal')

@public.get('/card')
def card():
    return jsonify(service='catalog', product='Daftar')

@internal.get('/status')
def status():
    return jsonify(service='internal', marker='A7-INTERNAL')

if __name__ == '__main__':
    one = make_server('127.0.0.1', 8017, public)
    two = make_server('127.0.0.1', 8018, internal)
    Thread(target=one.serve_forever, daemon=True).start()
    print('Public: 8017 /card; internal: 8018 /status')
    try:
        two.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        one.shutdown()
        one.server_close()
        two.server_close()
```
</details>

<details>
<summary><b>▶ 3. prepare.py (Sinov fayllarini tayyorlovchi kod - bosish orqali oching)</b></summary>

```python
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent
for name in ('files', 'internal', 'samples'):
    (root / name).mkdir(exist_ok=True)

(root / 'files/guide.txt').write_text('A7-PUBLIC', encoding='utf-8')
(root / 'internal/demo.txt').write_text('A7-PRIVATE-FILE', encoding='utf-8')

Image.new('RGB', (32, 32), 'green').save(root / 'samples/good.png')
(root / 'samples/fake.png').write_bytes(b'NOT-A-PNG')
(root / 'samples/signature.png').write_bytes(b'\x89PNG\r\n\x1a\n' + b'NOT-AN-IMAGE')
(root / 'samples/big.png').write_bytes(b'A' * (256 * 1024 + 1))
Image.new('RGB', (1001, 1000), 'blue').save(root / 'samples/pixels.png')

print('A7 boshlangich fayllari tayyor')
```
</details>
