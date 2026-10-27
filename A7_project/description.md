# A7. Fayllar Bilan Ishlash va Server Tomon Zaifliklari
## 1-Variant: PNG Yuklash, Fayl O‘qish va Tashqi Resurs Olish Xizmatini Himoyalash

---

> **MUHIT VA ISH TARTIBI BO‘YICHA MUHIM ESLATMA:**
> 1. **Tarmoq (Wi-Fi):** Mazkur qo‘llanma **shaxsiy / lokal Wi-Fi** (to‘g‘ridan-to‘g‘ri internetga ulanish) muhiti uchun to‘liq moslashtirilgan. Universitetning ichki fayl serveri (`\\172.18.233.234\files`), universitet proksi serveri (`172.18.1.1:2500`), APT proksi konfiguratsiyasi (`/etc/apt/apt.conf.d/99proxy`) va snapd proksi sozlamalari **butunlay chiqarib tashlangan**. Barcha zarur paketlar bevosita internet orqali xavfsiz yuklab olinadi.
> 2. **Operatsion tizim va virtualizatsiya:** Barcha amallar **Ubuntu Linux (Host OS)** ustida o‘rnatilgan **VMware Workstation Pro / Player for Linux** orqali boshqariladigan **Ubuntu (Desktop yoki Server)** virtual mashinalarida bajariladi. Windows tizimiga oid buyruqlar (masalan, `Win+R`, `D:\...`, `.exe`, Windows Explorer) to‘liq chiqarib tashlanib, faqat toza Linux Bash CLI buyruqlari keltirilgan.
> 3. **CLI buyruqlar tavsifi:** Har bir Linux, Python va cURL buyrug‘ining vazifasi, qo‘llanilgan kalitlari (flags/parameters) va amaliy maqsadi qadamma-qadam batafsil tushuntirilgan.

---

## MUNDARIJA

