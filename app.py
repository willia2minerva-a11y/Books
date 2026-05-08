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
st.set_page_config(page_title="KDP Story-Driven Empire", page_icon="📖", layout="centered")

# --- جلب المتغيرات وتأمينها ---
api_keys = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2"), os.getenv("GEMINI_API_KEY_3")]
valid_keys = [k.strip() for k in api_keys if k and k.strip() != ""]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- محرك الذكاء الاصطناعي ---
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

# --- محمل الصور الآمن ---
def safe_download_image(prompt, filename, retries=3):
    for attempt in range(retries):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&nologo=true&seed={random.randint(1,9999)}"
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200 and len(resp.content) > 15000:
                with open(filename, "wb") as f: f.write(resp.content)
                return True
        except: pass
        time.sleep(2)
    return False

# --- محرك السرد القصصي (Story Engine) ---
def generate_story_lines(theme, count):
    prompt = f"Write a {count}-part exciting children's adventure story about '{theme}'. Each part must be exactly 1 short simple sentence in English. Return ONLY the sentences, separated by '||'. No numbers, no introductions."
    try:
        res = ask_gemini(prompt)
        lines = [l.strip() for l in res.split('||') if l.strip()]
        if len(lines) >= count: return lines[:count]
    except: pass
    return [f"Let's explore the world of {theme} together!" for _ in range(count)]

# --- خوارزميات الأنشطة المربوطة بالقصة ---

def draw_math_page(pdf, page_num, story_text="Solve the puzzle to continue!"):
    pdf.add_page()
    # طباعة القصة في الأعلى
    pdf.set_font("Arial", "I", 18)
    pdf.multi_cell(0, 0.4, story_text, align="C")
    pdf.ln(0.5)
    
    pdf.set_font("Arial", "B", 22)
    pdf.cell(0, 1, f"Secret Code - Page {page_num}", align="C", ln=True)
    pdf.set_font("Arial", "", 20)
    for i in range(7): # قللنا العدد لترك مساحة للقصة
        num1, num2 = random.randint(10, 99), random.randint(1, 10)
        op = random.choice(['+', '-', 'x'])
        pdf.cell(0, 0.9, f"{i+1})    {num1}  {op}  {num2}  =  _______", ln=True, align="C")

def draw_maze_page(pdf, page_num, story_text="Find the right path!"):
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

    pdf.add_page()
    pdf.set_font("Arial", "I", 18)
    pdf.multi_cell(0, 0.4, story_text, align="C")
    pdf.ln(0.2)
    
    pdf.set_font("Arial", "B", 22); pdf.cell(0, 1, f"The Great Escape - Page {page_num}", align="C", ln=True)
    start_x, start_y, cs = 1.8, 3.0, 0.4
    pdf.set_line_width(0.04)
    for y in range(rows):
        for x in range(cols):
            px, py = start_x + x*cs, start_y + y*cs
            if grid[y][x]['N']: pdf.line(px, py, px+cs, py)
            if grid[y][x]['S']: pdf.line(px, py+cs, px+cs, py+cs)
            if grid[y][x]['E']: pdf.line(px+cs, py, px+cs, py+cs)
            if grid[y][x]['W']: pdf.line(px, py, px, py+cs)

