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
st.set_page_config(page_title="KDP Empire V10", page_icon="👑", layout="centered")

# --- جلب المتغيرات وتأمينها ---
api_keys = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2"), os.getenv("GEMINI_API_KEY_3")]
valid_keys = [k.strip() for k in api_keys if k and k.strip() != ""]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- محرك الذكاء الاصطناعي المدرع ---
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
    raise Exception(f"تعطل المحرك: {last_err}")

# --- محمل الصور الآمن (Image Downloader) ---
def safe_download_image(prompt, filename, retries=3):
    for attempt in range(retries):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&nologo=true&seed={random.randint(1,9999)}"
            resp = requests.get(url, timeout=15)
            # التأكد أن الرد عبارة عن صورة وليس صفحة خطأ HTML وأن حجمها مناسب
            if resp.status_code == 200 and 'image' in resp.headers.get('Content-Type', '') and len(resp.content) > 15000:
                with open(filename, "wb") as f: f.write(resp.content)
                return True
        except: pass
        time.sleep(2) # استراحة قبل المحاولة القادمة
    return False

# --- خوارزميات الأنشطة 100% بايثون ---

def draw_math_page(pdf, page_num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 22)
    pdf.cell(0, 1, f"Math Master - Page {page_num}", align="C", ln=True)
    pdf.set_font("Arial", "", 20)
    pdf.ln(0.5)
    for i in range(8):
        num1, num2 = random.randint(10, 99), random.randint(1, 10)
        op = random.choice(['+', '-', 'x'])
        pdf.cell(0, 0.9, f"{i+1})    {num1}  {op}  {num2}  =  _______", ln=True, align="C")

def draw_word_search_page(pdf, theme, page_num):
    words = ["SUN", "STAR", "MOON", "SKY", "SPACE", "PLANET"] # افتراضي للطوارئ
    try:
        words_raw = ask_gemini(f"Give exactly 6 simple English words related to '{theme}'. ONLY words separated by commas. No spaces.").upper()
        gen_words = [w.strip() for w in words_raw.replace('\n', '').split(',')]
        gen_words = [w for w in gen_words if w.isalpha() and 3 <= len(w) <= 8][:6]
        if len(gen_words) == 6: words = gen_words
    except: pass

    grid_size = 10
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    for w in words:
        for _ in range(50):
            direction = random.choice([(0,1), (1,0)])
            r, c = random.randint(0, grid_size - 1 - (len(w)-1)*direction[0]), random.randint(0, grid_size - 1 - (len(w)-1)*direction[1])
            if all(grid[r+i*direction[0]][c+i*direction[1]] in (' ', w[i]) for i in range(len(w))):
                for i in range(len(w)): grid[r+i*direction[0]][c+i*direction[1]] = w[i]
                break
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c] == ' ': grid[r][c] = random.choice(string.ascii_uppercase)

    pdf.add_page()
    pdf.set_font("Arial", "B", 22); pdf.cell(0, 1, f"Word Search - Page {page_num}", align="C", ln=True)
    pdf.set_font("Arial", "B", 24)
    start_x, start_y, cell_size = 1.75, 2.5, 0.5
    for r in range(grid_size):
        for c in range(grid_size): pdf.text(start_x + c*cell_size, start_y + r*cell_size, grid[r][c])
    pdf.set_font("Arial", "", 16); pdf.set_y(8.0)
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

