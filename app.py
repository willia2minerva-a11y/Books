"""
KDP Factory Pro - Mobile-First & Telegram Optimized V31.0
Architect & CEO: Walid Zaki | Logic: Responsive UI, Dual Telegram Delivery
Features: Mobile Layout, PDF+Text Telegram, Bestseller AI, Hyper-Bot
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
import zipfile
import io
from datetime import datetime

# ==========================================
# 1. تهيئة الجلسة الأساسية
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    time.sleep(1)

st.set_page_config(page_title="KDP Empire V31", page_icon="📱", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    p, h1, h2, h3, h4, h5, h6, label, .stMarkdown, li { direction: rtl; text-align: right; }
    
    /* جعل العنوان الرئيسي متجاوباً مع الهواتف */
    .main-title {
        background: linear-gradient(90deg, #1CB5E0 0%, #000851 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem; font-weight: 900; text-align: center; margin: 0; direction: ltr;
    }
    .sub-title { text-align: center; color: #666; font-size: 1rem; margin-bottom: 20px; direction: ltr;}
    
    /* جعل التبويبات تلتف بشكل جميل على الشاشات الصغيرة */
    .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #f8f9fa; border-radius: 8px; padding: 10px 20px; font-weight: bold;}
    .stTabs [aria-selected="true"] { background-color: #1CB5E0; color: white; }
    
    input, textarea { text-align: left !important; direction: ltr !important; border-radius: 8px !important;}
    .stButton>button { border-radius: 8px; font-weight: bold; padding: 12px; font-size: 1.1rem;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة المفاتيح
# ==========================================
def get_all_keys():
    keys = [os.getenv(f"GEMINI_API_KEY_{i}", "") for i in range(1, 6)]
    valid = [k.strip() for k in keys if k.strip()]
    if valid:
        return valid
    else:
        return ["DUMMY"]

ALL_KEYS = get_all_keys()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def clean_text(text):
    if not text: 
        return ""
    return text.encode('latin-1', 'ignore').decode('latin-1').replace('\n', ' ')

# ==========================================
# 3. محرك عقل الإمبراطورية (Smart Gemini)
# ==========================================
class SmartGemini:
    @classmethod
    def ask(cls, prompt, fallback=""):
        if ALL_KEYS[0] == "DUMMY": 
            return fallback
            
        random.shuffle(ALL_KEYS)
        for key in ALL_KEYS:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(prompt)
                if res.text: 
                    return res.text.strip()
            except Exception: 
                continue 
                
        return fallback

# ==========================================
# 4. مصنع الصور (Stealth Shield)
# ==========================================
class ImageShield:
    @staticmethod
    def generate(prompt, filename, style="coloring"):
        if style == "cover": 
            p = f"Bestselling aesthetic children book cover, {prompt}, vibrant, blank background, STRICTLY NO TEXT NO LETTERS"
        elif style == "flashcard": 
            p = f"Cute simple vector illustration of {prompt}, isolated on pure white background, thick lines, colorful, educational flashcard style"
        else: 
            p = f"Bold black and white line art, {prompt}, thick clean outlines, pure white background, NO shading, kids coloring page"
        
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36'}
        
        for _ in range(3):
            try:
                time.sleep(1.5)
                r = requests.get(url, headers=headers, timeout=30)
                if r.status_code == 200 and len(r.content) > 15000:
                    with open(filename, "wb") as f: 
                        f.write(r.content)
                    return True
            except Exception: 
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
                try: 
                    results[filename] = future.result()
                except Exception: 
                    results[filename] = False
                    
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
        for p in random.sample(range(s*s), s*s*2//3): 
            board[p//s][p%s] = 0
        return board

    @staticmethod
    def maze(w=12, h=12):
        grid = [[{'N':True, 'S':True, 'E':True, 'W':True, 'v':False} for _ in range(w)] for _ in range(h)]
        stack = [(0, 0)]
        grid[0][0]['v'] = True
        
        while stack:
            cx, cy = stack[-1]
            dirs = [('N', 0,-1,'S'), ('S', 0,1,'N'), ('E', 1,0,'W'), ('W', -1,0,'E')]
            random.shuffle(dirs)
            moved = False
            for d, dx, dy, opp in dirs:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < w and 0 <= ny < h and not grid[ny][nx]['v']:
                    grid[cy][cx][d] = False
                    grid[ny][nx][opp] = False
                    grid[ny][nx]['v'] = True
                    stack.append((nx, ny))
                    moved = True
                    break
            if not moved: 
                stack.pop()
                
        grid[0][0]['W'] = False
        grid[h-1][w-1]['E'] = False
        return grid

# ==========================================
# 6. صانع الكتب و الأصول الرقمية (KDP Factory)
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

    def _add_belongs_to_page(self):
        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 28)
        self.pdf.set_y(3)
        self.pdf.cell(0, 1, "This Book Belongs To:", align="C", ln=True)
        self.pdf.set_line_width(0.02)
        self.pdf.line(1.5, 4.5, 7.0, 4.5)

    def run(self):
        t = self.config['theme']
        p = self.config['pages']
        m = self.config['mode']
        
        self.log(f"🎨 جاري رسم الغلاف الاحترافي لـ {t[:30]}...")
        if ImageShield.generate(t, "cover.jpg", "cover"):
            self.pdf.add_page()
            self.pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11)
            if os.path.exists("cover.jpg"):
                os.remove("cover.jpg")
        else:
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 40)
            self.pdf.set_y(4)
            self.pdf.cell(0, 1, t.upper(), align="C")
        
        # Copyright Page (Walid Zaki)
        self.pdf.add_page()
        self.pdf.set_font("Arial", "I", 12)
        self.pdf.set_y(9)
        self.pdf.cell(0, 0.5, f"© {datetime.now().year} Published by Walid Zaki. All Rights Reserved.", align="C")

        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 30)
        self.pdf.set_y(4)
        self.pdf.multi_cell(0, 0.5, f"THE BIG BOOK OF\n{clean_text(t).upper()}", align="C")

        try:
            if m == "تلوين للأطفال": 
                self._coloring_mode(p, t)
            elif m == "قصص مصورة": 
                self._story_mode(p, t)
            elif m == "ألغاز ونشاطات": 
                self._puzzles_mode(p, t)
            elif m == "تعليم وتتبع": 
                self._alphabet_mode(p)
            elif m == "مخططات ودفاتر": 
                self._journal_mode(p, t)
            elif m == "كتب اقتباسات": 
                self._quotes_mode(p, t)
            elif m == "بطاقات تعليمية": 
                self._flashcards_mode(p, t)
            elif m == "كوميكس ومانغا": 
                self._comics_mode(p, t)
            else: 
                self._mixed_mode(p, t)
        except Exception as e:
            self.log(f"⚠️ تجاوز آمن لخطأ: {e}")

        clean_theme = re.sub(r'[^a-zA-Z0-9]', '_', t)[:20]
        pdf_name = f"Book_{clean_theme}_{int(time.time())}.pdf"
        self.pdf.output(pdf_name)
        
        self.log("📝 جاري هندسة الـ SEO وسكريبت الـ TikTok...")
        marketing_prompt = f"Act as a KDP and TikTok Marketing Expert. Create a launch package for a book titled '{t}'.\n1. KDP SEO: Catchy Title, Subtitle, 7 Keywords, Persuasive Description.\n2. VIRAL TIKTOK SCRIPT: A 30-second video script to sell this book organically."
        marketing_data = SmartGemini.ask(marketing_prompt, f"Title: {t}\nDescription: Amazing activity book for kids.\n\nTikTok Script:\nHey guys! Check out this awesome {t} book!")
        
        # إعادة الملف النصي والنص الخام بدلاً من الـ ZIP فقط
        return pdf_name, marketing_data

    # --- Modes (مصانع المحتوى) ---
    def _coloring_mode(self, count, theme):
        ideas = SmartGemini.ask(f"List {count+5} simple items for {theme} coloring. Names only.", "Item").split('\n')
        tasks = [(clean_text(item), f"tmp_{i}.jpg", "coloring") for i, item in enumerate(ideas[:count]) if len(item)>2]
        results = ImageShield.generate_parallel(tasks)
        
        for i, (item, fname, _) in enumerate(tasks):
            if results.get(fname, False):
                self.pdf.add_page()
                self.pdf.image(fname, x=1, y=1.5, w=6.5, h=6.5)
                if os.path.exists(fname):
                    os.remove(fname)
            else:
                self.pdf.add_page()
                self.pdf.set_font("Arial", "B", 20)
                self.pdf.set_y(5)
                self.pdf.cell(0, 1, f"Draw a {item[:30]}!", align="C")
            self.pdf.add_page() 

    def _story_mode(self, count, theme):
        parts = SmartGemini.ask(f"Write a {count} part children's story about {theme}. Split with '||'.", "Story continues||").split('||')
        tasks = [(f"scene of {text[:30]}", f"story_{i}.jpg", "coloring") for i, text in enumerate(parts[:count])]
        results = ImageShield.generate_parallel(tasks)
        
        for i, (prompt, fname, _) in enumerate(tasks):
            self.pdf.add_page()
            self.pdf.set_font("Arial", "I", 18)
            self.pdf.set_y(4)
            self.pdf.multi_cell(0, 0.5, clean_text(parts[i]), align="C")
            
            if results.get(fname, False):
                self.pdf.add_page()
                self.pdf.image(fname, x=1, y=2, w=6.5, h=6.5)
                if os.path.exists(fname):
                    os.remove(fname)
            else: 
                self.pdf.add_page()
            self.pdf.add_page()

    def _puzzles_mode(self, count, theme):
        per = max(1, count // 2)
        for i in range(per):
            b = PuzzleEngine.sudoku()
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 24)
            self.pdf.set_y(1)
            self.pdf.cell(0, 1, f"Sudoku #{i+1}", align="C")
            sx, sy, cs = 1.25, 2.5, 0.66
            self.pdf.set_line_width(0.01)
            for r in range(9):
                for c in range(9):
                    self.pdf.rect(sx+c*cs, sy+r*cs, cs, cs)
                    if b[r][c] != 0: 
                        self.pdf.text(sx+c*cs+0.25, sy+r*cs+0.45, str(b[r][c]))
                        
        for i in range(per):
            g = PuzzleEngine.maze()
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 24)
            self.pdf.set_y(1)
            self.pdf.cell(0, 1, f"Maze #{i+1}", align="C")
            sx, sy, cs = 1.8, 2.5, 0.4
            self.pdf.set_line_width(0.04)
            for y in range(12):
                for x in range(12):
                    if g[y][x]['N']: 
                        self.pdf.line(sx+x*cs, sy+y*cs, sx+(x+1)*cs, sy+y*cs)
                    if g[y][x]['S']: 
                        self.pdf.line(sx+x*cs, sy+(y+1)*cs, sx+(x+1)*cs, sy+(y+1)*cs)

    def _alphabet_mode(self, count):
        L = list(string.ascii_uppercase)[:min(count, 26)]
        for char in L:
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 100)
            self.pdf.set_y(2)
            self.pdf.cell(0, 1.5, char, align="C", ln=True)
            self.pdf.set_font("Arial", "", 24)
            self.pdf.cell(0, 1, f"Trace:", align="C", ln=True)
            self.pdf.set_text_color(200)
            self.pdf.cell(0, 1, f"{char} {char} {char}", align="C")
            self.pdf.set_text_color(0)
            self.pdf.add_page()

    def _journal_mode(self, count, theme):
        self.log("📏 هندسة المخططات اليومية...")
        for i in range(count):
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 18)
            self.pdf.set_y(1)
            self.pdf.cell(0, 1, f"Day {i+1} - Focus: {clean_text(theme)[:20]}", ln=True)
            self.pdf.set_font("Arial", "I", 12)
            self.pdf.cell(0, 0.5, "Top 3 priorities today:", ln=True)
            self.pdf.set_draw_color(150)
            self.pdf.set_line_width(0.01)
            for y in range(3, 10): 
                self.pdf.line(1, y, 7.5, y)
            self.pdf.set_draw_color(0)

    def _quotes_mode(self, count, theme):
        self.log("💭 تأليف الاقتباسات...")
        quotes = SmartGemini.ask(f"Write {count} profound, short motivational quotes about {theme}. One per line.", "Be strong.\nStay focused.").split('\n')
        for i in range(count):
            q = quotes[i] if i < len(quotes) else "Keep moving forward."
            self.pdf.add_page()
            self.pdf.set_line_width(0.05)
            self.pdf.rect(0.5, 0.5, 7.5, 10) 
            self.pdf.set_font("Arial", "I", 22)
            self.pdf.set_y(4)
            self.pdf.multi_cell(0, 0.6, clean_text(q), align="C")

    def _flashcards_mode(self, count, theme):
        self.log("🃏 تصميم البطاقات التعليمية...")
        words = SmartGemini.ask(f"List {count} simple educational words related to {theme} for flashcards. One per line.", "Sun\nMoon").split('\n')
        tasks = [(clean_text(w), f"flash_{i}.jpg", "flashcard") for i, w in enumerate(words[:count]) if len(w)>2]
        results = ImageShield.generate_parallel(tasks)
        for i, (word, fname, _) in enumerate(tasks):
            self.pdf.add_page()
            self.pdf.set_line_width(0.05)
            self.pdf.rect(1.25, 2, 6, 7) 
            if results.get(fname, False):
                self.pdf.image(fname, x=1.5, y=2.5, w=5.5, h=5.5)
                if os.path.exists(fname):
                    os.remove(fname)
            self.pdf.set_font("Arial", "B", 36)
            self.pdf.set_y(8.2)
            self.pdf.cell(0, 1, word.upper(), align="C")

    def _comics_mode(self, count, theme):
        for i in range(count):
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 24)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 1, f"My {clean_text(theme)[:15]} Comic", align="C")
            self.pdf.set_line_width(0.04)
            self.pdf.rect(0.75, 1.8, 3.4, 4)
            self.pdf.rect(4.35, 1.8, 3.4, 4)
            self.pdf.rect(0.75, 6.0, 7, 4.2)

    def _mixed_mode(self, count, theme):
        part = count // 4
        self._coloring_mode(part, theme)
        self._puzzles_mode(part, theme)
        self._journal_mode(part, theme)
        self._quotes_mode(count - (part*3), theme)

# ==========================================
# 7. البوت الآلي الفائق (Hyper-Bot)
# ==========================================
def hyper_bot_loop():
    while True:
        try:
            if TELEGRAM_TOKEN and ALL_KEYS[0] != "DUMMY":
                theme = SmartGemini.ask("Output ONLY 2 words highly profitable KDP micro-niche for kids (e.g. Cyberpunk Cats).", "Ninja Cats").strip()
                engine = ProductionEngine({'theme': theme, 'pages': 24, 'mode': 'تشكيلة منوعة'}, lambda x: None)
                pdf_file, meta = engine.run()
                
                try:
                    # 1. إرسال الكتاب كـ PDF
                    with open(pdf_file, "rb") as f:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", 
                                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"📚 كتاب آلي جديد: {theme}"}, 
                                      files={"document": f}, timeout=30)
                    
                    # 2. إرسال النصوص والمعلومات كرسالة منفصلة
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "text": f"📊 تفاصيل النشر لـ {theme}:\n\n{meta}"}, timeout=20)
                except Exception: 
                    pass
                finally:
                    # تنظيف السيرفر
                    if os.path.exists(pdf_file):
                        os.remove(pdf_file)
        except Exception: 
            pass
            
        time.sleep(900)

if not hasattr(st, 'hyper_bot_started'):
    st.hyper_bot_started = True
    threading.Thread(target=hyper_bot_loop, daemon=True).start()

# ==========================================
# 8. واجهة الإمبراطورية (The Dashboard - Mobile Optimized)
# ==========================================
def main():
    st.markdown('<h1 class="main-title">KDP Digital Empire V31 🏭</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Engineered by Walid Zaki | Mobile Optimized Factory</p>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🏭 المصنع السريع", "🧠 عقل الإمبراطورية", "🤖 الأتمتة الشاملة", "⚙️ الإعدادات"])

    with tabs[0]:
        st.info("اختر خط الإنتاج المباشر وسيتم تصنيع حزمة النشر الخاصة بك.")
        # تم إزالة الأعمدة لتصبح الواجهة عمودية ومتوافقة 100% مع شاشات الهواتف
        u_t = st.text_input("🎯 فكرة النيش (Niche):", "Cyberpunk Dinosaurs")
        u_p = st.number_input("📄 حجم الكتاب (صفحات):", min_value=10, max_value=150, value=20, step=1)
        modes = ["تلوين للأطفال", "قصص مصورة", "ألغاز ونشاطات", "مخططات ودفاتر", "بطاقات تعليمية", "كتب اقتباسات", "كوميكس ومانغا", "تعليم وتتبع", "تشكيلة منوعة"]
        u_m = st.selectbox("📦 خط الإنتاج الرقمي:", modes)
        
        if st.button("🚀 تصنيع وحفظ الحزمة الرقمية", use_container_width=True):
            run_prod(u_t, u_p, u_m)

    with tabs[1]:
        st.info("أدخل فكرتك الخام، وسيقوم الذكاء الاصطناعي بهندستها عكسياً من أفضل الكتب مبيعاً.")
        o_t = st.text_input("🎯 الموضوع الأساسي:", placeholder="مثلاً: يوميات للطلاب، أطباق كيتو...")
        o_p = st.number_input("📄 عدد الصفحات المستهدف:", min_value=10, max_value=150, value=30, step=1)
        
        if st.button("🪄 ابدأ الهندسة العكسية", use_container_width=True):
            with st.spinner("جاري تحليل خوارزميات أمازون..."):
                plan = SmartGemini.ask(f"Idea: {o_t}. Suggest best output from: [قصص مصورة, ألغاز ونشاطات, مخططات ودفاتر, كتب اقتباسات, بطاقات تعليمية]. Output strict Arabic name.", "مخططات ودفاتر")
                st.success(f"النوع الأمثل لضرب المنافسة هو: {plan}")
                run_prod(o_t, o_p, plan if plan in modes else "تشكيلة منوعة")

    with tabs[2]:
        st.success("🟢 **حالة الـ Hyper-Bot:** نشط ويعمل في خلفية السيرفر. يقوم بتوليد حزمة نشر جديدة كل 15 دقيقة (كتاب PDF + رسالة منفصلة لـ SEO وسكريبت تيك توك) ويرسلها إليك مباشرة.")
        st.info("📊 **استراتيجية الإمبراطورية:** أنت الآن تمتلك مصنعاً ينتج الأصول الرقمية بلا توقف. اترك الموقع يعمل أو استخدم UptimeRobot.")

    with tabs[3]:
        st.success("✅ تم تأمين العلامة التجارية (Walid Zaki) في ملفات الـ PDF.")
        st.success("📱 واجهة المستخدم الآن محسنة بالكامل لشاشات الهواتف المحمولة.")

def run_prod(t, p, m):
    stat = st.empty()
    try:
        engine = ProductionEngine({'theme':t, 'pages':p, 'mode':m}, stat.info)
        pdf_file, meta = engine.run()
        
        # إنشاء ملف ZIP للتحميل اليدوي عبر الموقع
        zip_buffer = io.BytesIO()
        zip_name = f"KDP_AssetPack_{int(time.time())}.zip"
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.write(pdf_file)
            zf.writestr("01_Marketing_And_TikTok_Script.txt", meta)
            
        stat.success("🎉 اكتمل التصنيع! حزمتك الرقمية جاهزة.")
        
        with st.expander("👀 معاينة خطة التسويق وسكريبت TikTok", expanded=True):
            st.code(meta, language="markdown")
            
        st.download_button("📦 تحميل الحزمة الشاملة (ZIP)", zip_buffer.getvalue(), file_name=zip_name, use_container_width=True)
        
        if TELEGRAM_TOKEN:
            try:
                # 1. إرسال ملف PDF فقط
                with open(pdf_file, "rb") as f:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"📚 كتاب {t} جاهز للرفع!"}, 
                                  files={"document": f}, timeout=30)
                # 2. إرسال النصوص كرسالة
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                              data={"chat_id": TELEGRAM_CHAT_ID, "text": f"📊 معلومات الـ SEO:\n\n{meta}"}, timeout=20)
            except Exception: 
                pass
                
        # تنظيف الملف من السيرفر بعد الانتهاء
        if os.path.exists(pdf_file):
            os.remove(pdf_file)
            
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

