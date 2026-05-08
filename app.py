import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import random
import time
import traceback
import string

# --- إعدادات الواجهة ---
st.set_page_config(page_title="KDP Auto-Empire", page_icon="👑", layout="centered")

# --- جلب المتغيرات وتأمينها ---
api_keys = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2"), os.getenv("GEMINI_API_KEY_3")]
valid_keys = [k.strip() for k in api_keys if k and k.strip() != ""]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- محرك الذكاء الاصطناعي (محدث لـ 2.5-flash) ---
def ask_gemini(prompt_text):
    models = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    last_err = ""
    for key in valid_keys:
        genai.configure(api_key=key)
        for model in models:
            try:
                m = genai.GenerativeModel(model)
                res = m.generate_content(prompt_text)
                if res.text: return res.text
            except Exception as e:
                last_err = f"[{model}]: {str(e)}"
                continue
    raise Exception(f"تعطل المحرك. آخر خطأ: {last_err}")

# --- خوارزميات الأنشطة المربحة (100% كود بايثون بدون أخطاء صور) ---

def draw_math_page(pdf, page_num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 22)
    pdf.cell(0, 1, f"Math Master - Page {page_num}", align="C", ln=True)
    pdf.set_font("Arial", "", 20)
    pdf.ln(0.5)
    for i in range(8):
        num1 = random.randint(10, 99)
        num2 = random.randint(1, 10)
        op = random.choice(['+', '-', 'x'])
        pdf.cell(0, 0.9, f"{i+1})    {num1}  {op}  {num2}  =  _______", ln=True, align="C")

def draw_word_search_page(pdf, theme, page_num):
    # توليد كلمات متعلقة بالثيم
    try:
        words_raw = ask_gemini(f"Give me exactly 6 simple English words related to '{theme}' for kids. Return ONLY the words separated by commas. No spaces, uppercase.").upper()
        words = [w.strip() for w in words_raw.replace('\n', '').split(',')]
        words = [w for w in words if w.isalpha() and 3 <= len(w) <= 8][:6]
        if len(words) < 6: words = ["SUN", "STAR", "MOON", "SKY", "SPACE", "PLANET"]
    except:
        words = ["APPLE", "BANANA", "CHERRY", "GRAPE", "MANGO", "PEACH"]

    grid_size = 10
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    
    # وضع الكلمات في الشبكة أفقياً وعمودياً
    for w in words:
        for _ in range(50): # محاولات التموضع
            direction = random.choice([(0,1), (1,0)]) # (أفقي، عمودي)
            r = random.randint(0, grid_size - 1 - (len(w)-1)*direction[0])
            c = random.randint(0, grid_size - 1 - (len(w)-1)*direction[1])
            
            overlap = False
            for i in range(len(w)):
                if grid[r+i*direction[0]][c+i*direction[1]] not in (' ', w[i]):
                    overlap = True; break
            if not overlap:
                for i in range(len(w)):
                    grid[r+i*direction[0]][c+i*direction[1]] = w[i]
                break
                
    # ملء الفراغات بحروف عشوائية
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c] == ' ': grid[r][c] = random.choice(string.ascii_uppercase)

    pdf.add_page()
    pdf.set_font("Arial", "B", 22)
    pdf.cell(0, 1, f"Word Search - Page {page_num}", align="C", ln=True)
    pdf.set_font("Arial", "B", 24)
    start_x, start_y, cell_size = 1.75, 2.5, 0.5
    for r in range(grid_size):
        for c in range(grid_size):
            pdf.text(start_x + c*cell_size, start_y + r*cell_size, grid[r][c])
            
    pdf.set_font("Arial", "", 16)
    pdf.set_y(8.0)
    pdf.cell(0, 0.5, "Find these words:", align="C", ln=True)
    pdf.cell(0, 0.5, " - ".join(words), align="C", ln=True)

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
    pdf.set_font("Arial", "B", 22); pdf.cell(0, 1, f"Sudoku Challenge #{num}", align="C", ln=True)
    start_x, start_y, cs = 1.25, 2.5, 0.66
    for r in range(9):
        for c in range(9):
            pdf.set_line_width(0.05 if (r%3==0 or c%3==0) else 0.01)
            pdf.rect(start_x+c*cs, start_y+r*cs, cs, cs)
            if board[r][c] != 0: 
                pdf.set_font("Arial", "B", 20)
                pdf.text(start_x+c*cs+0.25, start_y+r*cs+0.45, str(board[r][c]))

