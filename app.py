"""
KDP Factory Pro - Mobile-First & Telegram Optimized V32.1
Architect & CEO: Walid Zaki | Logic: Content Factories, Reverse SEO, Visual Cards
Fixes: Error Display, Niche Generator, Complete Puzzle Modes, Telegram Debugging
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
from collections import deque

# ==========================================
# 1. الجلسة الأساسية و التهيئة
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.error_log = deque(maxlen=20)
    st.session_state.hyper_bot_log = deque(maxlen=10)
    time.sleep(0.3)

st.set_page_config(page_title="مصنع المحتوى V32.1", page_icon="🏭", layout="centered")

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
    
    .info-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border: 1px solid #eee;
        transition: transform 0.2s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .card-seo { border-right: 6px solid #0D6EFD; }
    .card-tiktok { border-right: 6px solid #FD0D6E; }
    .card-book { border-right: 6px solid #0DFD6E; }
    .card-error { border-right: 6px solid #DC3545; background: #FFF5F5; }
    
    .card-header {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
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
    
    .niche-btn>button:hover {
        box-shadow: 0 5px 15px rgba(102,126,234,0.4);
    }
    
    .error-box {
        background: #FFF5F5;
        border: 2px solid #DC3545;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        direction: ltr;
        text-align: left;
        font-family: monospace;
        font-size: 0.85rem;
        max-height: 300px;
        overflow-y: auto;
    }
    
    .success-badge {
        display: inline-block;
        background: #d4edda;
        color: #155724;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        color: #999;
        font-size: 0.8rem;
    }
    
    /* Responsive grid for cards */
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
        # مفتاح احتياطي واحد للتطوير
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
    # استبدال الرموز غير المدعومة
    text = text.encode('ascii', 'ignore').decode('ascii')
    # تنظيف الأسطر
    text = re.sub(r'[^\w\s.,!?؛،؟\-:()""\'\']', ' ', text)
    return text.strip()

def log_error(error_msg, source="UI"):
    """تسجيل الخطأ في الجلسة وعرضه"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {source}: {str(error_msg)[:200]}"
    st.session_state.error_log.append(full_msg)
    return full_msg

# ==========================================
# 4. ذكاء الإمبراطورية (AI Engine)
# ==========================================
class SmartGemini:
    """محرك الذكاء الاصطناعي مع توزيع ذكي على المفاتيح"""
    
    @classmethod
    def ask(cls, prompt, fallback="", max_retries=2):
        if ALL_KEYS[0] == "DUMMY":
            log_error("No API keys configured", "Gemini")
            return fallback
        
        # توزيع عشوائي للمفاتيح
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
                        # تجاوز حد الاستخدام - جرب المفتاح التالي
                        continue
                    elif "403" in error_str:
                        # مفتاح غير صالح - أزله من القائمة
                        log_error(f"Invalid key removed: {key[:10]}...", "Gemini")
                        if key in ALL_KEYS:
                            ALL_KEYS.remove(key)
                        continue
                    else:
                        log_error(f"API Error: {error_str[:100]}", "Gemini")
                        continue
            
            # انتظار قبل إعادة المحاولة
            if attempt < max_retries - 1:
                time.sleep(2)
        
        log_error("All API keys exhausted", "Gemini")
        return fallback

    @classmethod
    def generate_niche(cls):
        """توليد نيش مربح عشوائي"""
        prompts = [
            "Output ONLY 2-3 words: highly profitable KDP micro-niche for kids activity books. Be creative and specific. Example: 'Cyberpunk Dinosaurs' or 'Astronaut Chefs'",
            "Output ONLY 2-3 words: trending Etsy printable niche for 2024. Be specific. Example: 'Gothic Unicorns' or 'Kawaii Robots'",
            "Output ONLY 2-3 words: unique children coloring book theme that parents would buy. Example: 'Samurai Pandas' or 'Witch Kittens'",
        ]
        prompt = random.choice(prompts)
        result = cls.ask(prompt, "Fantasy Animals")
        # تنظيف النتيجة
        result = result.strip().strip('"').strip("'")
        # إزالة أي نص إضافي
        result = re.sub(r'[^a-zA-Z\s\-]', '', result)
        result = ' '.join(result.split()[:4])  # خذ أول 4 كلمات كحد أقصى
        return result if len(result) > 3 else "Magical Creatures"

