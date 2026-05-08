"""
KDP Factory Pro - الإصدار الأسطوري V12.1 (مع نظام التعويض الذكي لنفس النوع)
الهندسة المعمارية: Irwin Smith | التطوير المتقدم: AI
"""

import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import random
import time
import traceback
import string
from datetime import datetime

# ------------------------------------------------------------------------------
# إعدادات الصفحة و CSS
# ------------------------------------------------------------------------------
st.set_page_config(page_title="KDP Factory Pro", page_icon="📚", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    .main-title {
        background: linear-gradient(120deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 48px; font-weight: 900; text-align: center; margin-bottom: 0;
    }
    .sub-title { text-align: center; color: #888; margin-bottom: 30px; }
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white; border: none; border-radius: 30px;
        padding: 12px 30px; font-weight: bold; font-size: 18px; transition: all 0.3s;
    }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(102,126,234,0.4); }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# إدارة البيئة (Environment)
# ------------------------------------------------------------------------------
def get_api_keys():
    keys = [os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 4)]
    valid_keys = [k.strip() for k in keys if k and k.strip()]
    return valid_keys if valid_keys else ["DUMMY"]

API_KEYS = get_api_keys()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ------------------------------------------------------------------------------
# المحركات الأساسية (Engines)
# ------------------------------------------------------------------------------
class GeminiEngine:
    MODELS = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    @classmethod
    def ask(cls, prompt, retries=2):
        if API_KEYS[0] == "DUMMY": return cls._fallback(prompt)
        for _ in range(retries):
            for key in API_KEYS:
                genai.configure(api_key=key)
                for model_name in cls.MODELS:
                    try:
                        m = genai.GenerativeModel(model_name)
                        res = m.generate_content(prompt)
                        if res.text: return res.text.strip()
                    except: continue
            time.sleep(1)
        return cls._fallback(prompt)
    
    @classmethod
    def _fallback(cls, prompt):
        p = prompt.lower()
        if "theme" in p or "niche" in p: return random.choice(["Space Robots", "Magic Ocean", "Dinosaur Knights"])
        if "story" in p or "sentences" in p: return "Welcome to the adventure!||Let's explore.||Solve this puzzle!||Great job!"
        if "keywords" in p: return "kids book, activity book, puzzle, coloring, educational"
        if "description" in p: return "An amazing activity book for kids. Hours of fun and learning!"
        if "titles" in p: return "The Big Adventure Book\nFun Kids Activities"
        return "SUN\nMOON\nSTAR\nSKY\nSPACE\nALIEN"

class ImageGenerator:
    @staticmethod
    def generate(prompt, filename):
        for _ in range(2): # قللنا المحاولات لنسرع الانتقال للرسمة البديلة
            try:
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&nologo=true&seed={random.randint(1,9999)}"
                resp = requests.get(url, timeout=12)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    with open(filename, "wb") as f: f.write(resp.content)
                    return True
            except: time.sleep(1)
        return False

