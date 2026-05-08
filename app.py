import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import random
import time

# --- إعدادات الواجهة ---
st.set_page_config(page_title="KDP Auto-Agency V5", page_icon="🤖", layout="centered")
st.title("🤖 وكالة KDP الآلية (الإصدار الشامل)")
st.markdown("**Made by Erwin Smith** | متصل بتليجرام ✈️")
st.divider()

# --- جلب المتغيرات من السيرفر ---
api_keys = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2"), os.getenv("GEMINI_API_KEY_3")]
valid_keys = [key for key in api_keys if key]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not valid_keys:
    st.warning("⚠️ لا توجد مفاتيح API. أدخل مفتاحاً للعمل المؤقت:")
    manual_key = st.text_input("Gemini API Key:", type="password")
    if manual_key: valid_keys.append(manual_key)

# --- محرك الذكاء الاصطناعي (المدرع) ---
def ask_gemini(prompt_text):
    models = ['gemini-1.5-flash', 'gemini-1.5-pro-latest', 'gemini-pro']
    for key in valid_keys:
        genai.configure(api_key=key)
        for model_name in models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt_text)
                if response.text: return response.text
            except: continue
    raise Exception("❌ فشلت جميع المفاتيح والنماذج. راجع حصة الاستخدام.")

# --- نظام مراجعة الجودة (QA System) ---
def generate_and_review_prompts(theme, count):
    # 1. التوليد المبدئي
    draft_prompt = f"""Generate {count} unique image prompts for a children's coloring book. 
    Theme: {theme}. Target: Western kids. Return ONLY prompts, one per line."""
    drafts = ask_gemini(draft_prompt)
    
    # 2. المراجعة والتصحيح الصارم لـ KDP
    review_prompt = f"""You are a strict KDP Quality Assurance reviewer. Review these image prompts:
    {drafts}
    Rewrite EVERY prompt to strictly include these rules:
    - "thick black outlines"
    - "pure white background"
    - "simple flat vector"
    - "NO shading, NO color, NO grayscale"
    Return ONLY the corrected prompts, one per line."""
    final_prompts = ask_gemini(review_prompt)
    return [p.strip() for p in final_prompts.split('\n') if p.strip()]

# --- خوارزميات الألغاز ---
def generate_sudoku_board():
    base = 3; side = base * base
    def pattern(r, c): return (base * (r % base) + r // base + c) % side
    def shuffle(s): return random.sample(s, len(s))
    rBase = range(base)
    rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, base * base + 1))
    board = [[nums[pattern(r, c)] for c in cols] for r in rows]
    squares = side * side
    for p in random.sample(range(squares), squares * 1 // 2): board[p // side][p % side] = 0
    return board

def draw_sudoku(pdf, board, num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 1, f"Puzzle #{num} - Sudoku", align="C", ln=True)
    start_x, start_y, cell_size = 1.25, 2.5, 0.66
    for i in range(10):
        pdf.set_line_width(0.05 if i % 3 == 0 else 0.01)
        pdf.line(start_x, start_y + i * cell_size, start_x + 9 * cell_size, start_y + i * cell_size)
        pdf.line(start_x + i * cell_size, start_y, start_x + i * cell_size, start_y + 9 * cell_size)
    pdf.set_font("Arial", "B", 16)
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0: pdf.text(start_x + c * cell_size + 0.25, start_y + r * cell_size + 0.45, str(board[r][c]))

def draw_tictactoe(pdf, num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 1, f"Tic-Tac-Toe - Page {num}", align="C", ln=True)
    pdf.set_line_width(0.02)
    for px, py in [(1.5, 2), (4.5, 2), (1.5, 5), (4.5, 5), (1.5, 8), (4.5, 8)]:
        step = 2.0 / 3
        pdf.line(px + step, py, px + step, py + 2.0); pdf.line(px + 2*step, py, px + 2*step, py + 2.0)
        pdf.line(px, py + step, px + 2.0, py + step); pdf.line(px, py + 2*step, px + 2.0, py + 2*step)

# --- إرسال للملف عبر تليجرام ---
def send_to_telegram(file_path, caption):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        resp = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"document": f})
    return resp.status_code == 200

# --- واجهة المستخدم الرئيسية ---
st.info("💡 اضغط على الزر ليقوم البوت بتوليد الكتاب وإرساله مباشرة لهاتفك!")

if st.button("🚀 تصميم وإرسال الكتاب لـ Telegram الآن", use_container_width=True):
    if not valid_keys: st.stop()
    
    try:
        progress = st.progress(0)
        status = st.empty()
        pdf = FPDF(unit="in", format=(8.5, 11))
        pdf.set_auto_page_break(0)

        # 1. اختيار النيش التلقائي (Auto-Niche)
        status.text("🧠 البوت يبحث عن أفضل نيش غير مشبع...")
        theme = ask_gemini("Suggest ONE highly profitable, low-competition children's activity book niche (just the name, e.g., 'Space Dinosaurs').").strip()
        book_title = f"The Ultimate {theme} Activity Book"

        # 2. الغلاف
        status.text(f"🎨 جاري رسم الغلاف (النيش: {theme})...")
        try:
            cover_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(f'kids activity book cover, {theme}, colorful, no text')}?width=816&height=1056&nologo=true"
            with open("cover.jpg", "wb") as f: f.write(requests.get(cover_url, timeout=15).content)
            pdf.add_page(); pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11); os.remove("cover.jpg")
        except: pass

        pdf.add_page()
        pdf.set_font("Arial", "B", 26); pdf.set_y(4); pdf.cell(0, 1, book_title, align="C", ln=True)

        # 3. التلوين (مع المراجعة الصارمة)
        status.text("🔍 جاري كتابة ومراجعة أوامر التلوين لضمان جودة KDP...")
        prompts = generate_and_review_prompts(theme, 10) # 10 صفحات تلوين
        
        for i, p in enumerate(prompts):
            status.text(f"🖌️ رسم صفحة التلوين {i+1}/10...")
            try:
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true&seed={i}"
                with open("temp.jpg", "wb") as f: f.write(requests.get(img_url, timeout=15).content)
                pdf.add_page(); pdf.image("temp.jpg", x=0.75, y=1.5, w=7, h=7)
                pdf.add_page() # ظهر فارغ
                os.remove("temp.jpg")
            except: continue
            progress.progress((i + 1) / 15)

        # 4. الألغاز المبرمجة
        status.text("🔢 جاري بناء شبكات السودوكو و X-O...")
        for i in range(3): draw_sudoku(pdf, generate_sudoku_board(), i+1)
        for i in range(2): draw_tictactoe(pdf, i+1)
        progress.progress(1.0)

        # 5. الحفظ والإرسال
        status.text("✈️ جاري إرسال الكتاب لتليجرام...")
        file_name = f"KDP_{theme.replace(' ', '_')}.pdf"
        pdf.output(file_name)
        
        if send_to_telegram(file_name, f"✅ يا صاح! كتابك جاهز.\nالنيش: {theme}\nجاهز للرفع على KDP."):
            st.success("تم الإرسال لتليجرام بنجاح! 📱")
        else:
            st.warning("تم صنع الكتاب لكن الإرسال لتليجرام فشل (تأكد من الـ Token والـ ID).")
            
        with open(file_name, "rb") as f:
            st.download_button("⬇️ تحميل احتياطي من هنا", f, file_name=file_name)

    except Exception as e:
        st.error(f"خطأ حرج: {e}")

