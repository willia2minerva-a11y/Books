"""
KDP Factory Pro - The All-In-One Elite V22
Architect & Creator: Irwin Smith | AI Logic: Final Stability Shield
Features: Open Mode, Factory Mode, Facing Pages, Parallel Images, Session Fix
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
import re
import concurrent.futures
from datetime import datetime

# ------------------------------------------------------------------------------
# 1. 🛡️ درع تهيئة الجلسة (يجب أن يكون في أول الكود)
# ------------------------------------------------------------------------------
if 'session_initialized' not in st.session_state:
    st.session_state['session_initialized'] = True
    time.sleep(1) # تأخير طفيف لضمان استقرار WebSocket

# ------------------------------------------------------------------------------
# 2. إعدادات الواجهة و CSS المعالج (RTL Support)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="KDP Factory Pro", page_icon="👑", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    p, h1, h2, h3, h4, h5, h6, label, .stMarkdown {
        font-family: 'Cairo', sans-serif; direction: rtl; text-align: right;
    }
    .main-title {
        background: linear-gradient(120deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 45px; font-weight: 900; text-align: center; margin: 0; direction: ltr;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 10px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #667eea; color: white; }
    input, textarea { text-align: left !important; direction: ltr !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. إدارة المفاتيح والتنظيف
# ------------------------------------------------------------------------------
def get_api_keys():
    keys = [os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 6)]
    return [k.strip() for k in keys if k and k.strip()]

API_KEYS = get_api_keys() or ["DUMMY"]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def clean_text(text):
    if not text: return ""
    return text.encode('latin-1', 'ignore').decode('latin-1').replace('\n', ' ')

# ------------------------------------------------------------------------------
# 4. محركات الذكاء الاصطناعي والصور
# ------------------------------------------------------------------------------
class GeminiEngine:
    MODELS = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    @classmethod
    def ask(cls, prompt):
        if API_KEYS[0] == "DUMMY": return ""
        for key in API_KEYS:
            genai.configure(api_key=key)
            for m_name in cls.MODELS:
                try:
                    res = genai.GenerativeModel(m_name).generate_content(prompt)
                    if res.text: return res.text.strip()
                except: continue
        return ""

class ImageGenerator:
    @staticmethod
    def generate(prompt, filename, style="coloring"):
        styles = {
            "coloring": "bold black and white line art, thick outlines, white background, NO shading, NO gray, kids style",
            "dots": "simple dot-to-dot puzzle for kids, numbered dots, black and white, white background",
            "cover": "vibrant colorful kids book cover illustration, professional, BLANK COVER NO TEXT NO LETTERS"
        }
        full_p = f"{styles.get(style, styles['coloring'])}, {prompt}"
        for _ in range(3):
            try:
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
                resp = requests.get(url, timeout=25)
                if resp.status_code == 200 and 'image' in resp.headers.get('content-type', '').lower():
                    with open(filename, "wb") as f: f.write(resp.content)
                    return True
            except: time.sleep(1)
        return False

# ------------------------------------------------------------------------------
# 5. محرك الألغاز المبرمج
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
        board = [[nums[(b*(r%b)+r//b+c)%s] for c in cols] for r in rows]
        for p in random.sample(range(s*s), s*s*2//3): board[p//s][p%s] = 0
        return board

# ------------------------------------------------------------------------------
# 6. صانع الكتاب KDP
# ------------------------------------------------------------------------------
class KDPBook(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(False)
        self.set_margins(0.875, 0.5, 0.75)

# ------------------------------------------------------------------------------
# 7. محرك الإنتاج الشامل
# ------------------------------------------------------------------------------
class ProductionEngine:
    def __init__(self, config, log_func):
        self.config = config
        self.log = log_func
        self.pdf = KDPBook()

    def run(self):
        t, p, m = self.config['theme'], self.config['pages'], self.config['mode']
        self.log(f"🎨 جاري إنشاء غلاف احترافي لـ {t[:30]}...")
        if ImageGenerator.generate(f"happy {t[:30]} kids book", "c.jpg", "cover"):
            self.pdf.add_page(); self.pdf.image("c.jpg", x=0, y=0, w=8.5, h=11); os.remove("c.jpg")
        
        self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(4)
        self.pdf.multi_cell(0, 0.5, f"THE BIG BOOK OF\n{clean_text(t).upper()}", align="C")

        # توزيع المهام
        if m == "تلوين فقط": self._coloring_mode(p, t)
        elif m == "قصص ورسومات": self._story_mode(p, t)
        elif m == "تعليم (A-Z)": self._alphabet_mode(p)
        elif m == "ألغاز منوعة": self._puzzles_mode(p, t)
        elif m == "وصل النقاط": self._dots_mode(p, t)
        elif m == "ملاحظات مسطرة": self._lined_mode(p)
        else: # منوع
            part = max(1, p // 3)
            self._coloring_mode(part, t)
            self._puzzles_mode(part, t)
            self._story_mode(max(1, p - (part*2)), t)

        clean_theme = re.sub(r'[^a-zA-Z0-9]', '_', t)[:30]
        fname = f"KDP_{clean_theme}_{int(time.time())}.pdf"
        self.pdf.output(fname)
        
        self.log("📝 جاري كتابة معلومات النشر (SEO)...")
        meta = GeminiEngine.ask(f"Act as Amazon KDP Expert. Write Title, Subtitle, 7 Keywords, and Description for a '{t}' kids activity book.")
        return fname, meta

    def _coloring_mode(self, count, theme):
        items = GeminiEngine.ask(f"List {count+5} coloring items for {theme}. One per line.").split('\n')
        success = 0
        for item in items:
            if success >= count: break
            if len(item.strip()) < 3: continue
            self.log(f"🖌️ رسم صفحة التلوين {success+1}: {item[:20]}")
            if ImageGenerator.generate(f"cute {item}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=1.5, w=6.5, h=6.5)
                self.pdf.add_page(); os.remove("t.jpg"); success += 1

    def _story_mode(self, count, theme):
        raw = GeminiEngine.ask(f"Write {count} part story about {theme}. Split with '||'. Each part 2 short sentences.")
        parts = [p.strip() for p in raw.split('||')][:count]
        for i, text in enumerate(parts):
            self.log(f"📖 إنشاء الزوج القصصي {i+1}...")
            self.pdf.add_page(); self.pdf.set_font("Arial", "I", 18); self.pdf.set_y(4)
            self.pdf.multi_cell(0, 0.5, clean_text(text), align="C")
            if ImageGenerator.generate(f"coloring page of {text[:40]}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=2, w=6.5, h=6.5); os.remove("t.jpg")
            else: self.pdf.add_page()
            self.pdf.add_page()

    def _puzzles_mode(self, count, theme):
        per = max(1, count // 2)
        # Sudoku
        for i in range(per):
            self.log(f"🧩 بناء سودوكو {i+1}...")
            b = PuzzleEngine.sudoku(); self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1)
            self.pdf.cell(0, 1, f"Sudoku #{i+1}", align="C", ln=True)
            sx, sy, cs = 1.25, 2.5, 0.66
            self.pdf.set_line_width(0.01)
            for r in range(9):
                for c in range(9):
                    self.pdf.rect(sx+c*cs, sy+r*cs, cs, cs)
                    if b[r][c] != 0: self.pdf.text(sx+c*cs+0.25, sy+r*cs+0.45, str(b[r][c]))
            self.pdf.set_line_width(0.05)
            for k in range(4):
                self.pdf.line(sx+k*3*cs, sy, sx+k*3*cs, sy+9*cs)
                self.pdf.line(sx, sy+k*3*cs, sx+9*cs, sy+k*3*cs)

        # Maze
        maze_t = GeminiEngine.ask(f"For {theme} maze: Hero | Goal").split('|')
        s_txt = maze_t[0].strip() if len(maze_t)>0 else "Start"
        g_txt = maze_t[1].strip() if len(maze_t)>1 else "Goal"
        for i in range(per):
            self.log(f"🌀 بناء متاهة {i+1}...")
            g = PuzzleEngine.maze(); self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(0.8)
            self.pdf.cell(0, 1, f"Maze #{i+1}", align="C", ln=True)
            sx, sy, cs = 1.8, 2.5, 0.4
            self.pdf.set_font("Arial", "B", 12); self.pdf.text(sx, sy-0.2, f"Start: {s_txt}")
            self.pdf.set_line_width(0.04)
            for y in range(12):
                for x in range(12):
                    if g[y][x]['N']: self.pdf.line(sx+x*cs, sy+y*cs, sx+(x+1)*cs, sy+y*cs)
                    if g[y][x]['S']: self.pdf.line(sx+x*cs, sy+(y+1)*cs, sx+(x+1)*cs, sy+(y+1)*cs)
                    if g[y][x]['E']: self.pdf.line(sx+(x+1)*cs, sy+y*cs, sx+(x+1)*cs, sy+(y+1)*cs)
                    if g[y][x]['W']: self.pdf.line(sx+x*cs, sy+y*cs, sx+x*cs, sy+(y+1)*cs)
            self.pdf.text(sx + 8*cs, sy + 12*cs + 0.3, f"Goal: {g_txt}")

    def _alphabet_mode(self, count):
        L = list(string.ascii_uppercase)[:min(count, 26)]
        for char in L:
            self.log(f"✏️ تصميم الحرف {char}...")
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 100); self.pdf.set_y(2); self.pdf.cell(0, 1.5, char, align="C", ln=True)
            item = GeminiEngine.ask(f"One word starting with {char} for coloring.").strip()
            if ImageGenerator.generate(f"a cute {item}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1.5, y=2.5, w=5.5, h=5.5); os.remove("t.jpg")
            else: self.pdf.add_page()
            self.pdf.add_page()

    def _dots_mode(self, count, theme):
        for i in range(count):
            self.log(f"📍 رسم وصل النقاط {i+1}...")
            if ImageGenerator.generate(f"dot-to-dot puzzle of {theme}", "t.jpg", "dots"):
                self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(4); self.pdf.cell(0, 1, "Draw Space", align="C")
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=1.5, w=6.5, h=7.5); os.remove("t.jpg")
                self.pdf.add_page()

    def _lined_mode(self, count):
        for _ in range(count):
            self.pdf.add_page(); self.pdf.set_draw_color(200); self.pdf.set_line_width(0.01)
            for i in range(2, 11): self.pdf.line(1, i, 7.5, i)

# ------------------------------------------------------------------------------
# 8. واجهة التحكم والتشغيل
# ------------------------------------------------------------------------------
def check_auto():
    try:
        if hasattr(st, 'query_params'): return st.query_params.get("auto") == "true"
        return st.experimental_get_query_params().get("auto", [""])[0] == "true"
    except: return False

def main():
    if check_auto():
        theme = clean_text(GeminiEngine.ask("Suggest ONE KDP niche phrase (2 words).").strip())
        eng = ProductionEngine({'theme':theme, 'pages':24, 'mode':'منوع'}, lambda x: print(x))
        f, meta = eng.run()
        if TELEGRAM_TOKEN:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ {theme}"}, files={"document": open(f, "rb")})
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": meta})
        return

    st.markdown('<h1 class="main-title">📚 KDP Factory Pro V22 👑</h1>', unsafe_allow_html=True)
    tabs = st.tabs(["⚡ الطور السريع", "💡 طور العبقري", "⚙️ الإعدادات"])

    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            u_t = st.text_input("🎯 موضوع الكتاب:", "Ocean Adventures")
            u_p = st.number_input("📄 عدد الصفحات:", 12, 100, 24)
        with c2:
            u_m = st.selectbox("🎭 النوع:", ["تلوين فقط", "قصص ورسومات", "ألغاز منوعة", "تعليم (A-Z)", "وصل النقاط", "ملاحظات مسطرة", "منوع"])
        if st.button("🚀 ابدأ الإنتاج السريع", use_container_width=True):
            run_prod(u_t, u_p, u_m)

    with tabs[1]:
        o_t = st.text_input("🎯 الموضوع الأساسي:", placeholder="قطط النينجا...")
        o_d = st.text_area("📝 وصف الفكرة:", placeholder="أريد كتاب ألغاز مضحك...")
        o_p = st.number_input("📄 عدد الصفحات:", 12, 150, 30, key="open_p")
        if st.button("🪄 نفذ فكرتي العبقرية", use_container_width=True):
            with st.spinner("جاري التحليل..."):
                plan = GeminiEngine.ask(f"Idea: {o_t}. Suggest best type: [قصص ورسومات, منوع, ألغاز منوعة]. Output strictly Arabic name.")
                run_prod(o_t, o_p, plan if plan in ["قصص ورسومات", "منوع", "ألغاز منوعة"] else "منوع")

    with tabs[2]:
        st.success("Gemini & Telegram connection is managed via Render Env Vars.")

def run_prod(t, p, m):
    stat = st.empty()
    try:
        engine = ProductionEngine({'theme':t, 'pages':p, 'mode':m}, stat.info)
        f, meta = engine.run()
        stat.success("🎉 تم الإنتاج! تفحص تليجرام.")
        st.info(f"**Amazon SEO Metadata:**\n\n{meta}")
        with open(f, "rb") as b: st.download_button("⬇️ تحميل PDF", b, file_name=f)
        if TELEGRAM_TOKEN:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ {t} Ready!"}, files={"document": open(f, "rb")})
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": meta})
    except Exception as e: st.error(f"❌ Error: {e}"); st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

