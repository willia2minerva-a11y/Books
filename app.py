"""
KDP Factory Pro - Mobile-First & Telegram Optimized V32.3
Architect & CEO: Walid Zaki
✅ New: Open Prompt Mode (اكتب وصفاً حراً والنظام يفهم ويُنفذ)
✅ Live errors display with delete button
✅ Smart Hyper-Bot with status
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
from datetime import datetime
from collections import deque

# ==========================================
# 1. الجلسة الأساسية والتهيئة
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.errors = []  # قائمة الأخطاء المرئية
    st.session_state.hyper_bot_status = "⏳ جاري التشغيل..."
    st.session_state.hyper_bot_logs = deque(maxlen=10)
    time.sleep(0.3)

st.set_page_config(page_title="مصنع المحتوى V32.3", page_icon="🏭", layout="centered")

# ==========================================
# 2. التصميم البصري (Mobile-First UI)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    
    .stMarkdown, .stButton>button, .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, .stSelectbox>div>div>div, 
    .stNumberInput>div>div>input, p, h1, h2, h3, h4, h5, h6, label, li {
        direction: rtl; text-align: right;
    }
    
    .main-title {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 900;
        text-align: center;
        margin: 0;
        line-height: 1.3;
        padding: 10px 0;
    }
    
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 25px;
        font-weight: 600;
    }
    
    /* التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 12px 18px;
        font-weight: 700;
        font-size: 0.9rem;
        white-space: nowrap;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF416C, #FF4B2B);
        color: white !important;
        border-color: #FF416C;
    }
    
    /* البطاقات */
    .info-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border: 1px solid #eee;
    }
    
    .card-seo { border-right: 6px solid #0D6EFD; }
    .card-tiktok { border-right: 6px solid #FD0D6E; }
    .card-book { border-right: 6px solid #0DFD6E; }
    
    .card-header {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    /* الأزرار */
    input, textarea, .stButton>button {
        border-radius: 12px !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #FF416C, #FF4B2B);
        border: none;
        color: white;
        font-weight: 700;
        padding: 14px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 20px rgba(255,65,108,0.4);
    }
    
    .niche-btn>button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        font-size: 0.85rem;
        padding: 8px 12px;
        white-space: nowrap;
    }
    
    .delete-btn>button {
        background: linear-gradient(135deg, #dc3545, #c82333);
        font-size: 0.85rem;
        padding: 8px 16px;
    }
    
    /* عرض الأخطاء */
    .error-container {
        background: #fff5f5;
        border: 2px solid #dc3545;
        border-radius: 12px;
        padding: 15px;
        margin: 15px 0;
    }
    
    .error-item {
        background: #ffe0e0;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        font-family: monospace;
        font-size: 0.85rem;
        direction: ltr;
        text-align: left;
        word-break: break-all;
    }
    
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .status-active { background: #d4edda; color: #155724; }
    .status-error { background: #f8d7da; color: #721c24; }
    .status-waiting { background: #fff3cd; color: #856404; }
    
    /* شبكة البطاقات */
    .card-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    @media (min-width: 768px) {
        .card-grid {
            grid-template-columns: 1fr 1fr;
        }
    }
    
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        color: #999;
        font-size: 0.8rem;
    }
    
    /* تحسين textarea */
    .stTextArea textarea {
        min-height: 120px !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. إدارة المفاتيح والأمان
# ==========================================
def get_all_keys():
    """استخراج جميع مفاتيح Gemini من المتغيرات البيئية"""
    keys = []
    for i in range(1, 6):
        key = os.getenv(f"GEMINI_API_KEY_{i}", "")
        if key.strip():
            keys.append(key.strip())
    
    if not keys:
        default_key = os.getenv("GEMINI_API_KEY", "")
        if default_key.strip():
            keys.append(default_key.strip())
    
    return keys if keys else ["DUMMY"]

ALL_KEYS = get_all_keys()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def clean_text(text):
    """تنظيف النص للاستخدام في PDF"""
    if not text:
        return ""
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s.,!?؛،؟\-:()""\'\'\u0600-\u06FF]', ' ', text)
    return text.strip()

def add_error(error_msg, source="النظام"):
    """إضافة خطأ للسجل المرئي"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {source}: {str(error_msg)[:300]}"
    st.session_state.errors.append(full_msg)
    # الاحتفاظ بآخر 20 خطأ فقط
    if len(st.session_state.errors) > 20:
        st.session_state.errors = st.session_state.errors[-20:]

def clear_errors():
    """مسح جميع الأخطاء"""
    st.session_state.errors = []