# ==========================================
# 5. مصنع الصور (Image Generation)
# ==========================================
class ImageShield:
    """مولد الصور مع حماية من الفشل"""
    
    @staticmethod
    def _fetch_image(url, max_retries=3):
        """جلب الصورة من الرابط مع إعادة المحاولة"""
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
                log_error(f"Image fetch error: {e}", "ImageShield")
                continue
                
        return None

    @staticmethod
    def generate(prompt, filename, style="coloring"):
        """توليد صورة واحدة"""
        # تحسين البرومبت حسب النوع
        if style == "cover":
            full_prompt = f"Professional children's book cover illustration, {prompt}, vibrant colors, magical atmosphere, blank sky background, STRICTLY NO TEXT NO LETTERS NO NUMBERS NO WORDS"
        elif style == "flashcard":
            full_prompt = f"Cute simple vector educational illustration of {prompt}, isolated on pure white background, thick outlines, bright colors, Montessori flashcard style, no background"
        elif style == "background":
            full_prompt = f"Soft watercolor abstract background, {prompt} theme, light pastel colors, calming, gentle gradients, subtle patterns"
        elif style == "story":
            full_prompt = f"Children's book illustration, {prompt}, colorful, whimsical, storybook art style, detailed but cute"
        else:  # coloring
            full_prompt = f"Bold black and white line art, {prompt}, thick clean outlines, pure white background, NO shading NO colors NO grey, simple clear shapes, kids coloring page, commercial use"
        
        encoded_prompt = requests.utils.quote(full_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1, 99999)}"
        
        img_data = ImageShield._fetch_image(url)
        
        if img_data:
            try:
                with open(filename, "wb") as f:
                    f.write(img_data)
                return True
            except Exception as e:
                log_error(f"File write error: {e}", "ImageShield")
        
        return False

    @classmethod
    def generate_parallel(cls, tasks, max_workers=3):
        """توليد مجموعة صور بالتوازي"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {}
            
            for prompt, filename, style in tasks:
                # تأخير عشوائي لمنع الـ rate limiting
                time.sleep(random.uniform(0.1, 0.4))
                future = executor.submit(cls.generate, prompt, filename, style)
                future_to_file[future] = filename
            
            for future in concurrent.futures.as_completed(future_to_file):
                filename = future_to_file[future]
                try:
                    results[filename] = future.result()
                except Exception as e:
                    log_error(f"Parallel generation error: {e}", "ImageShield")
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
        # إضافة خط مدمج
        self.set_font("Arial", "", 12)

class ProductionEngine:
    """محرك الإنتاج الرئيسي"""
    
    def __init__(self, config, progress_callback=None):
        self.config = config
        self.progress = progress_callback or (lambda x, y: None)
        self.pdf = KDPBook()
        self.temp_files = []
        self.created_pages = 0
    
    def _add_temp_file(self, path):
        """تسجيل ملف مؤقت للتنظيف لاحقاً"""
        self.temp_files.append(path)
    
    def _cleanup(self):
        """تنظيف جميع الملفات المؤقتة"""
        cleaned = 0
        for f in self.temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                    cleaned += 1
                except Exception as e:
                    log_error(f"Cleanup error for {f}: {e}", "Cleanup")
        self.temp_files = []
        return cleaned
    
    def _add_page_number(self, page_num):
        """إضافة رقم الصفحة"""
        self.pdf.set_font("Arial", "I", 8)
        self.pdf.set_y(10.5)
        self.pdf.cell(0, 0.3, str(page_num), align="C")
    
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
    
    def _add_belongs_to_page(self):
        """صفحة الملكية"""
        self.pdf.add_page()
        
        # إطار زخرفي
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
    
    def _add_copyright_page(self):
        """صفحة حقوق النشر"""
        self.pdf.add_page()
        self.pdf.set_font("Arial", "I", 10)
        self.pdf.set_y(9)
        year = datetime.now().year
        self.pdf.multi_cell(0, 0.4, 
            f"© {year} Published by Walid Zaki. All Rights Reserved.\n"
            f"This book is generated for personal use.\n"
            f"KDP Factory Pro V32.1",
            align="C")
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
            # غلاف احتياطي
            self.pdf.add_page()
            self.pdf.set_fill_color(30, 30, 80)
            self.pdf.rect(0, 0, 8.5, 11, 'F')
            self.pdf.set_text_color(255, 255, 255)
            self.pdf.set_font("Arial", "B", 32)
            self.pdf.set_y(4)
            clean_theme = clean_text(theme)
            self.pdf.cell(0, 1, clean_theme[:40].upper(), align="C")
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
        self.pdf.multi_cell(0, 0.5, f"كتاب {clean_text(theme)}\n\n{mode}\n{self.created_pages + pages} صفحة من المتعة والإبداع!", align="C")
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
            else:  # تشكيلة منوعة
                self._mixed_mode(pages, theme)
        except Exception as e:
            log_error(f"Production error in {mode}: {e}", "Production")
            # إضافة صفحات احتياطية
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
            log_error(f"PDF save error: {e}", "Production")
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
        
        prompt = f"""Act as a KDP and TikTok marketing expert. Create a launch package for a children's book with theme: '{clean_theme}'.

