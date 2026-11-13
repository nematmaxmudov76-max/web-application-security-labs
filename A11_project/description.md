# VEB DASTURLAR XAVFSIZLIGI — A11-LABORATORIYA ISHI (1-VARIANT)
## Mavzu: Botlardan himoyalanish, monitoring va xavfsiz ekspluatatsiya
### Variant: Login urinishlarini cheklash va xavfsizlik hodisalarini aniqlash (Rate Limiting & Incident Detection)

---

## 📌 MAXSUS MUHIT VA ISH SHAROITI ESLATMASI (O'QING!)

Ushbu qo'llanma sizning aniq ish muhitingiz va tarmoq sharoitingizga to'liq moslashtirilgan:

1. **Lokal Wi-Fi tarmog'i (Universitet tarmog'i emas):**
   * Laboratoriyadagi barcha xizmatlar (`app.py`, `monitor.py`, `curl`) tashqi internetga bog'liq bo'lmagan holda, to'liq lokal **loopback (`127.0.0.1:8011`)** manzilida ishlaydi.
   * Universitet Wi-Fi tarmog'idagi cheklovlar, proksi (proxy) yoki xavfsizlik filtrlari sizga xalaqit bermaydi.
   * Buyruqlarda berilgan `--noproxy "*"` kaliti `curl` dasturini tizimda oldindan qolgan bo'lishi mumkin bo'lgan har qanday proksi sozlamalarini chetlab o'tib, to'g'ridan-to'g'ri `127.0.0.1` ga ulanishini kafolatlaydi.
   * VMware'dagi virtual mashinaga (Ubuntu Server) faqat dastlabki paketlarni (`apt update`, `apt install python3 curl nano`) o'rnatish uchun lokal Wi-Fi orqali internet kerak bo'ladi (buning uchun VMware tarmoq adapterini **NAT** rejimida qoldirish kifoya).

2. **Operatsion tizim: Ubuntu (Xost) -> VMware Workstation -> Ubuntu Server (VM):**
   * Asosiy kompyuteringiz (Xost) — **Ubuntu**.
   * Virtualizatsiya — **VMware** vositasida ishlaydi.
   * Barcha laboratoriya amallari VMware ichidagi **Ubuntu Server** (yoki Ubuntu Desktop) terminalida bajariladi. Windows buyruqlari (PowerShell/CMD) ishlatilmaydi; barcha ko'rsatmalar toza **Linux/Bash** muhitiga mo'ljallangan.
   * Laboratoriya davomida parallel ravishda **2 ta terminal seansi** kerak bo'ladi (1-terminalda server ishlaydi, 2-terminalda test buyruqlari yuboriladi). Buni Ubuntu xostidan VM ga 2 ta SSH seans ochish orqali, yoki VM ichida `tmux` (terminal multiplexer) vositasida ekranni ikkiga bo'lish orqali bajarishingiz mumkin.

