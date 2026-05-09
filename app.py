"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║         KDP FACTORY PRO V16 - الإصدار الملهم (بناءً على 20 فكرة عبقرية)       ║
║                              تصميم: إروين سميث                                ║
║                                                                               ║
║  📚 أفضل 10 أنواع كتب تم استلهامها من أفكارك:                                 ║
║  ✓ المحقق الصغير (قصة + ألغاز + أدلة + تلوين)                                ║
║  ✓ الهروب من المتاهة (مغامرة + متاهات + قرارات)                              ║
║  ✓ تعلم وارسم (تعليم + tracing + تلوين + وصل نقاط)                          ║
║  ✓ قصتي الخاصة (قصة مخصصة باسم الطفل)                                        ║
║  ✓ لون ثم ابحث (تلوين + Hidden Objects)                                      ║
║  ✓ الكوميكس التفاعلي (اختيارات + نهايات متعددة)                              ║
║  ✓ رحلة عبر الزمن (قصة + تعليم تاريخي + ألعاب)                              ║
║  ✓ أكاديمية السحرة (تعلم + نظام تطور + رتب)                                  ║
║  ✓ صيد الكنوز (خريطة + ألغاز + تجميع رموز)                                  ║
║  ✓ من نقطة إلى عالم (وصل نقاط + قصة متسلسلة)                                ║
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
import hashlib

# ------------------------------------------------------------------------------
# إعدادات الواجهة
# ------------------------------------------------------------------------------