Respond in this EXACT format:
---SEO_TITLE---
[Catchy title + subtitle for Amazon KDP]
---SEO_KEYWORDS---
[7 relevant keywords separated by commas]
---AMAZON_DESCRIPTION---
[Compelling book description in Arabic or English, 3-5 sentences]
---TIKTOK_SCRIPT---
[30-second viral TikTok script with hook, body, and call to action]"""

        result = SmartGemini.ask(prompt)
        
        # استخراج الأقسام
        marketing = {
            "seo_title": clean_theme,
            "keywords": "kids, activity, book, fun, learning, creative, gift",
            "description": f"A wonderful activity book featuring {clean_theme}!",
            "tiktok": f"🎨 Check out this amazing {clean_theme} book! Perfect for kids! #KDP #KidsBooks"
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
        # الحصول على أفكار الصور
        prompt = f"List exactly {count+5} simple, cute items related to '{theme}' for kids coloring. Output ONLY the item names, one per line. No numbers, no descriptions."
        ideas_text = SmartGemini.ask(prompt, "\n".join([f"Item {i}" for i in range(count+5)]))
        
        ideas = []
        for line in ideas_text.split('\n'):
            line = line.strip().strip('1234567890.- ')
            if len(line) > 2:
                ideas.append(line)
        
        ideas = ideas[:max(count, 10)]
        
        # تحضير المهام
        tasks = []
        for i, idea in enumerate(ideas):
            clean_idea = clean_text(idea)
            if clean_idea:
                fname = f"col_{i}_{random.randint(100,999)}.jpg"
                self._add_temp_file(fname)
                tasks.append((clean_idea, fname, "coloring"))
        
        # توليد الصور بالتوازي
        if tasks:
            results = ImageShield.generate_parallel(tasks[:count])
            
            for i, (idea, fname, _) in enumerate(tasks[:count]):
                progress_pct = 0.15 + (i / len(tasks[:count])) * 0.55
                self.progress(progress_pct, f"🎨 صفحة تلوين {i+1}/{len(tasks[:count])}")
                
                self.pdf.add_page()
                
                # عنوان الصفحة
                self.pdf.set_font("Arial", "B", 16)
                self.pdf.set_y(0.5)
                self.pdf.cell(0, 0.5, f"🎨 تلوين: {idea[:30]}", align="C", ln=True)
                
                # إطار للتلوين
                self.pdf.set_line_width(0.02)
                self.pdf.set_draw_color(200)
                self.pdf.rect(1, 1.5, 6.5, 7.5)
                
                # إدراج الصورة إذا وجدت
                if results.get(fname, False):
                    try:
                        self.pdf.image(fname, x=1.2, y=1.7, w=6.1, h=7.1)
                    except:
                        self._emergency_page()
                else:
                    # صفحة بديلة
                    self.pdf.set_font("Arial", "B", 24)
                    self.pdf.set_y(4)
                    self.pdf.cell(0, 1, f"ارسم: {idea[:20]}!", align="C")
                
                self._add_page_number(self.created_pages + 1)
                self.created_pages += 1
                
                # صفحة فارغة للفصل بين الصفحات
                if i < len(tasks[:count]) - 1:
                    self.pdf.add_page()
                    self.created_pages += 1
    
    def _story_mode(self, count, theme):
        """خط إنتاج القصص المصورة"""
        clean_theme = clean_text(theme)
        prompt = f"Write a children's story about '{clean_theme}' with exactly {min(count, 8)} short parts. Separate each part with '||'. Make it fun and engaging for ages 4-8."
        
        story_text = SmartGemini.ask(prompt, "Part 1||Part 2||Part 3")
        parts = [p.strip() for p in story_text.split('||') if p.strip()]
        parts = parts[:count]
        
        # توليد صور للقصة
        tasks = []
        for i, part in enumerate(parts):
            # استخدام الجملة الأولى كوصف للصورة
            first_sentence = part.split('.')[0][:80]
            fname = f"story_{i}_{random.randint(100,999)}.jpg"
            self._add_temp_file(fname)
            tasks.append((first_sentence, fname, "story"))
        
        results = ImageShield.generate_parallel(tasks) if tasks else {}
        
        for i, part in enumerate(parts):
            progress_pct = 0.15 + (i / len(parts)) * 0.55
            self.progress(progress_pct, f"📖 صفحة قصة {i+1}/{len(parts)}")
            
            # صفحة النص
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 14)
            self.pdf.set_y(1)
            self.pdf.multi_cell(0, 0.4, f"الجزء {i+1}", align="C")
            self.pdf.set_font("Arial", "", 14)
            self.pdf.set_y(2)
            self.pdf.multi_cell(0, 0.5, clean_text(part), align="C")
            self.created_pages += 1
            
            # صفحة الصورة
            fname = tasks[i][1] if i < len(tasks) else None
            self.pdf.add_page()
            
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
        puzzles_per_type = max(2, count // 4)
        
        puzzle_count = 0
        
        # سودوكو
        for i in range(puzzles_per_type):
            if puzzle_count >= count:
                break
            
            progress_pct = 0.15 + (puzzle_count / count) * 0.55
            self.progress(progress_pct, f"🧩 سودوكو {i+1}")
            
            # إنشاء سودوكو
            board, solution = self._generate_sudoku()
            
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.8, f"🧩 Sudoku #{i+1}", align="C")
            
            # رسم شبكة السودوكو
            self._draw_sudoku_grid(board)
            
            self._add_page_number(self.created_pages + 1)
            self.created_pages += 1
            puzzle_count += 1
            
            # صفحة الحل
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.8, f"✅ حل Sudoku #{i+1}", align="C")
            self._draw_sudoku_grid(solution, is_solution=True)
            self.created_pages += 1
        
        # متاهات
        for i in range(puzzles_per_type):
            if puzzle_count >= count:
                break
            
            progress_pct = 0.15 + (puzzle_count / count) * 0.55
            self.progress(progress_pct, f"🌀 متاهة {i+1}")
            
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.8, f"🌀 Maze #{i+1}", align="C")
            self._draw_maze()
            self.created_pages += 1
            puzzle_count += 1
        
        # البحث عن الكلمات
        words_prompt = f"List 6 simple words related to '{clean_theme}' for a word search puzzle. One word per line, max 8 letters each."
        words_text = SmartGemini.ask(words_prompt, "FUN\nGAME\nPLAY\nHAPPY\nSMILE\nJOY")
        words = [w.strip().upper()[:8] for w in words_text.split('\n') if w.strip()]
        words = words[:6]
        
        for i in range(puzzles_per_type):
            if puzzle_count >= count:
                break
            
            progress_pct = 0.15 + (puzzle_count / count) * 0.55
            self.progress(progress_pct, f"🔤 بحث كلمات {i+1}")
            
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.8, f"🔤 Word Search #{i+1}", align="C")
            
            # عرض الكلمات
            self.pdf.set_font("Arial", "", 12)
            self.pdf.set_y(1.8)
            self.pdf.cell(0, 0.5, "Find these words: " + ", ".join(words), align="C")
            
            self._draw_word_search(words)
            self.created_pages += 1
            puzzle_count += 1
    
    def _generate_sudoku(self):
        """توليد سودوكو مع الحل"""
        base = 3
        side = base * base
        
        def pattern(r, c):
            return (base * (r % base) + r // base + c) % side
        
        def shuffle(s):
            return random.sample(s, len(s))
        
        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, side + 1))
        
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        solution = [row[:] for row in board]
        
        # إخفاء الخلايا
        squares = side * side
        empties = squares * 2 // 3
        for p in random.sample(range(squares), empties):
            board[p // side][p % side] = 0
        
        return board, solution
    
    def _draw_sudoku_grid(self, board, is_solution=False):
        """رسم شبكة السودوكو"""
        side = len(board)
        cell_size = 0.6
        start_x = (8.5 - (cell_size * side)) / 2
        start_y = 2.0
        
        self.pdf.set_line_width(0.01)
        self.pdf.set_draw_color(100)
        
        for i in range(side + 1):
            line_width = 0.03 if i % 3 == 0 else 0.01
            self.pdf.set_line_width(line_width)
            
            # خطوط أفقية
            self.pdf.line(start_x, start_y + i * cell_size, 
                         start_x + side * cell_size, start_y + i * cell_size)
            # خطوط عمودية
            self.pdf.line(start_x + i * cell_size, start_y, 
                         start_x + i * cell_size, start_y + side * cell_size)
        
        # كتابة الأرقام
        self.pdf.set_font("Arial", "B", 16)
        for r in range(side):
            for c in range(side):
                val = board[r][c]
                if val != 0:
                    x = start_x + c * cell_size + cell_size / 3
                    y = start_y + r * cell_size + cell_size / 1.4
                    if is_solution:
                        self.pdf.set_text_color(0, 150, 0)
                    else:
                        self.pdf.set_text_color(0)
                    self.pdf.text(x, y, str(val))
        
        self.pdf.set_text_color(0)
    
    def _draw_maze(self, width=10, height=10):
        """رسم متاهة"""
        # إنشاء المتاهة
        grid = [[{'N': True, 'S': True, 'E': True, 'W': True, 'visited': False} 
                 for _ in range(width)] for _ in range(height)]
        
        stack = [(0, 0)]
        grid[0][0]['visited'] = True
        
        while stack:
            cx, cy = stack[-1]
            directions = [('N', 0, -1, 'S'), ('S', 0, 1, 'N'), 
                         ('E', 1, 0, 'W'), ('W', -1, 0, 'E')]
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
        
        # فتح المدخل والمخرج
        grid[0][0]['W'] = False
        grid[height-1][width-1]['E'] = False
        
        # رسم المتاهة
        cell_size = 0.5
        start_x = (8.5 - (width * cell_size)) / 2
        start_y = 2.5
        
        self.pdf.set_line_width(0.03)
        self.pdf.set_draw_color(0)
        
        for y in range(height):
            for x in range(width):
                sx = start_x + x * cell_size
                sy = start_y + y * cell_size
                
                if grid[y][x]['N']:
                    self.pdf.line(sx, sy, sx + cell_size, sy)
                if grid[y][x]['S']:
                    self.pdf.line(sx, sy + cell_size, sx + cell_size, sy + cell_size)
                if grid[y][x]['W']:
                    self.pdf.line(sx, sy, sx, sy + cell_size)
                if grid[y][x]['E']:
                    self.pdf.line(sx + cell_size, sy, sx + cell_size, sy + cell_size)
        
        # علامة البداية والنهاية
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.set_text_color(0, 150, 0)
        self.pdf.text(start_x - 0.3, start_y + 0.3, "ابدأ")
        self.pdf.set_text_color(255, 0, 0)
        self.pdf.text(start_x + width * cell_size - 0.1, start_y + height * cell_size - 0.2, "النهاية")
        self.pdf.set_text_color(0)
    
    def _draw_word_search(self, words, size=10):
        """رسم شبكة البحث عن الكلمات"""
        # إنشاء الشبكة
        grid = [[' ' for _ in range(size)] for _ in range(size)]
        
        for word in words:
            word = word.upper().replace(' ', '')
            placed = False
            
            for _ in range(50):
                direction = random.choice(['H', 'V', 'D'])
                if direction == 'H':
                    dr, dc = 0, 1
                elif direction == 'V':
                    dr, dc = 1, 0
                else:
                    dr, dc = 1, 1
                
                r = random.randint(0, size - 1)
                c = random.randint(0, size - 1)
                
                end_r = r + dr * (len(word) - 1)
                end_c = c + dc * (len(word) - 1)
                
                if 0 <= end_r < size and 0 <= end_c < size:
                    can_place = True
                    for i, char in enumerate(word):
                        cr, cc = r + dr * i, c + dc * i
                        if grid[cr][cc] not in (' ', char):
                            can_place = False
                            break
                    
                    if can_place:
                        for i, char in enumerate(word):
                            grid[r + dr * i][c + dc * i] = char
                        placed = True
                        break
        
        # ملء الفراغات
        for r in range(size):
            for c in range(size):
                if grid[r][c] == ' ':
                    grid[r][c] = random.choice(string.ascii_uppercase)
        
        # رسم الشبكة
        cell_size = 0.55
        start_x = (8.5 - (size * cell_size)) / 2
        start_y = 3.0
        
        self.pdf.set_line_width(0.01)
        self.pdf.set_draw_color(150)
        
        for i in range(size + 1):
            self.pdf.line(start_x, start_y + i * cell_size, 
                         start_x + size * cell_size, start_y + i * cell_size)
            self.pdf.line(start_x + i * cell_size, start_y, 
                         start_x + i * cell_size, start_y + size * cell_size)
        
        self.pdf.set_font("Arial", "B", 12)
        for r in range(size):
            for c in range(size):
                x = start_x + c * cell_size + cell_size / 3.5
                y = start_y + r * cell_size + cell_size / 1.5
                self.pdf.text(x, y, grid[r][c])
    
    def _journal_mode(self, count, theme):
        """خط إنتاج المخططات والدفاتر"""
        clean_theme = clean_text(theme)
        
        for i in range(count):
            progress_pct = 0.15 + (i / count) * 0.55
            self.progress(progress_pct, f"📋 مخطط {i+1}/{count}")
            
            self.pdf.add_page()
            
            # عنوان اليوم
            self.pdf.set_font("Arial", "B", 18)
            self.pdf.set_y(0.8)
            self.pdf.cell(0, 0.6, f"📅 يوم {i+1}: {clean_theme[:25]}", align="C", ln=True)
            
            # قسم الأولويات
            self.pdf.set_font("Arial", "B", 12)
            self.pdf.set_y(2)
            self.pdf.cell(0, 0.5, "🎯 أهم 3 أولويات اليوم:", ln=True)
            
            self.pdf.set_line_width(0.01)
            self.pdf.set_draw_color(200)
            for j in range(3):
                y = 2.8 + j * 0.8
                self.pdf.line(1.5, y, 7, y)
                self.pdf.set_font("Arial", "I", 10)
                self.pdf.text(1.5, y - 0.15, f"{j+1}.")
            
            # قسم الملاحظات
            self.pdf.set_font("Arial", "B", 12)
            self.pdf.set_y(5.5)
            self.pdf.cell(0, 0.5, "📝 ملاحظات:", ln=True)
            
            for j in range(5):
                y = 6 + j * 0.6
                self.pdf.line(1.5, y, 7, y)
            
            # قسم تتبع العادات
            self.pdf.set_font("Arial", "B", 12)
            self.pdf.set_y(9)
            self.pdf.cell(0, 0.5, "✅ تتبع العادات:", ln=True)
            
            habits = ["قراءة", "رياضة", "ماء", "تأمل", "تدوين"]
            for j, habit in enumerate(habits):
                y = 9.5 + j * 0.35
                self.pdf.set_font("Arial", "", 10)
                self.pdf.text(1.5, y, f"☐ {habit}")
            
            self._add_page_number(self.created_pages + 1)
            self.created_pages += 1
    
    def _quotes_mode(self, count, theme):
        """خط إنتاج الاقتباسات"""
        clean_theme = clean_text(theme)
        prompt = f"Generate {count} unique, inspiring quotes about '{clean_theme}'. One quote per line. Make them profound and original."
        
        quotes_text = SmartGemini.ask(prompt, "Believe in yourself.\nStay strong.\nKeep going.")
        quotes = [q.strip().strip('"').strip("'") for q in quotes_text.split('\n') if len(q.strip()) > 5]
        quotes = quotes[:count]
        
        for i, quote in enumerate(quotes):
            progress_pct = 0.15 + (i / len(quotes)) * 0.55
            self.progress(progress_pct, f"💭 اقتباس {i+1}/{len(quotes)}")
            
            self.pdf.add_page()
            
            # خلفية ملونة
            colors = [(255,245,238), (240,248,255), (255,250,240), (245,255,250), (255,245,245)]
            bg_color = random.choice(colors)
            self.pdf.set_fill_color(*bg_color)
            self.pdf.rect(0.5, 1, 7.5, 9, 'F')
            
            # إطار
            self.pdf.set_line_width(0.04)
            self.pdf.set_draw_color(100, 100, 150)
            self.pdf.rect(0.75, 1.25, 7, 8.5)
            
            # الاقتباس
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(3.5)
            self.pdf.multi_cell(0, 0.6, f'"{clean_text(quote)}"', align="C")
            
            # رقم الاقتباس
            self.pdf.set_font("Arial", "I", 10)
            self.pdf.set_y(10)
            self.pdf.cell(0, 0.4, f"اقتباس {i+1}/{len(quotes)}", align="C")
            
            self._add_page_number(self.created_pages + 1)
            self.created_pages += 1
    
    def _flashcards_mode(self, count, theme):
        """خط إنتاج البطاقات التعليمية"""
        clean_theme = clean_text(theme)
        prompt = f"List {count} simple educational words related to '{clean_theme}' for children's flashcards. One word per line."
        
        words_text = SmartGemini.ask(prompt, "Sun\nMoon\nStar\nTree\nBook")
        words = [w.strip() for w in words_text.split('\n') if len(w.strip()) > 1]
        words = words[:count]
        
        tasks = []
        for i, word in enumerate(words):
            fname = f"flash_{i}_{random.randint(100,999)}.jpg"
            self._add_temp_file(fname)
            tasks.append((word, fname, "flashcard"))
        
        results = ImageShield.generate_parallel(tasks) if tasks else {}
        
        for i, (word, fname, _) in enumerate(tasks[:count]):
            progress_pct = 0.15 + (i / len(tasks[:count])) * 0.55
            self.progress(progress_pct, f"🃏 بطاقة {i+1}/{len(tasks[:count])}")
            
            self.pdf.add_page()
            
            # إطار البطاقة
            self.pdf.set_line_width(0.05)
            self.pdf.set_draw_color(50, 50, 150)
            self.pdf.rect(1.25, 1.5, 6, 7)
            
            # الصورة
            if results.get(fname, False):
                try:
                    self.pdf.image(fname, x=1.5, y=2, w=5.5, h=5.5)
                except:
                    pass
            
            # الكلمة
            self.pdf.set_font("Arial", "B", 32)
            self.pdf.set_y(8.5)
            self.pdf.cell(0, 0.8, word.upper(), align="C")
            
            self._add_page_number(self.created_pages + 1)
            self.created_pages += 1
    
    def _comics_mode(self, count, theme):
        """خط إنتاج الكوميكس"""
        clean_theme = clean_text(theme)
        
        for i in range(count):
            progress_pct = 0.15 + (i / count) * 0.55
            self.progress(progress_pct, f"💬 كوميكس {i+1}/{count}")
            
            self.pdf.add_page()
            
            # عنوان
            self.pdf.set_font("Arial", "B", 20)
            self.pdf.set_y(0.5)
            self.pdf.cell(0, 0.6, f"💬 {clean_theme[:20]} Comics #{i+1}", align="C")
            
            # لوحات الكوميكس
            # لوحة 1
            self.pdf.set_line_width(0.03)
            self.pdf.rect(0.75, 1.5, 3.4, 3.5)
            self.pdf.set_font("Arial", "", 10)
            self.pdf.set_y(1.7)
            self.pdf.cell(0, 0.3, "Panel 1", align="C")
            
            # لوحة 2
            self.pdf.rect(4.35, 1.5, 3.4, 3.5)
            self.pdf.set_y(1.7)
            self.pdf.cell(0, 0.3, "Panel 2", align="C")
            
            # لوحة 3
            self.pdf.rect(0.75, 5.3, 3.4, 3.5)
            self.pdf.set_y(5.5)
            self.pdf.cell(0, 0.3, "Panel 3", align="C")
            
            # لوحة 4
            self.pdf.rect(4.35, 5.3, 3.4, 3.5)
            self.pdf.set_y(5.5)
            self.pdf.cell(0, 0.3, "Panel 4", align="C")
            
            # فقاعات كلام
            self.pdf.set_font("Arial", "I", 12)
            self.pdf.set_y(9.2)
            self.pdf.cell(0, 0.4, "اكتب قصتك هنا...", align="C")
            
            self._add_page_number(self.created_pages + 1)
            self.created_pages += 1
    
    def _alphabet_mode(self, count):
        """خط إنتاج تعليم الحروف"""
        letters = list(string.ascii_uppercase)[:min(count, 26)]
        
        for i, char in enumerate(letters):
            progress_pct = 0.15 + (i / len(letters)) * 0.55
            self.progress(progress_pct, f"🔤 حرف {char}")
            
            self.pdf.add_page()
            
            # الحرف الكبير
            self.pdf.set_font("Arial", "B", 120)
            self.pdf.set_y(1.5)
            self.pdf.cell(0, 2, char, align="C", ln=True)
            
            # الحرف الصغير
            self.pdf.set_font("Arial", "B", 60)
            self.pdf.set_y(3.5)
            self.pdf.cell(0, 1, char.lower(), align="C", ln=True)
            
            # خطوط للتتبع
            self.pdf.set_font("Arial", "", 20)
            self.pdf.set_y(5)
            self.pdf.cell(0, 0.5, "✏️ تتبع الحرف:", align="C", ln=True)
            
            self.pdf.set_text_color(200)
            for j in range(3):
                y = 6 + j * 1
                self.pdf.set_font("Arial", "", 40)
                self.pdf.set_y(y)
                self.pdf.cell(0, 1, f"{char}  {char.lower()}  {char}  {char.lower()}", align="C")
            
            self.pdf.set_text_color(0)
            self._add_page_number(self.created_pages + 1)
            self.created_pages += 1
    
    def _mixed_mode(self, count, theme):
        """خط إنتاج متنوع"""
        quarter = max(2, count // 4)
        remaining = count
        
        modes = [
            (self._coloring_mode, "🎨 تلوين"),
            (self._puzzles_mode, "🧩 ألغاز"),
            (self._journal_mode, "📋 تخطيط"),
            (self._quotes_mode, "💭 اقتباسات")
        ]
        
        for func, mode_name in modes:
            if remaining <= 0:
                break
            
            pages_for_mode = min(quarter, remaining)
            self.progress(0.2, f"{mode_name} ({pages_for_mode} صفحات)")
            
            try:
                func(pages_for_mode, theme)
                remaining -= pages_for_mode
            except Exception as e:
                log_error(f"Mixed mode error in {mode_name}: {e}", "Production")
                for _ in range(pages_for_mode):
                    self._emergency_page()
                remaining -= pages_for_mode

# ==========================================
# 7. البوت الآلي (Hyper-Bot)
# ==========================================
def send_to_telegram(pdf_file, marketing_data, theme):
    """إرسال المحتوى إلى تيليجرام"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False, "Token or Chat ID not configured"
    
    results = []
    
    # إرسال الكتاب
    try:
        with open(pdf_file, "rb") as f:
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": f"📚 كتاب جديد: {theme}\n🏭 KDP Factory Pro V32.1"
                },
                files={"document": f},
                timeout=30
            )
            if response.status_code == 200:
                results.append("✅ تم إرسال الكتاب")
            else:
                results.append(f"❌ فشل إرسال الكتاب: {response.status_code}")
    except Exception as e:
        results.append(f"❌ خطأ إرسال الكتاب: {str(e)[:100]}")
    
    # إرسال التسويق
    try:
        seo_text = f"""📊 معلومات النشر لـ: {theme}

🏷️ العنوان: {marketing_data.get('seo_title', theme)}

🔑 الكلمات المفتاحية: {marketing_data.get('keywords', '')}

📝 الوصف: {marketing_data.get('description', '')}

🎬 سكريبت تيك توك:
{marketing_data.get('tiktok', '')}"""

        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": seo_text[:4000]
            },
            timeout=20
        )
        if response.status_code == 200:
            results.append("✅ تم إرسال التسويق")
        else:
            results.append(f"❌ فشل إرسال التسويق: {response.status_code}")
    except Exception as e:
        results.append(f"❌ خطأ إرسال التسويق: {str(e)[:100]}")
    
    return True, " | ".join(results)

