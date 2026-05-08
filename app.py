"""
KDP Factory Pro - الإصدار الملكي V14.0
تصميم وبرمجة: إروين سميث | المحرك: AI المدرع بنظام الصفحات المتقابلة
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
# إعدادات الواجهة والجماليات
# ------------------------------------------------------------------------------
st.set_page_config(page_title="KDP Factory Pro V14", page_icon="👑", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    .main-title {
        background: linear-gradient(120deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 45px; font-weight: 900; text-align: center; margin: 0;
    }
    .status-card { background: #ffffff; border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-right: 8px solid #764ba2; }
    .stButton > button { background: linear-gradient(90deg, #667eea, #764ba2); color: white; border-radius: 30px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# المحرك الذكي (Gemini & Images)
# ------------------------------------------------------------------------------
def get_api_keys():
    keys = [os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 4)]
    return [k.strip() for k in keys if k and k.strip()]

API_KEYS = get_api_keys() or ["DUMMY"]

class GeminiEngine:
    MODELS = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    @classmethod
    def ask(cls, prompt):
        if API_KEYS[0] == "DUMMY": return "A magical journey begins!||He saw a big star.||The hero smiled."
        for key in API_KEYS:
            genai.configure(api_key=key)
            for m_name in cls.MODELS:
                try:
                    res = genai.GenerativeModel(m_name).generate_content(prompt)
                    if res.text: return res.text.strip()
                except: continue
        return "Default adventure text for the story."

class ImageGenerator:
    @staticmethod
    def generate(prompt, filename, style="coloring"):
        styles = {
            "coloring": "bold black and white line art, thick outlines, pure white background, no shading",
            "dots": "simple dot-to-dot puzzle for kids, numbered dots forming a shape, black and white, white background",
            "cover": "vibrant colorful children's book cover, high resolution, professional cartoon style, NO text"
        }
        full_p = f"{styles.get(style, styles['coloring'])}, {prompt}"
        for _ in range(3):
            try:
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200 and len(resp.content) > 18000:
                    with open(filename, "wb") as f: f.write(resp.content)
                    return True
            except: time.sleep(1)
        return False

# ------------------------------------------------------------------------------
# محرك الألغاز المتقدم
# ------------------------------------------------------------------------------
class PuzzleEngine:
    @staticmethod
    def maze(w=12, h=12):
        grid = [[{'N':True, 'S':True, 'E':True, 'W':True, 'v':False} for _ in range(w)] for _ in range(h)]
        stack, grid[0][0]['v'] = [(0, 0)], True
        while stack:
            cx, cy = stack[-1]
            dirs = [('N', 0,-1,'S'), ('S', 0,1,'N'), ('E', 1,0,'W'), ('W', -1,0,'E')]
            random.shuffle(dirs)
            moved = False
            for d, dx, dy, opp in dirs:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < w and 0 <= ny < h and not grid[ny][nx]['v']:
                    grid[cy][cx][d]=False; grid[ny][nx][opp]=False; grid[ny][nx]['v']=True
                    stack.append((nx, ny)); moved=True; break
            if not moved: stack.pop()
        grid[0][0]['W'] = False; grid[h-1][w-1]['E'] = False
        return grid

    @staticmethod
    def sudoku():
        b = 3; s = b*b; rb = range(b)
        rows = [g*b + r for g in random.sample(rb,b) for r in random.sample(rb,b)]
        cols = [g*b + c for g in random.sample(rb,b) for c in random.sample(rb,b)]
        nums = random.sample(range(1,s+1),s)
        board = [[nums[(b*(r%b)+r//base+c)%s] for c in cols] for r in rows] # Note: simplistic fill
        for p in random.sample(range(s*s), s*s*2//3): board[p//s][p%s] = 0
        return board

# ------------------------------------------------------------------------------
# صانع الكتاب المتطور (KDP Expert)
# ------------------------------------------------------------------------------
class KDPBook(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(False)
        # Gutter margin (0.75 + 0.125) لضمان عدم اختفاء المحتوى عند التجليد
        self.set_margins(0.875, 0.5, 0.75)

    def title_page(self, theme):
        self.add_page(); self.set_font("Arial", "B", 36); self.set_y(4)
        self.cell(0, 1, f"THE BIG BOOK OF", align="C", ln=True)
        self.cell(0, 1, theme.upper(), align="C", ln=True)

# ------------------------------------------------------------------------------
# المحرك الملكي للإنتاج
# ------------------------------------------------------------------------------
class RoyalProductionEngine:
    def __init__(self, config, ui_status, ui_progress):
        self.config = config
        self.status = ui_status
        self.progress = ui_progress
        self.pdf = KDPBook()

    def run(self):
        t, p, m = self.config['theme'], self.config['pages'], self.config['mode']
        
        # 1. الغلاف
        self.status.info("🎨 جاري تصميم الغلاف الملكي...")
        if ImageGenerator.generate(f"happy {t} characters, children's book", "c.jpg", "cover"):
            self.pdf.add_page(); self.pdf.image("c.jpg", x=0, y=0, w=8.5, h=11); os.remove("c.jpg")
        
        self.pdf.title_page(t)

        # 2. توليد المحتوى حسب النوع
        if m == "قصص ورسومات":
            self._story_and_color_mode(p, t)
        elif m == "كتب تعليم (A-Z)":
            self._alphabet_mode(p)
        elif m == "وصل النقاط (رسم)":
            self._dot_to_dot_mode(p, t)
        elif m == "ألغاز منوعة":
            self._puzzles_mode(p, t)
        else: # منوع (الكل)
            self._mixed_mode(p, t)

        fname = f"KDP_Royal_{t.replace(' ', '_')}_{int(time.time())}.pdf"
        self.pdf.output(fname)
        meta = GeminiEngine.ask(f"Write KDP SEO listing for {t} book. Title, Subtitle, 7 Keywords, Description.")
        return fname, meta

    def _story_and_color_mode(self, count, theme):
        raw = GeminiEngine.ask(f"Write a {count} part story about {theme}. Each part 2 short sentences. Split with '||'.")
        parts = [p.strip() for p in raw.split('||')][:count]
        for i, text in enumerate(parts):
            self.status.write(f"📖 جاري معالجة الزوج القصصي {i+1} من {count}...")
            # صفحة القصة (على اليمين)
            self.pdf.add_page(); self.pdf.set_font("Arial", "I", 20); self.pdf.set_y(4)
            self.pdf.multi_cell(0, 0.5, text, align="C")
            # صفحة التلوين المقابلة (على اليسار)
            self.status.write(f"🖌️ رسم المشهد المخصص لـ: {text[:30]}...")
            if ImageGenerator.generate(f"scene of {text[:50]}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=2, w=6.5, h=6.5); os.remove("t.jpg")
            else: self.pdf.add_page()
            self.ui_progress((i+1)/count)

    def _alphabet_mode(self, count):
        letters = list(string.ascii_uppercase)[:min(count, 26)]
        for i, L in enumerate(letters):
            self.status.write(f"✏️ جاري تصميم صفحة الحرف {L}...")
            # صفحة الكتابة والتتبع
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 120); self.pdf.set_y(2)
            self.pdf.cell(0, 1.5, L, align="C", ln=True)
            self.pdf.set_font("Arial", "", 24); self.pdf.cell(0, 1, f"Practice Writing {L}", align="C")
            # صفحة التلوين المقابلة
            item = GeminiEngine.ask(f"One word starting with {L} for kids coloring.").strip()
            if ImageGenerator.generate(f"a cute {item}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1.5, y=2.5, w=5.5, h=5.5); os.remove("t.jpg")
            else: self.pdf.add_page()
            self.ui_progress((i+1)/len(letters))

    def _dot_to_dot_mode(self, count, theme):
        for i in range(count):
            self.status.write(f"📍 جاري رسم لغز وصل النقاط رقم {i+1}...")
            # صفحة فارغة للرسم الحر
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 20); self.pdf.set_y(4); self.pdf.cell(0, 1, "Your Drawing Space", align="C")
            # صفحة لغز النقاط المقابلة
            if ImageGenerator.generate(f"dot-to-dot puzzle of {theme}", "t.jpg", "dots"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=1.5, w=6.5, h=7.5); os.remove("t.jpg")
            else: self.pdf.add_page()

    def _puzzles_mode(self, count, theme):
        per = count // 2
        for i in range(per):
            self.status.write(f"🧩 بناء المتاهة والسودوكو {i+1}...")
            # المتاهة
            g = PuzzleEngine.maze(); self.pdf.add_page(); sx, sy, cs = 1.8, 2.5, 0.4
            for y in range(12):
                for x in range(12):
                    px, py = sx+x*cs, sy+y*cs
                    if g[y][x]['N']: self.pdf.line(px, py, px+cs, py)
                    if g[y][x]['S']: self.pdf.line(px, py+cs, px+cs, py+cs)
                    if g[y][x]['E']: self.pdf.line(px+cs, py, px+cs, py+cs)
                    if g[y][x]['W']: self.pdf.line(px, py, px, py+cs)
            # سودوكو مقابلة (تبسيط الرسم)
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(4); self.pdf.cell(0, 1, "Sudoku Coming Soon", align="C")

# ------------------------------------------------------------------------------
# واجهة التحكم والتشغيل
# ------------------------------------------------------------------------------
def main():
    st.markdown('<h1 class="main-title">📚 KDP Factory Pro V14 👑</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#888;">نظام الصفحات المتقابلة والتنسيق الملكي للمحترفين</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        u_theme = st.text_input("🎯 موضوع/نيش الكتاب:", "Space Cats Adventure")
        u_pages = st.slider("📄 عدد أزواج الصفحات:", 10, 50, 15)
    with col2:
        modes = ["قصص ورسومات", "كتب تعليم (A-Z)", "وصل النقاط (رسم)", "ألغاز منوعة", "منوع (الكل)"]
        u_mode = st.selectbox("🎭 نوع التنسيق المتقابل:", modes)

    if st.button("🚀 ابدأ الإنتاج الملكي والتنسيق", use_container_width=True):
        status_c = st.container()
        with status_c:
            s_msg = st.empty(); p_bar = st.progress(0)
            try:
                engine = RoyalProductionEngine({'theme':u_theme, 'pages':u_pages, 'mode':u_mode}, s_msg, p_bar.progress)
                file, meta = engine.run()
                st.success("🎉 اكتمل الكتاب بالتنسيق المتقابل بنجاح!")
                st.info(f"**KDP Meta Info:**\n\n{meta}")
                with open(file, "rb") as f: st.download_button("⬇️ تحميل الملف (PDF)", f, file_name=file)
                if TELEGRAM_TOKEN:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ مبروك! كتاب {u_theme} جاهز للرفع."}, files={"document": open(file, "rb")})
            except Exception as e:
                st.error(f"❌ حدث خطأ: {e}"); st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