def draw_word_search_page(pdf, theme, page_num, story_text="Find the hidden magic words!"):
    try:
        words_raw = ask_gemini(f"Give exactly 6 simple English words related to '{theme}'. ONLY words separated by commas. No spaces.").upper()
        words = [w.strip() for w in words_raw.replace('\n', '').split(',') if w.strip().isalpha() and 3 <= len(w.strip()) <= 8][:6]
        if len(words) < 6: words = ["HERO", "MAGIC", "POWER", "SECRET", "BRAVE", "QUEST"]
    except: words = ["HERO", "MAGIC", "POWER", "SECRET", "BRAVE", "QUEST"]

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
    pdf.set_font("Arial", "I", 18)
    pdf.multi_cell(0, 0.4, story_text, align="C")
    pdf.ln(0.2)
    
    pdf.set_font("Arial", "B", 22); pdf.cell(0, 1, f"Hidden Clues - Page {page_num}", align="C", ln=True)
    pdf.set_font("Arial", "B", 24)
    start_x, start_y, cell_size = 1.75, 3.2, 0.5
    for r in range(grid_size):
        for c in range(grid_size): pdf.text(start_x + c*cell_size, start_y + r*cell_size, grid[r][c])
    pdf.set_font("Arial", "", 16); pdf.set_y(8.5)
    pdf.cell(0, 0.5, "Find these words:", align="C", ln=True)
    pdf.cell(0, 0.5, " - ".join(words), align="C", ln=True)