def draw_maze_page(pdf, page_num):
    cols, rows = 12, 12
    grid = [[{'N':True, 'S':True, 'E':True, 'W':True, 'visited':False} for _ in range(cols)] for _ in range(rows)]
    stack = [(0, 0)]; grid[0][0]['visited'] = True
    while stack:
        cx, cy = stack[-1]
        directions = [('N', 0, -1, 'S'), ('S', 0, 1, 'N'), ('E', 1, 0, 'W'), ('W', -1, 0, 'E')]
        random.shuffle(directions)
        moved = False
        for dir_name, dx, dy, opposite in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and not grid[ny][nx]['visited']:
                grid[cy][cx][dir_name] = False; grid[ny][nx][opposite] = False
                grid[ny][nx]['visited'] = True
                stack.append((nx, ny)); moved = True; break
        if not moved: stack.pop()
    grid[0][0]['W'] = False; grid[rows-1][cols-1]['E'] = False

    pdf.add_page(); pdf.set_font("Arial", "B", 22); pdf.cell(0, 1, f"Escape the Maze - Page {page_num}", align="C", ln=True)
    start_x, start_y, cs = 1.8, 2.5, 0.4
    pdf.set_line_width(0.04)
    for y in range(rows):
        for x in range(cols):
            px, py = start_x + x*cs, start_y + y*cs
            if grid[y][x]['N']: pdf.line(px, py, px+cs, py)
            if grid[y][x]['S']: pdf.line(px, py+cs, px+cs, py+cs)
            if grid[y][x]['E']: pdf.line(px+cs, py, px+cs, py+cs)
            if grid[y][x]['W']: pdf.line(px, py, px, py+cs)