def hyper_bot_loop():
    """حلقة البوت الآلي"""
    st.session_state.hyper_bot_log.append("🟢 بدء تشغيل البوت الآلي")
    
    while True:
        try:
            # تحقق من وجود مفاتيح
            has_keys = ALL_KEYS[0] != "DUMMY"
            has_telegram = bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)
            
            if not has_keys:
                st.session_state.hyper_bot_log.append("⚠️ لا توجد مفاتيح API")
                time.sleep(900)
                continue
            
            if not has_telegram:
                st.session_state.hyper_bot_log.append("⚠️ لم يتم تكوين تيليجرام")
                time.sleep(900)
                continue
            
            # توليد فكرة
            theme = SmartGemini.generate_niche()
            st.session_state.hyper_bot_log.append(f"🎯 النيش المولد: {theme}")
            
            # إنتاج الكتاب
            engine = ProductionEngine({
                'theme': theme,
                'pages': 24,
                'mode': 'تشكيلة منوعة'
            })
            
            pdf_file, marketing = engine.run()
            
            # إرسال للتليجرام
            success, msg = send_to_telegram(pdf_file, marketing, theme)
            st.session_state.hyper_bot_log.append(msg)
            
            # تنظيف
            engine._cleanup()
            
        except Exception as e:
            error_msg = f"❌ خطأ في البوت: {str(e)[:150]}"
            st.session_state.hyper_bot_log.append(error_msg)
            log_error(error_msg, "HyperBot")
            
            # محاولة إرسال الخطأ للتليجرام
            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                try:
                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                        data={
                            "chat_id": TELEGRAM_CHAT_ID,
                            "text": f"⚠️ خطأ في Hyper-Bot:\n{error_msg}"
                        },
                        timeout=10
                    )
                except:
                    pass
        
        time.sleep(900)  # 15 دقيقة

