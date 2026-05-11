"""
KDP Factory Pro - The Ultimate Masterpiece V28
Architect: Irwin Smith | Logic: Full UI + 15-Min Hyper-Bot + Stealth Gen
Features: Complete Arabic UI, Autonomous Bot, Parallel Engine, All Book Modes
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
# 1. درع استقرار الجلسة
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    time.sleep(1)

st.set_page_config(page_title="KDP Factory Pro V28", page_icon="👑", layout="wide")

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
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 10px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #667eea; color: white; }
    input, textarea { text-align: left !important; direction: ltr !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة المفاتيح
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
# 3. محرك Gemini 
# ==========================================
class SmartGemini:
    @classmethod
    def ask(cls, prompt, fallback_response=""):
        if ALL_KEYS[0] == "DUMMY": return fallback_response
        random.shuffle(ALL_KEYS)
        for key in ALL_KEYS:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(prompt)
                if res.text: return res.text.strip()
            except:
                continue 
        return fallback_response

# ==========================================
# 4. محرك الصور المقنع (Stealth Shield)
# ==========================================
class ImageShield:
    @staticmethod
    def generate(prompt, filename, style="coloring"):
        if style == "cover":
            p = f"Professional children book cover illustration, {prompt}, vibrant colors, happy, BLANK COVER STRICTLY NO TEXT NO LETTERS"
        elif style == "dots":
            p = f"simple dot-to-dot puzzle for kids, {prompt}, numbered dots, black and white line art"
        else:
            p = f"bold black and white line art, {prompt}, thick clean outlines, white background, strictly NO shading, coloring page for kids"
        
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        for attempt in range(3):
            try:
                r = requests.get(url, headers=headers, timeout=30)
                if r.status_code == 200 and len(r.content) > 15000:
                    with open(filename, "wb") as f: f.write(r.content)
                    return True
            except:
                time.sleep(1)
                continue
        return False

    @staticmethod
    def generate_parallel(tasks, max_workers=3):
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {}
            for prompt, filename, style in tasks:
                time.sleep(random.uniform(0.2, 0.7)) 
                future = executor.submit(ImageShield.generate, prompt, filename, style)
                future_to_file[future] = filename
                
            for future in concurrent.futures.as_completed(future_to_file):
                filename = future_to_file[future]
                try: results[filename] = future.result()
                except: results[filename] = False
        return results

# ==========================================
# 5. محرك الألغاز
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

# ==========================================
# 6. صانع الكتاب KDP
# ==========================================
class KDPBook(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(False)
        self.set_margins(0.875, 0.5, 0.75)

class ProductionEngine:
    def __init__(self, config, logger):
        self.config = config
        self.log = logger
        self.pdf = KDPBook()

    def _emergency_page(self, title="Draw Here!"):
        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 20)
        self.pdf.set_y(1)
        self.pdf.cell(0, 1, title, align="C", ln=True)
        self.pdf.set_line_width(0.05)
        self.pdf.rect(1, 2.5, 6.5, 7) 
        self.pdf.set_font("Arial", "I", 14)
        self.pdf.set_y(5)
        self.pdf.cell(0, 1, "Use your imagination to draw something amazing!", align="C")

    def run(self):
        t, p, m = self.config['theme'], self.config['pages'], self.config['mode']
        
        self.log(f"🎨 جاري رسم الغلاف لـ {t[:30]}...")
        if ImageShield.generate(t, "cover.jpg", "cover"):
            self.pdf.add_page(); self.pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11); os.remove("cover.jpg")
        else:
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 40); self.pdf.set_y(4); self.pdf.cell(0, 1, t.upper(), align="C")
        
        self.pdf.add_page(); self.pdf.set_font("Arial", "B", 30); self.pdf.set_y(4)
        self.pdf.multi_cell(0, 0.5, f"THE BIG BOOK OF\n{clean_text(t).upper()}", align="C")

        try:
            if m == "تلوين فقط": self._coloring_mode(p, t)
            elif m == "قصص ورسومات": self._story_mode(p, t)
            elif m == "ألغاز منوعة": self._puzzles_mode(p, t)
            elif m == "تعليم (A-Z)": self._alphabet_mode(p)
            elif m == "كوميكس فقط": self._comics_mode(p, t)
            elif m == "وصل النقاط": self._dots_mode(p, t)
            elif m == "ملاحظات مسطرة": self._lined_mode(p)
            else: self._mixed_mode(p, t)
        except Exception as e:
            self.log(f"⚠️ خطأ صامت تم تجاوزه: {e}")

        clean_theme = re.sub(r'[^a-zA-Z0-9]', '_', t)[:30]
        fname = f"KDP_{clean_theme}_{int(time.time())}.pdf"
        self.pdf.output(fname)
        
        self.log("📝 جاري استخراج معلومات أمازون SEO...")
        fallback_seo = f"Title: Awesome {t} Activity Book\nSubtitle: Hours of fun!\nKeywords: kids, activity, {t}\nDescription: A great book."
        seo = SmartGemini.ask(f"Write KDP SEO for '{t}': Title, Subtitle, 7 Keywords, Description.", fallback_seo)
        
        return fname, seo

    def _coloring_mode(self, count, theme):
        self.log("🧠 جاري التفكير في الصور ورسمها في نفس الوقت (تسريع 3x)...")
        fallback_ideas = "\n".join([f"{theme} character {i}" for i in range(1, count+10)])
        ideas_raw = SmartGemini.ask(f"List {count+5} simple items for {theme} coloring. One per line.", fallback_ideas)
        ideas = [i.strip() for i in ideas_raw.split('\n') if len(i) > 2]
        
        tasks = []
        for i in range(count):
            item = ideas[i] if i < len(ideas) else f"cute {theme} {i}"
            tasks.append((item, f"tmp_{i}.jpg", "coloring"))
            
        results = ImageShield.generate_parallel(tasks, max_workers=3)
        
        for i in range(count):
            item = ideas[i] if i < len(ideas) else f"cute {theme} {i}"
            fname = f"tmp_{i}.jpg"
            if results.get(fname, False):
                self.pdf.add_page(); self.pdf.image(fname, x=1, y=1.5, w=6.5, h=6.5)
                os.remove(fname)
            else:
                self._emergency_page(f"Draw your own {clean_text(item)[:40]}!")
            self.pdf.add_page() 

    def _story_mode(self, count, theme):
        fallback_story = "||".join([f"The great {theme} adventure continues!" for _ in range(count)])
        raw = SmartGemini.ask(f"Write a {count} part simple story about {theme}. Split with '||'.", fallback_story)
        parts = [p.strip() for p in raw.split('||')]
        
        tasks = []
        for i in range(count):
            text = parts[i] if i < len(parts) else "Let's keep going!"
            tasks.append((f"scene of {text[:30]}", f"story_{i}.jpg", "coloring"))
            
        self.log("⚡ جاري رسم المشاهد القصصية بسرعة...")
        results = ImageShield.generate_parallel(tasks, max_workers=3)
        
        for i in range(count):
            text = parts[i] if i < len(parts) else "Let's keep going!"
            fname = f"story_{i}.jpg"
            self.pdf.add_page(); self.pdf.set_font("Arial", "I", 18); self.pdf.set_y(4)
            self.pdf.multi_cell(0, 0.5, clean_text(text), align="C")
            
            if results.get(fname, False):
                self.pdf.add_page(); self.pdf.image(fname, x=1, y=2, w=6.5, h=6.5)
                os.remove(fname)
            else:
                self._emergency_page("Draw this exciting scene!")
            self.pdf.add_page()

    def _puzzles_mode(self, count, theme):
        per = max(1, count // 2)
        for i in range(per):
            self.log(f"🧩 بناء سودوكو {i+1}...")
            b = PuzzleEngine.sudoku(); self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1); self.pdf.cell(0, 1, f"Sudoku #{i+1}", align="C")
            sx, sy, cs = 1.25, 2.5, 0.66
            self.pdf.set_line_width(0.01)
            for r in range(9):
                for c in range(9):
                    self.pdf.rect(sx+c*cs, sy+r*cs, cs, cs)
                    if b[r][c] != 0: self.pdf.text(sx+c*cs+0.25, sy+r*cs+0.45, str(b[r][c]))

        for i in range(per):
            self.log(f"🌀 بناء متاهة {i+1}...")
            g = PuzzleEngine.maze(); self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1); self.pdf.cell(0, 1, f"Maze #{i+1}", align="C")
            sx, sy, cs = 1.8, 2.5, 0.4
            self.pdf.set_line_width(0.04)
            for y in range(12):
                for x in range(12):
                    if g[y][x]['N']: self.pdf.line(sx+x*cs, sy+y*cs, sx+(x+1)*cs, sy+y*cs)
                    if g[y][x]['S']: self.pdf.line(sx+x*cs, sy+(y+1)*cs, sx+(x+1)*cs, sy+(y+1)*cs)
                    if g[y][x]['E']: self.pdf.line(sx+(x+1)*cs, sy+y*cs, sx+(x+1)*cs, sy+(y+1)*cs)
                    if g[y][x]['W']: self.pdf.line(sx+x*cs, sy+y*cs, sx+x*cs, sy+(y+1)*cs)

    def _alphabet_mode(self, count):
        L = list(string.ascii_uppercase)[:min(count, 26)]
        for char in L:
            self.log(f"✏️ تصميم الحرف {char}...")
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 100); self.pdf.set_y(2); self.pdf.cell(0, 1.5, char, align="C", ln=True)
            item = SmartGemini.ask(f"One word starting with {char} for coloring.", "Apple").strip()
            if ImageShield.generate(f"a cute {item}", "t.jpg"):
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1.5, y=2.5, w=5.5, h=5.5); os.remove("t.jpg")
            else: self._emergency_page(f"Draw a {item}!")
            self.pdf.add_page()

    def _dots_mode(self, count, theme):
        for i in range(count):
            self.log(f"📍 رسم وصل النقاط {i+1}...")
            if ImageShield.generate(f"dot-to-dot puzzle of {theme}", "t.jpg", "dots"):
                self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(4); self.pdf.cell(0, 1, "Draw Space", align="C")
                self.pdf.add_page(); self.pdf.image("t.jpg", x=1, y=1.5, w=6.5, h=7.5); os.remove("t.jpg")
                self.pdf.add_page()

    def _comics_mode(self, count, theme):
        for i in range(count):
            self.log(f"🦸 تسطير كوميكس {i+1}...")
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(0.8); self.pdf.cell(0, 1, f"Draw Your Comic", align="C")
            self.pdf.set_line_width(0.04)
            self.pdf.rect(0.75, 1.8, 3.4, 4); self.pdf.rect(4.35, 1.8, 3.4, 4); self.pdf.rect(0.75, 6.0, 7, 4.2)

    def _lined_mode(self, count):
        for _ in range(count):
            self.log("📏 تسطير صفحة ملاحظات...")
            self.pdf.add_page(); self.pdf.set_draw_color(200); self.pdf.set_line_width(0.01)
            for i in range(2, 11): self.pdf.line(1, i, 7.5, i)

    def _mixed_mode(self, count, theme):
        part = count // 3
        self._coloring_mode(part, theme)
        self._puzzles_mode(part, theme)
        self._story_mode(count - (part*2), theme)

# ==========================================
# 7. البوت الآلي الفائق (Hyper-Bot) في الخلفية
# ==========================================
def hyper_bot_loop():
    while True:
        try:
            if TELEGRAM_TOKEN and ALL_KEYS[0] != "DUMMY":
                theme = SmartGemini.ask("Output ONLY 2 words profitable KDP niche for kids (e.g. Space Dinosaurs).", "Ninja Cats").strip()
                # إنتاج كتاب بـ 24 صفحة (منوع) كإعداد افتراضي
                engine = ProductionEngine({'theme': theme, 'pages': 24, 'mode': 'منوع'}, lambda x: None)
                f, meta = engine.run()
                
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", 
                              data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ Hyper-Bot Book: {theme}"}, 
                              files={"document": open(f, "rb")})
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                              data={"chat_id": TELEGRAM_CHAT_ID, "text": meta})
        except: pass
        # نوم لمدة 15 دقيقة (900 ثانية)
        time.sleep(900)

# تفعيل البوت الآلي مرة واحدة عند بدء التطبيق
if not hasattr(st, 'hyper_bot_started'):
    st.hyper_bot_started = True
    threading.Thread(target=hyper_bot_loop, daemon=True).start()

# ==========================================
# 8. الواجهة الرئيسية
# ==========================================
def main():
    st.markdown('<h1 class="main-title">📚 KDP Factory Pro V28 👑</h1>', unsafe_allow_html=True)
    
    tabs = st.tabs(["⚡ الطور السريع", "💡 طور العبقري", "⚙️ الإعدادات"])

    with tabs[0]:
        st.info("اختر الإعدادات وسيقوم النظام بتوليد الكتاب فوراً.")
        c1, c2 = st.columns(2)
        with c1:
            u_t = st.text_input("🎯 موضوع الكتاب (Niche):", "Magic Ocean")
            u_p = st.number_input("📄 عدد الصفحات:", min_value=12, max_value=150, value=24, step=1, key="fast_pages")
        with c2:
            u_m = st.selectbox("🎭 النوع:", ["تلوين فقط", "قصص ورسومات", "ألغاز منوعة", "تعليم (A-Z)", "كوميكس فقط", "وصل النقاط", "ملاحظات مسطرة", "منوع"])
        
        if st.button("🚀 ابدأ الإنتاج السريع", use_container_width=True):
            run_prod(u_t, u_p, u_m)

    with tabs[1]:
        st.info("اكتب فكرتك بحرية وسيقوم الذكاء الاصطناعي بتخطيط الكتاب لك بأفضل طريقة لـ KDP.")
        o_t = st.text_input("🎯 الموضوع الأساسي (Theme):", placeholder="روبوتات في الغابة...")
        o_d = st.text_area("📝 وصف الفكرة بالتفصيل:", placeholder="كتاب أنشطة مسلي وتلوين...")
        o_p = st.number_input("📄 عدد الصفحات المطلوب:", min_value=12, max_value=150, value=30, step=1, key="genius_pages")
        
        if st.button("🪄 نفذ فكرتي العبقرية", use_container_width=True):
            with st.spinner("جاري التحليل..."):
                plan = SmartGemini.ask(f"Idea: {o_t}. Suggest best type: [قصص ورسومات, منوع, ألغاز منوعة]. Output strictly Arabic name.", "منوع")
                run_prod(o_t, o_p, plan if plan in ["قصص ورسومات", "منوع", "ألغاز منوعة"] else "منوع")

    with tabs[2]:
        st.info("🤖 **البوت الآلي (Hyper-Bot):** يعمل الآن في خلفية السيرفر! سيقوم بصنع كتاب واحد كل 15 دقيقة ويرسله لتليجرام تلقائياً دون تدخل منك. (تأكد من استخدام موقع UptimeRobot لمنع السيرفر من النوم).")
        st.success("⚡ **التوليد الموازي:** مفعل (تسريع 3x).")
        st.success("🛡️ **نظام التعويض:** مفعل (لا توجد صفحات مفقودة).")

def run_prod(t, p, m):
    stat = st.empty()
    try:
        engine = ProductionEngine({'theme':t, 'pages':p, 'mode':m}, stat.info)
        f, meta = engine.run()
        
        stat.success("🎉 اكتمل الإنتاج بالسرعة القصوى!")
        st.code(meta, language="markdown")
        
        with open(f, "rb") as b: st.download_button("⬇️ تحميل الملف محلياً", b, file_name=f)
        
        if TELEGRAM_TOKEN:
            try:
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ {t} جاهز!"}, files={"document": open(f, "rb")}, timeout=30)
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": meta}, timeout=20)
            except: pass
    except Exception as e:

