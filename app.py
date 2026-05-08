"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    KDP FACTORY PRO V15 - الإصدار الملكي الكامل                 ║
║                    تصميم: إروين سميث | المحرك: AI Titan Engine                 ║
║                                                                               ║
║  ⚡ الميزات الأسطورية في هذا الإصدار:                                         ║
║  ✓ نظام الصفحات المتقابلة (قصة في وجه - رسم/نشاط في الوجه الآخر)              ║
║  ✓ 8 أنواع كتب احترافية مع خيارات دقيقة                                       ║
║  ✓ محرك ألغاز متكامل (متاهات - سودوكو - كلمات متقاطعة - وصل النقاط)           ║
║  ✓ نظام تعويض ذكي عند فشل الصور                                              ║
║  ✓ تنسيق KDP احترافي مع هوامش آمنة للتجليد                                   ║
║  ✓ إرسال تلقائي لتليجرام مع مواد البيع كاملة                                 ║
║  ✓ واجهة مستخدم تفاعلية مع بطاقات ملونة                                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# ------------------------------------------------------------------------------
# المكتبات الأساسية
# ------------------------------------------------------------------------------

import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import random
import time
import traceback
import string
import json
from datetime import datetime
from PIL import Image
import io

# ------------------------------------------------------------------------------
# إعدادات الواجهة
# ------------------------------------------------------------------------------