def draw_comic_panels(pdf, page_num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 20); pdf.cell(0, 1, f"Draw Your Story - Page {page_num}", align="C", ln=True)
    pdf.set_line_width(0.04)
    layouts = [
        [(0.75, 2.0, 3.3, 3), (4.45, 2.0, 3.3, 3), (0.75, 5.5, 7, 4)],
        [(0.75, 2.0, 7, 3.5), (0.75, 6.0, 3.3, 3.5), (4.45, 6.0, 3.3, 3.5)]
    ]
    for x, y, w, h in random.choice(layouts): pdf.rect(x, y, w, h)

# --- محرك النشر الآلي المتكامل ---
def create_full_package(theme, book_type, pages, status):
    pdf = FPDF(unit="in", format=(8.5, 11))
    pdf.set_auto_page_break(0)
    
    # 1. الغلاف (تم تحسين البرومبت ليكون كرتونياً وجذاباً بدون أخطاء)
    status.text(f"🎨 جاري رسم الغلاف الاحترافي لـ {theme}...")
    try:
        cover_prompt = f"beautiful children activity book cover design, {theme}, cute cartoon style, highly detailed, vibrant bright colors, masterpiece, blank background no text"
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(cover_prompt)}?width=816&height=1056&nologo=true"
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            with open("c.jpg", "wb") as f: f.write(resp.content)
            pdf.add_page(); pdf.image("c.jpg", x=0, y=0, w=8.5, h=11); os.remove("c.jpg")
    except: pass

    # 2. العنوان
    pdf.add_page(); pdf.set_font("Arial", "B", 36); pdf.set_y(4)
    pdf.cell(0, 1, f"The BIG Book of", align="C", ln=True)
    pdf.cell(0, 1, f"{theme.upper()}", align="C", ln=True)

    # حساب توزيع الصفحات
    types_count = 5 if book_type == "منوع (الكل)" else 1
    per_type = max(1, pages // types_count)
    
    # --- التلوين (تم حل مشكلة الصفحات البيضاء) ---
    if book_type in ["منوع (الكل)", "تلوين فقط"]:
        status.text(f"🧠 توليد {per_type} صفحات تلوين...")
        # نجبر غيميني على إعطاء أسماء أشياء فقط (مثلاً: رائد فضاء، قرد، سفينة)
        subjects = ask_gemini(f"Give me {per_type} simple single subjects related to {theme} for a kid to color. Example: a cute alien. Return one per line, no numbering.").split('\n')
        
        for i, sub in enumerate(subjects[:per_type]):
            if not sub.strip(): continue
            status.text(f"🖌️ رسم وتنزيل الصفحة {i+1}...")
            try:
                # البرومبت السحري للتلوين الصافي (Line art)
                safe_prompt = f"black and white line art coloring page for kids, {sub.strip()}, thick clean black outlines, blank white background, simple vector, uncolored, no shading"
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(safe_prompt)}?width=1024&height=1024&nologo=true&seed={random.randint(1,999)}"
                img_resp = requests.get(img_url, timeout=20)
                if img_resp.status_code == 200 and len(img_resp.content) > 10000: # تجنب الصور التالفة
                    with open("t.jpg", "wb") as f: f.write(img_resp.content)
                    pdf.add_page(); pdf.image("t.jpg", x=0.75, y=1.5, w=7, h=7); pdf.add_page() # صفحة الحماية
                    os.remove("t.jpg")
                time.sleep(1)
            except Exception as e: print(f"Skipped image {i}: {e}")

    # --- الرياضيات ---
    if book_type in ["منوع (الكل)", "رياضيات فقط"]:
        status.text("🔢 توليد أوراق عمل الرياضيات...")
        for i in range(per_type): draw_math_page(pdf, i+1)

    # --- البحث عن الكلمات ---
    if book_type in ["منوع (الكل)", "البحث عن الكلمات"]:
        status.text("🔍 بناء شبكات البحث عن الكلمات...")
        for i in range(per_type): draw_word_search_page(pdf, theme, i+1)

    # --- الكوميكس ---
    if book_type in ["منوع (الكل)", "كوميكس فقط"]:
        status.text("📝 رسم قوالب الكوميكس الفارغة...")
        for i in range(per_type): draw_comic_panels(pdf, i+1)

    # --- السودوكو ---
    if book_type in ["منوع (الكل)", "سودوكو فقط"]:
        status.text("🧩 حل وتوليد ألغاز السودوكو...")
        for i in range(per_type): draw_sudoku_page(pdf, generate_sudoku(), i+1)

    fname = f"KDP_{theme.replace(' ', '_')}_{int(time.time())}.pdf"
    pdf.output(fname)
    
    # 3. SEO Metadata
    status.text("📝 كتابة وصف احترافي للبيع (SEO)...")
    try: 
        meta = ask_gemini(f"Act as Amazon KDP expert. Write highly converting listing for a kids activity book. Theme: {theme}. Type: {book_type}. Pages: {pages}. Include: Catchy Title, Subtitle, 7 Backend Search Keywords (comma separated), and a short persuasive Description with bullet points.")
    except: 
        meta = "حدث خطأ في توليد الوصف. يمكنك استخدام بيانات عامة."
    
    # 4. تليجرام
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        status.text("✈️ إرسال الطرد لتليجرام...")
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ مبروك! كتاب {theme} جاهز للرفع."}, files={"document": open(fname, "rb")}, timeout=40)
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": meta}, timeout=20)
        except Exception as e: print(f"Telegram error: {e}")

    return fname, meta

