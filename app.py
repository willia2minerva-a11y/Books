import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import random
import time

# --- إعدادات الواجهة ---
st.set_page_config(page_title="KDP Empire Builder", page_icon="💰", layout="centered")

# --- جلب المتغيرات ---
api_keys = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2"), os.getenv("GEMINI_API_KEY_3")]
valid_keys = [k.strip() for k in api_keys if k and k.strip() != ""]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- محرك الذكاء الاصطناعي المدرع ---
def ask_gemini(prompt_text):
    models = ['gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-1.0-pro']
    last_err = ""
    for key in valid_keys:
        genai.configure(api_key=key)
        for model in models:
            try:
                m = genai.GenerativeModel(model)
                res = m.generate_content(prompt_text)
                if res.text: return res.text
            except Exception as e:
                last_err = str(e)
                continue
    raise Exception(f"فشلت المحاولات. آخر خطأ: {last_err}")

# --- خوارزميات الأنشطة المربحة (Logic Based) ---

def draw_math_page(pdf, page_num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 1, f"Math Practice - Page {page_num}", align="C", ln=True)
    pdf.set_font("Arial", "", 18)
    pdf.ln(0.5)
    for i in range(8): # 8 عمليات في الصفحة
        num1 = random.randint(10, 99)
        num2 = random.randint(1, 10)
        op = random.choice(['+', '-', 'x'])
        pdf.cell(0, 0.8, f"{i+1})  {num1}  {op}  {num2}  =  _______", ln=True, align="C")

def draw_comic_panels(pdf, page_num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 0.5, f"Create Your Comic - Page {page_num}", align="C", ln=True)
    pdf.set_line_width(0.03)
    layouts = [
        [(0.75, 1.5, 3.5, 4), (4.25, 1.5, 3.5, 4), (0.75, 5.75, 7, 4)], # Layout 1
        [(0.75, 1.5, 7, 3), (0.75, 4.75, 7, 3), (0.75, 8, 7, 2.5)]      # Layout 2
    ]
    selected = random.choice(layouts)
    for x, y, w, h in selected:
        pdf.rect(x, y, w, h)

def generate_sudoku():
    base = 3; side = base*base
    rBase = range(base)
    rows = [g*base + r for g in random.sample(rBase,base) for r in random.sample(rBase,base)]
    cols = [g*base + c for g in random.sample(rBase,base) for c in random.sample(rBase,base)]
    nums = random.sample(range(1,side+1),side)
    board = [[nums[(base*(r%base)+r//base+c)%side] for c in cols] for r in rows]
    for p in random.sample(range(side*side), side*side*2//3): board[p//side][p%side] = 0
    return board

def draw_sudoku_page(pdf, board, num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 20); pdf.cell(0, 1, f"Sudoku Challenge #{num}", align="C", ln=True)
    start_x, start_y, cs = 1.25, 2.5, 0.66
    for r in range(9):
        for c in range(9):
            pdf.set_line_width(0.05 if (r%3==0 or c%3==0) else 0.01)
            pdf.rect(start_x+c*cs, start_y+r*cs, cs, cs)
            if board[r][c] != 0: pdf.text(start_x+c*cs+0.25, start_y+r*cs+0.45, str(board[r][c]))

# --- محرك النشر الآلي (Metadata + PDF) ---

def create_full_package(theme, book_type, pages, status):
    pdf = FPDF(unit="in", format=(8.5, 11))
    pdf.set_auto_page_break(0)
    
    # 1. الغلاف
    status.text(f"🎨 جاري تصميم الغلاف لـ {theme}...")
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(f'kids book cover, {theme}, vibrant')}?width=816&height=1056&nologo=true"
        with open("c.jpg", "wb") as f: f.write(requests.get(url, timeout=20).content)
        pdf.add_page(); pdf.image("c.jpg", x=0, y=0, w=8.5, h=11); os.remove("c.jpg")
    except: pass

    # 2. العنوان والأنشطة
    pdf.add_page(); pdf.set_font("Arial", "B", 30); pdf.set_y(4)
    pdf.cell(0, 1, f"The Big Book of {theme}", align="C", ln=True)

    # توزيع المحتوى بالتساوي
    per_type = pages // 4
    
    # - التلوين
    status.text("🧠 توليد أوامر التلوين...")
    p_raw = ask_gemini(f"List {per_type} coloring prompts for {theme}. Bold lines, white bg. One per line.")
    for i, p in enumerate(p_raw.split('\n')[:per_type]):
        try:
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true&seed={i}"
            with open("t.jpg", "wb") as f: f.write(requests.get(img_url, timeout=20).content)
            pdf.add_page(); pdf.image("t.jpg", x=0.75, y=1.5, w=7, h=7); pdf.add_page(); os.remove("t.jpg")
        except: continue

    # - الرياضيات
    status.text("🔢 توليد صفحات الرياضيات...")
    for i in range(per_type): draw_math_page(pdf, i+1)

    # - الكوميكس
    status.text("📝 رسم قوالب الكوميكس...")
    for i in range(per_type): draw_comic_panels(pdf, i+1)

    # - السودوكو
    status.text("🧩 توليد السودوكو...")
    for i in range(per_type): draw_sudoku_page(pdf, generate_sudoku(), i+1)

    fname = f"KDP_PRO_{int(time.time())}.pdf"
    pdf.output(fname)
    
    # 3. SEO Metadata
    status.text("📝 توليد بيانات النشر (SEO)...")
    meta = ask_gemini(f"Create KDP Metadata for {theme} activity book. Include Title, Subtitle, 7 Keywords, and Description.")
    
    # 4. تليجرام
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        status.text("✈️ إرسال الحزمة كاملة لتليجرام...")
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ كتاب {theme} جاهز!"}, files={"document": open(fname, "rb")})
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": meta})

    return fname, meta

# --- التشغيل الذكي ---
is_auto = st.query_params.get("auto") == "true"
status = st.empty()

if is_auto:
    st.warning("🤖 البوت يعمل الآن بشكل مستقل...")
    if not valid_keys: st.stop()
    theme = ask_gemini("Pick one very profitable KDP niche (one phrase).").strip()
    create_full_package(theme, "الكل", 40, status)
    st.success("✅ تم النشر بنجاح!")
else:
    st.title("💰 مصنع الأرباح: KDP Auto-Elite")
    u_theme = st.text_input("موضوع الكتاب:", "Ocean Adventures")
    u_pages = st.slider("عدد الصفحات:", 10, 80, 40)
    if st.button("🚀 ابدأ الإنتاج الشامل"):
        f, m = create_full_package(u_theme, "الكل", u_pages, status)
        st.success("تفقد التليجرام الخاص بك!")
        st.info(m)

