"""
KDP Factory Pro - The Stealth Mask V25
Architect: Irwin Smith | Logic: Fault Tolerance + Anti-Bot Bypass
Fixes: Cloudflare 403 Bypass (Headers), Fixed Truncation Bug
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

# ==========================================
# 1. درع استقرار الجلسة 
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    time.sleep(1)

st.set_page_config(page_title="KDP Factory Pro V25", page_icon="👑", layout="wide")

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
    def ask(cls, prompt, fallback_response):
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
        
        # قناع التخفي: نوهم السيرفر أننا متصفح جوجل كروم حقيقي وليس بوت بايثون
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }
        
        for attempt in range(3):
            try:
                time.sleep(1.5) 
                # إضافة قناع التخفي للطلب
                r = requests.get(url, headers=headers, timeout=30)
                if r.status_code == 200 and len(r.content) > 15000:
                    with open(filename, "wb") as f: f.write(r.content)
                    return True
            except:
                time.sleep(1)
                continue
        return False

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
        self.pdf.set_font("Arial", "B", 20) # تصغير الخط قليلاً لاستيعاب الجمل
        self.pdf.set_y(1)
        self.pdf.cell(0, 1, title, align="C", ln=True)
        self.pdf.set_line_width(0.05)
        self.pdf.rect(1, 2.5, 6.5, 7) 
        self.pdf.set_font("Arial", "I", 14)
        self.pdf.set_y(5)
        self.pdf.cell(0, 1, "Use your imagination to draw something amazing!", align="C")

    def run(self):
        t, p, m = self.config['theme'], self.config['pages'], self.config['mode']
        
        self.log(f"🎨 جاري رسم الغلاف الاحترافي لـ {t[:30]}...")
        if ImageShield.generate(t, "cover.jpg", "cover"):
            self.pdf.add_page(); self.pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11); os.remove("cover.jpg")
        else:
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 40); self.pdf.set_y(4)
            self.pdf.cell(0, 1, t.upper(), align="C")
        
        self.pdf.add_page(); self.pdf.set_font("Arial", "B", 30); self.pdf.set_y(4)
        self.pdf.multi_cell(0, 0.5, f"THE BIG BOOK OF\n{clean_text(t).upper()}", align="C")

        try:
            if m == "تلوين فقط": self._coloring_mode(p, t)
            elif m == "قصص ورسومات": self._story_mode(p, t)
            elif m == "ألغاز منوعة": self._puzzles_mode(p, t)
            else: self._mixed_mode(p, t)
        except Exception as e:
            self.log(f"⚠️ خطأ صامت تم تجاوزه: {e}")

        clean_theme = re.sub(r'[^a-zA-Z0-9]', '_', t)[:30]
        fname = f"KDP_{clean_theme}_{int(time.time())}.pdf"
        self.pdf.output(fname)
        
        self.log("📝 جاري استخراج معلومات أمازون SEO...")
        fallback_seo = f"Title: Awesome {t} Activity Book\nSubtitle: Hours of fun!\nKeywords: kids, book, activity, {t}, fun\nDescription: A great book for children."
        seo = SmartGemini.ask(f"Write KDP SEO for '{t}': Title, Subtitle, 7 Keywords, Description.", fallback_seo)
        
        return fname, seo

    def _coloring_mode(self, count, theme):
        fallback_ideas = "\n".join([f"{theme} character {i}" for i in range(1, count+10)])
        ideas_raw = SmartGemini.ask(f"List {count+5} simple items for {theme} coloring. One per line.", fallback_ideas)
        ideas = [i.strip() for i in ideas_raw.split('\n') if len(i) > 2]
        
        for i in range(count):
            item = ideas[i] if i < len(ideas) else f"cute {theme} {i}"
            self.log(f"🖍️ رسم صفحة {i+1}/{count}: {item[:20]}...")
            
            if ImageShield.generate(item, "tmp.jpg"):
                self.pdf.add_page(); self.pdf.image("tmp.jpg", x=1, y=1.5, w=6.5, h=6.5)
                os.remove("tmp.jpg")
            else:
                self.log(f"⚠️ فشلت الصورة {i+1} بسبب الحظر. جاري وضع صفحة رسم حر...")
                # زيادة مساحة القص لـ 40 حرف لمنع مشكلة cha!
                self._emergency_page(f"Draw your own {clean_text(item)[:40]}!")
            
            self.pdf.add_page() 

    def _story_mode(self, count, theme):
        fallback_story = "||".join([f"The great {theme} adventure continues!" for _ in range(count)])
        raw = SmartGemini.ask(f"Write a {count} part simple story about {theme}. Split with '||'.", fallback_story)
        parts = [p.strip() for p in raw.split('||')]
        
        for i in range(count):
            text = parts[i] if i < len(parts) else "Let's keep going!"
            self.log(f"📖 إعداد الجزء القصصي {i+1}...")
            
            self.pdf.add_page(); self.pdf.set_font("Arial", "I", 18); self.pdf.set_y(4)
            self.pdf.multi_cell(0, 0.5, clean_text(text), align="C")
            
            if ImageShield.generate(f"scene of {text[:30]}", "tmp.jpg"):
                self.pdf.add_page(); self.pdf.image("tmp.jpg", x=1, y=2, w=6.5, h=6.5)
                os.remove("tmp.jpg")
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

    def _mixed_mode(self, count, theme):
        part = count // 3
        self._coloring_mode(part, theme)
        self._puzzles_mode(part, theme)
        self._story_mode(count - (part*2), theme)

# ==========================================
# 7. الواجهة
# ==========================================
def main():
    st.markdown('<h1 class="main-title">📚 KDP Factory Pro V25 👑</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#888;">نظام "قناع التخفي": لتجاوز حظر السيرفرات</p>', unsafe_allow_html=True)

    tabs = st.tabs(["⚡ الطور السريع", "💡 طور العبقري", "⚙️ الإعدادات"])

    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            u_t = st.text_input("🎯 موضوع الكتاب:", "Magic Ocean")
            u_p = st.number_input("📄 عدد الصفحات:", 12, 100, 12, key="fp")
        with c2:
            u_m = st.selectbox("🎭 النوع:", ["تلوين فقط", "قصص ورسومات", "ألغاز منوعة", "منوع"])
        
        if st.button("🚀 ابدأ الإنتاج السريع", use_container_width=True):
            run_prod(u_t, u_p, u_m)

    with tabs[1]:
        o_t = st.text_input("🎯 الموضوع الأساسي:", placeholder="روبوتات في الغابة...")
        o_d = st.text_area("📝 وصف الفكرة:", placeholder="كتاب أنشطة مسلي وتلوين...")
        o_p = st.number_input("📄 عدد الصفحات:", 12, 100, 20, key="op")
        
        if st.button("🪄 نفذ فكرتي العبقرية", use_container_width=True):
            with st.spinner("جاري التحليل..."):
                plan = SmartGemini.ask(f"Idea: {o_t}. Suggest best type: [قصص ورسومات, منوع, ألغاز منوعة]. Output strictly Arabic name.", "منوع")
                run_prod(o_t, o_p, plan if plan in ["قصص ورسومات", "منوع", "ألغاز منوعة"] else "منوع")

    with tabs[2]:
        st.info("نظام (User-Agent Stealth) مُفعّل لمنع حظر موقع الصور لطلبات السيرفر الخاص بك.")

def run_prod(t, p, m):
    stat = st.empty()
    try:
        engine = ProductionEngine({'theme':t, 'pages':p, 'mode':m}, stat.info)
        f, meta = engine.run()
        
        stat.success("🎉 اكتمل الإنتاج!")
        st.code(meta, language="markdown")
        
        with open(f, "rb") as b: st.download_button("⬇️ تحميل محلي", b, file_name=f)
        
        if TELEGRAM_TOKEN:
            try:
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID}, files={"document": open(f, "rb")}, timeout=30)
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": f"✅ الكتاب جاهز!\n{meta}"}, timeout=20)
            except:
                st.warning("⚠️ تم بناء الكتاب بنجاح، لكن فشل إرساله عبر تليجرام.")
                
    except Exception as e:
        st.error("❌ حدث خطأ، ولكن الكود لا يزال يعمل.")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
