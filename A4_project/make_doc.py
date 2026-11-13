import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

def create_report():
    doc = docx.Document()

    # 1. Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Helper styling functions
    def set_cell_background(cell, hex_color):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
        tcPr = cell._tc.get_or_add_tcPr()
        borders_xml = f'<w:tcBorders {nsdecls("w")}>'
        borders_xml += f'<w:top w:val="{top or "none"}" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        borders_xml += f'<w:left w:val="{left or "none"}" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        borders_xml += f'<w:bottom w:val="{bottom or "none"}" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        borders_xml += f'<w:right w:val="{right or "none"}" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        borders_xml += '</w:tcBorders>'
        tcPr.append(parse_xml(borders_xml))

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D) # Navy
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x2B, 0x54, 0x7E)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11.5)
        run.font.color.rgb = RGBColor(0x2B, 0x54, 0x7E)
        return p

    def add_p(text, bold_prefix="", italic_note=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.bold = True
            r_b.font.name = 'Times New Roman'
            r_b.font.size = Pt(10.5)
        if text:
            r_t = p.add_run(text)
            r_t.font.name = 'Times New Roman'
            r_t.font.size = Pt(10.5)
        if italic_note:
            r_i = p.add_run(italic_note)
            r_i.italic = True
            r_i.font.name = 'Times New Roman'
            r_i.font.size = Pt(10)
            r_i.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        return p

    def add_code_block(code_text):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.rows[0].cells[0]
        set_cell_background(cell, "F4F6F8")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/><w:left w:val="single" w:sz="18" w:space="0" w:color="1B365D"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/><w:right w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/></w:tcBorders>')
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.05
        run = p.add_run(code_text.strip())
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0x24, 0x29, 0x2F)
        
        # Add empty small paragraph after table for spacing
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(2)

    def add_image_with_caption(img_path, caption_text):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(2)
            run = p_img.add_run()
            run.add_picture(img_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(8)
        run_cap = p_cap.add_run(caption_text)
        run_cap.italic = True
        run_cap.bold = False
        run_cap.font.name = 'Times New Roman'
        run_cap.font.size = Pt(9.5)
        run_cap.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    def add_placeholder_box(title, instructions):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.rows[0].cells[0]
        set_cell_background(cell, "FFFBEB") # Light amber/yellow
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="dashed" w:sz="8" w:space="0" w:color="F59E0B"/><w:left w:val="single" w:sz="24" w:space="0" w:color="D97706"/><w:bottom w:val="dashed" w:sz="8" w:space="0" w:color="F59E0B"/><w:right w:val="dashed" w:sz="8" w:space="0" w:color="F59E0B"/></w:tcBorders>')
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r_t = p.add_run(f"📷 [RASM / SKRINSHOT JOYI — {title}]\n")
        r_t.bold = True
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(10.5)
        r_t.font.color.rgb = RGBColor(0xB4, 0x53, 0x09)
        
        r_inst = p.add_run(f"Talab qilinadigan skrinshot mazmuni: {instructions}")
        r_inst.italic = True
        r_inst.font.name = 'Times New Roman'
        r_inst.font.size = Pt(9.5)
        r_inst.font.color.rgb = RGBColor(0x78, 0x35, 0x0F)
        
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(2)

    # ------------------ TITUL VA METADATA ------------------
    add_title("VEB DASTURLAR XAVFSIZLIGI")
    add_subtitle("A4. Server tomoni arxitekturasi, autentifikatsiya va avtorizatsiya\n1-VARIANT — Talabalar hujjatlari portalida sessiya, rollar va obyektga kirish huquqlarini tekshirish")

    # Talaba ma'lumotlari jadvali
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Talaba (F.I.Sh.):", "Maxsudov ...................................."),
        ("Guruh / Semestr:", "507-guruh / 5-semestr (A4 / 1-variant)"),
        ("Topshirilgan sana:", "2026-yil 12-noyabr"),
        ("Baholash mezonlari:", "Jami 10 ball (Individual hisobot, P1–P4, D1–D5 dalillar va og‘zaki himoya)")
    ]
    for idx, (label, val) in enumerate(meta_data):
        c0 = tbl_meta.rows[idx].cells[0]
        c1 = tbl_meta.rows[idx].cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)
        set_cell_background(c0, "F1F5F9")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        set_cell_borders(c0, "single", "single", "single", "single")
        set_cell_borders(c1, "single", "single", "single", "single")
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(10)
        r0.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(val)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(2)

    # Mashg'ulot maqsadi qisqacha
    add_p("Talaba autentifikatsiya bilan avtorizatsiyani ajratadi; serverda parol xeshini tekshirish va sessiya yaratish jarayonini kuzatadi; talaba hamda administrator huquqlarini taqqoslaydi. Obyekt egasi tekshirilmagan holatni (BOLA/IDOR) aniqlab, kodni tuzatadi; chiqish va amal qilish muddati tugaganda sessiyaning bekor bo‘lishini tekshiradi.", bold_prefix="Mashg‘ulot maqsadi: ")
    add_p("Talaba 401 va 403 javoblarini to‘g‘ri talqin qiladi, sessiya identifikatori kirishdan keyin yangilanishini ko‘rsatadi, ruxsat matritsasini sinovlar bilan to‘ldiradi. Himoya faqat interfeysda emas, serverning har bir tegishli so‘rovida bajarilganini dalil bilan asoslaydi.", bold_prefix="Kutiladigan natija: ")

    # ------------------ 1-QISM: BAJARISH TARTIBI VA DALILLAR BO'YICHA RASMLAR ------------------
    add_h1("1-QISM. BAJARISH TARTIBI VA DALILLAR BO‘YICHA RASMLAR")

    # 0-BO'LIM
    add_h2("0-BO‘LIM. Dastlabki tayyorgarlik (VMware, proksi va muhit sozlamalari)")

    add_p("Windowsda Win+R orqali fayl serverga ulaning: \\\\172.18.233.234\\files (login: fileuser, parol: 1234567). Dasturlar papkasidan VMware-workstation-full-17.6.4.exe va Ubuntu_24.04_VM.7z arxivini lokal diskka (D:\\Veb-A4-LAB\\) nusxalang va 7-Zip orqali oching.", bold_prefix="0.1. Fayl serverga kirish va obrazni tanlash: ")
    add_placeholder_box("Fayl serverga ulanish", "Windows Explorer yoki Win+R orqali \\\\172.18.233.234\\files SMB serveriga ulanish oynasi va Dasturlar papkasidagi VMware/Ubuntu fayllari.")

    add_p("VMware'da File -> Open orqali ochilgan papkadagi .vmx faylini tanlang. VM nomini Veb-A4-LAB deb belgilang, 'I copied it' tanlang. VM sozlamalarida 4 vCPU va 8 GB RAM belgilang. Ubuntu terminalini ochib identifikatsiya buyruqlarini bajaring:", bold_prefix="0.2. VMware virtual mashinasini ochish va identifikatsiya (Dalil P1): ")
    add_code_block("sudo hostnamectl set-hostname veb-a4-lab\nwhoami\nid\nsudo -v\ndate -Is")
    add_placeholder_box("DALIL P1: Tayyor obraz va VMware nusxasi", "Ubuntu terminalida hostnamectl (veb-a4-lab), whoami, id, sudo -v va date -Is buyruqlari chiqishi ko‘ringan skrinshot.")

    add_p("VM Network Adapter sozlamasini NAT qilib, paketlarni yuklash uchun universitet proksi parametrlarini o'rnating:", bold_prefix="0.3. Vaqtinchalik NAT va universitet proksisi konfiguratsiyasi (Dalil P2 - 1-qism): ")
    add_code_block("export http_proxy=\"http://172.18.1.1:2500\"\nexport https_proxy=\"http://172.18.1.1:2500\"\nexport HTTP_PROXY=\"http://172.18.1.1:2500\"\nexport HTTPS_PROXY=\"http://172.18.1.1:2500\"\nexport no_proxy=\"localhost,127.0.0.1,::1,app.a6.test,evil.a6.test,a9.test,wrong.test\"\nexport NO_PROXY=\"$no_proxy\"\ncurl -I https://ubuntu.com")
    add_p("APT sozlamasi uchun /etc/apt/apt.conf.d/99proxy faylini yarating va tekshiring:")
    add_code_block("sudo nano /etc/apt/apt.conf.d/99proxy\n# Fayl ichiga yoziladi:\n# Acquire::http::Proxy  \"http://172.18.1.1:2500\";\n# Acquire::https::Proxy \"http://172.18.1.1:2500\";\n# Acquire::ftp::Proxy   \"http://172.18.1.1:2500\";\n\napt-config dump | grep -i proxy")
    add_placeholder_box("DALIL P2 (1-qism): Proksi va APT konfiguratsiyasi", "Terminalda export buyruqlari, curl -I https://ubuntu.com va apt-config dump | grep -i proxy chiqishi ko‘ringan skrinshot.")

    add_p("Laboratoriya uchun zarur paketlarni o'rnating, virtual muhitni (.venv) faollashtiring va Flask 3.1.3 ni o'rnating:", bold_prefix="0.4. Paketlarni o‘rnatish va versiyalarni tekshirish (Dalil P2 - 2-qism): ")
    add_code_block("sudo apt update\nsudo apt install -y python3 python3-venv python3-pip curl nano open-vm-tools open-vm-tools-desktop\nmkdir -p ~/websec/A4/templates\ncd ~/websec/A4\npython3 -m venv .venv\nsource .venv/bin/activate\npython -m pip install Flask==3.1.3\npython -m pip freeze > requirements-lock.txt\npython -m pip show Flask Werkzeug")
    add_placeholder_box("DALIL P2 (2-qism): Paket versiyalari", "pip show Flask Werkzeug buyrug‘i orqali Flask 3.1.3 va Werkzeug versiyalari hamda faol .venv ko‘ringan skrinshot.")

    add_p("Barcha paketlar yuklangach, VMni o'chiring va VM Settings -> Network Adapter sozlamasida Connected hamda Connect at power on belgilarini olib tashlang (tarmoq uziladi). VMni qayta yoqing. Brauzer va curl bitta mashina ichida 127.0.0.1 da ishlaydi.", bold_prefix="0.5. Lokal xavfsiz tajribaga o‘tish (Dalil P3): ")
    add_placeholder_box("DALIL P3: Tarmoq uzilganligi va lokal muhit", "VM Settings oynasida Network Adapter uzilgan holati (Disconnected) hamda tizimda 127.0.0.1 lokal xizmatga tayyorlik skrinshoti.")

    add_p("VM o‘chiq holatida VM -> Snapshot -> Take Snapshot orqali Veb-A4-base snapshotini yarating. So'ngra Windowsdagi D:\\Veb-A4-LAB\\Report papkasini VebA4 nomi bilan Shared Folders orqali ulang va Ubuntu ichida mount qiling:", bold_prefix="0.6. Snapshot va Shared Folders sozlash (Dalil P4): ")
    add_code_block("vmware-hgfsclient\nsudo mkdir -p /mnt/veba4share\nsudo vmhgfs-fuse .host:/VebA4 /mnt/veba4share -o allow_other,uid=$(id -u),gid=$(id -g)\ntouch /mnt/veba4share/export-check.txt")
    add_placeholder_box("DALIL P4: Snapshot va Shared Folders", "VMware Snapshot Manager oynasida Veb-A4-base ko‘rinishi hamda /mnt/veba4share papkasida export-check.txt fayli tekshirilgan skrinshot.")

    # 1-BO'LIM
    add_h2("1-BO‘LIM. Asosiy laboratoriya ishi (D1–D5 dalillar)")

    add_p("app.py va templates/index.html fayllari ~/websec/A4 papkasida yaratiladi. Sintaksis tekshirilib, ilova ishga tushiriladi:", bold_prefix="1.1. Ilovani yaratish va ishga tushirish: ")
    add_code_block("cd ~/websec/A4\nsource .venv/bin/activate\npython -m py_compile app.py\npython app.py")

    add_p("Ikkinchi terminalni ochib, tizimga kirmasdan (anonim) so'rovlar yuborib ko'riladi:", bold_prefix="1.2. Dastlabki HTTP tekshiruvi (Anonim so‘rovlar): ")
    add_code_block("a4_base=http://127.0.0.1:8004\ncurl --noproxy \"*\" -i \"$a4_base/api/me\"\ncurl --noproxy \"*\" -i \"$a4_base/api/admin\"")
    add_p("Ikkala so‘rovga ham serverdan HTTP/1.1 401 UNAUTHORIZED qaytadi. Chunki anonim so‘rovda sessiya cookie identifikatori mavjud emas.", bold_prefix="Kutilgan natija: ")
    add_image_with_caption("extracted_images/image1.png", "1-rasm. Anonim so‘rovlarga 401 Unauthorized qaytishi")

    add_p("Avval xato login/parol bilan so'rov yuboriladi: 401 Unauthorized (har doim bir xil 'Login yoki parol xato.' xabari qaytadi). So'ngra Ali nomidan to'g'ri login qilinadi va sessiya identifikatori (SID) yangilanishi kuzatiladi:", bold_prefix="1.3. Autentifikatsiya: to‘g‘ri/noto‘g‘ri kirish, CSRF va SID yangilanishi (Dalil D1): ")
    add_code_block("curl --noproxy \"*\" -s -c ali.cookies \"$a4_base/api/csrf\" > csrf.json\na4_csrf=$(python3 -c 'import json; print(json.load(open(\"csrf.json\"))[\"csrf\"])')\ncp ali.cookies anon.cookies\ncurl --noproxy \"*\" -i -b ali.cookies -c ali.cookies \\\n  -H \"X-CSRF-Token: $a4_csrf\" \\\n  --data-urlencode 'username=ali' \\\n  --data-urlencode 'password=Ali-A4-Only!' \"$a4_base/login\"\n\n# Sessiya yangilanishini tekshirish:\ncat anon.cookies\ncat ali.cookies\ncurl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/me\"\ncurl --noproxy \"*\" -i -b anon.cookies \"$a4_base/api/me\"")
    add_p("Muvaffaqiyatli login paytida eski vaqtinchalik a4_sid bekor qilinib, yangi SID yaratiladi (Session Fixation profilaktikasi). Cookie atributlari: HttpOnly=True, SameSite=Lax, Path=/, secure=False.", bold_prefix="Dalil D1 tahlili: ")
    add_image_with_caption("extracted_images/image2.png", "2-rasm. Dalil D1 — To‘g‘ri login, CSRF tekshiruvi va SID yangilanishi")
    add_image_with_caption("extracted_images/image3.png", "3-rasm. Dalil D1 (davomi) — Yangi cookie bilan 200 OK, anonim cookie bilan 401 qaytishi")

    add_p("Ali (student roli) nomidan turli resurslarga so'rov yuboriladi:", bold_prefix="1.4. Rol (RBAC) va obyekt (OBAC) darajasidagi ruxsat matritsasi (Dalil D2): ")
    add_code_block("curl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/admin\"            # -> 403 Forbidden\ncurl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/docs/101\"         # -> 200 OK (Alining o‘z hujjati)\ncurl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/docs/102\"         # -> 403 Forbidden (Valining hujjati)\ncurl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/admin?role=admin\" # -> 403 Forbidden\ncurl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/docs/999\"         # -> 404 Not Found")
    add_p("Rol nazorati (RBAC) va obyekt egasi tekshiruvi (OBAC) alohida ishlamoqda. Ali talaba bo‘lsa-da, boshqa talabaning (Valining) 102-hujjatini ocholmaydi. URLga ?role=admin qo‘shish ham server tekshiruvini chetlab o‘tolmaydi.", bold_prefix="Dalil D2 tahlili: ")
    add_image_with_caption("extracted_images/image4.png", "4-rasm. Dalil D2 — Rol va obyekt darajasidagi ruxsat matritsasi sinovlari")

    add_p("Server terminalida dasturni to'xtatib, zaiflik rejimi bilan ishga tushiramiz: python app.py --weak-authz. Ikkinchi terminalda Alining yangi loginini bajarib, Valiga tegishli 102-hujjatni so'raymiz:", bold_prefix="1.5. Boshqariladigan zaiflik sinovi: BOLA / IDOR amalda (Dalil D3): ")
    add_code_block("python app.py --weak-authz\n\n# Ikkinchi terminalda:\ncurl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/docs/102\"")
    add_p("Serverdan HTTP/1.1 200 OK va Valining o‘quv hujjati qaytadi! Bu BOLA (Broken Object Level Authorization) / IDOR zaifligining yaqqol dalilidir. Server obyekt egasini tekshirishni chetlab o‘tdi.", bold_prefix="Dalil D3 tahlili: ")
    add_image_with_caption("extracted_images/image5.png", "5-rasm. Dalil D3 — Zaif rejimda Alining 102-hujjatni noqonuniy o‘qishi (BOLA/IDOR)")

    add_p("app.py fayli tahrirlanib, zaif shart olib tashlanadi va qat'iy tekshiruv qoldiriladi:", bold_prefix="1.6. Zaiflikni kodda tuzatish va qayta sinash (Dalil D4): ")
    add_p("Eski zaif kod (app.py, document funksiyasi):")
    add_code_block("if not app.config['WEAK_AUTHZ'] and not allowed:\n    return jsonify({'error': 'Bu hujjatga ruxsat yo‘q.'}), 403")
    add_p("Tuzatilgan xavfsiz kod (app.py):")
    add_code_block("if not allowed:\n    return jsonify({'error': 'Bu hujjatga ruxsat yo‘q.'}), 403")
    add_p("Server yana ataylab python app.py --weak-authz bilan ishga tushiriladi va Ali nomidan qayta sinov o'tkaziladi:")
    add_code_block("curl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/docs/101\"   # -> 200 OK\ncurl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/docs/102\"   # -> 403 Forbidden")
    add_p("Server --weak-authz bayrog‘i bilan ishga tushgan bo‘lsa ham, koddagi chetlab o‘tish sharti olib tashlangani tufayli Valining 102-hujjati Aliga berilmadi (403 Forbidden qaytdi).", bold_prefix="Dalil D4 tahlili: ")
    add_image_with_caption("extracted_images/image6.png", "6-rasm. Dalil D4 — Kod tuzatilgach, 102-hujjatga so‘rov 403 Forbidden bilan rad etilishi")

    add_p("Alining faol cookie faylidan nusxa olinadi (replay.cookies). CSRF tokensiz logout urinishi 403 qaytaradi (sessiya saqlanadi). To'g'ri CSRF bilan logout qilingach (200 OK), saqlangan nusxa bilan qayta so'rov yuboriladi:", bold_prefix="1.7. Chiqishdan keyin eski sessiyani qayta ishlatish — Replay Attack (Dalil D5 - 1-qism): ")
    add_code_block("cp ali.cookies replay.cookies\ncurl --noproxy \"*\" -i -b replay.cookies \"$a4_base/api/me\"     # -> 200 OK (chiqishdan oldin)\n\n# To‘g‘ri logout:\ncurl --noproxy \"*\" -s -b ali.cookies -c ali.cookies \"$a4_base/api/csrf\" > csrf.json\na4_csrf=$(python3 -c 'import json; print(json.load(open(\"csrf.json\"))[\"csrf\"])')\ncurl --noproxy \"*\" -i -b ali.cookies -c ali.cookies -X POST \\\n  -H \"X-CSRF-Token: $a4_csrf\" \"$a4_base/api/logout\"               # -> 200 OK\n\n# Replay sinovi (eski cookie bilan):\ncurl --noproxy \"*\" -i -b replay.cookies \"$a4_base/api/me\"    # -> 401 Unauthorized")
    add_p("Brauzerda cookie o‘chirilmasdan saqlanib qolgan bo‘lsa ham, server xotirasidagi sessiya bekor qilingani sababli qayta kirish rad etildi (401 Unauthorized).", bold_prefix="Dalil D5 (1-qism) tahlili: ")
    add_image_with_caption("extracted_images/image7.png", "7-rasm. Dalil D5 (1-qism) — Logoutdan so‘ng eski cookie bilan replay so‘rovi 401 bilan rad etilishi")

    add_p("Server 20 soniyalik mutlaq muddat bilan yoqiladi: python app.py --ttl 20. Login qilinib darhol so'rov yuborilganda 200 OK olinadi. 22 soniya kutilgach (sleep 22) qayta so'rov yuborilganda 401 Unauthorized olinadi:", bold_prefix="1.8. Sessiya muddatini qisqa tajribada tekshirish — TTL (Dalil D5 - 2-qism): ")
    add_code_block("python app.py --ttl 20\n\n# Ikkinchi terminalda:\ncurl --noproxy \"*\" -s -c ali.cookies \"$a4_base/api/csrf\" > csrf.json\na4_csrf=$(python3 -c 'import json; print(json.load(open(\"csrf.json\"))[\"csrf\"])')\ncurl --noproxy \"*\" -s -b ali.cookies -c ali.cookies \\\n  -H \"X-CSRF-Token: $a4_csrf\" \\\n  --data-urlencode 'username=ali' \\\n  --data-urlencode 'password=Ali-A4-Only!' \"$a4_base/login\" > /dev/null\n\ncurl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/me\"     # Dastlabki soniyalarda: 200 OK\nsleep 22\ncurl --noproxy \"*\" -i -b ali.cookies \"$a4_base/api/me\"     # 22 soniyadan so‘ng: 401 Unauthorized\n\n# Tozalash:\nrm -f ali.cookies anon.cookies replay.cookies csrf.json")
    add_p("Mijozdagi cookie o‘zgarmagan bo‘lsa ham, serverdagi time.monotonic() >= record['expires'] sharti asosida sessiya muddati tugab avtomatik bekor bo‘ldi.", bold_prefix="Dalil D5 (2-qism) tahlili: ")
    add_image_with_caption("extracted_images/image8.png", "8-rasm. Dalil D5 (2-qism) — 20 soniya o‘tgach sessiyaning avtomatik bekor bo‘lishi (TTL)")

    # ------------------ 2-QISM: QO'SHIMCHA TALABLAR ------------------
    add_h1("2-QISM. QO‘SHIMCHA TALABLAR")

    # 2.1 NATIJALAR JADVALI
    add_h2("2.1. Topshiriqlar va natijalar jadvali (13 ta tekshiruv)")

    results_data = [
        ("№", "Tekshiruv sharti", "Kutiladigan natija", "Amaldagi natija va dalil"),
        ("1", "Cookie yo‘q: /api/me", "401", "401 Unauthorized (error: Avval tizimga kiring.) [1-rasm]"),
        ("2", "Mavjud/noma’lum login, xato parol", "401; bir xil xabar", "401 Unauthorized (error: Login yoki parol xato.) — Enumeration himoyasi"),
        ("3", "To‘g‘ri login (ali / Ali-A4-Only!)", "200; SID yangilanadi", "200 OK — a4_sid yangilandi (Dalil D1) [2-rasm]"),
        ("4", "Cookie atributlari (a4_sid)", "HttpOnly; SameSite=Lax", "HttpOnly=True, SameSite=Lax, Path=/, secure=False (Dalil D1)"),
        ("5", "Ali → /api/admin?role=admin", "403", "403 Forbidden (error: Administrator huquqi kerak.) (Dalil D2) [4-rasm]"),
        ("6", "Ali → 101 / 102; xavfsiz rejim", "200 / 403", "101: 200 OK (o‘z hujjati), 102: 403 Forbidden (Valining hujjati) (Dalil D2)"),
        ("7", "Vali → 101 / 102; xavfsiz rejim", "403 / 200", "101: 403 Forbidden, 102: 200 OK — Har bir talaba faqat o‘z hujjatiga ega"),
        ("8", "Admin → 101 / 102 / admin", "200 / 200 / 200", "Barchasiga 200 OK — Administrator to‘liq huquqqa ega"),
        ("9", "Ali → 102; zaif rejim (--weak-authz)", "200 — zaiflik dalili", "200 OK (Valining oquv hujjati) — BOLA / IDOR isbotlandi (Dalil D3) [5-rasm]"),
        ("10", "Ali → 102; kod tuzatilgan", "403; o‘z hujjati 200", "102: 403 Forbidden, 101: 200 OK — IDOR bartaraf etildi (Dalil D4) [6-rasm]"),
        ("11", "CSRFsiz logout so‘rovi", "403; sessiya saqlanadi", "403 Forbidden (error: CSRF tekshiruvi bajarilmadi.) — Sessiya faol qoldi"),
        ("12", "To‘g‘ri logout; eski cookie replay", "200; keyingi /me 401", "Logout: 200 OK, Replay /me: 401 Unauthorized (Dalil D5) [7-rasm]"),
        ("13", "20 soniyalik sessiya tugashi (--ttl 20)", "/me: avval 200, keyin 401", "Dastlab 200 OK, sleep 22 dan so‘ng 401 Unauthorized (Dalil D5) [8-rasm]")
    ]

    tbl_res = doc.add_table(rows=len(results_data), cols=4)
    tbl_res.alignment = WD_TABLE_ALIGNMENT.CENTER

    col_widths = [Inches(0.4), Inches(2.3), Inches(1.8), Inches(2.5)]

    for r_idx, row in enumerate(results_data):
        for c_idx, val in enumerate(row):
            cell = tbl_res.rows[r_idx].cells[c_idx]
            cell.width = col_widths[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            set_cell_borders(cell, "single", "single", "single", "single")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            
            if r_idx == 0:
                set_cell_background(cell, "1B365D")
                run = p.add_run(val)
                run.bold = True
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "FFFFFF")
                else:
                    set_cell_background(cell, "F8FAFC")
                run = p.add_run(val)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9)
                if c_idx == 0:
                    run.bold = True
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(2)
    p_sp.paragraph_format.space_after = Pt(4)

    # 2.2 TAHLILIY VAZIFALAR
    add_h2("2.2. Tahliliy savollarga javoblar")

    add_p("Kodda ruxsat tekshiruvi: allowed = (user['role'] == 'admin') or (doc['owner'] == user['username']). Student roli tizimda faqat foydalanuvchining toifasini bildiradi, biroq aynan qaysi hujjatga egalik qilishini belgilamaydi. Agar faqat student roli tekshirilsa, tizimdagi istalgan talaba boshqa barcha talabalarning shaxsiy ma'lumotlarini o'qiy oladi (BOLA/IDOR zaifligi). Shuning uchun obyekt darajasida (OBAC) har bir hujjatning egasi (doc['owner']) joriy sessiya egasi bilan qat'iy solishtirilishi shart.", bold_prefix="1-savol: Ruxsat matritsasidan kamida ikki qarorni kod sharti bilan bog‘lang. Nega student roli obyektga egalikni anglatmaydi?\nJavob: ")

    add_p("• 401 Unauthorized — Foydalanuvchi tizimga kirmagan (autentifikatsiyadan o'tmagan). Misol: Anonim holatda /api/me so'ralganda server 'Avval tizimga kiring' xabari bilan 401 qaytaradi.\n• 403 Forbidden — Foydalanuvchi tizimga kirgan, lekin so'ralgan resursga yoki amalga vakolati yo'q (avtorizatsiyadan o'tmadi). Misol: Ali talaba bo'lgani holda /api/admin yoki Valining 102-hujjatini (/api/docs/102) so'raganda server 403 qaytaradi.\n• 404 Not Found — Resurs bazada umuman mavjud emas. Misol: Ali /api/docs/999 so'raganda, baza ichida 999 identifikatorli hujjat yo'qligi sababli server 404 qaytaradi.", bold_prefix="2-savol: 401, 403 va 404 javoblarining ushbu API uchun ma’nosini bittadan misol bilan keltiring:\nJavob: ")

    add_p("• SID (Session ID) — Faol sessiyani ifodalovchi tasodifiy kriptografik identifikator. Brauzerda cookie (a4_sid) ichida saqlanadi; serverda esa SESSIONS xotira lug'atida saqlanadi.\n• CSRF token — Saytlararo so'rov soxtalashtirishdan himoyalovchi bir martalik tasodifiy token. Brauzerda mijoz tomonidan JSON sarlavhasida (X-CSRF-Token) yuboriladi; serverda sessiya yozuvi bilan birga saqlanadi va POST so'rovlarida solishtiriladi.\n• Parol xeshi — Foydalanuvchi parolini himoyalash uchun tuz (salt) qo'shilgan scrypt xeshi. Faqat serverda (USERS ro'yxatida) saqlanadi; brauzerga hech qachon yuborilmaydi va ochiq parol serverda saqlanmaydi.", bold_prefix="3-savol: SID, CSRF token va parol xeshining vazifalari va saqlanish joylari:\nJavob: ")

    add_p("Logout so'rovi bajarilganda brauzerga Set-Cookie: a4_sid=; Max-Age=0 sarlavhasi yuboriladi va brauzerdagi cookie avtomatik o'chiriladi. Replay attack tajribasining asl maqsadi — qonuniy foydalanuvchi tizimda faol paytida begona shaxs tomonidan o'g'irlangan yoki saqlab qolingan faol cookie nusxasini foydalanuvchi tizimdan chiqqandan (logout qilgandan) so'ng qayta ishlatganda server uni qabul qilmasligini (chunki server o'z SESSIONS jadvalidan yozuvni o'chirgan) isbotlashdir. Agar nusxa logoutdan keyin olinsa, u allaqachon bo'sh yoki yaroqsiz bo'ladi.", bold_prefix="4-savol: Cookie replay tajribasida nega cookie nusxasini logoutdan oldin olish kerak?\nJavob: ")

    # 2.3 XULOSA
    add_h2("2.3. Xulosa (5–7 gapdan iborat shaxsiy kuzatuv)")
    xulosa_text = (
        "1. Ushbu laboratoriya mashg‘ulotida veb-ilovalarning server tomoni (Backend) arxitekturasi, foydalanuvchini tanish (autentifikatsiya) va ularning huquqlarini tekshirish (avtorizatsiya) jarayonlari amalda tahlil qilindi. "
        "2. Parollar xavfsiz scrypt xeshi va tuzi (salt) bilan saqlanishi hamda sessiya fiksatsiyasining oldini olish uchun har bir muvaffaqiyatli kirishda yangi SID yaratilishi tajribada isbotlandi. "
        "3. Server kodidagi WEAK_AUTHZ sharti tufayli yuzaga kelgan BOLA / IDOR zaifligi amalda aniqlanib, Ali foydalanuvchisi Valiga tegishli 102-hujjatni noqonuniy qo‘lga kiritish holati ko‘rsatildi. "
        "4. Aniqlangan zaiflik app.py kodida obyektga egalik shartini (if not allowed:) qat’iy tekshirish orqali bartaraf etildi va qayta sinovda boshqa talabaning hujjatiga kirish 403 Forbidden bilan to‘liq to‘sildi. "
        "5. Tizimdan chiqish (logout) jarayonida sessiya identifikatori server xotirasidan o‘chirilishi sababli Replay hujumi muvaffaqiyatsiz bo‘lishi va 20 soniyalik muddat (TTL) o‘tgach sessiya avtomatik bekor bo‘lishi tasdiqlandi. "
        "6. Laboratoriya muhitidagi in-memory sessiyalar server qayta yuklanganda yo‘qolishi sababli, ishlab chiqarish tizimlarida doimiy ma’lumotlar bazasi, Redis kesh va HTTPS (Secure cookie) joriy etilishi tavsiya etiladi."
    )
    add_p(xulosa_text)

    # 2.4 HIMOYA SAVOLLARI
    add_h2("2.4. Himoya savollari va javoblari")

    add_p("Chunki to‘g‘ri parol faqat foydalanuvchining shaxsini tasdiqlaydi (autentifikatsiya), biroq uning muayyan obyektga (boshqa talabaning shaxsiy hujjatiga) kirish vakolatini (avtorizatsiyani) bermaydi. Har bir so‘rovda server obyekt egasini alohida tekshirishi shart.", bold_prefix="1. To‘g‘ri parol nima uchun boshqa foydalanuvchi hujjatini ochishga yetmaydi?\nJavob: ")

    add_p("Sessiya fiksatsiyasi (Session Fixation) xurujining oldini oladi. Agar hujumchi qurbonga oldindan ma’lum sessiya identifikatorini berib qo‘ygan bo‘lsa ham, login muvaffaqiyatli bo‘lganda server eski SIDni yo‘q qilib, yangi tasodifiy SID beradi va hujumchining identifikatori yaroqsiz bo‘lib qoladi.", bold_prefix="2. Login paytida SIDni almashtirish qaysi xavfni kamaytiradi?\nJavob: ")

    add_p("Ha, albatta qo‘shiladi. HttpOnly atributi mijoz tomonidagi skriptlarga (JavaScript / document.cookie) cookieni o‘qishni taqiqlaydi (XSSdan himoya). Ammo brauzer serverga har qanday HTTP so‘rov yuborganida Cookie sarlavhasida ushbu cookieni avtomatik ravishda qo‘shib jo‘natadi.", bold_prefix="3. HttpOnly bo‘lsa ham brauzer so‘roviga cookie qo‘shiladimi?\nJavob: ")

    add_p("Agar faqat brauzerdagi cookie o‘chirilsa, server xotirasidagi sessiya yozuvi o‘chmay qoladi va agar hujumchi cookieni nusxalab olgan bo‘lsa, uni qayta ishlatishi (Replay attack) mumkin bo‘ladi. Server sessiyasini bekor qilish esa cookieni server tomonida mutlaqo yaroqsiz qiladi.", bold_prefix="4. Logoutda faqat cookie o‘chirish bilan server sessiyasini o‘chirish farqi nima?\nJavob: ")

    add_p("Ha, 100% kerak bo‘ladi. JWT faqat foydalanuvchi shaxsi va uning umumiy rollarini ifodalovchi formatdir. JWT tokeni ichida obyekt darajasidagi egalik avtomatik kafolatlanmaydi; server har bir so‘rov kelganda tokendagi foydalanuvchi bilan so‘ralayotgan obyekt egasini baribir tekshirishi shart.", bold_prefix="5. JWT ishlatilsa obyekt darajasidagi ruxsat tekshiruvi kerak bo‘ladimi?\nJavob: ")

    # 2.5 KENGAYTIRISH YO'NALISHLARI
    add_h2("2.5. Kengaytirish yo‘nalishlari (Taqqosiy tahlil)")

    tech_data = [
        ("Texnologiya", "Vazifasi va laboratoriya mavzusi bilan bog‘lanishi"),
        ("OAuth 2.0", "Uchinchi tomon ilovalariga foydalanuvchi resurslariga cheklangan vakolat berish tizimi (Delegated Authorization); o‘z-o‘zicha login protokoli emas."),
        ("OpenID Connect", "OAuth 2.0 ustiga qurilgan shaxsni tasdiqlash (autentifikatsiya) qatlami; tashqi provayder (masalan Google, GitHub) orqali yagona kirishni (SSO) ta'minlaydi."),
        ("JWT (JSON Web Token)", "Foydalanuvchi ma'lumotlarini (claim) raqamli imzo bilan ifodalovchi token formati; stateless arxitekturaga mos, lekin obyektga egalikni server alohida tekshirishi shart."),
        ("MFA (Ko‘p omilli autentifikatsiya)", "Turli toifadagi (biladigan narsa: parol, ega bo‘lgan narsa: OTP/token, o‘zi bo‘lgan narsa: biometrika) omillarni birgalikda qo‘llash orqali kirish xavfsizligini oshirish."),
        ("WebAuthn / Passkeys", "Ochiq kalitli kriptografiya asosida parolsiz autentifikatsiya; domen (origin) bilan bog‘langan credentiallardan foydalanadi, fishingga chidamli.")
    ]

    tbl_tech = doc.add_table(rows=len(tech_data), cols=2)
    tbl_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, (t_name, t_desc) in enumerate(tech_data):
        c0 = tbl_tech.rows[r_idx].cells[0]
        c1 = tbl_tech.rows[r_idx].cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.8)
        set_cell_margins(c0, 60, 60, 80, 80)
        set_cell_margins(c1, 60, 60, 80, 80)
        set_cell_borders(c0, "single", "single", "single", "single")
        set_cell_borders(c1, "single", "single", "single", "single")
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        
        if r_idx == 0:
            set_cell_background(c0, "1B365D")
            set_cell_background(c1, "1B365D")
            r0 = p0.add_run(t_name)
            r0.bold = True
            r0.font.name = 'Times New Roman'
            r0.font.size = Pt(9.5)
            r0.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
            r1 = p1.add_run(t_desc)
            r1.bold = True
            r1.font.name = 'Times New Roman'
            r1.font.size = Pt(9.5)
            r1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        else:
            if r_idx % 2 == 1:
                set_cell_background(c0, "FFFFFF")
                set_cell_background(c1, "FFFFFF")
            else:
                set_cell_background(c0, "F8FAFC")
                set_cell_background(c1, "F8FAFC")
            r0 = p0.add_run(t_name)
            r0.bold = True
            r0.font.name = 'Times New Roman'
            r0.font.size = Pt(9)
            
            r1 = p1.add_run(t_desc)
            r1.font.name = 'Times New Roman'
            r1.font.size = Pt(9)

    # Save document
    doc.save("A4_hisobot.docx")
    print("A4_hisobot.docx successfully created and saved!")

if __name__ == '__main__':
    create_report()