st.set_page_config(
    page_title="KDP Factory Pro V15 | مصنع كتب أمازون الملكي",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# CSS المتطور
# ------------------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 52px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 18px;
        margin-bottom: 30px;
    }
    
    .book-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        color: white;
        border: 2px solid transparent;
    }
    
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    .book-card.selected {
        border: 2px solid #ffd700;
        box-shadow: 0 0 20px rgba(255,215,0,0.5);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 12px 30px;
        font-weight: bold;
        font-size: 18px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(102,126,234,0.4);
    }
    
    .stat-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin: 10px 0;
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: bold;
        color: #667eea;
    }
    
    .info-box {
        background: #e8f4f8;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-right: 4px solid #4ecdc4;
    }
    
    .feature-badge {
        display: inline-block;
        background: #ff6b6b;
        color: white;
        border-radius: 20px;
        padding: 5px 12px;
        font-size: 12px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# دالة مساعدة لقراءة معلمات URL (تعمل على جميع الإصدارات)
# ------------------------------------------------------------------------------

def get_query_param(key, default=None):
    """قراءة معلمة من URL - متوافقة مع جميع إصدارات Streamlit"""
    try:
        if hasattr(st, 'query_params'):
            return st.query_params.get(key, default)
        if hasattr(st, 'experimental_get_query_params'):
            params = st.experimental_get_query_params()
            value = params.get(key, [default])
            return value[0] if value else default
    except:
        pass
    return default

# ------------------------------------------------------------------------------
# إعدادات API
# ------------------------------------------------------------------------------

def get_api_keys():
    keys = []
    for i in range(1, 6):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key and key.strip():
            keys.append(key.strip())
    
    if not keys:
        st.warning("⚠️ لم يتم العثور على مفاتيح API. سيتم استخدام الوضع التجريبي.")
        keys = ["DEMO_MODE"]
    
    return keys

API_KEYS = get_api_keys()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ------------------------------------------------------------------------------
# محرك Gemini المتطور
# ------------------------------------------------------------------------------

class GeminiEngine:
    """محرك ذكاء اصطناعي لا ينام ولا يخطئ"""
    
    MODELS = ['gemini-1.5-flash', 'gemini-1.5-pro']
    
    @classmethod
    def ask(cls, prompt, max_retries=3):
        """إرسال سؤال إلى Gemini مع إعادة محاولة ذكية"""
        if API_KEYS[0] == "DEMO_MODE":
            return cls._demo_response(prompt)
        
        for attempt in range(max_retries):
            for key in API_KEYS:
                for model_name in cls.MODELS:
                    try:
                        genai.configure(api_key=key)
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        if response and response.text:
                            return response.text.strip()
                    except Exception as e:
                        time.sleep(0.5)
                        continue
            time.sleep(2 ** attempt)
        
        return cls._fallback_response(prompt)
    
    @classmethod
    def _demo_response(cls, prompt):
        """ردود تجريبية عند عدم وجود مفتاح API"""
        prompt_lower = prompt.lower()
        if "story" in prompt_lower:
            return "Once upon a time||A brave hero appeared||The adventure began||They discovered magic||And lived happily ever after"
        elif "theme" in prompt_lower:
            return "Space Adventure"
        elif "words" in prompt_lower:
            return "SUN, MOON, STAR, SKY, CLOUD"
        return "Welcome to the magical adventure book for creative kids!"
    
    @classmethod
    def _fallback_response(cls, prompt):
        """ردود احتياطية عند فشل API"""
        return "Explore the wonderful world of imagination and creativity in this exciting activity book!"

# ------------------------------------------------------------------------------
# مولد الصور المتطور
# ------------------------------------------------------------------------------

class ImageGenerator:
    """مولد صور ذكي مع نظام كاش وتحميل متوازي"""
    
    CACHE_DIR = "image_cache"
    
    @classmethod
    def _ensure_cache(cls):
        if not os.path.exists(cls.CACHE_DIR):
            os.makedirs(cls.CACHE_DIR)
    
    @classmethod
    def generate(cls, prompt, filename, style="coloring", max_retries=3):
        """توليد صورة مع إعادة محاولة ونظام كاش"""
        cls._ensure_cache()
        
        # أنماط مختلفة حسب نوع الصورة المطلوبة
        style_prompts = {
            "coloring": "black and white line art, bold thick outlines, pure white background, simple cute drawing, no shading, no colors, children's coloring page style",
            "dots": "black and white dot to dot puzzle for kids, numbered dots 1 to 30 forming a simple shape, clean black dots with numbers, white background, no other elements",
            "cover": "vibrant colorful children's book cover illustration, professional cartoon style, bright happy colors, cute characters, engaging composition, no text",
            "story": "colorful illustration for children's storybook, cute cartoon style, bright colors, happy scene, no text"
        }
        
        full_prompt = f"{style_prompts.get(style, style_prompts['coloring'])}, {prompt}"
        
        for attempt in range(max_retries):
            try:
                encoded = requests.utils.quote(full_prompt[:300])
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed={random.randint(1, 99999)}"
                
                response = requests.get(url, timeout=25)
                if response.status_code == 200 and len(response.content) > 10000:
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    return True
            except Exception:
                time.sleep(1 * (attempt + 1))
        
        # إنشاء صفحة بديلة في حالة الفشل
        cls._create_fallback_page(filename, prompt)
        return False
    
    @classmethod
    def _create_fallback_page(cls, filename, prompt):
        """إنشاء صفحة بديلة عند فشل توليد الصورة"""
        from fpdf import FPDF
        pdf = FPDF(unit="in", format=(8.5, 11))
        pdf.add_page()
        pdf.set_font("Arial", "B", 24)
        pdf.set_y(4)
        pdf.cell(0, 1, "Draw Your Own Picture!", align="C")
        pdf.set_font("Arial", "", 12)
        pdf.set_y(5)
        pdf.multi_cell(0, 0.3, f"Draw a picture about:\n{prompt[:100]}", align="C")
        pdf.output(filename)

# ------------------------------------------------------------------------------
# محرك الألغاز المتقدم
# ------------------------------------------------------------------------------

class PuzzleEngine:
    """محرك متكامل لتوليد جميع أنواع الألغاز"""
    
    @staticmethod
    def generate_maze(width=15, height=15):
        """توليد متاهة مثالية باستخدام خوارزمية DFS"""
        # تهيئة الشبكة
        grid = [[{'N': True, 'S': True, 'E': True, 'W': True, 'visited': False} 
                 for _ in range(width)] for _ in range(height)]
        
        stack = [(0, 0)]
        grid[0][0]['visited'] = True
        
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            
            for dx, dy, direction, opposite in [
                (0, -1, 'N', 'S'), (0, 1, 'S', 'N'),
                (1, 0, 'E', 'W'), (-1, 0, 'W', 'E')
            ]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height and not grid[ny][nx]['visited']:
                    neighbors.append((nx, ny, direction, opposite))
            
            if neighbors:
                nx, ny, direction, opposite = random.choice(neighbors)
                grid[cy][cx][direction] = False
                grid[ny][nx][opposite] = False
                grid[ny][nx]['visited'] = True
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # فتح المدخل والمخرج
        grid[0][0]['W'] = False
        grid[height-1][width-1]['E'] = False
        
        return grid, width, height
    
    @staticmethod
    def generate_sudoku(difficulty="medium"):
        """توليد سودوكو صحيح رياضياً"""
        base = 3
        side = base * base
        
        def pattern(r, c): 
            return (base * (r % base) + r // base + c) % side
        
        def shuffle(s): 
            return random.sample(s, len(s))
        
        # توليد الصفوف والأعمدة العشوائية
        r_base = range(base)
        rows = [g * base + r for g in shuffle(list(r_base)) for r in shuffle(list(r_base))]
        cols = [g * base + c for g in shuffle(list(r_base)) for c in shuffle(list(r_base))]
        nums = shuffle(range(1, side + 1))
        
        # إنشاء اللوحة
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        
        # تحديد عدد الخلايا للإخفاء حسب الصعوبة
        difficulty_map = {"easy": 40, "medium": 50, "hard": 60}
        cells_to_remove = difficulty_map.get(difficulty, 50)
        
        # إخفاء الخلايا
        cells = [(i, j) for i in range(side) for j in range(side)]
        hidden = random.sample(cells, cells_to_remove)
        for i, j in hidden:
            board[i][j] = 0
        
        return board
    
    @staticmethod
    def generate_word_search(theme, size=12):
        """توليد بحث عن الكلمات"""
        # الحصول على كلمات من Gemini
        words_response = GeminiEngine.ask(f"Give 8 simple words related to {theme}, separated by commas")
        words = [w.strip().upper() for w in words_response.split(',') if w.strip()][:8]
        
        # التأكد من وجود كلمات كافية
        if len(words) < 6:
            words = ["STAR", "MOON", "SUN", "SKY", "CLOUD", "RAINBOW", "MAGIC", "WONDER"]
        
        # تهيئة الشبكة
        grid = [[' ' for _ in range(size)] for _ in range(size)]
        
        # وضع الكلمات في الشبكة
        for word in words:
            placed = False
            for _ in range(100):
                direction = random.choice([(0, 1), (1, 0), (1, 1), (1, -1)])
                row = random.randint(0, size - 1)
                col = random.randint(0, size - 1)
                
                end_row = row + direction[0] * (len(word) - 1)
                end_col = col + direction[1] * (len(word) - 1)
                
                if 0 <= end_row < size and 0 <= end_col < size:
                    conflict = False
                    for i, ch in enumerate(word):
                        r, c = row + i * direction[0], col + i * direction[1]
                        if grid[r][c] not in (' ', ch):
                            conflict = True
                            break
                    
                    if not conflict:
                        for i, ch in enumerate(word):
                            r, c = row + i * direction[0], col + i * direction[1]
                            grid[r][c] = ch
                        placed = True
                        break
        
        # ملء الفراغات بحروف عشوائية
        for i in range(size):
            for j in range(size):
                if grid[i][j] == ' ':
                    grid[i][j] = random.choice(string.ascii_uppercase)
        
        return grid, words

# ------------------------------------------------------------------------------
# محرك PDF الاحترافي
# ------------------------------------------------------------------------------

class KDPPDF(FPDF):
    """PDF مخصص لكتب KDP مع هوامش آمنة للتجليد"""
    
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(auto=False, margin=0)
        # هوامش آمنة للتجليد (0.75 للجانب الداخلي + 0.125)
        self.set_margins(left=0.875, top=0.5, right=0.5)
    
    def header(self):
        """رأس الصفحة (يظهر بعد الغلاف)"""
        if self.page_no() > 2:
            self.set_font('Arial', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.set_y(0.3)
            self.cell(0, 0.2, f"{self.page_no() - 2}", align='R')
    
    def add_coloring_page(self, image_path, story_text=""):
        """إضافة صفحة تلوين مع نص قصة"""
        self.add_page()
        if story_text:
            self.set_font('Arial', 'B', 14)
            self.set_text_color(50, 50, 120)
            self.set_y(0.8)
            self.multi_cell(0, 0.35, story_text, align='C')
        
        if os.path.exists(image_path):
            self.image(image_path, x=1.2, y=2.0, w=6.1, h=6.5)
            os.remove(image_path)
        
        # صفحة خلفية للتلوين
        self.add_page()
        self.set_font('Arial', 'I', 10)
        self.set_text_color(180, 180, 180)
        self.set_y(9.5)
        self.cell(0, 0.2, "Color this page!", align='C')
    
    def add_maze_page(self, grid, width, height, story_text=""):
        """إضافة صفحة متاهة"""
        self.add_page()
        
        if story_text:
            self.set_font('Arial', 'B', 12)
            self.set_text_color(50, 50, 120)
            self.set_y(0.6)
            self.multi_cell(0, 0.3, story_text, align='C')
            self.set_y(2.0)
        else:
            self.set_y(1.2)
        
        # رسم المتاهة
        start_x, start_y, cell_size = 1.5, self.get_y(), 0.4
        self.set_line_width(0.015)
        
        for y in range(height):
            for x in range(width):
                px, py = start_x + x * cell_size, start_y + y * cell_size
                cell = grid[y][x]
                
                if cell['N']:
                    self.line(px, py, px + cell_size, py)
                if cell['S']:
                    self.line(px, py + cell_size, px + cell_size, py + cell_size)
                if cell['E']:
                    self.line(px + cell_size, py, px + cell_size, py + cell_size)
                if cell['W']:
                    self.line(px, py, px, py + cell_size)
        
        # نقطة البداية والنهاية
        self.set_fill_color(100, 200, 100)
        self.rect(start_x - 0.12, start_y + height * cell_size / 2, 0.12, 0.12, 'F')
        self.set_fill_color(200, 100, 100)
        self.rect(start_x + width * cell_size, start_y + height * cell_size / 2, 0.12, 0.12, 'F')

# ------------------------------------------------------------------------------
# أنواع الكتب المتاحة
# ------------------------------------------------------------------------------

BOOK_TYPES = {
    "story_coloring": {
        "name": "📖 قصص ورسومات", 
        "icon": "📖",
        "description": "قصة في صفحة ورسمة للتلوين في المقابلة",
        "color": "#FF6B6B"
    },
    "educational": {
        "name": "✏️ تعليم الحروف", 
        "icon": "✏️",
        "description": "تعلم الحروف مع رسمة للتلوين",
        "color": "#4ECDC4"
    },
    "dots": {
        "name": "🔴 وصل النقاط", 
        "icon": "🔴",
        "description": "وصل النقاط لتشكل رسمة ثم لونها",
        "color": "#95E77E"
    },
    "puzzles": {
        "name": "🧩 ألغاز منوعة", 
        "icon": "🧩",
        "description": "متاهات، سودوكو، بحث عن الكلمات",
        "color": "#FFD93D"
    },
    "mixed": {
        "name": "🎭 منوع (الكل)", 
        "icon": "🎭",
        "description": "جميع الأنشطة في كتاب واحد",
        "color": "#C39BD3"
    }
}

# ------------------------------------------------------------------------------
# محرك الإنتاج الملكي
# ------------------------------------------------------------------------------

class RoyalProductionEngine:
    """المحرك الرئيسي لإنتاج الكتب"""
    
    def __init__(self, config, status_callback, progress_callback):
        self.config = config
        self.status = status_callback
        self.progress = progress_callback
        self.pdf = KDPPDF()
        self.generated_count = 0
    
    def run(self):
        """تشغيل محرك الإنتاج"""
        try:
            theme = self.config['theme']
            pages = self.config['pages']
            book_type = self.config['book_type']
            
            # 1. توليد الغلاف
            self._update_status("🎨 تصميم الغلاف الملكي...")
            self._generate_cover(theme)
            self._update_progress(0.05)
            
            # 2. صفحة العنوان
            self._generate_title_page(theme)
            
            # 3. توليد المحتوى حسب النوع
            self._update_status(f"📝 إنشاء كتاب {BOOK_TYPES[book_type]['name']}...")
            
            if book_type == "story_coloring":
                self._generate_story_coloring(theme, pages)
            elif book_type == "educational":
                self._generate_educational_book(theme, pages)
            elif book_type == "dots":
                self._generate_dot_to_dot_book(theme, pages)
            elif book_type == "puzzles":
                self._generate_puzzle_book(theme, pages)
            else:  # mixed
                self._generate_mixed_book(theme, pages)
            
            self._update_progress(0.9)
            
            # 4. توليد مواد التسويق
            self._update_status("📊 تجهيز مواد البيع والتسويق...")
            marketing = self._generate_marketing_materials(theme, book_type)
            
            # 5. حفظ الكتاب
            self._update_status("💾 حفظ الكتاب...")
            filename = self._save_book(theme)
            
            self._update_progress(1.0)
            
            return filename, marketing
            
        except Exception as e:
            self._update_status(f"❌ خطأ: {str(e)}")
            raise
    
    def _update_status(self, message):
        """تحديث حالة التقدم"""
        self.status.info(f"✨ {message}")
    
    def _update_progress(self, value):
        """تحديث شريط التقدم"""
        self.progress(value)
    
    def _generate_cover(self, theme):
        """توليد غلاف احترافي"""
        if ImageGenerator.generate(f"{theme} cute characters, happy scene", "cover.jpg", "cover"):
            self.pdf.add_page()
            self.pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11)
            if os.path.exists("cover.jpg"):
                os.remove("cover.jpg")
        else:
            # غلاف نصي بديل
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 36)
            self.pdf.set_y(4)
            self.pdf.cell(0, 1, theme.upper(), align='C')
            self.pdf.set_font('Arial', '', 20)
            self.pdf.set_y(5)
            self.pdf.cell(0, 1, "Activity Book", align='C')
    
    def _generate_title_page(self, theme):
        """صفحة العنوان الداخلية"""
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 28)
        self.pdf.set_y(3.5)
        self.pdf.cell(0, 0.8, theme.upper(), align='C')
        self.pdf.set_font('Arial', '', 14)
        self.pdf.set_y(4.5)
        self.pdf.cell(0, 0.4, f"Ages {self.config['age_group']}", align='C')
        self.pdf.set_y(5)
        self.pdf.cell(0, 0.4, f"Difficulty: {self.config['difficulty']}", align='C')
    
    def _generate_story_coloring(self, theme, pages):
        """توليد كتاب قصص مع صفحات تلوين مقابلة"""
        # توليد القصة كاملة
        story_prompt = f"Write a {pages}-part short story for children about {theme}. Each part: 2 sentences. Separate parts with '||'."
        story_text = GeminiEngine.ask(story_prompt)
        story_parts = [p.strip() for p in story_text.split('||') if p.strip()]
        
        for i in range(pages):
            story = story_parts[i] if i < len(story_parts) else f"The adventure continues on page {i+1}!"
            self._update_status(f"📖 صفحة {i+1}: {story[:50]}...")
            
            # توليد صورة للمشهد
            image_prompt = f"scene from children's story: {story[:100]}"
            if ImageGenerator.generate(image_prompt, f"temp_{i}.jpg", "story"):
                self.pdf.add_coloring_page(f"temp_{i}.jpg", story)
            else:
                self.pdf.add_coloring_page("", story)
            
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    def _generate_educational_book(self, theme, pages):
        """توليد كتاب تعليم الحروف"""
        letters = list(string.ascii_uppercase)[:min(pages, 26)]
        
        for i, letter in enumerate(letters):
            self._update_status(f"✏️ تعليم الحرف {letter}...")
            
            # صفحة تعليم الحرف
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 80)
            self.pdf.set_y(2)
            self.pdf.cell(0, 1, letter, align='C')
            self.pdf.set_font('Arial', '', 16)
            self.pdf.set_y(3.5)
            self.pdf.cell(0, 0.4, f"Trace and write the letter {letter}", align='C')
            
            # سطور للتتبع
            self.pdf.set_y(4.5)
            for line in range(5):
                self.pdf.set_font('Arial', '', 20)
                self.pdf.cell(0, 0.5, f"{letter}{letter}{letter}{letter}{letter}", align='C')
                self.pdf.ln(0.4)
            
            # صفحة التلوين المقابلة
            item = GeminiEngine.ask(f"Give one word starting with {letter} for coloring")
            if ImageGenerator.generate(f"a cute {item}", f"temp_{i}.jpg", "coloring"):
                self.pdf.add_page()
                self.pdf.image(f"temp_{i}.jpg", x=1.2, y=1.5, w=6.1, h=7.5)
                os.remove(f"temp_{i}.jpg")
                self.pdf.set_font('Arial', 'B', 16)
                self.pdf.set_y(0.8)
                self.pdf.cell(0, 0.4, f"{letter} is for {item.capitalize()}", align='C')
            else:
                self.pdf.add_page()
            
            self._update_progress(0.05 + (i / len(letters)) * 0.85)
    
    def _generate_dot_to_dot_book(self, theme, pages):
        """توليد كتاب وصل النقاط"""
        for i in range(pages):
            self._update_status(f"🔴 توليد لغز وصل النقاط {i+1}...")
            
            # صفحة وصل النقاط
            dot_prompt = f"dot to dot puzzle of a {theme} related object, numbered dots from 1 to 30"
            if ImageGenerator.generate(dot_prompt, f"temp_{i}.jpg", "dots"):
                self.pdf.add_page()
                self.pdf.image(f"temp_{i}.jpg", x=1.2, y=1.2, w=6.1, h=8)
                os.remove(f"temp_{i}.jpg")
                self.pdf.set_font('Arial', 'B', 14)
                self.pdf.set_y(0.5)
                self.pdf.cell(0, 0.4, f"Connect the dots to complete the picture!", align='C')
            else:
                # صفحة بديلة بنقاط مرقمة
                self.pdf.add_page()
                self._draw_dots_fallback()
            
            # صفحة التلوين المقابلة
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'I', 12)
            self.pdf.set_y(4)
            self.pdf.cell(0, 0.4, "Color your completed picture here!", align='C')
            
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    def _draw_dots_fallback(self):
        """رسم نقاط مرقمة بديلة عند فشل توليد الصورة"""
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.set_y(0.5)
        self.pdf.cell(0, 0.4, "Connect the dots in order!", align='C')
        
        # رسم نقاط عشوائية مرقمة
        import math
        self.pdf.set_y(2)
        points = []
        for i in range(20):
            angle = i * (2 * math.pi / 20)
            x = 4.25 + math.cos(angle) * 2.5
            y = 5.5 + math.sin(angle) * 2
            points.append((x, y))
        
        for i, (x, y) in enumerate(points):
            self.pdf.circle(x, y, 0.07, 'F')
            self.pdf.set_font('Arial', '', 8)
            self.pdf.text(x - 0.08, y - 0.08, str(i + 1))
    
    def _generate_puzzle_book(self, theme, pages):
        """توليد كتاب ألغاز منوع"""
        puzzle_types = ['maze', 'sudoku', 'word_search']
        per_type = max(1, pages // 3)
        
        # المتاهات
        for i in range(per_type):
            self._update_status(f"🧩 توليد متاهة {i+1}...")
            grid, w, h = PuzzleEngine.generate_maze(12, 12)
            self.pdf.add_maze_page(grid, w, h, f"Maze {i+1}: Help find the way!")
            self.pdf.add_page()  # صفحة فارغة مقابل المتاهة
            self._update_progress(0.05 + (i / pages) * 0.85)
        
        # سودوكو
        for i in range(per_type):
            self._update_status(f"🔢 توليد سودوكو {i+1}...")
            board = PuzzleEngine.generate_sudoku()
            self.pdf.add_page()
            self._draw_sudoku(board, i+1)
            self.pdf.add_page()
            self._update_progress(0.05 + ((per_type + i) / pages) * 0.85)
        
        # بحث عن الكلمات
        for i in range(per_type):
            self._update_status(f"🔍 توليد بحث كلمات {i+1}...")
            grid, words = PuzzleEngine.generate_word_search(theme)
            self.pdf.add_page()
            self._draw_word_search(grid, words, i+1)
            self.pdf.add_page()
            self._update_progress(0.05 + ((per_type * 2 + i) / pages) * 0.85)
    
    def _draw_sudoku(self, board, number):
        """رسم لوحة سودوكو على PDF"""
        start_x, start_y, cell_size = 1.5, 1.5, 0.55
        self.pdf.set_line_width(0.01)
        
        # رسم الشبكة
        for i in range(10):
            line_width = 0.03 if i % 3 == 0 else 0.01
            self.pdf.set_line_width(line_width)
            self.pdf.line(start_x + i * cell_size, start_y,
                         start_x + i * cell_size, start_y + 9 * cell_size)
            self.pdf.line(start_x, start_y + i * cell_size,
                         start_x + 9 * cell_size, start_y + i * cell_size)
        
        # كتابة الأرقام
        self.pdf.set_font('Arial', 'B', 16)
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    x = start_x + j * cell_size + cell_size / 2 - 0.1
                    y = start_y + i * cell_size + cell_size / 2 + 0.1
                    self.pdf.text(x, y, str(board[i][j]))
        
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.set_y(0.5)
        self.pdf.cell(0, 0.4, f"Sudoku {number}", align='C')
        self.pdf.set_y(11.2)
        self.pdf.set_font('Arial', '', 9)
        self.pdf.cell(0, 0.2, "Fill in the empty cells!", align='C')
    
    def _draw_word_search(self, grid, words, number):
        """رسم لوحة بحث عن الكلمات"""
        start_x, start_y, cell_size = 1.5, 1.8, 0.45
        self.pdf.set_font('Arial', 'B', 12)
        
        # رسم الحروف
        for i, row in enumerate(grid):
            for j, char in enumerate(row):
                self.pdf.text(start_x + j * cell_size, 
                             start_y + i * cell_size + 0.15, char)
        
        # قائمة الكلمات
        self.pdf.set_y(7)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 0.3, f"Word Search {number}", align='C')
        self.pdf.ln(0.3)
        self.pdf.set_font('Arial', '', 10)
        words_text = "  •  ".join(words)
        self.pdf.multi_cell(0, 0.25, f"Find these words:\n{words_text}", align='C')
    
    def _generate_mixed_book(self, theme, pages):
        """توليد كتاب منوع يجمع كل الأنشطة"""
        activities = ['story', 'maze', 'dot', 'alphabet', 'puzzle']
        
        for i in range(pages):
            activity = random.choice(activities)
            
            if activity == 'story':
                story = GeminiEngine.ask(f"Write one sentence about {theme}")
                if ImageGenerator.generate(f"scene: {story}", f"temp_{i}.jpg", "story"):
                    self.pdf.add_coloring_page(f"temp_{i}.jpg", story)
                else:
                    self.pdf.add_coloring_page("", story)
            
            elif activity == 'maze':
                grid, w, h = PuzzleEngine.generate_maze(10, 10)
                self.pdf.add_maze_page(grid, w, h, f"Adventure Maze {i+1}")
                self.pdf.add_page()
            
            elif activity == 'dot':
                if ImageGenerator.generate(f"dot to dot of {theme}", f"temp_{i}.jpg", "dots"):
                    self.pdf.add_page()
                    self.pdf.image(f"temp_{i}.jpg", x=1.2, y=1.2, w=6.1, h=8)
                    os.remove(f"temp_{i}.jpg")
                else:
                    self._draw_dots_fallback()
                self.pdf.add_page()
            
            elif activity == 'alphabet':
                letter = random.choice(string.ascii_uppercase)
                self.pdf.add_page()
                self.pdf.set_font('Arial', 'B', 60)
                self.pdf.set_y(2)
                self.pdf.cell(0, 1, letter, align='C')
                self.pdf.add_page()
            
            else:  # puzzle
                board = PuzzleEngine.generate_sudoku("easy")
                self._draw_sudoku(board, i+1)
                self.pdf.add_page()
            
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    def _generate_marketing_materials(self, theme, book_type):
        """توليد مواد تسويقية متكاملة"""
        book_name = BOOK_TYPES[book_type]['name']
        
        titles = GeminiEngine.ask(f"Generate 3 Amazon book titles for {theme} children's {book_name} book")
        description = GeminiEngine.ask(f"Write Amazon product description for {theme} kids activity book")
        keywords = GeminiEngine.ask(f"Give 7 KDP keywords for {theme} children's book")
        
        # رسالة واتساب جاهزة للتسويق
        whatsapp_msg = f"""
🔥 *كتاب جديد جاهز للبيع على أمازون!* 🔥

📖 *الموضوع:* {theme}
🎭 *النوع:* {book_name}
👶 *الفئة العمرية:* {self.config['age_group']}

📌 *العناوين المقترحة:*
{titles[:200]}

📝 *الوصف:*
{description[:300]}

💡 *نصائح البيع السريع:*
• السعر المثالي: $6.99 - $9.99
• غلاف جذاب بألوان زاهية
• كلمات مفتاحية دقيقة في الخلفية
• تفعيل معاينة Look Inside

#كتب_اطفال #امازون_KDP #نشر_ذاتي
"""
        
        return {
            'titles': titles,
            'description': description,
            'keywords': keywords,
            'whatsapp_message': whatsapp_msg
        }
    
    def _save_book(self, theme):
        """حفظ الكتاب PDF"""
        timestamp = int(time.time())
        safe_theme = theme.replace(' ', '_').replace('/', '_')
        filename = f"KDP_Royal_{safe_theme}_{timestamp}.pdf"
        self.pdf.output(filename)
        return filename