# ==========================================
# 4. ذكاء الإمبراطورية (AI Engine)
# ==========================================
class SmartGemini:
    """محرك الذكاء الاصطناعي مع توزيع ذكي على المفاتيح"""
    
    @classmethod
    def ask(cls, prompt, fallback="", max_retries=2):
        if ALL_KEYS[0] == "DUMMY":
            add_error("لا توجد مفاتيح API. الرجاء إضافة GEMINI_API_KEY", "API")
            return fallback
        
        keys_pool = ALL_KEYS.copy()
        random.shuffle(keys_pool)
        
        for attempt in range(max_retries):
            for key in keys_pool:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel(
                        'gemini-1.5-flash',
                        generation_config={"temperature": 0.8, "top_p": 0.95}
                    )
                    res = model.generate_content(prompt)
                    
                    if res and res.text:
                        return res.text.strip()
                        
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str:
                        continue
                    elif "403" in error_str or "400" in error_str:
                        add_error(f"مفتاح غير صالح: {key[:15]}...", "API")
                        if key in ALL_KEYS:
                            ALL_KEYS.remove(key)
                        continue
                    else:
                        add_error(f"خطأ API: {error_str[:150]}", "Gemini")
                        continue
            
            if attempt < max_retries - 1:
                time.sleep(2)
        
        add_error("تم استنفاذ جميع المفاتيح", "Gemini")
        return fallback

    @classmethod
    def generate_niche(cls):
        """توليد نيش مربح عشوائي"""
        prompts = [
            "Output ONLY 2-3 words: highly profitable KDP micro-niche for kids. Be specific and creative. Example: 'Cyberpunk Dinosaurs' or 'Astronaut Chefs'",
            "Output ONLY 2-3 words: trending children book theme. Example: 'Gothic Unicorns' or 'Kawaii Robots'",
            "Output ONLY 2-3 words: unique coloring book niche. Example: 'Samurai Pandas' or 'Witch Kittens'",
        ]
        prompt = random.choice(prompts)
        result = cls.ask(prompt, "Fantasy Animals")
        result = result.strip().strip('"').strip("'")
        result = re.sub(r'[^a-zA-Z\s\-]', '', result)
        result = ' '.join(result.split()[:4])
        return result if len(result) > 3 else "Magical Creatures"

    @classmethod
    def parse_open_prompt(cls, user_prompt):
        """تحليل الموجه المفتوح لاستخراج: الموضوع، عدد الصفحات، نوع الكتاب"""
        analysis_prompt = f"""Analyze this user request for creating a book: "{user_prompt}"

Extract these details and respond in STRICT format:
---THEME---
[2-4 words main theme/topic]
---PAGES---
[suggested number of pages, between 10-100]
---MODE---
[best matching category from this list: تلوين للأطفال, قصص مصورة, ألغاز ونشاطات, مخططات ودفاتر, بطاقات تعليمية, كتب اقتباسات, كوميكس ومانغا, تعليم وتتبع, تشكيلة منوعة]
---ENHANCED_IDEA---
[a better, more creative version of the theme idea]"""

        result = cls.ask(analysis_prompt)
        
        # قيم افتراضية
        theme = "كتاب إبداعي"
        pages = 24
        mode = "تشكيلة منوعة"
        
        if result:
            theme_match = re.search(r'---THEME---\s*\n?(.*?)(?=---|$)', result, re.DOTALL)
            pages_match = re.search(r'---PAGES---\s*\n?(\d+)', result)
            mode_match = re.search(r'---MODE---\s*\n?(.*?)(?=---|$)', result, re.DOTALL)
            enhanced_match = re.search(r'---ENHANCED_IDEA---\s*\n?(.*?)(?=---|$)', result, re.DOTALL)
            
            if theme_match:
                theme = theme_match.group(1).strip()[:50]
            if pages_match:
                try:
                    pages = min(100, max(10, int(pages_match.group(1))))
                except:
                    pass
            if mode_match:
                extracted_mode = mode_match.group(1).strip()
                valid_modes = ["تلوين للأطفال", "قصص مصورة", "ألغاز ونشاطات", 
                             "مخططات ودفاتر", "بطاقات تعليمية", "كتب اقتباسات",
                             "كوميكس ومانغا", "تعليم وتتبع", "تشكيلة منوعة"]
                for vm in valid_modes:
                    if vm in extracted_mode:
                        mode = vm
                        break
            if enhanced_match:
                enhanced = enhanced_match.group(1).strip()
                if len(enhanced) > 3:
                    theme = enhanced[:50]
        
        return theme, pages, mode