# --- محرك الإنتاج والموزع ---
def create_full_package(theme, book_type, pages, status):
    pdf = FPDF(unit="in", format=(8.5, 11))
    pdf.set_auto_page_break(0)
    progress_bar = st.progress(0)
    
    # 1. الغلاف (برومبت آمن ومبهج للأطفال)
    status.text(f"🎨 تصميم الغلاف لـ {theme}...")
    cover_prompt = f"cute happy {theme} illustration for kids book cover, simple cartoon style, bright colors, NO text, NO words"
    if safe_download_image(cover_prompt, "cover.jpg"):
        pdf.add_page(); pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11); os.remove("cover.jpg")
    else:
        # غلاف طوارئ نصي إذا فشل الذكاء الاصطناعي كلياً
        pdf.add_page(); pdf.set_font("Arial", "B", 40); pdf.set_y(5)
        pdf.cell(0, 1, f"{theme.upper()} BOOK", align="C", ln=True)

    # 2. صفحة العنوان الداخلية
    pdf.add_page(); pdf.set_font("Arial", "B", 36); pdf.set_y(4)
    pdf.cell(0, 1, f"The BIG Book of", align="C", ln=True)
    pdf.cell(0, 1, f"{theme.upper()}", align="C", ln=True)

    # 3. تنظيم الأقسام وحساب العدد
    activities = ["تلوين", "رياضيات", "متاهات", "كلمات", "كوميكس", "سودوكو"] if book_type == "منوع (الكل)" else [book_type]
    per_type = max(1, pages // len(activities))
    failed_images_count = 0 # لتسجيل الصفحات التي فشلت لنعوضها بصفحات أخرى

    # --- التلوين ---
    if "تلوين" in activities or "تلوين فقط" in book_type:
        status.text(f"🧠 توليد أفكار التلوين...")
        try:
            subjects = ask_gemini(f"Give {per_type} simple cute single items related to {theme} for kids to color. Just the item name, one per line.").split('\n')
            for i, sub in enumerate(subjects[:per_type]):
                status.text(f"🖌️ رسم صفحة التلوين {i+1}...")
                safe_prompt = f"black and white line art coloring page for kids, a simple cute {sub.strip()}, thick clean black outlines, pure white background, uncolored, NO shading"
                if safe_download_image(safe_prompt, "t.jpg"):
                    pdf.add_page(); pdf.image("t.jpg", x=0.75, y=1.5, w=7, h=7); pdf.add_page() # صفحة التلوين + ظهر فارغ
                    os.remove("t.jpg")
                else:
                    failed_images_count += 1 # فشلت الصورة، سجلها للتعويض
                progress_bar.progress((i+1)/(per_type*len(activities)))
        except: failed_images_count += per_type

    # --- الأنشطة البرمجية (تعمل 100% بدون انترنت) ---
    def safe_draw(func, *args):
        try: func(*args)
        except Exception as e: print(f"Error drawing {func.__name__}: {e}")

    if "رياضيات" in activities or "رياضيات فقط" in book_type:
        status.text("🔢 توليد أوراق الرياضيات...")
        for i in range(per_type + failed_images_count): # تعويض الصفحات الفاشلة هنا
            safe_draw(draw_math_page, pdf, i+1)

    if "متاهات" in activities or "متاهات فقط" in book_type:
        status.text("🌀 توليد المتاهات الهندسية...")
        for i in range(per_type): safe_draw(draw_maze_page, pdf, i+1)

    if "كلمات" in activities or "البحث عن الكلمات" in book_type:
        status.text("🔍 بناء شبكات البحث عن الكلمات...")
        for i in range(per_type): safe_draw(draw_word_search_page, pdf, theme, i+1)

    if "كوميكس" in activities or "كوميكس فقط" in book_type:
        status.text("📝 رسم قوالب الكوميكس...")
        for i in range(per_type): safe_draw(draw_comic_panels, pdf, i+1)

    if "سودوكو" in activities or "سودوكو فقط" in book_type:
        status.text("🧩 حل وتوليد ألغاز السودوكو...")
        for i in range(per_type): safe_draw(draw_sudoku_page, pdf, generate_sudoku(), i+1)

    # 4. التصدير
    progress_bar.progress(1.0)
    fname = f"KDP_{theme.replace(' ', '_')}_{int(time.time())}.pdf"
    pdf.output(fname)
    
    # 5. SEO Metadata
    status.text("📝 كتابة وصف البيع لـ KDP...")
    try: 
        meta = ask_gemini(f"Act as Amazon KDP expert. Write converting listing for kids activity book. Theme: {theme}. Type: {book_type}. Include: Catchy Title, Subtitle, 7 Backend Search Keywords (comma separated), and a short Description.")
    except: meta = "⚠️ استخدم كلمات مفتاحية متعلقة بالنيش الخاص بك."
    
    # 6. الإرسال لتليجرام
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        status.text("✈️ إرسال الكتاب لتليجرام...")
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ مبروك! كتاب {theme} جاهز."}, files={"document": open(fname, "rb")}, timeout=60)
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
        theme = ask_gemini("Suggest ONE highly profitable, low-competition KDP niche for kids activity books (e.g. Space Dogs). Just the exact phrase.").strip()
        create_full_package(theme, "منوع (الكل)", 36, status)
        st.success("✅ تم الإنتاج والإرسال الآلي!")
    except Exception as e: status.error(f"خطأ آلي: {e}")
else:
    st.title("🚀 مصنع KDP المدرع (V10)")
    st.info("💡 النظام الآن محصن تماماً ضد توقف الصور، ويحتوي على تعويض ديناميكي للصفحات التالفة.")
    
    col1, col2 = st.columns(2)
    with col1:
        u_theme = st.text_input("موضوع الكتاب (نيش):", "Ninja Animals")
        u_pages = st.slider("عدد الصفحات الإجمالي:", 12, 100, 30)
    with col2:
        types_list = ["منوع (الكل)", "متاهات فقط", "البحث عن الكلمات", "تلوين فقط", "رياضيات فقط", "سودوكو فقط", "كوميكس فقط"]
        u_type = st.selectbox("نوع الكتاب الذي تريد بيعه:", types_list)

    if st.button("🪄 ابدأ السحر (تصميم + نشر)", use_container_width=True):
        if not valid_keys: st.error("⚠️ الرجاء وضع مفاتيح API في Render!")
        else:
            try:
                f_name, meta_data = create_full_package(u_theme, u_type, u_pages, status)
                st.success("🎉 الكتاب جاهز تماماً وتم الإرسال لتليجرام!")
                st.info(f"**خطة النشر الجاهزة:**\n\n{meta_data}")
                with open(f_name, "rb") as f:
                    st.download_button("⬇️ تحميل الكتاب (PDF)", f, file_name=f_name, use_container_width=True)
            except Exception as e:
                status.error(f"❌ حدث خطأ حرج: {e}")
                st.code(traceback.format_exc())

