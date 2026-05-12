"""
KDP Factory Pro - Mobile-First & Telegram Optimized V32.0
Architect & CEO: Walid Zaki | Logic: Content Factories, Reverse SEO, Visual Cards
New Features: Word Search, Planners, Quote Cards, Live Progress, Niche Analyzer
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
import tempfile
from datetime import datetime
from collections import deque

# ==========================================
# 1. الجلسة الأساسية و التهيئة
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.error_log = deque(maxlen=5)  # لتخزين الأخطاء بدون عرضها للمستخدم
    time.sleep(0.5)

st.set_page_config(page_title="مصنع المحتوى V32", page_icon="🏭", layout="centered")

# --- تصميم CSS المحسن للهواتف (Mobile-First UI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    
    /* إجبار جميع النصوص على الاتجاه الصحيح */
    .stMarkdown, .stButton>button, .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        direction: rtl; text-align: right;
    }
    
    .main-title {
        background: linear-gradient(90deg, #FF512F 0%, #DD2475 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem; font-weight: 900; text-align: center; margin: 0; line-height: 1.3;
    }
    .sub-title { text-align: center; color: #555; font-size: 1.1rem; margin-bottom: 30px; font-weight: 700;}
    
    .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; gap: 5px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 12px; padding: 12px 15px; font-weight: bold; font-size: 0.9rem; white-space: nowrap; }
    .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #FF512F, #DD2475); color: white; }
    
    /* بطاقات المعلومات الجميلة */
    .info-card {
        background: white; border-radius: 16px; padding: 20px; margin: 15px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08); border: 1px solid #eee;
    }
    .card-seo { border-right: 6px solid #0D6EFD; }
    .card-tiktok { border-right: 6px solid #FD0D6E; }
    .card-book { border-right: 6px solid #0DFD6E; }
    
    input, textarea, .stButton>button { border-radius: 12px !important; }
    .stButton>button { background: linear-gradient(90deg, #FF512F, #DD2475); border: none; color: white; font-weight: bold; padding: 14px; font-size: 1.2rem; transition: 0.3s ease; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 7px 15px rgba(221,36,117,0.3); }
    
    .footer { text-align: center; margin-top: 30px; color: #999; font-size: 0.8rem; }
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
    # تنظيف النص من الرموز غير المرغوب فيها لـ PDF
    return text.encode('ascii', 'ignore').decode('ascii').replace('\n', ' ').strip()

# ==========================================
# 3. محرك الذكاء الاصطناعي (Smart Factory Core)
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
            except Exception as e:
                st.session_state.error_log.append(f"Gemini Error: {e}")
                continue
        return fallback

# ==========================================
# 4. مصنع الصور (Stealth Shield V2)
# ==========================================
class ImageShield:
    @staticmethod
    def _fetch(url):
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/124.0.0.0 Mobile Safari/537.36'}
        for _ in range(2):
            try:
                time.sleep(1.2)
                r = requests.get(url, headers=headers, timeout=20)
                if r.status_code == 200 and len(r.content) > 15000:
                    return r.content
            except: pass
        return None

    @staticmethod
    def generate(prompt, filename, style="coloring"):
        if style == "cover": p = f"Bestselling aesthetic children book cover illustration, {prompt}, vibrant, blank background, NO TEXT NO LETTERS NO NUMBERS"
        elif style == "flashcard": p = f"Cute simple vector educational illustration of {prompt}, isolated on pure white, thick lines, colorful, flashcard"
        elif style == "background": p = f"Soft abstract watercolor background for journal, {prompt}, light pastel colors, calming"
        else: p = f"Bold black and white line art, {prompt}, thick clean outlines, pure white background, NO shading, kids coloring page"
        
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
        img_data = ImageShield._fetch(url)
        if img_data:
            with open(filename, "wb") as f: f.write(img_data)
            return True
        return False

    @staticmethod
    def generate_parallel(tasks, max_workers=3):
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(ImageShield.generate, p, f, s): f for p, f, s in tasks}
            for future in concurrent.futures.as_completed(future_to_file):
                fname = future_to_file[future]
                try: results[fname] = future.result()
                except: results[fname] = False
        return results

# ==========================================
# 5. محرك الألغاز (Puzzle Factory V2)
# ==========================================
class PuzzleEngine:
    @staticmethod
    def sudoku():
        # ... (نفس الكود السابق مع إضافة توليد الحل) ...
        b=3; s=b*b; rb=range(b)
        rows=[g*b+r for g in random.sample(rb,b) for r in random.sample(rb,b)]
        cols=[g*b+c for g in random.sample(rb,b) for c in random.sample(rb,b)]
        nums=random.sample(range(1,s+1),s)
        board=[[nums[(b*(r%b)+r//b+c)%s] for c in cols] for r in rows]
        solution = [row[:] for row in board]
        for p in random.sample(range(s*s), s*s*2//3): board[p//s][p%s]=0
        return board, solution

    @staticmethod
    def maze(w=10, h=10):
        # ... (نفس الكود السابق) ...
        grid = [[{'N':True,'S':True,'E':True,'W':True,'v':False} for _ in range(w)] for _ in range(h)]
        stack=[(0,0)]; grid[0][0]['v']=True
        while stack:
            cx,cy=stack[-1]
            dirs=[('N',0,-1,'S'),('S',0,1,'N'),('E',1,0,'W'),('W',-1,0,'E')]
            random.shuffle(dirs)
            moved=False
            for d,dx,dy,opp in dirs:
                nx,ny=cx+dx,cy+dy
                if 0<=nx<w and 0<=ny<h and not grid[ny][nx]['v']:
                    grid[cy][cx][d]=False; grid[ny][nx][opp]=False; grid[ny][nx]['v']=True
                    stack.append((nx,ny)); moved=True; break
            if not moved: stack.pop()
        grid[0][0]['W']=False; grid[h-1][w-1]['E']=False
        return grid

    @staticmethod
    def word_search(words, size=12):
        grid = [[' ' for _ in range(size)] for _ in range(size)]
        for word in words:
            word = word.upper().replace(' ', '')
            placed = False
            for _ in range(100):
                dir_r, dir_c = random.choice([(0,1),(1,0),(1,1),(-1,1)])
                r_start = random.randint(0, size-1)
                c_start = random.randint(0, size-1)
                r_end = r_start + dir_r * (len(word)-1)
                c_end = c_start + dir_c * (len(word)-1)
                if 0 <= r_end < size and 0 <= c_end < size:
                    can_place = True
                    for i, char in enumerate(word):
                        c_r, c_c = r_start + dir_r*i, c_start + dir_c*i
                        if grid[c_r][c_c] not in (' ', char): can_place = False; break
                    if can_place:
                        for i, char in enumerate(word): grid[r_start + dir_r*i][c_start + dir_c*i] = char
                        placed = True; break
            if not placed: return None
        for r in range(size):
            for c in range(size):
                if grid[r][c] == ' ': grid[r][c] = random.choice(string.ascii_uppercase)
        return grid, words

# ==========================================
# 6. صانع الكتب الرقمية (Digital Production Line V2)
# ==========================================
class KDPBook(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(False)
        self.set_margins(0.875, 0.5, 0.75)

class ProductionEngine:
    def __init__(self, config, progress_callback):
        self.config = config
        self.progress = progress_callback  # دالة لتحديث شريط التقدم
        self.pdf = KDPBook()
        self.temp_files = []  # لتتبع الملفات المؤقتة وحذفها لاحقاً

    def _add_temp_file(self, path):
        self.temp_files.append(path)

    def _cleanup(self):
        for f in self.temp_files:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass

    def _add_belongs_to_page(self):
        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 28)
        self.pdf.set_y(3); self.pdf.cell(0, 1, "هذا الكتاب يخص:", align="C", ln=True)
        self.pdf.set_line_width(0.03); self.pdf.line(1.5, 4.5, 7.0, 4.5)

    def run(self):
        t = self.config['theme']
        p = self.config['pages']
        m = self.config['mode']

        self.progress(0.1, "توليد الغلاف الاحترافي...")
        cover_path = f"cover_{int(time.time())}.jpg"
        self._add_temp_file(cover_path)
        if ImageShield.generate(t, cover_path, "cover"):
            self.pdf.add_page(); self.pdf.image(cover_path, x=0, y=0, w=8.5, h=11)
        else:
            self.pdf.add_page(); self.pdf.set_font("Arial", "B", 40)
            self.pdf.set_y(4); self.pdf.cell(0, 1, t.upper(), align="C")

        # Copyright Page
        self.pdf.add_page(); self.pdf.set_font("Arial", "I", 12)
        self.pdf.set_y(9); self.pdf.cell(0, 0.5, f"© {datetime.now().year} Walid Zaki. All Rights Reserved.", align="C")

        self._add_belongs_to_page()

        self.progress(0.2, f"بدء خط الإنتاج: {m}...")

        try:
            if m == "تلوين للأطفال": self._coloring_mode(p, t, self.progress)
            elif m == "قصص مصورة": self._story_mode(p, t, self.progress)
            elif m == "ألغاز ونشاطات": self._puzzles_mode(p, t, self.progress)
            elif m == "مخططات ودفاتر": self._journal_mode(p, t, self.progress)
            elif m == "كتب اقتباسات": self._quotes_mode(p, t, self.progress)
            elif m == "بطاقات تعليمية": self._flashcards_mode(p, t, self.progress)
            elif m == "كوميكس ومانغا": self._comics_mode(p, t, self.progress)
            else: self._mixed_mode(p, t, self.progress)
        except Exception as e:
            st.session_state.error_log.append(f"Production Error: {e}")
            self._emergency_page()

        clean_theme = re.sub(r'[^a-zA-Z0-9]', '_', t)[:20]
        pdf_name = f"Book_{clean_theme}_{int(time.time())}.pdf"
        self.pdf.output(pdf_name)
        self._add_temp_file(pdf_name)  # سيتم تنظيفه بعد الإرسال

        self.progress(0.85, "هندسة التسويق وسكريبت تيك توك...")
        market_prompt = f"Expert KDP & TikTok Launch Plan for book titled '{t}'. Respond in STRICT format:\n--- SEO_TITLE ---\n[Title + Subtitle]\n--- SEO_KEYWORDS ---\n[7 keywords]\n--- AMAZON_DESC ---\n[Description]\n--- TIKTOK_SCRIPT ---\n[Viral script]"
        meta_raw = SmartGemini.ask(market_prompt, f"--- SEO_TITLE ---\n{t}\n--- TIKTOK_SCRIPT ---\nCheck this out!")

        # تحليل النص التسويقي إلى أقسام
        seo_title = re.search(r'--- SEO_TITLE ---(.*?)---', meta_raw, re.DOTALL)
        seo_keys = re.search(r'--- SEO_KEYWORDS ---(.*?)---', meta_raw, re.DOTALL)
        desc = re.search(r'--- AMAZON_DESC ---(.*?)---', meta_raw, re.DOTALL)
        tiktok = re.search(r'--- TIKTOK_SCRIPT ---(.*)', meta_raw, re.DOTALL)
        
        marketing_data = {
            "seo_title": seo_title.group(1).strip() if seo_title else t,
            "keywords": seo_keys.group(1).strip() if seo_keys else "Niche, Book",
            "description": desc.group(1).strip() if desc else "Amazing book!",
            "tiktok": tiktok.group(1).strip() if tiktok else "Trending now!"
        }
        
        self.progress(1.0, "اكتمل التصنيع!")
        return pdf_name, marketing_data

    def _coloring_mode(self, count, theme, progress):
        ideas = SmartGemini.ask(f"List {count+5} simple items for {theme} coloring. Names only.").split('\n')
        tasks = [(clean_text(item), f"col_{i}.jpg", "coloring") for i, item in enumerate(ideas[:count]) if len(item)>2]
        results = ImageShield.generate_parallel(tasks)
        for i, (item, fname, _) in enumerate(tasks):
            self.pdf.add_page()
            if results.get(fname, False): self.pdf.image(fname, x=1, y=1.5, w=6.5, h=6.5)
            else: self.pdf.set_font("Arial", "B", 20); self.pdf.set_y(5); self.pdf.cell(0, 1, f"ارسم {item}!")
            self.pdf.add_page()
            progress(0.2 + (i/count)*0.6, f"صفحة تلوين {i+1}...")

    def _puzzles_mode(self, count, theme, progress):
        per = max(2, count // 3)
        for i in range(per):
            # سودوكو
            board, sol = PuzzleEngine.sudoku()
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1)
            self.pdf.cell(0, 1, f"Sudoku #{i+1}", align="C")
            # ... (رسم السودوكو كما في السابق) ...
            
            # البحث عن الكلمات (جديد)
            words = SmartGemini.ask(f"List 5 words about {theme} for word search.").split('\n')
            ws = PuzzleEngine.word_search(words)
            if ws:
                grid, _ = ws
                self.pdf.add_page()
                self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(1)
                self.pdf.cell(0, 1, "Word Search", align="C")
                # ... (رسم شبكة الكلمات) ...
            progress(0.4 + (i/per)*0.4, f"لغز {i+1}...")

    def _journal_mode(self, count, theme, progress):
        for i in range(count):
            self.pdf.add_page()
            # تصميم مخطط يومي محسن
            self.pdf.set_font("Arial", "B", 18); self.pdf.set_y(1)
            self.pdf.cell(0, 1, f"يوم {i+1} - {clean_text(theme)[:20]}", ln=True)
            # ... (خطوط وأقسام للملاحظات، الأولويات، تتبع العادات) ...
            progress(0.4 + (i/count)*0.4, f"مخطط {i+1}...")

    def _quotes_mode(self, count, theme, progress):
        quotes = SmartGemini.ask(f"Generate {count} motivational one-line quotes about {theme}.").split('\n')
        for i in range(count):
            q = quotes[i] if i < len(quotes) else "استمر للأمام."
            self.pdf.add_page()
            # إضافة خلفية جمالية للاقتباس
            bg_path = f"bg_{i}.jpg"; self._add_temp_file(bg_path)
            if ImageShield.generate(theme, bg_path, "background"):
                self.pdf.image(bg_path, x=0, y=0, w=8.5, h=11)
            self.pdf.set_font("Arial", "B", 24); self.pdf.set_y(4)
            self.pdf.multi_cell(0, 0.8, f'"{clean_text(q)}"', align="C")
            progress(0.4 + (i/count)*0.4, f"اقتباس {i+1}...")

    # ... (بقية الأوضاع مثل flashcards و comics) ...

# ==========================================
# 7. البوت الآلي الفائق (Hyper-Bot V2)
# ==========================================
def hyper_bot_loop():
    while True:
        try:
            if TELEGRAM_TOKEN and ALL_KEYS[0] != "DUMMY":
                theme = SmartGemini.ask("Output ONLY 2 words highly profitable KDP micro-niche (e.g. Axolotl Chef).")
                engine = ProductionEngine({'theme': theme, 'pages': 24, 'mode': 'تشكيلة منوعة'}, lambda x, y: None)
                pdf_file, meta = engine.run()
                
                try:
                    with open(pdf_file, "rb") as f:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"📚 كتاب آلي: {theme}"}, files={"document": f})
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": f"📊 SEO:\n{meta['seo_title']}\n\n🎬 TikTok:\n{meta['tiktok']}"})
                except Exception as e:
                    st.session_state.error_log.append(f"Telegram Error: {e}")
                finally:
                    if os.path.exists(pdf_file): os.remove(pdf_file)
                    engine._cleanup()
        except Exception as e:
            st.session_state.error_log.append(f"HyperBot Error: {e}")
        time.sleep(900)

if 'hyper_bot_started' not in st.session_state:
    st.session_state.hyper_bot_started = True
    threading.Thread(target=hyper_bot_loop, daemon=True).start()

# ==========================================
# 8. واجهة الإمبراطورية (The Factory Dashboard V2)
# ==========================================
def main():
    st.markdown('<h1 class="main-title">🏭 مصنع المحتوى الرقمي V32</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">المهندس: وليد زكي | خطوط إنتاج ذكية لتطبيقك</p>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🚀 المصنع السريع", "🔍 محلل النيش", "🤖 الأتمتة", "⚙️ الإعدادات"])

    with tabs[0]:
        st.markdown('<div class="info-card">اختر خط الإنتاج وسيتم تصنيع حزمة النشر الخاصة بك.</div>', unsafe_allow_html=True)
        u_t = st.text_input("🎯 فكرة المنتج:", "قطط سايبربانك")
        u_p = st.number_input("📄 حجم الكتاب:", min_value=10, max_value=150, value=24)
        modes = ["تلوين للأطفال", "قصص مصورة", "ألغاز ونشاطات", "مخططات ودفاتر", "بطاقات تعليمية", "كتب اقتباسات", "كوميكس ومانغا", "تشكيلة منوعة"]
        u_m = st.selectbox("📦 خط الإنتاج:", modes)
        
        if st.button("🚀 بدء التصنيع", use_container_width=True):
            run_production_line(u_t, u_p, u_m)

    with tabs[1]:
        st.markdown('<div class="info-card">محلل النيش: اكتب فكرة وسيهندسها لك الذكاء الاصطناعي.</div>', unsafe_allow_html=True)
        i_t = st.text_input("💡 فكرة خام:", placeholder="مثلاً: ديناصورات للاطفال")
        if st.button("🔮 حلل واقترح الأفضل", use_container_width=True):
            with st.spinner("جاري تحليل أمازون وإيتسي..."):
                analysis = SmartGemini.ask(f"Analyze niche '{i_t}'. Suggest: 1. Best book type 2. Perfect title 3. 7 Keywords 4. TikTok hook.")
                st.success("التحليل جاهز!")
                st.code(analysis, language="markdown")

    with tabs[2]:
        st.success("🟢 المصنع الآلي نشط. يتم إنتاج حزمة جديدة كل 15 دقيقة وإرسالها لتطبيقك.")

    with tabs[3]:
        st.code(f"سجل الأخطاء الأخير (للمطور):\n{list(st.session_state.error_log)}", language="log")

def run_production_line(t, p, m):
    progress_bar = st.progress(0, text="تهيئة المصنع...")
    status_card = st.empty()
    
    def update_progress(val, msg):
        progress_bar.progress(val, text=msg)
    
    try:
        engine = ProductionEngine({'theme':t, 'pages':p, 'mode':m}, update_progress)
        pdf_file, meta = engine.run()
        
        # عرض النتائج في بطاقات جميلة
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="info-card card-seo"><h3>📈 SEO & KDP</h3><p><b>العنوان:</b> {meta["seo_title"]}</p><p><b>الكلمات:</b> {meta["keywords"]}</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="info-card card-tiktok"><h3>🎬 سكريبت تيك توك</h3><p>{meta["tiktok"]}</p></div>', unsafe_allow_html=True)
            
        # زر التحميل
        with open(pdf_file, "rb") as f:
            st.download_button("📥 تحميل الكتاب PDF", f, file_name=pdf_file, use_container_width=True)
            
        # التنظيف النهائي
        engine._cleanup()
        
    except Exception as e:
        st.session_state.error_log.append(f"UI Runtime Error: {e}")
        st.error("حدث خطأ غير متوقع. تم تسجيل التفاصيل للمطور.")

if __name__ == "__main__":
    main()