# بدء البوت
if 'hyper_bot_started' not in st.session_state:
    st.session_state.hyper_bot_started = True
    st.session_state.hyper_bot_log = deque(maxlen=20)
    threading.Thread(target=hyper_bot_loop, daemon=True).start()

# ==========================================
# 8. واجهة المستخدم (Dashboard)
# ==========================================
def main():
    # العنوان الرئيسي
    st.markdown('<h1 class="main-title">🏭 مصنع المحتوى الرقمي</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">المهندس: وليد زكي | KDP Factory Pro V32.1</p>', unsafe_allow_html=True)
    
    # التبويبات
    tabs = st.tabs(["🚀 المصنع السريع", "🔍 محلل النيش", "🤖 الأتمتة", "📋 السجلات"])
    
    # ========== تبويب المصنع السريع ==========
    with tabs[0]:
        st.markdown('<div class="info-card">⚡ اختر خط الإنتاج وسيتم تصنيع الكتاب كاملاً مع خطة التسويق.</div>', unsafe_allow_html=True)
        
        # حقل النيش مع زر التوليد
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_theme = st.text_input(
                "🎯 فكرة النيش:",
                value="قطط سايبربانك",
                key="theme_input",
                placeholder="مثال: ديناصورات فضائية، أميرات نينجا..."
            )
        
        with col2:
            st.markdown('<div class="niche-btn">', unsafe_allow_html=True)
            if st.button("✨ توليد", key="gen_niche", use_container_width=True, help="توليد نيش مربح عشوائياً"):
                with st.spinner("جاري توليد فكرة..."):
                    new_niche = SmartGemini.generate_niche()
                    st.session_state.theme_input = new_niche
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # عدد الصفحات
        user_pages = st.number_input(
            "📄 عدد الصفحات:",
            min_value=10,
            max_value=150,
            value=24,
            step=2,
            key="pages_input"
        )
        
        # نوع الكتاب
        modes = [
            "تلوين للأطفال",
            "قصص مصورة",
            "ألغاز ونشاطات",
            "مخططات ودفاتر",
            "بطاقات تعليمية",
            "كتب اقتباسات",
            "كوميكس ومانغا",
            "تعليم وتتبع",
            "تشكيلة منوعة"
        ]
        user_mode = st.selectbox("📦 خط الإنتاج:", modes, key="mode_input")
        
        # زر التصنيع
        if st.button("🚀 ابدأ التصنيع", use_container_width=True, key="start_production"):
            if not user_theme or len(user_theme.strip()) < 2:
                st.error("⚠️ الرجاء إدخال فكرة النيش أولاً")
            else:
                run_production_line(user_theme.strip(), user_pages, user_mode)
    
    # ========== تبويب محلل النيش ==========
    with tabs[1]:
        st.markdown('<div class="info-card">🔮 أدخل فكرة خام وسيقوم الذكاء الاصطناعي بتحليلها واقتراح أفضل استراتيجية للنشر.</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            idea_input = st.text_input(
                "💡 فكرة خام:",
                placeholder="مثال: قطط للأطفال، يوميات دراسية، وصفات كيتو...",
                key="idea_input"
            )
        
        with col2:
            st.markdown('<div class="niche-btn">', unsafe_allow_html=True)
            if st.button("🎲 عشوائي", key="random_idea", use_container_width=True):
                random_ideas = ["ديناصورات", "حوريات بحر", "روبوتات", "أبطال خارقين", "حيوانات المزرعة", "فضاء", "قراصنة", "جنيات"]
                st.session_state.idea_input = random.choice(random_ideas)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🔍 حلل النيش", use_container_width=True, key="analyze_niche"):
            if not idea_input or len(idea_input.strip()) < 2:
                st.error("⚠️ الرجاء إدخال فكرة للتحليل")
            else:
                with st.spinner("🕵️ جاري تحليل السوق والمنافسة..."):
                    analysis_prompt = f"""Analyze the niche '{idea_input}' for KDP and Etsy.

Provide a complete analysis in Arabic:
1. 📊 تقييم السوق: هل النيش مطلوب؟ ما حجم المنافسة؟
2. 📖 أفضل نوع كتاب: اقترح نوع الكتاب الأنسب (تلوين، ألغاز، قصص...)
3. 🏷️ عنوان مقترح: عنوان جذاب للكتاب
4. 🔑 7 كلمات مفتاحية: للبحث في أمازون
5. 💰 توقعات: هل يستحق النشر؟
6. 🎬 خطاف تيك توك: جملة افتتاحية لفيديو تسويقي"""
                    
                    analysis = SmartGemini.ask(analysis_prompt, 
                        "النيش واعد. نوصي بكتاب تلوين.")
                    
                    st.success("✅ اكتمل التحليل!")
                    st.markdown(f'<div class="info-card card-seo">{analysis}</div>', unsafe_allow_html=True)
    
    # ========== تبويب الأتمتة ==========
    with tabs[2]:
        st.markdown('<div class="info-card">🤖 حالة المصنع الآلي ومركز التحكم.</div>', unsafe_allow_html=True)
        
        # حالة البوت
        bot_status = "🟢 نشط" if hasattr(st.session_state, 'hyper_bot_started') else "🔴 غير نشط"
        st.metric("حالة الـ Hyper-Bot", bot_status)
        
        telegram_status = "✅ متصل" if (TELEGRAM_TOKEN and TELEGRAM_CHAT_ID) else "❌ غير مكون"
        st.metric("الاتصال بتليجرام", telegram_status)
        
        api_status = f"✅ {len(ALL_KEYS)} مفاتيح" if ALL_KEYS[0] != "DUMMY" else "❌ لا توجد مفاتيح"
        st.metric("مفاتيح Gemini API", api_status)
        
        # سجل البوت
        if hasattr(st.session_state, 'hyper_bot_log') and st.session_state.hyper_bot_log:
            st.markdown("#### 📜 سجل نشاط البوت:")
            for log_entry in list(st.session_state.hyper_bot_log)[-5:]:
                st.text(log_entry)
        
        # زر إعادة تشغيل البوت
        if st.button("🔄 أعد تشغيل البوت", use_container_width=True):
            st.session_state.hyper_bot_log = deque(maxlen=20)
            st.session_state.hyper_bot_log.append("🔄 جاري إعادة التشغيل...")
            st.rerun()
    
    # ========== تبويب السجلات ==========
    with tabs[3]:
        st.markdown('<div class="info-card">📋 سجل الأخطاء والمعلومات التقنية للمطور.</div>', unsafe_allow_html=True)
        
        if st.session_state.error_log:
            st.markdown("#### ❌ سجل الأخطاء:")
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            for error in list(st.session_state.error_log):
                st.text(error)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("🗑️ مسح السجلات", use_container_width=True):
                st.session_state.error_log.clear()
                st.rerun()
        else:
            st.success("✅ لا توجد أخطاء مسجلة. كل شيء يعمل بشكل طبيعي!")
        
        # معلومات النظام
        if st.button("ℹ️ عرض معلومات النظام", use_container_width=True):
            st.json({
                "version": "32.1",
                "api_keys": len(ALL_KEYS),
                "telegram_configured": bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID),
                "hyper_bot_active": hasattr(st.session_state, 'hyper_bot_started'),
                "errors_count": len(st.session_state.error_log)
            })

