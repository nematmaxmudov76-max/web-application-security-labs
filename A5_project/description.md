# Veb Dasturlar Xavfsizligi: A5 Amaliy Mashg‘ulot Qo‘llanmasi

**Mavzu:** A5. Inyeksiya zaifliklari: SQL inyeksiya, NoSQL va ORM xavfsizligi  
**Variant:** 1-VARIANT — Mahsulotlar katalogida so‘rovlarni tekshirish va himoyalash  
**Tizim muhiti:** Host: Ubuntu Linux $\rightarrow$ VMware Workstation $\rightarrow$ Guest: Ubuntu Desktop / Ubuntu Server  
**Tarmoq muhiti:** Shaxsiy lokal Wi-Fi (To‘g‘ridan-to‘g‘ri internet, universitet proksisisiz va cheklovlarsiz)  
**Laboratoriya manzili:** `http://127.0.0.1:8005/`  

---

## MUNDARIJA

1. [Mavzuning Maqsadi va Kutiladigan Natijalar](#1-mavzuning-maqsadi-va-kutiladigan-natijalar)
   - 1.1. Asosiy maqsad
   - 1.2. O‘rganiladigan asosiy tushunchalar va ko‘nikmalar
   - 1.3. Kutiladigan amaliy natijalar
   - 1.4. Mashg‘ulot parametrlari va arxitekturasi
2. [Barcha Nazariy va Amaliy Mavzular Bo‘yicha To‘liq Qo‘llanma](#2-barcha-nazariy-va-amaliy-mavzular-boyicha-toliq-qollanma)
   - 2.1. Inyeksiya (Injection) zaifliklari nima? (OWASP Top 10 — A03:2021)
   - 2.2. Ishonch chegarasi (Trust Boundary) va ma’lumot/kod aralashuvi
   - 2.3. Klassik SQL Inyeksiyasi (SQLi) va WHERE mantiqining buzilishi
   - 2.4. ORM (Object-Relational Mapping) xavfsizligi va xom SQL (Raw SQL) xatosi
   - 2.5. NoSQL Inyeksiyasi va Operator Inyeksiyasi (`$ne`, `$gt`, JSON kiritmalar)
   - 2.6. SQL vs ORM vs NoSQL: Taqqoslash va himoya mexanizmlari
   - 2.7. Nima uchun "Qora ro‘yxat" (Blocklist/Sanitizatsiya) samarasiz? Apostrof muammosi (`O'quv qo'llanma`)
   - 2.8. Parametrli so‘rovlar (Prepared Statements / Parameterized Queries) qanday ishlaydi?
   - 2.9. Kiritma turini tekshirish (Type Validation, Scalar tekshiruv, Allowlist)
   - 2.10. Kirish huquqi (Access Control / `public` filtri) va Inyeksiya o‘rtasidagi bog‘liqlik
3. [Amaliy Mashqni Bajarish Ketma-Ketligi (Qadamma-Qadam Qo‘llanma)](#3-amaliy-mashqni-bajarish-ketma-ketligi-qadamma-qadam-qollanma)
   - 3.1. Ishchi muhitni tayyorlash (Ubuntu Host $\rightarrow$ VMware $\rightarrow$ Ubuntu Guest)
   - 3.2. Shaxsiy lokal Wi-Fi sozlamalari (Universitet proksisini tozalash va to‘g‘ridan-to‘g‘ri ulanish)
   - 3.3. Kerakli paketlar va Virtual Muhit (Python venv)ni sozlash (Har bir CLI buyruq tahlili bilan)
   - 3.4. Dastur kodini (`app.py`) yaratish va tahlil qilish
   - 3.5. Serverni ishga tushirish va boshlang‘ich holatni tekshirish (1-topshiriq, Dalil D1)
   - 3.6. SQL Inyeksiyani sinash va tahlil qilish (2-topshiriq, Dalillar D2–D3)
   - 3.7. ORM xavfsizligini tekshirish: Xom SQL vs Model ifodasi (3-topshiriq, Dalil D4)
   - 3.8. NoSQL Operator Inyeksiyasini sinash (4-topshiriq, Dalil D5)
   - 3.9. Kodni tuzatish va avvalgi manzillarda qayta sinash (5-topshiriq, Dalil D6)
   - 3.10. Qo‘shimcha topshiriq: UNION SELECT inyeksiyasi
   - 3.11. Natijalar jadvali (Oldin va Keyin holati)
   - 3.12. Hisobotga qo‘yiladigan talablar va dalillar ro‘yxati
   - 3.13. Ko‘p uchraydigan xatolar va ularni bartaraf etish (Troubleshooting)
   - 3.14. Nazorat savollari va to‘liq, mukammal javoblar
4. [Foydalanilgan va Tavsiya Etiladigan Manbalar](#4-foydalanilgan-va-tavsiya-etiladigan-manbalar)

---

## 1. MAVZUNING MAQSADI VA KUTILADIGAN NATIJALAR

### 1.1. Asosiy maqsad
Ushbu A5 laboratoriya mashg‘ulotining asosiy maqsadi — talabalarda veb-ilovalarning ma’lumotlar bazasi bilan aloqa qiluvchi qatlamlarida (Database Abstraction Layer) yuzaga keladigan **Inyeksiya (Injection)** zaifliklarini amaliy tushunish, ularni ekspluatatsiya qilish, sabablarini tahlil qilish hamda zamonaviy dasturlash standartlariga muvofiq xavfsiz holatga keltirish ko‘nikmalarini shakllantirishdir.

Laboratoriya davomida:
1. Foydalanuvchi kiritgan ma’lumotlar (Input) dastur kodi va ma’lumotlar bazasi so‘rovi (Query Structure) tuzilishini qanday o‘zgartirib yuborishini tajribada isbotlash.
2. Relyatsion ma’lumotlar bazalarida xom SQL (Raw SQL) va string formatlash (`f-string`, konkatenatsiya) qanday xavf tug‘dirishini ko‘rsatish.
3. ORM (Object-Relational Mapping — SQLAlchemy) kutubxonasidan foydalanishning o‘zi avtomatik tarzda xavfsizlik kafolatini bermasligini (ORM ichida xom SQL bajarish xatosi) ochib berish.
4. NoSQL (MongoDB / mongomock) ma’lumotlar omborida matn (String) o‘rniga JSON obyektlari (`Object / Dictionary`) yuborilganda so‘rov mantig‘i qanday buzilishini (Operator Injection) tahlil qilish.
5. Har uchala zaiflikni to‘g‘ri himoya usullari: parametrli so‘rovlar (Parameterized Queries / Prepared Statements), ORM model ifodalari hamda kiritma turini tekshirish (Type / Scalar Validation) orqali to‘liq bartaraf etish.

### 1.2. O‘rganiladigan asosiy tushunchalar va ko‘nikmalar
* **SQL Injection (SQLi):** So‘rov parametriga maxsus belgilar (`'`, `--`, `OR 1=1`) kiritish orqali `WHERE` shartini manipulyatsiya qilish va yashirin/yopiq yozuvlarni ruxsatsiz o‘qish.
* **ORM Raw SQL Injection:** ORM sessiyasida `session.execute(text(...))` orqali foydalanuvchi ma’lumotini to‘g‘ridan-to‘g‘ri matnga qo‘shib yuborish oqibatlari.
* **NoSQL Operator Injection:** NoSQL so‘roviga mijoz tomonidan operatorlar (`$ne`, `$gt`, `$regex`) inyeksiya qilinishi va buning natijasida ruxsatsiz filtrlashni chetlab o‘tish.
* **Prepared Statements / Parametrlarni bog‘lash:** Kod va ma’lumotni ajratish mexanizmi.
* **Kiritma ma’lumotlarini tekshirish (Validation):** Foydalanuvchi yuborgan ma’lumotning turi (`isinstance`), hajmi (`len`) va ruxsat etilgan maydonlar (`allowlist`) bo‘yicha nazorat o‘rnatish.

### 1.3. Kutiladigan amaliy natijalar
* Talaba uchta zaif endpoint (`/sql/weak`, `/orm/weak`, `/nosql/weak`) bo‘yicha takrorlanuvchi dalillarni to‘playdi.
* Oddiy kiritma (`name=Daftar`), yopiq kiritma (`name=Ichki loyiha`), apostrofli qonuniy kiritma (`name=O'quv qo'llanma`) hamda inyeksiya kiritmalarining natijalarini HTTP status kodlari, qaytgan elementlar soni (`count`) va ID raqamlari orqali solishtiradi.
* `app.py` faylidagi uchta zaif funksiyani (`sql_weak`, `orm_weak`, `nosql_weak`) to‘g‘rilaydi va aynan shu manzillarda regressiya testlarini muvaffaqiyatli o‘tkazadi.
* Barcha buyruqlar, ularning natijalari va dalillari hisobot uchun tayyorlanadi.

### 1.4. Mashg‘ulot parametrlari va arxitekturasi
* **Variant:** Faqat 5-semestr / A5 / 1-variant.
* **Vaqt me’yori:** 80 daqiqa (asosiy tajriba).
* **Asosiy operatsion tizim (Host OS):** Ubuntu Linux (20.04 / 22.04 / 24.04 LTS).
* **Virtualizatsiya dasturi:** VMware Workstation Pro / Player for Linux.
* **Virtual mashina (Guest VM):** Ubuntu Desktop 24.04 LTS yoki Ubuntu Server 24.04 LTS (4 vCPU, 8 GB RAM, kamida 20 GB disk).
* **Tarmoq konfiguratsiyasi:** Shaxsiy lokal Wi-Fi (NAT / Bridged rejimida internetga to‘g‘ridan-to‘g‘ri ulanish, universitet proksisisiz).
* **Laboratoriya manzili:** `http://127.0.0.1:8005/` (Server va mijoz (curl) bitta VM ichida loopback orqali ishlaydi).
* **Sun’iy ma’lumotlar bazasi:**
  - Jami 4 ta mahsulot: 3 ta ochiq (`public: True`) va 1 ta maxfiy/yopiq (`public: False`).
  - Ma’lumotlar dastur ishga tushganda SQLite xotirasida (`:memory:`) va `mongomock` kolleksiyasida dinamik yaratiladi.

---

## 2. BARCHA NAZARIY VA AMALIY MAVZULAR BO‘YICHA TO‘LIQ QO‘LLANMA

### 2.1. Inyeksiya (Injection) zaifliklari nima? (OWASP Top 10 — A03:2021)
Inyeksiya zaifliklari ko‘p yillardan buyon **OWASP Top 10** ro‘yxatining eng yuqori o‘rinlarida turadi. Bu zaiflikning tub mohiyati quyidagicha:
> **Inyeksiya** — bu ishonchsiz, tekshirilmagan foydalanuvchi ma’lumotining dastur buyrug‘i yoki ma’lumotlar bazasi so‘rovi (SQL, NoSQL, LDAP, OS command) tarkibiga sintaktik ajratgichlarsiz to‘g‘ridan-to‘g‘ri qo‘shilishi natijasida, ma’lumotning **bajariluvchi kod (instruction)** sifatida talqin qilinishidir.

Buzg‘unchi kiritgan maxsus belgilar (`'`, `"`, `--`, `$ne`, `;`) dastur tomonidan tuzilgan so‘rov sintaksisini sindiradi va bazaga mutlaqo boshqa mantiqdagi buyruqni bajarishga majbur qiladi.

---

### 2.2. Ishonch chegarasi (Trust Boundary) va ma’lumot/kod aralashuvi
Xavfsiz dasturlashda eng muhim qoida: **Ishonchsiz ma’lumot (Untrusted Data) hech qachon bajariluvchi kod (Code/Syntax) bilan aralashib ketmasligi kerak**.

```
[ Foydalanuvchi Kiritmasi ]  ---> (Ishonch chegarasi) ---> [ Dastur Mantiqi ] ---> [ Ma'lumotlar Bazasi ]
   (Xavfli ma'lumot)                                          (SQL Shabloni)           (Interpreter/Parser)
```

Agar dasturchi quyidagicha kod yozsa:
```python
# XATO VA XAVFLI USUL (String Formatting):
query = f"SELECT * FROM products WHERE name = '{name}' AND public = 1"
```
Bu yerda `name` o‘zgaruvchisi oddiy qiymat bo‘lib qolmaydi, u to‘g‘ridan-to‘g‘ri SQL matnining bir qismiga aylanadi. Agar `name` ichiga `'` (apostrof) kelsa, SQL parsiri buni kiritma emas, balki string literalining oxiri deb tushunadi.

---

### 2.3. Klassik SQL Inyeksiyasi (SQLi) va WHERE mantiqining buzilishi
Bizning katalogimizdagi mahsulotlar ro‘yxati:
1. `id=1, name='Daftar', public=True`
2. `id=2, name='Qalam', public=True`
3. `id=3, name="O'quv qo'llanma", public=True`
4. `id=4, name='Ichki loyiha', public=False` (Maxfiy, oddiy foydalanuvchiga ko‘rinmasligi kerak!)

Oddiy qidiruv so‘rovi:
```sql
SELECT id, name, public FROM products WHERE name = 'Daftar' AND public = 1
```
Bu so‘rov faqat `id=1` mahsulotini qaytaradi.

Buzg‘unchi kiritmasi:
```text
Daftar' OR 1=1 -- 
```
SQL so‘rovi quyidagi ko‘rinishga keladi:
```sql
SELECT id, name, public FROM products WHERE name = 'Daftar' OR 1=1 -- ' AND public = 1
```

Bu so‘rov qanday ishlaydi?
1. `Daftar'` — apostrof orqali `name` qiymatining chegarasi yopiladi.
2. `OR 1=1` — mantiqiy shart qo‘shiladi. `1=1` doimo rost (TRUE) bo‘lganligi sababli, butun `WHERE` sharti barcha qatorlar uchun TRUE qiymat qaytaradi.
3. `-- ` — SQLite va ko‘plab SQL bazalarda izoh (comment) belgisidir. U o‘zidan keyingi barcha belgilarni, shu jumladan dasturchi qo‘ygan `' AND public = 1` cheklovini butunlay bekor qiladi (ignore qilinadi).
4. **Natija:** Baza barcha 4 ta qatorni qaytaradi! Shu jumladan `public=0` bo‘lgan maxfiy `Ichki loyiha` (ID=4) ham fosh bo‘ladi. Bu ma’lumotlar sizib chiqishi (Information Disclosure) va kirish huquqining buzilishidir.

---

### 2.4. ORM (Object-Relational Mapping) xavfsizligi va xom SQL (Raw SQL) xatosi
Ko‘plab dasturchilar orasida noto‘g‘ri tushuncha mavjud: *"Biz SQLAlchemy (yoki Django ORM, Hibernate) ishlatamiz, demak bizda SQL inyeksiya bo‘lishi mumkin emas"*.

Bu tushuncha xatodir! ORM vositalari odatda so‘rovlarni xavfsiz tuzish imkonini beradi, biroq agar dasturchi ORM ichida **xom SQL (Raw SQL)** ifodalaridan foydalansa va unga foydalanuvchi ma’lumotini formatlab qo‘shsa, zaiflik to‘liq saqlanib qoladi.

**Zaif ORM kodi (`/orm/weak`):**
```python
# Xom SQL ORM ichida bajarilmoqda:
query = SQL + f"WHERE name = '{name}' AND public = 1"
session.execute(text(query))
```
Bu yerda `text(query)` chaqirilishidan oldin Pythonning `f-string` mexanizmi foydalanuvchi kiritmasini SQL matniga yopishtirib bo‘lgan. `session.execute()` bu xavfli SQLni to‘g‘ridan-to‘g‘ri ma’lumotlar bazasiga yuboradi.

**Xavfsiz ORM kodi (`/orm/safe`):**
```python
# Model obyektlari va Where ifodalari orqali:
stmt = select(Product).where(
    Product.name == name,
    Product.public.is_(True)
)
session.scalars(stmt).all()
```
Bu yerda `Product.name == name` ifodasi Python operatori emas, balki SQLAlchemy’ning BinaryExpression obyektidir. SQLAlchemy `name` o‘zgaruvchisini SQL shabloniga qo‘shmaydi, balki uni parametr (`:name`) sifatida alohida uzatadi.

---

### 2.5. NoSQL Inyeksiyasi va Operator Inyeksiyasi (`$ne`, `$gt`, JSON kiritmalar)
Relyatsion bazalarda SQL sintaksisi manipulyatsiya qilinsa, hujjatlarga yo‘naltirilgan NoSQL (MongoDB) bazalarida so‘rovlar **JSON / BSON** obyektlari orqali yuboriladi.

Ko‘pincha dastur API’lari JSON qabul qiladi. Agar backend kiritilgan ma’lumot turini tekshirmasa, hujumchi matn (string) o‘rniga ichki operatorli JSON obyekt yuborishi mumkin.

**Oddiy so‘rov:**
```json
{"name": "Daftar"}
```
Bazada bajariladigan filtr:
```python
query = {'name': 'Daftar', 'public': True}
```

**Operator inyeksiyasi:**
Mijoz string o‘rniga `{"$ne": null}` obyektini yuboradi:
```json
{"name": {"$ne": null}}
```
Zaif kod buni to‘g‘ridan-to‘g‘ri filtrga qo‘yadi:
```python
query = {'name': {'$ne': null}, 'public': True}
```

Bu nima degani?
* `$ne` — MongoDB’da **Not Equal (Teng emas)** operatoridir.
* `{"$ne": null}` sharti: *"Nomi mavjud bo‘lgan va null bo‘lmagan barcha yozuvlarni top"* degan ma’noni beradi.
* Barcha 3 ta ochiq mahsulotning nomi bor va ular null emas, shuning uchun so‘rov 3 ta mahsulotni qaytaradi!
* **Muhim farq:** Bu yerda `public: True` filtri server tomonidan alohida qo‘yilgan va u o‘zgarmagan. Shuning uchun `public: False` bo‘lgan ID=4 bu yerda chiqmaydi. Ya’ni NoSQL operator inyeksiyasi SQL inyeksiyasidagi kabi qator oxirini izohlab (`--`), boshqa filtrlarni bekor qila olmaydi.

---

### 2.6. SQL vs ORM vs NoSQL: Taqqoslash va himoya mexanizmlari

| Xususiyat | SQL (Relyatsion) | ORM (SQLAlchemy) | NoSQL (MongoDB / mongomock) |
| :--- | :--- | :--- | :--- |
| **So‘rov formati** | Matnli SQL buyrug‘i | Python Model ifodasi yoki xom SQL | BSON / Lug‘at (Dictionary) obyekti |
| **Zaif yondashuv** | `f"WHERE name = '{name}'"` | `session.execute(text(f"...{name}..."))` | `query = {'name': body['name']}` (tekshiruvsiz) |
| **Hujum vektori** | Sintaktik manipulyatsiya (`' OR 1=1 -- `) | Sintaktik manipulyatsiya (`' OR 1=1 -- `) | Operator inyeksiyasi (`{"$ne": null}`) |
| **Xavfsiz yondashuv** | Parametrli so‘rov (`WHERE name = ?`) | `select(Product).where(Product.name == name)` | Tur tekshiruvi (`scalar`) va qat’iy `$eq` |
| **Himoya yadrosi** | Parser ma’lumotni koddan ajratadi | ORM parametrli bog‘lashni avtomatlashtiradi | Server operatorni mijozdan qabul qilmaydi |

---

### 2.7. Nima uchun "Qora ro‘yxat" (Blocklist/Sanitizatsiya) samarasiz? Apostrof muammosi (`O'quv qo'llanma`)
Ko‘plab tajribasiz dasturchilar SQL inyeksiyadan himoyalanish uchun apostroflarni (`'`), tirnoqlarni yoki `OR`, `SELECT` so‘zlarini o‘chirib tashlashga yoki filtrlashga urinadilar (Blocklist / Sanitization).

Bu yondashuvning ikkita katta kamchiligi bor:
1. **Qonuniy ma’lumotlar buziladi:** O‘zbek tilida apostrof tutuq belgisi sifatida juda keng qo‘llaniladi (masalan, `O'quv qo'llanma`, `Ma'lumot`, `Yo'l`). Agar dastur apostrofni taqiqlasa yoki o‘chirib yuborsa, foydalanuvchi qonuniy tovarlarni qidira olmaydi yoki qidiruv xatoga uchraydi.
2. **Aylanib o‘tish (Bypass) xavfi:** Qora ro‘yxatdagi barcha xavfli belgilarni to‘liq qamrab olish imkonsiz. Hujumchilar URL-encoding, hex-encoding yoki boshqa SQL operatorlari orqali filtrlarni chetlab o‘tadilar.

**Xulosa:** Himoya qilishning to‘g‘ri yo‘li apostroflarni o‘chirish emas, balki ma’lumotlar bazasiga ma’lumotni alohida kanal (parametr) orqali uzatishdir!

---

### 2.8. Parametrli so‘rovlar (Prepared Statements / Parameterized Queries) qanday ishlaydi?
Parametrli so‘rov — bu SQL inyeksiyasiga qarshi **yagona 100% rasmiy va to‘g‘ri himoya vositasi** (OWASP Primary Defense).

U qanday ishlaydi?
1. **1-bosqich (Kompilyatsiya/Parse):** Dastur ma’lumotlar bazasiga SQL shablonini yuboradi:
   ```sql
   SELECT id, name, public FROM products WHERE name = ? AND public = 1
   ```
   Baza bu shablonni kompilyatsiya qiladi, sintaksisini tahlil qiladi va ijro rejasini (execution plan) tuzadi. Baza `?` belgisi turgan joyga faqat **bitta oddiy qiymat (literal)** kelishini oldindan biladi.
2. **2-bosqich (Parametrni bog‘lash - Binding):** Dastur bazaga alohida qiymatni uzatadi:
   ```python
   (name,)  # Masalan: "Daftar' OR 1=1 -- "
   ```
3. Baza bu qiymatni hech qachon SQL kodi deb hisoblamaydi. U qiymat ichidagi `'` belgilarini shunchaki matn belgisi sifatida qabul qiladi va bazadagi tovarlar orasidan nomi aynan `"Daftar' OR 1=1 -- "` bo‘lgan mahsulotni qidiradi. Bunday tovar yo‘qligi sababli bo‘sh natija (`count: 0`) qaytadi.

---

### 2.9. Kiritma turini tekshirish (Type Validation, Scalar tekshiruv, Allowlist)
NoSQL va umumiy veb-arxitekturada kiritma turlarini tekshirish muhim ikkinchi himoya qatlamidir:
* **Skalyar tekshiruv (`scalar`):** Kelayotgan qiymat haqiqatan ham oddiy matnmi (`isinstance(value, str)`)? U obyekt (`dict`), ro‘yxat (`list`) yoki son emasligiga ishonch hosil qilish.
* **Hajm tekshiruvi:** Matn uzunligi ruxsat etilgan chegaradami (`1 <= len(value) <= 120`)?
* **Maydonlar oq ro‘yxati (Field Allowlist):** JSON tanasida faqat ruxsat etilgan kalitlar kelganini tekshirish (`set(body) == {'name'}`). Agar foydalanuvchi ortiqcha `public: false` yoki `role: admin` kabi maydonlarni qo‘shib yuborsa, tizim darhol HTTP 400 xatosi bilan so‘rovni to‘xtatadi.

---

### 2.10. Kirish huquqi (Access Control / `public` filtri) va Inyeksiya o‘rtasidagi bog‘liqlik
Bizning tizimimizda ikkita alohida mantiqiy vazifa bor:
1. **So‘rov sintaksisi yaxlitligi:** Foydalanuvchi qidirayotgan nom (`name`).
2. **Biznes qoidasi va ruxsat nazorati:** Tizim faqat ommaviy tovarlarni ko‘rsatishi kerak (`public = 1` yoki `public: True`).

SQL inyeksiyasida buzg‘unchi izoh (`--`) qo‘yish orqali biznes qoidasini yo‘qqa chiqardi. Parametrli so‘rov joriy etilganda esa, foydalanuvchi kiritmasi faqat `name` parametriga bog‘lanadi va server tomonidan qo‘yilgan `public = 1` shartiga hech qachon daxl qila olmaydi!

---

## 3. AMALIY MASHQNI BAJARISH KETMA-KETLIGI (QADAMMA-QADAM QO‘LLANMA)

### 3.1. Ishchi muhitni tayyorlash (Ubuntu Host $\rightarrow$ VMware $\rightarrow$ Ubuntu Guest)

Sizning ishchi muhitingiz:
* **Host kompyuter:** Ubuntu Linux.
* **Virtualizatsiya:** VMware Workstation Pro / Player for Linux.
* **VM (Guest):** Ubuntu Desktop 24.04 LTS yoki Ubuntu Server 24.04 LTS.

#### VMware virtual mashina sozlamalari:
1. VMware dasturini ishga tushiring:
   ```bash
   vmware &
   ```
2. Virtual mashinani (Ubuntu Desktop yoki Ubuntu Server) tanlang.
3. **VM Settings** oynasiga kiring:
   - **Processors:** 4 vCPU belgilang.
   - **Memory:** 8 GB RAM (kamida 4 GB) ajrating.
   - **Network Adapter:** `NAT` rejimini tanlang (paketlarni yuklash uchun).
4. Virtual mashinani yoqing.

---

### 3.2. Shaxsiy lokal Wi-Fi sozlamalari (Universitet proksisini tozalash va to‘g‘ridan-to‘g‘ri ulanish)

> [!IMPORTANT]
> **MUHIM OGOHLANTIRISH (Shaxsiy Wi-Fi foydalanuvchilari uchun):**  
> Universitetning `A5` metodik qo‘llanmasida `172.18.1.1:2500` proksi manzili va `\\172.18.233.234\files` SMB serveri ko‘rsatilgan. Bu sozlamalar **faqat va faqat universitet laboratoriya xonasidagi Wi-Fi tarmog‘i uchun mo‘ljallangan!**  
> Siz o‘zingizning uyingizdagi yoki shaxsiy lokal Wi-Fi tarmog‘ingizda bo‘lganingiz sababli, **hech qanday proksi sozlamasini kiritmaysiz!** Agar kiritilgan bo‘lsa, tizim internetga chiqa olmay qoladi.

Agar virtual mashinangizda ilgari universitet proksisi o‘rnatilgan bo‘lsa, uni tozalash uchun quyidagi amallarni bajaring:

```bash
# 1. Terminaldagi proksi muhit o'zgaruvchilarini tozalash:
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy NO_PROXY

# 2. APT proksi konfiguratsiyasi mavjud bo'lsa, uni o'chirish:
sudo rm -f /etc/apt/apt.conf.d/99proxy

# 3. snapd uchun proksi fayli mavjud bo'lsa, uni o'chirish va xizmatni qayta ishga tushirish:
sudo rm -f /etc/systemd/system/snapd.service.d/veb-proxy.conf
sudo systemctl daemon-reload
sudo systemctl restart snapd
```

Internet aloqasini tekshirish:
```bash
curl -I https://ubuntu.com
```
* **Nima qiladi:** Ubuntu rasmiy serveriga HTTP HEAD so‘rovi yuboradi.
* **Kutiladigan natija:** `HTTP/2 200` yoki `HTTP/1.1 200 OK`. Bu shaxsiy Wi-Fi orqali to‘g‘ridan-to‘g‘ri internet ishlayotganini bildiradi.

---

### 3.3. Kerakli paketlar va Virtual Muhit (Python venv)ni sozlash

Endi virtual mashina terminalida laboratoriya uchun zarur bo‘lgan dasturiy ta’minotlarni o‘rnatamiz.

#### 1-qadam: Tizim paketlarini yangilash va o‘rnatish
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip curl nano open-vm-tools
```
**Har bir komanda va bayroqchaning vazifasi:**
* `sudo`: Buyruqni administrator (root) huquqi bilan bajaradi.
* `apt update`: Linux paket repozitoriylaridagi dasturlarning eng so‘nggi ro‘yxatini yuklab oladi va yangilaydi.
* `apt install -y`: Ko‘rsatilgan paketlarni o‘rnatadi. `-y` (yes) bayrog‘i o‘rnatish jarayonida foydalanuvchidan tasdiqlash (`Do you want to continue? [Y/n]`) so‘ramasdan avtomatik "ha" deb javob beradi.
* `python3`: Asosiy dasturlash tili interpretatori.
* `python3-venv`: Python uchun alohida izolyatsiyalangan virtual muhit yaratish moduli.
* `python3-pip`: Python paketlar menejeri (tashqi kutubxonalarni yuklash uchun).
* `curl`: Buyruqlar satri orqali HTTP so‘rovlar (GET, POST) yuborish vositasi.
* `nano`: Terminalda ishlovchi qulay matn muharriri.
* `open-vm-tools`: VMware va Ubuntu o‘rtasida klipbord, ekran o‘lchami va drayverlar integratsiyasini ta’minlovchi ochiq kodli xizmat.

#### 2-qadam: Loyiha katalogini yaratish va unga o‘tish
```bash
mkdir -p ~/websec/A5
cd ~/websec/A5
```
**Har bir komanda va bayroqchaning vazifasi:**
* `mkdir -p ~/websec/A5`: Foydalanuvchi uy katalogida (`~`) `websec/A5` papkalar zanjirini yaratadi. `-p` (parents) bayrog‘i ota-ona kataloglar mavjud bo‘lmasa, ularni ham xatoliksiz ketma-ket yaratadi.
* `cd ~/websec/A5`: Ishchi katalogni yangi yaratilgan `~/websec/A5` ga o‘zgartiradi.

#### 3-qadam: Python virtual muhitini yaratish va faollashtirish
```bash
python3 -m venv .venv
source .venv/bin/activate
```
**Har bir komanda va bayroqchaning vazifasi:**
* `python3 -m venv .venv`: `venv` moduli yordamida joriy katalogda `.venv` nomli yashirin virtual muhit papkasini yaratadi.
* `source .venv/bin/activate`: Yaratilgan virtual muhitni faollashtiradi. Shundan so‘ng terminal qatorining boshida `(.venv)` belgisi paydo bo‘ladi. Bu o‘rnatiladigan barcha Python paketlar tizimga emas, aynan shu lokal loyihaga tushishini kafolatlaydi.

#### 4-qadam: Laboratoriya kutubxonalarini o‘rnatish
```bash
python -m pip install Flask==3.1.3 SQLAlchemy==2.0.43 mongomock==4.3.0
python -m pip freeze > requirements-lock.txt
```
**Har bir komanda va bayroqchaning vazifasi:**
* `python -m pip install`: Paketlarni o‘rnatish buyrug‘i.
* `Flask==3.1.3`: Veb-server va marshrutlash (routing) uchun yengil veb-freymvork.
* `SQLAlchemy==2.0.43`: SQL bazalar bilan ishlash va ORM imkoniyatlarini taqdim etuvchi zamonaviy Python kutubxonasi.
* `mongomock==4.3.0`: Haqiqiy MongoDB serverini o‘rnatmasdan, uning operatsiyalarini xotirada tezkor simulyatsiya qiluvchi test kutubxonasi.
* `python -m pip freeze > requirements-lock.txt`: O‘rnatilgan barcha paketlar va ularning qat’iy versiyalari ro‘yxatini `requirements-lock.txt` fayliga saqlaydi. `>` belgisi chiqish oqimini faylga yo‘naltiradi.

---

### 3.4. Dastur kodini (`app.py`) yaratish va tahlil qilish

`nano app.py` buyrug‘i orqali fayl oching va quyidagi to‘liq kodni yozing:

```python
import sqlite3
import mongomock
from flask import Flask, abort, jsonify, request
from sqlalchemy import create_engine, select, text
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import Session, mapped_column
from sqlalchemy.pool import StaticPool

# 1. Flask ilovasini yaratish va maksimal so'rov hajmini cheklash (4 KB)
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4096

# 2. Boshlang'ich test ma'lumotlari: 3 ta ochiq va 1 ta maxfiy tovar
DATA = [
    {'id': 1, 'name': 'Daftar', 'public': True},
    {'id': 2, 'name': 'Qalam', 'public': True},
    {'id': 3, 'name': "O'quv qo'llanma", 'public': True},
    {'id': 4, 'name': 'Ichki loyiha', 'public': False},
]
SQL = 'SELECT id, name, public FROM products '

# 3. SQLAlchemy ORM modelini ta'riflash
class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    public: Mapped[bool] = mapped_column(Boolean)

# 4. Xotiradagi (in-memory) SQLite ma'lumotlar bazasini initsializatsiya qilish
engine = create_engine(
    'sqlite://', poolclass=StaticPool,
    connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
with engine.begin() as conn:
    conn.execute(Product.__table__.insert(), DATA)

# 5. Xotiradagi mongomock NoSQL kolleksiyasini yaratish
collection = mongomock.MongoClient().a5.products
collection.insert_many([dict(row) for row in DATA])

# 6. Kiritma tekshiruvi: faqat 1..120 belgili matn bo'lishi shart
def scalar(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 120:
        abort(400, description='name: 1..120 belgili matn kerak')
    return value

# ==================== FUNKSIYALAR: ZAIF VA XAVFSIZ ====================

# [SQL ZAIF]: f-string orqali SQL tuzilgan (SQL Injection mavjud)
def sql_weak(name):
    with engine.connect() as conn:
        query = SQL + f"WHERE name = '{name}' AND public = 1"
        return conn.exec_driver_sql(query).mappings().all()

# [SQL XAVFSIZ]: Parametrli so'rov (? placeholder)
def sql_safe(name):
    with engine.connect() as conn:
        query = SQL + 'WHERE name = ? AND public = 1'
        return conn.exec_driver_sql(query, (name,)).mappings().all()

# [ORM ZAIF]: ORM sessiyasi ichida xom SQL matni ishlatilgan
def orm_weak(name):
    with Session(engine) as session:
        query = SQL + f"WHERE name = '{name}' AND public = 1"
        return session.execute(text(query)).mappings().all()

# [ORM XAVFSIZ]: Model obyektlari va where filtrlari
def orm_safe(name):
    with Session(engine) as session:
        stmt = select(Product).where(
            Product.name == name, Product.public.is_(True))
        return [dict(id=p.id, name=p.name, public=p.public)
                for p in session.scalars(stmt).all()]

# [NoSQL ZAIF]: JSONdagi obyekt to'g'ridan-to'g'ri filtrga berilgan (Operator Injection)
def nosql_weak(body):
    if not isinstance(body, dict) or 'name' not in body:
        abort(400, description='JSON obyektida name kerak')
    query = {'name': body['name'], 'public': True}
    return list(collection.find(query, {'_id': 0}))

# [NoSQL XAVFSIZ]: Maydonlar tekshirilgan, string qat'iy talab qilingan, $eq operatori
def nosql_safe(body):
    if not isinstance(body, dict) or set(body) != {'name'}:
        abort(400, description='Faqat name maydoni kerak')
    name = scalar(body['name'])
    query = {'name': {'$eq': name}, 'public': True}
    return list(collection.find(query, {'_id': 0}))

# Natijalarni tartiblab JSON formatida qaytarish
def result(rows):
    items = sorted([dict(row) for row in rows], key=lambda x: x['id'])
    for item in items:
        item['public'] = bool(item['public'])
    return jsonify(count=len(items), items=items)

# ==================== FLASK ENDPOINTLARI ====================

@app.get('/')
def home():
    return jsonify(lab='A5 / 1-variant',
                   endpoints=['/sql/weak', '/sql/safe',
                              '/orm/weak', '/orm/safe',
                              '/nosql/weak', '/nosql/safe'])

@app.get('/<kind>/<mode>')
def sql_route(kind, mode):
    funcs = {('sql', 'weak'): sql_weak,
             ('sql', 'safe'): sql_safe,
             ('orm', 'weak'): orm_weak,
             ('orm', 'safe'): orm_safe}
    if (kind, mode) not in funcs:
        abort(404)
    name = scalar(request.args.get('name'))
    from sqlalchemy.exc import SQLAlchemyError
    try:
        return result(funcs[kind, mode](name))
    except (SQLAlchemyError, sqlite3.Error):
        return jsonify(error='Sorov bajarilmadi'), 400

@app.post('/nosql/<mode>')
def nosql_route(mode):
    if mode not in ('weak', 'safe'):
        abort(404)
    body = request.get_json(silent=True)
    func = nosql_weak if mode == 'weak' else nosql_safe
    return result(func(body))

@app.errorhandler(400)
def bad_request(error):
    return jsonify(error=error.description), 400

if __name__ == '__main__':
    # Faqat lokal loopback manzilida ishga tushirish
    app.run(host='127.0.0.1', port=8005,
            debug=False, threaded=False)
```

Faylni tekshirish va zaxira nusxasini olish:
```bash
python -m py_compile app.py
cp app.py app_before.py
```
* `python -m py_compile app.py`: Dasturda sintaktik xatolar (SyntaxError, IndentationError) yo‘qligini tekshiradi va baytkod hosil qiladi.
* `cp app.py app_before.py`: Boshlang‘ich zaif kodni keyinchalik solishtirish uchun `app_before.py` nomi bilan zaxiraga oladi.

---

### 3.5. Serverni ishga tushirish va boshlang‘ich holatni tekshirish (1-topshiriq, Dalil D1)

Laboratoriyada qulay ishlash uchun **ikkita terminal oynasi** kerak bo‘ladi:
* **1-terminal (Server terminali):** Serverni ishga tushiradi va konsol xabarlarini ko‘rsatib turadi.
* **2-terminal (Mijoz terminali):** `curl` buyruqlari orqali so‘rovlar yuboriladi va javoblar tahlil qilinadi.

#### 1-terminalda serverni ishga tushiring:
```bash
source .venv/bin/activate
python app.py
```
Server `http://127.0.0.1:8005` manzilida ishga tushadi. Ushbu terminalni yopmang!

#### 2-terminalni oching va dalillar papkasini yarating:
```bash
cd ~/websec/A5
source .venv/bin/activate
mkdir -p evidence
```

Bosh sahifani tekshirish:
```bash
curl --noproxy "*" -i http://127.0.0.1:8005/
```
**Buyruq parametrlari tushuntirishi:**
* `curl`: HTTP so‘rov yuboruvchi dastur.
* `--noproxy "*"`: Barcha tizim proksilarini e’tiborsiz qoldirib, so‘rovni to‘g‘ridan-to‘g‘ri `127.0.0.1` ga yuborishni buyuradi.
* `-i` (include): Javobning HTTP sarlavhalarini (HTTP Status, Content-Type, Content-Length) ham ekranga chiqaradi.

#### 1-topshiriq: Nazorat so‘rovlari (Oddiy nom, yopiq nom va mavjud bo‘lmagan nom)
```bash
# 1. Ochiq tovar: "Daftar"
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=Daftar" | tee evidence/D1_daftar.txt

# 2. Maxfiy/yopiq tovar: "Ichki loyiha"
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=Ichki loyiha" | tee evidence/D1_ichki.txt

# 3. Mavjud bo'lmagan tovar
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=Mavjud emas" | tee evidence/D1_mavjud_emas.txt
```
**Har bir parametrning vazifasi:**
* `-G`: `curl`ga GET so‘rovi tuzishni aytadi va `--data-urlencode`dagi ma’lumotlarni URL manzilining oxiriga query string sifatida (`?name=...`) qo‘shadi.
* `--data-urlencode`: Parametr qiymatidagi bo‘sh joylar, apostroflar va maxsus belgilarni to‘g‘ri URL formatiga o‘tkazadi (masalan, bo‘sh joy `%20` bo‘ladi).
* `| tee evidence/D1_daftar.txt`: `|` (pipe) orqali chiqishni `tee` buyrug‘iga yo‘naltiradi. `tee` natijani bir vaqtning o‘zida ham ekranga chiqaradi, ham faylga yozib qo‘yadi.

**Kutiladigan natija (Dalil D1):**
* `name=Daftar`: `HTTP 200 OK`, `count: 1`, `items: [{"id": 1, "name": "Daftar", "public": true}]`.
* `name=Ichki loyiha`: `HTTP 200 OK`, `count: 0`, `items: []`. (Chunki `public=0`, ko‘rinmasligi shart!).
* `name=Mavjud emas`: `HTTP 200 OK`, `count: 0`, `items: []`.

---

### 3.6. SQL Inyeksiyani sinash va tahlil qilish (2-topshiriq, Dalillar D2–D3)

#### 2-topshiriq: SQL Inyeksiya orqali yopiq ma’lumotlarni sizdirish
Buzg‘unchi kiritmasi: `Daftar' OR 1=1 -- `

```bash
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=Daftar' OR 1=1 -- " | tee evidence/D2_sql_inject.txt
```

**Kutiladigan natija (Dalil D2):**
* `HTTP/1.1 200 OK`
* `count: 4`
* Qaytgan IDlar: `[1, 2, 3, 4]`.
* **Xulosa:** Tizimdagi maxfiy `Ichki loyiha` (ID=4, `public: false`) ham ro‘yxatda chiqib keldi! SQL inyeksiya muvaffaqiyatli amalga oshdi.

#### True / False mantiqiy juftligi testi:
Inyeksiya chindan ham mantiqiy shartga bog‘liqligini isbotlash uchun `AND 1=1` (rost) va `AND 1=2` (yolg‘on) shartlarini yuboramiz:

```bash
# Rost (True) shart:
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=Daftar' AND 1=1 -- " | tee evidence/D2_true.txt

# Yolg'on (False) shart:
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=Daftar' AND 1=2 -- " | tee evidence/D2_false.txt
```
* `AND 1=1`: `HTTP 200 OK`, `count: 1`, `ID: 1` qaytadi (shart rost bo‘lgani uchun Daftar chiqadi).
* `AND 1=2`: `HTTP 200 OK`, `count: 0` qaytadi (chunki `1=2` har doim yolg‘on).

#### Parametrli xavfsiz endpoint bilan taqqoslash (Dalil D3):
```bash
# 1. Xavfsiz endpointga inyeksiya yuborish:
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/safe \
  --data-urlencode "name=Daftar' OR 1=1 -- " | tee evidence/D3_safe_inject.txt

# 2. Xavfsiz endpointga apostrofli qonuniy tovar yuborish:
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/safe \
  --data-urlencode "name=O'quv qo'llanma" | tee evidence/D3_safe_apostrophe.txt

# 3. Zaif endpointga apostrofli qonuniy tovar yuborish:
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=O'quv qo'llanma" | tee evidence/D3_weak_apostrophe.txt
```

**Tahlil va natijalar:**
1. `/sql/safe` da inyeksiya urinishi: `HTTP 200 OK`, `count: 0`. Tizim butun satrni bitta qiymat deb bildi va buzilmadi.
2. `/sql/safe` da `O'quv qo'llanma`: `HTTP 200 OK`, `count: 1`, `ID: 3`. Qonuniy apostrof xatosiz ishlaydi!
3. `/sql/weak` da `O'quv qo'llanma`: `HTTP 400 Bad Request`, `{"error": "Sorov bajarilmadi"}`. Chunki `O'quv` so‘zidagi apostrof SQL sintaksisini buzib, SQLite xatosini keltirib chiqardi!

---

### 3.7. ORM xavfsizligini tekshirish: Xom SQL vs Model ifodasi (3-topshiriq, Dalil D4)

#### 3-topshiriq: ORM endpointlarini tekshirish
```bash
# 1. Zaif ORM endpointiga inyeksiya yuborish:
curl --noproxy "*" -i -G http://127.0.0.1:8005/orm/weak \
  --data-urlencode "name=Daftar' OR 1=1 -- " | tee evidence/D4_orm_weak.txt

# 2. Xavfsiz ORM endpointiga inyeksiya yuborish:
curl --noproxy "*" -i -G http://127.0.0.1:8005/orm/safe \
  --data-urlencode "name=Daftar' OR 1=1 -- " | tee evidence/D4_orm_safe.txt

# 3. Xavfsiz ORM endpointiga apostrofli tovar yuborish:
curl --noproxy "*" -i -G http://127.0.0.1:8005/orm/safe \
  --data-urlencode "name=O'quv qo'llanma" | tee evidence/D4_orm_safe_apostrophe.txt
```

**Natijalar (Dalil D4):**
* `/orm/weak` + inyeksiya: `HTTP 200 OK`, `count: 4` (ID 1–4). ORM ishlatilishiga qaramasdan, xom SQL tufayli yopiq tovar sizib chiqdi!
* `/orm/safe` + inyeksiya: `HTTP 200 OK`, `count: 0`.
* `/orm/safe` + `O'quv qo'llanma`: `HTTP 200 OK`, `count: 1`, `ID: 3`.

---

### 3.8. NoSQL Operator Inyeksiyasini sinash (4-topshiriq, Dalil D5)

NoSQL endpointlari `POST` so‘rovlarini qabul qiladi.

```bash
# 1. Zaif NoSQL endpointiga oddiy nom yuborish:
curl --noproxy "*" -i http://127.0.0.1:8005/nosql/weak \
  -H 'Content-Type: application/json' \
  -d '{"name":"Daftar"}' | tee evidence/D5_nosql_normal.txt

# 2. Zaif NoSQL endpointiga operatorli obyekt inyeksiyasi yuborish:
curl --noproxy "*" -i http://127.0.0.1:8005/nosql/weak \
  -H 'Content-Type: application/json' \
  -d '{"name":{"$ne":null}}' | tee evidence/D5_nosql_inject.txt

# 3. Xavfsiz NoSQL endpointiga o'sha operatorni yuborish:
curl --noproxy "*" -i http://127.0.0.1:8005/nosql/safe \
  -H 'Content-Type: application/json' \
  -d '{"name":{"$ne":null}}' | tee evidence/D5_nosql_safe_reject.txt

# 4. Xavfsiz NoSQL endpointiga qo'shimcha "public" maydoni qo'shib yuborish:
curl --noproxy "*" -i http://127.0.0.1:8005/nosql/safe \
  -H 'Content-Type: application/json' \
  -d '{"name":"Daftar","public":false}' | tee evidence/D5_nosql_safe_extra_field.txt
```
**Buyruq parametrlari tushuntirishi:**
* `-H 'Content-Type: application/json'`: HTTP so‘rov sarlavhasida yuborilayotgan tana (body) JSON formatida ekanligini bildiradi.
* `-d '...'`: POST so‘rovi tanasida yuboriladigan ma’lumot. Bash qobig‘ida `$ne` belgisi o‘zgaruvchi deb talqin qilinmasligi uchun butun JSON bir tirnoq (`'...'`) ichiga olinadi.

**Natijalar (Dalil D5):**
* Zaif endpointda `{"name":{"$ne":null}}`: `HTTP 200 OK`, `count: 3`, IDlar: `[1, 2, 3]`. Barcha ochiq tovarlar chiqdi!
* Nega ID=4 chiqmadi? Chunki serverdagi `public: True` kodi saqlanib qolgan.
* Xavfsiz endpointda: `HTTP 400 Bad Request`, `{"error": "name: 1..120 belgili matn kerak"}`. Server obyektni rad etdi!
* Qo‘shimcha maydonda: `HTTP 400 Bad Request`, `{"error": "Faqat name maydoni kerak"}`.

---

### 3.9. Kodni tuzatish va avvalgi manzillarda qayta sinash (5-topshiriq, Dalil D6)

Endi `app.py` faylidagi uchta zaif funksiyani xavfsiz holatga keltiramiz.

#### 1. Serverni to‘xtating:
1-terminalda `Ctrl+C` tugmalarini bosing.

#### 2. `app.py` faylini tahrirlang:
`nano app.py` orqali faylni oching va `sql_weak`, `orm_weak`, hamda `nosql_weak` funksiyalarini quyidagi xavfsiz kodlarga almashtiring (funksiya nomlarini o‘zgartirmang!):

```python
# Tuzatilgan sql_weak funksiyasi (Parametrli so'rov):
def sql_weak(name):
    with engine.connect() as conn:
        query = SQL + 'WHERE name = ? AND public = 1'
        return conn.exec_driver_sql(query, (name,)).mappings().all()

# Tuzatilgan orm_weak funksiyasi (Model ifodasi):
def orm_weak(name):
    with Session(engine) as session:
        stmt = select(Product).where(
            Product.name == name, Product.public.is_(True))
        return [dict(id=p.id, name=p.name, public=p.public)
                for p in session.scalars(stmt).all()]

# Tuzatilgan nosql_weak funksiyasi (Sxema va tur tekshiruvi):
def nosql_weak(body):
    if not isinstance(body, dict) or set(body) != {'name'}:
        abort(400, description='Faqat name maydoni kerak')
    name = scalar(body['name'])
    query = {'name': {'$eq': name}, 'public': True}
    return list(collection.find(query, {'_id': 0}))
```

Faylni saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`).

Kodni tekshiring va serverni qayta ishga tushiring:
```bash
python -m py_compile app.py
python app.py
```

#### 3. Regressiya sinovlarini o‘tkazish (Aynan `/weak` endpointlarida!):
2-terminalda quyidagi buyruqlarni bajaring:

```bash
# 1. SQL zaif endpointida inyeksiyani qayta sinash:
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=Daftar' OR 1=1 -- " | tee evidence/D6_sql_fixed_inject.txt

# 2. SQL zaif endpointida apostrofli tovar:
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=O'quv qo'llanma" | tee evidence/D6_sql_fixed_apostrophe.txt

# 3. ORM zaif endpointida inyeksiyani qayta sinash:
curl --noproxy "*" -i -G http://127.0.0.1:8005/orm/weak \
  --data-urlencode "name=Daftar' OR 1=1 -- " | tee evidence/D6_orm_fixed_inject.txt

# 4. ORM zaif endpointida apostrofli tovar:
curl --noproxy "*" -i -G http://127.0.0.1:8005/orm/weak \
  --data-urlencode "name=O'quv qo'llanma" | tee evidence/D6_orm_fixed_apostrophe.txt

# 5. NoSQL zaif endpointida operatorni qayta sinash:
curl --noproxy "*" -i http://127.0.0.1:8005/nosql/weak \
  -H 'Content-Type: application/json' \
  -d '{"name":{"$ne":null}}' | tee evidence/D6_nosql_fixed_operator.txt
```

**Kutiladigan natija (Dalil D6):**
* SQL va ORM da `OR 1=1`: Endi `HTTP 200 OK`, `count: 0`. Zaiflik to‘liq bartaraf etildi!
* SQL va ORM da `O'quv qo'llanma`: `HTTP 200 OK`, `count: 1`, `ID: 3`. Qonuniy nom muammosiz topildi.
* NoSQL da `{"name":{"$ne":null}}`: `HTTP 400 Bad Request`, xato xabari qaytadi.

Kodlar farqini (diff) ko‘rish:
```bash
diff -u app_before.py app.py | tee evidence/D6_code_diff.txt
```

---

### 3.10. Qo‘shimcha topshiriq: UNION SELECT inyeksiyasi

UNION SELECT inyeksiyasi orqali joriy natijaga sun’iy qatorlar qo‘shish mumkinligini sinab ko‘ramiz.

Zaif nusxada quyidagi kiritma yuboriladi:
```text
x' UNION SELECT 99, 'TEST', 1 -- 
```

Buyruq:
```bash
curl --noproxy "*" -i -G http://127.0.0.1:8005/sql/weak \
  --data-urlencode "name=x' UNION SELECT 99,'TEST',1 -- "
```

* **Zaif kodda kutiladigan natija:** `HTTP 200 OK`, `count: 1`, `items: [{"id": 99, "name": "TEST", "public": true}]`. Bazada mavjud bo‘lmagan soxta qator hosil qilindi!
* **Tuzatilgan kodda kutiladigan natija:** `HTTP 200 OK`, `count: 0`.

---

### 3.11. Natijalar jadvali (Oldin va Keyin holati)

| Sinov turi va Kiritma (Payload) | Tuzatishdan oldin (`/weak`) | Tuzatishdan keyin (`/weak`) | Natija holati |
| :--- | :--- | :--- | :--- |
| **SQL:** `name=Daftar` | HTTP 200; count: 1; ID=1 | HTTP 200; count: 1; ID=1 | Qonuniy qidiruv saqlangan |
| **SQL:** `name=Daftar' OR 1=1 -- ` | **HTTP 200; count: 4; ID=1–4** | **HTTP 200; count: 0** | **Zaiflik bartaraf etildi** |
| **SQL:** `name=O'quv qo'llanma` | HTTP 400; Xato (buzildi) | HTTP 200; count: 1; ID=3 | Apostrof xavfsiz ishlamoqda |
| **ORM:** `name=Daftar' OR 1=1 -- ` | **HTTP 200; count: 4; ID=1–4** | **HTTP 200; count: 0** | **Zaiflik bartaraf etildi** |
| **ORM:** `name=O'quv qo'llanma` | HTTP 400; Xato (buzildi) | HTTP 200; count: 1; ID=3 | Model ifodasi to‘g‘ri ishladi |
| **NoSQL:** `{"name": "Daftar"}` | HTTP 200; count: 1; ID=1 | HTTP 200; count: 1; ID=1 | Qonuniy JSON saqlangan |
| **NoSQL:** `{"name":{"$ne":null}}` | **HTTP 200; count: 3; ID=1–3** | **HTTP 400; Error** | **Operator inyeksiyasi to‘xtatildi** |
| **SQL/ORM/NoSQL:** `Ichki loyiha` | HTTP 200; count: 0 | HTTP 200; count: 0 | Maxfiy yozuv himoyalangan |

---

### 3.12. Hisobotga qo‘yiladigan talablar va dalillar ro‘yxati

Hisobot individual DOCX yoki PDF formatida tayyorlanadi va quyidagilarni o‘z ichiga oladi:
1. **Titul varag‘i:** Fan nomi, semestr, A5 mavzusi, variant (1-variant), F.I.Sh., guruh va sana.
2. **Ishchi muhit tavsifi:** Host: Ubuntu Linux, VM: Ubuntu Desktop/Server, vCPU, RAM, Python va paket versiyalari (`Flask 3.1.3`, `SQLAlchemy 2.0.43`, `mongomock 4.3.0`), manzil: `http://127.0.0.1:8005/`.
3. **Dalillar to‘plami (Screenshots / Text logs):**
   - **D1:** Boshlang‘ich nazorat so‘rovlari (`Daftar`, `Ichki loyiha`, `Mavjud emas`).
   - **D2:** SQL zaif endpointida `OR 1=1` va yopiq yozuv (ID=4) chiqishi hamda `AND 1=1 / 1=2` juftligi.
   - **D3:** `/sql/safe` da inyeksiya qaytarilishi va apostrofli tovar to‘g‘ri topilishi.
   - **D4:** `/orm/weak` dagi zaiflik va `/orm/safe` dagi xavfsiz natija.
   - **D5:** NoSQL zaif endpointida `{"$ne":null}` natijasida 3 ta tovar chiqishi va xavfsiz endpointdagi HTTP 400.
   - **D6:** Uchta funksiyaning tuzatilgan kodlari (`diff`), qayta sinovlar va amaliy natijalar jadvali.
4. **Xulosa (5–7 gap):** Inyeksiya sabablari, ma’lumot va kod ajratilishi, ORM va NoSQLdagi o‘ziga xosliklar hamda parametrli so‘rovlarning afzalliklari bo‘yicha xulosa.

---

### 3.13. Ko‘p uchraydigan xatolar va ularni bartaraf etish (Troubleshooting)

1. **`curl: (7) Failed to connect to 127.0.0.1 port 8005: Connection refused`**
   - *Sababi:* Flask serveri ishga tushmagan yoki boshqa portda ishlayapti.
   - *Yechim:* 1-terminalda `python app.py` ishga tushganini tekshiring. `curl` so‘rovida port `8005` ekanligiga ishonch hosil qiling.
2. **`ModuleNotFoundError: No module named 'flask'`**
   - *Sababi:* Virtual muhit (`.venv`) faollashtirilmagan.
   - *Yechim:* Buyruqni bajarishdan oldin `source .venv/bin/activate` buyrug‘ini bering.
3. **SQL inyeksiyasi ishlamadi (ID=4 chiqmadi)**
   - *Sababi:* Shell maxsus belgilarni yoki apostroflarni buzib yuborgan yoki `-- ` izoh belgisi oxirida bo‘sh joy qolib ketgan.
   - *Yechim:* `--data-urlencode "name=Daftar' OR 1=1 -- "` ko‘rinishida to‘liq yozing. `--` belgisidan so‘ng albatta bitta bo‘sh joy (space) bo‘lishi shart.
4. **NoSQL so‘rovida xatolik yoki `$ne` o‘zgarmay qoldi**
   - *Sababi:* Bashda qo‘shtirnoq ishlatilgani uchun `$ne` o‘zgaruvchi deb qabul qilingan.
   - *Yechim:* JSON tanasini faqat bittalik tirnoq (`'{"name":{"$ne":null}}'`) ichiga oling.
5. **Kodni tuzatgandan keyin ham eski natija chiqmoqda**
   - *Sababi:* Server to‘xtatilib qayta ishga tushirilmagan (`debug=False` bo‘lgani uchun avtomatik yangilanmaydi).
   - *Yechim:* Server terminalida `Ctrl+C` bosing, `python -m py_compile app.py` bilan tekshiring va `python app.py` ni qayta ishga tushiring.

---

### 3.14. Nazorat savollari va to‘liq, mukammal javoblar

#### 1-savol: SQLdagi `?` placeholder nima uchun qo‘shtirnoqqa olinmaydi? `(name,)` oxiridagi vergul nimani bildiradi?
* **Javob:**
  1. `?` belgisi SQL tahlilchisi (parser) uchun maxsus o‘rin egallovchi (placeholder) hisoblanadi. Agar uni `WHERE name = '?'` deb qo‘shtirnoqqa olsak, ma’lumotlar bazasi uni parametr emas, balki so‘roq belgisi shaklidagi oddiy matn literal deb tushunadi. Shuning uchun `?` qo‘shtirnoqsiz yoziladi.
  2. Python tilida `(name)` ifodasi oddiy qavs ichidagi o‘zgaruvchi hisoblanadi (string turi). Oxiriga vergul qo‘yilgan `(name,)` sintaksisi esa Python’da bitta elementdan iborat **kortej (tuple)** yaratadi. Ma’lumotlar bazasi drayverlari parametrlarni kortej yoki ro‘yxat ko‘rinishida qabul qilishi shart.

#### 2-savol: Nega "O'quv qo'llanma" nomini rad etish (yoki apostrofni o‘chirish) to‘g‘ri himoya emas?
* **Javob:**
  O‘zbek, ingliz va boshqa ko‘plab tillarda apostrof so‘zning ajralmas grammatik qismidir (masalan: `O'quv`, `Ma'lumot`, `O'zbekiston`, `Don't`). Agar tizim apostroflarni taqiqlasa yoki o‘chirib tashlasa:
  - Foydalanuvchilar o‘z mahsulotlarini qonuniy nomi bilan saqlay olmaydi va qidira olmaydi.
  - Bu xavfsizlik emas, balki tizim funksionalligining buzilishi (buzuq arxitektura) hisoblanadi.
  To‘g‘ri yo‘l — apostrofni o‘chirish emas, balki parametrli so‘rovlar orqali apostrofli matnlarni xavfsiz qayta ishlashdir.

#### 3-savol: `session.execute(text(query))` qachon xavfli? Parametrli ORM ifodasi undan nimasi bilan farq qiladi?
* **Javob:**
  - `session.execute(text(query))` funksiyasi, agar `query` o‘zgaruvchisi `f-string` yoki string konkatenatsiyasi (`+`) yordamida foydalanuvchi ma’lumotlari bilan birlashtirilgan bo‘lsa, o‘ta xavflidir. Chunki `text()` funksiyasi SQL matnini avtomatik xavfsizlantirmaydi.
  - Parametrli ORM ifodasi (`select(Product).where(Product.name == name)`) esa obyekt darajasida ishlaydi. U foydalanuvchi kiritmasini SQL matniga qo‘shmaydi, balki drayver darajasida xavfsiz bog‘langan parametr sifatida uzatadi.

#### 4-savol: Nega NoSQL `$ne:null` sinovida 3 ta yozuv chiqdi, SQL `OR` sinovida esa 4 ta?
* **Javob:**
  - SQL inyeksiyasida buzg‘unchi oxiriga izoh (`-- `) belgisini qo‘ydi. Natijada dasturchi yozgan `AND public = 1` sharti butunlay bekor qilindi va hatto maxfiy bo‘lgan `public = 0` yozuvi (ID=4) ham chiqdi (jami 4 ta).
  - NoSQL kiritmasida esa foydalanuvchi faqat `name` maydoni o‘rniga obyekt yubordi. Lekin server kodi tomonidan belgilangan `query = {'name': ..., 'public': True}` filtridagi `'public': True` sharti buzilmadi va saqlanib qoldi. Shu sababli NoSQL bazasi faqat `public: True` bo‘lgan 3 ta ochiq mahsulotni qaytardi, maxfiy ID=4 esa chiqmadi.

#### 5-savol: Parametrli so‘rov `public` kabi ko‘rinish shartining (ruxsat nazoratining) o‘rnini bosa oladimi?
* **Javob:**
  Yo‘q, bosa olmaydi! Parametrli so‘rov — bu faqat **so‘rov sintaksisini (tuzilmasini)** buzilishdan himoya qiluvchi vositadir. Ko‘rinish sharti (`public = 1`) esa **biznes mantiqi va ruxsat nazorati (Access Control)** qoidasidir. Ular bir-birining o‘rnini bosmaydi, balki bir-birini to‘ldiradi.

#### 6-savol: Stored Procedure va "faqat xatoni yashirish" nega avtomatik himoya kafolati emas?
* **Javob:**
  1. Agar Stored Procedure (saqlanadigan protsedura) ichida dinamik SQL (`EXECUTE IMMEDIATE` yoki `sp_executesql`) formatlash orqali yozilgan bo‘lsa, inyeksiya xuddi oddiy so‘rovdagi kabi sodir bo‘laveradi.
  2. Xato xabarlarini yashirish (masalan, foydalanuvchiga faqat HTTP 500 yoki umumiy xato ko‘rsatish) zaiflikni tuzatmaydi, balki faqat uni ko‘rinmas qiladi. Tajribali buzg‘unchi "Blind SQL Injection" (mantiqiy yoki vaqtga asoslangan inyeksiya) usullari orqali ma’lumotlarni o‘g‘irlashda davom etaveradi.

---

## 4. FOYDALANILGAN VA TAVSIYA ETILADIGAN MANBALAR

1. **OWASP SQL Injection Prevention Cheat Sheet:**  
   [https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)  
   *(Relyatsion bazalarda parametrli so‘rovlar va himoyalanish strategiyalari bo‘yicha dunyo standarti).*

2. **OWASP NoSQL Injection Prevention Cheat Sheet:**  
   [https://cheatsheetseries.owasp.org/cheatsheets/NoSQL_Injection_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/NoSQL_Injection_Prevention_Cheat_Sheet.html)  
   *(Hujjatli ma’lumotlar bazalarida operatorlar inyeksiyasi va kiritma tekshiruvlari).*

3. **SQLAlchemy 2.0 Documentation — Using SELECT Statements & Working with Data:**  
   [https://docs.sqlalchemy.org/en/20/core/selectable.html](https://docs.sqlalchemy.org/en/20/core/selectable.html)  
   *(SQLAlchemy ORMda xavfsiz `select()` va `where()` ifodalarini tuzish qo‘llanmasi).*

4. **MongoDB Manual — Query and Projection Operators (`$ne`, `$eq`):**  
   [https://www.mongodb.com/docs/manual/reference/operator/query/ne/](https://www.mongodb.com/docs/manual/reference/operator/query/ne/)  
   *(MongoDB so‘rov operatorlari xususiyatlari va ularning ishlash mexanizmi).*

5. **mongomock GitHub Repository & Documentation:**  
   [https://github.com/mongomock/mongomock](https://github.com/mongomock/mongomock)  
   *(Sinov muhitlari uchun mo‘ljallangan MongoDB xotiraviy emulyatori imkoniyatlari).*

6. **Python Official Documentation — `sqlite3` Module Placeholders:**  
   [https://docs.python.org/3/library/sqlite3.html](https://docs.python.org/3/library/sqlite3.html)  
   *(Python standart kutubxonasida SQL parametrlarini `?` orqali xavfsiz uzatish qoidalari).*

7. **Common Weakness Enumeration (CWE):**
   - **CWE-89:** Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection').
   - **CWE-943:** Improper Neutralization of Special Elements in Data Query Logic ('NoSQL Injection').
   - **CWE-564:** SQL Injection: Hibernate / ORM.
