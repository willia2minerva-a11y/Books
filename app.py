"""
KDP Factory Pro - Hyper-Bot V27
Architect: Irwin Smith | Logic: Autonomous 15-Min Cycle
Features: Auto-Pilot (Every 15 Mins), Multi-threaded, KDP Standard Formatting
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
import threading
import concurrent.futures

# ==========================================
# 1. إعدادات الواجهة و CSS
# ==========================================
st.set_page_config(page_title="KDP Factory Pro V27", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    p, h1, h2, h3, h4, h5, h6, label, .stMarkdown { direction: rtl; text-align: right; }
    .main-title {
        background: linear-gradient(120deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 45px; font-weight: 900; text-align: center; margin: 0; direction: ltr;
    }
    input, textarea { text-align: left !important; direction: ltr !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة المفاتيح والبيئة
# ==========================================
def get_all_keys():
    keys = [os.getenv(f"GEMINI_API_KEY_{i}", "") for i in range(1, 6)]
    valid = [k.strip() for k in keys if k.strip()]
    return valid if valid else ["DUMMY"]

ALL_KEYS = get_all_keys()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def clean_text(text):
    if not text: return ""
    return text.encode('latin-1', 'ignore').decode('latin-1').replace('\n', ' ')

# ==========================================
# 3. محركات الذكاء الاصطناعي والصور
# ==========================================
class SmartGemini:
    @classmethod
    def ask(cls, prompt, fallback=""):
        if ALL_KEYS[0] == "DUMMY": return fallback
        random.shuffle(ALL_KEYS)
        for key in ALL_KEYS:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(prompt)
                if res.text: return res.text.strip()
            except: continue 
        return fallback

class ImageShield:
    @staticmethod
    def generate(prompt, filename, style="coloring"):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36'}
        if style == "cover":
            p = f"Professional kids book cover, {prompt}, vibrant, blank background, NO TEXT"
        else:
            p = f"Bold black and white line art, {prompt}, thick outlines, white background, NO shading"
        
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
        
        for _ in range(3):
            try:
                r = requests.get(url, headers=headers, timeout=30)
                if r.status_code == 200 and len(r.content) > 15000:
                    with open(filename, "wb") as f: f.write(r.content)
                    return True
            except: time.sleep(1); continue
        return False

    @staticmethod
    def generate_parallel(tasks, max_workers=3):
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(ImageShield.generate, p, f, s): f for p, f, s in tasks}
            for future in concurrent.futures.as_completed(future_to_file):
                f = future_to_file[future]
                try: results[f] = future.result()
                except: results[f] = False
        return results

# ==========================================
# 4. محرك الألغاز وصانع الكتب
# ==========================================
class PuzzleEngine:
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

class ProductionEngine:
    def __init__(self, config, logger):
        self.config = config
        self.log = logger
        self.pdf = FPDF(unit="in", format=(8.5, 11))
        self.pdf.set_auto_page_break(False)
        self.pdf.set_margins(0.875, 0.5, 0.75)

    def run(self):
        t, p, m = self.config['theme'], self.config['pages'], self.config['mode']
        
        # Cover
        if ImageShield.generate(t, "cover.jpg", "cover"):
            self.pdf.add_page(); self.pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11); os.remove("cover.jpg")
        
        # Title Page
        self.pdf.add_page(); self.pdf.set_font("Arial", "B", 30); self.pdf.set_y(4)
        self.pdf.multi_cell(0, 0.5, f"THE BIG BOOK OF\n{clean_text(t).upper()}", align="C")

        # Logic per mode
        if m == "تلوين فقط": self._coloring(p, t)
        elif m == "ألغاز منوعة": self._puzzles(p, t)
        else: self._mixed(p, t)

        fname = f"KDP_{re.sub(r'[^a-zA-Z0-9]', '_', t)[:20]}_{int(time.time())}.pdf"
        self.pdf.output(fname)
        seo = SmartGemini.ask(f"Write KDP SEO for '{t}': Title, Subtitle, 7 Keywords, Description.")
        return fname, seo

    def _coloring(self, count, theme):
        ideas = SmartGemini.ask(f"List {count} items for {theme} coloring. One per line.").split('\n')
        tasks = [(clean_text(item), f"img_{i}.jpg", "coloring") for i, item in enumerate(ideas[:count])]
        results = ImageShield.generate_parallel(tasks)
        for i in range(len(tasks)):
            fname = f"img_{i}.jpg"
            if results.get(fname):
                self.pdf.add_page(); self.pdf.image(fname, x=1, y=1.5, w=6.5, h=6.5)
                self.pdf.add_page(); os.remove(fname)

    def _puzzles(self, count, theme):
        per = max(1, count // 2)
        for i in range(per): # Sudoku
            b = PuzzleEngine.sudoku(); self.pdf.add_page()
            sx, sy, cs = 1.25, 2.5, 0.66
            for r in range(9):
                for c in range(9):
                    self.pdf.rect(sx+c*cs, sy+r*cs, cs, cs)
                    if b[r][c] != 0: self.pdf.text(sx+c*cs+0.25, sy+r*cs+0.45, str(b[r][c]))
        for i in range(per): # Maze
            g = PuzzleEngine.maze(); self.pdf.add_page()
            sx, sy, cs = 1.8, 2.5, 0.4
            for y in range(12):
                for x in range(12):
                    if g[y][x]['N']: self.pdf.line(sx+x*cs, sy+y*cs, sx+(x+1)*cs, sy+y*cs)
                    if g[y][x]['S']: self.pdf.line(sx+x*cs, sy+(y+1)*cs, sx+(x+1)*cs, sy+(y+1)*cs)

    def _mixed(self, count, theme):
        self._coloring(count//2, theme)
        self._puzzles(count//2, theme)

# ==========================================
# 5. بوت التوليد الفائق (كل 15 دقيقة)
# ==========================================
def hyper_bot_loop():
    while True:
        try:
            if TELEGRAM_TOKEN and ALL_KEYS[0] != "DUMMY":
                # اختيار نيش عشوائي ومربح
                theme = SmartGemini.ask("Output ONLY 2 words profitable KDP niche (e.g. Space Dinosaurs).", "Funny Animals").strip()
                engine = ProductionEngine({'theme': theme, 'pages': 24, 'mode': 'منوع'}, lambda x: None)
                f, meta = engine.run()
                
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", 
                              data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ Hyper-Bot Book: {theme}"}, 
                              files={"document": open(f, "rb")})
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                              data={"chat_id": TELEGRAM_CHAT_ID, "text": meta})
        except: pass
        # الانتظار لمدة 15 دقيقة (900 ثانية)
        time.sleep(900) 

if not hasattr(st, 'hyper_bot_started'):
    st.hyper_bot_started = True
    threading.Thread(target=hyper_bot_loop, daemon=True).start()

# ==========================================
# 6. الواجهة
# ==========================================
def main():
    st.markdown('<h1 class="main-title">🚀 KDP Hyper-Bot V27 👑</h1>', unsafe_allow_html=True)
    st.info("🤖 البوت الآلي يعمل الآن في الخلفية! سيقوم بتوليد كتاب جديد كل 15 دقيقة وإرساله لتليجرام.")
    
    t1, t2 = st.tabs(["🎮 التحكم اليدوي", "📊 إحصائيات"])
    with t1:
        u_t = st.text_input("🎯 موضوع سريع:", "Ocean Adventure")
        if st.button("🚀 إنشاء يدوي الآن"):
            engine = ProductionEngine({'theme': u_t, 'pages': 20, 'mode': 'منوع'}, st.write)
            f, m = engine.run()
            st.success("تم الإنتاج!")
            with open(f, "rb") as file: st.download_button("تحميل", file, file_name=f)

if __name__ == "__main__":
    main()
