# VEB DASTURLAR XAVFSIZLIGI — 5-SEMESTR
## A9-AMALIY MASHG‘ULOT: VEB SERVER, TLS, WAF VA XAVFSIZ KONFIGURATSIYA
### 1-VARIANT: Apache teskari proksisini TLS va ModSecurity bilan himoyalash bo‘yicha to‘liq va batafsil qo‘llanma

---

## MUNDARIJA
1. [Laboratoriya tavsifi va Ishchi muhit arxitekturasi](#1-laboratoriya-tavsifi-va-ishchi-muhit-arxitekturasi)
   - 1.1. Sizning ishchi muhitingiz bo‘yicha aniq parametrlar (Ubuntu + VMware)
   - 1.2. Tarmoq konfiguratsiyasi: Shaxsiy Wi-Fi va Proksisiz toza muhit
   - 1.3. Windows 11 masalasi va uning roli
   - 1.4. Tizim arxitekturasi va portlar taqsimoti
2. [Mashg‘ulotning maqsadi va kutiladigan natijalar](#2-mashgulotning-maqsadi-va-kutiladigan-natijalar)
3. [Nazariy asoslar va xavfsizlik konsepsiyalari (To‘liq ilmiy qo‘llanma)](#3-nazariy-asoslar-va-xavfsizlik-konsepsiyalari)
   - 3.1. Veb server va teskari proksi (Reverse Proxy vs Forward Proxy)
   - 3.2. TLS/SSL arxitekturasi, kriptografik zanjir va protokollar nazorati (TLS 1.2 / TLS 1.3)
   - 3.3. PKI (Public Key Infrastructure): O‘quv CA, Server sertifikati, SAN va Zanjir ishonchi
   - 3.4. HTTP Xavfsizlik sarlavhalari (Security Headers) va `Header always` zarurati
   - 3.5. Server ma’lumotlarini yashirish va metodlar nazorati (Information Disclosure & XST)
   - 3.6. Proksi sarlavhalarini soxtalashtirish (Header Spoofing) va tozalash mexanizmi
   - 3.7. WAF (Web Application Firewall) — ModSecurity v2 mexanizmi va qoidalar tuzilishi
   - 3.8. WAFning izolyatsiya chegarasi va zaifliklarni bartaraf etishdagi haqiqiy o‘rni
4. [Amaliy mashg‘ulotni bajarish bo‘yicha qadamma-qadam qo‘llanma (Barcha CLI buyruqlarning to‘liq tahlili bilan)](#4-amaliy-mashgulotni-bajarish-boyicha-qadamma-qadam-qollanma)
   - 4.1. 1-qadam: Muhitni tayyorlash, kataloglar yaratish va paketlarni o‘rnatish
   - 4.2. 2-qadam: Python backend (`backend.py`) va Apache konfiguratsiyasi (`httpd.conf`) fayllarini tayyorlash (Dalil D1)
   - 4.3. 3-qadam: O‘quv CA va server sertifikatini yaratish hamda tekshirish (Dalil D2)
   - 4.4. 4-qadam: Alohida Apache nusxasini ishga tushirish va portlarni tekshirish (Dalil D3)
   - 4.5. 5-qadam: TLS protokoli va proksi sarlavhalarini qat’iy tekshirish (Dalil D4)
   - 4.6. 6-qadam: Xavfsizlik sarlavhalari va WAF kuzatish (DetectionOnly) rejimini sinash (Dalil D5)
   - 4.7. 7-qadam: WAFni bloklash (On) rejimiga o‘tkazish va qayta sinov (Dalil D6)
   - 4.8. 8-qadam: Laboratoriya xizmatlarini xavfsiz to‘xtatish va yakunlash
5. [Dalillar (Skrinshotlar) tizimi va Hisobot talablari](#5-dalillar-skrinshotlar-tizimi-va-hisobot-talablari)
   - 5.1. D1 – D6 dalillari bo‘yicha ko‘rsatmalar
   - 5.2. Yakuniy natijalar taqqoslash jadvali
   - 5.3. Hisobot tarkibi va xavfsizlik cheklovlari
6. [Nosozliklarni aniqlash va bartaraf etish (Troubleshooting Guide)](#6-nosozliklarni-aniqlash-va-bartaraf-etish-troubleshooting-guide)
7. [Nazorat savollari va ularning to‘liq ilmiy-amaliy javoblari](#7-nazorat-savollari-va-ularning-toliq-ilmiy-amaliy-javoblari)
8. [Baholash mezonlari (10 ballik tizim)](#8-baholash-mezonlari-10-ballik-tizim)
9. [Qo‘shimcha tahlil: Apache vs Nginx vs IIS arxitekturasi](#9-qoshimcha-tahlil-apache-vs-nginx-vs-iis-arxitekturasi)
10. [Foydalanilgan va tavsiya etiladigan rasmiy manbalar](#10-foydalanilgan-va-tavsiya-etiladigan-rasmiy-manbalar)
11. [ILOVALAR (To‘liq dasturiy kodlar va konfiguratsiyalar)](#11-ilovalari-toliq-dasturiy-kodlar)
    - 11.1. 1-ilova: `backend.py` (Python 3 standart kutubxonasidagi HTTP server)
    - 11.2. 2-ilova: `httpd.conf` (To‘liq birlashtirilgan Apache va ModSecurity konfiguratsiyasi)

---

## 1. LABORATORIYA TAVSIFI VA ISHCHI MUHIT ARXITEKTURASI

Ushbu laboratoriya ishi zamonaviy veb-infrastruktura xavfsizligining eng muhim qismlari — **veb-serverlar xavfsiz konfiguratsiyasi**, **teskari proksi (Reverse Proxy)**, **TLS/HTTPS shifrlash protokollari**, **HTTP xavfsizlik sarlavhalari (Security Headers)** hamda **WAF (Web Application Firewall — ModSecurity)** tizimini amaliyotda o‘rnatish, sozlash va tahlil qilishga bag‘ishlangan.

### 1.1. Sizning ishchi muhitingiz bo‘yicha aniq parametrlar (Ubuntu + VMware)
Sizning ishchi mashinangiz va virtualizatsiya infratuzilmangiz quyidagi arxitekturaga ega:
* **Asosiy mezbon operatsion tizim (Host OS):** **Ubuntu Linux (Ubuntu Desktop)**. *(Mezbon tizim Windows 11 EMAS!)*
* **Virtualizatsiya gipervizori:** Ubuntu Desktop ichida o‘rnatilgan **VMware Workstation**.
* **Mehmon virtual mashina (Guest VM):** VMware ichida ishlaydigan **Ubuntu 24.04 LTS Live Server** (yoki Ubuntu Server VM).
* **Virtual mashina resurslari:** 2 vCPU, 4 GB operativ xotira (RAM), 25 GB qattiq disk, tarmoq adapteri: **NAT**.
* **Foydalanuvchi huquqi:** `sudo` huquqiga ega oddiy foydalanuvchi (`maxfull` yoki `ubuntu`).

### 1.2. Tarmoq konfiguratsiyasi: Shaxsiy Wi-Fi va Proksisiz toza muhit
* Siz **universitet tarmog‘idan (university Wi-Fi) EMAS**, balki **o‘zingizning shaxsiy/lokal Wi-Fi tarmog‘ingizdan** foydalanasiz.
* **Proksisiz toza tarmoq:** Tizimingizda hech qanday universitet proksi-serveri (`proxy.tuit.uz` yoki shunga o‘xshash cheklovchi gatewaylar) talab etilmaydi.
* Internetga to‘g‘ridan-to‘g‘ri shaxsiy routeringiz orqali chiqiladi. Shuning uchun Ubuntu Server VM ichida `apt update`, `apt install` kabi paket o‘rnatish jarayonlari to‘siqlarsiz, to‘g‘ridan-to‘g‘ri rasmiy Ubuntu omborlaridan amalga oshadi.
* **`curl --noproxy "*"` parametrining o‘rni:** Metodik qo‘llanmadagi barcha `curl` buyruqlarida `--noproxy "*"` flagi mavjud. Bu parametr operatsion tizimdagi mumkin bo‘lgan `http_proxy` yoki `https_proxy` muhit o‘zgaruvchilarini e’tiborsiz qoldirib, laboratoriyaning ichki loopback (`127.0.0.1`) so‘rovlarini to‘g‘ridan-to‘g‘ri lokal serverga yo‘naltirishni kafolatlaydi.

### 1.3. Windows 11 masalasi va uning roli
* Sizning VMware virtualizatsiya muhitingizda **Windows 11 Desktop VM** ham oldindan tayyorlab qo‘yilgan.
* **A9 laboratoriyasi uchun qoida:** A9 1-variantidagi barcha amaliy tadqiqotlar (Apache 2.4, ModSecurity 2, OpenSSL, cURL, Python 3) **sof Linux/Ubuntu server terminalida** bajariladi. Barcha tekshiruvlar `curl` va `openssl` CLI vositalari orqali avtomatlashtirilgan.
* **Windows 11 qachon kerak bo‘lishi mumkin?** Agar siz yaratilgan HTTPS xizmatini va xavfsizlik sarlavhalarini (masalan, CSP, X-Frame-Options) brauzer (Chrome/Edge/Firefox) grafik interfeysida ko‘z bilan ko‘rishni va tekshirishni xohlasangiz, Windows 11 VM brauzeridan (yoki asosiy Ubuntu Desktop brauzeringizdan) foydalanishingiz mumkin. Ammo laboratoriyani 100% bajarish, barcha D1–D6 dalillarini to‘plash va topshirish uchun **Ubuntu Server VM terminalining o‘zi to‘liq yetarli** hisoblanadi.

### 1.4. Tizim arxitekturasi va portlar taqsimoti
Tajriba davomida virtual mashina ichida bitta loopback interfeysida (`127.0.0.1`) 3 ta mustaqil port ishlatiladi:

```
[Mijoz: curl / Brauzer]
         │
         ├─── HTTP  (Port 8089)  ──► [Apache HTTP VirtualHost] ──(301 Redirect)──► https://a9.test:8449/
         │
         └─── HTTPS (Port 8449)  ──► [Apache HTTPS VirtualHost]
                                               │
                                      [TLS Termination (TLS 1.2 / 1.3)]
                                               │
                                      [ModSecurity WAF (SecRule 1009001)]
                                      (DetectionOnly: 200 / On: 403 Forbidden)
                                               │
                                      [Reverse Proxy (mod_proxy_http)]
                                      (Header sanitization: unset XFF, set XFP)
                                               │
                                               ▼
                                      [Python Backend (Port 8009)]
                                      (Tashqi tarmoqqa yopiq, faqat 127.0.0.1)
```

| Manzil va Port | Komponent va Xizmat | Vazifasi va Kutiladigan holat |
| :--- | :--- | :--- |
| `http://a9.test:8089` | Apache HTTP VirtualHost | Ochiq HTTP kirish nuqtasi. Barcha so‘rovlarni qat’iy ravishda `301 Moved Permanently` orqali `https://a9.test:8449/` manziliga yo‘naltiradi. |
| `https://a9.test:8449` | Apache HTTPS VirtualHost | Asosiy xavfsizlik darvozasi (TLS Termination + WAF ModSecurity + Teskari Proksi + Xavfsizlik sarlavhalari). Ruxsatli so‘rovlarga `200 OK`, markerli so‘rovga WAF On rejimida `403 Forbidden` qaytaradi. |
| `http://127.0.0.1:8009` | Python 3 Backend xizmati | Ichki biznes-mantiq serveri (`backend.py`). Faqat loopbackda tinglaydi, tashqi portlarga chiqmaydi. Oddiy so‘rovga `A9-BACKEND` markerini, `/headers` ga esa JSON ma’lumotini qaytaradi. |

> **Domen nomi (`a9.test`):** Ushbu o‘quv domeni uchun global DNS yoki `/etc/hosts` faylini tahrirlash shart emas. `curl --resolve a9.test:8449:127.0.0.1` buyrug‘i orqali curl bevosita domen nomini ichki IP ga bog‘laydi va TLS tekshiruvida Server Name Indication (SNI) hamda Host sarlavhasini saqlab qoladi.

---

## 2. MASHG‘ULOTNING MAQSADI VA KUTILADIGAN NATIJALAR

### Mashg‘ulot maqsadi:
1. Maxfiy va himoyalanmagan ichki lokal veb-xizmat (Python backend) oldiga zamonaviy arxitekturaga mos **Apache teskari proksisini (Reverse Proxy)** o‘rnatish.
2. O‘quv sertifikat markazi (**Certificate Authority — CA**) tashkil qilish va domen nomiga (`a9.test`) mos keluvchi rasmiy **SAN (Subject Alternative Name)** atributli server sertifikatini generatsiya qilish.
3. Eskirgan va zaif shifrlash protokollarini (SSLv2, SSLv3, TLS 1.0, TLS 1.1) taqiqlab, faqat **TLS 1.2 va TLS 1.3** shifrlash kanallarini ruxsat etish.
4. Zamonaviy brauzer himoya vositalari bo‘lgan **HTTP xavfsizlik sarlavhalarini** (`Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`) joriy etish va ularning 200, 404 hamda 403 javoblarida to‘liq ishlashini ta’minlash (`Header always`).
5. **ModSecurity (WAF)** modulini o‘rnatib, uning kuzatish (**DetectionOnly**) hamda bloklash (**On**) rejimlari o‘rtasidagi farqni so‘rov status kodi (200 vs 403), WAF qoida identifikatori (`id:1009001`) va backend jurnali (`backend.log`) dalillari asosida amaliy isbotlash.
6. Proksi darajasida mijoz tomonidan kiritilgan soxta sarlavhalarni tozalash (`RequestHeader unset X-Forwarded-For`) va ishonchli sarlavha qo‘shishni (`RequestHeader set X-Forwarded-Proto "https"`) o‘rganish.

### Kutiladigan natijalar:
* Talaba sertifikat zanjiriga ishonch (Chain of Trust) va domen nomining sertifikatga mosligini (Hostname Verification) alohida ajrata oladi.
* HTTP (8089) dan HTTPS (8449) ga 301 yo‘naltirilishi, shuningdek eski TLS versiyalari ulanishining rad etilishi isbotlanadi.
* WAF qoidasining `DetectionOnly` rejimida so‘rov backendga yetib borishi (200 OK), `On` rejimida esa so‘rov Apache darajasida to‘xtatilib, backendga yetib bormasdan mijozga `403 Forbidden` qaytishi jurnal yozuvlari bilan tasdiqlanadi.

---

## 3. NAZARIY ASOSLAR VA XAVFSIZLIK KONSEPSIYALARI

### 3.1. Veb server va teskari proksi (Reverse Proxy vs Forward Proxy)
* **Forward Proxy (To‘g‘ridan-to‘g‘ri proksi):** Mijozlar (foydalanuvchilar) tomonida turadi va ularning internetdagi tashqi serverlarga chiqishini ta’minlaydi yoki nazorat qiladi. Veb-server konfiguratsiyasida ushbu rejim xavfsizlik yuzasidan o‘chirib qo‘yilishi shart:
  ```apache
  ProxyRequests Off
  ```
  *(Agar `ProxyRequests On` qilib qo‘yilsa, server "Open Proxy"ga aylanadi va tajovuzkorlar undan o‘zlarining noqonuniy hujumlarini yashirishda foydalanishi mumkin).*
* **Reverse Proxy (Teskari proksi):** Veb-xizmat (backend) oldida turadi. Tashqi tarmoqdan kelgan barcha mijoz so‘rovlarini o‘zida qabul qiladi, xavfsizlik filtrlaridan o‘tkazadi, TLS shifrlashini yakunlaydi (TLS Termination) va so‘rovni ichki tarmoqdagi haqiqiy dasturga yo‘naltiradi.
  - `ProxyPass / http://127.0.0.1:8009/`: Mijozning barcha URI yo‘llarini ichki backendga uzatadi.
  - `ProxyPassReverse / http://127.0.0.1:8009/`: Backend tomonidan qaytarilgan `Location`, `Content-Location` va `URI` sarlavhalaridagi ichki manzillarni tashqi proksi manziliga moslashtiradi (backendning ichki tuzilmasi tashqariga oshkor bo‘lmaydi).
  - `ProxyPreserveHost On`: Mijoz yuborgan asl `Host` sarlavhasini backendga o‘zgarishsiz uzatadi (virtual hostlar to‘g‘ri ishlashi uchun muhim).

### 3.2. TLS/SSL arxitekturasi, kriptografik zanjir va protokollar nazorati
Transport qatlami xavfsizligi (**TLS — Transport Layer Security**) mijoz va server o‘rtasidagi ma’lumotlarni shifrlash, yaxlitligini kafolatlash va server haqiqiyligini tasdiqlash uchun xizmat qiladi.
* **Eskirgan va xavfli protokollar:** SSLv2, SSLv3, TLS 1.0 va TLS 1.1 protokollarida jiddiy kriptografik zaifliklar (POODLE, BEAST, CRIME, DROWN) mavjud. Zamonaviy xavfsizlik standartlarida (PCI-DSS, NIST SP 800-52r2) ularni ishlatish qat’iyan man etiladi.
* **Xavfsiz konfiguratsiya:**
  ```apache
  SSLProtocol -all +TLSv1.2 +TLSv1.3
  ```
  Bu direktiva barcha protokollarni butunlay o‘chirib (`-all`), faqat eng zamonaviy va xavfsiz **TLS 1.2 hamda TLS 1.3** protokollariga ruxsat beradi.

### 3.3. PKI (Public Key Infrastructure): O‘quv CA, Server sertifikati, SAN va Zanjir ishonchi
Raqamli sertifikatlar ochiq kalitlar infratuzilmasiga (PKI) tayanadi.
* **O‘quv Sertifikat Markazi (Root CA):** O‘z-o‘zini imzolagan (self-signed) ildiz sertifikat (`ca.crt`) va uning maxfiy kaliti (`ca.key`). CA server sertifikatlarini tasdiqlash uchun imzo qo‘yadi.
  - `basicConstraints=critical,CA:TRUE`: Ushbu sertifikat boshqa sertifikatlarni imzolash vakolatiga ega ekanini belgilaydi.
* **Server sertifikati va So‘rov (CSR):** Server o‘zining yopiq kalitini (`server.key`) yaratadi va sertifikat so‘rovini (`server.csr`) shakllantiradi. CA ushbu so‘rovni tekshirib, serverga `server.crt` sertifikatini taqdim etadi.
  - `basicConstraints=critical,CA:FALSE`: Server sertifikati boshqa sertifikat imzolay olmaydi.
* **SAN (Subject Alternative Name) standarti (RFC 2818, RFC 6125):**
  Eski tizimlarda domen nomi sertifikatning `Common Name (CN)` maydonidan olingan. Zamonaviy brauzerlar va `curl` vositasi CN maydoniga ishonmaydi! Domen nomi sertifikatning **X.509 v3 kengaytmasidagi `subjectAltName` (SAN)** maydonida (`DNS:a9.test`) aniq ko‘rsatilgan bo‘lishi shart.
* **Ikki mustaqil tekshiruv qatlami:**
  1. **Ishonch zanjiri (Chain of Trust):** Server taqdim etgan sertifikat mijoz ishonadigan CA tomonidan imzolanganmi? (Agar mijozda CA bo‘lmasa — `curl: (60) SSL certificate problem: unable to get local issuer certificate`).
  2. **Domen mosligi (Hostname Verification):** Mijoz so‘rov yuborayotgan domen nomi (masalan, `wrong.test`) server sertifikatining SAN ro‘yxatida bormi? Agar sertifikat eng ishonchli CA tomonidan imzolangan bo‘lsa ham, domen mos kelmasa ulanish to‘xtatiladi (`curl: (60) SSL: certificate subject name does not match target host name`).

### 3.4. HTTP Xavfsizlik sarlavhalari (Security Headers) va `Header always` zarurati
HTTP sarlavhalari brauzerga veb-sahifa kontentini qanday xavfsiz qayta ishlash kerakligi haqida qat’iy ko‘rsatmalar beradi:
* **`X-Content-Type-Options: "nosniff"`:** Brauzerning MIME-sniffing xususiyatini o‘chiradi. Server `Content-Type` sarlavhasida nima deb ko‘rsatgan bo‘lsa (masalan, `text/plain`), brauzer faylni aynan shu formatda ochadi; tajovuzkorning rasm ichiga yashirilgan zararli JavaScript kodini HTML sifatida talqin qilishiga yo‘l qo‘ymaydi.
* **`X-Frame-Options: "DENY"`:** Saytni `<iframe>`, `<frame>`, `<embed>` yoki `<object>` ichida yuklashni butunlay taqiqlaydi. Bu orqali foydalanuvchini aldamchi ko‘rinmas freymlar yordamida tugmalarni bosishga majburlash (**Clickjacking / UI Redressing**) hujumlarining oldi olinadi.
* **`Referrer-Policy: "no-referrer"`:** Saytdan tashqi havolalarga o‘tilganda yoki resurslar yuklanganda brauzer `Referer` sarlavhasida sahifa manzilini oshkor qilmaydi (URL ichidagi maxfiy tokenlar yoki sessiya parametrlari sizib chiqishini to‘xtatadi).
* **`Content-Security-Policy (CSP)`:** XSS (Cross-Site Scripting) va ma’lumotlarni ruxsatsiz kiritishga qarshi eng kuchli vosita:
  ```http
  default-src 'self'; frame-ancestors 'none'; object-src 'none'
  ```
  - `default-src 'self'`: Skript, rasm va boshqa barcha resurslar faqat o‘z manzilidan yuklanishiga ruxsat beradi.
  - `frame-ancestors 'none'`: Sahifani boshqa saytlarda freym qilishni taqiqlaydi (zamonaviy Clickjacking himoyasi).
  - `object-src 'none'`: Flash, Java applet kabi eskirgan plaginlarni bloklaydi.
* **Nega `Header always set` ishlatiladi?**
  Apache veb-serverida oddiy `Header set` faqat muvaffaqiyatli (`2xx`, `3xx`) javoblar uchun sarlavha qo‘shadi. Agar so‘rov xatolik bilan tugasa (`400`, `403 Forbidden`, `404 Not Found`, `500`), oddiy direktiva ishlamaydi va xavfsizlik sarlavhalari tushib qoladi!
  `Header always set` direktivasi sarlavhalarni javob statusidan qat’i nazar (shu jumladan WAF bloklagan `403` yoki `404` xatolarida ham) mijozga majburiy jo‘natilishini kafolatlaydi.

### 3.5. Server ma’lumotlarini yashirish va metodlar nazorati (Information Disclosure & XST)
* **`ServerTokens Prod`:** Apache javobidagi `Server` sarlavhasini minimal holatga keltiradi (faqat `Server: Apache` ko‘rsatiladi; operatsion tizim versiyasi, o‘rnatilgan modullar va patch raqamlari yashiriladi).
* **`ServerSignature Off`:** Xato sahifalari tagida server versiyasi va server nomini ko‘rsatuvchi ma’lumotlar qatorini o‘chiradi.
* **`TraceEnable Off`:** HTTP `TRACE` metodini butunlay o‘chiradi. Ushbu metod so‘rovni mijozga aks ettirib qaytaradi, bu esa XSS orqali `HttpOnly` cookie-fayllarini o‘g‘irlashga qaratilgan **Cross-Site Tracing (XST)** hujumlariga yo‘l ochadi.

### 3.6. Proksi sarlavhalarini soxtalashtirish (Header Spoofing) va tozalash mexanizmi
Tashqi mijoz veb-serverga o‘zboshimcha soxta sarlavhalar yuborishi mumkin (masalan, `X-Forwarded-For: 198.51.100.77` yoki `X-Forwarded-Proto: http`). Agar backend server ushbu sarlavhalarga ko‘r-ko‘rona ishonsa, IP-ga asoslangan cheklovlar chetlab o‘tiladi (IP Spoofing) yoki protokollar chalkashadi.
Shu sababli proksi server kiruvchi soxta sarlavhalarni tozalashi shart:
```apache
RequestHeader unset X-Forwarded-For
RequestHeader set X-Forwarded-Proto "https"
```
* `RequestHeader unset X-Forwarded-For`: Mijoz kiritgan soxta IP sarlavhasini o‘chirib tashlaydi. `mod_proxy` uning o‘rniga haqiqiy TCP ulanish o‘rnatgan mijoz IP manzilini (`127.0.0.1`) ishonchli tarzda joylashtiradi.
* `RequestHeader set X-Forwarded-Proto "https"`: Tashqaridan ulanish HTTPS orqali amalga oshirilganini backendga qat’iy bildiradi.

### 3.7. WAF (Web Application Firewall) — ModSecurity v2 mexanizmi va qoidalar tuzilishi
ModSecurity — veb-ilovalar uchun 7-qatlam (Application Layer) xavfsizlik devori bo‘lib, kiruvchi HTTP/HTTPS so‘rovlari va chiquvchi javoblarni real vaqt rejimida tahlil qiladi.
* **Asosiy ishlash rejimlari (`SecRuleEngine`):**
  1. `DetectionOnly`: Kuzatuv rejimi. ModSecurity so‘rovlarni qoidalar bo‘yicha tekshiradi. Moslik topilsa, log fayllariga (`error.log`, `audit.log`) yozadi, ammo `deny` amali bo‘lsa ham so‘rovni BLOKLAMAYDI! So‘rov backendga to‘siqsiz yetib boradi va `200 OK` qaytadi. Ushbu rejim qoidalarni ishlab chiqarish muhitiga kiritishdan oldin yolg‘on musbat (false positive) natijalarni o‘rganish uchun ishlatiladi.
  2. `On`: Haqiqiy faol bloklash rejimi. Qoidaga mos keluvchi har qanday so‘rov zudlik bilan to‘xtatiladi, backendga uzatilmaydi va mijozga `403 Forbidden` xatosi qaytariladi.
* **O‘quv qoidasining anatomiyasi:**
  ```apache
  SecRule ARGS:probe "@streq A9-WAF-TEST" \
  "id:1009001,phase:2,t:none,deny,status:403,log,auditlog,msg:'A9 marker'"
  ```
  - `ARGS:probe`: Tekshiriladigan nishon — URL query parametrlaridagi yoki formadagi `probe` argumentining qiymati.
  - `@streq A9-WAF-TEST`: Operator — satr aynan `A9-WAF-TEST` matniga teng bo‘lishini tekshiradi.
  - `id:1009001`: Qoidaning yagona raqamli identifikatori (ID).
  - `phase:2`: So‘rovni tahlil qilish bosqichi (Request Body phase — sarlavhalar va argumentlar to‘liq qabul qilingan payt).
  - `t:none`: Qoida uchun maxsus transformatsiya filtrlarini qo‘llamaslik (standart URL-dekodlash baribir bajariladi).
  - `deny`: Agar operator `true` qaytarsa, so‘rovni darhol rad etish.
  - `status:403`: Mijozga qaytariladigan HTTP holat kodi (`403 Forbidden`).
  - `log, auditlog`: Moslik haqida Apache xatolar jurnaliga (`error.log`) hamda WAF audit jurnaliga (`audit.log`) batafsil yozish.
  - `msg:'A9 marker'`: Jurnalda ko‘rinadigan tushuntirish xabari.

### 3.8. WAFning izolyatsiya chegarasi va zaifliklarni bartaraf etishdagi haqiqiy o‘rni
* **WAF kod zaifliklarini tuzatmaydi!** WAF tashqi tomondan kelayotgan hujum simptomlarini filtrlaydi, ammo ilovadagi asosiy arxitektura xatolari (SQL inyeksiya, XSS, BOLA/IDOR) kod darajasida xavfsiz dasturlash orqali tuzatilishi shart.
* **Bypass (Aylanib o‘tish) xavfi:** Agar ichki backend (`http://127.0.0.1:8009`) lokal tarmoqdagi yoki shu serverdagi boshqa foydalanuvchilar uchun ochiq bo‘lsa, tajovuzkor Apache proksisini chetlab o‘tib, backendga to‘g‘ridan-to‘g‘ri murojaat qilishi mumkin. Bu holda WAF so‘rovni umuman ko‘rmaydi. Shuning uchun ishlab chiqarishda backend tarmoq xavfsizlik devori (iptables/nftables) va servis huquqlari bilan qat’iy izolyatsiya qilinishi talab etiladi.

---

## 4. AMALIY MASHG‘ULOTNI BAJARISH BO‘YICHA QADAMMA-QADAM QO‘LLANMA

Ushbu bo‘limda barcha vazifalar ketma-ket, har bir CLI buyrug‘ining maqsadi, har bir parametri va kutiladigan natijasi bilan batafsil keltirilgan.

### 4.1. 1-qadam: Muhitni tayyorlash, kataloglar yaratish va paketlarni o‘rnatish

Ubuntu Server VM terminalini oching. Barcha buyruqlar Bash qobig‘ida bajariladi.

#### 1-bosqich: Paketlar bazasini yangilash va zarur dasturlarni o‘rnatish
```bash
sudo apt update
sudo apt install -y apache2 libapache2-mod-security2 openssl curl python3
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `sudo`: Buyruqni administrator (root) huquqi bilan bajarish.
* `apt update`: Ubuntu repozitoriylaridagi paketlar ro‘yxatini va so‘nggi versiyalar indeksini yangilash (shaxsiy Wi-Fi orqali to‘g‘ridan-to‘g‘ri internetdan olinadi).
* `apt install`: Yangi dasturiy paketlarni o‘rnatish.
* `-y`: O‘rnatish jarayonida tasdiqlash so‘rovlariga avtomatik "Yes" (Ha) deb javob berish.
* `apache2`: Apache HTTP Server 2.4 veb-server dasturi.
* `libapache2-mod-security2`: Apache uchun ModSecurity v2 veb-ilovalar xavfsizlik devori (WAF) moduli.
* `openssl`: Kriptografik kalitlar, CA va SSL/TLS sertifikatlarini boshqarish vositasi.
* `curl`: Buyruqlar satridan HTTP/HTTPS so‘rovlarini yuboruvchi tarmoq mijoz vositasi.
* `python3`: Standart Python 3 interpretatori (bizning sodda backendimizni ishlatish uchun).

#### 2-bosqich: Loyiha va tizim kataloglarini yaratish
```bash
mkdir -p ~/a9-lab
cd ~/a9-lab
sudo mkdir -p /opt/a9-lab/{run,logs,tls}
sudo chmod 755 /opt/a9-lab /opt/a9-lab/{run,logs,tls}
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `mkdir -p ~/a9-lab`: Talabaning uy katalogida (`/home/maxfull/a9-lab`) amaliy ish fayllarini saqlash uchun papka yaratish (`-p` — agar papka mavjud bo‘lsa xato bermaydi, oraliq kataloglarni ham hosil qiladi).
* `cd ~/a9-lab`: Yaratilgan ishchi katalogga o‘tish.
* `sudo mkdir -p /opt/a9-lab/{run,logs,tls}`: Tizimning `/opt` bo‘limida alohida Apache nusxasi uchun ishchi kataloglarni yaratish:
  - `/opt/a9-lab/run`: Apache jarayonining PID fayli (`httpd.pid`) saqlanadigan joy.
  - `/opt/a9-lab/logs`: Kirish, xato va audit jurnallari (`access.log`, `error.log`, `audit.log`) joylashadigan katalog.
  - `/opt/a9-lab/tls`: TLS server sertifikati (`server.crt`) va maxfiy kaliti (`server.key`) saqlanadigan xavfsiz katalog.
* `sudo chmod 755 ...`: Ushbu kataloglarga barcha foydalanuvchilar va Apache ishchi jarayoni (`www-data`) kirishi hamda fayllarni o‘qiy olishi uchun `rwxr-xr-x` (755) ruxsatini berish.

---

### 4.2. 2-qadam: Python backend va Apache konfiguratsiyasi fayllarini tayyorlash (Dalil D1)

#### 1-bosqich: `backend.py` faylini yaratish
`~/a9-lab/backend.py` faylini yarating:
```bash
nano ~/a9-lab/backend.py
```
Fayl ichiga quyidagi to‘liq kodni kiriting va saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`):
```python
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

class App(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        status, mime = 200, 'text/html; charset=utf-8'
        if path == '/headers':
            mime = 'application/json'
            body = json.dumps({
                'marker': 'A9-BACKEND',
                'host': self.headers.get('Host'),
                'proto': self.headers.get('X-Forwarded-Proto'),
                'client': self.headers.get('X-Forwarded-For'),
            }).encode()
        elif path == '/':
            body = b'<!doctype html><title>A9</title><h1>A9-BACKEND</h1>'
        else:
            status, mime, body = 404, 'text/plain', b'A9-NOT-FOUND'
            
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    print('A9 backend: http://127.0.0.1:8009', flush=True)
    HTTPServer(('127.0.0.1', 8009), App).serve_forever()
```

#### 2-bosqich: `httpd.conf` faylini yaratish (A va B qismlarini birlashtirish)
`~/a9-lab/httpd.conf` faylini yarating:
```bash
nano ~/a9-lab/httpd.conf
```
Fayl ichiga A va B qismlari birlashtirilgan quyidagi to‘liq konfiguratsiyani kiriting:
```apache
ServerRoot "/opt/a9-lab"
DefaultRuntimeDir "/opt/a9-lab/run"
PidFile "/opt/a9-lab/run/httpd.pid"
ServerName a9.test

Listen 127.0.0.1:8089
Listen 127.0.0.1:8449

LoadModule mpm_event_module /usr/lib/apache2/modules/mod_mpm_event.so
LoadModule authz_core_module /usr/lib/apache2/modules/mod_authz_core.so
LoadModule authz_host_module /usr/lib/apache2/modules/mod_authz_host.so
LoadModule alias_module /usr/lib/apache2/modules/mod_alias.so
LoadModule ssl_module /usr/lib/apache2/modules/mod_ssl.so
LoadModule headers_module /usr/lib/apache2/modules/mod_headers.so
LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so
LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so
LoadModule unique_id_module /usr/lib/apache2/modules/mod_unique_id.so
LoadModule security2_module /usr/lib/apache2/modules/mod_security2.so

User www-data
Group www-data

ServerTokens Prod
ServerSignature Off
TraceEnable Off
ProxyRequests Off

ErrorLog "/opt/a9-lab/logs/error.log"
LogLevel warn
LogFormat "%h %t \"%r\" %>s %b" a9
CustomLog "/opt/a9-lab/logs/access.log" a9

<Directory />
    Require all denied
</Directory>

<Proxy "http://127.0.0.1:8009/">
    Require all granted
</Proxy>

<VirtualHost 127.0.0.1:8089>
    ServerName a9.test
    Redirect permanent / https://a9.test:8449/
</VirtualHost>

<VirtualHost 127.0.0.1:8449>
    ServerName a9.test
    SSLEngine On
    SSLCertificateFile "/opt/a9-lab/tls/server.crt"
    SSLCertificateKeyFile "/opt/a9-lab/tls/server.key"
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    
    ProxyPreserveHost On
    RequestHeader unset X-Forwarded-For
    RequestHeader set X-Forwarded-Proto "https"
    ProxyPass / http://127.0.0.1:8009/ connectiontimeout=3 timeout=5
    ProxyPassReverse / http://127.0.0.1:8009/
    
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "DENY"
    Header always set Referrer-Policy "no-referrer"
    Header always set Content-Security-Policy \
        "default-src 'self'; frame-ancestors 'none'; object-src 'none'"
        
    SecRuleEngine DetectionOnly
    SecRequestBodyAccess On
    SecAuditEngine RelevantOnly
    SecAuditLogType Serial
    SecAuditLogParts ABFHZ
    SecAuditLog "/opt/a9-lab/logs/audit.log"
    
    SecRule ARGS:probe "@streq A9-WAF-TEST" \
        "id:1009001,phase:2,t:none,deny,status:403,log,auditlog,msg:'A9 marker'"
</VirtualHost>
```

#### 3-bosqich: Sintaksis va versiyalarni tekshirish hamda backendni ishga tushirish (Dalil D1)
```bash
python3 -m py_compile backend.py
apache2 -v
openssl version
curl --version
dpkg-query -W apache2 libapache2-mod-security2
python3 -u backend.py 2>&1 | tee backend.log
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `python3 -m py_compile backend.py`: Python kodi sintaksisida xatolik yo‘qligini kompilyatsiya orqali tekshirish (`__pycache__` yaratiladi).
* `apache2 -v`: O‘rnatilgan Apache serverining rasmiy versiyasini ko‘rsatish (masalan, `Apache/2.4.58 (Ubuntu)`).
* `openssl version`: O‘rnatilgan OpenSSL kutubxonasi versiyasini tekshirish (masalan, `OpenSSL 3.0.13`).
* `curl --version`: `curl` mijozi versiyasi va u qo‘llab-quvvatlaydigan protokollar (HTTP, HTTPS, TLS) ro‘yxatini ko‘rish.
* `dpkg-query -W apache2 libapache2-mod-security2`: Ubuntu paketlar menejeri orqali tizimga o‘rnatilgan Apache va ModSecurity paketlarining aniq versiyalarini chiqarish.
* `python3 -u backend.py`: Backend skriptini ishga tushirish. `-u` (unbuffered) bayrog‘i kiritish-chiqarish oqimini buferlamaydi, ya’ni serverga kelgan har bir so‘rov darhol ekranga va jurnalga chiqadi.
* `2>&1`: Standart xatolik oqimini (stderr — 2) standart chiqish oqimiga (stdout — 1) birlashtirish.
* `| tee backend.log`: Chiqayotgan ma’lumotlarni bir vaqtning o‘zida ham terminal ekranida ko‘rsatish, ham `backend.log` fayliga saqlash.

Terminalda quyidagi satr paydo bo‘ladi va jarayon ochiq qoladi:
```
A9 backend: http://127.0.0.1:8009
```
> **DIQQAT:** Ushbu **1-terminalni yopmang!** Endi yangi **2-terminalni** oching.

#### 4-bosqich: 2-terminalda backendni to‘g‘ridan-to‘g‘ri sinash
Yangi ochilgan 2-terminalda quyidagi buyruqlarni bajaring:
```bash
cd ~/a9-lab
curl --noproxy "*" -i http://127.0.0.1:8009/
curl --noproxy "*" -i http://127.0.0.1:8009/headers
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `curl`: HTTP so‘rov yuborish.
* `--noproxy "*"`: Barcha proksilarni chetlab o‘tib, so‘rovni to‘g‘ridan-to‘g‘ri 127.0.0.1 ga yo‘naltirish.
* `-i`: Server qaytargan HTTP javob sarlavhalarini (Status code, Content-Type, Content-Length) tana (body) bilan birga ko‘rsatish.
* `http://127.0.0.1:8009/`: Asosiy sahifani so‘rash. Javob: `HTTP/1.0 200 OK` va `<h1>A9-BACKEND</h1>`.
* `http://127.0.0.1:8009/headers`: Sarlavhalar endpointini so‘rash. Javob: `HTTP/1.0 200 OK` va JSON:
  `{"marker": "A9-BACKEND", "host": "127.0.0.1:8009", "proto": null, "client": null}`. *(To‘g‘ridan-to‘g‘ri ulanishda proto va client null bo‘lishi tabiiy, chunki hali proksi ulanmagan).*

📸 **DALIL D1:** Dastur versiyalari, backend 200 javoblari va 1-terminaldagi server jurnali aks etgan skrinshot olinadi.

---

### 4.3. 3-qadam: O‘quv CA va server sertifikatini yaratish hamda tekshirish (Dalil D2)

Ushbu qadam 2-terminalda bajariladi.

#### 1-bosqich: O‘quv CA (Certificate Authority) yaratish
```bash
umask 077
mkdir -p ~/a9-ca
cd ~/a9-ca
openssl req -x509 -newkey rsa:2048 -nodes -days 7 \
  -keyout ca.key -out ca.crt -subj "/CN=A9 Lab Root" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `umask 077`: Yangi yaratiladigan fayllarga faqat joriy foydalanuvchi uchun o‘qish va yozish huquqini berish (`-rw-------`), boshqa foydalanuvchilarga esa butunlay yopish. Bu maxfiy kalitlar (`.key`) xavfsizligi uchun o‘ta muhim.
* `mkdir -p ~/a9-ca && cd ~/a9-ca`: CA kalitlarini saqlash uchun alohida katalog ochish va unga o‘tish.
* `openssl req`: PKI so‘rovlari va sertifikatlarini boshqarish sub-buyrug‘i.
* `-x509`: Sertifikat so‘rovi (CSR) o‘rniga to‘g‘ridan-to‘g‘ri o‘z-o‘zini imzolagan (self-signed) Root CA sertifikatini shakllantirish.
* `-newkey rsa:2048`: 2048 bit uzunlikdagi yangi RSA kalitlar juftligini yaratish.
* `-nodes`: "No DES" — maxfiy kalitni parol bilan shifrlamaslik (avtomatlashtirilgan laboratoriya uchun kalitni parolsiz saqlash).
* `-days 7`: CA sertifikatining amal qilish muddatini 7 kun qilib belgilash.
* `-keyout ca.key`: Yaratilgan CA maxfiy kalitini `ca.key` fayliga yozish.
* `-out ca.crt`: Ommaviy CA sertifikatini `ca.crt` fayliga yozish.
* `-subj "/CN=A9 Lab Root"`: Sertifikat egasining nomini (Common Name) "A9 Lab Root" qilib belgilash.
* `-addext "basicConstraints=critical,CA:TRUE"`: X.509 v3 kengaytmasi: bu sertifikat haqiqiy Sertifikat Markazi (CA) ekanini va boshqa sertifikatlarni imzolash huquqiga egaligini qat’iy belgilash.
* `-addext "keyUsage=critical,keyCertSign,cRLSign"`: Kalit faqat sertifikat va bekor qilish ro‘yxatlarini (CRL) imzolash uchun mo‘ljallanganini ko‘rsatish.

#### 2-bosqich: Server maxfiy kaliti, so‘rovi (CSR) va SAN konfiguratsiyasini yaratish
```bash
openssl req -new -newkey rsa:2048 -nodes \
  -keyout server.key -out server.csr -subj "/CN=a9.test"

cat > server.ext <<'EOF'
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:a9.test
EOF
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `openssl req -new -newkey rsa:2048 -nodes`: Server uchun yangi 2048 bitli RSA kalit va sertifikat so‘rovi yaratish.
* `-keyout server.key`: Serverning maxfiy kalitini `server.key` fayliga yozish.
* `-out server.csr`: Sertifikat so‘rovini (Certificate Signing Request) `server.csr` fayliga chiqarish.
* `-subj "/CN=a9.test"`: Serverning asosiy domen nomini `a9.test` deb ko‘rsatish.
* `cat > server.ext <<'EOF'`: Server sertifikati uchun X.509 v3 kengaytmalar faylini (`server.ext`) hosil qilish:
  - `basicConstraints=critical,CA:FALSE`: Ushbu sertifikat CA emas (oxirgi tugun sertifikati).
  - `keyUsage=critical,digitalSignature,keyEncipherment`: Kalit raqamli imzo va TLS kalit almashinuvini shifrlash uchun xizmat qiladi.
  - `extendedKeyUsage=serverAuth`: Ushbu sertifikat faqat TLS veb-server autentifikatsiyasi uchun yaroqli.
  - `subjectAltName=DNS:a9.test`: Zamonaviy brauzerlar talab qiladigan rasmiy domen nomi (`a9.test`).

#### 3-bosqich: Server sertifikatini CA kaliti bilan imzolash
```bash
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -days 7 -sha256 -extfile server.ext
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `openssl x509`: X.509 sertifikatlarini imzolash va boshqarish buyrug‘i.
* `-req -in server.csr`: Kiruvchi ma’lumot sifatida `server.csr` so‘rov faylini olish.
* `-CA ca.crt -CAkey ca.key`: Sertifikatni imzolash uchun biz yaratgan Root CA sertifikati va uning maxfiy kalitidan foydalanish.
* `-CAcreateserial`: Har bir imzolangan sertifikat uchun unikal seriya raqami faylini (`ca.srl`) yaratish.
* `-out server.crt`: Imzolangan tayyor server sertifikatini `server.crt` fayliga saqlash.
* `-days 7`: Sertifikatning amal qilish muddatini 7 kun qilib belgilash.
* `-sha256`: Imzolashda xavfsiz SHA-256 xeshlash algoritmidan foydalanish.
* `-extfile server.ext`: Yuqorida tuzilgan SAN va boshqa kengaytmalarni sertifikat ichiga joylashtirish.

#### 4-bosqich: Sertifikat atributlari va domen mosligini tekshirish
```bash
openssl x509 -in server.crt -noout -subject -issuer -dates
openssl x509 -in server.crt -noout -ext subjectAltName
openssl verify -CAfile ca.crt -verify_hostname a9.test server.crt
openssl verify -CAfile ca.crt -verify_hostname wrong.test server.crt
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `openssl x509 -in server.crt -noout`: Sertifikat tanasini (kodlangan matnini) ko‘rsatmasdan, faqat so‘ralgan maydonlarni chiqarish.
* `-subject -issuer -dates`: Sertifikat egasini (`subject = CN = a9.test`), uni imzolagan CA ni (`issuer = CN = A9 Lab Root`) hamda amal qilish muddatlarini ko‘rish.
* `-ext subjectAltName`: Sertifikat ichidagi SAN maydonini tekshirish. Kutiladigan natija: `DNS:a9.test`.
* `openssl verify -CAfile ca.crt -verify_hostname a9.test server.crt`: Sertifikatni `ca.crt` orqali zanjir bo‘yicha va `a9.test` domeniga nisbatan tekshirish. Kutiladigan natija: `server.crt: OK`.
* `openssl verify -CAfile ca.crt -verify_hostname wrong.test server.crt`: Ayni sertifikatni noto‘g‘ri nom (`wrong.test`) bilan tekshirish. Kutiladigan natija: `hostname mismatch` xatosi. Bu sertifikat CA tomonidan tasdiqlangan bo‘lsa ham, begona domenlar uchun o‘tmasligini isbotlaydi!

#### 5-bosqich: Kalit va sertifikatni Apache katalogiga o‘rnatish
```bash
sudo install -m 600 server.key /opt/a9-lab/tls/server.key
sudo install -m 644 server.crt /opt/a9-lab/tls/server.crt
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `sudo install`: Faylni ko‘chirish va unga bir vaqtning o‘zida aniq huquqlarni (permissions) berish.
* `-m 600`: `server.key` fayliga faqat root foydalanuvchisi uchun o‘qish-yozish huquqini (`-rw-------`) o‘rnatish (maxfiy kalit o‘g‘irlanishining oldini oladi).
* `-m 644`: `server.crt` ochiq sertifikat fayliga barcha foydalanuvchilar va `www-data` uchun o‘qish huquqini (`-rw-r--r--`) berish.

📸 **DALIL D2:** Subject, issuer, muddat, SAN, to‘g‘ri nom (`server.crt: OK`) va noto‘g‘ri nom (`hostname mismatch`) natijalari aks etgan skrinshot olinadi.

---

### 4.4. 4-qadam: Alohida Apache nusxasini ishga tushirish va portlarni tekshirish (Dalil D3)

Ushbu qadamda tizimning asosiy Apache xizmatiga tegmasdan, faqat bizning `/opt/a9-lab/httpd.conf` konfiguratsiyamiz asosida ishlaydigan alohida Apache instansi ishga tushiriladi.

#### 1-bosqich: Konfiguratsiyani o‘rnatish, sintaksis va modullarni tekshirish
```bash
cd ~/a9-lab
sudo install -m 644 httpd.conf /opt/a9-lab/httpd.conf
sudo apache2 -t -f /opt/a9-lab/httpd.conf
sudo apache2 -M -f /opt/a9-lab/httpd.conf
sudo apache2 -f /opt/a9-lab/httpd.conf -k start
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `sudo install -m 644 httpd.conf /opt/a9-lab/httpd.conf`: Tayyorlangan konfiguratsiya faylini `/opt/a9-lab` tizim katalogiga xavfsiz o‘rnatish.
* `apache2 -t -f /opt/a9-lab/httpd.conf`: Konfiguratsiya fayli sintaksisini tekshirish (`-t` — test syntax, `-f` — alohida konfiguratsiya fayli yo‘li).
  > **Kutiladigan natija:** `Syntax OK`. Agar sintaksisda xatolik bo‘lsa, keyingi buyruqlar bajarilmaydi!
* `apache2 -M -f /opt/a9-lab/httpd.conf`: Yuklangan barcha Apache modullarini ro‘yxat shaklida chiqarish. Ro‘yxatda quyidagi modullar mavjudligi tekshiriladi:
  - `ssl_module` (TLS shifrlash)
  - `headers_module` (Xavfsizlik sarlavhalari)
  - `proxy_module` va `proxy_http_module` (Teskari proksi)
  - `security2_module` (ModSecurity WAF)
* `sudo apache2 -f /opt/a9-lab/httpd.conf -k start`: Alohida Apache nusxasini fon rejimida ishga tushirish (`-k start` signali).

#### 2-bosqich: Faol portlarni va HTTP/HTTPS ulanishini tekshirish
```bash
ss -ltn | grep -E ":(8009|8089|8449)[[:space:]]"
CA="$HOME/a9-ca/ca.crt"
URL="https://a9.test:8449"

curl --noproxy "*" --resolve a9.test:8089:127.0.0.1 \
  -i http://a9.test:8089/

curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" -i "$URL/"
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `ss -ltn`: Tizimdagi barcha tinglovchi (listening — `-l`), TCP (`-t`), raqamli portlarni (numeric — `-n`) ko‘rsatish.
* `grep -E ":(8009|8089|8449)[[:space:]]"`: Faqat bizning 3 ta portimiz (8009, 8089, 8449) `127.0.0.1` manzilida faol ekanini filtrlash.
* `CA="$HOME/a9-ca/ca.crt"`: CA sertifikati yo‘lini qobiq o‘zgaruvchisiga biriktirish.
* `URL="https://a9.test:8449"`: Asosiy HTTPS manzilini o‘zgaruvchiga olish.
* `curl ... http://a9.test:8089/`: Ochiq HTTP portiga so‘rov yuborish.
  - `--resolve a9.test:8089:127.0.0.1`: DNS ni chetlab o‘tib, `a9.test:8089` manzilini to‘g‘ridan-to‘g‘ri `127.0.0.1` ga bog‘lash.
  - **Kutiladigan natija:** `HTTP/1.1 301 Moved Permanently` va `Location: https://a9.test:8449/`.
* `curl ... "$URL/"`: Xavfsiz HTTPS portiga so‘rov yuborish.
  - `--cacert "$CA"`: So‘rov yuborishda server sertifikatini tekshirish uchun o‘zimiz yaratgan `ca.crt` faylidan foydalanish.
  - **Kutiladigan natija:** `HTTP/1.1 200 OK` va sahifa tanasida `<h1>A9-BACKEND</h1>` yozuvi.

📸 **DALIL D3:** Syntax OK, modullar ro‘yxati, 3 ta faol port (`ss`), HTTP 8089 dan 301 yo‘naltirish va HTTPS 8449 orqali olingan 200 OK javobi aks etgan skrinshot olinadi.

---

### 4.5. 5-qadam: TLS protokoli va proksi sarlavhalarini qat’iy tekshirish (Dalil D4)

Ushbu qadamda TLS zanjiri ishonchi, domen nomi nazorati, TLS 1.2/1.3 protokollari hamda proksi sarlavhalari xavfsizligi sinovdan o‘tkaziladi.

#### 1-bosqich: Sertifikat xatolarini (CA yo‘qligi va noto‘g‘ri nom) alohida isbotlash
```bash
curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  -i "$URL/"

curl --noproxy "*" --resolve wrong.test:8449:127.0.0.1 \
  --cacert "$CA" -i https://wrong.test:8449/
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `curl -i "$URL/"` (CA ko‘rsatilmagan): Mijozga server sertifikatini tasdiqlovchi CA berilmagan.
  - **Kutiladigan natija:** `curl: (60) SSL certificate problem: unable to get local issuer certificate`.
* `curl --cacert "$CA" https://wrong.test:8449/` (Noto‘g‘ri domen): CA to‘g‘ri berilgan, lekin so‘rov server sertifikatida bo‘lmagan `wrong.test` nomiga yuborilmoqda.
  - **Kutiladigan natija:** `curl: (60) SSL: certificate subject name (a9.test) does not match target host name 'wrong.test'`.
  > **Muhim xulosa:** Ikkala holda ham xatolik kodi `curl (60)` bo‘lsa-da, ularning sababi tubdan farq qiladi: birinchisida ishonch zanjiri yo‘q, ikkinchisida esa domen nomi mos emas!

#### 2-bosqich: Faqat TLS 1.2 va TLS 1.3 protokollarini alohida sinash
```bash
curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" --tlsv1.2 --tls-max 1.2 -i "$URL/"

curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" --tlsv1.3 --tls-max 1.3 -i "$URL/"
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `--tlsv1.2 --tls-max 1.2`: Mijozni faqat TLS 1.2 protokoli bilan ulanishga majburlash. Javob: `HTTP/1.1 200 OK`.
* `--tlsv1.3 --tls-max 1.3`: Mijozni faqat TLS 1.3 protokoli bilan ulanishga majburlash. Javob: `HTTP/1.1 200 OK`.

#### 3-bosqich: OpenSSL s_client orqali qo‘shimcha protokollar tahlili
```bash
openssl s_client -connect 127.0.0.1:8449 -servername a9.test \
  -CAfile "$CA" -verify_hostname a9.test -verify_return_error \
  -tls1_2 -brief < /dev/null
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `openssl s_client`: TLS ulanishini past darajali (low-level) diagnostika qilish.
* `-connect 127.0.0.1:8449`: Server IP va portiga ulanish.
* `-servername a9.test`: SNI (Server Name Indication) sarlavhasida `a9.test` domenini uzatish.
* `-CAfile "$CA"`: Ishonchli CA faylini ko‘rsatish.
* `-verify_hostname a9.test`: Domen nomini sertifikat bilan solishtirish.
* `-verify_return_error`: Agar tekshiruvda xatolik bo‘lsa zudlik bilan ulanishni to‘xtatish.
* `-tls1_2`: Aniq TLS 1.2 protokolidan foydalanish.
* `-brief`: Natijani qisqa va lo‘nda formatda (protokol, shifr va tekshiruv statusi) chiqarish.
* `< /dev/null`: Ulanish o‘rnatilgach darhol chiqib ketish (interaktiv rejimda qolib ketmaslik).
  > **Kutiladigan natija:** `Protocol version: TLSv1.2` va `Verification: OK`.

#### 4-bosqich: Mijoz kiritgan soxta sarlavhalarning tozalanishini sinash
```bash
curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" -H "X-Forwarded-Proto: http" \
  -H "X-Forwarded-For: 198.51.100.77" "$URL/headers"
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `-H "X-Forwarded-Proto: http"`: Mijoz tomonidan ataylab yuborilgan soxta protokol sarlavhasi.
* `-H "X-Forwarded-For: 198.51.100.77"`: Mijoz tomonidan ataylab kiritilgan soxta tashqi IP manzili.
* `$URL/headers`: Backenddagi sarlavhalarni tahlil qiluvchi endpointga so‘rov yuborish.
* **Kutiladigan natija (JSON javob):**
  ```json
  {"marker": "A9-BACKEND", "host": "a9.test:8449", "proto": "https", "client": "127.0.0.1"}
  ```
  > **Tahlil:** Mijoz kiritgan soxta IP (`198.51.100.77`) proksining `RequestHeader unset X-Forwarded-For` qoidasi tufayli o‘chirib tashlangan va haqiqiy mijoz IP si (`127.0.0.1`) qo‘yilgan. Soxta protokol (`http`) esa `RequestHeader set X-Forwarded-Proto "https"` direktivasi orqali ishonchli `https` ga almashtirilgan!

📸 **DALIL D4:** Ikki xil sertifikat xatosi (CA yo‘qligi va nom mos kelmasligi), TLS 1.2/1.3 muvaffaqiyatli ulanishi va soxta sarlavhalar tozalangan JSON javobi aks etgan skrinshot olinadi.

---

### 4.6. 6-qadam: Xavfsizlik sarlavhalari va WAF kuzatish (DetectionOnly) rejimini sinash (Dalil D5)

#### 1-bosqich: HTTP xavfsizlik sarlavhalarini 200 va 404 javoblarda tekshirish
```bash
curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" -D - -o /dev/null "$URL/"

curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" -D - -o /dev/null "$URL/missing"
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `-D -`: Server qaytargan barcha HTTP sarlavhalarini to‘g‘ridan-to‘g‘ri standart chiqishga (ekranga) chiqarish.
* `-o /dev/null`: Javob tanasini (HTML/matn) yashirish, faqat sarlavhalarni ko‘rish.
* `$URL/`: Mavjud sahifaga so‘rov (200 OK).
* `$URL/missing`: Mavjud bo‘lmagan sahifaga so‘rov (404 Not Found).
* **Kutiladigan natija:** Ikkala holatda ham (200 da ham, 404 da ham) quyidagi to‘rtta xavfsizlik sarlavhasi to‘liq mavjud bo‘lishi kerak:
  ```http
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: no-referrer
  Content-Security-Policy: default-src 'self'; frame-ancestors 'none'; object-src 'none'
  ```
  *(Bu `Header always` direktivasining to‘g‘ri ishlashini isbotlaydi).*

#### 2-bosqich: DetectionOnly rejimida WAF marker so‘rovini yuborish
```bash
curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" -i "$URL/?probe=A9-WAF-TEST&case=before"

sudo grep "1009001" /opt/a9-lab/logs/error.log
tail -n 5 ~/a9-lab/backend.log
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `curl ... "$URL/?probe=A9-WAF-TEST&case=before"`: ModSecurity qoidasiga to‘g‘ri keluvchi nazorat markerini (`probe=A9-WAF-TEST`) va sinov holatini (`case=before`) yuborish.
  - **Kutiladigan natija:** `HTTP/1.1 200 OK` va `<h1>A9-BACKEND</h1>`. (Chunki WAF hozir `DetectionOnly` rejimida!).
* `sudo grep "1009001" /opt/a9-lab/logs/error.log`: Apache xatoliklar jurnalidan qoidamiz ID si (`1009001`) bo‘yicha qidirish.
  - **Kutiladigan natija:** Jurnalda `[id "1009001"]` va `[msg "A9 marker"]` satri topiladi. WAF so‘rovni tanidi va qayd etdi!
* `tail -n 5 ~/a9-lab/backend.log`: Backend server jurnalining so‘nggi 5 qatorini ko‘rish.
  - **Kutiladigan natija:** Backend jurnalida `GET /?probe=A9-WAF-TEST&case=before HTTP/1.1 200` yozuvi paydo bo‘ladi.
  > **Xulosa:** `DetectionOnly` rejimida WAF qoidaga tushgan so‘rovni jurnalga yozadi, ammo bloklamaydi — so‘rov backendga yetib boradi va 200 OK qaytadi.

📸 **DALIL D5:** 200 va 404 sarlavhalari, DetectionOnly da olingan 200 OK javobi, `error.log` dagi 1009001 qoidasi va `backend.log` ga yetib borgan `case=before` so‘rovi aks etgan skrinshot olinadi.

---

### 4.7. 7-qadam: WAFni bloklash (On) rejimiga o‘tkazish va qayta sinov (Dalil D6)

Ushbu qadamda ModSecurity haqiqiy himoya rejimiga o‘tkaziladi.

#### 1-bosqich: Konfiguratsiyani o‘zgartirish va xizmatni qayta yuklash
```bash
sudo cp /opt/a9-lab/httpd.conf /opt/a9-lab/httpd.before.conf
sudo sed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' /opt/a9-lab/httpd.conf
sudo apache2 -t -f /opt/a9-lab/httpd.conf
sudo apache2 -f /opt/a9-lab/httpd.conf -k graceful
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `sudo cp ... httpd.before.conf`: Hozirgi ishlayotgan konfiguratsiyadan zaxira nusxa olish.
* `sudo sed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' ...`: Fayl ichidagi `SecRuleEngine DetectionOnly` satrini tezkor ravishda `SecRuleEngine On` ga almashtirish. *(Xohlasangiz `sudo nano /opt/a9-lab/httpd.conf` orqali qo‘lda tahrirlashingiz ham mumkin).*
* `sudo apache2 -t -f /opt/a9-lab/httpd.conf`: O‘zgarishdan so‘ng sintaksisni qayta tekshirish (`Syntax OK`).
* `sudo apache2 -f /opt/a9-lab/httpd.conf -k graceful`: Apache serverini to‘xtatmasdan (mavjud ulanishlarni uzmasdan) yangi konfiguratsiyani muloyim qayta yuklash (graceful restart).

#### 2-bosqich: Marker so‘rovini qayta yuborish va bloklanishni tekshirish
```bash
curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" -i "$URL/?probe=A9-WAF-TEST&case=after"

sudo grep "1009001" /opt/a9-lab/logs/error.log | tail -n 2
tail -n 8 ~/a9-lab/backend.log
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `curl ... "$URL/?probe=A9-WAF-TEST&case=after"`: Ayni marker bilan yangi sinov so‘rovini (`case=after`) yuborish.
  - **Kutiladigan natija:** **`HTTP/1.1 403 Forbidden`**! Apache mijozga qat’iy 403 xatosini qaytaradi.
* `sudo grep "1009001" ... | tail -n 2`: Xatolar jurnalining so‘nggi yozuvlarini tekshirish.
  - **Kutiladigan natija:** Jurnalda yangi yozuvda `Access denied with code 403 (phase 2)`, `[id "1009001"]` va `[msg "A9 marker"]` ko‘rinadi.
* `tail -n 8 ~/a9-lab/backend.log`: Backend server jurnalini tekshirish.
  - **Kutiladigan natija:** Backend jurnalida **`case=after` so‘rovi umuman yo‘q!** Faqat avvalgi `case=before` yozuvi turadi. Bu shuni isbotlaydiki, WAF so‘rovni Apache darajasida ushlab qoldi va backendga o‘tkazmadi!

#### 3-bosqich: Qonuniy so‘rovlarning to‘sqinliksiz ishlashini tekshirish
Xavfsizlik tizimi faqat zararli/markerli so‘rovlarni bloklashi, oddiy foydalanuvchilarning qonuniy so‘rovlariga esa xalal bermasligi shart:
```bash
curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" -i "$URL/?probe=hello&case=control"

curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" -i "$URL/"

curl --noproxy "*" --resolve a9.test:8449:127.0.0.1 \
  --cacert "$CA" -i "$URL/missing"
```
**Har bir CLI buyruq va parametrining vazifasi:**
* `curl ... "?probe=hello&case=control"`: Marker bo‘lmagan oddiy parametr yuborish. Kutiladigan natija: `HTTP/1.1 200 OK`.
* `curl ... "$URL/"`: Asosiy sahifani so‘rash. Kutiladigan natija: `HTTP/1.1 200 OK`.
* `curl ... "$URL/missing"`: Mavjud bo‘lmagan sahifani so‘rash. Kutiladigan natija: `HTTP/1.1 404 Not Found`.

📸 **DALIL D6:** WAF On rejimida marker so‘rovi 403 Forbidden bilan bloklangani, `error.log` dagi "Access denied" yozuvi, backend jurnaliga `case=after` yetib bormagani hamda qonuniy so‘rovlarning 200 OK qaytargani aks etgan skrinshot olinadi.

---

### 4.8. 8-qadam: Laboratoriya xizmatlarini xavfsiz to‘xtatish va yakunlash

Barcha sinovlar va dalillar to‘plangach, laboratoriya nusxasini to‘xtatish lozim:
```bash
sudo apache2 -f /opt/a9-lab/httpd.conf -k stop
```
* `apache2 -f ... -k stop`: Faqat bizning `/opt/a9-lab` katalogidagi laboratoriya Apache nusxasini to‘xtatadi. Tizimning umumiy xizmatlariga ziyon yetkazmaydi.
* 1-terminalga o‘tib, ishlab turgan `backend.py` jarayonini **`Ctrl + C`** tugmalarini bosish orqali to‘xtating.

---

## 5. DALILLAR (SKRINSHOTLAR) TIZIMI VA HISOBOT TALABLARI

Laboratoriya hisoboti uchun jami **6 ta asosiy dalil (D1 – D6)** skrinshot shaklida olinishi va hisobot matniga kiritilishi shart.

### 5.1. D1 – D6 dalillari bo‘yicha ko‘rsatmalar

| Dalil | Nomi va Mazmuni | Skrinshotda nimalar aniq ko‘rinishi shart? |
| :---: | :--- | :--- |
| **D1** | Muhit, versiyalar va dastlabki backend sinovi | 1. `apache2 -v`, `openssl version`, `curl --version`, `dpkg-query` buyruqlari natijasi.<br>2. 1-terminalda `python3 -u backend.py` ishga tushgani.<br>3. 2-terminalda `curl -i http://127.0.0.1:8009/` va `/headers` so‘rovlariga olingan `200 OK` javoblari. |
| **D2** | O‘quv CA, SAN va domen tekshiruvi natijalari | 1. `openssl x509 -in server.crt -noout -subject -issuer -dates` (A9 Lab Root, a9.test).<br>2. `openssl x509 ... -ext subjectAltName` (DNS:a9.test).<br>3. `openssl verify ... -verify_hostname a9.test server.crt` (`server.crt: OK`).<br>4. `openssl verify ... -verify_hostname wrong.test server.crt` (`hostname mismatch`). |
| **D3** | Apache ishga tushishi, portlar va 301 yo‘naltirish | 1. `apache2 -t` (`Syntax OK`) va `apache2 -M` (barcha 5 ta asosiy modul).<br>2. `ss -ltn` da 8009, 8089, 8449 portlarining `127.0.0.1` da faolligi.<br>3. `curl` orqali 8089 portiga so‘rovda `301 Moved Permanently` (Location: https://a9.test:8449/).<br>4. HTTPS 8449 portidan `--cacert "$CA"` bilan olingan `200 OK` javobi. |
| **D4** | Sertifikat xatolari, TLS 1.2/1.3 va soxta sarlavhalar tozalanishi | 1. CA berilmaganda `curl (60)` issuer xatosi.<br>2. Noto‘g‘ri nomda (`wrong.test`) `curl (60)` hostname mismatch xatosi.<br>3. `--tlsv1.2` va `--tlsv1.3` bilan olingan `200 OK` javoblari.<br>4. Soxta `X-Forwarded-*` sarlavhalari yuborilganda backend qaytargan JSONda `proto=https`, `client=127.0.0.1` ekanligi. |
| **D5** | Xavfsizlik sarlavhalari va WAF DetectionOnly rejimi | 1. `curl -D -` orqali 200 va 404 javoblarida to‘rtta xavfsizlik sarlavhasi mavjudligi.<br>2. `probe=A9-WAF-TEST&case=before` so‘roviga `200 OK` qaytgani.<br>3. `error.log` da `id:1009001` va `A9 marker` yozuvi.<br>4. `backend.log` ga `case=before` so‘rovi yetib borgani. |
| **D6** | WAF On bloklash rejimi va qonuniy qayta sinov | 1. `probe=A9-WAF-TEST&case=after` so‘roviga `403 Forbidden` qaytgani.<br>2. `error.log` da yangi so‘rov uchun `Access denied with code 403` va `id:1009001`.<br>3. `backend.log` da `case=after` so‘rovi YO‘QLIGI (bloklangani isboti).<br>4. `probe=hello` va `/` so‘rovlariga `200 OK`, `/missing` ga `404` qaytgani. |

### 5.2. Yakuniy natijalar taqqoslash jadvali (Hisobot uchun tayyor)

| № | Sinov amaliyoti | Kutilgan natija | Haqiqiy natija va Dalil | Xulosa |
| :---: | :--- | :--- | :--- | :--- |
| **1** | Sertifikat: `a9.test` | `server.crt: OK` | `server.crt: OK` (D2) | SAN va CA zanjiri to‘liq tasdiqlandi. |
| **2** | Sertifikat: `wrong.test` | `hostname mismatch` xatosi | `error 62: hostname mismatch` (D2) | Sertifikat begona domenlar uchun o‘tmaydi. |
| **3** | HTTP 8089 porti | `301 Moved Permanently` | `301` -> `https://a9.test:8449/` (D3) | Ochiq HTTP to‘liq HTTPSga yo‘naltirildi. |
| **4** | HTTPS 8449 + CA + to‘g‘ri nom | `200 OK`, `A9-BACKEND` | `HTTP/1.1 200 OK` (D3) | Xavfsiz TLS va proksi muvaffaqiyatli ishladi. |
| **5** | CA ko‘rsatilmaganda | `curl: (60)` issuer xatosi | `curl: (60) unable to get local issuer` (D4) | Ishonchsiz sertifikatlar bloklanadi. |
| **6** | CA bor, nom `wrong.test` | `curl: (60)` mismatch xatosi | `curl: (60) name does not match` (D4) | Brauzer/mijoz domen nomini qat’iy tekshiradi. |
| **7** | TLS 1.2 majburiy ulanish | `200 OK` | `HTTP/1.1 200 OK`, TLS 1.2 (D4) | TLS 1.2 to‘liq qo‘llab-quvvatlanadi. |
| **8** | TLS 1.3 majburiy ulanish | `200 OK` | `HTTP/1.1 200 OK`, TLS 1.3 (D4) | Zamonaviy TLS 1.3 to‘liq ishlamoqda. |
| **9** | Soxta sarlavhalar sinovi | Soxta IP o‘chiriladi | `proto=https`, `client=127.0.0.1` (D4) | Sarlavha spoofingining oldi olindi. |
| **10** | 200 / 404 / 403 javoblari | Xavfsizlik sarlavhalari mavjud | CSP, XFO, XCTO, RP to‘liq chiqdi (D5) | `Header always` barcha kodlarda ishlaydi. |
| **11** | DetectionOnly + marker | `200 OK`; log ID; backendga yetadi | `200 OK`; ID 1009001; `case=before` bor (D5) | Kuzatuv rejimida bloklash yo‘qligi isbotlandi. |
| **12** | WAF On + marker | `403 Forbidden`; backendga yetmaydi | `403 Forbidden`; `case=after` yo‘q (D6) | WAF so‘rovni to‘xtatdi, backend xavfsiz. |
| **13** | WAF On + oddiy so‘rov | `200 OK`; xizmat ishlaydi | `HTTP/1.1 200 OK` (D6) | Qonuniy foydalanuvchilar bloklanmadi. |

### 5.3. Hisobot tarkibi va xavfsizlik cheklovlari
1. **Titul varag‘i:** Fan nomi (Veb dasturlar xavfsizligi), semestr (5-semestr), laboratoriya mavzusi (A9), variant (1-variant), talabaning F.I.Sh., guruhi va topshirish sanasi.
2. **Asosiy qism:** Ishning maqsadi, foydalanilgan virtual muhit parametrlari (Ubuntu Desktop, VMware, Ubuntu Server 24.04 LTS), tizim arxitekturasi chizmasi.
3. **Dalillar bo‘limi:** D1 dan D6 gacha bo‘lgan barcha 6 ta skrinshot (har bir skrinshot tagida buyruq, vaqt va tushuntirish yozilishi shart).
4. **Natijalar jadvali:** Yuqoridagi 5.2-bo‘limdagi taqqoslash jadvali.
5. **Yakuniy xulosa:** 5–7 gapdan iborat umumlashtiruvchi tahliliy xulosa.
6. ⚠️ **XAVFSIZLIK CHEKLOVI (Qat’iy talab):**
   Hisobotga ochiq sertifikat ma’lumotlarini (`ca.crt`, `server.crt`) kiritish mumkin, ammo **yopiq maxfiy kalitlar (`ca.key`, `server.key`) hisobotga, umumiy chatlarga yoki repozitoriyga QAT’IYAN KIRITILMASLIGI SHART!**

---

## 6. NOSOZLIKLARNI ANIQLASH VA BARTARAF ETISH (TROUBLESHOOTING GUIDE)

| Muammo va Xatolik alomati | Sababi | Qadamma-qadam yechim |
| :--- | :--- | :--- |
| **`Syntax error` yoki `Invalid command`** | `httpd.conf` faylida xato yozilgan satr, noto‘g‘ri qo‘shtirnoq yoki teskari slesh (`\`). | `sudo apache2 -t -f /opt/a9-lab/httpd.conf` buyrug‘ini bering. Xatoda ko‘rsatilgan satr raqamini ochib, sintaksisni va `LoadModule` yo‘llarini tekshiring. |
| **`Cannot find certificate or key file`** | Sertifikat yoki maxfiy kalit ko‘rsatilgan yo‘lda mavjud emas. | `/opt/a9-lab/tls/` katalogida `server.crt` va `server.key` borligini tekshiring: `ls -la /opt/a9-lab/tls/`. 3-qadamdagi `sudo install` buyruqlarini qaytadan bajaring. |
| **`curl: (60) SSL certificate problem`** | CA ko‘rsatilmagan, SAN noto‘g‘ri yoki tizim soati orqada qolgan. | `curl` buyrug‘ida `--cacert "$HOME/a9-ca/ca.crt"` ko‘rsatilganini tekshiring. Muammoni `-k` bilan yashirmang! `openssl verify` orqali sertifikat muddatini tekshiring. |
| **`Connection refused`** | Apache yoki Python backend ishga tushmagan, portlar band. | `ss -ltn` orqali 8009, 8089, 8449 portlarini ko‘ring. 1-terminalda `backend.py` ishlab turganiga ishonch hosil qiling. Apache ni `-k start` bilan qayta yoqing. |
| **`502 Bad Gateway` yoki `503 Service Unavailable`** | Apache ishlayapti, lekin orqadagi Python backendga ulana olmayapti. | Python backend (`http://127.0.0.1:8009`) to‘xtab qolgan. 1-terminalni tekshiring. `curl -i http://127.0.0.1:8009/` orqali backend tirikligini tasdiqlang. |
| **WAF `SecRuleEngine On` bo‘lsa ham markerga `200 OK` qaytmoqda** | Apache yangi konfiguratsiyani yuklamagan yoki boshqa fayl tahrirlangan. | `/opt/a9-lab/httpd.conf` faylida `SecRuleEngine On` yozilganini tekshiring. `sudo apache2 -f /opt/a9-lab/httpd.conf -k graceful` ni qayta bajaring. |
| **Jurnalda ID 1009001 bor, ammo status `200 OK`** | WAF hali ham `DetectionOnly` rejimida qolgan. | 7-qadamga qarang. `sed` yoki `nano` orqali `SecRuleEngine On` qiling va `graceful` bering. Eski log yozuvlarini yangisidan vaqt bo‘yicha ajrating. |
| **`AH01882: Init: this version of mod_ssl only compiles a single global SSLSessionCache`** | SSL sessiya keshining minimal konfiguratsiyada yo‘qligi haqidagi ogohlantirish. | Bu xatolik emas, shunchaki xabarnoma (warning). U Apache ishlashiga to‘sqinlik qilmaydi; e’tiborsiz qoldirish mumkin. |

---

## 7. NAZORAT SAVOLLARI VA ULARNING TO‘LIQ ILMIY-AMALIY JAVOBLARI

### 1-savol (8): CAga ishonish va sertifikat nomi mosligi nega alohida tekshiriladi?
**To‘liq ilmiy-amaliy javob:**
Chunki bu ikki parametr PKI (Public Key Infrastructure) xavfsizlik modelining ikki xil, bir-biriga bog‘liq bo‘lmagan mustaqil tekshiruv qatlamidir:
1. **Ishonch zanjiri (Chain of Trust):** Sertifikatning haqiqiyligini va uni kim berganini tekshiradi. Agar sertifikat ishonchli CA tomonidan imzolangan bo‘lsa, mijoz ushbu sertifikat va uning ochiq kaliti qonuniy ekaniga ishonadi.
2. **Domen mosligi (Hostname Verification / SAN):** Sertifikat aynan mijoz murojaat qilayotgan serverga tegishli ekanini tasdiqlaydi.
* **Xavf misoli:** Tajovuzkor o‘zining `attacker.com` domeni uchun dunyodagi eng nufuzli CA (masalan, Let's Encrypt yoki DigiCert) orqali 100% qonuniy sertifikat olishi mumkin. Agar mijoz faqat "CA imzolaganmi?" deb tekshirib, domen nomini tekshirmasa, tajovuzkor Man-in-the-Middle (MitM) orqali `bank.uz` trafigini o‘ziga burib olib, o‘zining qonuniy `attacker.com` sertifikatini taqdim etadi va shifrlangan ma’lumotlarni tutib oladi. Shu sababli ikkala shart ham (Ishonchli CA + Domen nomi mosligi) birgalikda tekshirilishi shart.

### 2-savol (9): TLS 1.2 ning ishlashi TLS 1.0 o‘chirilganini o‘zi isbotlaydimi?
**To‘liq ilmiy-amaliy javob:**
**Yo‘q, mutlaqo isbotlamaydi!**
TLS mijoz va server o‘rtasidagi ulanish bosqichida (Handshake) tomonlar qo‘llab-quvvatlaydigan eng yuqori umumiy protokol versiyasini tanlaydi (Cipher/Protocol Negotiation). Agar serverda TLS 1.0, TLS 1.1 va TLS 1.2 bir vaqtda yoqilgan bo‘lsa, zamonaviy `curl` mijozi tabiiy ravishda TLS 1.2 orqali ulanadi va 200 OK oladi.
Biroq, agar tajovuzkor tarmoqda so‘rovlarni o‘zgartirsa (Downgrade Attack — masalan, POODLE hujumi), mijozni server bilan eski va zaif TLS 1.0 orqali ulanishga majburlashi mumkin.
TLS 1.0 haqiqatdan ham o‘chirilganini isbotlash uchun:
- Server konfiguratsiyasida `SSLProtocol -all +TLSv1.2 +TLSv1.3` direktivasi borligini ko‘rsatish;
- Mijozdan ataylab TLS 1.0 orqali ulanish so‘rovini yuborib (`openssl s_client -tls1` yoki `curl --tlsv1.0 --tls-max 1.0`), server ulanishni darhol uzganini (`protocol version alert` yoki handshake failure) amalda qayd etish talab etiladi.

### 3-savol (10): DetectionOnly va On orasidagi farq qaysi uch dalil bilan ko‘rsatildi?
**To‘liq ilmiy-amaliy javob:**
Ushbu farq laboratoriyada aynan bir xil qoida (`id:1009001`) va bir xil marker (`probe=A9-WAF-TEST`) yuborilganda quyidagi **uchta aniq dalil** orqali isbotlandi:
1. **HTTP status kodi:**
   - `DetectionOnly` rejimida mijozga **`200 OK`** qaytdi;
   - `On` rejimida esa so‘rov bloklanib, mijozga **`403 Forbidden`** qaytdi.
2. **Backend jurnali (`backend.log`):**
   - `DetectionOnly` rejimida `case=before` so‘rovi backend serverga to‘siqsiz yetib bordi va `backend.log` da qayd etildi;
   - `On` rejimida esa `case=after` so‘rovi backendga UMUMAN YETIB BORMAY, Apache darajasida to‘xtatildi (`backend.log` da yozuv paydo bo‘lmadi).
3. **Apache xatoliklar jurnali (`error.log`):**
   - `DetectionOnly` rejimida jurnalda moslik qayd etildi (`id "1009001"`), ammo u ogohlantirish sifatida yozildi;
   - `On` rejimida esa jurnalda aniq **`Access denied with code 403 (phase 2)`** yozuvi qayd etildi.

### 4-savol (11): Header always nega error javoblari uchun muhim?
**To‘liq ilmiy-amaliy javob:**
Apache veb-serverida `mod_headers` moduli ikkita ichki jadval bilan ishlaydi: `headers_out` (oddiy muvaffaqiyatli javoblar jadvali) va `err_headers_out` (xatoliklar jadvali).
- Standart `Header set` direktivasi sarlavhalarni faqat `headers_out` jadvaliga yozadi. Bu jadval faqat muvaffaqiyatli status kodlarida (`2xx`, masalan 200 OK, va ayrim `3xx`) mijozga jo‘natiladi.
- Agar server xatolik qaytarsa (masalan, 400 Bad Request, 403 Forbidden, 404 Not Found, 500 Internal Error), Apache faqat `err_headers_out` jadvalidagi sarlavhalarni yuboradi va oddiy `Header set` orqali berilgan sarlavhalar tushib qoladi!
- **`Header always set`** direktivasi sarlavhani `err_headers_out` jadvaliga joylashtiradi. Natijada so‘rov WAF tomonidan 403 bilan bloklanganda yoki 404 xatosi yuz berganda ham xavfsizlik sarlavhalari (`Content-Security-Policy`, `X-Frame-Options` va h.k.) mijoz brauzeriga majburiy jo‘natiladi. Bu esa xatolik sahifalarining o‘zida yuzaga kelishi mumkin bo‘lgan XSS yoki Clickjacking hujumlarining oldini oladi.

### 5-savol (12): Backendga bevosita kirish ochiq bo‘lsa WAF himoyasining chegarasi qanday?
**To‘liq ilmiy-amaliy javob:**
WAF faqat o‘zi orqali o‘tgan trafikni tekshiradi. Agar orqadagi backend xizmati (`http://127.0.0.1:8009`) tarmoqdagi boshqa mashinalar uchun ochiq bo‘lsa yoki ayni shu serverdagi boshqa lokal jarayonlar unga to‘g‘ridan-to‘g‘ri murojaat qila olsa:
- Tajovuzkor Apache proksisini (8449 portini) butunlay chetlab o‘tib (WAF Bypass), bevosita backendning 8009 portiga so‘rov yuboradi.
- Natijada ModSecurity WAF ushbu so‘rovni umuman ko‘rmaydi, hech qanday qoida ishga tushmaydi, log yozilmaydi va hujum to‘siqsiz amalga oshadi.
- **Xulosa:** WAF mustaqil va yetarli himoya vositasi emas. U har doim qat’iy tarmoq segmentatsiyasi (Firewall, iptables), backendni faqat loopbackka bog‘lash hamda mTLS (Mutual TLS) kabi himoya choralari bilan birgalikda qo‘llanilishi shart.

### 6-savol (13): Marker qoidasidan to‘liq SQLi/XSS himoyasi haqida xulosa chiqarish nega noto‘g‘ri?
**To‘liq ilmiy-amaliy javob:**
Chunki bizning laboratoriyadagi o‘quv qoidasi:
```apache
SecRule ARGS:probe "@streq A9-WAF-TEST" "deny,status:403"
```
faqat va faqat bitta aniq parametr (`probe`) va bitta statik matnni (`A9-WAF-TEST`) tekshiradi.
1. **Qamrovning cheklanganligi:** Ushbu qoida SQL inyeksiya sintaksisini (`' OR '1'='1`, `UNION SELECT`), XSS teglari va hodisalarini (`<script>`, `onerror=alert()`), BOLA manipulyatsiyalarini yoki boshqa URL parametrlarini mutlaqo tekshirmaydi.
2. **Aylanib o‘tish (Obfuscation):** Haqiqiy hujumchilar har xil kodlash (URL encoding, double encoding, Unicode, SQL commentlar) usullaridan foydalanadi. Bitta oddiy `@streq` qoidasi bunday murakkab hujumlarni taniy olmaydi.
3. **OWASP CRS zarurati:** Haqiqiy veb-ilovani himoya qilish uchun yuzlab murakkab muntazam ifodalar (RegEx) va anomaliyalarni hisoblash balli tizimiga (Anomaly Scoring) ega bo‘lgan to‘liq **OWASP ModSecurity Core Rule Set (CRS)** to‘plami talab etiladi. Bitta marker qoidasi faqat WAF mexanizmi ishlayotganini isbotlovchi namoyish vositasidir, xolos.

---

## 8. BAHOLASH MEZONLARI (10 BALLIK TIZIM)

| Bo‘lim | Baholanadigan komponentlar va talablar | Ball |
| :---: | :--- | :---: |
| **1** | **Muhit, backend va arxitektura:** VM sozlamalari, paketlar versiyasi, backend ishga tushishi va D1 dalili. | **1 ball** |
| **2** | **CA, SAN, sertifikat zanjiri va nom sinovlari:** Root CA, server.crt, SAN (DNS:a9.test), openssl verify natijalari va D2 dalili. | **2 ball** |
| **3** | **TLS, yo‘naltirish va proksi sarlavhalari:** 8089 dan 301 yo‘naltirish, TLS 1.2/1.3 muvaffaqiyati, soxta sarlavhalar tozalanishi va D3, D4 dalillari. | **2 ball** |
| **4** | **Xavfsizlik sarlavhalari:** 200, 404 va 403 javoblarida to‘rtta xavfsizlik sarlavhasining to‘liq chiqishi (`Header always`) va D5 ning 1-qismi. | **1 ball** |
| **5** | **WAF rejimlari, ID, backend va qonuniy qayta sinov:** `DetectionOnly` da 200 va log ID; `On` rejimida 403, ID 1009001, backendga yetmagan so‘rov va qonuniy so‘rovlarning ishlashi (D5, D6 dalillari). | **3 ball** |
| **6** | **Hisobot sifati va nazorat savollariga javob:** To‘ldirilgan natijalar jadvali, xulosa, xavfsizlik talablariga rioya qilingani va 6 ta nazorat savoliga ilmiy javoblar. | **1 ball** |
| **JAMI** | **A9 Amaliy mashg‘ulot bo‘yicha maksimal ball** | **10 ball** |

---

## 9. QO‘SHIMCHA TAHLIL: APACHE VS NGINX VS IIS ARXITEKTURASI

Qo‘llanmaning qo‘shimcha topshirig‘i talabiga binoan, ushbu A9 arxitekturasining boshqa mashhur veb-serverlarda (Nginx va Microsoft IIS) qanday amalga oshirilishi bo‘yicha amaliy qiyosiy tahlil:

| Funksional qatlam | Apache HTTP Server 2.4 | Nginx (Engine-X) | Microsoft IIS (Internet Information Services) |
| :--- | :--- | :--- | :--- |
| **TLS/HTTPS sozlamalari** | `mod_ssl`<br>`SSLEngine On`<br>`SSLCertificateFile ...`<br>`SSLProtocol -all +TLSv1.2 +TLSv1.3` | `ssl_certificate ...;`<br>`ssl_certificate_key ...;`<br>`ssl_protocols TLSv1.2 TLSv1.3;` | IIS Manager -> Server Certificates (Schannel). TLS 1.2/1.3 Windows Registry (SCHANNEL kalitlari) orqali boshqariladi. |
| **Teskari Proksi (Reverse Proxy)** | `mod_proxy`, `mod_proxy_http`<br>`ProxyPass / http://127.0.0.1:8009/`<br>`ProxyPassReverse / ...` | `ngx_http_proxy_module`<br>`proxy_pass http://127.0.0.1:8009;`<br>`proxy_set_header Host $host;` | Application Request Routing (ARR) va URL Rewrite modullari orqali Reverse Proxy qoidalari tuziladi. |
| **Proksi sarlavhalarini boshqarish** | `RequestHeader unset X-Forwarded-For`<br>`RequestHeader set X-Forwarded-Proto "https"` | `proxy_set_header X-Forwarded-For $remote_addr;`<br>`proxy_set_header X-Forwarded-Proto $scheme;` | URL Rewrite moduli orqali Server Variables (`HTTP_X_FORWARDED_PROTO`) sozlanadi. |
| **Xavfsizlik sarlavhalari** | `mod_headers`<br>`Header always set X-Frame-Options "DENY"` | `add_header X-Frame-Options "DENY" always;`<br>`add_header Content-Security-Policy ... always;` | `web.config` faylidagi `<system.webServer><httpProtocol><customHeaders>` bo‘limida belgilanadi. |
| **WAF integratsiyasi** | `mod_security2` (libapache2-mod-security2). To‘g‘ridan-to‘g‘ri Apache moduli sifatida yuklanadi. | `ModSecurity-nginx` konnektori (libmodsecurity3 / Coraza WAF) orqali dinamik modul sifatida ulanadi. | IIS uchun ModSecurity MSI o‘rnatuvchisi yoki Azure Application Gateway WAF xizmati ishlatiladi. |

---

## 10. FOYDALANILGAN VA TAVSIYA ETILADIGAN RASMIY MANBALAR

1. **Apache HTTP Server Documentation — Module mod_ssl:**
   - Rasmiy manzil: https://httpd.apache.org/docs/2.4/mod/mod_ssl.html
   - Mazmuni: TLS sertifikatlarini ulash, `SSLEngine`, `SSLCertificateFile` va `SSLProtocol` direktivalari orqali shifrlash kanallarini boshqarish.
2. **cURL Documentation — SSL CA Certificates & Name Resolution:**
   - Rasmiy manzil: https://curl.se/docs/sslcerts.html | https://curl.se/docs/manpage.html
   - Mazmuni: `--cacert`, `--resolve`, `--noproxy` bayroqlarining ishlash mexanizmi va SSL xatolik kodlari (`curl: (60)`).
3. **Apache HTTP Server Documentation — Module mod_proxy & mod_proxy_http:**
   - Rasmiy manzil: https://httpd.apache.org/docs/2.4/mod/mod_proxy.html
   - Mazmuni: `ProxyRequests Off`, `ProxyPass`, `ProxyPassReverse` va `ProxyPreserveHost` parametrlarining teskari proksidagi vazifasi.
4. **ModSecurity v2 Reference Manual (OWASP):**
   - Rasmiy manzil: https://github.com/owasp-modsecurity/ModSecurity/wiki/Reference-Manual-(v2.x)
   - Mazmuni: `SecRuleEngine` (`DetectionOnly` vs `On`), qoida sintaksisi, o‘zgaruvchilar (`ARGS`), operatorlar (`@streq`), fazalar (`phase:2`) va amallar (`deny`, `status:403`).
5. **OWASP Secure Headers Project & Cheat Sheet Series:**
   - Rasmiy manzil: https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
   - Mazmuni: `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` sarlavhalarining zamonaviy xavfsizlik standartlari.
6. **OpenSSL Cryptography and SSL/TLS Toolkit (OpenSSL 3.0 Documentation):**
   - Rasmiy manzil: https://www.openssl.org/docs/man3.0/man1/openssl-req.html
   - Mazmuni: RSA kalitlar juftligi, X.509 v3 sertifikatlari, CSR shakllantirish, SAN kengaytmasi va `openssl verify` diagnostikasi.
7. **Apache HTTP Server Documentation — Module mod_headers:**
   - Rasmiy manzil: https://httpd.apache.org/docs/2.4/mod/mod_headers.html
   - Mazmuni: `Header always set` direktivasining xatolik (`4xx`, `5xx`) javoblarida ishlash xususiyati va `RequestHeader unset`.
8. **IETF RFC 6797 — HTTP Strict Transport Security (HSTS):**
   - Rasmiy manzil: https://datatracker.ietf.org/doc/html/rfc6797#section-8.3
   - Mazmuni: HSTS ning port xaritalash cheklovlari va nima uchun nostandart portlarda (8089/8449) HSTS qo‘llanilmasligi.
9. **IETF RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3:**
   - Rasmiy manzil: https://datatracker.ietf.org/doc/html/rfc8446
   - Mazmuni: 0-RTT, zaif algoritmlarning olib tashlanishi va 1-roundtrip handshake arxitekturasi.
10. **OWASP Top 10:2021 — A05:2021 Security Misconfiguration:**
    - Rasmiy manzil: https://owasp.org/Top10/A05_2021-Security_Misconfiguration/
    - Mazmuni: Veb-serverlar, xavfsizlik sarlavhalari va standart sozlamalardagi zaifliklar tahlili.

---

## 11. ILOVALAR (TO‘LIQ DASTURIY KODLAR)

### 11.1. 1-ilova: `backend.py`
Fayl joylashuvi: `~/a9-lab/backend.py`
*(Python 3 standart kutubxonasidagi HTTP server kodi. Qo‘shimcha `pip` paketlari talab qilinmaydi).*

```python
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

class App(BaseHTTPRequestHandler):
    def do_GET(self):
        # Kelgan URI yo'lidan sof manzilni ajratib olish
        path = urlsplit(self.path).path
        status, mime = 200, 'text/html; charset=utf-8'
        
        if path == '/headers':
            # Proksi uzatgan sarlavhalarni JSON formatida qaytarish
            mime = 'application/json'
            body = json.dumps({
                'marker': 'A9-BACKEND',
                'host': self.headers.get('Host'),
                'proto': self.headers.get('X-Forwarded-Proto'),
                'client': self.headers.get('X-Forwarded-For'),
            }).encode()
        elif path == '/':
            # Asosiy sahifa: A9-BACKEND markerini o'z ichiga olgan HTML
            body = b'<!doctype html><title>A9</title><h1>A9-BACKEND</h1>'
        else:
            # Mavjud bo'lmagan yo'llar uchun 404 javobi
            status, mime, body = 404, 'text/plain', b'A9-NOT-FOUND'
            
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    # Faqat 127.0.0.1 (loopback) interfeysida va 8009-portda tinglash
    print('A9 backend: http://127.0.0.1:8009', flush=True)
    HTTPServer(('127.0.0.1', 8009), App).serve_forever()
```

---

### 11.2. 2-ilova: `httpd.conf`
Fayl joylashuvi: `/opt/a9-lab/httpd.conf`
*(A va B qismlari ketma-ket to‘liq birlashtirilgan Apache va ModSecurity konfiguratsiyasi).*

```apache
# ==============================================================================
# VEB DASTURLAR XAVFSIZLIGI — A9 LABORATORIYA ISHI (1-VARIANT)
# ALOHIDA APACHE NUSXASI UCHUN ASOSIY KONFIGURATSIYA FAYLI
# ==============================================================================

# 1. Asosiy kataloglar va jarayon parametrlari
ServerRoot "/opt/a9-lab"
DefaultRuntimeDir "/opt/a9-lab/run"
PidFile "/opt/a9-lab/run/httpd.pid"
ServerName a9.test

# 2. Tinglovchi portlar (Faqat loopback 127.0.0.1 da)
Listen 127.0.0.1:8089
Listen 127.0.0.1:8449

# 3. Zaruriy Apache modullarini yuklash
LoadModule mpm_event_module /usr/lib/apache2/modules/mod_mpm_event.so
LoadModule authz_core_module /usr/lib/apache2/modules/mod_authz_core.so
LoadModule authz_host_module /usr/lib/apache2/modules/mod_authz_host.so
LoadModule alias_module /usr/lib/apache2/modules/mod_alias.so
LoadModule ssl_module /usr/lib/apache2/modules/mod_ssl.so
LoadModule headers_module /usr/lib/apache2/modules/mod_headers.so
LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so
LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so
LoadModule unique_id_module /usr/lib/apache2/modules/mod_unique_id.so
LoadModule security2_module /usr/lib/apache2/modules/mod_security2.so

# 4. Xizmat foydalanuvchisi va guruhi
User www-data
Group www-data

# 5. Xavfsiz server konfiguratsiyasi va axborot sizib chiqishini to'xtatish
ServerTokens Prod
ServerSignature Off
TraceEnable Off
ProxyRequests Off

# 6. Jurnallar (Logs) konfiguratsiyasi
ErrorLog "/opt/a9-lab/logs/error.log"
LogLevel warn
LogFormat "%h %t \"%r\" %>s %b" a9
CustomLog "/opt/a9-lab/logs/access.log" a9

# 7. Global ruxsatlar nazorati (Faqat backend proksisiga ruxsat)
<Directory />
    Require all denied
</Directory>

<Proxy "http://127.0.0.1:8009/">
    Require all granted
</Proxy>

# 8. HTTP VirtualHost (Port 8089): Barcha so'rovlarni HTTPS ga yo'naltirish
<VirtualHost 127.0.0.1:8089>
    ServerName a9.test
    Redirect permanent / https://a9.test:8449/
</VirtualHost>

# 9. HTTPS VirtualHost (Port 8449): TLS + WAF + Reverse Proxy + Security Headers
<VirtualHost 127.0.0.1:8449>
    ServerName a9.test
    
    # --- TLS / SSL Konfiguratsiyasi ---
    SSLEngine On
    SSLCertificateFile "/opt/a9-lab/tls/server.crt"
    SSLCertificateKeyFile "/opt/a9-lab/tls/server.key"
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    
    # --- Teskari Proksi va Sarlavhalarni xavfsiz boshqarish ---
    ProxyPreserveHost On
    RequestHeader unset X-Forwarded-For
    RequestHeader set X-Forwarded-Proto "https"
    ProxyPass / http://127.0.0.1:8009/ connectiontimeout=3 timeout=5
    ProxyPassReverse / http://127.0.0.1:8009/
    
    # --- HTTP Xavfsizlik sarlavhalari (Har doim, hatto xato kodlarida ham) ---
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "DENY"
    Header always set Referrer-Policy "no-referrer"
    Header always set Content-Security-Policy \
        "default-src 'self'; frame-ancestors 'none'; object-src 'none'"
        
    # --- ModSecurity WAF Konfiguratsiyasi ---
    # Dastlab DetectionOnly holatida sinovdan o'tkaziladi.
    # 7-bosqichda ushbu satr "SecRuleEngine On" qilib o'zgartiriladi!
    SecRuleEngine DetectionOnly
    
    SecRequestBodyAccess On
    SecAuditEngine RelevantOnly
    SecAuditLogType Serial
    SecAuditLogParts ABFHZ
    SecAuditLog "/opt/a9-lab/logs/audit.log"
    
    # O'quv nazorat qoidasi (A9 markerini tekshirish)
    SecRule ARGS:probe "@streq A9-WAF-TEST" \
        "id:1009001,phase:2,t:none,deny,status:403,log,auditlog,msg:'A9 marker'"
</VirtualHost>
```