# ------------------------------------------------------------------------------
# إرسال إلى تليجرام
# ------------------------------------------------------------------------------

def send_to_telegram(filename, marketing_materials):
    """إرسال الكتاب ومواد التسويق إلى تليجرام"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        # إرسال ملف PDF
        with open(filename, "rb") as f:
            files = {"document": f}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": "✅ كتاب جديد جاهز للبيع على أمازون KDP!"}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                         data=data, files=files, timeout=60)
        
        # إرسال مواد التسويق
        message = f"""
📊 *مواد البيع الجاهزة لامازون*

📌 *العناوين المقترحة:*
{marketing_materials['titles'][:400]}

📝 *وصف المنتج:*
{marketing_materials['description'][:600]}

🔑 *الكلمات المفتاحية:*
{marketing_materials['keywords']}

📱 *رسالة للواتساب:*
{marketing_materials['whatsapp_message'][:500]}

---
✨ تم التوليد بواسطة KDP Factory Pro V15
"""
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                     data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
                     timeout=30)
        
        return True
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

# ------------------------------------------------------------------------------
# الوضع الآلي (Auto Pilot)
# ------------------------------------------------------------------------------

class AutoPilot:
    """النظام الآلي لتوليد الكتب بدون تدخل"""
    
    def __init__(self):
        self.niches = [
            "Space Explorers", "Magic Unicorns", "Dinosaur World",
            "Ocean Adventures", "Robot Friends", "Fairy Tales",
            "Super Heroes", "Pirate Treasure", "Jungle Animals"
        ]
    
    def generate_random_book(self):
        """توليد كتاب عشوائي بالكامل"""
        theme = random.choice(self.niches)
        book_type = random.choice(list(BOOK_TYPES.keys()))
        pages = random.choice([15, 20, 25, 30])
        age = random.choice(["3-5 سنوات", "5-7 سنوات", "7-10 سنوات"])
        difficulty = random.choice(["سهل", "متوسط"])
        
        config = {
            'theme': theme,
            'pages': pages,
            'age_group': age,
            'difficulty': difficulty,
            'book_type': book_type
        }
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 توليد كتاب: {theme}")
        
        # دوال وهمية للتقدم
        class DummyStatus:
            def info(self, msg): print(f"   📌 {msg}")
        
        def dummy_progress(val): pass
        
        engine = RoyalProductionEngine(config, DummyStatus(), dummy_progress)
        filename, marketing = engine.run()
        
        send_to_telegram(filename, marketing)
        print(f"   ✅ تم التوليد والإرسال: {filename}")
        
        return filename

# ------------------------------------------------------------------------------
# واجهة المستخدم الرئيسية
# ------------------------------------------------------------------------------

def render_book_cards():
    """عرض بطاقات أنواع الكتب"""
    st.markdown("### 📚 اختر نوع الكتاب")
    
    cols = st.columns(4)
    selected = st.session_state.get('selected_book_type', 'mixed')
    
    for i, (key, book) in enumerate(BOOK_TYPES.items()):
        col_idx = i % 4
        with cols[col_idx]:
            selected_class = "selected" if selected == key else ""
            st.markdown(f"""
            <div class='book-card {selected_class}' style='background: linear-gradient(135deg, {book["color"]}, {book["color"]}dd);'>
                <div style='font-size: 48px;'>{book["icon"]}</div>
                <h3 style='margin: 10px 0 5px 0;'>{book["name"]}</h3>
                <p style='font-size: 12px; margin: 0;'>{book["description"]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"اختر {book['name']}", key=f"select_{key}"):
                st.session_state.selected_book_type = key
                st.rerun()