# --- محرك الإنتاج والموزع ---
def create_full_package(theme, book_type, pages, status):
    pdf = FPDF(unit="in", format=(8.5, 11))
    pdf.set_auto_page_break(0)
    progress_bar = st.progress(0)
    
    status.text(f"🎨 تصميم الغلاف لـ {theme}...")
    cover_prompt = f"cute happy {theme} illustration for kids book cover, simple cartoon style, bright colors, NO text, NO words"
    if safe_download_image(cover_prompt, "cover.jpg"):
        pdf.add_page(); pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11); os.remove("cover.jpg")
    else:
        pdf.add_page(); pdf.set_font("Arial", "B", 40); pdf.set_y(5)
        pdf.cell(0, 1, f"{theme.upper()} BOOK", align="C", ln=True)

    pdf.add_page(); pdf.set_font("Arial", "B", 36); pdf.set_y(4)
    pdf.cell(0, 1, f"The BIG Adventure of", align="C", ln=True)
    pdf.cell(0, 1, f"{theme.upper()}", align="C", ln=True)

    activities = ["تلوين", "رياضيات", "متاهات", "كلمات"] if book_type in ["منوع (الكل)", "قصة تفاعلية (Story Mode)"] else [book_type]
    per_type = max(1, pages // len(activities))
    
    # استخراج القصة إذا كان النمط قصصياً
    story_lines = []
    if book_type == "قصة تفاعلية (Story Mode)":
        status.text("🧠 تأليف القصة التفاعلية المترابطة...")
        story_lines = generate_story_lines(theme, pages)

    def get_story_line(index):
        if book_type == "قصة تفاعلية (Story Mode)" and index < len(story_lines):
            return story_lines[index]
        return ""

    page_counter = 0

    if "تلوين" in activities or "تلوين فقط" in book_type:
        status.text(f"🧠 توليد مشاهد التلوين...")
        try:
            subjects = ask_gemini(f"Give {per_type} simple cute single items related to {theme} for kids to color. Just the item name, one per line.").split('\n')
            for sub in subjects[:per_type]:
                status.text(f"🖌️ رسم صفحة {page_counter+1}...")
                story_t = get_story_line(page_counter)
                
                safe_prompt = f"black and white line art coloring page for kids, a simple cute {sub.strip()}, thick clean black outlines, pure white background, uncolored, NO shading"
                if safe_download_image(safe_prompt, "t.jpg"):
                    pdf.add_page()
                    if story_t:
                        pdf.set_font("Arial", "I", 18)
                        pdf.multi_cell(0, 0.5, story_t, align="C")
                        pdf.image("t.jpg", x=0.75, y=2.0, w=7, h=7) # نزلنا الصورة لترك مساحة للنص
                    else:
                        pdf.image("t.jpg", x=0.75, y=1.5, w=7, h=7)
                    pdf.add_page() # ظهر فارغ للتلوين
                    os.remove("t.jpg")
                page_counter += 1
                progress_bar.progress(page_counter/pages)
        except: pass

    def safe_draw(func, *args):
        try: func(*args)
        except Exception as e: print(f"Error: {e}")

    if "متاهات" in activities or "متاهات فقط" in book_type:
        status.text("🌀 تصميم المتاهات...")
        for _ in range(per_type): 
            s_text = get_story_line(page_counter) or "Find the way out!"
            safe_draw(draw_maze_page, pdf, page_counter+1, s_text)
            page_counter += 1

    if "رياضيات" in activities or "رياضيات فقط" in book_type:
        status.text("🔢 تشفير صفحات الرياضيات...")
        for _ in range(per_type): 
            s_text = get_story_line(page_counter) or "Solve the math puzzle!"
            safe_draw(draw_math_page, pdf, page_counter+1, s_text)
            page_counter += 1

    if "كلمات" in activities or "البحث عن الكلمات" in book_type:
        status.text("🔍 إخفاء الكلمات السرية...")
        for _ in range(per_type): 
            s_text = get_story_line(page_counter) or "Find the hidden words!"
            safe_draw(draw_word_search_page, pdf, theme, page_counter+1, s_text)
            page_counter += 1

    progress_bar.progress(1.0)
    fname = f"KDP_Story_{theme.replace(' ', '_')}_{int(time.time())}.pdf"
    pdf.output(fname)
    
    status.text("📝 كتابة وصف البيع لـ KDP...")
    try: 
        meta = ask_gemini(f"Act as Amazon KDP expert. Write converting listing for kids story-based activity book. Theme: {theme}. Type: {book_type}. Include: Catchy Title, Subtitle, 7 Backend Search Keywords, and a short Description.")
    except: meta = "⚠️ استخدم كلمات مفتاحية متعلقة بالقصة والنيش الخاص بك."
    
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        status.text("✈️ إرسال الكتاب لتليجرام...")
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ مبروك! كتاب المغامرات {theme} جاهز."}, files={"document": open(fname, "rb")}, timeout=60)
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
        theme = ask_gemini("Suggest ONE highly profitable, low-competition KDP niche for a story-driven kids activity book (e.g. Magic Pirates). Just the exact phrase.").strip()
        create_full_package(theme, "قصة تفاعلية (Story Mode)", 20, status)
        st.success("✅ تم الإنتاج والإرسال الآلي!")
    except Exception as e: status.error(f"خطأ آلي: {e}")
else:
    st.title("📖 مصنع KDP التفاعلي (V11)")
    st.info("💡 اختر 'قصة تفاعلية' لتوليد كتاب يربط بين جميع الأنشطة بقصة إنجليزية مشوقة في أعلى كل صفحة!")
    
    col1, col2 = st.columns(2)
    with col1:
        u_theme = st.text_input("موضوع/بطل الكتاب (نيش):", "Leo the Space Explorer")
        u_pages = st.slider("عدد الأنشطة الإجمالي:", 12, 100, 20)
    with col2:
        types_list = ["قصة تفاعلية (Story Mode)", "منوع (الكل بدون قصة)", "متاهات فقط", "البحث عن الكلمات", "تلوين فقط", "رياضيات فقط"]
        u_type = st.selectbox("نوع الكتاب الذي تريد بيعه:", types_list)

    if st.button("🪄 ابدأ السرد وصناعة الكتاب", use_container_width=True):
        if not valid_keys: st.error("⚠️ الرجاء وضع مفاتيح API في Render!")
        else:
            try:
                f_name, meta_data = create_full_package(u_theme, u_type, u_pages, status)
                st.success("🎉 الكتاب التفاعلي جاهز تماماً وتم الإرسال لتليجرام!")
                st.info(f"**خطة النشر الجاهزة:**\n\n{meta_data}")
                with open(f_name, "rb") as f:
                    st.download_button("⬇️ تحميل الكتاب (PDF)", f, file_name=f_name, use_container_width=True)
            except Exception as e:
                status.error(f"❌ حدث خطأ حرج: {e}")
                st.code(traceback.format_exc())

