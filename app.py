import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import random
import time
import traceback

# --- إعدادات الواجهة ---
st.set_page_config(page_title="KDP Empire Builder", page_icon="💰", layout="centered")

# --- جلب المتغيرات ---
api_keys = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2"), os.getenv("GEMINI_API_KEY_3")]
valid_keys = [k.strip() for k in api_keys if k and k.strip() != ""]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- محرك الذكاء الاصطناعي المدرع (محدث لـ 2.5-flash) ---
def ask_gemini(prompt_text):
    # التسلسل الصحيح والمدعوم حالياً
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
    raise Exception(f"فشلت المحاولات مع كل النماذج. آخر خطأ: {last_err}")

# --- خوارزميات الأنشطة المربحة ---
def draw_math_page(pdf, page_num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 1, f"Math Practice - Page {page_num}", align="C", ln=True)
    pdf.set_font("Arial", "", 18)
    pdf.ln(0.5)
    for i in range(8):
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
        [(0.75, 1.5, 3.5, 4), (4.25, 1.5, 3.5, 4), (0.75, 5.75, 7, 4)],
        [(0.75, 1.5, 7, 3), (0.75, 4.75, 7, 3), (0.75, 8, 7, 2.5)]
    ]
    for x, y, w, h in random.choice(layouts):
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

# --- محرك النشر الآلي ---
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

    # 2. العنوان
    pdf.add_page(); pdf.set_font("Arial", "B", 30); pdf.set_y(4)
    pdf.cell(0, 1, f"The Big Book of {theme}", align="C", ln=True)

    # تحديد أعداد الصفحات لكل نوع بناءً على اختيار المستخدم
    c_count = m_count = com_count = s_count = 0
    
    if book_type == "منوع (كل الأنشطة)":
        c_count = m_count = com_count = s_count = max(1, pages // 4)
    elif book_type == "تلوين فقط": c_count = pages
    elif book_type == "رياضيات فقط": m_count = pages
    elif book_type == "كوميكس فقط": com_count = pages
    elif book_type == "سودوكو فقط": s_count = pages

    # 3. توليد المحتوى
    if c_count > 0:
        status.text(f"🧠 توليد {c_count} أوامر تلوين لـ {theme}...")
        p_raw = ask_gemini(f"List {c_count} simple coloring prompts for {theme}. Bold outlines, white bg. One per line.")
        for i, p in enumerate(p_raw.split('\n')[:c_count]):
            status.text(f"🖌️ رسم صفحة التلوين {i+1} من {c_count}...")
            try:
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,999)}"
                with open("t.jpg", "wb") as f: f.write(requests.get(img_url, timeout=20).content)
                pdf.add_page(); pdf.image("t.jpg", x=0.75, y=1.5, w=7, h=7); pdf.add_page(); os.remove("t.jpg")
                time.sleep(1) # استراحة قصيرة لتجنب حظر السيرفر
            except: continue

    if m_count > 0:
        status.text(f"🔢 توليد {m_count} صفحات رياضيات...")
        for i in range(m_count): draw_math_page(pdf, i+1)

    if com_count > 0:
        status.text(f"📝 رسم {com_count} صفحات كوميكس...")
        for i in range(com_count): draw_comic_panels(pdf, i+1)

    if s_count > 0:
        status.text(f"🧩 توليد {s_count} ألغاز سودوكو...")
        for i in range(s_count): draw_sudoku_page(pdf, generate_sudoku(), i+1)

    fname = f"KDP_{theme.replace(' ', '_')}_{int(time.time())}.pdf"
    pdf.output(fname)
    
    # 4. SEO Metadata
    status.text("📝 كتابة بيانات النشر (SEO)...")
    meta_prompt = f"Write Amazon KDP listing for kids book. Theme: {theme}. Type: {book_type}. Pages: {pages}. Include: Title, Subtitle, 7 Backend Keywords (comma separated), and short Description."
    try: meta = ask_gemini(meta_prompt)
    except: meta = "لم يتم توليد الوصف بسبب ضغط السيرفر."
    
    # 5. تليجرام
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        status.text("✈️ إرسال لتليجرام...")
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ كتاب {theme} جاهز!"}, files={"document": open(fname, "rb")}, timeout=30)
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": meta}, timeout=15)
        except Exception as e: print(f"Telegram error: {e}")

    return fname, meta

# --- التشغيل الذكي واليدوي ---
is_auto = st.query_params.get("auto") == "true"
status = st.empty()

if is_auto:
    st.warning("🤖 الوضع الآلي (الخفي) مفعل...")
    if not valid_keys: st.stop()
    try:
        theme = ask_gemini("Suggest ONE highly profitable children's activity book niche (e.g. Space Robots, Mermaid Adventures). Just the phrase.").strip()
        create_full_package(theme, "منوع (كل الأنشطة)", 40, status)
        st.success("✅ تم الإنتاج والإرسال الآلي بنجاح!")
    except Exception as e:
        status.error(f"خطأ في الوضع الآلي: {e}")
else:
    st.title("💰 مصنع الأرباح: KDP Auto-Elite")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        u_theme = st.text_input("موضوع الكتاب (الثيم):", "Space Adventures")
        u_pages = st.slider("عدد الصفحات المراد توليدها:", 10, 60, 20)
    with col2:
        types_list = ["منوع (كل الأنشطة)", "تلوين فقط", "رياضيات فقط", "كوميكس فقط", "سودوكو فقط"]
        u_type = st.selectbox("نوع محتوى الكتاب:", types_list)

    if st.button("🚀 ابدأ صناعة الكتاب الآن", use_container_width=True):
        if not valid_keys:
            st.error("⚠️ الرجاء وضع مفتاح API في متغيرات Render!")
        else:
            try:
                f_name, meta_data = create_full_package(u_theme, u_type, u_pages, status)
                st.success("🎉 اكتملت العملية! تفقد التليجرام الخاص بك.")
                st.info(f"**بيانات النشر المقترحة:**\n\n{meta_data}")
                with open(f_name, "rb") as f:
                    st.download_button("⬇️ تحميل الكتاب محلياً (PDF)", f, file_name=f_name, use_container_width=True)
            except Exception as e:
                status.error(f"حدث خطأ أثناء التنفيذ: {e}")
                st.code(traceback.format_exc())