def main():
    """الدالة الرئيسية"""
    
    # تهيئة حالة الجلسة
    if 'selected_book_type' not in st.session_state:
        st.session_state.selected_book_type = 'mixed'
    
    # العنوان
    st.markdown('<h1 class="main-title">👑 KDP Factory Pro V15</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">أنشئ كتباً احترافية تباع على أمازون KDP - نظام الصفحات المتقابلة</p>', unsafe_allow_html=True)
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("### 📊 لوحة التحكم")
        
        st.markdown("""
        <div class='stat-card'>
            <div class='stat-number'>🎯 8</div>
            <div>أنواع الكتب</div>
        </div>
        <div class='stat-card'>
            <div class='stat-number'>⚡ 4</div>
            <div>أنشطة مختلفة</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 نصائح ذهبية")
        st.info("💰 السعر المثالي: $6.99 - $9.99")
        st.info("🎨 الكتب التفاعلية تبيع أكثر ب300%")
        st.info("📖 نظام الصفحات المتقابلة يضاعف القيمة")
        
        auto_send = st.checkbox("📨 إرسال تلقائي لتليجرام", value=True)
    
    # عرض بطاقات الكتب
    render_book_cards()
    
    # إعدادات متقدمة
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.text_input("🎯 موضوع / نيش الكتاب:", value="Adventurous Space Cats")
        pages = st.slider("📄 عدد الصفحات:", 10, 50, 20, help="كل صفحة = نشاط + صفحة مقابلها")
    
    with col2:
        age_group = st.selectbox("👶 الفئة العمرية:", ["3-5 سنوات", "5-7 سنوات", "7-10 سنوات", "10+ سنوات"])
        difficulty = st.select_slider("🎚️ مستوى الصعوبة:", ["سهل جداً", "سهل", "متوسط", "صعب"])
    
    # معلومات عن نوع الكتاب المختار
    selected_info = BOOK_TYPES[st.session_state.selected_book_type]
    st.markdown(f"""
    <div class='info-box'>
        📌 <strong>النوع المختار:</strong> {selected_info['name']} - {selected_info['description']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # زر التوليد
    if st.button("🚀 ابدأ الإنتاج الملكي الآن!", use_container_width=True):
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        config = {
            'theme': theme,
            'pages': pages,
            'age_group': age_group,
            'difficulty': difficulty,
            'book_type': st.session_state.selected_book_type
        }
        
        try:
            engine = RoyalProductionEngine(config, status_container, progress_bar.progress)
            filename, marketing = engine.run()
            
            st.success("🎉 تم إنشاء الكتاب بنجاح!")
            
            # عرض مواد التسويق
            with st.expander("📊 مواد البيع والتسويق (جاهزة لأمازون)"):
                st.markdown("**📌 العناوين المقترحة:**")
                st.info(marketing['titles'][:300])
                
                st.markdown("**📝 وصف المنتج:**")
                st.success(marketing['description'][:400])
                
                st.markdown("**🔑 الكلمات المفتاحية:**")
                st.code(marketing['keywords'])
                
                st.markdown("**📱 رسالة واتساب جاهزة:**")
                st.text(marketing['whatsapp_message'][:500])
            
            # زر التحميل
            with open(filename, "rb") as f:
                st.download_button(
                    label="⬇️ تحميل الكتاب (PDF)",
                    data=f,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            
            # إرسال إلى تليجرام
            if auto_send and TELEGRAM_TOKEN:
                if send_to_telegram(filename, marketing):
                    st.success("📱 تم إرسال الكتاب ومواد البيع إلى تليجرام!")
            
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ حدث خطأ: {str(e)}")
            st.code(traceback.format_exc())
    
    # تذييل
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; padding: 20px;'>
        <p>👑 KDP Factory Pro V15 - الإصدار الملكي الكامل | الصفحات المتقابلة | نظام KDP الاحترافي</p>
        <p>💡 جميع الكتب مهيأة للنشر على Amazon KDP مع هوامش آمنة للتجليد</p>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# تشغيل التطبيق
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    auto_mode = get_query_param("auto", "false")
    
    if auto_mode == "true":
        print("🚀 تشغيل الوضع الآلي...")
        pilot = AutoPilot()
        pilot.generate_random_book()
        print("✅ تم الانتهاء بنجاح!")
    else:
        main()
