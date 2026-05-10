"""
KDP Factory Pro - The Ultimate Masterpiece (V15.0)
Architect: Irwin Smith | Advanced Dev: AI
Description: Fully Automated KDP Book Generator with Facing Pages & Dynamic Compensation
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
# UI Configuration & Custom CSS
# ------------------------------------------------------------------------------
st.set_page_config(page_title="KDP Factory Pro V15", page_icon="👑", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800;900&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .main-title {
        background: linear-gradient(120deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 48px; font-weight: 900; text-align: center; margin: 0; padding-bottom: 10px;
    }
    .status-card { background: #ffffff; border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 8px solid #764ba2; }
    .stButton > button { background: linear-gradient(90deg, #667eea, #764ba2); color: white; border-radius: 30px; font-weight: bold; padding: 10px 20px; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Environment & API Management
# ------------------------------------------------------------------------------
def get_api_keys():
    keys = [os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 4)]
    return [k.strip() for k in keys if k and k.strip()]

API_KEYS = get_api_keys() or ["DUMMY"]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ------------------------------------------------------------------------------
# AI Engines (Gemini & Pollinations)
# ------------------------------------------------------------------------------
class GeminiEngine:
    MODELS = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    @classmethod
    def ask(cls, prompt):
        if API_KEYS[0] == "DUMMY": return cls._fallback(prompt)
        for key in API_KEYS:
            genai.configure(api_key=key)
            for m_name in cls.MODELS:
                try:
                    res = genai.GenerativeModel(m_name).generate_content(prompt)
                    if res.text: return res.text.strip()
                except: continue
        return cls._fallback(prompt)
        
    @classmethod
    def _fallback(cls, prompt):
        p = prompt.lower()
        if "story" in p: return "A magical journey begins!||He saw a big star.||The hero smiled."
        if "niche" in p: return "Space Dinosaurs"
        if "words" in p: return "SUN,MOON,STAR,SKY,SPACE,HERO"
        return "Generic response due to API timeout."

class ImageGenerator:
    @staticmethod
    def generate(prompt, filename, style="coloring"):
        styles = {
            "coloring": "bold black and white line art, thick clean outlines, pure white background, coloring book style, NO shading, NO gray",
            "dots": "simple dot-to-dot puzzle for kids, numbered dots forming a shape, black and white, white background",
            "cover": "vibrant colorful children's book cover, high resolution, professional cartoon style, NO text, NO words"
        }
        full_p = f"{styles.get(style, styles['coloring'])}, {prompt}"
        for _ in range(3):
            try:
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200 and len(resp.content) > 18000: # Ensure image isn't a tiny error page
                    with open(filename, "wb") as f: f.write(resp.content)
                    return True
            except: time.sleep(1)
        return False

# ------------------------------------------------------------------------------
# Puzzle Logic Engine (Pure Python)
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
        try:
            raw = GeminiEngine.ask(f"Give exactly 6 simple English words related to '{theme}'. ONLY words separated by commas. No spaces.").upper()
            words = [w.strip() for w in raw.replace('\n', '').split(',')]
            words = [w for w in words if w.isalpha() and 3 <= len(w) <= 8][:6]
            if len(words) < 6: words = ["HERO", "MAGIC", "POWER", "SECRET", "BRAVE", "QUEST"]
        except: words = ["HERO", "MAGIC", "POWER", "SECRET", "BRAVE", "QUEST"]

        size = 10
        grid = [[' ' for _ in range(size)] for _ in range(size)]
        for w in words:
            for _ in range(50):
                direction = random.choice([(0,1), (1,0)])
                r, c = random.randint(0, size - 1 - (len(w)-1)*direction[0]), random.randint(0, size - 1 - (len(w)-1)*direction[1])
                if all(grid[r+i*direction[0]][c+i*direction[1]] in (' ', w[i]) for i in range(len(w))):
                    for i in range(len(w)): grid[r+i*direction[0]][c+i*direction[1]] = w[i]
                    break
        for r in range(size):
            for c in range(size):
                if grid[r][c] == ' ': grid[r][c] = random.choice(string.ascii_uppercase)
        return grid, words

# ------------------------------------------------------------------------------
# PDF Builder (KDP Formatted)
# ------------------------------------------------------------------------------
class KDPBook(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(False)
        self.set_margins(0.875, 0.5, 0.75) # Gutter margin included

    def add_title(self, text, y=0.8, size=24):
        self.set_font("Arial", "B", size)
        self.set_y(y)
        self.cell(0, 0.5, text, align="C", ln=True)

# ------------------------------------------------------------------------------
# Main Production Engine
# ------------------------------------------------------------------------------
class RoyalProductionEngine:
    def __init__(self, config, ui_status, ui_progress):
        self.config = config
        self.status = ui_status
        self.progress = ui_progress
        self.pdf = KDPBook()

    def run(self):
        t, p, m = self.config['theme'], self.config['pages'], self.config['mode']
        
        # 1. Cover Generation
        self.status.info(f"🎨 Designing professional KDP cover for '{t}'...")
        if ImageGenerator.generate(f"happy {t} characters, beautiful children's book", "c.jpg", "cover"):
            self.pdf.add_page(); self.pdf.image("c.jpg", x=0, y=0, w=8.5, h=11); os.remove("c.jpg")
        
        # Title Page
        self.pdf.add_page(); self.pdf.set_font("Arial", "B", 36); self.pdf.set_y(4)
        self.pdf.cell(0, 1, f"THE BIG BOOK OF", align="C", ln=True)
        self.pdf.cell(0, 1, t.upper(), align="C", ln=True)

        # 2. Content Generation
        if m == "Story & Coloring": self._story_coloring(p, t)
        elif m == "Educational (A-Z)": self._alphabet(p)
        elif m == "Dot-to-Dot": self._dot_to_dot(p, t)
        elif m == "Coloring Only": self._coloring_only(p, t)
        elif m == "Puzzles (Mixed)": self._puzzles(p, t)
        elif m == "Comics": self._comics(p, t)
        else: self._mixed_mode(p, t)

        # 3. Export & SEO
        fname = f"KDP_Royal_{t.replace(' ', '_')}_{int(time.time())}.pdf"
        self.pdf.output(fname)
        self.status.info("📝 Writing Amazon KDP SEO Listing...")
        meta = GeminiEngine.ask(f"Act as Amazon KDP expert. Write converting listing for '{t}' kids activity book (Type: {m}). Include: Catchy Title, Subtitle, 7 Backend Search Keywords (comma separated), and a short persuasive Description with bullet points.")
        return fname, meta

    def _story_coloring(self, count, theme):
        raw = GeminiEngine.ask(f"Write a {count} part exciting story about {theme}. Each part 2 short sentences. Split with '||'.")
        parts = [p.strip() for p in raw.split('||')][:count]
        for i, text in enumerate(parts):
            self.status.write(f"📖 Generating Story/Coloring Pair {i+1}/{count}...")
            # Left Page: Story
            self.pdf.add_page(); self.pdf.set_font("Arial", "I", 22); self.pdf.set_y(4)
            self.pdf.multi_cell(0, 0.5, text, align="C")
            # Right Page: Coloring
            if ImageGenerator.generate(f"scene of {text[:50]}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=2, w=6.5, h=6.5); os.remove("t.jpg")
            else: self.pdf.add_page()
            self.pdf.add_page() # Blank back to protect colors
            self.progress((i+1)/count)

    def _alphabet(self, count):
        letters = list(string.ascii_uppercase)[:min(count, 26)]
        for i, L in enumerate(letters):
            self.status.write(f"✏️ Designing Letter '{L}' Pair...")
            # Left Page: Trace
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 120); self.pdf.set_y(2)
            self.pdf.cell(0, 1.5, L, align="C", ln=True)
            self.pdf.set_font("Arial", "", 24); self.pdf.cell(0, 1, f"Practice Writing {L}", align="C")
            # Right Page: Color
            item = GeminiEngine.ask(f"One simple word starting with {L} for kids coloring. Just the word.").strip()
            if ImageGenerator.generate(f"a cute {item}", "t.jpg"):
                self.pdf.add_page(); self.pdf.add_title(f"{L} is for {item.upper()}", 1.0, 30)
                self.pdf.image("t.jpg", x=1.5, y=2.5, w=5.5, h=5.5); os.remove("t.jpg")
            else: self.pdf.add_page()
            self.pdf.add_page() # Blank back
            self.progress((i+1)/len(letters))

    def _dot_to_dot(self, count, theme):
        items = GeminiEngine.ask(f"Give {count+10} simple items related to {theme}. One per line.").split('\n')
        success = 0
        for item in items:
            if success >= count: break
            if not item.strip(): continue
            self.status.write(f"📍 Drawing Dot-to-Dot Puzzle {success+1}/{count}...")
            if ImageGenerator.generate(f"dot-to-dot puzzle of {item.strip()}", "t.jpg", "dots"):
                # Left Page: Drawing space
                self.pdf.add_page(); self.pdf.add_title("Draw Your Own Here!", 4.0)
                # Right Page: Dot Puzzle
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=1.5, w=6.5, h=7.5); os.remove("t.jpg")
                self.pdf.add_page() # Blank back
                success += 1
                self.progress(success/count)

    def _coloring_only(self, count, theme):
        items = GeminiEngine.ask(f"Give {count+10} simple items related to {theme} for kids coloring. One per line.").split('\n')
        success = 0
        for item in items:
            if success >= count: break
            if not item.strip(): continue
            self.status.write(f"🖌️ Drawing Coloring Page {success+1}/{count}...")
            if ImageGenerator.generate(f"a cute {item.strip()}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=1.5, w=6.5, h=6.5); os.remove("t.jpg")
                self.pdf.add_page() # Blank back
                success += 1
                self.progress(success/count)

    def _puzzles(self, count, theme):
        per_type = max(1, count // 3)
        # 1. Sudoku
        for i in range(per_type):
            self.status.write(f"🧩 Generating Sudoku {i+1}...")
            board = PuzzleEngine.sudoku(); self.pdf.add_page(); self.pdf.add_title(f"Sudoku Challenge #{i+1}")
            sx, sy, cs = 1.25, 2.5, 0.66
            for r in range(9):
                for c in range(9):
                    self.pdf.set_line_width(0.05 if (r%3==0 or c%3==0) else 0.01)
                    self.pdf.rect(sx+c*cs, sy+r*cs, cs, cs)
                    if board[r][c] != 0: self.pdf.set_font("Arial", "B", 20); self.pdf.text(sx+c*cs+0.25, sy+r*cs+0.45, str(board[r][c]))
        # 2. Maze
        for i in range(per_type):
            self.status.write(f"🌀 Building Maze {i+1}...")
            g = PuzzleEngine.maze(); self.pdf.add_page(); self.pdf.add_title(f"Maze Adventure #{i+1}")
            sx, sy, cs = 1.8, 2.5, 0.4; self.pdf.set_line_width(0.04)
            for y in range(12):
                for x in range(12):
                    px, py = sx+x*cs, sy+y*cs
                    if g[y][x]['N']: self.pdf.line(px, py, px+cs, py)
                    if g[y][x]['S']: self.pdf.line(px, py+cs, px+cs, py+cs)
                    if g[y][x]['E']: self.pdf.line(px+cs, py, px+cs, py+cs)
                    if g[y][x]['W']: self.pdf.line(px, py, px, py+cs)
        # 3. Word Search
        for i in range(per_type):
            self.status.write(f"🔍 Creating Word Search {i+1}...")
            grid, words = PuzzleEngine.word_search(theme)
            self.pdf.add_page(); self.pdf.add_title(f"Word Search #{i+1}"); self.pdf.set_font("Arial", "B", 24)
            sx, sy, cs = 1.75, 2.5, 0.5
            for r in range(10):
                for c in range(10): self.pdf.text(sx + c*cs, sy + r*cs, grid[r][c])
            self.pdf.set_font("Arial", "", 16); self.pdf.set_y(8.0)
            self.pdf.cell(0, 0.5, "Find these words:", align="C", ln=True)
            self.pdf.cell(0, 0.5, " - ".join(words), align="C", ln=True)
        self.progress(1.0)

    def _comics(self, count, theme):
        for i in range(count):
            self.status.write(f"🦸 Drawing Comic Panels {i+1}/{count}...")
            self.pdf.add_page(); self.pdf.add_title(f"Draw Your {theme} Comic!")
            self.pdf.set_line_width(0.04)
            # Layout
            self.pdf.rect(0.75, 1.5, 3.4, 4); self.pdf.rect(4.35, 1.5, 3.4, 4)
            self.pdf.rect(0.75, 5.7, 7, 4.5)
            self.progress((i+1)/count)

    def _mixed_mode(self, count, theme):
        self._coloring_only(count//4, theme)
        self._puzzles(count//4 * 3, theme) # Mix of puzzles fills the rest

# ------------------------------------------------------------------------------
# System & UI Logic
# ------------------------------------------------------------------------------
def check_auto():
    try:
        if hasattr(st, 'query_params'): return st.query_params.get("auto") == "true"
        return st.experimental_get_query_params().get("auto", [""])[0] == "true"
    except: return False

def main():
    if check_auto():
        st.warning("🤖 Auto-Pilot Mode is running in the background...")
        theme = GeminiEngine.ask("Suggest ONE highly profitable, low-competition KDP niche phrase for kids.").strip()
        eng = RoyalProductionEngine({'theme':theme, 'pages':20, 'mode':'Story & Coloring'}, st.empty(), lambda x: None)
        f, m = eng.run()
        if TELEGRAM_TOKEN:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ Auto-Generated: {theme}"}, files={"document": open(f, "rb")})
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": m})
        return

    st.markdown('<h1 class="main-title">📚 KDP Factory Pro V15 👑</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#888;">The Ultimate AI-Powered Publishing Agency</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        u_theme = st.text_input("🎯 Target Niche / Theme:", "Space Explorers")
        u_pages = st.slider("📄 Number of Pages/Pairs:", 10, 100, 20)
    with col2:
        modes = ["Story & Coloring", "Coloring Only", "Puzzles (Mixed)", "Educational (A-Z)", "Dot-to-Dot", "Comics", "Everything (Mixed)"]
        u_mode = st.selectbox("🎭 Book Format & Type:", modes)

    if st.button("🚀 Start Royal Production", use_container_width=True):
        if API_KEYS[0] == "DUMMY":
            st.warning("⚠️ Warning: Running in Fallback Mode. Please add GEMINI_API_KEY_1 in Render settings for AI text.")
            
        status_c = st.container()
        with status_c:
            s_msg = st.empty()
            p_bar = st.progress(0)
            try:
                engine = RoyalProductionEngine({'theme':u_theme, 'pages':u_pages, 'mode':u_mode}, s_msg, p_bar.progress)
                file, meta = engine.run()
                
                st.success("🎉 Your KDP Book is Ready!")
                st.info(f"**Amazon KDP SEO Metadata:**\n\n{meta}")
                
                with open(file, "rb") as f: 
                    st.download_button("⬇️ Download PDF Book", f, file_name=file, use_container_width=True)
                    
                if TELEGRAM_TOKEN:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ Your book '{u_theme}' is ready for KDP!"}, files={"document": open(file, "rb")})
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": meta})
            except Exception as e:
                st.error(f"❌ A critical error occurred: {e}")
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