1. [1-BO‘LIM: MAVZUNING MAQSADI VA KUTILADIGAN NATIJALAR](#1-bolim-mavzuning-maqsadi-va-kutiladigan-natijalar)
   - 1.1. Mashg‘ulotning asosiy maqsadi
   - 1.2. Kutiladigan amaliy natijalar
   - 1.3. Laboratoriya muhiti va ko‘rsatkichlari jadvali
2. [2-BO‘LIM: NAZARIY VA AMALIY TUSHUNCHALAR BO‘YICHA TO‘LIQ QO‘LLANMA](#2-bolim-nazariy-va-amaliy-tushunchalar-boyicha-toliq-qollanma)
   - 2.1. Fayl yuklash zaifligi (Unrestricted File Upload) va MIME/Kengaytma aldovi
   - 2.2. Fayl mazmunini haqiqiy tekshirish usullari (Magic Bytes, Format, Re-encoding)
   - 2.3. Resurs tugashi hujumlari (Decompression Bomb / Pixel Flood) va ikki qatlamli cheklov
   - 2.4. Katalog chegarasidan chiqish (Path Traversal / Directory Traversal) mexanizmi
   - 2.5. `resolve()` va `is_relative_to()`: To‘g‘ri katalog chegarasini aniqlash va Symlink xavfi
   - 2.6. Path Traversal va LFI (Local File Inclusion) o‘rtasidagi farq
   - 2.7. SSRF (Server-Side Request Forgery) tushunchasi, xavflari va Allowlist himoyasi
   - 2.8. SSRF va RFI (Remote File Inclusion) o‘rtasidagi farq
   - 2.9. Xavfsiz ma’lumot tiklash (Safe Deserialization): Python `pickle` xavfi va qat’iy JSON sxema tekshiruvi
3. [3-BO‘LIM: FOYDALANILADIGAN BARCHA CLI BUYRUQLAR VA ULARNING TAVSIFI](#3-bolim-foydalaniladigan-barcha-cli-buyruqlar-va-ularning-tavsifi)
   - 3.1. Tizim va xavfsizlik sozlamalari (`hostnamectl`, `umask`, `whoami`, `id`, `date`)
   - 3.2. Paketlar va Python virtual muhiti (`apt`, `python3 -m venv`, `source`, `pip`, `py_compile`)
   - 3.3. HTTP so‘rovlari va sinov vositasi (`curl` va uning barcha bayroqlari)
   - 3.4. Fayl tizimi va tekshiruv vositalari (`ln -s`, `sha256sum`, `diff`, `rm`)
4. [4-BO‘LIM: MASHQNI BAJARISH KETMA-KETLIGI (BOSQICHMA-BOSQICH)](#4-bolim-mashqni-bajarish-ketma-ketligi-bosqichma-bosqich)
   - Bosqich 0: Ubuntu Host va VMware muhitini tayyorlash (Lokal Wi-Fi orqali)
   - Bosqich 1: Loyiha katalogini tashkil qilish va Python virtual muhitini (`.venv`) yaratish
   - Bosqich 2: Dastlabki kod fayllarini yaratish (`app.py`, `services.py`, `prepare.py`)
   - Bosqich 3: Sinov fayllarini tayyorlash va xizmatlarni ishga tushirish (8007, 8017, 8018)
   - Bosqich 4: Boshlang‘ich tayyorgarlikni tekshirish va D1 dalilini olish
   - Bosqich 5: PNG fayl yuklash sinovlari (Zaif vs Xavfsiz) va D2 dalilini olish
   - Bosqich 6: Path Traversal sinovlari (Katalog chegarasi va Symlink) va D3 dalilini olish
   - Bosqich 7: SSRF sinovlari (Backend jurnali tahlili) va D4 dalilini olish
   - Bosqich 8: Uchta kod tuzatishini kiritish (`upload_weak`, `read_weak`, `fetch_weak`)
   - Bosqich 9: Regressiya sinovlari va D5 dalilini olish
   - Bosqich 10: Qo‘shimcha topshiriq: JSON sxema va xavfsiz sozlamalar (`/preferences`)
5. [5-BO‘LIM: HISOBOT JADVALI, MUAMMOLARNI BARTARAF ETISH VA NAZORAT SAVOLLARI](#5-bolim-hisobot-jadvali-muammolarni-bartaraf-etish-va-nazorat-savollari)
   - 5.1. D1–D6 dalillarining yakuniy solishtirma jadvali (Oldin va Keyin holati)
   - 5.2. Ko‘p uchraydigan muammolar va ularni bartaraf etish (Troubleshooting)
   - 5.3. Nazorat savollariga batafsil ilmiy va amaliy javoblar
6. [6-BO‘LIM: FOYDALANILGAN VA TAVSIYA ETILADIGAN MANBALAR](#6-bolim-foydalanilgan-va-tavsiya-etiladigan-manbalar)

---

## 1-BO‘LIM: MAVZUNING MAQSADI VA KUTILADIGAN NATIJALAR

### 1.1. Mashg‘ulotning asosiy maqsadi
Ushbu laboratoriya mashg‘ulotining asosiy maqsadi — zamonaviy veb-dasturlarda server tomonida (backend) fayllarni qabul qilish, saqlash, o‘qish hamda tashqi/ichki resurslar bilan bog‘lanish jarayonida yuzaga keladigan eng xavfli arxitektura va kod zaifliklarini amaliy tadqiq qilish, ularning ekspluatatsiya mexanizmlarini tushunish hamda ko‘p qatlamli himoya choralarini tatbiq etishdan iborat:

1. **Fayl nomi va MIME turining ishonchsizligi:** Mijoz (brauzer yoki hujumchi) tomonidan yuborilgan fayl kengaytmasi (`.png`) va HTTP sarlavhasidagi `Content-Type: image/png` ko‘rsatkichi uning haqiqiy ichki mazmunini kafolatlamasligini ko‘rsatish. Soxta fayllarni aniqlash uchun fayl tuzilmasini chuqur tekshirish (Magic Bytes, format tahlili, to‘liq dekodlash va qayta kodlash) zarurligini isbotlash.
2. **Katalog chegarasini (Directory Sandbox) qat’iy saqlash:** Foydalanuvchi kiritgan fayl yo‘llari orqali ruxsat etilgan ommaviy katalogdan tashqariga chiqib ketish (**Path Traversal**) xavfini o‘rganish; `resolve()` va `is_relative_to()` funksiyalaridan foydalanib, operatsion tizimning maxfiy fayllari yoki loyihaning yopiq qismlarini himoyalash.
3. **Server tomonidagi so‘rovlarni cheklash (SSRF himoyasi):** Serverning tashqi yoki ichki xizmatlar bilan aloqasini qat’iy nazorat qilish; foydalanuvchi kiritgan havolalar (URL) vositasida serverni ichki yopiq ma’muriy xizmatlarga so‘rov yuborishga majburlash (**SSRF**) holatini fosh etish va qat’iy **Allowlist** (ruxsat etilgan oq ro‘yxat) orqali ushbu tahdidni bartaraf etish.
4. **Kod darajasida xavfsizlikni kuchaytirish:** Zaif (`/weak`) va himoyalangan (`/safe`) endpointlarni o‘zaro taqqoslab, uchta asosiy funksiyada kod tuzatishlarini amalga oshirish hamda tizimning qonuniy ishlash funksionalligi buzilmaganini (regressiya sinovlari) dalillar bilan tasdiqlash.

### 1.2. Kutiladigan amaliy natijalar
Laboratoriya ishini muvaffaqiyatli yakunlagan talaba:
- Soxta PNG fayllar (`fake.png`, `signature.png`), katta hajmli fayllar (`big.png`) va dekompressiya hujumi (`pixels.png`) bilan nazorat qilinadigan sinovlarni o‘tkaza oladi;
- Noto‘g‘ri fayl yo‘llari (`../internal/demo.txt`) va ramziy bog‘lamalar (symlink) orqali katalog chegarasini buzishga urinishlarni aniqlaydi va bloklaydi;
- Ichki xizmat manziliga (`http://127.0.0.1:8018/status`) yo‘naltirilgan SSRF so‘rovlarini server backendiga ulanishidan avval to‘xtatishni dalillaydi;
- HTTP status kodlari (200, 201, 400, 403, 413, 415, 502), server saqlash joyidagi fayllar holati, SHA-256 xeshlari hamda ichki xizmat jurnali orqali o‘z xulosalarini asoslaydi;
- **Path Traversal**, **LFI (Local File Inclusion)**, **RFI (Remote File Inclusion)**, **SSRF** va **xavfsiz bo‘lmagan deserializatsiya** tushunchalarini bir-biridan aniq farqlay oladi.

### 1.3. Laboratoriya muhiti va ko‘rsatkichlari jadvali

| Ko‘rsatkich | Standart parametrlar | Talabaning joriy muhiti (Moslashtirilgan) |
| :--- | :--- | :--- |
| **Semestr / Variant** | 5-semestr / A7 / 1-variant | Faqat 5-semestr / A7 / 1-variant |
| **Ajratilgan vaqt** | 80 daqiqa (asosiy tajriba) | 80 daqiqa (tayyorgarlik alohida 30-40 daqiqa) |
| **Asosiy operatsion tizim (Host OS)** | Windows 11 | **Ubuntu Linux (x86_64 / amd64)** |
| **Virtualizatsiya vositasi** | VMware Workstation | **VMware Workstation Pro / Player for Linux** |
| **Virtual mashina (Guest OS)** | Ubuntu Desktop 24.04 LTS | **Ubuntu 24.04 LTS (Desktop yoki Server)** |
| **VM resurslari** | 4 vCPU, 8 GB RAM, 25+ GB SSD | 4 vCPU, 8 GB RAM (kamida 2 vCPU, 4 GB RAM) |
| **Tarmoq ulanishi** | Universitet LAN / Proxy (`172.18.1.1:2500`) | **Shaxsiy lokal Wi-Fi (To‘g‘ridan-to‘g‘ri internet)** |
| **Asosiy veb-ilova** | `http://127.0.0.1:8007/` | Flask API: Fayl yuklash, o‘qish, fetch, sozlamalar |
| **Ruxsat etilgan o‘quv xizmati** | `http://127.0.0.1:8017/card` | Public catalog xizmati (Qonuniy endpoint) |
| **Ichki yopiq xizmat modeli** | `http://127.0.0.1:8018/status` | Maxfiy ichki boshqaruv xizmati (`A7-INTERNAL`) |
| **Asosiy dasturiy vositalar** | Python 3, Flask 3.1.3, Pillow 11.3.0 | Python 3.12+, Flask 3.1.3, Pillow 11.3.0, cURL, Bash |
| **Topshiriladigan dalillar** | Individual hisobot, `app.py`, D1–D6 | `description.md`, tuzatilgan kod va D1–D6 jurnallari |
| **Baholash** | 10 ballik tizim | Amaliy ish natijalari va og‘zaki himoya asosida |

---

## 2-BO‘LIM: NAZARIY VA AMALIY TUSHUNCHALAR BO‘YICHA TO‘LIQ QO‘LLANMA

Laboratoriya ishidagi har bir jarayonni to‘g‘ri tushunish va xatolarga yo‘l qo‘ymaslik uchun quyidagi nazariy asoslarni o‘zlashtirish shart.

### 2.1. Fayl yuklash zaifligi (Unrestricted File Upload) va MIME/Kengaytma aldovi
Ko‘pgina veb-ishlab chiquvchilar foydalanuvchi tomonidan yuklanayotgan faylni tekshirishda faqat ikki narsaga tayanadilar:
1. Fayl nomining kengaytmasiga (masalan, `avatar.png` -> kengaytmasi `.png`);
2. HTTP so‘rovining sarlavhasida kelgan MIME turiga (`Content-Type: image/png`).

**Nega bu yondashuv o‘ta xavfli va yetarli emas?**
- **Kengaytma mijoz nazoratida:** Hujumchi ixtiyoriy zararli skriptni (masalan, PHP web-shell, Bash buyrug‘i yoki HTML/XSS kodi) olib, uning nomini shunchaki `exploit.png` deb qayta nomlashi mumkin.
- **MIME turi mijoz tomonidan yuboriladi:** `Content-Type` sarlavhasi brauzer yoki cURL orqali erkin shakllantiriladi. Agar cURL buyrug‘ida `-F "file=@fake.txt;type=image/png"` deb ko‘rsatilsa, serverga `image/png` sarlavhasi boradi, ammo fayl ichida butunlay boshqa narsa bo‘ladi.
- Ushbu laboratoriyaning `/upload/weak` endpointida aynan shu xato mavjud: u faqat `.png` kengaytmasi va `image/png` MIME turini tekshiradi, ammo fayl baytlarining haqiqiy mazmunini umuman tahlil qilmaydi. Natijada oddiy matnli `fake.png` (`NOT-A-PNG`) tizimga `201 Created` kodi bilan saqlanib qoladi.

### 2.2. Fayl mazmunini haqiqiy tekshirish usullari (Magic Bytes, Format, Re-encoding)
Haqiqiy xavfsiz tizimda fayl tekshiruvi ko‘p qatlamli (Defense-in-Depth) bo‘lishi zarur:

1. **Sehrli baytlar (Magic Bytes / File Signature):**
   Har bir standart fayl formati o‘zining boshlang‘ich baytlarida o‘ziga xos imzo saqlaydi. Masalan, PNG fayllari har doim quyidagi 8 bayt bilan boshlanadi:
   `\x89 P N G \r \n \x1a \n` (o‘n oltilik tizimda: `89 50 4E 47 0D 0A 1A 0A`).
   Lekin faqat sehrli baytlarni tekshirish ham xavfsizlikni to‘liq kafolatlamaydi! Hujumchi zararli PHP kod yoki matnning boshiga ushbu 8 baytni qo‘shib qo‘yishi mumkin (`signature.png` namunasi kabi).
2. **Kutubxona orqali strukturaviy tahlil (`im.verify()`):**
   Fayl baytlari ixtisoslashgan grafik kutubxona (Pillow) orqali xotirada ochilib, uning ichki bloklari (PNG chunklari: IHDR, IDAT, IEND) butunligi tekshiriladi. Agar fayl boshi PNG bo‘lib, davomi buzilgan bo‘lsa, `im.verify()` xatolik beradi (`UnidentifiedImageError` yoki `OSError`).
3. **Rasmni to‘liq qayta kodlash (Image Re-encoding):**
   Eng yuqori darajadagi himoya — bu foydalanuvchi yuborgan xom baytlarni to‘g‘ridan-to‘g‘ri diskka saqlamaslikdir!
   - Kod rasm piksel matritsasini to‘liq xotiraga yuklaydi (`im.load()`);
   - Yangi toza oqim ochib, uni xavfsiz formatda qayta chizadi (`im.convert("RGBA").save(out, format="PNG")`);
   - Natijada rasm ichiga yashirilgan steganografik zararli kodlar, ortiqcha metadata bloklari (EXIF, maxsus izohlar) butunlay o‘chib ketadi.
4. **Tasodifiy nom va xavfsiz katalog:**
   Yuklangan fayl foydalanuvchi bergan nom bilan emas, serverda generatsiya qilingan tasodifiy nom (`uuid.uuid4().hex + ".png"`) bilan, veb-serverning ildiz katalogidan (Web Root) tashqarida joylashgan `storage/` papkasiga saqlanadi.

### 2.3. Resurs tugashi hujumlari (Decompression Bomb / Pixel Flood) va ikki qatlamli cheklov
Fayl yuklashda faqat uning zararliligini emas, balki server resurslarini (RAM, CPU, Disk) sarflashini ham cheklash lozim.

- **Fayl bayt hajmi (Network & Disk limit):**
  Tizimda `MAX_FILE = 256 * 1024` (256 KB) limiti o‘rnatilgan. Agar yuklangan fayl hajmi 256 KB dan oshsa, server uni qabul qilmaydi (`413 Payload Too Large`).
- **Piksel dekompressiya bombasi (RAM & CPU limit):**
  PNG siqilgan (compressed) formatdir. Hujumchi hajmi bor-yo‘g‘i 10–20 KB bo‘lgan, lekin ochilganda 100 000 × 100 000 pikselga aylanadigan rasm yuborishi mumkin. Bunday fayl xotirada dekompressiya qilinganda gigabaytlab operativ xotirani (RAM) egallaydi va serverda `Out-Of-Memory (OOM)` yoki `DecompressionBombError` keltirib chiqaradi.
- Shuning uchun kodda **ikki mustaqil limit** qo‘llaniladi:
  1. Bayt hajmi tekshiruvi: `len(raw) > MAX_FILE` -> 413;
  2. Piksel soni tekshiruvi: `im.width * im.height > 1_000_000` (1 megapiksel) -> 413.

### 2.4. Katalog chegarasidan chiqish (Path Traversal / Directory Traversal) mexanizmi
Path Traversal zaifligi dastur foydalanuvchi kiritgan fayl yo‘li parametrini yetarlicha filtrlamay, fayl tizimidagi boshqa kataloglarga murojaat qilishiga yo‘l qo‘yganida paydo bo‘ladi.
- Hujumchi yo‘lni orqaga qaytaruvchi `../` (dot-dot-slash) ketma-ketligidan foydalanadi.
- Masalan, agar ruxsat etilgan katalog `/home/user/websec/A7/files/` bo‘lsa, foydalanuvchi `name="../internal/demo.txt"` deb so‘rov yuborsa, operatsion tizim yo‘lni `/home/user/websec/A7/internal/demo.txt` deb hisoblaydi va maxfiy ma’lumotni ochib beradi.

### 2.5. `resolve()` va `is_relative_to()`: To‘g‘ri katalog chegarasini aniqlash va Symlink xavfi
Pythonning zamonaviy `pathlib` kutubxonasida yo‘llarni tekshirish uchun maxsus xavfsizlik funksiyalari mavjud:
1. `Path.resolve()`: Yo‘l tarkibidagi barcha nisbiy elementlarni (`.` va `..`) hamda ramziy bog‘lamalarni (symlinks) yechib, faylning operatsion tizimdagi **haqiqiy, to‘liq (kanonik) mutlaq manzilini** hosil qiladi.
2. `Path.is_relative_to(base)`: Berilgan yo‘l aynan `base` katalogi ichida yoki uning quyi qismida joylashganini mantiqiy tekshiradi (`True` yoki `False`).

**Zaif kodning xatosi:**
```python
# Zaif kod (app.py read_weak):
target = (FILES / name).resolve()
if not target.is_relative_to(ROOT):
    abort(403)
```
Zaif kod tekshirish chegarasini butun loyiha ildizi (`ROOT = ~/websec/A7`) deb belgilagan! Hujumchi `../internal/demo.txt` yuborganida, `resolve()` amalidan so‘ng fayl `files/` dan tashqariga chiqadi, ammo hali ham `ROOT` ichida bo‘lgani sababli `is_relative_to(ROOT)` `True` qaytaradi va maxfiy fayl o‘qiladi!

**To‘g‘ri va xavfsiz kod:**
```python
# Xavfsiz kod (app.py read_safe):
target = (FILES / name).resolve()
if not target.is_relative_to(FILES.resolve()):
    abort(403)
```
Bu yerda chegara qat’iy ravishda `FILES.resolve()` (`~/websec/A7/files`) ga qisqartirilgan. Agar foydalanuvchi hatto `files/link.txt` nomli symlink orqali `internal/demo.txt` ga ulanishga urinsa ham, `resolve()` funksiyasi haqiqiy nishon `internal/demo.txt` ekanini ochib tashlaydi va `is_relative_to(FILES.resolve())` `False` bo‘lib, zudlik bilan `403 Forbidden` xatosi qaytariladi.

### 2.6. Path Traversal va LFI (Local File Inclusion) o‘rtasidagi farq
Ushbu ikki tushunchani chalkashtirmaslik o‘ta muhim:
- **Path Traversal (Katalog chegarasidan chiqish):** Dastur faylni oddiy ma’lumot (matn yoki oqim) sifatida o‘qiydi (`file.read()`) va uning mazmunini foydalanuvchiga uzatadi. Bu yerda server kodni **bajarishi (execute)** yuz bermaydi.
- **LFI (Local File Inclusion):** Dastur ko‘rsatilgan mahalliy faylni o‘zining bajarilayotgan muhitiga qo‘shib oladi (masalan, PHPdagi `include($_GET["page"])` yoki Pythondagi dinamik `__import__()`). Agar yuklangan yoki o‘qilgan fayl ichida dasturlash kodi bo‘lsa, u serverda to‘g‘ridan-to‘g‘ri ishga tushib, **Remote Code Execution (RCE)** ga olib keladi.
- *Xulosa:* Ushbu A7 laboratoriya ishida fayl faqat `read_text()` orqali matn sifatida o‘qiladi, shuning uchun bu holat **LFI emas, balki sof Path Traversal** hisoblanadi.

### 2.7. SSRF (Server-Side Request Forgery) tushunchasi, xavflari va Allowlist himoyasi
**SSRF** — bu hujumchi zaif veb-server nomidan boshqa ichki yoki tashqi tarmoq resurslariga noqonuniy so‘rovlar (odatda HTTP GET/POST) yuborishga erishadigan zaiflikdir.

**SSRF qanday xavf tug‘diradi?**
- Ko‘p tarmoqlarda ichki serverlar, ma’lumotlar bazalari, kesh tizimlari (Redis) yoki ma’muriy boshqaruv panellari faqat lokal interfeysda (`127.0.0.1`) yoki ichki tarmoqda (`10.x.x.x`, `192.168.x.x`) ishlaydi va tashqi internetdan yopiq bo‘ladi.
- Bulutli muhitlarda (AWS, GCP, Azure) maxsus metadata xizmatlari mavjud (masalan, `http://169.254.169.254/latest/meta-data/`).
- Agar tashqi foydalanuvchi serverga `url=http://127.0.0.1:8018/status` kabi manzilni uzatsa va server uni o‘z nomidan chaqirib natijani qaytarsa, tashqi hujumchi ichki maxfiy tizimlarga kirish imkoniga ega bo‘ladi.

**Himoyalanish usullari:**
1. **Qat’iy Allowlist (Oq ro‘yxat):** Agar server ma’lum bir ichki xizmat bilan ishlashi kerak bo‘lsa, ruxsat etilgan URLlar ro‘yxati qat’iy cheklanadi. Ushbu laboratoriyada yagona ruxsat etilgan manzil — `PUBLIC_URL = "http://127.0.0.1:8017/card"`. Har qanday boshqa URL (shu jumladan `8018/status`) server tomonidan ulanish hosil qilinmasdan avval `403 Forbidden` bilan rad etiladi.
2. **DNS Rebinding va IP doiralarini tekshirish:** Ommaviy internetdan URL qabul qiluvchi ilovalarda domen nomi ichki IP doiralariga (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`) yo‘naltirilmagani qat’iy tekshiriladi.
3. **Redirectlarni taqiqlash:** HTTP 3xx yo‘naltirishlar avtomatik kuzatilmaydi.

### 2.8. SSRF va RFI (Remote File Inclusion) o‘rtasidagi farq
- **SSRF:** Server tashqi/ichki resursga HTTP so‘rovi yuboradi va uning javobini matn/ma’lumot ko‘rinishida qabul qiladi. Bu javob dastur kodi sifatida bajarilmaydi.
- **RFI (Remote File Inclusion):** Server begona masofaviy serverdan (masalan, `http://attacker.com/malicious.txt`) fayl yuklab olib, uni o‘zining kod oqimiga modul yoki skript sifatida kiritadi va ishga tushiradi (`include "http://..."`).
- *Xulosa:* Laboratoriyada `/fetch/weak` xizmati HTTP javobini faqat JSON ichida matn sifatida qaytaradi, kodni ijro etmaydi. Demak, bu **RFI emas, balki SSRF** holatidir.

### 2.9. Xavfsiz ma’lumot tiklash (Safe Deserialization): Python `pickle` xavfi va qat’iy JSON sxema tekshiruvi
Ko‘pgina dasturlarda obyektlarni saqlash yoki uzatish uchun deserializatsiya qo‘llaniladi.

- **Python `pickle` xavfi:**
  Pythonning standart `pickle` moduli obyektlar holatini ikkilik formatda saqlaydi. Ammo `pickle` tiklanayotgan vaqtda obyektning maxsus `__reduce__` metodini chaqirish xususiyatiga ega. Hujumchi maxsus soxtalashtirilgan baytlar oqimini yuborsa, `pickle.loads()` serverda operatsion tizim buyruqlarini (masalan, `os.system("rm -rf /")`) bevosita ishga tushirishi mumkin (RCE zaifligi).
- **Xavfsiz yondashuv — JSON:**
  JSON faqat matnli ma’lumot almashish formati bo‘lib, o‘zida bajariladigan kod yoki funksiyalarni saqlamaydi.
- **JSON sxemasini tekshirish (Schema Validation):**
  Faqat JSON ishlatishning o‘zi yetarli emas. Hujumchi JSON orqali kutilmagan parametrlar (masalan, `{"admin": true}`) yoki kutilmagan turlar yuborishi mumkin. Shu sababli `/preferences` endpointida qat’iy tekshiruv qo‘llaniladi:
  - Kelgan ma’lumot faqat lug‘at (`dict`) bo‘lishi shart;
  - Unda faqat `theme` kaliti mavjud bo‘lishi lozim (`set(data) == {"theme"}`);
  - Qiymati satr (`str`) bo‘lishi va faqat `"light"` yoki `"dark"` bo‘lishi ruxsat etiladi.

---

## 3-BO‘LIM: FOYDALANILADIGAN BARCHA CLI BUYRUQLAR VA ULARNING TAVSIFI

Ushbu laboratoriya mashg‘ulotida ishlatiladigan har bir Linux Bash va cURL buyrug‘i, ularning argumentlari va kalitlari quyida to‘liq izohlangan.

### 3.1. Tizim va xavfsizlik sozlamalari buyruqlari

```bash
sudo hostnamectl set-hostname veb-a7-lab
```
- **Vazifasi:** Virtual mashina kompyuter nomini (hostname) o‘zgartiradi.
- **Parametrlar:** `set-hostname veb-a7-lab` — tizimga `veb-a7-lab` nomini belgilaydi. Bu hisobotlarda individual laboratoriya nusxasini ajratib ko‘rsatish uchun kerak.

```bash
whoami; id; sudo -v; date -Is
```
- **Vazifasi:** Joriy foydalanuvchi nomi, uning UID/GID guruhlari, sudo huquqi faolligi va aniq vaqt tamg‘asini (ISO 8601 formatida) ko‘rsatadi. Dalillarni qayd etishda tizim holatini hujjatlashtirish uchun xizmat qiladi.

```bash
umask 077
```
- **Vazifasi:** Joriy terminal sessiyasida yaratiladigan yangi fayllar va kataloglar uchun birlamchi ruxsat huquqlarini (file permission mask) cheklaydi.
- **Natijasi:** `077` maskasi orqali yangi yaratilgan fayllarga faqat egasi (user) uchun o‘qish/yozish huquqi beriladi (`-rw-------`), boshqa foydalanuvchilar va guruhlar uchun esa kirish butunlay taqiqlanadi. Bu `storage/` katalogida saqlanadigan fayllarni mahalliy tizimdagi begona jarayonlardan himoyalaydi.

### 3.2. Paketlar va Python virtual muhiti buyruqlari

```bash
sudo apt update
```
- **Vazifasi:** Ubuntu repozitoriylaridagi paketlar ro‘yxati va ularning so‘nggi versiyalari haqidagi indeks ma’lumotlarini yangilaydi (to‘g‘ridan-to‘g‘ri shaxsiy Wi-Fi orqali).

```bash
sudo apt install -y python3 python3-venv python3-pip curl nano
```
- **Vazifasi:** Laboratoriya ishi uchun zarur bo‘lgan tizim paketlarini o‘rnatadi:
  - `python3` — Python 3 interpretatori;
  - `python3-venv` — mustaqil virtual muhitlarni yaratish moduli;
  - `python3-pip` — Python paketlar menejeri;
  - `curl` — HTTP/HTTPS so‘rovlarini terminaldan yuborish vositasi;
  - `nano` — konsol matn muharriri;
  - `-y` — o‘rnatish jarayonida so‘raladigan tasdiqlash savoliga avtomatik "Ha" (Yes) deb javob beradi.

```bash
python3 -m venv .venv
```
- **Vazifasi:** Loyiha papkasida `.venv` nomli ajratilgan, xavfsiz virtual muhit katalogini yaratadi. Tizimning asosiy Python muhitiga aralashmasdan alohida kutubxonalarni o‘rnatish imkonini beradi.

```bash
source .venv/bin/activate
```
- **Vazifasi:** Yaratilgan virtual muhitni joriy terminalda faollashtiradi (terminal oldida `(.venv)` belgisi paydo bo‘ladi).

```bash
python -m pip install Flask==3.1.3 Pillow==11.3.0
```
- **Vazifasi:** Virtual muhit ichiga qat’iy belgilangan barqaror versiyalardagi paketlarni o‘rnatadi:
  - `Flask==3.1.3` — veb-ilovalar va API yaratish uchun mikrofreyvmork;
  - `Pillow==11.3.0` — tasvirlarni ochish, tahlil qilish, formatini tekshirish va qayta kodlash kutubxonasi.

```bash
python -m pip freeze > requirements-lock.txt
```
- **Vazifasi:** Virtual muhitga o‘rnatilgan barcha paketlar va ularning aniq bog‘liqliklarini (dependencies) `requirements-lock.txt` fayliga saqlaydi.

```bash
python -m py_compile app.py services.py prepare.py
```
- **Vazifasi:** Yozilgan Python skriptlarining sintaksisini oldindan tekshiradi (kompilyatsiya qiladi). Dasturda chekinish (indentation) yoki sintaktik xato bo‘lsa, uni serverni ishga tushirishdan oldin ko‘rsatadi.

### 3.3. HTTP so‘rovlari va sinov vositasi (`curl`) buyruqlari

```bash
curl --noproxy "*" -i http://127.0.0.1:8007/
```
- **Vazifasi:** Asosiy ilovaning bosh sahifasiga GET so‘rovini yuboradi.
- **Parametrlar:**
  - `--noproxy "*"` — ushbu so‘rov uchun har qanday tizim yoki muhit proksisini chetlab o‘tib, bevosita lokal tarmoq orqali ulanishni ta’minlaydi;
  - `-i` (include) — server qaytargan HTTP javob sarlavhalarini (Status code, Content-Type va h.k.) javob tanasi (body) bilan birga terminalda ko‘rsatadi.

```bash
curl --noproxy "*" -i http://127.0.0.1:8007/upload/weak \
  -F "file=@samples/fake.png;type=image/png"
```
- **Vazifasi:** Zaif yuklash manziliga (`/upload/weak`) soxta faylni yuboradi.
- **Parametrlar:**
  - `-F` (form-data) — so‘rovni `multipart/form-data` formatida yuboradi (fayl yuklash standarti);
  - `@samples/fake.png` — lokal diskdagi faylni o‘qib serverga jo‘natadi (`@` belgisi fayldan o‘qishni bildiradi);
  - `;type=image/png` — mijoz tomonidan soxtalashtirilgan MIME sarlavhasini belgilaydi.

```bash
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/weak \
  --data-urlencode "name=../internal/demo.txt"
```
- **Vazifasi:** Fayl o‘qish endpointiga Path Traversal yuklamasini yuboradi.
- **Parametrlar:**
  - `-G` — berilgan ma’lumotlarni POST o‘rniga GET URL parametriga (`?name=...`) aylantiradi;
  - `--data-urlencode` — kiritilgan parametrdagi maxsus belgilar (`..`, `/`) ni xavfsiz URL-kodlangan shaklga (`%2E%2E%2F`) avtomatik o‘tkazib jo‘natadi.

```bash
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/weak \
  --data-urlencode "url=http://127.0.0.1:8018/status"
```
- **Vazifasi:** Resurs olish xizmatiga ichki xizmat manzilini uzatib, SSRF zaifligini tekshiradi.

```bash
curl --noproxy "*" -i http://127.0.0.1:8007/preferences \
  -H "Content-Type: application/json" \
  -d '{"theme":"dark"}'
```
- **Vazifasi:** `/preferences` endpointiga JSON formatida parametr jo‘natadi.
- **Parametrlar:**
  - `-H "Content-Type: application/json"` — so‘rov tanasi JSON formatida ekanini serverga bildiradi;
  - `-d '...'` — HTTP POST so‘rovining tanasida yuboriladigan xom ma’lumot.

### 3.4. Fayl tizimi va xavfsizlik nazorati buyruqlari

```bash
ln -s ../internal/demo.txt files/link.txt
```
- **Vazifasi:** `files/` papkasi ichida `link.txt` nomli yangi ramziy bog‘lama (symbolic link) yaratadi. Bu bog‘lama ruxsat etilgan papkadan tashqaridagi `../internal/demo.txt` fayliga ishora qiladi.

```bash
rm files/link.txt
```
- **Vazifasi:** Faqat yaratilgan ramziy bog‘lamani o‘chiradi. Haqiqiy nishon fayl (`internal/demo.txt`) daxlsiz qoladi.

```bash
sha256sum storage/<fayl-id>.png
```
- **Vazifasi:** `storage/` papkasida saqlangan faylning kriptografik SHA-256 xesh qiymatini hisoblaydi. Bu API qaytargan xesh bilan diskdagi fayl xeshining bir xilligini tasdiqlash imkonini beradi.

```bash
diff -u app_before.py app.py
```
- **Vazifasi:** Boshlang‘ich kod (`app_before.py`) bilan tuzatilgan kod (`app.py`) orasidagi farqni unifikatsiyalangan diff formatida ko‘rsatadi (D5 dalili uchun).

---

## 4-BO‘LIM: MASHQNI BAJARISH KETMA-KETLIGI (BOSQICHMA-BOSQICH)

Ushbu bo‘limda laboratoriya mashg‘ulotini boshidan oxirigacha mukammal bajarish ketma-ketligi qadamma-qadam keltirilgan.

### Bosqich 0: Ubuntu Host va VMware muhitini tayyorlash (Lokal Wi-Fi orqali)
1. Asosiy kompyuteringiz (Host OS) Ubuntu tizimida ekanini va shaxsiy Wi-Fi tarmog‘ingiz orqali internetga to‘g‘ridan-to‘g‘ri chiqish mavjudligini tekshiring:
   ```bash
   ping -c 3 google.com
   ```
2. VMware Workstation / Player dasturini oching va laboratoriya uchun ajratilgan Ubuntu 24.04 (Desktop yoki Server) virtual mashinasini ishga tushiring.
3. Virtual mashina sozlamalarida tarmoq adapteri **NAT** rejimida ekaniga ishonch hosil qiling (shunda VM shaxsiy Wi-Fi internetingizdan to‘g‘ridan-to‘g‘ri foydalanadi).
4. Virtual mashina ichida terminal ochib, tizim identifikatorini o‘rnating:
   ```bash
   sudo hostnamectl set-hostname veb-a7-lab
   whoami
   id
   sudo -v
   date -Is
   ```

### Bosqich 1: Loyiha katalogini tashkil qilish va Python virtual muhitini yaratish
Barcha operatsiyalar uy katalogidagi `~/websec/A7` papkasida bajariladi.

```bash
# 1. Tizim paketlarini yangilash va o'rnatish
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl nano

# 2. Ishchi kataloglar tuzilmasini yaratish
mkdir -p ~/websec/A7/evidence
cd ~/websec/A7

# 3. Python virtual muhitini (.venv) hosil qilish va faollashtirish
python3 -m venv .venv
source .venv/bin/activate

# 4. Kerakli versiyadagi paketlarni o'rnatish
python -m pip install Flask==3.1.3 Pillow==11.3.0

# 5. Paketlar ro'yxatini qayd qilish
python -m pip freeze > requirements-lock.txt
```

### Bosqich 2: Dastlabki kod fayllarini yaratish (`app.py`, `services.py`, `prepare.py`)
`~/websec/A7` katalogida quyidagi uchta faylni yarating.

#### 1. `app.py` fayli:
Ushbu fayl laboratoriyaning asosiy veb-ilovasi bo‘lib, fayl yuklash, o‘qish, tashqi resurs olish va sozlamalar endpointlarini taqdim etadi:

```bash
cat << 'EOF' > app.py
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
    return jsonify(lab='A7 / 1-variant',
                   services=[8017, 8018], modes=['weak', 'safe'])

@app.post('/upload/<mode>')
def upload(mode):
    if mode not in ('weak', 'safe'):
        abort(404)
    item = request.files.get('file')
    if item is None or not item.filename:
        abort(400)
    if (Path(item.filename).suffix.lower() != '.png'
            or item.mimetype != 'image/png'):
        abort(415)
    raw = item.stream.read(MAX_FILE + 1)
    if not raw:
        abort(400)
    if len(raw) > MAX_FILE:
        abort(413)
    data = upload_weak(raw) if mode == 'weak' else upload_safe(raw)
    ident = uuid.uuid4().hex + '.png'
    (STORE / ident).write_bytes(data)
    return jsonify(id=ident, bytes=len(data),
                   sha256=hashlib.sha256(data).hexdigest()), 201

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
EOF
```

#### 2. `services.py` fayli:
Ushbu skript ikkita yordamchi xizmatni bitta oqimda ishga tushiradi:
- 8017-port: ommaviy `/card` katalog xizmati (qonuniy target);
- 8018-port: ichki `/status` xizmati (maxfiy ma’muriy xizmat).

```bash
cat << 'EOF' > services.py
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
EOF
```

#### 3. `prepare.py` fayli:
Tajriba uchun barcha sun’iy test namunalarini avtomatik generatsiya qiladi:

```bash
cat << 'EOF' > prepare.py
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent
for name in ('files', 'internal', 'samples'):
    (root / name).mkdir(exist_ok=True)

(root / 'files/guide.txt').write_text('A7-PUBLIC', encoding='utf-8')
(root / 'internal/demo.txt').write_text('A7-PRIVATE-FILE', encoding='utf-8')

# 1. Haqiqiy to'g'ri PNG (32x32)
Image.new('RGB', (32, 32), 'green').save(root / 'samples/good.png')

# 2. Soxta PNG (aslida matn)
(root / 'samples/fake.png').write_bytes(b'NOT-A-PNG')

# 3. Sehrli baytlari bor, lekin buzilgan rasm
(root / 'samples/signature.png').write_bytes(
    b'\x89PNG\r\n\x1a\n' + b'NOT-AN-IMAGE'
)

# 4. Hajmi oshirilgan fayl (256KB + 1 bayt)
(root / 'samples/big.png').write_bytes(b'A' * (256 * 1024 + 1))

# 5. Piksel dekompressiya bombasi (1 001 000 piksel)
Image.new('RGB', (1001, 1000), 'blue').save(root / 'samples/pixels.png')

print('A7 boshlangich fayllari tayyor')
EOF
```

### Bosqich 3: Sinov fayllarini tayyorlash va xizmatlarni ishga tushirish (8007, 8017, 8018)

1. Sintaksisni tekshirish, namunalarni generatsiya qilish va boshlang‘ich kod nusxasini saqlash:
   ```bash
   cd ~/websec/A7
   source .venv/bin/activate
   python -m py_compile app.py services.py prepare.py
   python prepare.py
   cp app.py app_before.py
   ```

2. Yangi fayllar huquqini cheklash va **1-Terminalda** asosiy serverni ishga tushirish:
   ```bash
   umask 077
   python app.py
   ```
   *(Ushbu terminal ochiq turadi va 8007-portdagi so‘rovlar jurnalini ko‘rsatib turadi).*

3. Virtual mashinada **2-Terminalni** ochib, yordamchi xizmatlarni ishga tushiring:
   ```bash
   cd ~/websec/A7
   source .venv/bin/activate
   python services.py
   ```
   *(Ushbu terminal ham ochiq turadi va 8017 hamda 8018 portlaridagi so‘rovlarni qayd etadi).*

4. Virtual mashinada **3-Terminalni** oching. Barcha sinov buyruqlari aynan shu 3-terminalda bajariladi:
   ```bash
   cd ~/websec/A7
   source .venv/bin/activate
   ```

### Bosqich 4: Boshlang‘ich tayyorgarlikni tekshirish va D1 dalilini olish
Barcha uchta xizmatning loopback interfeysida normal ishlayotganini tekshiring:

```bash
# Asosiy API tekshiruvi (8007)
curl --noproxy "*" -i http://127.0.0.1:8007/

# Ommaviy katalog xizmati tekshiruvi (8017)
curl --noproxy "*" -i http://127.0.0.1:8017/card

# Ichki yopiq xizmat modeli tekshiruvi (8018)
curl --noproxy "*" -i http://127.0.0.1:8018/status
```

**Kutiladigan natija (D1 dalili):**
- Uchala so‘rovga ham `HTTP/1.1 200 OK` qaytadi;
- 8007 javobida: `{"lab":"A7 / 1-variant","modes":["weak","safe"],"services":[8017,8018]}`;
- 8017 javobida: `{"product":"Daftar","service":"catalog"}`;
- 8018 javobida: `{"marker":"A7-INTERNAL","service":"internal"}`.

### Bosqich 5: PNG fayl yuklash sinovlari (Zaif vs Xavfsiz) va D2 dalilini olish

#### 1. Dastlabki solishtirish:
```bash
# 1. Haqiqiy PNG yuklash (zaif endpoint)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/weak \
  -F "file=@samples/good.png;type=image/png"

# 2. Soxta PNG yuklash (zaif endpoint)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/weak \
  -F "file=@samples/fake.png;type=image/png"

# 3. Soxta PNG yuklash (xavfsiz endpoint)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe \
  -F "file=@samples/fake.png;type=image/png"
```

**Tahlil:**
- 1-so‘rov: `HTTP/1.1 201 Created` — fayl saqlanadi.
- 2-so‘rov: `HTTP/1.1 201 Created` — `fake.png` oddiy matn bo‘lsa ham `bytes: 9` bilan saqlanib qoladi (zaiflik tasdiqlandi!).
- 3-so‘rov: `HTTP/1.1 415 Unsupported Media Type` — xavfsiz endpoint faylni rasm sifatida ocholmaydi va uni rad etadi.

#### 2. Qolgan namunalarni xavfsiz endpointda sinash:
```bash
# Faqat imzo baytlari bor buzilgan rasm (kutiladi: 415)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe \
  -F "file=@samples/signature.png;type=image/png"

# Hajmi 256KB dan oshgan fayl (kutiladi: 413)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe \
  -F "file=@samples/big.png;type=image/png"

# Piksel soni 1 000 000 dan oshgan dekompressiya bombasi (kutiladi: 413)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe \
  -F "file=@samples/pixels.png;type=image/png"

# Haqiqiy PNG (kutiladi: 201)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe \
  -F "file=@samples/good.png;type=image/png"
```

#### 3. Tasodifiy ID va xesh yaxlitligini tekshirish:
`good.png` ni `/upload/safe` ga yana bir bor yuboring:
```bash
curl --noproxy "*" -i http://127.0.0.1:8007/upload/safe \
  -F "file=@samples/good.png;type=image/png"
```
Qaytgan JSON dagi `id` qiymatini oling (masalan, `e4b3...png`). So‘ngra `storage/` papkasidagi fayl xeshini solishtiring:
```bash
sha256sum storage/<qaytgan-id>
```
*(Burchak qavslarsiz, real fayl nomi yoziladi. Masalan: `sha256sum storage/e4b3a1...png`).*
Qaytarilgan xesh JSON dagi `sha256` qiymati bilan aynan bir xil bo‘lishi zarur (D2 dalili).

### Bosqich 6: Path Traversal sinovlari va D3 dalilini olish

```bash
# 1. Ruxsat etilgan ochiq faylni o'qish (zaif endpoint)
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/weak \
  --data-urlencode "name=guide.txt"

# 2. Katalogdan tashqariga chiqib maxfiy faylni o'qish (zaif endpoint)
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/weak \
  --data-urlencode "name=../internal/demo.txt"

# 3. Xuddi shu urinish xavfsiz endpointda
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/safe \
  --data-urlencode "name=../internal/demo.txt"

# 4. Qonuniy faylni xavfsiz endpointda o'qish
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/safe \
  --data-urlencode "name=guide.txt"
```

**Tahlil:**
- 1-so‘rov: `HTTP 200 OK`, `text: "A7-PUBLIC"` (qonuniy amal);
- 2-so‘rov: `HTTP 200 OK`, `text: "A7-PRIVATE-FILE"` (zaiflik! `internal/` katalogidagi yopiq ma’lumot sizdirildi);
- 3-so‘rov: `HTTP 403 Forbidden` (xavfsiz endpoint katalog chegarasidan chiqishni to‘xtatdi);
- 4-so‘rov: `HTTP 200 OK`, `text: "A7-PUBLIC"` (qonuniy foydalanuvchi ishlashda davom etmoqda).

#### Symlink (Ramziy bog‘lama) bo‘yicha tekshiruv:
```bash
# Ramziy bog'lama yaratish
ln -s ../internal/demo.txt files/link.txt

# Xavfsiz endpoint orqali murojaat qilish
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/safe \
  --data-urlencode "name=link.txt"

# Sinovdan so'ng symlinkni o'chirib tashlash
rm files/link.txt
```
**Natija:** Server `HTTP 403 Forbidden` qaytaradi. Sababi `resolve()` funksiyasi symlink ortidagi haqiqiy manzil `internal/demo.txt` ekanini aniqlaydi va `is_relative_to(FILES.resolve())` shartidan o‘tkazmaydi (D3 dalili).

### Bosqich 7: SSRF sinovlari (Backend jurnali tahlili) va D4 dalilini olish

Ushbu bosqichda so‘rov yuborish bilan birga **2-Terminaldagi** jurnallarni kuzatib turing:

```bash
# 1. Qonuniy tashqi resursni olish (zaif endpoint)
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/weak \
  --data-urlencode "url=http://127.0.0.1:8017/card"

# 2. SSRF hujumi: Ichki maxfiy xizmat manzilini uzatish (zaif endpoint)
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/weak \
  --data-urlencode "url=http://127.0.0.1:8018/status"

# 3. Xuddi shu SSRF urinishi xavfsiz endpointda
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/safe \
  --data-urlencode "url=http://127.0.0.1:8018/status"

# 4. Qonuniy manzil xavfsiz endpointda
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/safe \
  --data-urlencode "url=http://127.0.0.1:8017/card"
```

**Tahlil va Backend jurnali (D4 dalili):**
- 1-so‘rovda: `HTTP 200 OK`, body ichida `catalog` va `Daftar` qaytadi. 2-terminalda `GET /card` yozuvi paydo bo‘ladi.
- 2-so‘rovda: `HTTP 200 OK`, body ichida `A7-INTERNAL` markeri qaytadi! 2-terminalda `GET /status 200` yozuvi chiqadi (SSRF muvaffaqiyatli amalga oshdi!).
- 3-so‘rovda: `HTTP 403 Forbidden` qaytadi. **Eng muhimi:** 2-terminalda hech qanday yangi `GET /status` so‘rovi paydo bo‘lmaydi! Bu shuni isbotlaydiki, xavfsiz kod so‘rovni backendga yuborishdan oldin bloklagan.
- 4-so‘rovda: `HTTP 200 OK` qonuniy ishlaydi.

### Bosqich 8: Uchta kod tuzatishini kiritish (`upload_weak`, `read_weak`, `fetch_weak`)

Asosiy maqsad — `/weak` endpointlarining ichki funksiyalarini to‘g‘rilab, zaifliklarni bartaraf etish:
1. **1-Terminalda** ishlayotgan asosiy serverni `Ctrl+C` bilan to‘xtating.
2. `nano app.py` orqali quyidagi uchta funksiyani almashtiring:

**1-tuzatish (Fayl mazmunini to‘liq tekshirish va qayta kodlash):**
```python
def upload_weak(raw):
    return png_content(raw)
```

**2-tuzatish (Katalog chegarasini faqat FILES papkasiga qisqartirish):**
```python
def read_weak(name):
    target = (FILES / name).resolve()
    if not target.is_relative_to(FILES.resolve()):
        abort(403)
    return read_text(target)
```

**3-tuzatish (URL manzilini qat’iy tenglik bilan tekshirish):**
```python
def fetch_weak(url):
    if url != PUBLIC_URL:
        abort(403)
    return lab_fetch(url)
```

3. Kod sintaksisini tekshiring va serverni qayta ishga tushiring:
   ```bash
   python -m py_compile app.py
   python app.py
   ```

4. 3-Terminalda kod o‘zgarishlarini tekshiring (D5 dalili uchun):
   ```bash
   diff -u app_before.py app.py
   ```

### Bosqich 9: Regressiya sinovlari va D5 dalilini olish
Endi avval zaif bo‘lgan `/weak` endpointlarini qaytadan sinovdan o‘tkazamiz:

```bash
# 1. Soxta faylni yuklash endi rad etilishi kerak (kutiladi: 415)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/weak \
  -F "file=@samples/fake.png;type=image/png"

# 2. Qonuniy fayl hali ham muvaffaqiyatli yuklanishi kerak (kutiladi: 201)
curl --noproxy "*" -i http://127.0.0.1:8007/upload/weak \
  -F "file=@samples/good.png;type=image/png"

# 3. Path Traversal endi rad etilishi kerak (kutiladi: 403)
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/weak \
  --data-urlencode "name=../internal/demo.txt"

# 4. Qonuniy fayl o'qilishi saqlanishi kerak (kutiladi: 200)
curl --noproxy "*" -i -G http://127.0.0.1:8007/read/weak \
  --data-urlencode "name=guide.txt"

# 5. SSRF urinishi endi rad etilishi kerak (kutiladi: 403)
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/weak \
  --data-urlencode "url=http://127.0.0.1:8018/status"

# 6. Qonuniy URL fetch qilinishi saqlanishi kerak (kutiladi: 200)
curl --noproxy "*" -i -G http://127.0.0.1:8007/fetch/weak \
  --data-urlencode "url=http://127.0.0.1:8017/card"
```
**Xulosa:** Barcha zaif yo‘llar endi to‘g‘ri himoyalandi (415 va 403), barcha qonuniy funksiyalar esa o‘z ishini buzilmasdan davom ettirmoqda (201 va 200). Bu regressiya xatolari yo‘qligini tasdiqlaydi.

### Bosqich 10: Qo‘shimcha topshiriq: JSON sxema va xavfsiz sozlamalar (`/preferences`)
Ushbu sinov orqali deserializatsiya va ma’lumotlar yaxlitligini tekshiramiz:

```bash
# 1. Qonuniy sozlama yuborish (kutiladi: 200 OK)
curl --noproxy "*" -i http://127.0.0.1:8007/preferences \
  -H "Content-Type: application/json" \
  -d '{"theme":"dark"}'

# 2. Ichki murakkab obyekt yuborish (kutiladi: 400 Bad Request)
curl --noproxy "*" -i http://127.0.0.1:8007/preferences \
  -H "Content-Type: application/json" \
  -d '{"theme":{"name":"dark"}}'

# 3. Kutilmagan begona maydon qo'shib yuborish (kutiladi: 400 Bad Request)
curl --noproxy "*" -i http://127.0.0.1:8007/preferences \
  -H "Content-Type: application/json" \
  -d '{"theme":"dark","admin":true}'
```
Ushbu natijalar ilova JSON qabul qilish bilan birga, uning qat’iy sxemasini ham to‘liq nazorat qilayotganini ko‘rsatadi.

---

## 5-BO‘LIM: HISOBOT JADVALI, MUAMMOLARNI BARTARAF ETISH VA NAZORAT SAVOLLARI

### 5.1. D1–D6 dalillarining yakuniy solishtirma jadvali (Oldin va Keyin holati)

Laboratoriya hisobotini tayyorlashda quyidagi D6 yakuniy jadvalini amaliy natijalaringiz bilan to‘ldiring:

| Sinov operatsiyasi | Oldin (`/weak` boshlang‘ich) | Keyin (`/weak` tuzatilgach) | Amaldagi dalil tavsifi |
| :--- | :--- | :--- | :--- |
| **`good.png` yuklash** | `201 Created` | `201 Created` | Yangi UUID fayl yaratildi, SHA-256 xesh to‘g‘ri |
| **`fake.png` yuklash** | `201 Created; 9 bayt` | `415 Unsupported Media Type` | Soxta fayl rad etildi, yangi fayl yozilmadi |
| **`signature.png` yuklash** | `201 Created` | `415 Unsupported Media Type` | Buzilgan imzo rad etildi, dekodlash xatosi |
| **`big.png` yuklash** | `413 Payload Too Large` | `413 Payload Too Large` | 256 KB bayt limiti ishladi |
| **`pixels.png` yuklash** | `201 Created` | `413 Payload Too Large` | Piksel limiti (1M) oshgani sababli to‘xtatildi |
| **`guide.txt` o‘qish** | `200 OK; A7-PUBLIC` | `200 OK; A7-PUBLIC` | Qonuniy ochiq fayl o‘qildi |
| **`../internal/demo.txt`** | `200 OK; A7-PRIVATE-FILE` | `403 Forbidden` | Katalog chegarasidan chiqish to‘xtatildi |
| **`8017 /card` resursi** | `200 OK; catalog / Daftar` | `200 OK; catalog / Daftar` | Qonuniy katalog resursi olindi |
| **`8018 /status` resursi** | `200 OK; A7-INTERNAL` | `403 Forbidden` | SSRF to‘xtatildi, 8018 da yangi GET qayd etilmadi |

### 5.2. Ko‘p uchraydigan muammolar va ularni bartaraf etish (Troubleshooting)

1. **Xatolik: `Address already in use` (8007, 8017 yoki 8018 portlari band):**
   - *Sababi:* Oldingi laboratoriyadan (masalan A6 dan) qolgan server yoki orqa fonda qolib ketgan Python jarayoni portni egallab turibdi.
   - *Yechim:* Portni band qilgan jarayonni topib o‘chiring:
     ```bash
     sudo lsof -i :8007 -i :8017 -i :8018
     kill -9 <PID>
     ```
2. **Xatolik: `Connection refused` (curl ulanolmayapti):**
   - *Sababi:* `app.py` yoki `services.py` ishga tushmagan, yiqilgan yoki so‘rov boshqa IP/portga yuborilmoqda.
   - *Yechim:* 1 va 2-terminallarda serverlar ishlab turganini tekshiring, manzil aynan `127.0.0.1` ekaniga ishonch hosil qiling.
3. **Xatolik: `ModuleNotFoundError: No module named 'flask'` yoki `'PIL'`:**
   - *Sababi:* Virtual muhit faollashtirilmagan.
   - *Yechim:* Terminalda `source ~/websec/A7/.venv/bin/activate` buyrug‘ini bajaring.
4. **Xatolik: Haqiqiy `good.png` ga `415 Unsupported Media Type` qaytyapti:**
   - *Sababi:* cURL buyrug‘ida fayl kengaytmasi to‘g‘ri yozilmagan yoki multipart MIME turi `image/png` sifatida ko‘rsatilmagan.
   - *Yechim:* Buyruqda `-F "file=@samples/good.png;type=image/png"` sintaksisini tekshiring.
5. **Xatolik: SSRF sinovida `502 Bad Gateway` qaytyapti:**
   - *Sababi:* 8017 yoki 8018 portidagi `services.py` ishlamayapti yoki so‘ralgan manzil mavjud emas.
   - *Yechim:* 2-terminalda `python services.py` ishlab turganini tekshiring.
6. **Xatolik: Kodni tuzatgandan keyin ham eski natijalar qaytmoqda:**
   - *Sababi:* `app.py` da `debug=False` o‘rnatilgani sababli Flask kod o‘zgarganda o‘zini avtomatik qayta yuklamaydi.
   - *Yechim:* 1-terminalda serverni `Ctrl+C` bilan to‘xtatib, `python app.py` ni qayta ishga tushiring.

### 5.3. Nazorat savollariga batafsil ilmiy va amaliy javoblar

#### 1-savol: Nega `.png` kengaytmasi va `image/png` MIME turi fayl mazmunini isbotlamaydi?
**Javob:** Fayl nomi va uning kengaytmasi fayl tizimidagi ixtiyoriy matn yorlig‘idir, uni istalgan foydalanuvchi erkin o‘zgartirishi mumkin. HTTP protokoli orqali fayl yuborilganda `Content-Type: image/png` sarlavhasini mijoz (brauzer yoki cURL vositasi) o‘zi mustaqil belgilaydi. Hujumchi ixtiyoriy matnli skriptga `.png` kengaytmasini berib, soxta MIME sarlavhasini qo‘shib yuborishi mumkin. Server faylning ichki bayt tuzilmasini mustaqil tahlil qilmaguncha, uning haqiqiy tasvir ekaniga ishonch hosil qila olmaydi.

#### 2-savol: PNG imzosi (Magic Bytes) bor fayl nega baribir rasm sifatida ochilmasligi mumkin?
**Javob:** PNG formatining boshidagi 8 bayt (`\x89PNG\r\n\x1a\n`) faqat fayl boshlanishini bildiruvchi identifikator xolos. To‘liq va yaroqli rasm bo‘lishi uchun fayl o‘z ichida to‘g‘ri tuzilgan bosh sarlavha blokini (IHDR chunk), ranglar palitrasini, siqilgan piksel ma’lumotlarini (IDAT chunk) va yakunlovchi blokni (IEND chunk) saqlashi hamda ularning CRC nazorat summalari to‘g‘ri kelishi shart. Agar hujumchi oddiy zararli matn boshiga faqat 8 baytli imzoni qo‘shib qo‘ysa (`signature.png` kabi), Pillow kutubxonasi uning ichki bloklarini o‘qiy olmaydi va `UnidentifiedImageError` xatoligini chiqaradi.

#### 3-savol: Fayl bayt hajmi va piksel soni nega ikki alohida limit sifatida tekshiriladi?
**Javob:**
1. **Bayt hajmi limiti (`MAX_FILE = 256 * 1024` bayt):** Tarmoq o‘tkazuvchanligini saqlash va server diskida joy tugab qolishining oldini olish uchun xizmat qiladi.
2. **Piksel soni limiti (`im.width * im.height <= 1_000_000`):** Dekompressiya hujumlaridan (Pixel Flood / Decompression Bomb) himoyalaydi. PNG yuqori darajada siqilganligi sababli, diskda 20 KB joy egallagan rasm xotiraga yuklanganda (dekompressiyada) yuzlab megabayt yoki gigabaytlab operativ xotirani (RAM) to‘ldirib yuborishi mumkin. Shuning uchun bayt hajmi va ochilgandagi piksel matritsasi o‘lchami alohida-alohida nazorat qilinishi shart.

#### 4-savol: `resolve()` va `is_relative_to()` qanday turli vazifalarni bajaradi?
**Javob:**
- `resolve()` — fayl yo‘lidagi barcha nisbiy qismlarni (`..`, `.`) va operatsion tizimdagi ramziy bog‘lamalarni (symlinks) to‘liq yechadi hamda faylning tizimdagi haqiqiy, kanonik mutlaq manzilini hosil qiladi.
- `is_relative_to(base)` — bitta yo‘l ikkinchi katalog ichida joylashgan-joylashmaganini mantiqiy solishtiradi (`True` yoki `False`).
- *Muhim:* `is_relative_to()` yo‘llarni o‘zi yechmaydi, shuning uchun avval `resolve()` orqali haqiqiy nishon aniqlanadi, so‘ngra `is_relative_to()` orqali uning ruxsat etilgan katalog chegarasida ekani tekshiriladi.

#### 5-savol: SSRF so‘rovi backendga ulanishdan oldin rad etilganini qanday bilasiz?
**Javob:** Buni ikkita o‘zaro bog‘liq dalil orqali isbotlash mumkin:
1. Asosiy ilova mijozga zudlik bilan `403 Forbidden` javobini qaytaradi;
2. Eng asosiysi — ichki xizmat (`services.py` 8018-port) ishlayotgan 2-terminal jurnalida ushbu so‘rov paytida hech qanday yangi `GET /status` yozuvi paydo bo‘lmaydi. Agar server avval ulanib, keyin javobni tekshirganda edi, 8018 jurnalida so‘rov qayd etilgan bo‘lardi. Jurnalda yozuv yo‘qligi server ulanishni umuman amalga oshirmasdan rad etganini bildiradi.

#### 6-savol: Nega bu tajribadagi matn o‘qish LFI, HTTP javob olish esa RFI deb atalmasligi kerak?
**Javob:**
- LFI (Local File Inclusion) va RFI (Remote File Inclusion) zaifliklarida fayl yoki tashqi resurs dasturlash tili interpretatoriga kiritiladi va undagi kod ijro etiladi (`include`, `require`, `eval()`).
- Ushbu tajribada `read_weak()` faylni shunchaki matn sifatida o‘qiydi (`read_text()`), `fetch_weak()` esa HTTP javobini JSON ichida matn sifatida qaytaradi. Ular serverda hech qanday kodni bajarmaydi (execute qilmaydi). Shu sababli bu holatlar mos ravishda **Path Traversal** va **SSRF** hisoblanadi.

#### 7-savol: JSON sxemasini tekshirish va ishonchsiz `pickle`dan voz kechish qaysi xavflarni kamaytiradi?
**Javob:**
1. Pythonning `pickle` moduli obyektlarni qayta tiklashda `__reduce__` metodi orqali operatsion tizim darajasida ixtiyoriy kodni ishga tushirish imkoniga ega bo‘lib, RCE (Remote Code Execution) xavfini keltirib chiqaradi. Undan voz kechish kod ijrosi xavfini butunlay yo‘qotadi.
2. JSON faqat ma’lumot uzatuvchi xavfsiz formatdir, ammo uning sxemasi tekshirilmasa, Mass Assignment yoki parametr manipulyatsiyasi (masalan, `{"admin": true}`) yuzaga kelishi mumkin. Qat’iy sxema tekshiruvi faqat ruxsat etilgan kalitlar (`theme`) va qat’iy qiymatlar (`light`/`dark`) qabul qilinishini ta’minlab, ma’lumotlar yaxlitligini kafolatlaydi.

---

## 6-BO‘LIM: FOYDALANILGAN VA TAVSIYA ETILADIGAN MANBALAR

1. **OWASP — File Upload Cheat Sheet:**
   Fayllarni xavfsiz yuklash, MIME/kengaytma tekshiruvi, xavfsiz saqlash va tasvirlarni qayta kodlash bo‘yicha xalqaro standart tavsiyalar.
   https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
2. **OWASP — Path Traversal:**
   Katalog chegarasidan chiqish zaifligi tabiati, namunalari va oldini olish choralari.
   https://owasp.org/www-community/attacks/Path_Traversal
3. **OWASP — Server-Side Request Forgery Prevention Cheat Sheet:**
   SSRF zaifligini aniqlash, ruxsat etilgan oq ro‘yxatlar (Allowlist) va ichki tarmoq himoyasi bo‘yicha to‘liq qo‘llanma.
   https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
4. **Pillow (PIL Fork) Documentation — Security Considerations:**
   Tasvirlarni tahlil qilish, `im.verify()`, `im.load()` va `DecompressionBombError` cheklovlari bo‘yicha rasmiy hujjatlar.
   https://pillow.readthedocs.io/en/stable/releasenotes/
5. **Python Documentation — `pathlib` Module:**
   Fayl tizimi yo‘llari bilan xavfsiz ishlash, `resolve()`, `is_relative_to()` funksiyalari va ramziy bog‘lamalar bilan ishlash qoidalari.
   https://docs.python.org/3/library/pathlib.html
6. **OWASP Web Security Testing Guide (WSTG) — Testing for Local File Inclusion:**
   LFI zaifliklarini testlash metodologiyasi va uning Path Traversaldan farqlari.
   https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11.1-Testing_for_Local_File_Inclusion
7. **OWASP Web Security Testing Guide (WSTG) — Testing for Remote File Inclusion:**
   RFI zaifliklarini tahlil qilish va uning SSRF dan farqlari.
   https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11.2-Testing_for_Remote_File_Inclusion
8. **Python Documentation — `http.client` Module:**
   Past darajadagi HTTP mijozini sozlash, ulanish taymautlari va oqimni xavfsiz o‘qish chegaralari.
   https://docs.python.org/3/library/http.client.html
9. **Python Documentation — `pickle` Security Warnings & CWE-502:**
   Ishonchsiz ma’lumotlarni deserializatsiya qilishdagi kritik xavflar va xavfsiz JSON muqobillari.
   https://docs.python.org/3/library/pickle.html