def run_production_line(theme, pages, mode):
    """تشغيل خط الإنتاج وعرض النتائج"""
    # شريط التقدم
    progress_bar = st.progress(0, "🚀 تهيئة المصنع...")
    status_area = st.empty()
    
    def update_progress(val, msg):
        progress_bar.progress(val, text=msg)
        status_area.info(msg)
    
    # تهيئة المحرك
    engine = ProductionEngine(
        {'theme': theme, 'pages': pages, 'mode': mode},
        progress_callback=update_progress
    )
    
    try:
        # تشغيل الإنتاج
        pdf_file, marketing = engine.run()
        
        # عرض النتائج
        progress_bar.progress(1.0, "✅ اكتمل الإنتاج!")
        status_area.success("🎉 تم تصنيع الكتاب بنجاح!")
        
        # عرض البطاقات
        st.markdown('<div class="card-grid">', unsafe_allow_html=True)
        
        # بطاقة SEO
        st.markdown(f'''
        <div class="info-card card-seo">
            <div class="card-header">📈 معلومات النشر (KDP SEO)</div>
            <p><strong>🏷️ العنوان:</strong> {marketing.get("seo_title", theme)}</p>
            <p><strong>🔑 الكلمات المفتاحية:</strong> {marketing.get("keywords", "")}</p>
            <p><strong>📝 الوصف:</strong> {marketing.get("description", "")}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # بطاقة TikTok
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
            # تحميل الكتاب
            with open(pdf_file, "rb") as f:
                pdf_bytes = f.read()
            
            st.download_button(
                "📥 تحميل الكتاب PDF",
                data=pdf_bytes,
                file_name=pdf_file,
                mime="application/pdf",
                use_container_width=True
            )
        
        with col2:
            # إرسال للتليجرام
            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                if st.button("📤 أرسل للتليجرام", use_container_width=True):
                    with st.spinner("جاري الإرسال..."):
                        success, msg = send_to_telegram(pdf_file, marketing, theme)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
            else:
                st.info("⚙️ قم بتكوين تيليجرام في الإعدادات للإرسال التلقائي")
        
        # تنظيف
        engine._cleanup()
        
        # عرض في حالة وجود أخطاء سابقة
        if st.session_state.error_log:
            with st.expander("⚠️ عرض سجل الأخطاء"):
                for error in list(st.session_state.error_log)[-5:]:
                    st.text(error)
        
    except Exception as e:
        error_msg = log_error(f"UI Production Error: {e}", "UI")
        
        # عرض الخطأ
        st.error("❌ حدث خطأ غير متوقع أثناء التصنيع")
        
        with st.expander("🔍 تفاصيل الخطأ (للمطور)"):
            st.code(traceback.format_exc())
            st.text(f"سجل الخطأ: {error_msg}")
        
        # إرسال الخطأ للتليجرام
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    data={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": f"⚠️ خطأ في المصنع:\n{error_msg}\n\nالموضوع: {theme}\nالوضع: {mode}"
                    },
                    timeout=10
                )
            except:
                pass
        
        # محاولة تنظيف
        try:
            engine._cleanup()
        except:
            pass

# ==========================================
# 9. التذييل
# ==========================================
st.markdown("""
<div class="footer">
    <p>🏭 KDP Factory Pro V32.1 | © 2024 Walid Zaki | جميع الحقوق محفوظة</p>
    <p>مصنع محتوى رقمي متكامل للإنتاج والنشر التلقائي</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()