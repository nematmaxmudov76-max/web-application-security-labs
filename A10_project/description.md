# A10. Veb Kesh, CDN va HTTP Protokoliga Oid Zamonaviy Hujumlar
## 1-Variant: Kesh kaliti, shaxsiy javob va HTTP so‘rov chegarasini tekshirish

---

## MUNDARIJA
1. [Laboratoriya Pasporti va Ish Muhiti](#1-laboratoriya-pasporti-va-ish-muhiti)
   - 1.1. VM va Tarmoq Konfiguratsiyasi (Ubuntu Host -> VMware -> Ubuntu Server)
   - 1.2. Lokal Wi-Fi Tarmog'ining Xususiyatlari
   - 1.3. Windows 11 Desktop VM bo'yicha Tushuntirish
2. [1-QISM: Mavzuning Maqsadi va Ahamiyati](#2-1-qism-mavzuning-maqsadi-va-ahamiyati)
   - 2.1. Mavzuning Asosiy Maqsadi
   - 2.2. Veb Kesh va CDN Hujumlarining Dolzarbligi
   - 2.3. Kutiladigan O'quv Natijalari va Kompetensiyalar
3. [2-QISM: Har Bir Mavzu Bo'yicha Mukammal Qo'llanma](#3-2-qism-har-bir-mavzu-boyicha-mukammal-qollanma)
   - 3.1. Veb Kesh va CDN Arxitekturasi (Edge vs Origin)
   - 3.2. Kesh Kaliti (Cache Key) va Unkeyed Inputs (Keshlanmagan Kiritmalar)
   - 3.3. Web Cache Poisoning (Keshni Zaharlash)
   - 3.4. Web Cache Deception (Keshni Aldash)
   - 3.5. Himoya Strategiyalari (Hardening & Mitigation)
   - 3.6. Qonuniy Keshlash va CDN Siyosat Kartasi
   - 3.7. HTTP Request Smuggling (CL.TE va TE.CL Chegaralar Nomuvofiqligi)
4. [3-QISM: Mashqni Bosqichma-Bosqich Bajarish va Har Bir CLI Buyruq Tahlili](#4-3-qism-mashqni-bosqichma-bosqich-bajarish-va-har-bir-cli-buyruq-tahlili)
   - 4.1. 0-Bosqich: Ish Muhitini Tayyorlash va Paketlarni O'rnatish
   - 4.2. 1-Bosqich: Fayllarni Shakllantirish va Dastlabki Serverni Ishga Tushirish (D1 Dalili)
   - 4.3. 2-Bosqich: Oddiy Keshlash va Web Cache Poisoning Hujumi (D2 Dalili)
   - 4.4. 3-Bosqich: Web Cache Deception Hujumi va Shaxsiy Ma'lumotlarni O'g'irlash (D3 Dalili)
   - 4.5. 4-Bosqich: Himoya Mexanizmlarini Sozlash va Qayta Sinov (D4 Dalili)
   - 4.6. 5-Bosqich: Qonuniy Ochiq Resurslarni Tekshirish va CDN Siyosat Kartasi (D5 Dalili)
   - 4.7. 6-Bosqich: HTTP Request Smuggling Bayt Modelini Tahlil Qilish (D6 Dalili)
   - 4.8. 7-Bosqich: Dalillarni Rasmilashtirish va Hisobot Qoidalari
   - 4.9. Texnik Muammolarni Hal Qilish (Troubleshooting)
   - 4.10. Nazorat Savollari va Ilmiy Asoslangan Javoblar
5. [4-QISM: Rasmiy Manbalar va Foydalanilgan Adabiyotlar](#5-4-qism-rasmiy-manbalar-va-foydalanilgan-adabiyotlar)

---

## 1. LABORATORIYA PASPORTI VA ISH MUHITI

| Ko‘rsatkich | Mashg‘ulot Sharti / Parametri |
| :--- | :--- |
| **Fan / Semestr** | Veb dasturlar xavfsizligi / 5-semestr |
| **Mavzu kodi va nomi** | A10 — Veb kesh, CDN va HTTP protokoliga oid zamonaviy hujumlar |
| **Variant** | 1-VARIANT — Kesh kaliti, shaxsiy javob va HTTP so‘rov chegarasini tekshirish |
| **Ajratilgan vaqt / Baho** | 80 daqiqa (muhit tayyor bo'lgandan so'ng) / 10 ball |
| **Asosiy Kompyuter (Host OS)** | **Ubuntu Linux** (Windows emas!) |
| **Virtualizator** | **VMware Workstation for Linux** |
| **Mehmon Tizim (Guest VM)** | **Ubuntu Server 24.04 LTS** (2 vCPU, 4 GB RAM, 25 GB SSD) |
| **Tarmoq Rejimi (Network)** | **NAT Adapter**; Shaxsiy **Lokal Wi-Fi** (Universitet Wi-Fi emas) |
| **Sinov manzillari** | Faqat lokal loopback: `127.0.0.1:8080` (Edge) va `127.0.0.1:8010` (Origin) |

### 1.1. VM va Tarmoq Konfiguratsiyasi (Ubuntu Host -> VMware -> Ubuntu Server)
Ushbu laboratoriya ishi **Ubuntu Host** operatsion tizimi ustida o'rnatilgan **VMware Workstation** dasturi ichidagi **Ubuntu Server 24.04 LTS** virtual mashinasida bajariladi:
* Hech qanday Windows buyruqlari (PowerShell yoki cmd) ishlatilmaydi; barcha amallar Linux Bash qobig'ida bajariladi.
* Virtual mashina tarmog'i VMware'da **NAT (VMnet8)** rejimida sozlanadi. Bu rejim mehmon Ubuntu Server tizimiga internetga (paketlar yuklab olish uchun) chiqish imkonini beradi va shu bilan birga tashqi tarmoqdan virtual mashinani izolyatsiya qiladi.
* Mashg'ulot davomida barcha HTTP so'rovlar virtual mashinaning ichki loopback interfeysi (`127.0.0.1` yoki `localhost`) orqali yuboriladi.

### 1.2. Lokal Wi-Fi Tarmog'ining Xususiyatlari
Siz universitetning korporativ Wi-Fi tarmog'idan emas, balki o'zingizning **shaxsiy/lokal Wi-Fi** tarmog'ingizdan foydalanmoqdasiz:
1. **Cheklovlarsiz Internet:** Universitet tarmoqlarida odatda HTTP/HTTPS proksilari (Corporate Proxy), Captive Portal yoki port blokirovkalari bo'ladi. Shaxsiy Wi-Fi tarmog'ingizda bu kabi to'siqlar yo'q, shuning uchun `sudo apt update` va `sudo apt install` to'g'ridan-to'g'ri, tezkor ishlaydi.
2. **Proksi chalkashligining oldini olish:** Agar tizimingizda global proksi o'zgaruvchilari (`http_proxy`, `https_proxy`) o'rnatilgan bo'lsa ham, laboratoriyadagi barcha `curl` buyruqlarida `--noproxy "*"` kaliti qo'llanilgan. Bu orqali `curl` mahalliy `127.0.0.1` portlariga to'g'ridan-to'g'ri murojaat qiladi va lokal Wi-Fi yoki tizim proksisi so'rovlarga aslo xalaqit bermaydi.
3. **Mustaqil Sinov:** Sinovlar tashqi serverlar yoki haqiqiy pullik CDN (Cloudflare, Akamai, Fastly) akkauntlariga bog'liq emas. Laboratoriya arxitekturasi o'z-o'zini ta'minlovchi (self-contained) yopiq model hisoblanadi.

### 1.3. Windows 11 Desktop VM bo'yicha Tushuntirish
Sizning VMware ichida Windows 11 Desktop virtual mashinangiz sozlangan, ammo:
* **Ushbu A10 laboratoriyasi uchun Windows 11 mutlaqo shart emas!**
* **Nega brauzer emas, faqat Ubuntu Server va curl kerak?**
  Zamonaviy veb brauzerlar (Chrome, Edge, Firefox) o'zlarining ichki, agressiv kesh tizimiga (Disk Cache, Memory Cache, Service Worker kesh) ega. Agar siz brauzer orqali test qilsangiz, brauzer serverga so'rov yubormasdan o'zining keshidan javob qaytarishi va Edge keshdagi haqiqiy `MISS`, `HIT`, `BYPASS` holatlarini ko'rishga to'sqinlik qilishi mumkin.
* **curl vositasining ustunligi:** `curl` har bir so'rovni alohida, toza holda yuboradi, sarlavhalarni aniq boshqarish (`-H`), Cookie yuborish/yubormaslik va kesh xatti-harakatini 100% ob'ektiv o'rganish imkonini beradi.
* *(Qo'shimcha imkoniyat)*: Agar xohlasangiz, tajriba yakunida Windows 11 brauzeri orqali Ubuntu Server IP manziliga murojaat qilib ko'rishingiz mumkin, biroq rasmiy 80 daqiqalik topshiriq va 10 ballik mezon to'liq **Ubuntu Server terminalida `curl` orqali** bajarishga mo'ljallangan.

---

## 2. 1-QISM: MAVZUNING MAQSADI VA AHAMIYATI

```
+-------------------------------------------------------------------------------+
|                       VEB KESH VA PROTOKOL XAVFSIZLIGI                        |
+-------------------------------------------------------------------------------+
|                                                                               |
|   +-------------------+         HTTP So'rov         +---------------------+   |
|   |   Foydalanuvchi   | --------------------------> |      Edge Kesh      |   |
|   |   (curl mijoz)    | <-------------------------- |    (Reverse Proxy)  |   |
|   +-------------------+          HTTP Javob         +---------------------+   |
|                                                            |       ^          |
|                                                       MISS |       | Javob    |
|                                                            v       |          |
|                                                     +---------------------+   |
|                                                     |    Origin Server    |   |
|                                                     |   (Backend xizmat)  |   |
|                                                     +---------------------+   |
+-------------------------------------------------------------------------------+
```

### 2.1. Mavzuning Asosiy Maqsadi
Ushbu laboratoriya mashg'ulotining bosh maqsadi — zamonaviy ko'p qatlamli veb infratuzilmalarda **oraliq kesh (Edge Kesh / CDN / Reverse Proxy)** bilan **asosiy server (Origin Server)** o'rtasidagi so'rov va javoblarni talqin qilishdagi nomuvofiqliklar (desynchronization) qanday jiddiy xavfsizlik oqibatlariga olib kelishini amaliy tajribada ko'rsatishdan iborat.

Mashg'ulot quyidagi asosiy masalalarni qamrab oladi:
1. **Web Cache Poisoning (Keshni zaharlash):** Kesh kalitiga kirmagan (unkeyed) sarlavhalar orqali keshga soxtalashtirilgan yoki zararli kontentni kiritish va uni boshqa barcha begunoh foydalanuvchilarga tarqatish mexanizmini tahlil qilish.
2. **Web Cache Deception (Keshni aldash):** Statik yo'l kengaytmalari (masalan, `.css`) orqali oraliq keshni chalg'itib, dinamik shaxsiy ma'lumotlarni (autentifikatsiya qilingan foydalanuvchi ma'lumotlari, maxfiy tokenlar) umumiy keshga saqlanishiga erishish va uni ruxsatsiz egallash.
3. **Himoyalangan Kesh Siyosatini Sozlash:** Oq ro'yxat (whitelist), sarlavhalarni tozalash (sanitization) va qat'iy HTTP marshrutlash qoidalarini kiritish orqali zaifliklarni bartaraf etish, shu bilan birga qonuniy statik resurslarning keshlanish samaradorligini saqlab qolish.
4. **HTTP Request Smuggling (Bayt darajasida tahlil):** HTTP/1.1 spetsifikatsiyasidagi `Content-Length` (CL) va `Transfer-Encoding: chunked` (TE) sarlavhalarining ikki xil parser tomonidan turlicha tushunilishi natijasida xabarlar chegarasining (framing) buzilishini matematik va baytma-bayt darajada hisoblash.

### 2.2. Veb Kesh va CDN Hujumlarining Dolzarbligi
Zamonaviy veb ilovalar yuqori tezlik va yuklamani ko'tarish uchun Cloudflare, Fastly, Akamai, AWS CloudFront, Nginx yoki Varnish kabi oraliq kesh tizimlariga tayanadi.
* **Xavfning ildizi:** Kesh serveri mijozning so'rovi va serverning javobini to'liq semantik tushunmaydi; u faqat o'ziga berilgan evristik qoidalar (sarlavhalar, URL kengaytmalari) asosida qaror chiqaradi.
* **Origin va Edge nomutanosibligi:** Agar Origin server biror sarlavhani (masalan, `X-Lab-Banner`) javob generatsiyasida ishlatsa, lekin Edge kesh uni kesh kalitiga (Cache Key) kiritmasa, kesh zaharlanadi. Yoki Origin server yo'ldagi `/account/report.css` so'rovini `/account` sifatida dinamik bajarib shaxsiy sahifani chiqarsa, Edge esa `.css` so'zini ko'rib uni "statik ochiq fayl" deb keshlab qo'ysa, shaxsiy hisob ma'lumotlari butun internetga sizib chiqadi.
* **Request Smuggling xavfi:** Frontend va Backend serverlar o'rtasidagi yagona TCP sessiyasida xabar uzunligini aniqlashdagi nomuvofiqlik tajovuzkorga so'rovlar ketma-ketligini o'g'irlash, keshni zaharlash yoki boshqa foydalanuvchilarning sessiya kukilarini (cookies) tutib olish imkonini beradi.

### 2.3. Kutiladigan O'quv Natijalari va Kompetensiyalar
Mashg'ulot yakunida talaba quyidagi bilimlarni to'liq o'zlashtiradi:
* `MISS`, `HIT` va `BYPASS` kesh holatlarini HTTP sarlavhalari (`X-Lab-Cache`, `Age`, `Cache-Control`) va origin hisoblagichi (`X-Origin-Id`) orqali isbotlash.
* Kesh kalitining (Cache Key) tuzilishi va unkeyed parametrlarning xavfliligini tushuntirish.
* Cache Poisoning va Cache Deception zaifliklarining konseptual farqini ajrata olish (biri ma'lumot butunligini buzadi, ikkinchisi maxfiylikni sizdiradi).
* `settings.json` sozlamalari orqali xavfsizlik choralarini joriy etish (`trust_banner=false`, `loose_routes=false`, `safe_cache=true`).
* RFC 9111 (HTTP Caching) va RFC 9112 (HTTP/1.1 Framing) standartlarining xavfsizlik talablarini tushunish.
* HTTP bayt oqimida (byte stream) `\r\n\r\n` ajratuvchisi, Content-Length va Chunked framing bo'yicha hisob-kitoblarni amalga oshirish.

---

## 3. 2-QISM: HAR BIR MAVZU BO'YICHA MUKAMMAL QO'LLANMA

### 3.1. Veb Kesh va CDN Arxitekturasi (Edge vs Origin)

Laboratoriya muhiti bitta Python jarayoni ichida ikkita mustaqil HTTP serverni ishga tushiradi:
1. **Edge Server (Port 8080):** Foydalanuvchi (curl) bilan to'g'ridan-to'g'ri muloqot qiluvchi kesh serveri (Reverse Proxy / CDN Edge Node). U so'rovlarni qabul qiladi, keshda nusxa bor-yo'qligini tekshiradi, bo'lmasa Originga murojaat qiladi.
2. **Origin Server (Port 8010):** Asosiy backend server. U haqiqiy mantiqni bajaradi: shaxsiy foydalanuvchi hisobini boshqaradi, statik CSS faylni uzatadi yoki ochiq sahifani shakllantiradi.

```
       Mijoz (curl)
            |
            | 1. HTTP GET /public?case=p1
            v
   +------------------+
   |    Edge Kesh     |  (Port 8080)
   |  Kesh tekshiruvi |
   +------------------+
     |              ^
     | 2. MISS      | 3. HTTP 200 Javob
     v              |    X-Origin-Id: 1
   +------------------+
   |  Origin Server   |  (Port 8010)
   +------------------+
```

#### Kesh Holatlari (Cache States):
* **MISS:** Kesh kaliti bo'yicha xotirada saqlangan ma'lumot topilmadi. Edge server so'rovni Originga yo'naltiradi, javobni oladi, mijozga uzatadi va belgilangan qoidalarga muvofiq bo'lsa, xotirada saqlab qo'yadi (`X-Lab-Cache: MISS`, `Age: 0`).
* **HIT:** Kesh kaliti bo'yicha mos keluvchi va muddati o'tmagan (TTL < 300s) javob keshda mavjud. Edge server Origin serverga murojaat qilmasdan, saqlangan nusxani mijozga qaytaradi (`X-Lab-Cache: HIT`, `Age: N`).
* **BYPASS:** So'rov yoki javob kesh siyosatiga ko'ra keshlanishi taqiqlangan (masalan, autentifikatsiya qilingan, dinamik yo'l yoki 404/401 xatolik). So'rov to'g'ridan-to'g'ri Originga uzatiladi va qaytgan javob umumiy keshga saqlanmaydi (`X-Lab-Cache: BYPASS`).

#### `X-Origin-Id` sarlavhasining ahamiyati:
`X-Origin-Id` — bu Origin server har safar yangi GET so'rovini qabul qilganda oshirib boradigan global butun sonli hisoblagich (`Origin.count += 1`).
* Agar siz bir xil URL ga ketma-ket ikkita so'rov yuborsangiz va ikkinchi so'rovda `X-Origin-Id` birinchi so'rovdagi raqam bilan aynan bir xil bo'lsa hamda `X-Lab-Cache: HIT` kelsa, bu so'rov Origin serverga yetib bormasdan to'g'ridan-to'g'ri Edge keshdan qaytganining inkor etib bo'lmas isbotidir!
* `X-Origin-Id` foydalanuvchi identifikatori (User ID) emas!

---

### 3.2. Kesh Kaliti (Cache Key) va Unkeyed Inputs

Har qanday kesh tizimi kiruvchi HTTP so'rovini saqlangan javob bilan bog'lash uchun **Kesh Kaliti (Cache Key)** dan foydalanadi.

Ushbu laboratoriyada `lab.py` dagi kesh kaliti quyidagicha tuzilgan:
```python
key = ('GET', self.headers.get('Host', ''), self.path)
```
Ya'ni kalit quyidagi 3 elementdan iborat:
1. HTTP Metod: Faqat `GET`.
2. Host sarlavhasi: Masalan, `127.0.0.1:8080`.
3. To'liq yo'l va query string: Masalan, `/public?case=p1`.

#### Kesh Kalitiga Kirmagan Kiritmalar (Unkeyed Inputs):
* `X-Lab-Banner` — maxsus sarlavha.
* `Cookie` — foydalanuvchi sessiyasi.
* `Authorization` — avtorizatsiya tokenlari.

> [!IMPORTANT]
> **Asosiy qoida:** Agar veb ilovaning Origin serveri HTTP javobini generatsiya qilishda kesh kalitiga kirmagan biror parametrga (unkeyed input) tayansa, ushbu ilovada **Web Cache Poisoning** zaifligi yuzaga keladi!

---

### 3.3. Web Cache Poisoning (Keshni Zaharlash)

#### Hujum sxemasi:
```
1. Tajovuzkor:
   GET /public?case=p1 HTTP/1.1
   Host: 127.0.0.1:8080
   X-Lab-Banner: A10-MARKER   <-- [Unkeyed Input]

2. Edge Kesh:
   - Kalit: ('GET', '127.0.0.1:8080', '/public?case=p1')
   - Keshda yo'q (MISS).
   - trust_banner=true bo'lgani sababli sarlavhani Originga uzatadi.

3. Origin Server:
   - Sarlavhani o'qiydi va javob tanasiga qo'shadi: "PUBLIC banner=A10-MARKER"
   - Cache-Control: public, max-age=300 qaytaradi.

4. Edge Kesh:
   - Javobni yuqoridagi kalit bo'yicha kesh xotirasiga saqlaydi!

5. Begunoh Qurbon:
   GET /public?case=p1 HTTP/1.1
   Host: 127.0.0.1:8080
   (X-Lab-Banner sarlavhasini yubormaydi!)

6. Edge Kesh:
   - Kalit: ('GET', '127.0.0.1:8080', '/public?case=p1') mos keldi!
   - Natija: HIT!
   - Javob: "PUBLIC banner=A10-MARKER" qaytariladi!
```

**Natija:** Begunoh foydalanuvchi hech qanday zararli sarlavha yubormagan bo'lsa ham, keshdan tajovuzkor tomonidan "zaharlangan" javobni qabul qiladi. Real hayotda bu yerda zararli JavaScript kodi (Stored XSS via Cache) yoki soxta fishing havolalari tarqatilishi mumkin.

---

### 3.4. Web Cache Deception (Keshni Aldash)

Web Cache Deception hujumida tajovuzkor keshga zararli kontent kiritmaydi, aksincha **begunoh foydalanuvchining shaxsiy ma'lumotlarini keshga tushirishga** erishadi.

#### Zaiflikning ikki asosiy omili:
1. **Origin marshrutlashidagi xatolik (Path Confusion):**
   Origin serverda marshrutlash kodi quyidagicha yozilgan:
   ```python
   elif path == '/account' or (CFG['loose_routes'] and path.startswith('/account/')):
   ```
   Agar `loose_routes: true` bo'lsa, foydalanuvchi `/account/report.css` manziliga murojaat qilganda, Origin server `path.startswith('/account/')` shartini rost deb topadi va uni oddiy `/account` deb hisoblab, foydalanuvchining shaxsiy profilini (`DEMO-ALICE`) qaytaradi!
2. **Edge keshning statik fayl kengaytmasiga ko'r-ko'rona ishonishi:**
   Edge serverida keshga ruxsat berish kodi:
   ```python
   eligible = path == '/public' or path.endswith('.css')
   ```
   Edge URL oxirida `.css` qo'shimchasini ko'rib, uni statik uslub fayli deb o'ylaydi.
3. **Cache-Control sarlavhasini e'tiborsiz qoldirish:**
   Origin server javobda `Cache-Control: private, no-store` deb qaytargan bo'lsa-da, Edge serverida `safe_cache: false` bo'lgani sababli ushbu xavfsizlik sarlavhasini tekshirmaydi va javobni keshga saqlab qo'yadi!

#### Oqibati:
Hujumchi Alice nomidan yuborilgan keshlanib qolgan `/account/report.css?case=d1` manziliga **hech qanday kukisiz (Cookie yo'q)** oddiy so'rov yuboradi va Alice'ning maxfiy kodini (`code=DEMO-ALICE`) keshdan qo'lga kiritadi! Agar u to'g'ridan-to'g'ri Originga shunday so'rov yuborsa, 401 Unauthorized xatosi olar edi.

---

### 3.5. Himoya Strategiyalari (Hardening & Mitigation)

Tizimni ushbu zaifliklardan to'liq himoya qilish uchun `settings.json` faylida uchta parametr o'zgartiriladi:

```json
{
  "trust_banner": false,
  "loose_routes": false,
  "safe_cache": true
}
```

Ushbu uchala himoya mexanizmining ishlash tamoyili:

1. **`trust_banner: false` (Keshni zaharlashga qarshi):**
   Edge kesh mijozdan kelgan `X-Lab-Banner` sarlavhasini Originga o'tkazmaydi (strip header). Origin bu sarlavhani olmagani uchun har doim standart xavfsiz `NORMAL` bannerini qaytaradi.
2. **`loose_routes: false` (Keshni aldashga qarshi — Origin himoyasi):**
   Origin serverida qat'iy marshrutlash (Strict Routing) o'rnatiladi. Origin endi faqat aniq `/account` yo'lini taniydi. Har qanday `/account/report.css` yoki shunga o'xshash yo'llarga darhol `404 NOT FOUND` javobini beradi.
3. **`safe_cache: true` (Keshni aldashga qarshi — Edge himoyasi):**
   Edge serveri qat'iy oq ro'yxat (Whitelist) va sarlavhalar tekshiruvini yoqadi:
   * Faqat aniq ochiq yo'llar keshlanadi: `path in ('/public', '/assets/app.css')`.
   * Agar so'rovda `Cookie` yoki `Authorization` sarlavhalari mavjud bo'lsa, kesh darhol chetlab o'tiladi (`BYPASS`).
   * Origin qaytargan javob faqat `200 OK` bo'lsa va unda `Cache-Control: public, max-age=300` aniq ko'rsatilgan bo'lsagina keshga saqlanadi. `private, no-store` bo'lgan javoblar hech qachon keshlanmaydi!

> [!CAUTION]
> **Muhim tushuncha:** Keshni tozalash (Cache Purge/Invalidation) va Himoyani sozlash (Mitigation) ikki xil amaldir! Faqat keshni tozalash zaiflikni bartaraf etmaydi, chunki hujumchi yangi so'rov bilan keshni qayta zaharlashi mumkin. Qat'iy himoya qoidalarini joriy etish shart!

---

### 3.6. Qonuniy Keshlash va CDN Siyosat Kartasi

Xavfsizlik choralarini ko'rishda "ortiqcha himoyalanish" (over-defense) xatosi yuzaga kelmasligi kerak. Agar hamma narsa `BYPASS` qilib qo'yilsa, kesh va CDN o'zining asosiy funksiyasini (kontentni tezkor yetkazish va server yuklamasini kamaytirish) yo'qotadi.

To'g'ri sozlangan tizimda:
* `/assets/app.css` kabi statik ochiq resurslar birinchi so'rovda `MISS`, ikkinchi so'rovda `HIT` bo'lishi va normal keshlanishi shart.
* Shaxsiy `/account` sahifasi esa har doim `BYPASS` holatida qolishi kerak.

#### CDN Siyosat Kartasi (CDN Policy Mapping Table):

| Resurs / Holat | Talab etiladigan Qaror | Kesh Kaliti Holati | Natija / Dalil |
| :--- | :--- | :--- | :--- |
| `/assets/app.css`, oddiy GET | Ochiq 200 ni keshlash (TTL: 300s) | Keshga kiradi; bir xil URL | `MISS` -> `HIT`, Origin-Id o'zgarmaydi |
| `/account` va shaxsiy javob | Umumiy keshni chetlab o'tish | Keshlanmaydi | Har doim `BYPASS` |
| `/account/report.css` | Aniq marshrutlash: 404 qaytarish | Keshlanmaydi | `404 NOT FOUND` / `BYPASS` |
| `Cookie` yoki `Authorization` bor so'rov | Keshni chetlab o'tish | Keshlanmaydi | Har doim `BYPASS` |
| `X-Lab-Banner` sarlavhasi | Mijozdan kelgan qiymatni uzatmaslik | Kalitda yo'q, Originga o'tmaydi | Faqat `NORMAL` banner |

---

### 3.7. HTTP Request Smuggling (CL.TE va TE.CL Chegaralar Nomuvofiqligi)

HTTP/1.1 protokoli bir nechta so'rovlarni bitta doimiy (persistent) TCP ulanish orqali ketma-ket yuborish (pipelining / keep-alive) imkonini beradi. Har bir so'rov qayerda tugab, keyingisi qayerda boshlanishini aniqlash uchun ikki xil mexanizm mavjud:
1. `Content-Length` (CL): So'rov tanasining aniq uzunligini baytlarda ko'rsatadi.
2. `Transfer-Encoding: chunked` (TE): So'rov tanasi bo'laklarga (chunks) bo'lingan holda yuboriladi va `0\r\n\r\n` bo'lagi bilan yakunlanadi.

```
+------------------+                    +--------------------+
|  Frontend Proxy  |                    |   Backend Server   |
| (Content-Length) |                    | (Transfer-Encoding)|
+------------------+                    +--------------------+
         |                                         |
         |  POST /submit HTTP/1.1                  |
         |  Content-Length: 44                     |
         |  Transfer-Encoding: chunked             |
         |                                         |
         |  0\r\n\r\n   <------------------------  | TE shu yerda tugadi deb biladi!
         |  GET /probe HTTP/1.1                    |
         |  Host: a10.test                         | Qoldiq (39 bayt) keyingi
         |                                         | so'rovning boshi bo'lib qoladi!
         |              -------------------------> |
         |  CL 44 baytni to'liq bitta              |
         |  so'rov deb hisoblaydi                  |
```

#### CL.TE Hujumining Baytlar Modeli (`framing.py`):
Ushbu model tarmoqsiz, xotiradagi xom baytlar ustida ishlaydi:
* Sarlavhalar bloki uzunligi: **89 bayt**.
* Umumiy tana (`body`): **44 bayt**.
  - `0\r\n\r\n` (chunked yakunlovchi bo'lagi): **5 bayt**.
  - `GET /probe HTTP/1.1\r\nHost: a10.test\r\n\r\n`: **39 bayt**.
* **CL talqini:** Sarlavha + tana = `89 + 44 = 133 bayt`. Barcha 44 bayt bitta POST tanasi deb hisoblanadi, qoldiq qolmaydi (`remaining=b''`).
* **TE talqini:** Sarlavha + 0-chunk = `89 + 5 = 94 bayt`. Chunked xabar 94-baytda tugaydi! Qolgan **39 bayt** (`GET /probe ...`) TCP oqimida qoldiq bo'lib qoladi va navbatdagi foydalanuvchining so'rovi oldiga yopishib oladi!
* **RFC 9112 talabi (`strict` rejimi):** Agar so'rovda ham `Content-Length`, ham `Transfer-Encoding` mavjud bo'lsa, server uni potentsial xavf (ambiguous framing) deb topib, darhol rad etishi (`REJECT ambiguous framing` yoki HTTP 400 Bad Request) shart!

---

## 4. 3-QISM: MASHQNI BOSQICHMA-BOSQICH BAJARISH VA HAR BIR CLI BUYRUQ TAHLILI

Har bir bosqichda bajariladigan komandalar, ularning har bir parametri va chiqadigan natijasi to'liq tushuntiriladi.

```
+-----------------------------------------------------------------------------------+
|                        MASHG'ULOTNING VAQT REJASI (80 DAQIQA)                     |
+-----------------------------------------------------------------------------------+
| 1. Muhit va boshlang'ich tekshiruv (D1)                  --> 8 daqiqa             |
| 2. Oddiy kesh va Poisoning sinovi (D2)                   --> 14 daqiqa            |
| 3. Deception va nazorat so'rovlari (D3)                  --> 13 daqiqa            |
| 4. Himoyani sozlash va qayta sinash (D4)                 --> 18 daqiqa            |
| 5. Qonuniy keshlash va CDN kartasi (D5)                  --> 10 daqiqa            |
| 6. HTTP Request Smuggling framing tahlili (D6)           --> 10 daqiqa            |
| 7. Hisobotni rasmiylashtirish va xulosa                  --> 7 daqiqa             |
+-----------------------------------------------------------------------------------+
```

---

### 4.1. 0-Bosqich: Ish Muhitini Tayyorlash va Paketlarni O'rnatish

Ubuntu Server VM terminaliga kiring va quyidagi buyruqlarni ketma-ket bajaring:

```bash
sudo apt update
sudo apt install -y python3 curl nano
mkdir -p ~/a10-lab
cd ~/a10-lab
```

#### Har bir CLI buyruq tahlili:
1. `sudo apt update`:
   - `sudo` — administrator (root) huquqi bilan bajarish.
   - `apt update` — Ubuntu paketlar omborining (repositories) indekslarini yangilaydi. Shaxsiy lokal Wi-Fi tarmog'ingiz orqali rasmiy Ubuntu serverlariga to'g'ridan-to'g'ri ulanib, eng so'nggi paketlar ro'yxatini yuklaydi.
2. `sudo apt install -y python3 curl nano`:
   - `apt install` — yangi dasturlarni o'rnatish.
   - `-y` (`--yes`) — o'rnatish jarayonidagi tasdiqlash so'rovlariga ("Do you want to continue? [Y/n]") avtomatik "Ha" deb javob beradi.
   - `python3` — laboratoriya serverlari va framing skriptini ishga tushirish uchun Python 3 interpretatori.
   - `curl` — HTTP so'rovlarini terminal orqali yuborish va sarlavhalarni tahlil qilish uchun asosiy tarmoq vositasi.
   - `nano` — konsol matn muharriri (fayllarni ko'rish va tahrirlash uchun).
3. `mkdir -p ~/a10-lab`:
   - `mkdir` — yangi papka (direktoriya) yaratish.
   - `-p` (`--parents`) — agar papka mavjud bo'lmasa yaratadi, mavjud bo'lsa xatolik bermaydi.
   - `~/a10-lab` — joriy foydalanuvchining uy papkasida (`/home/foydalanuvchi/a10-lab`) laboratoriya loyihasi uchun alohida toza joy ajratadi.
4. `cd ~/a10-lab`:
   - `cd` (change directory) — yaratilgan `~/a10-lab` ishchi papkasiga o'tadi.

---

### 4.2. 1-Bosqich: Fayllarni Shakllantirish va Dastlabki Serverni Ishga Tushirish (D1 Dalili)

Loyihada 3 ta asosiy fayl bo'lishi kerak:
1. `settings.json` — boshlang'ich zaif sozlamalar.
2. `lab.py` — Edge va Origin serverlar kodi.
3. `framing.py` — HTTP/1.1 bayt tahlili modeli.

#### 1-Qadam: `settings.json` faylini yaratish:
```bash
cat > settings.json <<'EOF'
{
  "trust_banner": true,
  "loose_routes": true,
  "safe_cache": false
}
EOF
```

##### CLI buyruq tahlili:
* `cat > settings.json <<'EOF'` — bu "Here Document" (Heredoc) usuli bo'lib, terminal orqali ko'p qatorli matnni faylga yozish imkonini beradi.
* `<<'EOF'` — apostroflar ichidagi `EOF` yozuvi orqali matn ichidagi maxsus belgilarni bash qobig'i o'zgartirmasdan, qanday bo'lsa shundayligicha `settings.json` ga yozadi.

Nusxasini saqlab olamiz va JSON formatini tekshiramiz:
```bash
cp settings.json settings.before.json
python3 -m json.tool settings.json
```
* `cp settings.json settings.before.json` — boshlang'ich zaif konfiguratsiyani kelgusida taqqoslash (diff) qilish uchun zaxiraga nusxalaydi.
* `python3 -m json.tool settings.json` — Pythonning o'rnatilgan JSON validator modulini chaqirib, fayl sintaksisi to'g'riligini va formatlanganligini tekshiradi.

#### 2-Qadam: `lab.py` va `framing.py` fayllarini yaratish:
Ushbu fayllarni `nano lab.py` va `nano framing.py` orqali to'liq yarating (kodlari 2-ilovada keltirilgan).

Sintaksisni kompilyatsiya orqali tekshirish:
```bash
python3 -m py_compile lab.py framing.py
python3 --version
curl --version
```
* `python3 -m py_compile lab.py framing.py` — Python skriptlarini bayt-kodga (.pyc) kompilyatsiya qilib, barcha chekinishlar (indentation) va sintaksis to'g'ri ekanini tekshiradi. Xatolik chiqmasa, kodda sintaktik xato yo'q.
* `python3 --version` va `curl --version` — hisobot uchun tizimdagi dastur versiyalarini ekranga chiqaradi.

#### 3-Qadam: 1-Terminalda serverni ishga tushirish:
```bash
python3 -u lab.py 2>&1 | tee lab-before.log
```
##### CLI buyruq tahlili:
* `python3 -u` — unbuffered rejimi. Python terminalga yozilayotgan loglarni buferda ushlab turmasdan, darhol real vaqt rejimida chiqaradi.
* `2>&1` — standart xatoliklar oqimini (stderr - 2) standart chiqish oqimiga (stdout - 1) yo'naltiradi, ya'ni barcha xabarlar va xatolar bitta joyga yig'iladi.
* `| tee lab-before.log` — quvur (pipe) orqali barcha ma'lumotlarni bir vaqtning o'zida ham ekranga chiqaradi, ham `lab-before.log` fayliga saqlab boradi.

Terminalda quyidagi yozuv paydo bo'ladi:
```text
A10: origin=8010 edge=8080; config= {'trust_banner': True, 'loose_routes': True, 'safe_cache': False}
```
**Bu terminalni yopmang! U ochiq qoladi va barcha so'rovlar logini ko'rsatib turadi.**

#### 4-Qadam: 2-Terminalni ochish va D1 tekshiruvi:
Yangi terminal oching (yoki SSH orqali ikkinchi sessiyani boshlang):
```bash
cd ~/a10-lab
E=http://127.0.0.1:8080
O=http://127.0.0.1:8010
ss -ltn | grep -E ":(8010|8080)[[:space:]]"
curl --noproxy "*" -i "$O/public"
```

##### CLI buyruq tahlili:
* `E=http://127.0.0.1:8080` va `O=http://127.0.0.1:8010` — Edge va Origin serverlarining URL manzillarini `E` va `O` nomli muhit o'zgaruvchilariga biriktiradi. Bu har safar uzun URL yozmasdan, `$E` va `$O` deb qisqa chaqirish imkonini beradi.
* `ss -ltn` — tizimdagi barcha tinglovchi (listening) tarmoq portlarini raqamli ko'rinishda (`-n`), faqat TCP portlarni (`-t`) va tinglovchi holatdagilarini (`-l`) ko'rsatadi (`netstat` ning zamonaviy o'rinbosari).
* `| grep -E ":(8010|8080)[[:space:]]"` — faqat 8010 va 8080 portlariga tegishli qatorlarni filtrlab ajratib beradi.
* `curl --noproxy "*" -i "$O/public"`:
  - `curl` — HTTP mijoz.
  - `--noproxy "*"` — har qanday tizim proksisini chetlab o'tib, to'g'ridan-to'g'ri bog'lanishni ta'minlaydi.
  - `-i` (`--include`) — HTTP javobining nafaqat tanasini (body), balki server qaytargan **barcha HTTP sarlavhalarini (Status code, Content-Type, Cache-Control va h.k.)** ham ko'rsatadi.
  - `"$O/public"` — to'g'ridan-to'g'ri Origin serverga (`http://127.0.0.1:8010/public`) so'rov yuboradi.

Kutiladigan javob:
```http
HTTP/1.0 200 OK
Content-Type: text/plain
Cache-Control: public, max-age=300
X-Origin-Id: 1
Content-Length: 21

PUBLIC banner=NORMAL
```
> [!NOTE]
> **D1 Dalili:** Ushbu bosqichda tizim parametrlari, portlar holati (`ss` chiqishi) va Origin serverining `200 OK`, `PUBLIC banner=NORMAL`, `X-Origin-Id: 1` javobini hisobot uchun saqlab oling!

---

### 4.3. 2-Bosqich: Oddiy Keshlash va Web Cache Poisoning Hujumi (D2 Dalili)

#### 1-Qadam: Oddiy kesh holatini kuzatish (3-topshiriq):
2-terminalda quyidagi buyruqlarni ketma-ket bajaring:
```bash
curl --noproxy "*" -i "$E/public?case=base1"
curl --noproxy "*" -i "$E/public?case=base1"
```

##### Chiqish tahlili:
1. **1-so'rov javobi:**
   - Status: `200 OK`
   - `X-Lab-Cache: MISS` (Keshda yo'q edi, Origindan yuklandi)
   - `Age: 0`
   - `X-Origin-Id: 2` (Origin yangi so'rovni qayta ishladi)
   - Tana: `PUBLIC banner=NORMAL`
2. **2-so'rov javobi:**
   - Status: `200 OK`
   - `X-Lab-Cache: HIT` (Javob Edge kesh xotirasidan olindi)
   - `Age: 0` (yoki bir necha soniya)
   - `X-Origin-Id: 2` (**Muhim!** Origin hisoblagichi oshmadi, chunki Edge Originga murojaat qilmadi!)
   - Tana: `PUBLIC banner=NORMAL`

#### 2-Qadam: Web Cache Poisoning hujumini amalga oshirish (4-topshiriq):
Yangi `case=p1` kaliti bilan markerli so'rov yuboramiz, so'ngra markersiz oddiy so'rov bilan tekshiramiz:

```bash
curl --noproxy "*" -i -H "X-Lab-Banner: A10-MARKER" "$E/public?case=p1"
curl --noproxy "*" -i "$E/public?case=p1"
curl --noproxy "*" -i "$E/public?case=clean1"
```

##### CLI buyruq tahlili:
* `-H "X-Lab-Banner: A10-MARKER"` — `curl` orqali HTTP so'roviga maxsus sarlavha qo'shadi. Bu yerda `A10-MARKER` unkeyed kiruvchi ma'lumot (payload) hisoblanadi.

##### Natijalar Tahlil Jadvali:

| So'rov | Yuborilgan Parametrlar | Kesh Holati | X-Origin-Id | Qaytgan Javob Tanasi |
| :--- | :--- | :--- | :--- | :--- |
| **1-so'rov** | `case=p1`, `X-Lab-Banner: A10-MARKER` | `MISS` | Masalan: `3` | `PUBLIC banner=A10-MARKER` |
| **2-so'rov** | `case=p1`, **Sarlavhasiz!** | `HIT` | Masalan: `3` | **`PUBLIC banner=A10-MARKER`** |
| **3-so'rov** | `case=clean1`, Sarlavhasiz | `MISS` | Masalan: `4` | `PUBLIC banner=NORMAL` |

##### Nima yuz berdi? (Hodisaning mohiyati):
* 1-so'rovda Edge kesh `trust_banner: true` bo'lgani sababli `X-Lab-Banner` sarlavhasini Originga o'tkazdi. Origin sahifani "A10-MARKER" bilan generatsiya qildi. Kesh kalitiga (`'GET', Host, '/public?case=p1'`) esa bu sarlavha kirmagan edi. Natijada zaharlangan sahifa oddiy kalit ostida keshlanib qoldi!
* 2-so'rovda begunoh foydalanuvchi hech qanday sarlavhasiz murojaat qildi, ammo Edge kesh kalit bo'yicha zaharlangan javobni topdi va `HIT` holatida qaytardi!
* 3-so'rov yangi `case=clean1` kaliti bo'yicha yuborildi va toza `NORMAL` javobi olindi (bu kesh kalitida URL query string ishtirok etayotganini ko'rsatadi).

> [!NOTE]
> **D2 Dalili:** Ushbu 3 ta so'rov natijasi, `MISS` va `HIT` holatlari, `X-Origin-Id` ning o'zgarmagani va sarlavhasiz so'rovda `A10-MARKER` qaytganini hisobotga saqlang!

---

### 4.4. 3-Bosqich: Web Cache Deception Hujumi va Shaxsiy Ma'lumotlarni O'g'irlash (D3 Dalili)

Ushbu bosqichda jabrlanuvchi Alice nomidan keshlanuvchi qilib soxtalashtirilgan URL ochiladi, so'ngra hujumchi ushbu sahifani keshdan o'g'irlaydi (5-topshiriq).

2-terminalda quyidagi buyruqlarni ketma-ket bajaring:
```bash
curl --noproxy "*" -i -H "Cookie: lab_user=alice" "$E/account/report.css?case=d1"
curl --noproxy "*" -i "$E/account/report.css?case=d1"
curl --noproxy "*" -i "$O/account/report.css?case=d1"
```

##### CLI buyruq tahlili:
* `-H "Cookie: lab_user=alice"` — HTTP so'roviga autentifikatsiya kuki sarlavhasini qo'shadi. Bu orqali Origin server foydalanuvchini Alice deb taniydi.
* `"$E/account/report.css?case=d1"` — Edge kesh orqali chalg'ituvchi manzilga so'rov.
* `"$O/account/report.css?case=d1"` — to'g'ridan-to'g'ri Origin serverga so'rov.

##### Natijalar Tahlili:
1. **1-so'rov (Alice nomidan):**
   - Status: `200 OK`
   - `X-Lab-Cache: MISS`
   - `Cache-Control: private, no-store` (Origin buni saqlama degan!)
   - Tana: `PRIVATE user=alice code=DEMO-ALICE`
   - *Tahlil:* Origin server `loose_routes: true` bo'lgani uchun yo'lni `/account/` bilan boshlangan deb topdi va Alice'ning maxfiy kodini chiqardi. Edge server esa URL oxiridagi `.css` qo'shimchasini ko'rib, `safe_cache: false` bo'lgani uchun `private, no-store` ga qaramasdan uni keshga saqlab qo'ydi!
2. **2-so'rov (Hujumchi — Hech qanday Cookie yubormaydi):**
   - Status: `200 OK`
   - `X-Lab-Cache: HIT`
   - Tana: `PRIVATE user=alice code=DEMO-ALICE`
   - *Tahlil:* Hujumchi Alice'ning shaxsiy ma'lumotlarini keshdan o'g'irladi!
3. **3-so'rov (Origin serverga to'g'ridan-to'g'ri, Cookiesiz):**
   - Status: `401 Unauthorized`
   - Tana: `LOGIN REQUIRED`
   - *Tahlil:* Origin server shaxsiy sahifani hujjatsiz bermaydi (401), ammo oraliq Edge keshdagi xatolik sababli u hammaga tarqalib ketdi.

#### Nazorat So'rovlari (Oddiy yo'l bilan tekshirish):
```bash
curl --noproxy "*" -i -H "Cookie: lab_user=bob" "$E/account"
curl --noproxy "*" -i "$E/account"
```
* Bob uchun: `200 OK`, `X-Lab-Cache: BYPASS`, `code=DEMO-BOB`.
* Cookiesiz so'rov uchun: `401 Unauthorized`, `X-Lab-Cache: BYPASS`, `LOGIN REQUIRED`.
* *Xulosa:* Oddiy `/account` yo'li `.css` bilan tugamagani sababli Edge uni keshlamaydi (`BYPASS`). Bu hodisa aynan `.css` qo'shimchasi orqali keshni aldash (Cache Deception) ekanini to'liq isbotlaydi.

> [!NOTE]
> **D3 Dalili:** Alice bilan olingan 200 MISS, undan keyingi cookiesiz 200 HIT, bir xil Origin-Id hamda to'g'ridan-to'g'ri origin bergan 401 javoblarini hisobotga saqlang!

---

### 4.5. 4-Bosqich: Himoya Mexanizmlarini Sozlash va Qayta Sinov (D4 Dalili)

Endi aniqlangan zaifliklarni bartaraf etamiz (6-topshiriq).

#### 1-Qadam: Serverni to'xtatish:
1-terminalga o'ting va **`Ctrl + C`** tugmalarini bosib, ishlayotgan `lab.py` jarayonini to'xtating. Bu xotiradagi barcha eski kesh yozuvlarini tozalaydi.

#### 2-Qadam: `settings.json` ni himoyalangan holatga keltirish:
```bash
cd ~/a10-lab
cat > settings.json <<'EOF'
{
  "trust_banner": false,
  "loose_routes": false,
  "safe_cache": true
}
EOF
python3 -m json.tool settings.json
diff -u settings.before.json settings.json
```

##### CLI buyruq tahlili:
* `diff -u settings.before.json settings.json` — eski va yangi konfiguratsiya fayllari orasidagi farqni Unified Diff formatida ko'rsatadi:
  - `- "trust_banner": true`  -->  `+ "trust_banner": false`
  - `- "loose_routes": true`  -->  `+ "loose_routes": false`
  - `- "safe_cache": false`   -->  `+ "safe_cache": true`
  - *(Chiqish kodi 1 bo'ladi, chunki farq topildi — bu normal holat).*

#### 3-Qadam: Himoyalangan serverni ishga tushirish (1-terminalda):
```bash
python3 -u lab.py 2>&1 | tee lab-after.log
```
Terminalda yangi konfiguratsiya tasdiqlanadi:
```text
A10: origin=8010 edge=8080; config= {'trust_banner': False, 'loose_routes': False, 'safe_cache': True}
```

#### 4-Qadam: Qayta sinovlar (2-terminalda):
Oldin ifloslangan URL manzillari bilan qayta tekshiramiz:

```bash
curl --noproxy "*" -i -H "X-Lab-Banner: A10-MARKER" "$E/public?case=p1"
curl --noproxy "*" -i "$E/public?case=p1"
curl --noproxy "*" -i -H "Cookie: lab_user=alice" "$E/account/report.css?case=d1"
curl --noproxy "*" -i "$E/account/report.css?case=d1"
```

##### Natijalar Tahlili:
1. **Poisoning sinovi natijasi:**
   - 1-so'rov: `MISS`, javob: `PUBLIC banner=NORMAL`! Chunki `trust_banner: false` bo'lgani sababli Edge `X-Lab-Banner` sarlavhasini Originga o'tkazmadi!
   - 2-so'rov: `HIT`, javob: `PUBLIC banner=NORMAL`! Keshga zararli marker kirmadi, kesh toza qoldi!
2. **Deception sinovi natijasi:**
   - Alice so'rovi: `404 NOT FOUND`, `X-Lab-Cache: BYPASS`! Chunki `loose_routes: false` bo'lgani sababli Origin `/account/report.css` yo'lini rad etdi.
   - Cookiesiz so'rov: `404 NOT FOUND`, `X-Lab-Cache: BYPASS`! Hech qanday shaxsiy ma'lumot keshga tushmadi va tarqalmadi!

> [!NOTE]
> **D4 Dalili:** Konfiguratsiyaning diff chiqishi, yangi ishga tushish logi va takroriy so'rovlarda zaharlanish hamda aldanuvchi ma'lumotlar yo'qolganini tasdiqlovchi natijalarni saqlang!

---

### 4.6. 5-Bosqich: Qonuniy Ochiq Resurslarni Tekshirish va CDN Siyosat Kartasi (D5 Dalili)

Himoya yoqilgandan keyin qonuniy statik resurslar keshlana olishini va maxfiy ma'lumotlar keshdan chetlatilganini (BYPASS) tasdiqlash zarur (7-topshiriq).

2-terminalda quyidagi buyruqlarni bajaring:
```bash
curl --noproxy "*" -i "$E/assets/app.css"
curl --noproxy "*" -i "$E/assets/app.css"
curl --noproxy "*" -i -H "Cookie: lab_user=alice" "$E/account"
curl --noproxy "*" -i "$E/account"
curl --noproxy "*" -i -H "Authorization: Bearer DEMO" "$E/public?case=auth1"
```

##### CLI buyruq tahlili:
* `"$E/assets/app.css"`:
  - 1-so'rov: `200 OK`, `Content-Type: text/css`, `X-Lab-Cache: MISS`.
  - 2-so'rov: `200 OK`, `X-Lab-Cache: HIT`, bir xil `X-Origin-Id`. Bu qonuniy ochiq CSS resurslari muvaffaqiyatli keshlanayotganini isbotlaydi.
* `"$E/account"`:
  - Alice kukisi bilan: `200 OK`, `X-Lab-Cache: BYPASS`. Kuki borligi sababli keshlanmadi!
  - Kukisiz: `401 Unauthorized`, `X-Lab-Cache: BYPASS`.
* `-H "Authorization: Bearer DEMO" "$E/public?case=auth1"`:
  - `200 OK`, `X-Lab-Cache: BYPASS`. `safe_cache: true` qoidasiga binoan `Authorization` sarlavhasi mavjud bo'lgan har qanday so'rov ochiq sahifa bo'lsa ham keshlanmaydi!

> [!NOTE]
> **D5 Dalili:** CSS faylning `MISS` -> `HIT` bo'lgani, shaxsiy hisobning `BYPASS` bo'lgani va to'ldirilgan CDN Siyosat Kartasini hisobotga ilova qiling!

---

### 4.7. 6-Bosqich: HTTP Request Smuggling Bayt Modelini Tahlil Qilish (D6 Dalili)

Ushbu qismda tarmoqsiz model (`framing.py`) orqali HTTP/1.1 bayt chegaralaridagi nomuvofiqlik o'rganiladi (8-topshiriq).

```bash
cd ~/a10-lab
python3 framing.py | tee framing-result.txt
```

##### CLI buyruq tahlili:
* `python3 framing.py` — Python interpretatorida xom baytlar tahlilini amalga oshiradi.
* `| tee framing-result.txt` — hisob-kitob natijalarini ekranga chiqaradi va `framing-result.txt` fayliga saqlaydi.

##### Ekranga chiqadigan to'liq natija:
```text
body_bytes= 44
CL end= 133 remaining= b''
TE end= 94 remaining= b'GET /probe HTTP/1.1\r\nHost: a10.test\r\n\r\n'
strict REJECT ambiguous framing
CL-only accepted; remaining= b''
TE-only accepted; remaining= b'GET /probe HTTP/1.1\r\nHost: a10.test\r\n\r\n'
```

##### Matematik Hisob-kitob va Baytlar Tahlili:
1. **Sarlavhalar bloki (head):**
   ```http
   POST /submit HTTP/1.1\r\nHost: a10.test\r\nContent-Length: 44\r\nTransfer-Encoding: chunked\r\n\r\n
   ```
   Ushbu sarlavhalar blokining uzunligi: **89 bayt**.
2. **Jami tana (body):** **44 bayt**.
   - `0\r\n\r\n` (bo'sh chunked tugash belgisi) = **5 bayt**.
   - `GET /probe HTTP/1.1\r\nHost: a10.test\r\n\r\n` = **39 bayt**.
3. **CL (Content-Length) talqini:**
   - Chegara: `89 + 44 = 133 bayt`.
   - Parser 133-baytgacha bo'lgan barcha ma'lumotni POST so'rovi tanasi deb hisoblaydi. Qoldiq yo'q (`remaining = b''`).
4. **TE (Transfer-Encoding) talqini:**
   - Chegara: `89 + 5 = 94 bayt`.
   - Chunked parser `0\r\n\r\n` ni ko'rishi bilan so'rov tanasi tugadi deb hisoblaydi!
   - Natijada **39 baytlik** `GET /probe ...` so'rovi tarmoq buferida qoldiq bo'lib qoladi!
5. **Strict (RFC 9112) talqini:**
   - Agar bitta so'rovda ham `Content-Length`, ham `Transfer-Encoding` kelsa, parser uni darhol rad etadi: `REJECT ambiguous framing`!
6. **Nazorat variantlari:**
   - `CL-only`: Transfer-Encoding yo'q, 44 bayt to'liq qabul qilindi.
   - `TE-only`: Content-Length yo'q, chunked qabul qilindi, qoldiq 39 bayt. (Eslatma: ikkala tomon ham TE ni anglatsa, qoldiqning o'zi zaiflik emas; zaiflik ikki serverning ikki xil qoidani tanlashidan kelib chiqadi).

> [!NOTE]
> **D6 Dalili:** `framing.py` dasturining chiqish logi, 89+44=133 va 89+5=94 baytlik hisob-kitob tahlilini hisobotga kiriting!

---

### 4.8. 7-Bosqich: Dalillarni Rasmilashtirish va Hisobot Qoidalari

Mashg'ulot yakunlangach, 1-terminalda **`Ctrl + C`** bosib serverni to'xtating. Quyidagi fayllar mavjudligini tekshiring:
* `settings.before.json` (boshlang'ich zaif sozlama)
* `settings.json` (yakuniy himoyalangan sozlama)
* `lab-before.log` (zaif holatdagi server loglari)
* `lab-after.log` (himoyalangan holatdagi server loglari)
* `framing-result.txt` (bayt tahlili natijasi)

#### Hisobot Tituli Talablari:
* Fan: Veb dasturlar xavfsizligi
* Semestr: 5-semestr
* Mashg'ulot: A10, 1-variant
* F.I.Sh., Guruh, Sana
* Host OS: Ubuntu Linux; Virtualizator: VMware Workstation; Guest VM: Ubuntu Server 24.04 LTS; Tarmoq: Shaxsiy Lokal Wi-Fi.

#### Baholash Mezonlari (Jami 10 ball):
| Mezon | Ball | Talab qilinadigan Dalil |
| :--- | :---: | :--- |
| **Muhit, portlar va oddiy MISS/HIT** | 1 ball | D1 (ss portlari, Python/curl versiyalari, base1 so'rovi) |
| **Poisoning: sarlavhasiz qayta tarqalish** | 2 ball | D2 (`A10-MARKER` ning sarlavhasiz HIT bo'lishi va sababi) |
| **Deception: cookiesiz HIT va 401 bilan qiyos** | 2 ball | D3 (Alice ma'lumotining cookiesiz HIT bo'lishi va Origin 401) |
| **Tuzatish, shaxsiy BYPASS va ochiq CSS keshi** | 2 ball | D4 va D5 (diff sozlamalari, CSS HIT bo'lishi, account BYPASS) |
| **CL/TE hisobi, strict rad etish va nazorat** | 2 ball | D6 (133 va 94 bayt hisobi, strict rad etish dalili) |
| **Hisobot, CDN kartasi va yakuniy xulosa** | 1 ball | To'ldirilgan CDN jadvali va 5-7 gaplik xulosa |

---

### 4.9. Texnik Muammolarni Hal Qilish (Troubleshooting)

| Muammo belgisi | Sababi | Qat'iy Yechim |
| :--- | :--- | :--- |
| **`Address already in use`** | 8080 yoki 8010 porti avvalgi ishga tushirilgan jarayon tomonidan band qilingan | Terminalda `Ctrl + C` bosing yoki `fuser -k 8080/tcp 8010/tcp` buyrug'i bilan portni bo'shating |
| **`Connection refused`** | `lab.py` serveri ishga tushmagan yoki to'xtab qolgan | 1-terminalda `python3 -u lab.py` buyrug'i ishlayotganini va xatolik yo'qligini tekshiring |
| **Birinchi so'rov darhol `HIT` bo'ldi** | Ushbu URL kaliti avvalroq ishlatilgan | Yangi `case` qiymatidan foydalaning (masalan, `case=p2`) yoki serverni qayta ishga tushiring |
| **Ikkinchi so'rov `MISS` bo'lib qoldi** | 300 soniya (TTL) o'tib ketgan yoki URL/Query da harfiy farq bor | URL manzilini aynan bir xilligini tekshirib, 300 soniya ichida qayta yuboring |
| **Deception sinovida 401 chiqdi** | Birinchi so'rovda `Cookie: lab_user=alice` berilmagan | Cookie sarlavhasini tekshiring va boshlang'ich `settings.json` faol ekaniga ishonch hosil qiling |
| **Tuzatishdan keyin ham marker bor** | `settings.json` o'zgarishi faqat server startida o'qiladi | Serverni `Ctrl + C` bilan to'xtatib, qayta ishga tushiring |
| **`IndentationError` yoki `JSONDecodeError`** | Kodda surilishlar yoki JSON da vergullar xato qo'yilgan | `python3 -m py_compile lab.py` va `python3 -m json.tool settings.json` bilan tekshiring |

---

### 4.10. Nazorat Savollari va Ilmiy Asoslangan Javoblar

#### 6-Savol: Poisoning va Deceptionda keshga tushgan ma’lumotning kelib chiqishi nimasi bilan farq qiladi?
* **Javob:**
  - **Cache Poisoning**da keshga tushadigan ma'lumotning manbasi bevosita **tajovuzkorning o'zi** hisoblanadi. Tajovuzkor ataylab kesh kalitiga kirmaydigan sarlavha (masalan, `X-Lab-Banner: A10-MARKER` yoki zararli payload) yuboradi, server bu zararli kiritmani o'z ichiga olgan javob qaytaradi va u umumiy keshga saqlanadi. Maqsad — boshqa barcha foydalanuvchilarga ushbu zararli javobni yetkazish (ma'lumot butunligini buzish).
  - **Cache Deception**da esa keshga tushadigan ma'lumot **begunoh jabrlanuvchining shaxsiy hisob ma'lumotlari** (PII, maxfiy tokenlar) hisoblanadi. Tajovuzkor jabrlanuvchini maxsus tuzilgan statik ko'rinishdagi URL ga kirishga majbur qiladi. Jabrlanuvchi o'z sessiyasi (Cookie) orqali ushbu sahifani ochganda, kesh uni statik deb o'ylab saqlab qo'yadi. Maqsad — begunoh foydalanuvchining ma'lumotlarini o'g'irlash (maxfiylikni buzish).

#### 7-Savol: `private, no-store` ko‘rinib tursa ham nega D3da ma’lumot tarqaldi?
* **Javob:**
  Chunki oraliq kesh (Edge server) xavfsizlik sarlavhalarini avtomatik tahlil qilmaydi, balki o'ziga berilgan dasturiy mantiq bo'yicha ishlaydi. Dastlabki `settings.json` da `safe_cache: false` qilingan edi. `lab.py` kodida `safe_cache` o'chiq bo'lsa:
  ```python
  eligible = path == '/public' or path.endswith('.css')
  ```
  Edge faqat URL oxirida `.css` borligini tekshiradi va javobni keshlaydi. Origin server qaytargan `Cache-Control: private, no-store` sarlavhasi Edge tomonidan ko'r-ko'rona inkor etiladi. Bu shuni isbotlaydiki, himoyani faqat Originda sarlavha qo'yish bilan cheklab bo'lmaydi; oraliq CDN/Edge keshning o'zida ham qat'iy tekshiruv qoidalari (`safe_cache: true`) yoqilgan bo'lishi shart!

#### 8-Savol: Keshni tozalash (Purge) va qoidani tuzatish nega ikkita alohida amal?
* **Javob:**
  - **Keshni tozalash (Purge / Invalidation):** Bu faqatgina xotirada mavjud bo'lgan, ayni damda zaharlangan yoki noo'rin saqlangan ma'lumot nusxalarini o'chirib tashlaydi. Lekin kesh serverining ishlash qoidalari o'zgarmasdan qoladi. Agar qoidalar tuzatilmasa, keyingi daqiqada tajovuzkor yana xuddi shunday so'rov yuborib, keshni qaytadan zaharlashi mumkin.
  - **Qoidani tuzatish (Policy Hardening / Mitigation):** Bu asosiy sababni (root cause) bartaraf etadi — unkeyed sarlavhalarni filtrlaydi, statik kengaytmalarni ko'r-ko'rona keshlashni to'xtatadi va qat'iy marshrutlashni joriy etadi.
  - Shuning uchun haqiqiy infratuzilmalarda avval qoidalar yangilanadi va barcha Edge tugunlariga tarqatiladi (deploy), so'ngra eski zararlangan nusxalar to'liq tozalanadi (purge).

#### 9-Savol: CL va TE 39 baytga farq qilishi nimani anglatadi? TE-only qoldig‘i nega o‘zi zaiflik emas?
* **Javob:**
  - **39 bayt farq:** Bu `Content-Length: 44` (butun tana) bilan `Transfer-Encoding: chunked` (faqat `0\r\n\r\n` - 5 bayt) o'rtasidagi tafovutdir (`44 - 5 = 39 bayt`). Ushbu 39 bayt yashirin `GET /probe HTTP/1.1\r\nHost: a10.test\r\n\r\n` so'rovidan iborat. Agar frontend server CL ga, backend esa TE ga tayansa, backend 5-baytdan keyingi qolgan 39 baytni yangi, mustaqil HTTP so'rovi sifatida qabul qiladi.
  - **TE-only nima uchun o'zi zaiflik emas?** Chunki agar butun tarmoq zanjiridagi barcha vositachilar (ham Frontend, ham Backend) bir xil kelishuvga ega bo'lib, ikkalasi ham faqat TE bo'yicha ishlasa, har ikki tomon ham birinchi xabar 94-baytda tugaganini va keyingi 39 bayt navbatdagi qonuniy so'rov ekanini bir xil tushunadi. Zaiflik xabarning o'zida emas, balki **ikki xil serverning ikki xil qoidani tanlashi va desinxronizatsiya (nomuvofiqlik) vujudga kelishida** yotadi.

#### 10-Savol: Bitta lokal HIT natijasi butun CDN haqidagi qaysi xulosalarni bermaydi?
* **Javob:**
  Haqiqiy CDN (Cloudflare, Fastly, CloudFront) butun dunyo bo'ylab yuzlab va minglab geografik taqsimlangan **Edge PoP (Point of Presence)** tugunlariga ega.
  1. Bitta mahalliy tugunda olingan `HIT` yoki muvaffaqiyatli tozalash (purge) butun dunyodagi boshqa barcha Edge serverlarda ham kesh xuddi shunday holatda ekanini bildirmaydi (har bir tugun o'z kesh xotirasiga ega).
  2. Haqiqiy CDN larda Anycast routing, ko'p qatlamli kesh iyerarxiyasi (Tiered Caching / Shield Caching), xususiy HTTP/2 va HTTP/3 protokollari hamda murakkab `Vary` sarlavhalari mavjud.
  3. Shuning uchun bitta lokal laboratoriya modeli faqat asosiy mantiqiy algoritmni isbotlaydi, lekin haqiqiy yirik CDN infratuzilmasining to'liq holatini kafolatlamaydi.

---

## 5. 4-QISM: RASMIY MANBALAR VA FOYDALANILGAN ADABIYOTLAR

Ushbu laboratoriya mashg'uloti quyidagi xalqaro Internet standartlari (IETF RFC) va nufuzli veb xavfsizligi tadqiqotlariga to'liq asoslangan:

1. **RFC 9111 — HTTP Caching (IETF Rasmiy Standarti):**
   - 4.1-bo'lim: *Calculating Cache Keys* (Kesh kalitlarini shakllantirish).
   - 5.2-bo'lim: *Cache-Control Directives* (`public`, `private`, `no-store`, `no-cache`, `max-age`, `s-maxage` qoidalari).
   - Manba: [https://www.rfc-editor.org/rfc/rfc9111.html](https://www.rfc-editor.org/rfc/rfc9111.html)

2. **RFC 9112 — HTTP/1.1 (IETF Rasmiy Standarti):**
   - 6.1-bo'lim: *Transfer-Encoding* va Chunked oqimlar.
   - 6.3-bo'lim: *Message Body Length and Ambiguity Handling* (Content-Length va Transfer-Encoding birga kelganda xabarlarni rad etish qat'iy talablari).
   - Manba: [https://www.rfc-editor.org/rfc/rfc9112.html](https://www.rfc-editor.org/rfc/rfc9112.html)

3. **PortSwigger Web Security Academy — Web Cache Poisoning:**
   - James Kettle tadqiqotlari: *"Practical Web Cache Poisoning"* va unkeyed inputs mexanizmlari.
   - Manba: [https://portswigger.net/web-security/web-cache-poisoning](https://portswigger.net/web-security/web-cache-poisoning)

4. **PortSwigger Web Security Academy — Web Cache Deception:**
   - Omer Gil kashfiyoti: Path confusion va dinamik shaxsiy javoblarning statik qoidalar orqali keshlanib qolishi.
   - Manba: [https://portswigger.net/web-security/web-cache-deception](https://portswigger.net/web-security/web-cache-deception)

5. **PortSwigger Web Security Academy — HTTP Request Smuggling:**
   - CL.TE, TE.CL va TE.TE desinxronizatsiya hujumlari, frontend/backend zanjirini buzish.
   - Manba: [https://portswigger.net/web-security/request-smuggling](https://portswigger.net/web-security/request-smuggling)

6. **OWASP Web Security Testing Guide (WSTG):**
   - WSTG-CONF-12: *Testing for Web Cache Poisoning*.
   - WSTG-INPV-15: *Testing for HTTP Request Smuggling*.
   - Manba: [https://owasp.org/www-project-web-security-testing-guide/](https://owasp.org/www-project-web-security-testing-guide/)

---
*Hujjat talabaning barcha ko'rsatmalari (Ubuntu Host, VMware Workstation, Ubuntu Server mehmon tizimi, shaxsiy lokal Wi-Fi tarmog'i) inobatga olingan holda tayyorlandi.*
