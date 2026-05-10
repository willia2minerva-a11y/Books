"""
KDP Factory Pro - The Parallel Titan V20.0
Architect: Irwin Smith | AI Logic: Parallel Shield
Features: Multi-threading Image Gen, Zero-Crash Fallbacks, Perfect KDP Layouts
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
# 1. منع انهيار الجلسة
# ------------------------------------------------------------------------------
if 'init' not in st.session_state:
    st.session_state.init = True

st.set_page_config(page_title="KDP Factory Pro", page_icon="👑", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .main-title {
        background: linear-gradient(120deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 45px; font-weight: 900; text-align: center; margin: 0; direction: ltr;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 10px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #667eea; color: white; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. الإعدادات والتنظيف
# ------------------------------------------------------------------------------
def get_api_keys():
    keys = [os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 4)]
    return [k.strip() for k in keys if k and k.strip()]

API_KEYS = get_api_keys() or ["DUMMY"]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def clean_text(text):
    if not text: return ""
    return text.encode('latin-1', 'ignore').decode('latin-1').replace('\n', ' ')

# ------------------------------------------------------------------------------
# 3. محركات الذكاء الاصطناعي (موازية)
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
            "coloring": "bold black and white line art, extremely thick clean outlines, pure white background, coloring book style, strictly NO shading, NO gray, simple vector for kids",
            "dots": "simple dot-to-dot puzzle for kids, numbered dots forming a shape, black and white, white background",
            "cover": "vibrant colorful children's book cover, professional cartoon style, blank background, strictly NO words, NO letters, NO text, NO typography, blank cover"
        }
        full_p = f"{styles.get(style, styles['coloring'])}, {prompt}"
        for _ in range(3):
            try:
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200 and len(resp.content) > 15000:
                    with open(filename, "wb") as f: f.write(resp.content)
                    return True
            except: time.sleep(1)
        return False

    @staticmethod
    def generate_parallel(tasks, max_workers=3):
        """تقنية التوليد المتوازي لإنشاء عدة صور في نفس الوقت"""
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(ImageGenerator.generate, p, f, s): f for p, f, s in tasks}
            for future in concurrent.futures.as_completed(future_to_file):
                f = future_to_file[future]
                try:
                    results[f] = future.result()
                except:
                    results[f] = False
        return results

# ------------------------------------------------------------------------------
# 4. محرك الألغاز
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

    @staticmethod
    def word_search(theme):
        raw = clean_text(GeminiEngine.ask(f"Give 6 simple words for '{theme}'. Comma separated. No spaces.")).upper()
        words = [w.strip() for w in raw.replace('\n', '').split(',')]
        words = [w for w in words if w.isalpha() and 3 <= len(w) <= 8][:6]
        if len(words) < 6: words = ["HERO", "MAGIC", "POWER", "SECRET", "BRAVE", "QUEST"]

        size = 10; grid = [[' ' for _ in range(size)] for _ in range(size)]
        for w in words:
            for _ in range(50):
                d = random.choice([(0,1), (1,0)])
                r, c = random.randint(0, size - 1 - (len(w)-1)*d[0]), random.randint(0, size - 1 - (len(w)-1)*d[1])
                if all(grid[r+i*d[0]][c+i*d[1]] in (' ', w[i]) for i in range(len(w))):
                    for i in range(len(w)): grid[r+i*d[0]][c+i*d[1]] = w[i]
                    break
        for r in range(size):
            for c in range(size):
                if grid[r][c] == ' ': grid[r][c] = random.choice(string.ascii_uppercase)
        return grid, words

# ------------------------------------------------------------------------------
# 5. صانع الكتاب KDP
# ------------------------------------------------------------------------------
class KDPBook(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(False)
        self.set_margins(0.875, 0.5, 0.75)

    def add_lined_page(self):
        self.add_page(); self.set_draw_color(200, 200, 200); self.set_line_width(0.01)
        for i in range(2, 10): self.line(1, i, 7.5, i)

# ------------------------------------------------------------------------------
# 6. المحرك الجبار للتوليد
# ------------------------------------------------------------------------------
class ProductionEngine:
    def __init__(self, config, log_func):
        self.config = config
        self.log = log_func
        self.pdf = KDPBook()

    def run(self):
        t, p, m = self.config['theme'], self.config['pages'], self.config['mode']
        
        self.log(f"🎨 جاري رسم الغلاف الاحترافي...")
        if ImageGenerator.generate(f"cute {t[:30]} kids book cover", "cover.jpg", "cover"):
            self.pdf.add_page(); self.pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11); os.remove("cover.jpg")
        
        self.pdf.add_page(); self.pdf.set_font("Arial", "B", 36); self.pdf.set_y(4)
        self.pdf.set_font("Arial", "B", 24)
        clean_t = clean_text(t)
        self.pdf.multi_cell(0, 0.5, f"THE BIG BOOK OF\n{clean_t.upper()}", align="C")

        # معالجة قوية لمنع توقف السيرفر (Try-Except Blocks)
        try:
            if m == "تلوين فقط": self._coloring_mode(p, t)
            elif m == "قصص ورسومات": self._story_mode(p, t)
            elif m == "ألغاز منوعة": self._puzzles_mode(p, t)
            elif m == "تعليم (A-Z)": self._alphabet_mode(p)
            elif m == "كوميكس فقط": self._comics_mode(p, t)
            elif m == "وصل النقاط": self._dots_mode(p, t)
            elif m == "ملاحظات مسطرة": self._lined_mode(p)
            else:
                part = max(1, p // 3)
                self._coloring_mode(part, t)
                self._puzzles_mode(part, t)
                self._comics_mode(part, t)
        except Exception as e:
            self.log(f"⚠️ تحذير: تم تجاوز خطأ داخلي لإكمال الكتاب ({e})")

        # حفظ الملف
        clean_theme = re.sub(r'[^a-zA-Z0-9]', '_', t)[:30]
        fname = f"KDP_{clean_theme}_{int(time.time())}.pdf"
        self.pdf.output(fname)
        
        # استخراج الـ SEO بأمان
        self.log("📝 جاري كتابة معلومات النشر...")
        meta = GeminiEngine.ask(f"Act as KDP expert. Write Amazon listing for '{t}' kids book. Title, Subtitle, 7 Keywords, Short Description.")
        if not meta or len(meta) < 10:
            meta = f"Title: The Ultimate {t} Book\nSubtitle: Fun Activities for Kids\nKeywords: kids book, {t}, activity, coloring, puzzles\nDescription: An amazing book filled with fun activities!"
            
        return fname, meta

    def _coloring_mode(self, count, theme):
        self.log(f"🧠 جاري التفكير وطلب الصور بشكل متوازي...")
        raw = GeminiEngine.ask(f"List {count+5} simple items for {theme} coloring. One per line. Only names.")
        items = [clean_text(x.strip()[:20]) for x in raw.split('\n') if len(x.strip()) > 2]
        
        # قائمة طوارئ إذا فشل غيميني
        if len(items) < count:
            items = [f"{theme} character {i}" for i in range(count+2)]

        # تجهيز المهام للتوليد المتوازي
        tasks = []
        for i in range(count):
            tasks.append((f"cute {items[i]}", f"col_{i}.jpg", "coloring"))
            
        self.log("⚡ جاري رسم الصفحات معاً (تسريع متوازي)...")
        results = ImageGenerator.generate_parallel(tasks, max_workers=3)

        for i in range(count):
            fname = f"col_{i}.jpg"
            if results.get(fname, False):
                self.pdf.add_page(); self.pdf.image(fname, x=1, y=1.5, w=6.5, h=6.5)
                self.pdf.add_page(); os.remove(fname) # صفحة ظهر فارغة للحماية

    def _story_mode(self, count, theme):
        self.log("📖 جاري كتابة القصة وتوليد المشاهد...")
        raw = GeminiEngine.ask(f"Write {count} part story about {theme}. Part=2 sentences. Split '||'.")
        parts = [clean_text(p.strip()) for p in raw.split('||') if len(p) > 5]
        
        if len(parts) < count:
            parts = [f"The {theme} hero continued the adventure." for _ in range(count)]

        tasks = []
        for i in range(count):
            tasks.append((f"scene for {parts[i][:30]}", f"story_{i}.jpg", "coloring"))
            
        results = ImageGenerator.generate_parallel(tasks, max_workers=3)

        for i in range(count):
            fname = f"story_{i}.jpg"
            self.pdf.add_page(); self.pdf.set_font("Arial", "I", 22); self.pdf.set_y(4)
            self.pdf.multi_cell(0, 0.5, parts[i], align="C")
            if results.get(fname, False):
                self.pdf.add_page(); self.pdf.image(fname, x=1, y=2, w=6.5, h=6.5); os.remove(fname)
            else: self.pdf.add_page()
            self.pdf.add_page()

    def _alphabet_mode(self, count):
        L = list(string.ascii_uppercase)[:min(count, 26)]
        tasks = []
        for i, char in enumerate(L):
            tasks.append((f"object starting with letter {char}", f"alpha_{i}.jpg", "coloring"))
            
        self.log("✏️ جاري توليد الحروف والرسومات متوازياً...")
        results = ImageGenerator.generate_parallel(tasks, max_workers=3)

        for i, char in enumerate(L):
            fname = f"alpha_{i}.jpg"
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 120); self.pdf.set_y(2); self.pdf.cell(0, 1.5, char, align="C", ln=True)
            self.pdf.set_font("Arial", "", 24); self.pdf.cell(0, 1, f"Practice Writing {char}", align="C")
            
            if results.get(fname, False):
                self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1)
                self.pdf.cell(0, 1, f"{char} is for Awesome", align="C")
                self.pdf.image(fname, x=1.5, y=2.5, w=5.5, h=5.5); os.remove(fname)
            else: self.pdf.add_page()
            self.pdf.add_page()

    def _puzzles_mode(self, count, theme):
        per = max(1, count // 3)
        self.log(f"🧩 جاري بناء {per} سودوكو، {per} متاهات، {per} كلمات...")
        # Sudoku (Perfect Grid)
        for i in range(per):
            b = PuzzleEngine.sudoku(); self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1); self.pdf.cell(0, 1, f"Sudoku #{i+1}", align="C")
            sx, sy, cs = 1.25, 2.5, 0.66
            self.pdf.set_line_width(0.01); self.pdf.set_draw_color(150, 150, 150)
            for r in range(9):
                for c in range(9):
                    self.pdf.rect(sx+c*cs, sy+r*cs, cs, cs)
                    if b[r][c] != 0: self.pdf.set_font("Arial", "B", 20); self.pdf.text(sx+c*cs+0.25, sy+r*cs+0.45, str(b[r][c]))
            self.pdf.set_line_width(0.06); self.pdf.set_draw_color(0, 0, 0)
            for k in range(4):
                self.pdf.line(sx + k*3*cs, sy, sx + k*3*cs, sy + 9*cs)
                self.pdf.line(sx, sy + k*3*cs, sx + 9*cs, sy + k*3*cs)

        # Themed Maze
        maze_theme = clean_text(GeminiEngine.ask(f"Start and end character for a {theme} maze. Format: Hero | Goal"))
        if '|' in maze_theme: start_txt, goal_txt = maze_theme.split('|', 1)
        else: start_txt, goal_txt = "Start", "Finish"
        
        for i in range(per):
            g = PuzzleEngine.maze(); self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(0.5); self.pdf.cell(0, 1, f"Maze #{i+1}", align="C")
            sx, sy, cs = 1.8, 2.5, 0.4
            self.pdf.set_font("Arial", "B", 14); self.pdf.text(sx, sy - 0.2, f"Start: {start_txt.strip()[:15]}")
            self.pdf.set_line_width(0.04)
            for y in range(12):
                for x in range(12):
                    if g[y][x]['N']: self.pdf.line(sx+x*cs, sy+y*cs, sx+(x+1)*cs, sy+y*cs)
                    if g[y][x]['S']: self.pdf.line(sx+x*cs, sy+(y+1)*cs, sx+(x+1)*cs, sy+(y+1)*cs)
                    if g[y][x]['E']: self.pdf.line(sx+(x+1)*cs, sy+y*cs, sx+(x+1)*cs, sy+(y+1)*cs)
                    if g[y][x]['W']: self.pdf.line(sx+x*cs, sy+y*cs, sx+x*cs, sy+(y+1)*cs)
            self.pdf.set_font("Arial", "B", 14); self.pdf.text(sx + 8*cs, sy + 12*cs + 0.3, f"Goal: {goal_txt.strip()[:15]}")

        # Word Search
        for i in range(per):
            grid, words = PuzzleEngine.word_search(theme)
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1); self.pdf.cell(0, 1, f"Word Search #{i+1}", align="C")
            sx, sy, cs = 1.75, 2.5, 0.5
            for r in range(10):
                for c in range(10): self.pdf.text(sx + c*cs, sy + r*cs, grid[r][c])
            self.pdf.set_font("Arial", "", 16); self.pdf.set_y(8.0)
            self.pdf.cell(0, 0.5, "Find: " + " - ".join(words), align="C", ln=True)

    def _comics_mode(self, count, theme):
        self.log("🦸 جاري طباعة قوالب الكوميكس...")
        for i in range(count):
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(0.8); self.pdf.cell(0, 1, f"Draw Your {clean_text(theme)[:20]} Comic", align="C")
            self.pdf.set_line_width(0.04); self.pdf.set_draw_color(0, 0, 0)
            self.pdf.rect(0.75, 1.8, 3.4, 4); self.pdf.rect(4.35, 1.8, 3.4, 4); self.pdf.rect(0.75, 6.0, 7, 4.2)

    def _dots_mode(self, count, theme):
        self.log("📍 جاري تجهيز وصل النقاط بالتوازي...")
        raw = GeminiEngine.ask(f"Give {count} items related to {theme}. One per line.")
        items = [clean_text(x.strip()[:20]) for x in raw.split('\n') if len(x.strip()) > 2]
        if len(items) < count: items = [f"dot puzzle {i}" for i in range(count)]
        
        tasks = []
        for i in range(count): tasks.append((f"dot-to-dot puzzle of {items[i]}", f"dots_{i}.jpg", "dots"))
        results = ImageGenerator.generate_parallel(tasks, max_workers=3)

        for i in range(count):
            fname = f"dots_{i}.jpg"
            if results.get(fname, False):
                self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(4); self.pdf.cell(0, 1, "Draw Freehand Here", align="C")
                self.pdf.add_page(); self.pdf.image(fname, x=1, y=1.5, w=6.5, h=7.5); os.remove(fname)
                self.pdf.add_page()

    def _lined_mode(self, count):
        self.log("📏 جاري التسطير الهندسي...")
        for _ in range(count): self.pdf.add_lined_page()

# ------------------------------------------------------------------------------
# 7. واجهة التشغيل والوضع الآلي
# ------------------------------------------------------------------------------
def check_auto():
    try:
        if hasattr(st, 'query_params'): return st.query_params.get("auto") == "true"
        return st.experimental_get_query_params().get("auto", [""])[0] == "true"
    except: return False

def main():
    if check_auto():
        if API_KEYS[0] == "DUMMY": st.stop()
        theme = clean_text(GeminiEngine.ask("Output ONLY 2 to 4 words highly profitable KDP niche kids book. JUST THE WORDS.").replace('*', '').strip()[:40])
        eng = ProductionEngine({'theme':theme, 'pages':24, 'mode':'منوع'}, lambda x: print(x))
        try:
            f, meta = eng.run()
            if TELEGRAM_TOKEN:
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ كتاب آلي: {theme}"}, files={"document": open(f, "rb")})
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": meta})
        except: pass
        return

    st.markdown('<h1 class="main-title">📚 KDP Factory Pro V20 👑</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#888; font-weight:bold; direction:ltr;">By Irwin Smith | Multi-threaded Engine</p>', unsafe_allow_html=True)
    
    tabs = st.tabs(["⚡ الطور السريع", "💡 طور العبقري", "⚙️ الإعدادات"])

    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            u_theme = st.text_input("🎯 موضوع الكتاب (Niche):", "Ocean Animals")
            u_pages = st.number_input("📄 عدد الصفحات:", min_value=12, max_value=150, value=24, step=1)
        with c2:
            modes = ["تلوين فقط", "ألغاز منوعة", "قصص ورسومات", "تعليم (A-Z)", "كوميكس فقط", "وصل النقاط", "ملاحظات مسطرة", "منوع"]
            u_mode = st.selectbox("🎭 النوع التنسيقي:", modes)
        
        if st.button("🚀 ابدأ الإنتاج السريع", use_container_width=True):
            run_production(u_theme, u_pages, u_mode)

    with tabs[1]:
        o_theme = st.text_input("🎯 الموضوع الأساسي:", placeholder="مثال: قطط النينجا...")
        o_desc = st.text_area("📝 وصف الفكرة:", placeholder="أريد قصة تفاعلية مضحكة...")
        o_pages = st.number_input("📄 عدد الصفحات المطلوب:", min_value=12, max_value=150, value=24, step=1)
        
        if st.button("🪄 نفذ فكرتي", use_container_width=True):
            with st.spinner("جاري التحليل..."):
                plan = GeminiEngine.ask(f"Idea: {o_theme}. Suggest best type: [قصص ورسومات, منوع, ألغاز منوعة]. Output strictly the Arabic name.")
                run_production(o_theme, o_pages, plan if plan in ["قصص ورسومات", "منوع", "ألغاز منوعة"] else "منوع")

    with tabs[2]:
        st.write("جلب المفاتيح من Render تلقائي.")
        if API_KEYS[0] != "DUMMY": st.success("✅ Gemini متصل")
        if TELEGRAM_TOKEN: st.success("✅ Telegram متصل")

def run_production(t, p, m):
    stat = st.empty()
    try:
        engine = ProductionEngine({'theme':t, 'pages':p, 'mode':m}, stat.info)
        f, meta = engine.run()
        stat.success("🎉 اكتمل الكتاب بنجاح!")
        st.info(f"**SEO Info:**\n\n{meta}")
        with open(f, "rb") as b: st.download_button("⬇️ تحميل الكتاب", b, file_name=f, use_container_width=True)
        if TELEGRAM_TOKEN: 
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ كتاب {t} جاهز!"}, files={"document": open(f, "rb")})
    except Exception as e: 
        st.error(f"❌ خطأ غير متوقع: {e}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

