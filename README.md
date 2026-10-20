# Veb Dasturlar Xavfsizligi — Amaliy Laboratoriya Ishlari

Ushbu repozitoriy universitetning **5-semestr "Veb dasturlar xavfsizligi"** fani doirasida bajarilgan barcha amaliy tadqiqotlar, zaifliklarni modellashtirish va ularni bartaraf etish (remediation) kodlarini o‘z ichiga oladi.

Barcha laboratoriyalar **Ubuntu Live Server (VM) + Ubuntu Desctop** muhitida, toza lokal NAT tarmog‘ida hamda universitet proksisisiz (to‘g‘ridan-to‘g‘ri shaxsiy Wi-Fi tarmog‘ida) ishlab chiqilgan va sinovdan o‘tkazilgan.

---

## 📌 Qamrab olingan mavzular va laboratoriyalar

* **A1: Veb arxitekturasi va brauzer xavfsizlik modeli**
  * HTTP sarlavhalari, Same-Origin Policy (SOP), CORS mexanizmi, `HttpOnly` cookie xavfsizligi va Content Security Policy (CSP).
* **A2: Foydalanuvchi kiritmasini tekshirish va xavfsiz chiqarish**
  * Klient va server darajasidagi tekshiruvlar farqi, Unicode me’yorlashtirish (NFC), Jinja avtomatik kodlash va `nh3` yordamida HTML sanitizatsiyasi.
* **A3: Mijoz tomoni xavfsizligi (Client-side Security)**
  * DOM manipulyatsiyasi, `innerHTML` vs `textContent`, asinxron Fetch API xatoliklarini boshqarish, Web Storage (`localStorage`/`sessionStorage`) va skript yaxlitligi (SRI).
* **A4: Autentifikatsiya, sessiya va ruxsat nazorati (IDOR/BOLA)**
  * Werkzeug parollarni xeshlash (`scrypt`), xavfsiz sessiya boshqaruvi, obyekt darajasidagi ruxsat buzilishi (IDOR/BOLA) va CSRF himoyasi.
* **A5: Inyeksiya zaifliklari (Injections)**
  * SQL inyeksiyalari, ORMda xom so‘rovlar xavfi, NoSQL operator inyeksiyasi (`$ne`) va parametrlangan xavfsiz so‘rovlar.
* **A6: XSS (Reflected, Stored, DOM), CSRF va CSP integratsiyasi**
  * Manbalararo so‘rovlarni qalbakilashtirish (CSRF), XSS zanjirlari va ularni bartaraf etish strategiyalari.

---

## 📝 Xulosa (Summary)

Ushbu amaliy ishlar davomida zamonaviy veb-ilovalarda uchraydigan eng dolzarb zaifliklar (OWASP Top 10) bevosita amaliyotda tekshirildi va tahlil qilindi. 

Tadqiqotlar shuni ko‘rsatdiki:
1. **Klient tekshiruvi yetarli emas:** Brauzer darajasidagi cheklovlar (HTML atributlari, formalar) `curl` yoki tashqi so‘rovlar orqali osongina chetlab o‘tiladi; har bir parametr qat’iy ravishda server tomonida tekshirilishi va me’yorlashtirilishi shart.
2. **Kontekstga mos himoya:** XSS xavfiga qarshi faqat filtrlash emas, balki chiqish kontekstiga qarab to‘g‘ri kodlash (`textContent`, Jinja) va sanitizatsiya (`nh3`) qo‘llanilishi lozim.
3. **Rol ≠ Egalik:** Tizimda autentifikatsiya va rol nazorati (RBAC) mavjud bo‘lishi obyekt darajasidagi huquqni kafolatlamaydi (IDOR/BOLA); har bir resurs egasi so‘rov darajasida tekshirilishi talab etiladi.
4. **Chuqurlashtirilgan mudofaa (Defense-in-Depth):** Tizim xavfsizligi bitta vosita bilan cheklanmaydi — parametrlangan so‘rovlar (SQLi ga qarshi), CSP va `HttpOnly` bayroqlari (XSS oqibatlarini kamaytirish uchun), hamda CSRF tokenlari birgalikda tizimning umumiy xavfsizlik immunitetini hosil qiladi.