# ==========================================
# 5. مصنع الصور (Image Generation)
# ==========================================
class ImageShield:
    """مولد الصور مع حماية من الفشل"""
    
    @staticmethod
    def _fetch_image(url, max_retries=3):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/124.0.0.0 Mobile Safari/537.36'
        }
        
        for attempt in range(max_retries):
            try:
                time.sleep(1.0 + random.uniform(0.2, 0.8))
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200 and len(response.content) > 15000:
                    return response.content
                elif response.status_code == 429:
                    time.sleep(3 * (attempt + 1))
                    continue
                else:
                    time.sleep(1)
                    
            except requests.exceptions.Timeout:
                time.sleep(2)
                continue
            except Exception as e:
                add_error(f"خطأ جلب الصورة: {str(e)[:100]}", "ImageShield")
                continue
                
        return None

    @staticmethod
    def generate(prompt, filename, style="coloring"):
        """توليد صورة واحدة"""
        style_prompts = {
            "cover": f"Professional children's book cover, {prompt}, vibrant, magical, NO TEXT NO LETTERS NO NUMBERS",
            "flashcard": f"Cute vector illustration of {prompt}, isolated on white, thick outlines, bright, educational",
            "background": f"Soft watercolor background, {prompt} theme, pastel colors, calming",
            "story": f"Children's book illustration, {prompt}, colorful, whimsical, storybook style",
            "coloring": f"Bold black white line art, {prompt}, thick outlines, pure white background, NO shading, coloring page"
        }
        
        full_prompt = style_prompts.get(style, style_prompts["coloring"])
        encoded_prompt = requests.utils.quote(full_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1, 99999)}"
        
        img_data = ImageShield._fetch_image(url)
        
        if img_data:
            try:
                with open(filename, "wb") as f:
                    f.write(img_data)
                return True
            except Exception as e:
                add_error(f"خطأ حفظ الصورة: {str(e)[:100]}", "ImageShield")
        
        return False

    @classmethod
    def generate_parallel(cls, tasks, max_workers=3):
        """توليد مجموعة صور بالتوازي"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {}
            
            for prompt, filename, style in tasks:
                time.sleep(random.uniform(0.1, 0.4))
                future = executor.submit(cls.generate, prompt, filename, style)
                future_to_file[future] = filename
            
            for future in concurrent.futures.as_completed(future_to_file):
                filename = future_to_file[future]
                try:
                    results[filename] = future.result()
                except Exception as e:
                    add_error(f"خطأ توليد متوازي: {str(e)[:100]}", "ImageShield")
                    results[filename] = False
        
        return results

# ==========================================
# 6. صانع الكتب الرقمية (PDF Factory)
# ==========================================
class KDPBook(FPDF):
    """قاعدة الكتب الرقمية"""
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(False)
        self.set_margins(0.875, 0.5, 0.75)

class ProductionEngine:
    """محرك الإنتاج الرئيسي"""
    
    def __init__(self, config, progress_callback=None):
        self.config = config
        self.progress = progress_callback or (lambda x, y: None)
        self.pdf = KDPBook()
        self.temp_files = []
        self.created_pages = 0
    
    def _add_temp_file(self, path):
        self.temp_files.append(path)
    
    def _cleanup(self):
        cleaned = 0
        for f in self.temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                    cleaned += 1
                except:
                    pass
        self.temp_files = []
        return cleaned
    
    def _emergency_page(self):
        """صفحة طوارئ عند فشل التوليد"""
        self.pdf.add_page()
        self.pdf.set_fill_color(255, 255, 200)
        self.pdf.rect(0.5, 1.5, 7.5, 8, 'F')
        self.pdf.set_font("Arial", "B", 24)
        self.pdf.set_y(3)
        self.pdf.cell(0, 1, "🌟 Creative Space 🌟", align="C", ln=True)
        self.pdf.set_font("Arial", "I", 16)
        self.pdf.set_y(5)
        self.pdf.cell(0, 1, "Use your imagination!", align="C")
        self.created_pages += 1
    
    def _add_copyright_page(self):
        """صفحة حقوق النشر"""
        self.pdf.add_page()
        self.pdf.set_font("Arial", "I", 10)
        self.pdf.set_y(9)
        year = datetime.now().year
        self.pdf.multi_cell(0, 0.4, 
            f"© {year} Walid Zaki. All Rights Reserved.\n"
            f"KDP Factory Pro V32.3",
            align="C")
        self.created_pages += 1

    def _add_belongs_to_page(self):
        """صفحة الملكية"""
        self.pdf.add_page()
        self.pdf.set_line_width(0.03)
        self.pdf.set_draw_color(100, 100, 200)
        self.pdf.rect(1, 1.5, 6.5, 8)
        self.pdf.set_font("Arial", "B", 28)
        self.pdf.set_y(3)
        self.pdf.cell(0, 1, "📖 هذا الكتاب يخص:", align="C", ln=True)
        self.pdf.set_line_width(0.01)
        self.pdf.set_draw_color(150)
        self.pdf.line(1.5, 4.5, 7.0, 4.5)
        self.pdf.set_font("Arial", "I", 14)
        self.pdf.set_y(5.5)
        self.pdf.cell(0, 0.5, "الاسم: _________________", align="C", ln=True)
        self.pdf.set_y(6.5)
        self.pdf.cell(0, 0.5, "التاريخ: _________________", align="C")
        self.created_pages += 1

    def run(self):
        """تشغيل خط الإنتاج الكامل"""
        theme = self.config.get('theme', 'Activity Book')
        pages = self.config.get('pages', 20)
        mode = self.config.get('mode', 'تلوين للأطفال')
        
        # المرحلة 1: الغلاف
        self.progress(0.05, "🎨 تصميم الغلاف...")
        cover_file = f"cover_{int(time.time())}_{random.randint(100,999)}.jpg"
        self._add_temp_file(cover_file)
        
        if ImageShield.generate(theme, cover_file, "cover"):
            self.pdf.add_page()
            try:
                self.pdf.image(cover_file, x=0, y=0, w=8.5, h=11)
            except:
                self._emergency_page()
        else:
            self.pdf.add_page()
            self.pdf.set_fill_color(30, 30, 80)
            self.pdf.rect(0, 0, 8.5, 11, 'F')
            self.pdf.set_text_color(255, 255, 255)
            self.pdf.set_font("Arial", "B", 32)
            self.pdf.set_y(4)
            self.pdf.cell(0, 1, clean_text(theme)[:40].upper(), align="C")
            self.pdf.set_text_color(0, 0, 0)
        
        self.created_pages += 1
        
        # حقوق النشر
        self._add_copyright_page()
        
        # صفحة الملكية
        self._add_belongs_to_page()
        
        # صفحة المحتوى
        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 24)
        self.pdf.set_y(1)
        self.pdf.cell(0, 1, "📋 المحتويات", align="C", ln=True)
        self.pdf.set_font("Arial", "", 14)
        self.pdf.set_y(2.5)
        self.pdf.multi_cell(0, 0.5, f"كتاب {clean_text(theme)}\n\n{mode}\n{self.created_pages + pages} صفحة", align="C")
        self.created_pages += 1
        
        # المرحلة 2: المحتوى الرئيسي
        self.progress(0.15, f"🏭 تشغيل خط إنتاج: {mode}")
        
        try:
            if mode == "تلوين للأطفال":
                self._coloring_mode(pages, theme)
            elif mode == "قصص مصورة":
                self._story_mode(pages, theme)
            elif mode == "ألغاز ونشاطات":
                self._puzzles_mode(pages, theme)
            elif mode == "مخططات ودفاتر":
                self._journal_mode(pages, theme)
            elif mode == "كتب اقتباسات":
                self._quotes_mode(pages, theme)
            elif mode == "بطاقات تعليمية":
                self._flashcards_mode(pages, theme)
            elif mode == "كوميكس ومانغا":
                self._comics_mode(pages, theme)
            elif mode == "تعليم وتتبع":
                self._alphabet_mode(pages)
            else:
                self._mixed_mode(pages, theme)
        except Exception as e:
            add_error(f"خطأ في {mode}: {str(e)[:200]}", "إنتاج")
            for _ in range(max(1, pages - self.created_pages)):
                self._emergency_page()
        
        # المرحلة 3: حفظ الملف
        self.progress(0.85, "💾 حفظ الكتاب...")
        clean_name = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF]', '_', theme)[:30]
        pdf_filename = f"KDP_{clean_name}_{int(time.time())}.pdf"
        
        try:
            self.pdf.output(pdf_filename)
            self._add_temp_file(pdf_filename)
        except Exception as e:
            add_error(f"خطأ حفظ PDF: {str(e)[:200]}", "إنتاج")
            pdf_filename = f"Book_{int(time.time())}.pdf"
            self.pdf.output(pdf_filename)
            self._add_temp_file(pdf_filename)
        
        # المرحلة 4: التسويق
        self.progress(0.90, "📊 هندسة التسويق...")
        marketing_data = self._generate_marketing(theme)
        
        self.progress(1.0, "✅ اكتمل الإنتاج!")
        return pdf_filename, marketing_data
    
    def _generate_marketing(self, theme):
        """توليد محتوى تسويقي"""
        clean_theme = clean_text(theme)
        
        prompt = f"""Act as KDP and TikTok expert. Launch package for: '{clean_theme}'

