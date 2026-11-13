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


sen turgan faylda VDX_A12_1_variant_batafsil.pdf nomli pdf fayl bor, shu fayl
  ichini tahlil
    qilib menga, oldin shu takitlashim kerak,
  *men universitetmni wifi dan emas o'zimni lokal wifi dan foydalanaman, shu
  sababli description.md fayli to'g'ri tahrirla
  *agar zarur bo'lsa men hozirda ubuntu ichida vmware yordamida bu ishlarni
  bajaraman, shu sababli description.md ichiga xato yozma(windows emas,
  ubuntu!!), windowsda
  emas ubuntu->vmware-> nechtadir ubuntu server da ish qilishim kerak bo'ladi,
  *agarda mashqlarni bajarishda windows 11 zarur bo'lsa meni VMware ichida
  ubuntu server qiladigan ish bo'lmasa windows11 desctop ni set up qilib
  qo'yganman, mashq bajarishda kerak bo'lsa shu OS dan foydalansak bo'ladi!!!
  
    1*mavzuni maqsadini tushuntir,
    2*ichidagi har bir
    mazvularni to'liq qo'llanma tayyorla,
    3* mashqni bajarish bo'yicha ketma-ket tushuntir +(keyin har bir cli
  komanda nima ish qilishini ham tushuntirib, nima vazifa qilayotganini
  tushunishim kerak!!),
    4*yakunida shu mavzuga doir manbalar berib o't,
  
  hamma malumotlarni bitda qilib "description.md" fayliga joyla!!!!



"/home/maxfull/Downloads/507-LAB/projects/web-application-security-labs/A1_pr
  oject/A1_hisobot.docx"
  shu fayldagi men oldin tayyorlagan hisobotni ko'rib chi va ustozni bergan
  vazifasiga mos
  kelami/home/maxfull/Downloads/507-LAB/projects/web-application-security-labs/
  A1_project/A3_Veb_dasturlar_xavfsizligi_VMware_proxy.pdf)?
  agar kamchiligi bor bo'lsa yani qanday screen shot kamchilik qilyapdi? agar
  hech qanday rasm bo'yicha kamchilik bo'lmasa qayta tahrirlar ustoz so'ragan
  talablarni 100% bajarilsin
  
lekin ortiqcha malumot kerak emas faqat:
    1*bajarish tartibi 2*dalil bo'yicha rasm 3*qo'shimcha talablar, bo'lsa
    yetarli mavzu haqida nazarya shart emas!!

men senga barcha ubuntu serverda ishlangan vazifalarni dalil rasmlarini
    bitda papkaga(images) raqamlab tashlab bersam sen menga faqat amaliy
  qismini
    qanday bajargani haqida ketma ket(sodda ko'rinishda) hisobot.docx formatda
  hisobot
    taxlab bersang(amallarni o'zim mustaqil bajarib rasmlar yig'aman sen fayl
    taxlaysan) va asosiysi A7_Veb_dasturlar_xavfsizligi_VMware_proxy" pdfdagi
    Asosiy amaliy mashg'ulot bo'limidagi 1.7, +qo'shimcha topshiriq:xavsiz
  ma'lumot tiklash, +nazorat
    savollari, +foydalanilgan rasmiy manbalar va 1.8 baholash mezomlarini 100%
  to'liq qoniqtirgan bo'lishi kerak.
    shu amallarni to'liq qilish uchun senga qanday vazifani mustaqil bajarishim
    va har bir rasmni qanday tartibda nomerlab ketishim ketak bo'ladi  sen
  menga
    bermoqchi bo'lgan talablarni bitda talab.md fayliga yoz keyin men shunga
    qarab amalni bajaraman va rasmlarni yig'ib senga beraman