# --- واجهة المستخدم والتشغيل ---
is_auto = st.query_params.get("auto") == "true"
status = st.empty()

if is_auto:
    st.warning("🤖 الوضع الآلي (المخفي) يعمل الآن...")
    if not valid_keys: st.stop()
    try:
        theme = ask_gemini("Suggest ONE highly profitable, low-competition KDP niche for kids activity books (e.g. Space Dinosaurs). Just the exact phrase.").strip()
        create_full_package(theme, "منوع (الكل)", 50, status)
        st.success("✅ تم الإنتاج والإرسال الآلي!")
    except Exception as e:
        status.error(f"خطأ آلي: {e}")
else:
    st.title("🚀 مصنع KDP الشامل (V8 Elite)")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        u_theme = st.text_input("موضوع الكتاب (نيش):", "Robot Adventures")
        u_pages = st.slider("عدد الصفحات الإجمالي:", 10, 100, 40)
    with col2:
        types_list = ["منوع (الكل)", "البحث عن الكلمات", "تلوين فقط", "رياضيات فقط", "سودوكو فقط", "كوميكس فقط"]
        u_type = st.selectbox("نوع الكتاب الذي تريد بيعه:", types_list)

    if st.button("🪄 ابدأ السحر (تصميم + نشر)", use_container_width=True):
        if not valid_keys:
            st.error("⚠️ الرجاء وضع مفتاح API في متغيرات Render!")
        else:
            try:
                f_name, meta_data = create_full_package(u_theme, u_type, u_pages, status)
                st.success("🎉 الكتاب جاهز! تم إرسال نسخة لتليجرام مع الكلمات المفتاحية.")
                st.info(f"**خطة النشر الجاهزة لـ KDP:**\n\n{meta_data}")
                with open(f_name, "rb") as f:
                    st.download_button("⬇️ تحميل الكتاب (PDF) إلى هاتفك", f, file_name=f_name, use_container_width=True)
            except Exception as e:
                status.error(f"❌ حدث خطأ حرج: {e}")
                st.code(traceback.format_exc())