3. **Windows 11 VM masalasi:**
   * PDF qo'llanmaning 1-sahifasidagi jadvalda ko'rsatilgan "Windows 11" — bu universitet kompyuter sinfidagi jismoniy kompyuterlarning texnik ko'rsatkichidir.
   * Ushbu laboratoriya (A11, 1-variant) uchun Windows 11 umuman **shart emas**! Hamma narsa (Python 3, curl, bash skriptlari, loglar, SHA-256 xeshlash) to'liq Linux terminalida kechadi.
   * Siz tayyorlab qo'ygan Windows 11 VM'dan faqat ixtiyoriy ravishda mijoz sifatida so'rov yuborishda foydalanish mumkin, ammo bu holatda `app.py` dagi manzilni `0.0.0.0` ga o'zgartirish talab etiladi. Laboratoriya sharti va baholash mezonlari (jurnalda `ip: 127.0.0.1` bo'lishi) bo'yicha eng to'g'ri va xatosiz yo'l — barcha jarayonni bitta **Ubuntu Server VM** ichida loopback orqali bajarishdir.

---

# 1-BO'LIM. MAVZUNING MAQSADI VA AMALIY AHAMIYATI

### 1.1. Laboratoriya mashg'ulotining asosiy maqsadi
Mazkur amaliy ishning bosh maqsadi — zamonaviy veb-ilovalarda uchraydigan avtomatlashtirilgan bot hujumlariga (Brute-force, Credential Stuffing, Password Spraying) qarshi himoya mexanizmlarini yaratish, tadbiq etish, ularning samaradorligini monitoring va xavfsizlik jurnallari (security logs) orqali tekshirish hamda xavfsizlik insidentlariga to'g'ri javob berish (Incident Response) ko'nikmalarini shakllantirishdir.

### 1.2. Hal etiladigan amaliy vazifalar:
1. **Hujum vektorlarini lokal modellashtirish:** Avtomatlashtirilgan skriptlar (curl, bash tsikllari) yordamida login tizimiga ketma-ket to'g'ri va noto'g'ri so'rovlar yuborib, cheklov o'rnatilmagan tizim qanday zaiflikka uchrashini ko'rish.
2. **Ko'p qatlamli Rate Limiting (Tezlikni cheklash) joriy etish:** So'rovlarni nafaqat IP-manzil bo'yicha, balki foydalanuvchi akkaunti (username) bo'yicha ham mustaqil nazorat qiluvchi sirg'aluvchi oyna (sliding window) algoritmini yoqish.
3. **Standartlashtirilgan HTTP javob kodlarini tatbiq etish:** 
   * `200 OK` — Muvaffaqiyatli autentifikatsiya.
   * `401 Unauthorized` — Noto'g'ri login yoki parol.
   * `429 Too Many Requests` — Belgilangan vaqt oralig'ida limitdan oshib ketgan so'rovlar (RFC 6585).
   * `Retry-After` sarlavhasi (header) orqali mijozga cheklov qachon tugashini aniq soniyalarda bildirish.
4. **Mijoz aldovlariga (IP Spoofing) uchramaslik:** Mijoz tomonidan soxtalashtirib yuborilishi mumkin bo'lgan `X-Forwarded-For` kabi HTTP sarlavhalariga ko'r-ko'rona ishonmasdan, himoya mantiqini haqiqiy TCP ulanish rozetkasi (socket peer address) ga tayanishini tahlil qilish.
5. **Xavfsiz va maxfiylikka mos jurnallashtirish (OWASP Logging):** Har bir hodisani `events.jsonl` (JSON Lines) formatida qayd etish, har bir so'rovga unikal `request_id` (UUID4) biriktirish va eng muhimi — **parol, maxfiy token yoki so'rov tanasini aslo jurnalga yozmaslik**.
6. **Xavfsizlik monitoringi va Anomaliyalarni aniqlash:** `monitor.py` tahlil vositasi yordamida jurnaldan `FAIL_BURST` (parolni ommaviy topishga urinish) va `LIMIT_BURST` (faol limitga qaramay botning hujumni davom ettirishi) qoidalarini aniqlash.
7. **Qonuniy foydalanuvchi tiklanishini (Account Recovery) kafolatlash:** 30 soniyalik oyna o'tgach, haqiqiy foydalanuvchining hisobi doimiy bloklanib qolmasdan, xizmatdan yana emin-erkin foydalana olishini (`sleep 31` dan keyin `200 OK`) isbotlash.
8. **Raqamli dalillarni saqlash va tizim yaxlitligi (Digital Forensics & Integrity):** Hodisa sodir bo'lganda konfiguratsiyalar va jurnal fayllarini arxivlash, ularning SHA-256 xesh summalarini hisoblab, dalillarning soxtalashtirilmaganini (`sha256sum -c`) tekshirish.

---

# 2-BO'LIM. NAZARIY VA ARXITEKTURAVIY TO'LIQ QO'LLANMA

Ushbu bo'limda dastur kodi va laboratoriya jarayonida qo'llanilgan har bir tushuncha, xavfsizlik tamoyili va arxitektura komponenti chuqur tahlil qilinadi.

### 2.1. Hujum turlari: Farqlar va tushunchalar

| Hujum turi | Hujum mexanizmi | Tizimdagi belgilari | Asosiy xavf |
| :--- | :--- | :--- | :--- |
| **Brute Force (Qo'pol kuch)** | Bitta aniq akkauntga (masalan, `alice`) lug'atdagi minglab turli xil parollarni ketma-ket sinab ko'rish. | Bitta `user` ga bitta yoki bir nechta IPdan juda ko'p `401 login_failed` so'rovlarining kelishi. | Kuchli bo'lmagan parollar tezda fosh bo'ladi. |
| **Password Spraying (Parol sepish)** | Ommabop bitta parolni (masalan, `Winter2026!`) tizimdagi yuzlab turli foydalanuvchilar (`user1`, `user2`, ...) ustida bir martadan sinash. | Ko'plab turli `user`larga bitta manba IPdan kam sonli (har biriga 1 tadan) muvaffaqiyatsiz urinishlar. | Akkaunt darajasidagi cheklovni chetlab o'tadi (chunki har bir akkaunt 1 martagina uriniladi). |
| **Credential Stuffing** | Boshqa tashqi platformalardan sizib chiqqan (leak qilingan) login-parol juftliklarini ushbu tizimda avtomatik tekshirib ko'rish. | Turli foydalanuvchi nomlari va parollarning yuqori tezlikda sinab ko'rilishi. | Foydalanuvchilar turli saytlarda bir xil parol ishlatgan bo'lsa, akkauntlar ommaviy egallanadi. |
| **DDoS / HTTP Flood** | Server resurslarini (CPU, xotira, ulanishlar puli) tugatish maqsadida soniyasiga minglab so'rovlar yuborish. | Server javob vaqtining keskin oshishi, ulanishlarning uzilishi (`504 Gateway Timeout` yoki server qulashi). | Xizmat ko'rsatish butunlay to'xtaydi. |

### 2.2. Gibrid Rate Limiting (IP + Akkaunt) Mantiqi

Nima uchun faqat IP bo'yicha yoki faqat Akkaunt bo'yicha limit yetarli emas?

1. **Faqat IP bo'yicha limit qo'yilsa:**
   * *Kamchilik 1 (NAT muammosi):* Bitta korxona, universitet yoki mobil operator tarmog'idagi yuzlab qonuniy xodimlar bitta umumiy tashqi IP-manzil orqali internetga chiqadi. Agar bitta xodim parolini bir necha bor adashtirsa, butun korxona tizimdan bloklanib qolishi mumkin.
   * *Kamchilik 2 (Botnet / Proxy muammosi):* Tajovuzkor taqsimlangan botnet yoki aylanma proksi (proxy rotation) orqali har bir so'rovni yangi IPdan yuborsa, IP limiti umuman ishlamay qoladi.
2. **Faqat Akkaunt (Username) bo'yicha limit qo'yilsa:**
   * *Kamchilik 1 (Denial of Service - DoS):* Tajovuzkor o'zi bilgan begunoh foydalanuvchining loginiga ataylab 3 marta xato parol yuborib, uning akkauntini to'sib qo'yishi va qonuniy egasini tizimga kiritmay qo'yishi mumkin.
   * *Kamchilik 2 (Password Spraying):* Tajovuzkor bitta IPdan har bir foydalanuvchiga 1 martadan parol sinasa, hech qaysi akkaunt limitga yetmaydi va hujum sezilmay qolaveradi.
3. **Bizning modelimizdagi Gibrid yechim:**
   * **Akkaunt limiti:** 30 soniyalik sirg'aluvchi oynada bitta akkauntga ko'pi bilan **3 ta** tekshiruv.
   * **IP limiti:** 30 soniyalik sirg'aluvchi oynada bitta IPga ko'pi bilan **8 ta** tekshiruv.
   * So'rov faqat har ikkala shart ham bajarilgandagina parolni tekshirish bosqichiga o'tkaziladi!

### 2.3. Sirg'aluvchi oyna (Sliding Window) Algoritmi

Qat'iy oyna (Fixed Window) vaqtni qat'iy bloklarga bo'ladi (masalan, 12:00:00 dan 12:00:30 gacha). Tajovuzkor 12:00:29 da 3 ta so'rov, 12:00:31 da yana 3 ta so'rov yuborib, 2 soniya ichida 6 ta so'rov o'tkaza oladi (Traffic Burst).

Bizning tizimimizda qo'llanilgan **Sirg'aluvchi oyna (Sliding Window)** mantiqi:
* Har bir ruxsat etilgan so'rov vaqti Python `deque` (ikki tomonlama navbat) to'plamiga `time.monotonic()` orqali qo'shiladi.
* Yangi so'rov kelganda, joriy vaqtdan `window_seconds` (30 soniya) dan eski bo'lgan barcha vaqt tamg'alari navbat boshidan chiqarib tashlanadi (`while queue and queue[0] <= now - window: queue.popleft()`).
* Qolgan so'rovlar soni limitga teng yoki katta bo'lsa, eng eski so'rovning oynadan chiqib ketishiga qancha vaqt qolgani hisoblanadi: `waits.append(queue[0] + window - now)`.
* **Kritik xavfsizlik qoidasi:** Bloklangan so'rov (`429`) navbatga QO'SHILMAYDI! Agar bloklangan so'rov ham navbatga qo'shilganda edi, tajovuzkor har 20 soniyada bitta xato so'rov yuborib, foydalanuvchi oynasini abadiy cho'zib, akkauntni doimiy qulflab qo'ygan bo'lardi.

### 2.4. HTTP Standartlari va Muhim Sarlavhalar

* **HTTP 401 Unauthorized:** Foydalanuvchi o'z shaxsini tasdiqlay olmadi (login yoki parol xato). RFC bo'yicha bu status autentifikatsiya ma'lumotlari mavjud emasligini yoki noto'g'riligini bildiradi.
* **HTTP 429 Too Many Requests (RFC 6585):** Foydalanuvchi ma'lum vaqt oralig'ida ruxsat berilgan so'rovlar sonidan ortiq murojaat qildi.
* **`Retry-After` sarlavhasi:** Mijozga yangi so'rov yuborishdan oldin necha soniya kutishi kerakligini ko'rsatadi (masalan: `Retry-After: 28`). Qonuniy API mijozlari va skriptlar ushbu sarlavhadagi soniya davomida o'z so'rovlarini to'xtatib turishi (backoff strategy) kerak.
* **`X-Request-ID` sarlavhasi:** Server tomonidan har bir kiruvchi HTTP so'roviga beriladigan takrorlanmas unikal identifikator (UUID4, masalan: `9a8f12...`). Mijoz javob sarlavhasida bu IDni oladi. Agar tizimda nosozlik yoki shubhali bloklanish yuz bersa, foydalanuvchi administratorga aynan shu IDni aytadi. Administrator esa log faylidan ushbu ID bo'yicha so'rovning barcha parametrlarini bir zumda topadi.
* **`Cache-Control: no-store`:** Javob brauzer xotirasida yoki oraliq proksi-serverlar keshida aslo saqlanmasligini ta'minlaydi.

### 2.5. Soxta IP (IP Spoofing) va `X-Forwarded-For` Xavfi

* Ko'pgina yangi dasturchilar mijoz IP-manzilini `request.headers.get('X-Forwarded-For')` orqali olish xatosiga yo'l qo'yishadi.
* **Xavf:** `X-Forwarded-For` — bu mijoz o'zi xohlagan qiymatni yozib yuborishi mumkin bo'lgan oddiy HTTP sarlavhasi! Tajovuzkor har bir so'rovda `X-Forwarded-For: 1.1.1.1`, `X-Forwarded-For: 1.1.1.2` deb yangi soxta IP yuborib, IP bo'yicha barcha limitlarni bemalol aylanib o'tishi mumkin.
* **Bizning yechim:** Bizning kodimizda IP faqat TCP ulanish rozetkasidan olinadi: `self.client_address[0]`. Mijoz yuborgan `X-Forwarded-For: 198.51.100.10` sarlavhasi butunlay e'tiborsiz qoldiriladi.
* *(Eslatma: Haqiqiy ishlab chiqarishda Nginx/Cloudflare kabi ishonchli Reverse Proxy orqasida turgandagina, faqat proksining o'zi o'rnatgan va ishonchli ichki tarmoqdan kelgan sarlavhagina qabul qilinadi).*

### 2.6. Xavfsiz Autentifikatsiya va Jurnallashtirish Qoidalari

1. **User Enumeration (Foydalanuvchilarni qidirib topish) ga qarshi himoya:**
   * Agar foydalanuvchi `alice` mavjud bo'lib, unga "Parol noto'g'ri", `bob` mavjud bo'lmaganda esa "Bunday foydalanuvchi mavjud emas" deb javob qaytarilsa, tajovuzkor tizimda qanday foydalanuvchi nomlari borligini osongina aniqlab oladi.
   * Bizning kodimizda mavjud `alice` uchun ham, mavjud bo'lmagan `nobody` uchun ham mutlaqo bir xil javob qaytariladi: HTTP 401, `{"result": "login_failed", "request_id": "..."}`.
2. **Timing Attack (Vaqt tahlili) ga qarshi himoya:**
   * Python'ning oddiy `if a == b:` satrlari satr belgilarini birma-bir solishtiradi va birinchi mos kelmagan belgidayoq to'xtaydi. Tajovuzkor so'rovning qaytish vaqtini mikrosekundlargacha o'lchab, paroldagi qaysi harflar to'g'ri ekanini topishi mumkin.
   * Bizning kodimizda `hmac.compare_digest(password.encode(), DEMO_PASSWORD.encode())` ishlatilgan. Bu funksiya taqqoslashni har doim bir xil vaqtda (constant time) amalga oshiradi.
3. **OWASP Jurnallashtirish Standarti (Logging Cheat Sheet):**
   * Loglarga (jurnalga) HECH QACHON foydalanuvchi kiritgan ochiq parol, sessiya kaliti, token yoki shaxsiy ma'lumotlar yozilmasligi shart.
   * Bizning `events.jsonl` faylimizga faqat xavfsiz audit parametrlari yoziladi:
     `{"ts": 1731412345.123, "request_id": "...", "ip": "127.0.0.1", "user": "alice", "event": "login_failed", "status": 401}`.
   * Fayl ruxsati faqat yaratuvchiga tegishli bo'lishi uchun `umask 077` va `chmod 600` qilinadi.

### 2.7. Monitoring Qoidalari (`monitor.py`)

Xavfsizlik monitori jurnalni o'qib, 60 soniyalik sirg'aluvchi oynada quyidagi ikki xil anomaliyani aniqlaydi:
1. **`FAIL_BURST`:** 60 soniya ichida bitta IP-manzildan kamida 3 ta `login_failed` hodisasi qayd etilsa. Bu parolni topishga urinayotgan dastlabki hujumdan darak beradi.
2. **`LIMIT_BURST`:** 60 soniya ichida bitta IP-manzildan kamida 2 ta `rate_limited` hodisasi qayd etilsa. Bu tajovuzkor bot 429 xatosini olganiga qaramasdan, serverga tajovuzkorona so'rovlar yuborishda davom etayotganini ko'rsatadi.

---

# 3-BO'LIM. AMALIY MASHG'ULOTNI BAJARISH BO'YICHA KETMA-KET QO'LLANMA VA BARCHA CLI BUYRUQLARNING TO'LIQ TAHLILI

Ushbu bo'limda laboratoriya ishining 8 ta topshirig'i ketma-ket, har bir CLI buyrug'i, undagi parametr va bayroqlar (flags) batafsil tushuntirilgan holda ko'rsatiladi.

> **Eslatma:** Ubuntu Server terminalida ishlash uchun 2 ta alohida terminal oynasi (yoki 2 ta SSH seansi / `tmux` oynasi) oching.
> * **1-Terminal:** Python serveri (`app.py`) doimiy ishlab turishi uchun.
> * **2-Terminal:** Buyruqlar, test so'rovlari va tahlil vositalarini yurgazish uchun.

---

### 3.1. Tayyorgarlik va Muhitni Sozlash (1 va 2-qadamlar)

#### 1-qadam: Kerakli paketlarni o'rnatish va xavfsiz katalog yaratish

2-Terminalda quyidagi buyruqlarni bajaring:

```bash
sudo apt update
```
* **Nima qiladi:** Ubuntu paketlar ombori (repository) indekslarini yangilaydi, eng so'nggi dastur versiyalari ro'yxatini yuklab oladi.
* **Nega kerak:** Keyingi dasturlarni o'rnatishda xatolik yuz bermasligi uchun.

```bash
sudo apt install -y python3 curl nano
```
* **Nima qiladi:** Tizimga laboratoriya uchun zarur bo'lgan uchta asosiy vositani o'rnatadi:
  * `python3` — Backend xizmati (`app.py`) va monitoring vositasini (`monitor.py`) ishlatish uchun.
  * `curl` — HTTP so'rovlarini (GET, POST) terminal orqali yuborish uchun.
  * `nano` — Konfiguratsiya (`policy.json`) va kodlarni tahrirlash uchun qulay matn muharriri.
  * `-y` bayrog'i: O'rnatish paytida tasdiqlash so'roviga avtomatik "Yes" deb javob beradi.

```bash
umask 077
```
* **Nima qiladi:** Joriy terminal seansida yangi yaratiladigan barcha fayl va papkalar uchun birlamchi xavfsizlik niqobini (umask) `077` qilib belgilaydi.
* **Xavfsizlik ma'nosi:** Standart rejimda yaratilgan fayllarni boshqa foydalanuvchilar o'qishi mumkin. `077` niqobi yangi fayllarga faqat joriy foydalanuvchiga to'liq huquq beradi (fayllar uchun `600` — faqat egasi o'qiy/yoza oladi; papkalar uchun `700`), begona foydalanuvchilar esa uni mutlaqo o'qiy olmaydi. Bu xavfsizlik auditida muhim talabdir.

```bash
mkdir -p ~/a11-lab
```
* **Nima qiladi:** Foydalanuvchining uy katalogida (`~`) `a11-lab` nomli yangi papka ochadi.
  * `-p` bayrog'i: Agar papka oldindan mavjud bo'lsa, xatolik chiqarmaydi.

```bash
cd ~/a11-lab
```
* **Nima qiladi:** Yangi ochilgan `~/a11-lab` ishchi katalogiga o'tadi.

---

#### 2-qadam: Boshlang'ich konfiguratsiya va dastur kodlarini tayyorlash

Boshlang'ich konfiguratsiya fayli — `policy.json` ni yaratamiz. Dastlab unda rate limiting o'chirilgan (`"rate_limit": false`):

```bash
cat > policy.json <<'EOF'
{
 "rate_limit": false,
 "window_seconds": 30,
 "ip_limit": 8,
 "account_limit": 3
}
EOF
```
* **Nima qiladi:** `cat > policy.json <<'EOF'` konstruksiyasi ("Here Document") ko'rsatilgan matnni to'g'ridan-to'g'ri `policy.json` fayliga yozadi.
  * `"rate_limit": false` — Cheklov hozircha o'chiq.
  * `"window_seconds": 30` — Sirg'aluvchi oyna vaqti: 30 soniya.
  * `"ip_limit": 8` — Bitta IPga 30 soniyada ko'pi bilan 8 ta so'rov ruxsat etilgan.
  * `"account_limit": 3` — Bitta akkaunt nomiga 30 soniyada ko'pi bilan 3 ta so'rov ruxsat etilgan.

Endi fayldan zaxira nusxa olamiz va sintaksisini tekshiramiz:

```bash
cp policy.json policy.before.json
```
* **Nima qiladi:** `policy.json` faylidan `policy.before.json` nomli zaxira nusxa oladi. Bu keyinchalik cheklov yoqilganda `diff` orqali farqlarni solishtirish uchun kerak bo'ladi.

```bash
python3 -m json.tool policy.json
```
* **Nima qiladi:** Pythonning `json.tool` moduli orqali `policy.json` faylining sintaksisini tekshiradi va chiroyli formatda ekranga chiqaradi. Agar JSONda vergul yoki qavsda xatolik bo'lsa, xatoni darhol ko'rsatadi.

Endi laboratoriyaning ikkita asosiy skriptini yaratamiz:

1) `nano app.py` buyrug'i orqali fayl ochib, quyidagi kodni to'liq joylang va saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`):

```python
import json
import math
import os
import re
import time
import uuid
import hmac
from collections import defaultdict, deque
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'policy.json').read_text())
BUCKETS = defaultdict(deque)
CLOCK = time.monotonic
os.umask(0o077)
LOG = ROOT / 'events.jsonl'
# Synthetic fixture only; no session or real password database.
DEMO_PASSWORD = 'Lab11-Only!'