# ------------------------------------------------------------------------------
# خوارزميات الألغاز
# ------------------------------------------------------------------------------
class PuzzleGenerator:
    @staticmethod
    def generate_maze(w=12, h=12):
        grid = [[{'N':True, 'S':True, 'E':True, 'W':True, 'v':False} for _ in range(w)] for _ in range(h)]
        stack = [(0, 0)]; grid[0][0]['v'] = True
        while stack:
            cx, cy = stack[-1]
            dirs = [('N', 0, -1, 'S'), ('S', 0, 1, 'N'), ('E', 1, 0, 'W'), ('W', -1, 0, 'E')]
            random.shuffle(dirs)
            moved = False
            for d, dx, dy, opp in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and not grid[ny][nx]['v']:
                    grid[cy][cx][d] = False; grid[ny][nx][opp] = False
                    grid[ny][nx]['v'] = True
                    stack.append((nx, ny)); moved = True; break
            if not moved: stack.pop()
        grid[0][0]['W'] = False; grid[h-1][w-1]['E'] = False
        return grid
    
    @staticmethod
    def generate_sudoku():
        base = 3; side = base*base; rBase = range(base)
        rows = [g*base + r for g in random.sample(rBase,base) for r in random.sample(rBase,base)]
        cols = [g*base + c for g in random.sample(rBase,base) for c in random.sample(rBase,base)]
        nums = random.sample(range(1,side+1),side)
        board = [[nums[(base*(r%base)+r//base+c)%side] for c in cols] for r in rows]
        for p in random.sample(range(side*side), side*side*2//3): board[p//side][p%side] = 0
        return board

# ------------------------------------------------------------------------------
# محرك PDF
# ------------------------------------------------------------------------------
class KidsBookPDF(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(False)
    
    def add_story_text(self, text):
        if text:
            self.set_font("Arial", "I", 16)
            self.set_xy(0.5, 0.8)
            self.multi_cell(7.5, 0.4, text, align="C")

# ------------------------------------------------------------------------------
# المصنع الرئيسي
# ------------------------------------------------------------------------------
class KDPFactory:
    def __init__(self, config, ui_status, ui_progress):
        self.config = config
        self.status = ui_status
        self.progress = ui_progress
        self.pdf = KidsBookPDF()
        self.story_lines = []
    
    def run(self):
        theme = self.config['theme']
        pages = self.config['pages']
        b_type = self.config['type']
        
        # 1. الغلاف
        self.status(f"🎨 جاري تصميم الغلاف الاحترافي: {theme}...")
        c_prompt = f"beautiful children activity book cover, {theme}, cute cartoon style, highly detailed, vibrant colors, NO text"
        if ImageGenerator.generate(c_prompt, "cover.jpg"):
            self.pdf.add_page(); self.pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11); os.remove("cover.jpg")
        else:
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 40)
            self.pdf.cell(0, 5, f"{theme.upper()} BOOK", align="C", ln=True)

        self.pdf.add_page(); self.pdf.set_font("Arial", "B", 36); self.pdf.set_y(4)
        self.pdf.cell(0, 1, "The BIG Book of", align="C", ln=True)
        self.pdf.cell(0, 1, theme.upper(), align="C", ln=True)

        # 2. القصة (إذا طلبها)
        if b_type == "قصة تفاعلية":
            self.status("🧠 تأليف القصة المترابطة...")
            raw_story = GeminiEngine.ask(f"Write {pages} short simple English sentences for a kids story about {theme}. Separate with '||'.")
            self.story_lines = [s.strip() for s in raw_story.split('||') if s.strip()]

        # 3. الأنشطة
        activities = ["تلوين", "رياضيات", "متاهات", "سودوكو"] if "منوع" in b_type or "قصة" in b_type else [b_type.replace(" فقط", "")]
        per_type = max(1, pages // len(activities))
        page_counter = 0

        # --- التلوين (مع نظام الاستبدال الذكي) ---
        if "تلوين" in activities:
            self.status("🖌️ جاري رسم المشاهد (مع نظام التعويض)...")
            # نطلب ضعف العدد المطلوب كأفكار احتياطية
            items = GeminiEngine.ask(f"Give {per_type + 15} simple single items related to {theme} for kids coloring. One item per line. No numbers.").split('\n')
            
            success_count = 0
            for item in items:
                if success_count >= per_type: 
                    break # إذا وصلنا للعدد المطلوب، نتوقف
                
                if not item.strip(): continue
                
                safe_p = f"black and white line art coloring page, a cute {item.strip()}, thick clean black outlines, pure white background, NO shading"
                self.status(f"🖌️ محاولة رسم: {item.strip()} ({success_count+1}/{per_type})")
                
                if ImageGenerator.generate(safe_p, "t.jpg"):
                    self.pdf.add_page()
                    s_text = self.story_lines[page_counter] if page_counter < len(self.story_lines) else ""
                    self.pdf.add_story_text(s_text)
                    
                    self.pdf.image("t.jpg", x=0.75, y=2.0 if s_text else 1.5, w=7, h=7)
                    os.remove("t.jpg")
                    self.pdf.add_page() # ظهر فارغ لحماية الألوان
                    
                    success_count += 1
                    page_counter += 1
                    self.progress(min(1.0, page_counter/pages))
                else:
                    self.status(f"⚠️ فشل رسم '{item.strip()}'.. جاري تجربة رسمة بديلة من الاحتياط!")
                    # لا نزيد success_count، فيدور الـ loop للعنصر التالي

        # الرياضيات
        if "رياضيات" in activities:
            self.status("🔢 إعداد الألغاز الحسابية...")
            for _ in range(per_type):
                self.pdf.add_page()
                s_text = self.story_lines[page_counter] if page_counter < len(self.story_lines) else "Math Challenge!"
                self.pdf.add_story_text(s_text)
                self.pdf.set_font("Arial", "B", 22); self.pdf.set_y(2.0)
                for i in range(7):
                    n1, n2, op = random.randint(10,99), random.randint(1,10), random.choice(['+','-'])
                    self.pdf.cell(0, 0.9, f"{i+1})    {n1} {op} {n2} = _____", ln=True, align="C")
                page_counter += 1; self.progress(min(1.0, page_counter/pages))

        # المتاهات
        if "متاهات" in activities:
            self.status("🌀 تصميم المتاهات...")
            for _ in range(per_type):
                grid = PuzzleGenerator.generate_maze()
                self.pdf.add_page()
                s_text = self.story_lines[page_counter] if page_counter < len(self.story_lines) else "Escape the Maze!"
                self.pdf.add_story_text(s_text)
                sx, sy, cs = 1.8, 2.5, 0.4
                self.pdf.set_line_width(0.04)
                for y in range(12):
                    for x in range(12):
                        px, py = sx + x*cs, sy + y*cs
                        if grid[y][x]['N']: self.pdf.line(px, py, px+cs, py)
                        if grid[y][x]['S']: self.pdf.line(px, py+cs, px+cs, py+cs)
                        if grid[y][x]['E']: self.pdf.line(px+cs, py, px+cs, py+cs)
                        if grid[y][x]['W']: self.pdf.line(px, py, px, py+cs)
                page_counter += 1; self.progress(min(1.0, page_counter/pages))

        # 4. التصدير و الـ SEO
        self.progress(1.0)
        fname = f"KDP_{theme.replace(' ', '_')}_{int(time.time())}.pdf"
        self.pdf.output(fname)
        
        self.status("📝 كتابة وصف البيع لـ KDP...")
        meta = GeminiEngine.ask(f"Act as Amazon KDP expert. Write converting listing for kids activity book. Theme: {theme}. Type: {b_type}. Include: Catchy Title, Subtitle, 7 Backend Search Keywords, and a short Description.")
        
        return fname, meta

# ------------------------------------------------------------------------------
# إرسال تليجرام
# ------------------------------------------------------------------------------
def send_to_telegram(file_path, theme, metadata):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", 
                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ كتاب {theme} جاهز للبيع!"}, 
                      files={"document": open(file_path, "rb")}, timeout=60)
        
        msg = f"📊 *مواد البيع لامازون KDP*\n\n{metadata}\n\n✨ KDP Factory Pro"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      data={"chat_id": TELEGRAM_CHAT_ID, "text": msg[:4000], "parse_mode": "Markdown"}, timeout=20)
    except: pass

# ------------------------------------------------------------------------------
# الواجهة والتشغيل
# ------------------------------------------------------------------------------
def main():
    if st.query_params.get("auto") == "true":
        st.warning("🤖 النظام الآلي يعمل في الخلفية...")
        if API_KEYS[0] == "DUMMY": st.stop()
        theme = GeminiEngine.ask("Suggest ONE highly profitable children's activity book niche (e.g. Space Dogs). Just the phrase.").strip()
        st.info(f"النيش المختار: {theme}")
        factory = KDPFactory({'theme': theme, 'pages': 24, 'type': 'قصة تفاعلية'}, st.empty().text, st.progress(0).progress)
        fname, meta = factory.run()
        send_to_telegram(fname, theme, meta)
        st.success("✅ تمت العملية بنجاح!")
        return

    st.markdown('<h1 class="main-title">📚 KDP Factory Pro 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">إمبراطورية النشر الذكية - مصمم للعمل بسلاسة على الهواتف</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⚙️ إعدادات النظام")
        if API_KEYS[0] == "DUMMY": st.error("⚠️ يرجى إضافة مفاتيح GEMINI_API_KEY_1 في متغيرات Render")
        else: st.success("✅ النظام متصل بـ Gemini")
        if TELEGRAM_TOKEN: st.success("✅ متصل بتليجرام")
        else: st.warning("⚠️ تليجرام غير مفعل")

    col1, col2 = st.columns(2)
    with col1:
        theme = st.text_input("🎯 موضوع الكتاب (نيش):", "Ninja Cats")
        pages = st.slider("📄 عدد الصفحات (الأنشطة):", 10, 80, 20)
    with col2:
        types = ["قصة تفاعلية", "منوع (كل الأنشطة)", "تلوين فقط", "رياضيات فقط", "متاهات فقط"]
        b_type = st.selectbox("🎭 نوع الكتاب:", types)

    if st.button("🚀 ابدأ تصنيع الكتاب الآن", use_container_width=True):
        status_box = st.empty()
        prog_bar = st.progress(0)
        
        try:
            factory = KDPFactory({'theme': theme, 'pages': pages, 'type': b_type}, status_box.info, prog_bar.progress)
            fname, meta = factory.run()
            
            st.success("🎉 اكتمل الكتاب بنجاح!")
            send_to_telegram(fname, theme, meta)
            
            with st.expander("📊 خطة التسويق لـ KDP"):
                st.write(meta)
                
            with open(fname, "rb") as f:
                st.download_button("⬇️ تحميل الكتاب (PDF)", f, file_name=fname, use_container_width=True)
                
        except Exception as e:
            st.error("❌ حدث خطأ تقني:")
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