st.set_page_config(
    page_title="KDP Factory Pro V16 | مصنع الكتب التفاعلية",
    page_icon="🔍",
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
        min-height: 180px;
    }
    
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    .book-card.selected {
        border: 2px solid #ffd700;
        box-shadow: 0 0 20px rgba(255,215,0,0.5);
    }
    
    .book-icon {
        font-size: 48px;
        margin-bottom: 10px;
    }
    
    .book-name {
        font-size: 18px;
        font-weight: bold;
        margin: 10px 0 5px 0;
    }
    
    .book-desc {
        font-size: 11px;
        opacity: 0.9;
    }
    
    .book-tag {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 3px 8px;
        font-size: 10px;
        margin: 5px 3px;
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
        font-size: 28px;
        font-weight: bold;
        color: #667eea;
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
    
    .info-box {
        background: #e8f4f8;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-right: 4px solid #4ecdc4;
    }
    
    .style-chip {
        display: inline-block;
        background: #667eea;
        color: white;
        border-radius: 20px;
        padding: 5px 15px;
        margin: 3px;
        cursor: pointer;
        font-size: 13px;
    }
    
    .style-chip.selected {
        background: #ffd700;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# إعدادات API والأمان
# ------------------------------------------------------------------------------

def get_api_keys():
    keys = []
    for i in range(1, 6):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key and key.strip():
            keys.append(key.strip())
    
    if not keys:
        keys = ["DEMO_MODE"]
    
    return keys

API_KEYS = get_api_keys()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ------------------------------------------------------------------------------
# دالة مساعدة لقراءة معلمات URL
# ------------------------------------------------------------------------------

def get_query_param(key, default=None):
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
# محرك Gemini
# ------------------------------------------------------------------------------

class GeminiEngine:
    MODELS = ['gemini-1.5-flash', 'gemini-1.5-pro']
    
    @classmethod
    def ask(cls, prompt, max_retries=2):
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
                    except:
                        continue
            time.sleep(1)
        
        return cls._demo_response(prompt)
    
    @classmethod
    def _demo_response(cls, prompt):
        prompt_lower = prompt.lower()
        if "detective" in prompt_lower or "mystery" in prompt_lower:
            return "The missing cookie mystery||Someone took the golden cookie||The detective found crumbs near the window||The culprit was the little mouse!"
        elif "story" in prompt_lower:
            return "Once upon a time, in a magical land||A brave hero appeared||Together they saved the day"
        elif "clue" in prompt_lower:
            return "crumbs, footprint, missing object, suspicious shadow"
        else:
            return "Welcome to the amazing adventure book!"

# ------------------------------------------------------------------------------
# مولد الصور
# ------------------------------------------------------------------------------

class ImageGenerator:
    @staticmethod
    def generate(prompt, filename, style="illustration", max_retries=2):
        style_map = {
            "illustration": "colorful children's book illustration, cute cartoon style",
            "coloring": "black and white line art, bold thick outlines, white background",
            "dots": "black and white dot to dot puzzle, numbered dots 1-30",
            "hidden": "black and white hidden objects puzzle, items to find hidden in scene"
        }
        
        full_prompt = f"{style_map.get(style, style_map['illustration'])}, {prompt}"
        
        for attempt in range(max_retries):
            try:
                encoded = requests.utils.quote(full_prompt[:300])
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    with open(filename, "wb") as f:
                        f.write(resp.content)
                    return True
            except:
                pass
            time.sleep(1)
        return False

# ------------------------------------------------------------------------------
# أنواع الكتب الجديدة (المستلهمة من أفكارك)
# ------------------------------------------------------------------------------

BOOK_TYPES = {
    "detective": {
        "name": "🕵️ المحقق الصغير",
        "icon": "🕵️",
        "description": "قصة + ألغاز + أدلة + تلوين - حل الجريمة بنفسك!",
        "color": "#1a1a2e",
        "tags": ["قصة", "ألغاز", "أدلة", "تلوين", "تشويق"],
        "age": "5-10"
    },
    "maze_escape": {
        "name": "🏃 الهروب من المتاهة",
        "icon": "🏃",
        "description": "مغامرة + متاهات + قرارات - هل ستنجح في الهروب؟",
        "color": "#2d6a4f",
        "tags": ["متاهات", "مغامرة", "قرارات", "RPG"],
        "age": "6-12"
    },
    "learn_draw": {
        "name": "✏️ تعلم وارسم",
        "icon": "✏️",
        "description": "تعليم + تتبع + تلوين + وصل نقاط",
        "color": "#ff6b6b",
        "tags": ["تعليم", "تتبع", "رسم", "حروف"],
        "age": "3-7"
    },
    "my_story": {
        "name": "📖 قصتي الخاصة",
        "icon": "📖",
        "description": "قصة مخصصة باسم الطفل واختياراته",
        "color": "#f08c00",
        "tags": ["تخصيص", "قصة", "إبداع"],
        "age": "4-10"
    },
    "color_find": {
        "name": "🔍 لون ثم ابحث",
        "icon": "🔍",
        "description": "تلوين ثم اكتشاف عناصر مخفية",
        "color": "#9b59b6",
        "tags": ["تلوين", "بحث", "تركيز"],
        "age": "4-8"
    },
    "interactive_comics": {
        "name": "🎭 كوميكس تفاعلي",
        "icon": "🎭",
        "description": "قصص مصورة + اختيارات + نهايات متعددة",
        "color": "#e74c3c",
        "tags": ["كوميكس", "اختيارات", "مغامرة"],
        "age": "7-12"
    },
    "time_travel": {
        "name": "⏰ رحلة عبر الزمن",
        "icon": "⏰",
        "description": "قصة + معلومات تاريخية + ألعاب",
        "color": "#3b82f6",
        "tags": ["تاريخ", "تعليم", "مغامرة"],
        "age": "7-12"
    },
    "wizard_academy": {
        "name": "🧙 أكاديمية السحرة",
        "icon": "🧙",
        "description": "تعلم + ألعاب + نظام تطور ورتب سحرية",
        "color": "#8b5cf6",
        "tags": ["سحر", "تطور", "ألغاز", "رتب"],
        "age": "6-11"
    },
    "treasure_hunt": {
        "name": "🗺️ صيد الكنوز",
        "icon": "🗺️",
        "description": "خريطة + ألغاز + تجميع رموز لفتح الكنز",
        "color": "#d97706",
        "tags": ["كنز", "خريطة", "ألغاز", "مغامرة"],
        "age": "5-10"
    },
    "dots_to_world": {
        "name": "🔴 من نقطة إلى عالم",
        "icon": "🔴",
        "description": "وصل النقاط + قصة تتكشف تدريجياً",
        "color": "#10b981",
        "tags": ["وصل نقاط", "قصة", "رسم"],
        "age": "3-7"
    }
}

# ------------------------------------------------------------------------------
# أنماط الكتاب (Styles)
# ------------------------------------------------------------------------------

BOOK_STYLES = {
    "cozy": {"name": "☕ دافيء", "color": "#f5e6ca", "desc": "أجواء منزلية دافئة"},
    "fantasy": {"name": "🐉 فانتازيا", "color": "#e0d4ff", "desc": "عوالم خيالية وسحر"},
    "space": {"name": "🚀 فضائي", "color": "#1a1a3e", "desc": "مغامرات في الفضاء"},
    "cute": {"name": "🌸 كيوت", "color": "#ffd1dc", "desc": "رسوم لطيفة وجميلة"},
    "educational": {"name": "📚 تعليمي", "color": "#c8e6df", "desc": "تركيز على التعلم"},
    "adventure": {"name": "⚔️ مغامرة", "color": "#f4a460", "desc": "أكشن وإثارة"},
    "mystery": {"name": "🔍 غامض", "color": "#2c3e50", "desc": "ألغاز وتشويق"},
    "islamic": {"name": "🕌 إسلامي", "color": "#2e7d64", "desc": "قصص إسلامية هادفة"}
}

# ------------------------------------------------------------------------------
# محرك PDF المتقدم
# ------------------------------------------------------------------------------

class KDPPDF(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(auto=False, margin=0)
        self.set_margins(left=0.875, top=0.5, right=0.5)
    
    def add_story_page(self, text, image_path=None):
        """صفحة قصة مع رسم توضيحي"""
        self.add_page()
        self.set_font('Arial', 'B', 14)
        self.set_text_color(50, 50, 120)
        self.set_y(0.8)
        self.multi_cell(0, 0.35, text, align='C')
        
        if image_path and os.path.exists(image_path):
            self.image(image_path, x=1.2, y=2.5, w=6.1, h=5)
            os.remove(image_path)
    
    def add_puzzle_page(self, puzzle_type, content):
        """صفحة ألغاز متنوعة"""
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.set_y(0.5)
        self.cell(0, 0.4, f"🔍 {puzzle_type}", align='C')
        self.ln(0.5)
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 0.25, content, align='C')
    
    def add_clue_page(self, clues):
        """صفحة جمع الأدلة"""
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.set_y(0.5)
        self.cell(0, 0.4, "🔎 اجمع الأدلة", align='C')
        self.ln(0.5)
        self.set_font('Arial', '', 12)
        for clue in clues:
            self.cell(0, 0.3, f"• {clue}", ln=True)
    
    def add_choice_page(self, choices, page_refs):
        """صفحة اختيارات للكوميكس التفاعلي"""
        self.add_page()
        self.set_font('Arial', 'B', 14)
        self.set_y(1)
        self.cell(0, 0.4, "🎭 ماذا تختار؟", align='C')
        self.ln(0.5)
        self.set_font('Arial', '', 12)
        for i, (choice, target) in enumerate(zip(choices, page_refs)):
            self.cell(0, 0.35, f"{i+1}. {choice} → اذهب إلى الصفحة {target}", ln=True)
    
    def add_treasure_map(self, clues_collected):
        """صفحة خريطة الكنز"""
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.set_y(0.5)
        self.cell(0, 0.4, "🗺️ خريطة الكنز", align='C')
        self.ln(0.5)
        self.set_font('Arial', '', 12)
        
        # رسم خريطة بسيطة
        self.set_draw_color(100, 80, 50)
        self.set_line_width(0.02)
        
        # مسار متعرج كخريطة
        self.line(2, 3, 3, 4)
        self.line(3, 4, 2.5, 5)
        self.line(2.5, 5, 4, 5.5)
        self.line(4, 5.5, 5, 5)
        self.line(5, 5, 6, 6)
        
        # X علامة الكنز
        self.set_text_color(200, 0, 0)
        self.set_font('Arial', 'B', 20)
        self.text(5.8, 6.2, "X")
        
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 10)
        self.set_y(7)
        self.cell(0, 0.3, f"الأدلة التي جمعتها: {len(clues_collected)}/5", align='C')
        self.ln(0.2)
        self.cell(0, 0.3, "الرموز السرية: " + "".join(clues_collected), align='C')

# ------------------------------------------------------------------------------
# المحرك الملكي للإنتاج
# ------------------------------------------------------------------------------

class RoyalProductionEngine:
    def __init__(self, config, status_callback, progress_callback):
        self.config = config
        self.status = status_callback
        self.progress = progress_callback
        self.pdf = KDPPDF()
        self.style = config.get('style', 'cozy')
        self.page_count = 0
    
    def _update_status(self, msg):
        self.status.info(f"✨ {msg}")
    
    def _update_progress(self, val):
        self.progress(val)
    
    def run(self):
        theme = self.config['theme']
        pages = self.config['pages']
        book_type = self.config['book_type']
        
        self._update_status("🎨 تصميم الغلاف...")
        self._generate_cover(theme)
        self._update_progress(0.05)
        
        self._update_status(f"📝 إنشاء كتاب {BOOK_TYPES[book_type]['name']}...")
        
        # اختيار المحرك المناسب حسب نوع الكتاب
        engines = {
            "detective": self._generate_detective_book,
            "maze_escape": self._generate_maze_escape,
            "learn_draw": self._generate_learn_draw,
            "my_story": self._generate_my_story,
            "color_find": self._generate_color_find,
            "interactive_comics": self._generate_interactive_comics,
            "time_travel": self._generate_time_travel,
            "wizard_academy": self._generate_wizard_academy,
            "treasure_hunt": self._generate_treasure_hunt,
            "dots_to_world": self._generate_dots_to_world
        }
        
        engines.get(book_type, self._generate_detective_book)(theme, pages)
        
        self._update_progress(0.9)
        
        self._update_status("📊 تجهيز مواد التسويق...")
        marketing = self._generate_marketing()
        
        filename = self._save_book(theme)
        self._update_progress(1.0)
        
        return filename, marketing
    
    def _generate_cover(self, theme):
        style_desc = BOOK_STYLES.get(self.style, BOOK_STYLES["cozy"])["desc"]
        prompt = f"{style_desc}, {theme} children's book cover, cute colorful illustration"
        if ImageGenerator.generate(prompt, "cover.jpg", "illustration"):
            self.pdf.add_page()
            self.pdf.image("cover.jpg", x=0, y=0, w=8.5, h=11)
            os.remove("cover.jpg")
        else:
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 36)
            self.pdf.set_y(4)
            self.pdf.cell(0, 1, theme.upper(), align='C')
    
    # ============= كتاب 1: المحقق الصغير =============
    def _generate_detective_book(self, theme, pages):
        """قصة + ألغاز + أدلة + تلوين"""
        story = GeminiEngine.ask(f"Write a {pages//3}-part detective story about {theme}. Each part: 2-3 sentences.")
        parts = [p.strip() for p in story.split('||') if p.strip()]
        
        for i in range(min(pages, len(parts) * 3)):
            part_idx = i // 3
            if part_idx < len(parts):
                # صفحة قصة
                img_prompt = f"detective scene: {parts[part_idx][:100]}"
                ImageGenerator.generate(img_prompt, f"temp_{i}.jpg", "illustration")
                self.pdf.add_story_page(parts[part_idx], f"temp_{i}.jpg" if i % 3 == 0 else None)
                
                # صفحة لغز
                puzzles = [
                    f"🔍 لغز {i+1}: ابحث عن الدليل المخفي في الصورة السابقة",
                    "🕵️ حل الكود: M Y S T E R Y → ?",
                    "📋 أي من هذه ليس دليلاً؟ أ) بصمة ب) شعر ج) سحابة"
                ]
                self.pdf.add_puzzle_page("لغز تحقيق", puzzles[i % len(puzzles)])
                
                # صفحة أدلة
                clues = GeminiEngine.ask(f"Give 3 clues for {theme} mystery").split(',')
                self.pdf.add_clue_page([c.strip() for c in clues[:3]])
                
                # صفحة تلوين
                self.pdf.add_page()
                if ImageGenerator.generate(f"{theme} coloring page", f"color_{i}.jpg", "coloring"):
                    self.pdf.image(f"color_{i}.jpg", x=1.2, y=1.5, w=6.1, h=7.5)
            
            self._update_progress(0.05 + (i / (pages * 2)) * 0.85)
    
    # ============= كتاب 2: الهروب من المتاهة =============
    def _generate_maze_escape(self, theme, pages):
        """مغامرة + متاهات + قرارات"""
        for i in range(pages):
            story = GeminiEngine.ask(f"Write a short exciting paragraph about escaping {theme}, part {i+1}")
            self.pdf.add_story_page(story[:200])
            
            # صفحة متاهة
            self.pdf.add_page()
            self._draw_simple_maze(i)
            self.pdf.set_font('Arial', 'I', 11)
            self.pdf.set_y(9)
            self.pdf.cell(0, 0.3, f"🧭 المتاهة {i+1}: هل تستطيع إيجاد المخرج؟", align='C')
            
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    def _draw_simple_maze(self, seed):
        random.seed(seed)
        import math
        self.pdf.set_line_width(0.02)
        start_x, start_y, size = 2, 2.5, 0.45
        for y in range(12):
            for x in range(12):
                px, py = start_x + x * size, start_y + y * size
                if random.random() > 0.7:  # جدران عشوائية
                    self.pdf.line(px, py, px + size, py)
                if random.random() > 0.7:
                    self.pdf.line(px, py + size, px + size, py + size)
                if random.random() > 0.7:
                    self.pdf.line(px + size, py, px + size, py + size)
        random.seed()
    
    # ============= كتاب 3: تعلم وارسم =============
    def _generate_learn_draw(self, theme, pages):
        letters = list(string.ascii_uppercase)[:min(pages, 26)]
        for i, letter in enumerate(letters):
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 60)
            self.pdf.set_y(2)
            self.pdf.cell(0, 1, letter, align='C')
            
            # سطور للتتبع
            self.pdf.set_y(4)
            for _ in range(4):
                self.pdf.set_font('Arial', '', 24)
                self.pdf.cell(0, 0.5, f"{letter}{letter}{letter}{letter}", align='C')
                self.pdf.ln(0.4)
            
            # صفحة وصل نقاط
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 14)
            self.pdf.cell(0, 0.4, f"🔴 وصل النقاط لتشكل حرف {letter}", align='C')
            self._draw_dots_circle()
            
            self._update_progress(0.05 + (i / len(letters)) * 0.85)
    
    def _draw_dots_circle(self):
        import math
        self.pdf.set_y(2.5)
        for i in range(20):
            angle = i * (2 * math.pi / 20)
            x = 4.25 + math.cos(angle) * 2
            y = 5.5 + math.sin(angle) * 2
            self.pdf.circle(x, y, 0.07, 'F')
            self.pdf.set_font('Arial', '', 8)
            self.pdf.text(x - 0.07, y - 0.07, str(i + 1))
    
    # ============= كتاب 4: قصتي الخاصة =============
    def _generate_my_story(self, theme, pages):
        child_name = self.config.get('child_name', "بطل القصة")
        for i in range(pages):
            story = GeminiEngine.ask(f"Write a sentence for children's story about {theme}, including name {child_name}")
            story = story.replace("[اسم الطفل]", child_name)
            
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 14)
            self.pdf.set_y(2)
            self.pdf.multi_cell(0, 0.4, story, align='C')
            
            # فراغ للتلوين
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'I', 12)
            self.pdf.set_y(4)
            self.pdf.cell(0, 0.4, "ارسم مشهد القصة هنا:", align='C')
            
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    # ============= كتاب 5: لون ثم ابحث =============
    def _generate_color_find(self, theme, pages):
        for i in range(pages):
            # صفحة تلوين
            if ImageGenerator.generate(f"{theme} scene hidden objects", f"hidden_{i}.jpg", "hidden"):
                self.pdf.add_page()
                self.pdf.image(f"hidden_{i}.jpg", x=1, y=1, w=6.5, h=8.5)
                os.remove(f"hidden_{i}.jpg")
            
            # صفحة البحث عن الأشياء
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 14)
            self.pdf.set_y(0.5)
            self.pdf.cell(0, 0.4, "🔍 ماذا تجد في الرسمة؟", align='C')
            self.pdf.ln(0.8)
            
            items = ["نجمة ⭐", "مفتاح 🔑", "قلب ❤️", "سمكة 🐠", "زهرة 🌸"]
            random.shuffle(items)
            for item in items[:4]:
                self.pdf.cell(0, 0.3, f"□ {item}", ln=True)
            
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    # ============= كتاب 6-10 (مختصرات للتوفير) =============
    def _generate_interactive_comics(self, theme, pages):
        for i in range(min(pages, 10)):
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 14)
            self.pdf.set_y(0.5)
            self.pdf.cell(0, 0.4, f"🎭 صفحة {i+1}", align='C')
            self.pdf.ln(0.5)
            self.pdf.set_font('Arial', '', 11)
            self.pdf.multi_cell(0, 0.3, f"قصة {theme} جزء {i+1}\n\nالخيار 1: اذهب إلى الصفحة {i+3}\nالخيار 2: اذهب إلى الصفحة {i+5}", align='C')
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    def _generate_time_travel(self, theme, pages):
        eras = ["مصر القديمة", "العصور الوسطى", "العصر الحجري", "المستقبل", "الفضاء"]
        for i in range(min(pages, len(eras))):
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 16)
            self.pdf.set_y(0.5)
            self.pdf.cell(0, 0.4, f"⏰ {eras[i]}", align='C')
            self.pdf.ln(0.5)
            self.pdf.set_font('Arial', '', 11)
            self.pdf.multi_cell(0, 0.3, f"هل تعلم؟ في {eras[i]} كان الأطفال يلعبون بشكل مختلف...", align='C')
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    def _generate_wizard_academy(self, theme, pages):
        spells = ["تعويذة النار 🔥", "تعويذة الماء 💧", "تعويذة الرياح 🌬️", "تعويذة الحماية 🛡️"]
        for i in range(min(pages, len(spells))):
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 16)
            self.pdf.set_y(0.5)
            self.pdf.cell(0, 0.4, f"🧙 {spells[i]}", align='C')
            self.pdf.ln(0.5)
            self.pdf.set_font('Arial', '', 11)
            self.pdf.multi_cell(0, 0.3, f"لإتقان {spells[i]}، قم بحل هذا اللغز...\n\n____ السحرة أقوياء!", align='C')
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    def _generate_treasure_hunt(self, theme, pages):
        secrets = []
        for i in range(pages):
            secret = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            secrets.append(secret)
            self.pdf.add_puzzle_page(f"الكنز {i+1}", f"حل اللغز لتحصل على الرمز: ? ? ?\n\nالدليل: ابحث عن الحرف رقم {ord(secret)%10}")
            self._update_progress(0.05 + (i / pages) * 0.85)
        self.pdf.add_treasure_map(secrets)
    
    def _generate_dots_to_world(self, theme, pages):
        for i in range(pages):
            if ImageGenerator.generate(f"{theme} dot to dot", f"dot_{i}.jpg", "dots"):
                self.pdf.add_page()
                self.pdf.image(f"dot_{i}.jpg", x=1, y=1, w=6.5, h=8)
                os.remove(f"dot_{i}.jpg")
                self.pdf.set_font('Arial', 'I', 11)
                self.pdf.set_y(0.5)
                self.pdf.cell(0, 0.3, f"🔴 وصل النقاط {i+1} لتكشف المشهد!", align='C')
            self._update_progress(0.05 + (i / pages) * 0.85)
    
    def _generate_marketing(self):
        book_name = BOOK_TYPES[self.config['book_type']]['name']
        return {
            'titles': f"1. {self.config['theme']} Adventure Book\n2. Fun {book_name}\n3. Kids Activity Collection",
            'description': f"Join the amazing adventure in {self.config['theme']}! This {book_name} includes stories, puzzles, coloring, and more.",
            'keywords': f"{self.config['theme']}, kids book, activity book, {book_name}, children's stories",
            'whatsapp_message': f"🔥 كتاب جديد: {self.config['theme']}\nالنوع: {book_name}\nمناسب للأعمار: {BOOK_TYPES[self.config['book_type']]['age']}\n\nسعر خاص: فقط 7.99$"
        }
    
    def _save_book(self, theme):
        timestamp = int(time.time())
        filename = f"KDP_{self.config['book_type']}_{timestamp}.pdf"
        self.pdf.output(filename)
        return filename

