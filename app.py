import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import random
import time
import traceback

# --- إعدادات الواجهة ---
st.set_page_config(page_title="KDP Auto-Bot Elite", page_icon="🤖", layout="centered")

# --- جلب المتغيرات وتأمينها ---
api_keys = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2"), os.getenv("GEMINI_API_KEY_3")]
valid_keys = [key.strip() for key in api_keys if key and key.strip() != ""]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- محرك الذكاء الاصطناعي (المدرع بالكامل والمحدث) ---
def ask_gemini(prompt_text):
    # التسلسل الهرمي من الأحدث للأقدم
    models = ['gemini-2.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro']
    errors_log = []
    
    for key in valid_keys:
        genai.configure(api_key=key)
        # إخفاء جزء من المفتاح للأمان عند عرض الأخطاء
        safe_key_name = f"...{key[-4:]}" if len(key) > 4 else "Unknown_Key" 
        
        for model_name in models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt_text)
                if response.text: 
                    return response.text
            except Exception as e:
                # تسجيل تفاصيل الخطأ بدقة شديدة
                error_detail = f"🔑 المفتاح [{safe_key_name}] | 🧠 النموذج [{model_name}]: {str(e)}"
                errors_log.append(error_detail)
                time.sleep(1) # استراحة قصيرة لتجنب حظر الـ Spam
                continue
                
    # إذا استنفدنا كل المفاتيح وكل النماذج وفشلت جميعها
    full_error_report = "\n".join(errors_log)
    raise Exception(f"🚨 انهيار كامل للمحرك. تفاصيل الفشل لكل المفاتيح والنماذج:\n{full_error_report}")

def generate_and_review_prompts(theme, count):
    draft_prompt = f"Generate {count} unique image prompts for a children's coloring book. Theme: {theme}. Return ONLY prompts, one per line."
    drafts = ask_gemini(draft_prompt)
    review_prompt = f"Rewrite these prompts to be strictly: thick black outlines, pure white background, flat vector, no color, simple line art:\n{drafts}\nReturn ONLY prompts, one per line."
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
    for p in random.sample(range(side * side), side * side // 2): board[p // side][p % side] = 0
    return board

def draw_sudoku(pdf, board, num):
    pdf.add_page()
    pdf.set_font("Arial", "B", 18); pdf.cell(0, 1, f"Puzzle #{num} - Sudoku", align="C", ln=True)
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
    pdf.set_font("Arial", "B", 18); pdf.cell(0, 1, f"Tic-Tac-Toe - Page {num}", align="C", ln=True)
    pdf.set_line_width(0.02)
    for px, py in [(1.5, 2), (4.5, 2), (1.5, 5), (4.5, 5), (1.5, 8), (4.5, 8)]:
        step = 2.0 / 3
        pdf.line(px + step, py, px + step, py + 2.0); pdf.line(px + 2*step, py, px + 2*step, py + 2.0)
        pdf.line(px, py + step, px + 2.0, py + step); pdf.line(px, py + 2*step, px + 2.0, py + 2*step)

def send_to_telegram(file_path, caption):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            resp = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"document": f}, timeout=30)
        return resp.status_code == 200
    except Exception as e:
        print(f"Telegram Error: {e}")
        return False

# --- دالة التشغيل الرئيسية ---
def run_bot():
    if not valid_keys: 
        st.error("⚠️ مفاتيح API مفقودة من السيرفر!")
        return
        
    try:
        status = st.empty()
        pdf = FPDF(unit="in", format=(8.5, 11))
        pdf.set_auto_page_break(0)

        status.text("🧠 البوت يحلل السوق للبحث عن أفضل نيش...")
        theme = ask_gemini("Suggest ONE highly profitable children's activity book niche (just the name).").strip()
        book_title = f"The Ultimate {theme} Activity Book"

        status.text(f"🎨 رسم الغلاف لنيش: {theme}...")
        try:
            cover_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(f'kids activity book cover, {theme}, colorful')}?width=816&height=1056&nologo=true"
            # حماية الاتصال: إذا تأخر السيرفر يتخطى بسلام
            cover_resp = requests.get(cover_url, timeout=15)
            if cover_resp.status_code == 200:
                with open("cover.jpg", "wb") as f: f.write(cover_resp.content)
                pdf.add_page(); pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11); os.remove("cover.jpg")
        except Exception as e: 
            print(f"Cover generation skipped: {e}")

        pdf.add_page()
        pdf.set_font("Arial", "B", 26); pdf.set_y(4); pdf.cell(0, 1, book_title, align="C", ln=True)

        status.text("🔍 معالجة أوامر التلوين بصرامة KDP...")
        prompts = generate_and_review_prompts(theme, 10)
        
        for i, p in enumerate(prompts):
            status.text(f"🖌️ رسم وتنزيل الصورة {i+1}/10...")
            try:
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true&seed={i}"
                img_resp = requests.get(img_url, timeout=15)
                if img_resp.status_code == 200:
                    with open("temp.jpg", "wb") as f: f.write(img_resp.content)
                    pdf.add_page(); pdf.image("temp.jpg", x=0.75, y=1.5, w=7, h=7); pdf.add_page()
                    os.remove("temp.jpg")
            except Exception as e: 
                print(f"Image {i+1} skipped due to error: {e}")
                continue

        status.text("🔢 رسم الألغاز المعمارية...")
        for i in range(3): draw_sudoku(pdf, generate_sudoku_board(), i+1)
        for i in range(2): draw_tictactoe(pdf, i+1)

        file_name = f"KDP_{theme.replace(' ', '_')}.pdf"
        pdf.output(file_name)
        
        status.text("✈️ إرسال لتليجرام...")
        if send_to_telegram(file_name, f"✅ تم بحمد الله.\nالنيش: {theme}\nمستعد للرفع المباشر."):
            st.success("تم التصميم والإرسال لتليجرام بنجاح! 📱")
        else:
            st.warning("فشل الإرسال لتليجرام. قد يكون التوكن خاطئاً أو الملف كبيراً جداً.")
            
    except Exception as e:
        # عرض الخطأ التفصيلي في الواجهة إذا انهار البوت
        st.error("❌ توقفت العملية. إليك التقرير التقني:")
        st.code(str(e))
        st.error(traceback.format_exc()) # يعرض مسار الخطأ بالكامل للمبرمج

# --- آلية التشغيل (يدوي أو آلي) ---
is_auto_mode = st.query_params.get("auto") == "true"

if is_auto_mode:
    st.warning("⚙️ الوضع الآلي مفعل. جاري بناء الكتاب وإرساله...")
    run_bot()
else:
    st.title("🤖 وكالة KDP الآلية (Elite)")
    st.info("💡 النظام الآن محمي ضد الأخطاء، ويدعم أحدث نماذج Gemini.")
    if st.button("🚀 بدء دورة العمل والتصدير لـ Telegram"):
        run_bot()

