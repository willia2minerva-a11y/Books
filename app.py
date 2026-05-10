"""
KDP Factory Pro - Elite Version V19.0
Architect & Creator: Erwin Smith | AI Logic: Elite Shield
Fixes: RTL UI Bugs, FPDF Encoding Crashes, Perfect Sudoku Grid, Themed Mazes
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

# ------------------------------------------------------------------------------
# 1. منع انهيار الجلسة (Session Fix)
# ------------------------------------------------------------------------------
if 'init' not in st.session_state:
    st.session_state.init = True

# ------------------------------------------------------------------------------
# 2. إعدادات الواجهة و CSS المعالج
# ------------------------------------------------------------------------------
st.set_page_config(page_title="KDP Factory Pro", page_icon="👑", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    /* تطبيق العربية على النصوص فقط لمنع تخريب عناصر Streamlit كالأزرار والأشرطة */
    p, h1, h2, h3, h4, h5, h6, label, .stMarkdown {
        font-family: 'Cairo', sans-serif; 
        direction: rtl; 
        text-align: right;
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
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. جلب المفاتيح والإعدادات
# ------------------------------------------------------------------------------
def get_api_keys():
    keys = [os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 4)]
    return [k.strip() for k in keys if k and k.strip()]

API_KEYS = get_api_keys() or ["DUMMY"]
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def clean_text(text):
    """منع انهيار مكتبة PDF بتنظيف النص من الرموز الغريبة والإيموجي"""
    if not text: return ""
    return text.encode('latin-1', 'ignore').decode('latin-1').replace('\n', ' ')

# ------------------------------------------------------------------------------
# 4. محرك الذكاء الاصطناعي والصور
# ------------------------------------------------------------------------------
class GeminiEngine:
    MODELS = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    @classmethod
    def ask(cls, prompt):
        if API_KEYS[0] == "DUMMY": return "A magical journey begins!||He saw a big star."
        for key in API_KEYS:
            genai.configure(api_key=key)
            for m_name in cls.MODELS:
                try:
                    res = genai.GenerativeModel(m_name).generate_content(prompt)
                    if res.text: return res.text.strip()
                except: continue
        return "Default adventure content due to timeout."

class ImageGenerator:
    @staticmethod
    def generate(prompt, filename, style="coloring"):
        styles = {
            "coloring": "bold black and white line art, thick outlines, white background, coloring book style, NO shading, clean vector",
            "dots": "dot-to-dot puzzle for kids, simple numbered dots, black and white, white background",
            "cover": "vibrant colorful children's book cover, high resolution, professional, NO text, NO words"
        }
        full_p = f"{styles.get(style, styles['coloring'])}, {prompt}"
        for _ in range(3):
            try:
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
                resp = requests.get(url, timeout=20)
                # التأكد من أن المخرجات صورة وليست صفحة خطأ
                if resp.status_code == 200 and 'image' in resp.headers.get('content-type', '').lower():
                    with open(filename, "wb") as f: f.write(resp.content)
                    return True
            except: time.sleep(1)
        return False

# ------------------------------------------------------------------------------
# 5. محرك الألغاز (Pure Python)
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
            raw = clean_text(GeminiEngine.ask(f"Give exactly 6 simple English words related to '{theme}'. ONLY words separated by commas. No spaces.")).upper()
            words = [w.strip() for w in raw.replace('\n', '').split(',')]
            words = [w for w in words if w.isalpha() and 3 <= len(w) <= 8][:6]
            if len(words) < 6: words = ["HERO", "MAGIC", "POWER", "SECRET", "BRAVE", "QUEST"]
        except: words = ["HERO", "MAGIC", "POWER", "SECRET", "BRAVE", "QUEST"]

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
# 6. صانع الكتاب (KDP Formatter)
# ------------------------------------------------------------------------------
class KDPBook(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(False)
        self.set_margins(0.875, 0.5, 0.75) # Gutter margin included

    def add_lined_page(self):
        self.add_page(); self.set_draw_color(200, 200, 200); self.set_line_width(0.01)
        for i in range(2, 10): self.line(1, i, 7.5, i)

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
        
        self.log(f"🎨 جاري إنشاء الغلاف الاحترافي لـ {t[:30]}...")
        if ImageGenerator.generate(f"happy {t[:30]} kids illustration", "c.jpg", "cover"):
            self.pdf.add_page(); self.pdf.image("c.jpg", x=0, y=0, w=8.5, h=11); os.remove("c.jpg")
        
        self.pdf.add_page(); self.pdf.set_font("Arial", "B", 36); self.pdf.set_y(4)
        self.pdf.set_font("Arial", "B", 24)
        clean_t = clean_text(t)
        self.pdf.multi_cell(0, 0.5, f"THE BIG BOOK OF\n{clean_t.upper()}", align="C")

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

        clean_theme = re.sub(r'[^a-zA-Z0-9]', '_', t)[:30]
        fname = f"KDP_{clean_theme}_{int(time.time())}.pdf"
        
        self.pdf.output(fname)
        meta = GeminiEngine.ask(f"Write KDP SEO listing for {t} book. Title, Subtitle, 7 Keywords, Description with bullets.")
        return fname, meta

    def _coloring_mode(self, count, theme):
        items = GeminiEngine.ask(f"List {count+10} simple coloring items for {theme}. One per line.").split('\n')
        success = 0
        for item in items:
            if success >= count: break
            if len(item.strip()) < 3: continue
            self.log(f"🖌️ جاري رسم المشهد {success+1}: {clean_text(item.strip()[:20])}...")
            if ImageGenerator.generate(f"cute {item.strip()}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=1.5, w=6.5, h=6.5)
                self.pdf.add_page(); os.remove("t.jpg"); success += 1

    def _story_mode(self, count, theme):
        raw = GeminiEngine.ask(f"Write {count} part exciting story about {theme}. Part=2 sentences. Split '||'.")
        parts = [clean_text(p.strip()) for p in raw.split('||')][:count]
        for i, text in enumerate(parts):
            self.log(f"📖 جاري إنشاء الجزء القصصي {i+1}...")
            self.pdf.add_page(); self.pdf.set_font("Arial", "I", 22); self.pdf.set_y(4); self.pdf.multi_cell(0, 0.5, text, align="C")
            if ImageGenerator.generate(f"scene for {text[:40]}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=2, w=6.5, h=6.5); os.remove("t.jpg")
            else: self.pdf.add_page()
            self.pdf.add_page()

    def _alphabet_mode(self, count):
        L = list(string.ascii_uppercase)[:min(count, 26)]
        for i, char in enumerate(L):
            self.log(f"✏️ جاري إعداد وتصميم الحرف {char}...")
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 120); self.pdf.set_y(2); self.pdf.cell(0, 1.5, char, align="C", ln=True)
            self.pdf.set_font("Arial", "", 24); self.pdf.cell(0, 1, f"Practice Writing {char}", align="C")
            item = clean_text(GeminiEngine.ask(f"One simple word starting with {char} for kids coloring. Just the word.").strip())
            if ImageGenerator.generate(f"a cute {item}", "t.jpg"):
                self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1)
                self.pdf.cell(0, 1, f"{char} is for {item.upper()}", align="C")
                self.pdf.image("t.jpg", x=1.5, y=2.5, w=5.5, h=5.5); os.remove("t.jpg")
            else: self.pdf.add_page()
            self.pdf.add_page()

    def _puzzles_mode(self, count, theme):
        per = max(1, count // 3)
        # 🧩 1. Perfect Sudoku
        for i in range(per):
            self.log(f"🧩 جاري بناء سودوكو {i+1}...")
            b = PuzzleEngine.sudoku(); self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1); self.pdf.cell(0, 1, f"Sudoku #{i+1}", align="C")
            sx, sy, cs = 1.25, 2.5, 0.66
            # Draw thin inner grid
            self.pdf.set_line_width(0.01); self.pdf.set_draw_color(100, 100, 100)
            for r in range(9):
                for c in range(9):
                    self.pdf.rect(sx+c*cs, sy+r*cs, cs, cs)
                    if b[r][c] != 0: self.pdf.set_font("Arial", "B", 20); self.pdf.text(sx+c*cs+0.25, sy+r*cs+0.45, str(b[r][c]))
            # Draw thick 3x3 outer borders
            self.pdf.set_line_width(0.05); self.pdf.set_draw_color(0, 0, 0)
            for k in range(4):
                self.pdf.line(sx + k*3*cs, sy, sx + k*3*cs, sy + 9*cs) # Vertical
                self.pdf.line(sx, sy + k*3*cs, sx + 9*cs, sy + k*3*cs) # Horizontal

        # 🌀 2. Themed Maze
        for i in range(per):
            self.log(f"🌀 جاري تصميم المتاهة {i+1}...")
            # Ask Gemini for Start/Goal
            maze_theme = clean_text(GeminiEngine.ask(f"For a maze about {theme}, give a start character and end goal. Format: Character | Goal. Example: Astronaut | Moon"))
            if '|' in maze_theme: start_txt, goal_txt = maze_theme.split('|', 1)
            else: start_txt, goal_txt = "Start", "Finish"
            
            g = PuzzleEngine.maze(); self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(0.5); self.pdf.cell(0, 1, f"Maze #{i+1}", align="C")
            
            sx, sy, cs = 1.8, 2.5, 0.4
            # Draw Start Text
            self.pdf.set_font("Arial", "B", 14); self.pdf.text(sx, sy - 0.2, f"Start: {start_txt.strip()}")
            
            self.pdf.set_line_width(0.04)
            for y in range(12):
                for x in range(12):
                    if g[y][x]['N']: self.pdf.line(sx+x*cs, sy+y*cs, sx+(x+1)*cs, sy+y*cs)
                    if g[y][x]['S']: self.pdf.line(sx+x*cs, sy+(y+1)*cs, sx+(x+1)*cs, sy+(y+1)*cs)
                    if g[y][x]['E']: self.pdf.line(sx+(x+1)*cs, sy+y*cs, sx+(x+1)*cs, sy+(y+1)*cs)
                    if g[y][x]['W']: self.pdf.line(sx+x*cs, sy+y*cs, sx+x*cs, sy+(y+1)*cs)
            
            # Draw Goal Text
            self.pdf.set_font("Arial", "B", 14); self.pdf.text(sx + 8*cs, sy + 12*cs + 0.3, f"Goal: {goal_txt.strip()}")

        # 🔍 3. Word Search
        for i in range(per):
            self.log(f"🔍 جاري إخفاء الكلمات {i+1}...")
            grid, words = PuzzleEngine.word_search(theme)
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1); self.pdf.cell(0, 1, f"Word Search #{i+1}", align="C")
            sx, sy, cs = 1.75, 2.5, 0.5
            for r in range(10):
                for c in range(10): self.pdf.text(sx + c*cs, sy + r*cs, grid[r][c])
            self.pdf.set_font("Arial", "", 16); self.pdf.set_y(8.0)
            self.pdf.cell(0, 0.5, "Find: " + " - ".join(words), align="C")

    def _comics_mode(self, count, theme):
        for i in range(count):
            self.log(f"🦸 جاري تسطير الكوميكس {i+1}...")
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(0.8); self.pdf.cell(0, 1, f"Draw Your {clean_text(theme)} Comic", align="C")
            self.pdf.set_line_width(0.04); self.pdf.set_draw_color(0, 0, 0)
            self.pdf.rect(0.75, 1.8, 3.4, 4); self.pdf.rect(4.35, 1.8, 3.4, 4); self.pdf.rect(0.75, 6.0, 7, 4.2)

    def _dots_mode(self, count, theme):
        items = GeminiEngine.ask(f"Give {count+10} items related to {theme}. One per line.").split('\n')
        s = 0
        for item in items:
            if s >= count: break
            if len(item.strip()) < 3: continue
            self.log(f"📍 جاري رسم لغز النقاط {s+1}...")
            if ImageGenerator.generate(f"dot-to-dot puzzle of {clean_text(item.strip())}", "t.jpg", "dots"):
                self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(4); self.pdf.cell(0, 1, "Draw Freehand Here", align="C")
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=1.5, w=6.5, h=7.5); os.remove("t.jpg")
                self.pdf.add_page()
                s += 1
                
    def _lined_mode(self, count):
        for i in range(count):
            self.log(f"📏 جاري تسطير الصفحة {i+1}...")
            self.pdf.add_lined_page()

# ------------------------------------------------------------------------------
# 8. واجهة التحكم والتشغيل (UI & Auto Mode)
# ------------------------------------------------------------------------------
def check_auto():
    try:
        if hasattr(st, 'query_params'): return st.query_params.get("auto") == "true"
        return st.experimental_get_query_params().get("auto", [""])[0] == "true"
    except: return False

def main():
    # ==========================================
    # الطور الآلي (الخفي) - يعمل بدون أي تدخل
    # ==========================================
    if check_auto():
        st.warning("🤖 النظام الآلي يعمل في الخلفية بصمت...")
        if API_KEYS[0] == "DUMMY": st.stop()
        
        strict_prompt = "Output ONLY a 2 to 4 words highly profitable KDP niche for kids activity book. Examples: Space Dogs, Ninja Cats. DO NOT write explanations. JUST THE WORDS."
        theme = clean_text(GeminiEngine.ask(strict_prompt).replace('*', '').strip()[:40])
        
        eng = ProductionEngine({'theme':theme, 'pages':30, 'mode':'منوع'}, lambda x: print(x))
        f, meta = eng.run()
        if TELEGRAM_TOKEN:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ كتاب آلي جديد: {theme}"}, files={"document": open(f, "rb")})
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": meta})
        st.success("تم الإرسال!")
        return

    # ==========================================
    # الواجهة التفاعلية (للاستخدام اليدوي)
    # ==========================================
    st.markdown('<h1 class="main-title">📚 KDP Factory Pro V19 👑</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#888; font-weight:bold; direction:ltr;">صُنع بواسطة Irwin Smith</p>', unsafe_allow_html=True)
    
    tabs = st.tabs(["⚡ الطور السريع", "💡 طور العبقري", "⚙️ الإعدادات"])

    with tabs[0]:
        st.info("اختر نوع الكتاب وعدد الصفحات، وسيقوم النظام بتوليده فوراً.")
        c1, c2 = st.columns(2)
        with c1:
            u_theme = st.text_input("🎯 موضوع الكتاب (Niche):", "Ocean Animals")
            # تغيير الـ Slider إلى Number Input لمنع اختفاء الرقم
            u_pages = st.number_input("📄 عدد الصفحات:", min_value=12, max_value=150, value=24, step=1)
        with c2:
            modes = ["تلوين فقط", "ألغاز منوعة", "قصص ورسومات", "تعليم (A-Z)", "كوميكس فقط", "وصل النقاط", "ملاحظات مسطرة", "منوع"]
            u_mode = st.selectbox("🎭 النوع التنسيقي:", modes)
        
        if st.button("🚀 ابدأ الإنتاج السريع", key="btn_fast", use_container_width=True):
            run_production(u_theme, u_pages, u_mode)

    with tabs[1]:
        st.info("اكتب فكرتك بحرية وسيقوم الذكاء الاصطناعي بتخطيط الكتاب لك بأفضل طريقة لـ KDP.")
        o_theme = st.text_input("🎯 الموضوع الأساسي (Theme):", placeholder="مثال: قطط النينجا في الفضاء...")
        o_desc = st.text_area("📝 وصف الفكرة بالتفصيل:", placeholder="مثال: أريد قصة تفاعلية مضحكة مع الكثير من المتاهات...")
        o_pages = st.number_input("📄 عدد الصفحات المطلوب:", min_value=12, max_value=150, value=30, step=1)
        
        if st.button("🪄 نفذ فكرتي العبقرية", key="btn_open", use_container_width=True):
            with st.spinner("جاري تحليل فكرتك وتخطيط الكتاب..."):
                plan = GeminiEngine.ask(f"User idea: {o_theme}. Details: {o_desc}. Suggest the best KDP activity book type from this list: [قصص ورسومات, منوع, ألغاز منوعة]. Output ONLY the exact Arabic name of the type.")
                st.success(f"النوع الأمثل لفكرتك هو: {plan}")
                run_production(o_theme, o_pages, plan if plan in ["قصص ورسومات", "منوع", "ألغاز منوعة"] else "منوع")

    with tabs[2]:
        st.markdown("### 🔑 إدارة حالة النظام")
        st.write("يتم جلب المفاتيح تلقائياً من إعدادات Render.")
        if API_KEYS[0] != "DUMMY": st.success("✅ Gemini متصل ومستقر")
        else: st.error("⚠️ يرجى إضافة GEMINI_API_KEY_1")
        if TELEGRAM_TOKEN: st.success("✅ Telegram متصل ومستعد للاستلام")

def run_production(t, p, m):
    status_c = st.container()
    with status_c:
        stat = st.empty()
        try:
            engine = ProductionEngine({'theme':t, 'pages':p, 'mode':m}, stat.info)
            f, meta = engine.run()
            stat.success("🎉 تم الإنتاج بنجاح!")
            st.info(f"**SEO Info for Amazon:**\n\n{meta}")
            with open(f, "rb") as b: st.download_button("⬇️ تحميل الكتاب (PDF)", b, file_name=f, use_container_width=True)
            if TELEGRAM_TOKEN: 
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ كتاب {t} جاهز للرفع!"}, files={"document": open(f, "rb")})
        except Exception as e: 
            st.error(f"❌ حدث خطأ غير متوقع: {e}")
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