# ------------------------------------------------------------------------------
# إرسال إلى تليجرام
# ------------------------------------------------------------------------------

def send_to_telegram(filename, marketing):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        with open(filename, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                         data={"chat_id": TELEGRAM_CHAT_ID, "caption": "✅ كتاب جديد جاهز للبيع!"},
                         files={"document": f}, timeout=60)
        return True
    except:
        return False

# ------------------------------------------------------------------------------
# الوضع الآلي
# ------------------------------------------------------------------------------

class AutoPilot:
    def generate_random_book(self):
        themes = ["Magic Forest", "Space Journey", "Ocean Adventure", "Dinosaur World"]
        book_type = random.choice(list(BOOK_TYPES.keys()))
        config = {
            'theme': random.choice(themes),
            'pages': random.choice([15, 20, 25]),
            'book_type': book_type,
            'style': random.choice(list(BOOK_STYLES.keys()))
        }
        print(f"🚀 توليد كتاب: {config['theme']} - {BOOK_TYPES[book_type]['name']}")
        engine = RoyalProductionEngine(config, type('Dummy', (), {'info': print}), lambda x: None)
        filename, marketing = engine.run()
        send_to_telegram(filename, marketing)
        return filename

# ------------------------------------------------------------------------------
# واجهة المستخدم
# ------------------------------------------------------------------------------