def retry_after(ip, user):
    now, window = CLOCK(), CFG['window_seconds']
    pairs = [(('ip', ip), CFG['ip_limit']),
             (('account', user), CFG['account_limit'])]
    waits = []
    for key, limit in pairs:
        queue = BUCKETS[key]
        while queue and queue[0] <= now - window:
            queue.popleft()
        if len(queue) >= limit:
            waits.append(queue[0] + window - now)
    if waits:
        return max(1, math.ceil(max(waits)))
    for key, limit in pairs:
        BUCKETS[key].append(now)
    return 0

class App(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_result(self, status, event, user='-', retry=0):
        rid = uuid.uuid4().hex
        record = dict(ts=round(time.time(), 3), request_id=rid,
                      ip=self.client_address[0], user=user,
                      event=event, status=status)
        with LOG.open('a', encoding='utf-8') as out:
            out.write(json.dumps(record) + '\n')
        body = json.dumps({'result': event, 'request_id': rid}).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Request-ID', rid)
        if retry:
            self.send_header('Retry-After', str(retry))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            self.send_result(200, 'health_ok')
        else:
            self.send_result(404, 'not_found')

    def do_POST(self):
        if self.path != '/login':
            return self.send_result(404, 'not_found')
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 1024:
                return self.send_result(413, 'invalid_size')
            data = json.loads(self.rfile.read(length))
            user = data.get('username', '').strip().lower()
            password = data.get('password')
            if not re.fullmatch(r'[a-z0-9_]{1,24}', user):
                raise ValueError('invalid username')
            if not isinstance(password, str) or len(password) > 128:
                raise ValueError('invalid password')
        except (ValueError, AttributeError, TypeError):
            return self.send_result(400, 'invalid_input')
        wait = retry_after(self.client_address[0], user) if (
            CFG['rate_limit']) else 0
        if wait:
            return self.send_result(429, 'rate_limited', user, wait)
        valid = hmac.compare_digest(password.encode(), DEMO_PASSWORD.encode())
        valid = valid and user == 'alice'
        self.send_result(200 if valid else 401,
                         'login_ok' if valid else 'login_failed', user)

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8011), App)
    print('A11 127.0.0.1:8011; policy=', CFG, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
```

2) `nano monitor.py` buyrug'i orqali monitoring skriptini joylang va saqlang:

```python
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

rows, invalid = [], 0
for line in Path(sys.argv[1]).read_text().splitlines():
    try:
        row = json.loads(line)
        assert isinstance(row['ts'], (int, float))
        assert all(isinstance(row[k], str) for k in
                   ('ip', 'user', 'event', 'request_id'))
        rows.append(row)
    except (ValueError, KeyError, TypeError, AssertionError):
        invalid += 1
queues, seen = defaultdict(deque), set()
totals = Counter(row['event'] for row in rows)
for row in sorted(rows, key=lambda r: r['ts']):
    if row['event'] not in ('login_failed', 'rate_limited'):
        continue
    queue = queues[row['ip']]
    queue.append(row)
    while queue and queue[0]['ts'] < row['ts'] - 60:
        queue.popleft()
    counts = Counter(r['event'] for r in queue)
    for name, event, threshold in (
        ('FAIL_BURST', 'login_failed', 3),
        ('LIMIT_BURST', 'rate_limited', 2)
    ):
        key = (row['ip'], name)
        if counts[event] >= threshold and key not in seen:
            seen.add(key)
            print(json.dumps(dict(alert=name, ip=row['ip'],
                                  count=counts[event], window_seconds=60,
                                  request_id=row['request_id'], ts=row['ts'])))
print(json.dumps(dict(summary=dict(totals), invalid_lines=invalid)))
```

Fayllarni sintaksis xatolariga tekshiramiz:

```bash
python3 -m py_compile app.py monitor.py
```
* **Nima qiladi:** Python fayllarini bayt-kodga kompilyatsiya qilib, sintaktik xatolar (indentation, qavslar, imlo xatolari) yo'qligini tekshiradi. Hech qanday xabar chiqmasa — kodlar 100% to'g'ri.

Versiyalarni tekshiramiz:

```bash
python3 --version
curl --version
```
* **Nima qiladi:** Tizimdagi Python va curl versiyalarini ekranga chiqaradi (Hisobotning D1 dalili uchun).

Bo'sh jurnal faylini yaratamiz va unga qat'iy ruxsat beramiz:

```bash
touch events.jsonl
chmod 600 events.jsonl
```
* **Nima qiladi:** 
  * `touch events.jsonl` — Bo'sh log faylini yaratadi.
  * `chmod 600 events.jsonl` — Faylga faqat uning egasi (joriy foydalanuvchi) o'qiy olishi va yoza olishi huquqini beradi (`rw-------`). Begonalar umuman kira olmaydi.

---

#### Serverni ishga tushirish (1-Terminal)

1-Terminalda dasturni ishga tushiring:

```bash
python3 -u app.py
```
* **Nima qiladi:** Serverni ishga tushiradi.
  * `-u` bayrog'i (unbuffered): Python chiqish oqimini (stdout) buferlamaydi, har bir chop etilgan xabarni darhol ekranga chiqaradi.
  * Ekranda quyidagi satr paydo bo'ladi:
    `A11 127.0.0.1:8011; policy= {'rate_limit': False, 'window_seconds': 30, 'ip_limit': 8, 'account_limit': 3}`
  * **DIQQAT:** Dasturni `sudo` bilan ishga tushirmang! 1-Terminal doimo ochiq turadi.

---

#### 2-Terminalda tekshirish (Dalil D1)

2-Terminalga o'tib, quyidagi buyruqlarni bajaring:

```bash
cd ~/a11-lab
U=http://127.0.0.1:8011
ss -ltn | grep ":8011"
```
* **Nima qiladi:**
  * `U=http://127.0.0.1:8011` — Tez-tez ishlatiladigan server manzilini `U` o'zgaruvchisiga saqlaydi.
  * `ss -ltn` — Tizimdagi tinglovchi (listening) TCP portlarini ko'rsatadi (`-l` listening, `-t` TCP, `-n` sonli portlar).
  * `grep ":8011"` — Chiqishdan faqat 8011-port qatorini filtrlaydi.
  * Natijada `127.0.0.1:8011` manzilida server tinglayotgani ko'rinadi.

Sog'lomlik tekshiruvini (healthcheck) bajaramiz:

```bash
curl --noproxy "*" -i "$U/health"
```
* **Har bir parametr ma'nosi:**
  * `curl` — HTTP so'rovlarini jo'natish vositasi.
  * `--noproxy "*"` — Har qanday tizim proksilarini chetlab o'tib, to'g'ridan-to'g'ri bog'lanishni ta'minlaydi.
  * `-i` (include): Javobning HTTP sarlavhalarini (headers) ham qo'shib ko'rsatadi.
  * `"$U/health"` — `http://127.0.0.1:8011/health` manziliga so'rov.
* **Kutiladigan natija:**
  * Status: `HTTP/1.0 200 OK`
  * Sarlavhalar: `Content-Type: application/json`, `Cache-Control: no-store`, `X-Request-ID: <unikal_uuid>`
  * Tana: `{"result": "health_ok", "request_id": "<unikal_uuid>"}`
* 🎯 **Dalil D1:** Terminaldagi VM parametrlari, versiyalar, faol policy, `ss` chiqishi va `/health` javobini skrinshot qiling yoki hisobotga qayd eting.

---

### 3.2. Cheklovsiz Holatni Kuzatish (Topshiriq 3 — Dalil D2)

Hozir `rate_limit: false`. Tizimga avtomatlashtirilgan parolni topish hujumini modellashtiramiz.

2-Terminalda `alice` akkauntiga ketma-ket 4 ta xato parol yuboring:

```bash
for attempt in 1 2 3 4; do
 curl --noproxy "*" -s -i "$U/login" \
 -H "Content-Type: application/json" \
 -d '{"username":"alice","password":"Wrong11!"}'
done
```
* **Har bir parametr ma'nosi:**
  * `for attempt in 1 2 3 4; do ... done` — Bash sikli, buyruqni ketma-ket 4 marta bajaradi.
  * `-s` (silent): Yuklanish jarayoni (progress bar) metrlarini yashiradi.
  * `-i` — HTTP status kodi va sarlavhalarini ko'rsatadi.
  * `-H "Content-Type: application/json"` — So'rov tanasi JSON formatida ekanini serverga bildiradi.
  * `-d '{"username":"alice","password":"Wrong11!"}'` — So'rov tanasida (body) foydalanuvchi nomi va xato parolni jo'natadi.
* **Kutiladigan natija:** To'rttala so'rov ham `401 Unauthorized` va `{"result": "login_failed"}` qaytaradi.
* **Xavfsizlik xulosasi:** Cheklov o'chiq bo'lgani uchun, 4-urinish ham hech qanday to'siqsiz serverga yetib bordi va parol bazasidan tekshirildi.

Endi mavjud bo'lmagan `nobody` nomiga va to'g'ri `alice` paroliga so'rov yuboramiz:

```bash
curl --noproxy "*" -i "$U/login" \
 -H "Content-Type: application/json" \
 -d '{"username":"nobody","password":"Wrong11!"}'
```
* **Natija:** `HTTP/1.0 401 Unauthorized` va `login_failed`.

```bash
curl --noproxy "*" -i "$U/login" \
 -H "Content-Type: application/json" \
 -d '{"username":"alice","password":"Lab11-Only!"}'
```
* **Natija:** `HTTP/1.0 200 OK` va `{"result": "login_ok"}`.

#### Boshlang'ich jurnaldan dalil olish va tahlil qilish:

1-Terminalga o'ting va serverni to'xtatish uchun `Ctrl + C` tugmalarini bosing.
2-Terminalda quyidagi buyruqlarni bajaring:

```bash
mv events.jsonl before.jsonl
chmod 400 before.jsonl
python3 monitor.py before.jsonl | tee before-alerts.txt
```
* **Buyruqlar tahlili:**
  * `mv events.jsonl before.jsonl` — Server yozgan log faylini birinchi tajriba dalili sifatida `before.jsonl` ga o'zgartiradi.
  * `chmod 400 before.jsonl` — Faylga faqat o'qish (Read-only, `r--------`) huquqini beradi. Bu dalil faylining tasodifan o'zgarib ketmasligini kafolatlaydi.
  * `python3 monitor.py before.jsonl` — Monitoring skriptini ishga tushirib, jurnaldan anomaliyalarni qidiradi.
  * `| tee before-alerts.txt` — Chiqqan natijani ham ekranda ko'rsatadi, ham `before-alerts.txt` fayliga saqlaydi.
* **Kutiladigan tahlil natijasi:**
  * `{"alert": "FAIL_BURST", "ip": "127.0.0.1", "count": 3, "window_seconds": 60, ...}`
  * `{"summary": {"login_failed": 5, "login_ok": 1, "health_ok": 1}, "invalid_lines": 0}`
* 🎯 **Dalil D2:** 4 ta 401, bitta 200, `before-alerts.txt` dagi `FAIL_BURST` ogohlantirishi.

---

### 3.3. Akkaunt Limiti va Ishonchli IP Manbasi (Topshiriq 4 — Dalil D3)

Endi tizimda Rate Limitingni faollashtiramiz.

`policy.json` faylini tahrirlang:

```bash
nano policy.json
```
Faqat `"rate_limit": false` qatorini `"rate_limit": true` ga o'zgartiring va saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`).

O'zgarishlarni tekshiramiz:

```bash
python3 -m json.tool policy.json
diff -u policy.before.json policy.json
cp policy.json policy.good.json
```
* **Buyruqlar tahlili:**
  * `diff -u policy.before.json policy.json` — Oldingi va yangi fayl o'rtasidagi farqni unifikatsiyalangan ko'rinishda chiqaradi (`- rate_limit: false`, `+ rate_limit: true`).
  * `cp policy.json policy.good.json` — To'g'ri sozlangan konfiguratsiyaning zaxira nusxasini saqlab qo'yadi.

#### Serverni qayta ishga tushirish (1-Terminal):

1-Terminalda serverni qayta yoqing:
```bash
python3 -u app.py
```
* Chiqishda `rate_limit: True` bo'lganini ko'rasiz. Yangi bo'sh `events.jsonl` avtomatik yaratiladi.

#### 2-Terminalda tezkor 4 ta so'rov yuborish:

```bash
for attempt in 1 2 3 4; do
 curl --noproxy "*" -s -i "$U/login" \
 -H "Content-Type: application/json" \
 -d '{"username":"alice","password":"Wrong11!"}'
done
```
* **Kutiladigan natija:**
  * 1-urinish: `401 Unauthorized` (result: login_failed)
  * 2-urinish: `401 Unauthorized` (result: login_failed)
  * 3-urinish: `401 Unauthorized` (result: login_failed) — `account_limit: 3` tugadi!
  * 4-urinish: **`HTTP/1.0 429 Too Many Requests`**!
    * Sarlavha: `Retry-After: 30` (yoki 28–29 soniya)
    * Tana: `{"result": "rate_limited", "request_id": "..."}`
* **Xulosa:** 4-urinishda server parolni tekshirishga ham o'tirmasdan, so'rovni darhol 429 bilan qaytardi.

#### Soxta `X-Forwarded-For` bilan aldashga urinish:

30 soniya o'tmasdan turib, to'g'ri parol va soxta IP sarlavhasi bilan so'rov yuboring:

```bash
curl --noproxy "*" -i "$U/login" \
 -H "Content-Type: application/json" \
 -H "X-Forwarded-For: 198.51.100.10" \
 -d '{"username":"alice","password":"Lab11-Only!"}'
```
* **Kutiladigan natija:** **`HTTP/1.0 429 Too Many Requests`**!
* **Nega?**
  1. Parol to'g'ri bo'lsa ham, limit tekshiruvi parolni tekshirishdan oldin turadi!
  2. Mijoz o'zini `198.51.100.10` manzilidan deb ko'rsatgan bo'lsa ham, server unga ishonmadi va haqiqiy ulanish IPsi (`127.0.0.1`) hamda akkaunt (`alice`) bo'yicha limit qo'ydi.

Tizim umumiy ishdan chiqmaganini (`/health`) tekshiramiz:

```bash
curl --noproxy "*" -i "$U/health"
```
* **Natija:** `HTTP/1.0 200 OK`, `result: health_ok`.
* **Xulosa:** Login chegarasi `/health` marshrutiga ta'sir qilmaydi, xizmat ko'rsatish butunlay to'xtab qolmagan (No DoS).
* 🎯 **Dalil D3:** 401, 401, 401, 429 javoblari, `Retry-After` mavjudligi, soxta IP bilan ham 429 olinishi va healthcheck 200 OK bergani.

---

### 3.4. Qonuniy Tiklanish va IP Bo'yicha Cheklov (5 va 6-topshiriqlar — Dalil D4)

#### 5-topshiriq: Qonuniy foydalanuvchining tiklanishi (31 soniya kutish)

Akkaunt bloklanishi doimiy emasligini tekshirish uchun 31 soniya kuting (chunki oyna vaqti 30 soniya) va to'g'ri parol bilan kiring:

```bash
sleep 31
curl --noproxy "*" -i "$U/login" \
 -H "Content-Type: application/json" \
 -d '{"username":"alice","password":"Lab11-Only!"}'
```
* **Buyruqlar tahlili:**
  * `sleep 31` — Terminalni 31 soniyaga to'xtatib turadi. Bu vaqt ichida sirg'aluvchi oyna bo'shaydi.
* **Kutiladigan natija:** **`HTTP/1.0 200 OK`**, `{"result": "login_ok"}`.
* **Xavfsizlik xulosasi:** Tizim xatoga yo'l qo'ygan haqiqiy foydalanuvchini abadiy qulflab qo'ymaydi; belgilangan vaqt o'tgach, qonuniy foydalanuvchi hisobi o'z-o'zidan tiklanadi.

---

#### 6-topshiriq: IP bo'yicha limitni tekshirish (Password Spraying modellashtirish)

Yana 31 soniya kuting (IP hisoblagichi bo'shashi uchun), so'ng bitta IPdan 9 ta har xil nom bilan (`user1` dan `user9` gacha) so'rov yuboring:

```bash
sleep 31
for n in 1 2 3 4 5 6 7 8 9; do
 curl --noproxy "*" -s -i "$U/login" \
 -H "Content-Type: application/json" \
 -d '{"username":"user'"$n"'","password":"Wrong11!"}'
done
```
* **Buyruq tahlili:** Har bir so'rovda `username` har xil (`user1`, `user2`, ...), shuning uchun `account_limit: 3` ishlamaydi (chunki har bir akkauntga atigi 1 tadan so'rov bormoqda).
* **Kutiladigan natija:**
  * Dastlabki 8 ta so'rov (`user1` dan `user8` gacha): **`401 Unauthorized`**.
  * 9-so'rov (`user9`): **`HTTP/1.0 429 Too Many Requests`**!
* **Xavfsizlik xulosasi:** Tizim Password Spraying hujumini aniqladi — garchi har bir akkauntga bittadan urinish bo'lsa-da, bitta IPdan 30 soniyada 8 tadan ko'p so'rov kelgani sababli `ip_limit: 8` ishga tushdi va 9-so'rov to'xtatildi!

---

#### Tahliliy topshiriq: CAPTCHA va MFA bo'yicha qarorlar jadvali

Laboratoriya shartidagi tahliliy jadval uchun asoslangan xavfsizlik qarorlari:

| Holat | Talabaning xavfsizlik qarori |
| :--- | :--- |
| **Bir marta parolni adashtirgan odatiy foydalanuvchi** | Hech qanday qo'shimcha cheklov yoki CAPTCHA qo'yilmaydi. Oddiy `401 Unauthorized` xatosi qaytarilib, qayta kiritishga ruxsat beriladi (Foydalanuvchi qulayligini buzmaslik uchun). |
| **Takroriy urinish va ko'p akkauntga bir xil manbadan murojaat** | Xavf darajasi yuqori deb baholanadi. Rate Limiting (429) ishga tushiriladi va vaqtinchalik bloklanadi. Agar so'rovlar davom etsa, kirish sahifasida majburiy Google reCAPTCHA v3 / Cloudflare Turnstile va ko'p bosqichli autentifikatsiya (MFA — SMS yoki Authenticator TOTP kodi) talab etiladi. |
| **CAPTCHA tokeni yo'q, muddati o'tgan yoki qayta yuborilgan** | So'rov zudlik bilan server tomonida rad etiladi (`400 Bad Request` yoki `403 Forbidden`). Parol tekshirish funksiyasiga umuman o'tkazilmaydi. Tokenning haqiqiyligi, yaratilgan vaqti va bir martalik ishlatilishi (Replay attack oldini olish) qat'iy serverda tekshirilishi shart. |

* 🎯 **Dalil D4:** `sleep 31` dan keyingi 200 OK, 9 ta so'rovda 8 ta 401 va 1 ta 429 olingani hamda yuqoridagi CAPTCHA/MFA qarorlar jadvali.

---

### 3.5. Jurnal va Monitoring Natijalarini Tekshirish (Topshiriq 7 — Dalil D5)

1-Terminalda `Ctrl + C` bosib serverni to'xtating.
2-Terminalda log faylini arxivlab, monitoring vositasini ishga tushiring:

```bash
cp events.jsonl after.jsonl
chmod 400 after.jsonl
python3 monitor.py after.jsonl | tee after-alerts.txt
```
* **Nima qiladi:**
  * `cp events.jsonl after.jsonl` — Ikkinchi tajriba loglarini `after.jsonl` ga nusxalaydi.
  * `chmod 400 after.jsonl` — Faylni o'zgartirib bo'lmas holatga (Read-only) keltiradi.
  * `python3 monitor.py after.jsonl | tee after-alerts.txt` — Monitoring skriptini yurgazadi.
* **Kutiladigan monitoring natijasi:**
  * Ikkala ogohlantirish ham qayd etiladi:
    1. `{"alert": "FAIL_BURST", "ip": "127.0.0.1", "count": 3, "window_seconds": 60, ...}`
    2. **`{"alert": "LIMIT_BURST", "ip": "127.0.0.1", "count": 2, "window_seconds": 60, ...}`**
  * `LIMIT_BURST` chiqishi — bitta IPdan 60 soniya ichida kamida 2 marta `rate_limited` (429) sodir bo'lganini bildiradi.
  * Xulosa qatorida `invalid_lines: 0` bo'lishi kerak.

Jurnalning oxirgi qatorlarini va fayl ruxsatlarini tekshiring:

```bash
tail -n 6 after.jsonl
```
* **Nima qiladi:** `after.jsonl` faylining eng oxirgi 6 ta yozuvini ekranga chiqaradi.

```bash
stat -c "%a %n" events.jsonl before.jsonl after.jsonl
```
* **Nima qiladi:** Fayllarning raqamli kirish huquqlarini (permissions) ko'rsatadi:
  * `events.jsonl` — `600` (egasi o'qiydi/yozadi)
  * `before.jsonl` — `400` (faqat o'qish)
  * `after.jsonl` — `400` (faqat o'qish)

#### Maxfiy ma'lumotlar sizib chiqmaganini isbotlash (Kritik tekshiruv):

```bash
grep -nE 'Wrong11!|Lab11-Only!|password|Authorization' after.jsonl
```
* **Har bir parametr ma'nosi:**
  * `grep` — Matn qidirish vositasi.
  * `-n` — Mos kelgan qator raqamini ko'rsatadi.
  * `-E` (Extended Regex) — Bir nechta kalit so'zlarni mantiqiy "YOKI" (`|`) bilan qidiradi.
* **Kutiladigan natija:** **Mutlaqo hech qanday natija chiqmasligi kerak (bo'sh qolishi kerak)!**
* `echo $?` buyrug'ini bersangiz, `1` chiqadi (chunki hech qanday moslik topilmadi).
* **Xulosa:** Tizim OWASP Logging qoidalariga to'liq mos keladi — parollar, avtorizatsiya sarlavhalari log faylida umuman qayd etilmagan!

#### `X-Request-ID` orqali insidentni log bilan bog'lash:

Yuqoridagi 429 javoblaridan birida chiqqan `X-Request-ID` qiymatini oling (masalan, `d3b1a8f9...`) va logdan qidiring:

```bash
grep -F "BU_YERGA_O'ZINGIZNING_REQUEST_ID_QOYING" after.jsonl
```
* **Har bir parametr ma'nosi:**
  * `-F` (Fixed strings) — Satrni muntazam ifoda (regex) deb emas, oddiy qat'iy matn sifatida tezkor qidiradi.
* **Kutiladigan natija:**
  `{"ts": 17314..., "request_id": "d3b1...", "ip": "127.0.0.1", "user": "alice", "event": "rate_limited", "status": 429}`
* **Xulosa:** Mijozga yuborilgan xato javobi va serverdagi xavfsizlik jurnali bir-biriga 100% bog'langan.
* 🎯 **Dalil D5:** `FAIL_BURST` va `LIMIT_BURST` chiqishi, `invalid_lines: 0`, maxfiy so'zlar qidiruvida hech narsa chiqmagani (`exit code 1`), fayl huquqlari (`600`, `400`) va `request_id` orqali topilgan log qatori.

---

### 3.6. Xavfsiz Ekspluatatsiya, Raqamli Dalillarni Saqlash va Hodisaga Javob (Topshiriq 8 — Dalil D6)

Ushbu bosqichda to'plangan barcha dalillar kriminalistik (forensic) talablar asosida arxivlanadi va yaxlitligi tekshiriladi.

#### Dalillarni arxivlash va SHA-256 xesh summasini hisoblash:

```bash
CASE_DIR="evidence-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -m 700 "$CASE_DIR"
cp before.jsonl after.jsonl before-alerts.txt after-alerts.txt \
 policy.before.json policy.good.json "$CASE_DIR/"
sha256sum "$CASE_DIR"/* > "$CASE_DIR/SHA256SUMS"
sha256sum -c "$CASE_DIR/SHA256SUMS"
chmod 400 "$CASE_DIR"/*
```
* **Buyruqlar tahlili:**
  * `CASE_DIR="evidence-$(date -u +%Y%m%dT%H%M%SZ)"` — UTC vaqti bilan unikal papka nomi generatsiya qiladi (masalan: `evidence-20261112T114958Z`).
  * `mkdir -m 700 "$CASE_DIR"` — Papkani faqat egasi kira oladigan huquq bilan yaratadi.
  * `cp ... "$CASE_DIR/"` — Tajribaning barcha loglari, alertlari va konfiguratsiyalarini papkaga nusxalaydi.
  * `sha256sum "$CASE_DIR"/* > "$CASE_DIR/SHA256SUMS"` — Papkadagi har bir faylning SHA-256 kriptografik xeshini hisoblab, manifest fayliga yozadi.
  * `sha256sum -c "$CASE_DIR/SHA256SUMS"` — Manifestdagi barcha fayllarni qayta tekshiradi. Har bir fayl qarshisida **`OK`** yozuvi chiqishi kerak. Bu fayllar butun va o'zgarmaganligini isbotlaydi.
  * `chmod 400 "$CASE_DIR"/*` — Dalillar papkasidagi barcha fayllarni faqat o'qish rejimiga o'tkazadi.

Konfiguratsiyaning asl nusxaga baytma-bayt mosligini tekshirish:

```bash
cp policy.good.json policy.restore-check.json
cmp policy.good.json policy.restore-check.json
```
* **Nima qiladi:** `cmp` (compare) buyrug'i ikkita faylni baytma-bayt solishtiradi. Hech qanday chiqish bo'lmasa va chiqish kodi 0 bo'lsa (`echo $?` -> 0), fayllar 100% bir xil ekani isbotlanadi.

---

#### Xavfsizlik Hodisasi Kartasi (Incident Response Card)

Laboratoriya talabiga ko'ra to'ldirilgan hodisa kartasi:

1. **Aniqlash (Detection):**
   * *Qaysi qoida va parametrlar shubha uyg'otdi?* `monitor.py` orqali 60 soniyalik oynada `127.0.0.1` manzilidan `FAIL_BURST` (3 ta ketma-ket `login_failed`) va `LIMIT_BURST` (2 ta ketma-ket `rate_limited`) ogohlantirishlari qayd etildi.
   * *Muvaffaqiyatli kirish bo'lganmi?* Jurnal tahlilida dastlabki noto'g'ri urinishlardan so'ng bitta `login_ok` hodisasi kuzatildi, keyingi ommaviy so'rovlar esa 429 bilan to'xtatildi.
2. **Tekshirish (Investigation):**
   * *Bu oddiy xatomi, NATmi yoki hujummi?* Bitta IPdan qisqa vaqt ichida turli xil foydalanuvchi nomlari (`user1`–`user9`) orqali so'rov yuborilishi — bu oddiy foydalanuvchi adashishi emas, balki Password Spraying yoki avtomatlashtirilgan bot harakati ekanligini ko'rsatadi.
   * *Zarur qo'shimcha dalillar:* Tashqi proksi jurnallari, User-Agent sarlavhasi tahlili, so'rovlar orasidagi intervallar (jitter) tahlili.
3. **Cheklash (Containment):**
   * Gibrid Rate Limiting mexanizmi tajovuzkor IPni vaqtincha 429 status kodi orqali parolni tekshirishdan to'sib qo'ydi.
   * Agar xavf davom etsa, ushbu manba IP uchun Cloudflare/WAF darajasida IP-bloklash yoki majburiy CAPTCHA/MFA tekshiruvi yoqiladi. Faqat xato urinishlar bo'lgani sababli akkaunt parolini majburiy o'zgartirish yoki akkauntni doimiy o'chirishga zarurat yo'q.
4. **Tiklash (Recovery):**
   * Konfiguratsiya `policy.good.json` asosida tiklandi. Server qayta ishga tushirilib, `/health` va to'g'ri login testdan o'tkazildi. Barcha loglar SHA-256 nazorati ostida arxivlandi.

---

#### Tizimni xavfsiz holatda qayta tiklash:

```bash
cp policy.good.json policy.json
python3 -m json.tool policy.json
python3 -u app.py
```
2-Terminalda tekshirib ko'ring:
```bash
curl --noproxy "*" -i "$U/health"
curl --noproxy "*" -i "$U/login" \
 -H "Content-Type: application/json" \
 -d '{"username":"alice","password":"Lab11-Only!"}'
```
* Ikkala so'rov ham `200 OK` qaytarishi kerak.
* 1-Terminalda `Ctrl + C` bosib mashg'ulotni yakunlang.
* 🎯 **Dalil D6:** SHA-256 xesh tekshiruvi natijasi (`OK`), `cmp` muvaffaqiyati, Hodisa kartasi va server qayta ulangandan keyingi 200 javoblari.

---

# 4-BO'LIM. TALABANING HISOBOTI VA TEKSHIRUV RO'YXATI

Laboratoriya topshirig'i bo'yicha hisobot quyidagi qismlardan iborat bo'lishi va har bir dalil uchun terminal buyrug'i hamda uning natijasi ko'rsatilishi kerak:

### 4.1. Tekshiruv natijalari xulosa jadvali

| Tekshiruv bosqichi | Kutiladigan holat | Amaldagi natija (Sizda qanday chiqdi) | Holati |
| :--- | :--- | :--- | :--- |
| **1. Limit o'chiq:** 4 ta noto'g'ri login | `401 Unauthorized` × 4 ta | To'rttala so'rov ham 401 va `login_failed` qaytardi | Bajarildi |
| **2. Akkaunt limiti yoqilgan:** 4 ta xato login | `401 × 3` → `429 Too Many Requests` | Dastlabki 3 tasi 401, 4-so'rovda 429 va `Retry-After: 30` qaytdi | Bajarildi |
| **3. Soxta IP bilan limitdan o'tish:** | 429 qaytadi; Haqiqiy IP saqlanadi | Soxta `X-Forwarded-For` e'tiborga olinmadi, 429 qaytdi, logda `127.0.0.1` | Bajarildi |
| **4. Muddat tugagach qonuniy login:** | 31 soniyadan so'ng `200 OK` | `sleep 31` dan keyin to'g'ri parol bilan 200 `login_ok` olindi | Bajarildi |
| **5. Turli 9 nom; bitta IP:** | `401 × 8` → `429 Too Many Requests` | Dastlabki 8 tasi 401, 9-si IP limiti bo'yicha 429 oldi | Bajarildi |
| **6. Monitoring natijasi:** | `FAIL_BURST` va `LIMIT_BURST` | Ikkala ogohlantirish chiqdi, `invalid_lines: 0` | Bajarildi |

### 4.2. Baholash mezonlari (Jami 10 ball)

* **Muhit, health va boshlang'ich nazorat (1 ball):** D1 dalili (Python, curl, port, health 200).
* **Akkaunt limiti, Retry-After va soxta IP tekshiruvi (2 ball):** D3 dalili (401x3 -> 429, Retry-After mavjudligi, soxta IP rad etilishi).
* **IP limiti va qonuniy tiklanish (2 ball):** D4 dalili (sleep 31 dan so'ng 200 OK, 9 ta nom bilan IP limit 429).
* **Monitoring, request_id va maxfiy qiymat tekshiruvi (2 ball):** D5 dalili (FAIL_BURST, LIMIT_BURST, grep maxfiy ma'lumot topmagani, request_id bog'lanishi).
* **Dalil nusxalari, hash va konfiguratsiyani qaytarish (2 ball):** D6 dalili (SHA256SUMS OK, cmp mosligi, arxivlash).
* **Hisobot, CAPTCHA/MFA qarori va xulosa (1 ball):** To'ldirilgan hodisa kartasi va tahliliy javoblar.

---

# 5-BO'LIM. NAZORAT SAVOLLARI VA ILMIY JAVOBLAR

Ushbu savollar himoya paytida o'qituvchi tomonidan berilishi mumkin bo'lgan nazorat savollaridir:

#### 10-savol: 401 va 429 o'rtasidagi farq nima? Nega to'g'ri parol ham vaqtincha 429 oladi?
* **Javob:** 
  * `401 Unauthorized` — Autentifikatsiyaning o'zi muvaffaqiyatsiz tugaganini bildiradi (kiritilgan login yoki parol xato).
  * `429 Too Many Requests` — Mijoz belgilangan vaqt oralig'ida (oynada) ruxsat etilgan so'rovlar limitidan oshib ketganini bildiradi. Bu xato mijoz kiritgan ma'lumotlarning to'g'ri yoki noto'g'riligiga bog'liq emas.
  * **To'g'ri parol nega 429 oladi?** Xavfsizlik arxitekturasida Rate Limiting filtri autentifikatsiya (parolni tekshirish) funksiyasidan **OLDIN** joylashtiriladi. Agar hisob yoki IP belgilangan limitga tushgan bo'lsa, server resurslarini (CPU, ma'lumotlar bazasi so'rovlari) tejash va parolni topishga urinayotgan botni to'xtatish uchun parol to'g'ri bo'lsa ham tekshirishga o'tmasdan darhol 429 javobini qaytaradi.

#### 11-savol: IP va akkaunt bo'yicha limitlarni birga qo'llash nimani yaxshilaydi?
* **Javob:** Faqat bitta parametrga tayanish jiddiy xavfsizlik kamchiliklarini keltirib chiqaradi. 
  * Agar faqat IP cheklansa, bitta umumiy NAT (korxona, universitet) ortidagi yuzlab begunoh odamlar bitta odamning xatosi tufayli bloklanadi, yoki tajovuzkor botnet orqali IPlarni almashtirib cheklovdan qochadi.
  * Agar faqat akkaunt cheklansa, tajovuzkor o'zi bilgan loginlarga ataylab xato so'rov yuborib, ularni bloklab qo'yishi (Denial of Service) yoki bitta IPdan minglab turli akkauntlarga bittadan parol sinab ko'rishi (Password Spraying) mumkin.
  * Ikkalasini birga qo'llash (Gibrid himoya) Brute-force'ni ham, Password Spraying'ni ham to'xtatishga imkon beradi va NATdagi zararni minimallashtiradi.

#### 12-savol: CAPTCHA nega yakka o'zi yetarli emas va nima uchun server tasdig'i kerak?
* **Javob:** 
  * CAPTCHA faqat mijozning inson ekanligini ehtimoliy tekshirish vositasi bo'lib, u so'rovlar tezligini to'liq jilovlay olmaydi (zamonaviy botlar AI va OCR modellari yoki arzon insoniy ferma xizmatlari orqali CAPTCHAni yechishga qodir).
  * Ko'plab dasturchilar CAPTCHAni faqat Frontend (brauzer) darajasida tekshiradi. Ammo tajovuzkor brauzerdan foydalanmasdan, to'g'ridan-to'g'ri `curl` yoki Python skript orqali API endpointiga so'rov yuborishi mumkin.
  * Shuning uchun CAPTCHA tokeni albatta server tomonida (backend) Google/Cloudflare API provayderiga yuborilib tekshirilishi, tokenning amal qilish muddati va qayta ishlatilmaganligi (Replay attack profilaktikasi) kafolatlanishi shart.

#### 13-savol: `request_id`, vaqt va hodisa turi insident tahlilida qanday bog'lanadi?
* **Javob:**
  * Har bir kiruvchi so'rovga serverda unikal `request_id` (UUID4) beriladi va bu ID mijozga qaytariladigan HTTP javob sarlavhasida (`X-Request-ID`) hamda `events.jsonl` xavfsizlik jurnalida qayd etiladi.
  * Insident sodir bo'lganda (masalan, foydalanuvchi bloklanib qolganini da'vo qilsa yoki monitoring `LIMIT_BURST` bersa), xavfsizlik mutaxassisi ushbu `request_id` orqali aynan qaysi vaqtda (`ts`), qaysi IPdan (`ip`), qaysi foydalanuvchi nomiga (`user`) so'rov kelganini va u qanday status (`429`) olganini 100% aniqlik bilan bog'lay oladi. Bu audit va surishtiruv ishlarini bir necha barobar tezlashtiradi.

#### 14-savol: Restart hisoblagichni tozalashi va umumiy NAT qanday cheklovlarni keltirib chiqaradi?
* **Javob:**
  * **Restart muammosi:** Ushbu o'quv modelida so'rovlar hisoblagichi (`BUCKETS`) serverning operativ xotirasida (`defaultdict(deque)`) saqlanadi. Agar server o'chirib yoqilsa (restart), xotiradagi barcha hisoblagichlar nolga tenglashadi. Haqiqiy ishlab chiqarishda tajovuzkor serverni qayta yuklashga majbur qilib, barcha limitlarni aylanib o'tishi mumkin. Shuning uchun real tizimlarda limitlar markazlashtirilgan xotira keshida (masalan, **Redis** yoki **Memcached**) saqlanishi kerak.
  * **Umumiy NAT muammosi:** Katta korxona yoki o'quv yurtlarida yuzlab foydalanuvchilar bitta tashqi IP orqali chiqadi. Agar IP limiti juda qattiq qo'yilsa, qonuniy xodimlarning faoliyati to'xtab qoladi. Shu sababli ishlab chiqarishda faqat oddiy IP limitga emas, balki foydalanuvchi qurilmasining raqamli izi (Device Fingerprinting), sessiya kukilari va xatarga asoslangan adaptiv autentifikatsiya (Risk-based adaptive auth) usullariga tayaniladi.

---

# 6-BO'LIM. KENG TARQALGAN XATOLAR VA ULARNI BARTARAF ETISH (TROUBLESHOOTING)

| Muammo / Xatolik belgisi | Sababi | Qanday tuzatiladi? |
| :--- | :--- | :--- |
| **`Connection refused` yoki port band** | `app.py` ishlamayapti yoki eski jarayon portni (8011) band qilib turibdi. | 1-Terminalda `Ctrl+C` bosing. Agar fon rejimida qolgan bo'lsa: `fuser -k 8011/tcp` buyrug'i bilan portni bo'shating va `python3 -u app.py` ni qayta ishga tushiring. |
| **4-urinishda ham 401 qaytishi (429 chiqmasligi)** | `policy.json` da `rate_limit: true` qilinmagan yoki tahrirdan keyin server restart qilinmagan. | `policy.json` ni ochib `"rate_limit": true` ekanini tekshiring, so'ng 1-terminalda serverni to'xtatib qayta yoqing. |
| **Kutilganidan oldin 429 chiqishi** | 30 soniyalik oyna ichida avvalgi urinishlar qolib ketgan. | 31 soniya hech narsaga tegmasdan tinch kuting (`sleep 31`), shunda sirg'aluvchi oyna to'liq bo'shaydi. |
| **Login so'rovida `400 Bad Request` yoki `413` chiqishi** | JSON sintaksisi buzilgan, qo'shtirnoqlar tushib qolgan yoki username 24 belgidan uzun. | `curl` buyrug'idagi `-d '{"username":"...", "password":"..."}'` qismida bir tirnoq va qo'shtirnoqlar to'g'ri yozilganini tekshiring. |
| **Monitoringda alert chiqmasligi** | So'rovlar orasidagi vaqt 60 soniyadan oshib ketgan yoki boshqa log fayli ko'rsatilgan. | Test buyruqlarini tezkor ketma-ket bajaring va `python3 monitor.py after.jsonl` da to'g'ri faylni ko'rsatayotganingizga ishonch hosil qiling. |
| **`invalid_lines > 0` bo'lib qolishi** | Server ishlab turgan vaqtda log nusxalangan, natijada oxirgi JSON qatori chala yozilgan. | Jurnaldan nusxa olishdan (`cp events.jsonl after.jsonl`) oldin har doim 1-Terminalda serverni `Ctrl+C` bilan to'xtating! |
| **`Permission denied` xatoligi** | Fayl huquqlari noto'g'ri o'rnatilgan yoki `sudo` ishlatilgan. | `chmod 600 events.jsonl` qiling. Dasturlarni hech qachon `sudo` bilan ishga tushirmang. |

---

# 7-BO'LIM. FOYDALANILGAN RASMIY MANBALAR VA ADABIYOTLAR

Mavzuni yanada chuqurroq o'rganish va hisobotda ilmiy asoslash uchun xalqaro xavfsizlik standartlari hamda rasmiy manbalar:

1. **[OWASP Credential Stuffing Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html)** — Ommaviy login hujumlariga qarshi ko'p bosqichli himoya, tezlikni cheklash va botlarni aniqlash bo'yicha global tavsiyalar.
2. **[OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)** — Xavfsizlik jurnallarini to'g'ri yuritish, qanday ma'lumotlarni yozish kerakligi va qat'iyan parollar hamda shaxsiy ma'lumotlarni loglarga yozmaslik qoidalari.
3. **[OWASP Denial of Service Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html)** — Veb-resurslarni ortiqcha yuklama va sun'iy so'rovlar toshqinidan himoya qilish mezonlari.
4. **[RFC 6585 — Additional HTTP Status Codes (Section 4: 429 Too Many Requests)](https://datatracker.ietf.org/doc/html/rfc6585#section-4)** — Internet muhandislik kengashining (IETF) 429 status kodi va `Retry-After` sarlavhasi bo'yicha rasmiy standarti.
5. **[RFC 7231 — Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content (Section 7.1.3: Retry-After)](https://datatracker.ietf.org/doc/html/rfc7231#section-7.1.3)** — Server cheklovlari va qayta urinish vaqtini mijozga bildirish spetsifikatsiyasi.
6. **[Python 3 Official Documentation — http.server](https://docs.python.org/3/library/http.server.html)** — Python o'rnatilgan HTTP serverining imkoniyatlari, sinflari va xavfsizlik chegaralari.
7. **[OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)** — Foydalanuvchi parollarini xavfsiz saqlash (Argon2id, bcrypt, PBKDF2) va doimiy vaqtli taqqoslash (`compare_digest`).
8. **[NIST Special Publication 800-63B — Digital Identity Guidelines: Authentication and Lifecycle Management](https://pages.nist.gov/800-63-3/sp800-63b.html)** — AQSh Milliy Standartlar va Texnologiyalar Instituti (NIST) tomonidan tavsiya etilgan raqamli autentifikatsiya va akkauntlarni himoyalash standartlari.