STRICT format:
---SEO_TITLE---
[Title + Subtitle]
---SEO_KEYWORDS---
[7 keywords, comma separated]
---AMAZON_DESCRIPTION---
[3-5 sentences description]
---TIKTOK_SCRIPT---
[30-second viral script]"""

        result = SmartGemini.ask(prompt)
        
        marketing = {
            "seo_title": clean_theme,
            "keywords": "kids, book, activity, fun, learning, creative, gift",
            "description": f"A wonderful book about {clean_theme}!",
            "tiktok": f"🎨 Check out this amazing {clean_theme} book! #KDP #KidsBooks"
        }
        
        if result:
            for section, key in [("SEO_TITLE", "seo_title"), ("SEO_KEYWORDS", "keywords"), 
                                ("AMAZON_DESCRIPTION", "description"), ("TIKTOK_SCRIPT", "tiktok")]:
                match = re.search(f'---{section}---\s*\n?(.*?)(?=---|$)', result, re.DOTALL | re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if value and len(value) > 5:
                        marketing[key] = value
        
        return marketing
    
    # ========== خطوط الإنتاج ==========
    
    def _coloring_mode(self, count, theme):
        """خط إنتاج التلوين"""
        prompt = f"List exactly {count+5} simple, cute items related to '{theme}' for coloring. One per line."
        ideas_text = SmartGemini.ask(prompt, "\n".join([f"Item {i}" for i in range(count+5)]))
        
        ideas = []
        for line in ideas_text.split('\n'):
            line = line.strip().strip('1234567890.- ')
            if len(line) > 2:
                ideas.append(line)
        
        ideas = ideas[:max(count, 10)]
        
        tasks = []
        for i, idea in enumerate(ideas):
            clean_idea = clean_text(idea)
            if clean_idea:
                fname = f"col_{i}_{random.randint(100,999)}.jpg"
                self._add_temp_file(fname)
                tasks.append((clean_idea, fname, "coloring"))
        
        if tasks:
            results = ImageShield.generate_parallel(tasks[:count])
            
            for i, (idea, fname, _) in enumerate(tasks[:count]):
                self.progress(0.15 + (i/len(tasks[:count]))*0.55, f"🎨 تلوين {i+1}/{len(tasks[:count])}")
                
                self.pdf.add_page()
                self.pdf.set_font("Arial", "B", 16)
                self.pdf.set_y(0.5)
                self.pdf.cell(0, 0.5, f"🎨 تلوين: {idea[:30]}", align="C", ln=True)
                self.pdf.set_line_width(0.02)
                self.pdf.set_draw_color(200)
                self.pdf.rect(1, 1.5, 6.5, 7.5)
                
                if results.get(fname, False):
                    try:
                        self.pdf.image(fname, x=1.2, y=1.7, w=6.1, h=7.1)
                    except:
                        self._emergency_page()
                else:
                    self.pdf.set_font("Arial", "B", 24)
                    self.pdf.set_y(4)
                    self.pdf.cell(0, 1, f"ارسم: {idea[:20]}!", align="C")
                
                self.created_pages += 1
                
                if i < len(tasks[:count]) - 1:
                    self.pdf.add_page()
                    self.created_pages += 1
    
    def _story_mode(self, count, theme):
        """خط إنتاج القصص المصورة"""
        clean_theme = clean_text(theme)
        prompt = f"Write a children's story about '{clean_theme}' with {min(count, 8)} parts. Separate with '||'."
        
        story_text = SmartGemini.ask(prompt, "Part 1||Part 2||Part 3")
        parts = [p.strip() for p in story_text.split('||') if p.strip()][:count]
        
        tasks = []
        for i, part in enumerate(parts):
            first_sentence = part.split('.')[0][:80]
            fname = f"story_{i}_{random.randint(100,999)}.jpg"
            self._add_temp_file(fname)
            tasks.append((first_sentence, fname, "story"))
        
        results = ImageShield.generate_parallel(tasks) if tasks else {}
        
        for i, part in enumerate(parts):
            self.progress(0.15 + (i/len(parts))*0.55, f"📖 قصة {i+1}/{len(parts)}")
            
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 14)
            self.pdf.set_y(1)
            self.pdf.multi_cell(0, 0.4, f"الجزء {i+1}", align="C")
            self.pdf.set_font("Arial", "", 14)
            self.pdf.set_y(2)
            self.pdf.multi_cell(0, 0.5, clean_text(part), align="C")
            self.created_pages += 1
            
            self.pdf.add_page()
            fname = tasks[i][1] if i < len(tasks) else None
            if fname and results.get(fname, False):
                try:
                    self.pdf.image(fname, x=1, y=2, w=6.5, h=6.5)
                except:
                    self._emergency_page()
            else:
                self.pdf.set_font("Arial", "B", 20)
                self.pdf.set_y(4)
                self.pdf.cell(0, 1, "🎨 مساحة للرسم", align="C")
            
            self.created_pages += 1
    
    def _puzzles_mode(self, count, theme):
        """خط إنتاج الألغاز"""
        clean_theme = clean_text(theme)
        puzzles_per_type = max(2, count // 3)
        puzzle_count = 0
        
        # سودوكو
        for i in range(puzzles_per_type):
            if puzzle_count >= count:
                break
            
            self.progress(0.15 + (puzzle_count/count)*0.55, f"🧩 سودوكو {i+1}")
            board, solution = self._generate_sudoku()
            
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.8, f"🧩 Sudoku #{i+1}", align="C")
            self._draw_sudoku_grid(board)
            self.created_pages += 1
            puzzle_count += 1
            
            # صفحة الحل
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.8, f"✅ الحل #{i+1}", align="C")
            self._draw_sudoku_grid(solution, is_solution=True)
            self.created_pages += 1
        
        # متاهات
        for i in range(puzzles_per_type):
            if puzzle_count >= count:
                break
            
            self.progress(0.15 + (puzzle_count/count)*0.55, f"🌀 متاهة {i+1}")
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.8, f"🌀 Maze #{i+1}", align="C")
            self._draw_maze()
            self.created_pages += 1
            puzzle_count += 1
        
        # البحث عن الكلمات
        words_prompt = f"List 6 simple words related to '{clean_theme}' for word search. One per line."
        words_text = SmartGemini.ask(words_prompt, "FUN\nGAME\nPLAY\nHAPPY\nSMILE\nJOY")
        words = [w.strip().upper()[:8] for w in words_text.split('\n') if w.strip()][:6]
        
        for i in range(puzzles_per_type):
            if puzzle_count >= count:
                break
            
            self.progress(0.15 + (puzzle_count/count)*0.55, f"🔤 بحث كلمات {i+1}")
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.8, f"🔤 Word Search #{i+1}", align="C")
            self.pdf.set_font("Arial", "", 12)
            self.pdf.set_y(1.8)
            self.pdf.cell(0, 0.5, "الكلمات: " + ", ".join(words), align="C")
            self._draw_word_search(words)
            self.created_pages += 1
            puzzle_count += 1
    
    def _generate_sudoku(self):
        """توليد سودوكو مع الحل"""
        base = 3
        side = base * base
        
        def pattern(r, c):
            return (base * (r % base) + r // base + c) % side
        
        r_base = range(base)
        rows = [g * base + r for g in random.sample(r_base, base) for r in random.sample(r_base, base)]
        cols = [g * base + c for g in random.sample(r_base, base) for c in random.sample(r_base, base)]
        nums = random.sample(range(1, side + 1), side)
        
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        solution = [row[:] for row in board]
        
        empties = (side * side) * 2 // 3
        for p in random.sample(range(side * side), empties):
            board[p // side][p % side] = 0
        
        return board, solution
    
    def _draw_sudoku_grid(self, board, is_solution=False):
        side = len(board)
        cell_size = 0.6
        start_x = (8.5 - (cell_size * side)) / 2
        start_y = 2.0
        
        self.pdf.set_line_width(0.01)
        self.pdf.set_draw_color(100)
        
        for i in range(side + 1):
            line_width = 0.03 if i % 3 == 0 else 0.01
            self.pdf.set_line_width(line_width)
            self.pdf.line(start_x, start_y + i * cell_size, start_x + side * cell_size, start_y + i * cell_size)
            self.pdf.line(start_x + i * cell_size, start_y, start_x + i * cell_size, start_y + side * cell_size)
        
        self.pdf.set_font("Arial", "B", 16)
        for r in range(side):
            for c in range(side):
                val = board[r][c]
                if val != 0:
                    x = start_x + c * cell_size + cell_size / 3
                    y = start_y + r * cell_size + cell_size / 1.4
                    self.pdf.set_text_color(0, 150, 0) if is_solution else self.pdf.set_text_color(0)
                    self.pdf.text(x, y, str(val))
        
        self.pdf.set_text_color(0)
    
    def _draw_maze(self, width=10, height=10):
        grid = [[{'N': True, 'S': True, 'E': True, 'W': True, 'visited': False} for _ in range(width)] for _ in range(height)]
        stack = [(0, 0)]
        grid[0][0]['visited'] = True
        
        while stack:
            cx, cy = stack[-1]
            directions = [('N', 0, -1, 'S'), ('S', 0, 1, 'N'), ('E', 1, 0, 'W'), ('W', -1, 0, 'E')]
            random.shuffle(directions)
            moved = False
            
            for d, dx, dy, opp in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height and not grid[ny][nx]['visited']:
                    grid[cy][cx][d] = False
                    grid[ny][nx][opp] = False
                    grid[ny][nx]['visited'] = True
                    stack.append((nx, ny))
                    moved = True
                    break
            
            if not moved:
                stack.pop()
        
        grid[0][0]['W'] = False
        grid[height-1][width-1]['E'] = False
        
        cell_size = min(0.5, 5/width)
        start_x = (8.5 - (width * cell_size)) / 2
        start_y = 2.5
        
        self.pdf.set_line_width(0.03)
        self.pdf.set_draw_color(0)
        
        for y in range(height):
            for x in range(width):
                sx = start_x + x * cell_size
                sy = start_y + y * cell_size
                if grid[y][x]['N']: self.pdf.line(sx, sy, sx + cell_size, sy)
                if grid[y][x]['S']: self.pdf.line(sx, sy + cell_size, sx + cell_size, sy + cell_size)
                if grid[y][x]['W']: self.pdf.line(sx, sy, sx, sy + cell_size)
                if grid[y][x]['E']: self.pdf.line(sx + cell_size, sy, sx + cell_size, sy + cell_size)
        
        self.pdf.set_font("Arial", "B", 10)
        self.pdf.set_text_color(0, 150, 0)
        self.pdf.text(start_x - 0.3, start_y + 0.2, "S")
        self.pdf.set_text_color(255, 0, 0)
        self.pdf.text(start_x + width * cell_size - 0.1, start_y + height * cell_size - 0.3, "E")
        self.pdf.set_text_color(0)
    
    def _draw_word_search(self, words, size=10):
        grid = [[' ' for _ in range(size)] for _ in range(size)]
        
        for word in words:
            word = word.upper().replace(' ', '')
            placed = False
            for _ in range(50):
                dr, dc = random.choice([(0, 1), (1, 0), (1, 1), (-1, 1)])
                r = random.randint(0, size-1)
                c = random.randint(0, size-1)
                end_r = r + dr * (len(word)-1)
                end_c = c + dc * (len(word)-1)
                
                if 0 <= end_r < size and 0 <= end_c < size:
                    can_place = True
                    for i, ch in enumerate(word):
                        cr, cc = r + dr*i, c + dc*i
                        if grid[cr][cc] not in (' ', ch):
                            can_place = False
                            break
                    if can_place:
                        for i, ch in enumerate(word):
                            grid[r + dr*i][c + dc*i] = ch
                        placed = True
                        break
        
        for r in range(size):
            for c in range(size):
                if grid[r][c] == ' ':
                    grid[r][c] = random.choice(string.ascii_uppercase)
        
        cell_size = min(0.55, 5/size)
        start_x = (8.5 - (size * cell_size)) / 2
        start_y = 3.0
        
        self.pdf.set_line_width(0.01)
        self.pdf.set_draw_color(150)
        
        for i in range(size + 1):
            self.pdf.line(start_x, start_y + i*cell_size, start_x + size*cell_size, start_y + i*cell_size)
            self.pdf.line(start_x + i*cell_size, start_y, start_x + i*cell_size, start_y + size*cell_size)
        
        self.pdf.set_font("Arial", "B", max(8, int(cell_size*14)))
        for r in range(size):
            for c in range(size):
                x = start_x + c*cell_size + cell_size/3.5
                y = start_y + r*cell_size + cell_size/1.5
                self.pdf.text(x, y, grid[r][c])
    
    def _journal_mode(self, count, theme):
        clean_theme = clean_text(theme)
        for i in range(count):
            self.progress(0.15 + (i/count)*0.55, f"📋 مخطط {i+1}/{count}")
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 18)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.6, f"📅 يوم {i+1}: {clean_theme[:25]}", align="C", ln=True)
            self.pdf.set_font("Arial", "B", 12)
            self.pdf.set_y(2)
            self.pdf.cell(0, 0.5, "🎯 أهم 3 أولويات:", ln=True)
            self.pdf.set_line_width(0.01)
            self.pdf.set_draw_color(200)
            for j in range(3):
                y = 2.8 + j*0.8
                self.pdf.line(1.5, y, 7, y)
                self.pdf.set_font("Arial", "I", 10)
                self.pdf.text(1.5, y-0.15, f"{j+1}.")
            self.pdf.set_font("Arial", "B", 12)
            self.pdf.set_y(5.5)
            self.pdf.cell(0, 0.5, "📝 ملاحظات:", ln=True)
            for j in range(5):
                self.pdf.line(1.5, 6 + j*0.6, 7, 6 + j*0.6)
            self.pdf.set_font("Arial", "B", 12)
            self.pdf.set_y(9)
            self.pdf.cell(0, 0.5, "✅ عادات:", ln=True)
            habits = ["قراءة", "رياضة", "ماء", "تأمل", "تدوين"]
            for j, habit in enumerate(habits):
                self.pdf.set_font("Arial", "", 10)
                self.pdf.text(1.5, 9.5 + j*0.35, f"☐ {habit}")
            self.created_pages += 1
    
    def _quotes_mode(self, count, theme):
        clean_theme = clean_text(theme)
        prompt = f"Generate {count} unique inspiring quotes about '{clean_theme}'. One per line."
        quotes_text = SmartGemini.ask(prompt, "Believe.\nStay strong.\nKeep going.")
        quotes = [q.strip().strip('"') for q in quotes_text.split('\n') if len(q.strip()) > 5][:count]
        
        for i, quote in enumerate(quotes):
            self.progress(0.15 + (i/len(quotes))*0.55, f"💭 اقتباس {i+1}/{len(quotes)}")
            self.pdf.add_page()
            bg_color = random.choice([(255,245,238), (240,248,255), (255,250,240)])
            self.pdf.set_fill_color(*bg_color)
            self.pdf.rect(0.5, 1, 7.5, 9, 'F')
            self.pdf.set_line_width(0.04)
            self.pdf.set_draw_color(100, 100, 150)
            self.pdf.rect(0.75, 1.25, 7, 8.5)
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(3.5)
            self.pdf.multi_cell(0, 0.6, f'"{clean_text(quote)}"', align="C")
            self.pdf.set_font("Arial", "I", 10)
            self.pdf.set_y(10)
            self.pdf.cell(0, 0.4, f"{i+1}/{len(quotes)}", align="C")
            self.created_pages += 1
    
    def _flashcards_mode(self, count, theme):
        clean_theme = clean_text(theme)
        prompt = f"List {count} simple educational words related to '{clean_theme}'. One per line."
        words_text = SmartGemini.ask(prompt, "Sun\nMoon\nStar\nTree")
        words = [w.strip() for w in words_text.split('\n') if len(w.strip()) > 1][:count]
        
        tasks = []
        for i, word in enumerate(words):
            fname = f"flash_{i}_{random.randint(100,999)}.jpg"
            self._add_temp_file(fname)
            tasks.append((word, fname, "flashcard"))
        
        results = ImageShield.generate_parallel(tasks) if tasks else {}
        
        for i, (word, fname, _) in enumerate(tasks[:count]):
            self.progress(0.15 + (i/len(tasks[:count]))*0.55, f"🃏 بطاقة {i+1}/{len(tasks[:count])}")
            self.pdf.add_page()
            self.pdf.set_line_width(0.05)
            self.pdf.set_draw_color(50, 50, 150)
            self.pdf.rect(1.25, 1.5, 6, 7)
            if results.get(fname, False):
                try:
                    self.pdf.image(fname, x=1.5, y=2, w=5.5, h=5.5)
                except:
                    pass
            self.pdf.set_font("Arial", "B", 32)
            self.pdf.set_y(8.5)
            self.pdf.cell(0, 0.8, word.upper(), align="C")
            self.created_pages += 1
    
    def _comics_mode(self, count, theme):
        clean_theme = clean_text(theme)
        for i in range(count):
            self.progress(0.15 + (i/count)*0.55, f"💬 كوميكس {i+1}/{count}")
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.5)
            self.pdf.cell(0, 0.6, f"💬 {clean_theme[:20]} #{i+1}", align="C")
            self.pdf.set_line_width(0.03)
            self.pdf.rect(0.75, 1.5, 3.4, 3.5)
            self.pdf.rect(4.35, 1.5, 3.4, 3.5)
            self.pdf.rect(0.75, 5.3, 3.4, 3.5)
            self.pdf.rect(4.35, 5.3, 3.4, 3.5)
            self.pdf.set_font("Arial", "I", 12)
            self.pdf.set_y(9.2)
            self.pdf.cell(0, 0.4, "اكتب قصتك هنا...", align="C")
            self.created_pages += 1
    
    def _alphabet_mode(self, count):
        letters = list(string.ascii_uppercase)[:min(count, 26)]
        for i, char in enumerate(letters):
            self.progress(0.15 + (i/len(letters))*0.55, f"🔤 حرف {char}")
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 120)
            self.pdf.set_y(1.5)
            self.pdf.cell(0, 2, char, align="C", ln=True)
            self.pdf.set_font("Arial", "B", 60)
            self.pdf.set_y(3.5)
            self.pdf.cell(0, 1, char.lower(), align="C", ln=True)
            self.pdf.set_font("Arial", "", 20)
            self.pdf.set_y(5)
            self.pdf.cell(0, 0.5, "✏️ تتبع الحرف:", align="C", ln=True)
            self.pdf.set_text_color(200)
            for j in range(3):
                self.pdf.set_font("Arial", "", 40)
                self.pdf.set_y(6 + j)
                self.pdf.cell(0, 1, f"{char}  {char.lower()}  {char}  {char.lower()}", align="C")
            self.pdf.set_text_color(0)
            self.created_pages += 1
    
    def _mixed_mode(self, count, theme):
        quarter = max(2, count // 4)
        remaining = count
        modes = [self._coloring_mode, self._puzzles_mode, self._journal_mode, self._quotes_mode]
        
        for func in modes:
            if remaining <= 0:
                break
            pages_for_mode = min(quarter, remaining)
            try:
                func(pages_for_mode, theme)
                remaining -= pages_for_mode
            except Exception as e:
                add_error(f"خطأ في الوضع المختلط: {str(e)[:200]}", "إنتاج")
                for _ in range(pages_for_mode):
                    self._emergency_page()
                remaining -= pages_for_mode

# ==========================================
# 7. البوت الآلي (Hyper-Bot)
# ==========================================
def send_to_telegram(pdf_file, marketing_data, theme):
    """إرسال المحتوى إلى تيليجرام"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False, "❌ لم يتم تكوين تيليجرام"
    
    results = []
    
    # إرسال الكتاب
    try:
        with open(pdf_file, "rb") as f:
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"📚 كتاب: {theme}\n🏭 KDP Factory V32.3"},
                files={"document": f},
                timeout=30
            )
        if response.status_code == 200:
            results.append("✅ تم إرسال الكتاب")
        else:
            results.append(f"❌ فشل الكتاب: {response.status_code}")
    except Exception as e:
        results.append(f"❌ خطأ الكتاب: {str(e)[:80]}")
    
    # إرسال التسويق
    try:
        seo_text = f"""📊 تفاصيل: {theme}

🏷️ {marketing_data.get('seo_title', '')}
🔑 {marketing_data.get('keywords', '')}
📝 {marketing_data.get('description', '')}

🎬 تيك توك:
{marketing_data.get('tiktok', '')}"""
        
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": seo_text[:4000]},
            timeout=20
        )
        if response.status_code == 200:
            results.append("✅ تم إرسال التسويق")
        else:
            results.append(f"❌ فشل التسويق: {response.status_code}")
    except Exception as e:
        results.append(f"❌ خطأ التسويق: {str(e)[:80]}")
    
    return True, " | ".join(results)

