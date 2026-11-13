# AMALIY TOPSHIRIQNI BAJARISH VA SKRINSHOTLARNI YIG‘ISH TALABLARI (`talab.md`)

Ushbu hujjat sizga amaliy ishlarni o‘zingizning **Ubuntu (VMware)** muhitingizda mustaqil bajarishingiz va natijaviy **hisobot.docx** faylini tayyorlab berishim uchun zarur bo‘lgan rasmlarni yig‘ish bo‘yicha aniq yo‘riqnomani taqdim etadi.

---

## 1. SIZNING ISHCHI MUHITINGIZ VA VAZIFANGIZ
- **Tizim:** Ubuntu (VMware ichidagi Ubuntu Server yoki Desktop). Windows 11 kerak emas!
- **Tarmoq:** Shaxsiy lokal Wi-Fi (universitet proksisiz, to‘g‘ridan-to‘g‘ri NAT).
- **Vazifangiz:** `~/a8-lab` papkasida API serverni ishga tushirish, 5 ta bosqichdagi buyruqlarni bajarish va har bir bosqich natijasini terminal skrinshoti qilib `images/` papkasiga saqlash.

---

## 2. RASMLARNI NOMERLASH VA PAPKAGA JOYLASH TARTIBI

Loyiha papkasida `images` nomli papka oching:
```bash
mkdir -p images
```

Unga quyidagi **5 ta skrinshotni** aniq ko‘rsatilgan nomlar bilan saqlab bering:

### 📸 1. `images/1_d1_muhit.png` (Dalil D1)
- **Qachon olinadi:** Server ishga tushirilgach va 2-terminalda dastlabki sozlashlar qilingach.
- **Skrinshotda nimalar ko‘rinishi shart:**
  1. `uname -a` yoki Python/paket versiyalari (`python -m pip list` yoki Flask/PyJWT versiyasi).
  2. Serverning `http://127.0.0.1:8008` manzilida ishlayotgani.
  3. `curl -i "$BASE/"` ning `200 OK` javobi.
  4. `curl -i -H "Authorization: Bearer $ALI" "$BASE/api/me"` ning `200 OK` (`sub=ali`, `role=student`) javobi.

### 📸 2. `images/2_d2_jwt.png` (Dalil D2)
- **Qachon olinadi:** 7 xil token bilan `/api/me` tekshirilganda.
- **Skrinshotda nimalar ko‘rinishi shart:**
  - Ketma-ket yuborilgan 7 ta `curl` buyrug‘i va ularning HTTP statuslari:
    1. Tokensiz -> `401 Unauthorized` (`WWW-Authenticate: Bearer`)
    2. `$ALI` -> `200 OK`
    3. `$TAMPERED` -> `401 Unauthorized`
    4. `$EXPIRED` -> `401 Unauthorized`
    5. `$WRONG_AUD` -> `401 Unauthorized`
    6. `$WRONG_ISS` -> `401 Unauthorized`
    7. `$NO_EXP` -> `401 Unauthorized`

### 📸 3. `images/3_d3_bola.png` (Dalil D3 — BOLA zaifligi va himoyasi)
- **Qachon olinadi:** Buyurtmalar endpointi tekshirilganda.
- **Skrinshotda nimalar ko‘rinishi shart:**
  1. `curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/orders/101"` -> `200 OK` (Daftar).
  2. `curl -i -H "Authorization: Bearer $ALI" "$BASE/api/weak/orders/202"` -> `200 OK` (**owner=vali, BOLA fosh bo‘ldi!**).
  3. `curl -i -H "Authorization: Bearer $ALI" "$BASE/api/safe/orders/202"` -> `403 Forbidden` (**Himoya ishladi!**).
  4. `curl -i -H "Authorization: Bearer $VALI" "$BASE/api/safe/orders/202"` -> `200 OK` (Qonuniy egasi).
  5. `curl -i -H "Authorization: Bearer $ADMIN" "$BASE/api/safe/orders/202"` -> `200 OK` (Admin huquqi).

### 📸 4. `images/4_d4_bfla_apikey.png` (Dalil D4 — BFLA zaifligi va API Kaliti)
- **Qachon olinadi:** Admin endpointi va API kaliti tekshirilganda.
- **Skrinshotda nimalar ko‘rinishi shart:**
  1. `ALI` bilan `/api/weak/admin/summary` -> `200 OK` (**A8-ADMIN, BFLA fosh bo‘ldi!**).
  2. `ALI` bilan `/api/safe/admin/summary` -> `403 Forbidden` (**Himoya ishladi!**).
  3. `ADMIN` bilan `/api/safe/admin/summary` -> `200 OK`.
  4. API kalitsiz `/api/integration/ping` -> `401 Unauthorized` (`WWW-Authenticate: ApiKey`).
  5. To‘g‘ri `X-API-Key` bilan `/api/integration/ping` -> `200 OK` (`status=ok`).
  6. `$ALI` Bearer bilan integratsiyaga so‘rov -> `401 Unauthorized`.
  7. API kaliti bilan `/api/me` ga so‘rov -> `401 Unauthorized`.

### 📸 5. `images/5_d5_tuzatish.png` (Dalil D5 — Rate Limiting va Tuzatishlar)
- **Qachon olinadi:** Rate limiting sinovi va `app.py` tuzatilgandan so‘ng.
- **Skrinshotda nimalar ko‘rinishi shart:**
  1. Bash sikli orqali `safe` rejimida ketma-ket 6 ta so‘rov yuborilganda: `200, 200, 200, 200, 200, 429`.
  2. `curl -i` bilan `safe/catalog` ga so‘rov -> `429 Too Many Requests` va `Retry-After: ...` sarlavhasi.
  3. Ayni paytda `VALI` bilan so‘rov -> `200 OK` (alohida kvota).
  4. `app.py`dagi 3 ta funksiya (`order_weak`, `admin_weak`, `limit_weak`) tuzatilib server qayta ishga tushirilgach:
     - `ALI` bilan `/weak/orders/202` -> endi `403 Forbidden`!
     - `ALI` bilan `/weak/admin/summary` -> endi `403 Forbidden`!
     - `/weak/catalog` ga 6 ta so‘rov -> `200 x 5, 429`!

---

## 3. KEYINGI BOSQICH: SIZ RASMLARNI TASHLAGANINGIZDAN KEYIN NIMA BO‘LADI?

Siz amallarni bajarib, yuqoridagi 5 ta rasmni `images/` papkasiga joylashtirib menga xabar berishingiz bilan:
1. Men barcha rasmlarni tekshiraman.
2. `python-docx` kutubxonasi orqali rasmiy formatdagi **hisobot.docx** faylini shakllantirib beraman.
3. Hisobot ichida:
   - Standart Titul varag‘i;
   - Ishchi muhit va arxitektura tahlili;
   - Har bir rasmni (D1 dan D5 gacha) tartib bilan o‘z joyiga joylashtirib, tagiga texnik tushuntirish;
   - Kodlarning oldingi va keyingi holati (`diff`);
   - **D6 yakuniy taqqoslash jadvali** (100% to‘liq);
   - Nazorat savollariga batafsil 6 ta ilmiy javob;
   - Qo‘shimcha topshiriqlar (GraphQL va Multi-worker/Redis tahlili, xavfsiz ma'lumot tiklash);
   - 10 ballik mezonni to‘liq qondiruvchi xulosa va rasmiy adabiyotlar ro‘yxati kiritiladi.

Barcha bosqichlarning mukammal tafsilotlari va kodlar uchun [description.md](file:///home/maxfull/Downloads/507-LAB/projects/web-application-security-labs/A8_project/description.md) fayliga qarang!