def main():
    if 'selected_book_type' not in st.session_state:
        st.session_state.selected_book_type = 'detective'
    if 'selected_style' not in st.session_state:
        st.session_state.selected_style = 'cozy'
    
    st.markdown('<h1 class="main-title">🔍 KDP Factory Pro V16</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">أقوى 10 أنواع كتب مستلهمة من أفكار عبقرية - نظام تفاعلي متكامل</p>', unsafe_allow_html=True)
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("### 🎨 أنماط الكتاب")
        style_cols = st.columns(2)
        for i, (key, style) in enumerate(BOOK_STYLES.items()):
            col = style_cols[i % 2]
            selected = "selected" if st.session_state.selected_style == key else ""
            if col.button(f"{style['name']}", key=f"style_{key}"):
                st.session_state.selected_style = key
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 إحصائيات")
        st.markdown(f"**📚 10 أنواع كتب**")
        st.markdown(f"**🎨 {len(BOOK_STYLES)} نمط**")
        st.markdown(f"**⚡ توليد ذكي**")
        
        auto_send = st.checkbox("📨 إرسال لتليجرام", value=True)
    
    # عرض بطاقات الكتب
    st.markdown("### 📚 اختر نوع الكتاب")
    cols = st.columns(3)
    for i, (key, book) in enumerate(BOOK_TYPES.items()):
        col = cols[i % 3]
        with col:
            selected_class = "selected" if st.session_state.selected_book_type == key else ""
            st.markdown(f"""
            <div class='book-card {selected_class}' style='background: linear-gradient(135deg, {book["color"]}, {book["color"]}dd);'>
                <div class='book-icon'>{book["icon"]}</div>
                <div class='book-name'>{book["name"]}</div>
                <div class='book-desc'>{book["description"]}</div>
                <div>
                    {"".join(f'<span class="book-tag">{tag}</span>' for tag in book["tags"][:3])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"اختر", key=f"select_{key}"):
                st.session_state.selected_book_type = key
                st.rerun()
    
    # خيارات متقدمة
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        theme = st.text_input("🎯 موضوع الكتاب:", value="Detective Mystery")
        pages = st.slider("📄 عدد الصفحات:", 10, 40, 20)
    with col2:
        child_name = st.text_input("👦 اسم الطفل (للكتب المخصصة):", value="")
        age_group = st.selectbox("👶 الفئة العمرية:", ["3-5", "5-7", "7-10", "10+"])
    
    # معلومات عن الكتاب المختار
    selected = BOOK_TYPES[st.session_state.selected_book_type]
    style_name = BOOK_STYLES[st.session_state.selected_style]['name']
    st.markdown(f"""
    <div class='info-box'>
        📖 <strong>الكتاب المختار:</strong> {selected['name']} | 🎨 <strong>النمط:</strong> {style_name}<br>
        🏷️ <strong>الوسوم:</strong> {' - '.join(selected['tags'])}<br>
        👶 <strong>العمر المناسب:</strong> {selected['age']} سنة
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 ابدأ الإنتاج الأسطوري", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        config = {
            'theme': theme,
            'pages': pages,
            'book_type': st.session_state.selected_book_type,
            'style': st.session_state.selected_style,
            'child_name': child_name or theme,
            'age_group': age_group
        }
        
        try:
            engine = RoyalProductionEngine(config, status_text, progress_bar.progress)
            filename, marketing = engine.run()
            
            st.success("🎉 تم إنشاء الكتاب بنجاح!")
            
            with st.expander("📊 مواد التسويق"):
                st.info(marketing['titles'])
                st.success(marketing['description'])
                st.code(marketing['keywords'])
            
            with open(filename, "rb") as f:
                st.download_button("⬇️ تحميل الكتاب", f, file_name=filename)
            
            if auto_send and TELEGRAM_TOKEN:
                send_to_telegram(filename, marketing)
                st.success("📱 تم الإرسال إلى تليجرام")
            
            st.balloons()
            
        except Exception as e:
            st.error(f"خطأ: {e}")
            st.code(traceback.format_exc())

# ------------------------------------------------------------------------------
# التشغيل
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    auto_mode = get_query_param("auto", "false")
    if auto_mode == "true":
        print("🚀 تشغيل الوضع الآلي...")
        pilot = AutoPilot()
        pilot.generate_random_book()
        print("✅ تم الانتهاء!")
    else:
        main()