def hyper_bot_loop():
    """حلقة البوت الآلي"""
    st.session_state.hyper_bot_status = "🟢 يعمل"
    
    while True:
        try:
            has_keys = ALL_KEYS[0] != "DUMMY"
            has_telegram = bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)
            
            if not has_keys:
                st.session_state.hyper_bot_status = "⚠️ لا توجد مفاتيح API"
                st.session_state.hyper_bot_logs.append("⚠️ لا توجد مفاتيح")
                time.sleep(900)
                continue
            
            if not has_telegram:
                st.session_state.hyper_bot_status = "⚠️ تيليجرام غير مكون"
                st.session_state.hyper_bot_logs.append("⚠️ تيليجرام غير مكون")
                time.sleep(900)
                continue
            
            # توليد فكرة
            theme = SmartGemini.generate_niche()
            st.session_state.hyper_bot_status = f"🟢 يعمل - آخر إنتاج: {theme}"
            st.session_state.hyper_bot_logs.append(f"🎯 {theme}")
            
            # إنتاج الكتاب
            engine = ProductionEngine({'theme': theme, 'pages': 24, 'mode': 'تشكيلة منوعة'})
            pdf_file, marketing = engine.run()
            
            # إرسال
            success, msg = send_to_telegram(pdf_file, marketing, theme)
            st.session_state.hyper_bot_logs.append(msg)
            
            # تنظيف
            engine._cleanup()
            
        except Exception as e:
            error_msg = f"❌ خطأ: {str(e)[:150]}"
            st.session_state.hyper_bot_status = f"🔴 خطأ"
            st.session_state.hyper_bot_logs.append(error_msg)
            add_error(error_msg, "HyperBot")
            
            # إرسال الخطأ للتليجرام
            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                try:
                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                        data={"chat_id": TELEGRAM_CHAT_ID, "text": f"⚠️ HyperBot خطأ:\n{error_msg}"},
                        timeout=10
                    )
                except:
                    pass
        
        time.sleep(900)

# بدء البوت
if 'hyper_bot_started' not in st.session_state:
    st.session_state.hyper_bot_started = True
    threading.Thread(target=hyper_bot_loop, daemon=True).start()

# ==========================================
# 8. واجهة المستخدم (Dashboard)
# ==========================================
def main():
    # العنوان الرئيسي
    st.markdown('<h1 class="main-title">🏭 مصنع المحتوى الرقمي V32.3</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">المهندس: وليد زكي | Open Prompt + Smart Factory</p>', unsafe_allow_html=True)
    
    # عرض الأخطاء إن وجدت
    if st.session_state.errors:
        st.markdown('<div class="error-container">', unsafe_allow_html=True)
        st.markdown("### ⚠️ الأخطاء المسجلة:")
        for err in st.session_state.errors[-5:]:  # آخر 5 أخطاء
            st.markdown(f'<div class="error-item">❌ {err}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"عدد الأخطاء: {len(st.session_state.errors)}")
        with col2:
            st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
            if st.button("🗑️ مسح الأخطاء", use_container_width=True):
                clear_errors()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # التبويبات
    tabs = st.tabs(["📝 الموجه المفتوح", "🚀 المصنع السريع", "🔍 محلل النيش", "🤖 الأتمتة"])
    
    # ========== تبويب الموجه المفتوح (الجديد) ==========
    with tabs[0]:
        st.markdown("""
        <div class="info-card">
            <h3>📝 طور الموجه المفتوح</h3>
            <p>اكتب وصفاً حراً للكتاب الذي تريده، والنظام سيفهم طلبك وينفذه تلقائياً.</p>
            <p style="color: #666; font-size: 0.9rem;">مثال: <em>"اصنع لي كتاب تلوين للأطفال عن الديناصورات في الفضاء مع 30 صفحة"</em></p>
            <p style="color: #666; font-size: 0.9rem;">مثال: <em>"أريد كتاب قصص مصورة عن قطط نينجا للأطفال"</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        open_prompt = st.text_area(
            "✍️ اكتب وصف الكتاب الذي تريده:",
            placeholder="اكتب هنا... مثلاً: اصنع لي كتاب ألغاز ونشاطات عن المغامرات البحرية للاطفال مع 40 صفحة",
            height=120,
            key="open_prompt"
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🚀 نفذ الطلب", use_container_width=True, key="execute_prompt"):
                if not open_prompt or len(open_prompt.strip()) < 5:
                    st.error("⚠️ الرجاء كتابة وصف أطول للكتاب (5 أحرف على الأقل)")
                else:
                    with st.spinner("🧠 جاري فهم طلبك وتحليله..."):
                        theme, pages, mode = SmartGemini.parse_open_prompt(open_prompt)
                        
                        st.success(f"✅ فهمت طلبك!")
                        st.markdown(f"""
                        <div class="info-card">
                            <p>📌 <strong>الموضوع:</strong> {theme}</p>
                            <p>📄 <strong>عدد الصفحات:</strong> {pages}</p>
                            <p>📦 <strong>نوع الكتاب:</strong> {mode}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        run_production_line(theme, pages, mode)
        
        with col2:
            if st.button("✨ اقترح فكرة", use_container_width=True, key="suggest_idea"):
                new_niche = SmartGemini.generate_niche()
                mode_suggestions = ["تلوين للأطفال", "قصص مصورة", "ألغاز ونشاطات", "مخططات ودفاتر"]
                suggested_mode = random.choice(mode_suggestions)
                st.session_state.open_prompt = f"اصنع لي كتاب {suggested_mode} عن {new_niche} مع 24 صفحة"
                st.rerun()
    
    # ========== تبويب المصنع السريع ==========
    with tabs[1]:
        st.markdown('<div class="info-card">⚡ اختر خط الإنتاج مباشرة وسيتم التصنيع.</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_theme = st.text_input(
                "🎯 فكرة النيش:",
                placeholder="مثال: ديناصورات فضائية، أميرات نينجا...",
                key="theme_input"
            )
        
        with col2:
            st.markdown('<div class="niche-btn">', unsafe_allow_html=True)
            if st.button("✨ توليد", key="gen_niche", use_container_width=True):
                new_niche = SmartGemini.generate_niche()
                st.session_state.theme_input = new_niche
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        user_pages = st.number_input("📄 عدد الصفحات:", min_value=10, max_value=150, value=24, step=2)
        
        modes = [
            "تلوين للأطفال", "قصص مصورة", "ألغاز ونشاطات",
            "مخططات ودفاتر", "بطاقات تعليمية", "كتب اقتباسات",
            "كوميكس ومانغا", "تعليم وتتبع", "تشكيلة منوعة"
        ]
        user_mode = st.selectbox("📦 خط الإنتاج:", modes)
        
        if st.button("🚀 ابدأ التصنيع", use_container_width=True, key="start_production"):
            if not user_theme or len(user_theme.strip()) < 2:
                st.error("⚠️ الرجاء إدخال فكرة النيش")
            else:
                run_production_line(user_theme.strip(), user_pages, user_mode)
    
    # ========== تبويب محلل النيش ==========
    with tabs[2]:
        st.markdown('<div class="info-card">🔮 أدخل فكرة خام وسيتم تحليلها واقتراح أفضل استراتيجية.</div>', unsafe_allow_html=True)
        
        idea_input = st.text_input(
            "💡 فكرة خام:",
            placeholder="مثال: قطط للأطفال، يوميات دراسية، وصفات كيتو...",
            key="idea_input"
        )
        
        if st.button("🔍 حلل النيش", use_container_width=True, key="analyze_niche"):
            if not idea_input or len(idea_input.strip()) < 2:
                st.error("⚠️ الرجاء إدخال فكرة للتحليل")
            else:
                with st.spinner("🕵️ جاري تحليل السوق والمنافسة..."):
                    analysis = SmartGemini.ask(f"""
حلل النيش '{idea_input}' بالعربية:
1. تقييم السوق والمنافسة
2. أفضل نوع كتاب مقترح
3. عنوان جذاب
4. 7 كلمات مفتاحية
5. توقعات النجاح
6. خطاف تيك توك""")
                    
                    st.success("✅ اكتمل التحليل!")
                    st.markdown(f'<div class="info-card card-seo">{analysis}</div>', unsafe_allow_html=True)
    
    # ========== تبويب الأتمتة ==========
    with tabs[3]:
        st.markdown('<div class="info-card">🤖 حالة المصنع الآلي ومركز التحكم.</div>', unsafe_allow_html=True)
        
        # حالة البوت
        status = st.session_state.get('hyper_bot_status', '⏳...')
        status_class = "status-active" if "يعمل" in status else ("status-error" if "خطأ" in status else "status-waiting")
        st.markdown(f'<span class="status-badge {status_class}">{status}</span>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("بوت", "🟢 نشط" if hasattr(st.session_state, 'hyper_bot_started') else "🔴 متوقف")
        with col2:
            st.metric("تيليجرام", "✅ متصل" if (TELEGRAM_TOKEN and TELEGRAM_CHAT_ID) else "❌ غير مكون")
        with col3:
            st.metric("مفاتيح", f"{len(ALL_KEYS)} مفتاح" if ALL_KEYS[0] != "DUMMY" else "❌ لا يوجد")
        
        # سجل البوت
        if st.session_state.hyper_bot_logs:
            st.markdown("#### 📜 آخر نشاط:")
            for log in list(st.session_state.hyper_bot_logs)[-5:]:
                st.text(log)

def run_production_line(theme, pages, mode):
    """تشغيل خط الإنتاج وعرض النتائج"""
    progress_bar = st.progress(0, "🚀 تهيئة المصنع...")
    status_area = st.empty()
    
    def update_progress(val, msg):
        progress_bar.progress(val, text=msg)
        status_area.info(msg)
    
    engine = ProductionEngine(
        {'theme': theme, 'pages': pages, 'mode': mode},
        progress_callback=update_progress
    )
    
    try:
        pdf_file, marketing = engine.run()
        
        progress_bar.progress(1.0, "✅ اكتمل الإنتاج!")
        status_area.success("🎉 تم تصنيع الكتاب بنجاح!")
        
        # عرض البطاقات
        st.markdown('<div class="card-grid">', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="info-card card-seo">
            <div class="card-header">📈 معلومات النشر</div>
            <p><strong>🏷️ العنوان:</strong> {marketing.get("seo_title", theme)}</p>
            <p><strong>🔑 الكلمات:</strong> {marketing.get("keywords", "")}</p>
            <p><strong>📝 الوصف:</strong> {marketing.get("description", "")}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="info-card card-tiktok">
            <div class="card-header">🎬 سكريبت تيك توك</div>
            <p>{marketing.get("tiktok", "")}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # أزرار التحميل والإرسال
        col1, col2 = st.columns(2)
        
        with col1:
            with open(pdf_file, "rb") as f:
                pdf_bytes = f.read()
            st.download_button("📥 تحميل الكتاب PDF", data=pdf_bytes, file_name=pdf_file, mime="application/pdf", use_container_width=True)
        
        with col2:
            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                if st.button("📤 أرسل للتليجرام", use_container_width=True):
                    with st.spinner("جاري الإرسال..."):
                        success, msg = send_to_telegram(pdf_file, marketing, theme)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
            else:
                st.info("⚙️ قم بتكوين تيليجرام للإرسال")
        
        engine._cleanup()
        
        # عرض الأخطاء إن وجدت
        if st.session_state.errors:
            with st.expander("⚠️ عرض سجل الأخطاء"):
                for err in st.session_state.errors[-3:]:
                    st.text(err)
        
    except Exception as e:
        add_error(f"UI Error: {str(e)[:300]}", "الواجهة")
        st.error("❌ حدث خطأ غير متوقع")
        with st.expander("🔍 تفاصيل الخطأ"):
            st.code(traceback.format_exc())
        
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    data={"chat_id": TELEGRAM_CHAT_ID, "text": f"⚠️ خطأ:\n{str(e)[:500]}"},
                    timeout=10
                )
            except:
                pass
        
        try:
            engine._cleanup()
        except:
            pass

# ==========================================
# 9. التذييل
# ==========================================
st.markdown("""
<div class="footer">
    <p>🏭 KDP Factory Pro V32.3 | © 2024 Walid Zaki</p>
    <p>مصنع محتوى رقمي | طور موجه مفتوح | إنتاج ذكي</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()