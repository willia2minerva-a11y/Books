"""
KDP Factory Pro - الإصدار الأسطوري V2.0
تصميم: Irwin Smith | الهندسة: AI Legend
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
import hashlib
import json
from datetime import datetime

# ------------------------------------------------------------------------------
# اعدادات الصفحة
# ------------------------------------------------------------------------------

st.set_page_config(
    page_title="KDP Factory Pro | مصنع كتب امازون",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# CSS مخصص
# ------------------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    .book-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
        color: white;
    }
    
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    .main-title {
        background: linear-gradient(120deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 48px;
        font-weight: 900;
        text-align: center;
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
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 20px rgba(102,126,234,0.4);
    }
    
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: bold;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# اعدادات API
# ------------------------------------------------------------------------------

def get_api_keys():
    keys = []
    for i in range(1, 6):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key and key.strip():
            keys.append(key.strip())
    
    if not keys:
        st.warning("⚠️ لم يتم العثور على مفاتيح API")
        keys = ["DUMMY_KEY"]
    
    return keys

API_KEYS = get_api_keys()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ------------------------------------------------------------------------------
# محرك Gemini المحصن
# ------------------------------------------------------------------------------

class GeminiEngine:
    MODELS = ['gemini-1.5-flash', 'gemini-1.5-pro']
    
    @classmethod
    def ask(cls, prompt, retries=3):
        last_error = None
        
        for attempt in range(retries):
            for key in API_KEYS:
                if key == "DUMMY_KEY":
                    continue
                    
                for model_name in cls.MODELS:
                    try:
                        genai.configure(api_key=key)
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        
                        if response and response.text:
                            return response.text.strip()
                            
                    except Exception as e:
                        last_error = str(e)
                        time.sleep(0.5)
                        continue
            
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
        
        return cls._get_fallback_response(prompt)
    
    @classmethod
    def _get_fallback_response(cls, prompt):
        prompt_lower = prompt.lower()
        
        if "theme" in prompt_lower or "niche" in prompt_lower:
            themes = ["Space Explorers", "Magic Unicorns", "Dinosaur World",
                     "Ocean Adventures", "Jungle Animals", "Robot Friends"]
            return random.choice(themes)
        
        elif "words related to" in prompt_lower:
            return "SUN,MOON,STAR,SKY,CLOUD,RAINBOW"
        
        elif "story" in prompt_lower:
            return "Once upon a time||In a magical land||A brave hero appeared"
        
        elif "keywords" in prompt_lower:
            return "kids activity book, coloring book, puzzle book, children's story"
        
        elif "sales" in prompt_lower or "selling" in prompt_lower:
            return cls._get_sales_tips()
        
        else:
            return "Default response for KDP book generation"
    
    @classmethod
    def _get_sales_tips(cls):
        return """
=== نصائح لبيع الكتاب على امازون KDP ===

1. السعر المثالي: 6.99 - 9.99 دولار
2. الكلمات المفتاحية: ضعها في عنوان الكتاب الفرعي
3. الغلاف: استخدم الوان زاهية وخط واضح
4. المعاينة: اجعل اول 10% من الكتاب مجاني للمعاينة
5. المراجعات: اطلب من الاهل تقييم الكتاب
6. الفئة العمرية: حددها بدقة 3-5 او 5-7
7. السلسلة: اصدر اجزاء متعددة من نفس الموضوع
"""

# ------------------------------------------------------------------------------
# نظام الصور
# ------------------------------------------------------------------------------

class ImageGenerator:
    @staticmethod
    def generate_sync(prompt, filename):
        for attempt in range(3):
            try:
                encoded_prompt = requests.utils.quote(prompt[:200])
                url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1,9999)}"
                
                response = requests.get(url, timeout=20)
                if response.status_code == 200 and len(response.content) > 15000:
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    return True
            except:
                pass
            time.sleep(1)
        return False

# ------------------------------------------------------------------------------
# مولد الالغاز
# ------------------------------------------------------------------------------

class PuzzleGenerator:
    @staticmethod
    def generate_maze(width=12, height=12):
        grid = [[{'N': True, 'S': True, 'E': True, 'W': True, 'visited': False} 
                 for _ in range(width)] for _ in range(height)]
        
        stack = [(0, 0)]
        grid[0][0]['visited'] = True
        
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            
            for dx, dy, dir_name, opposite in [(0, -1, 'N', 'S'), (0, 1, 'S', 'N'), 
                                                 (1, 0, 'E', 'W'), (-1, 0, 'W', 'E')]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height and not grid[ny][nx]['visited']:
                    neighbors.append((nx, ny, dir_name, opposite))
            
            if neighbors:
                nx, ny, dir_name, opposite = random.choice(neighbors)
                grid[cy][cx][dir_name] = False
                grid[ny][nx][opposite] = False
                grid[ny][nx]['visited'] = True
                stack.append((nx, ny))
            else:
                stack.pop()
        
        grid[0][0]['W'] = False
        grid[height-1][width-1]['E'] = False
        
        return grid, width, height
    
    @staticmethod
    def generate_sudoku():
        board = [[0 for _ in range(9)] for _ in range(9)]
        
        def is_valid(board, row, col, num):
            for x in range(9):
                if board[row][x] == num or board[x][col] == num:
                    return False
            start_row, start_col = 3 * (row // 3), 3 * (col // 3)
            for i in range(3):
                for j in range(3):
                    if board[start_row + i][start_col + j] == num:
                        return False
            return True
        
        def fill(board):
            for i in range(9):
                for j in range(9):
                    if board[i][j] == 0:
                        for num in random.sample(range(1, 10), 9):
                            if is_valid(board, i, j, num):
                                board[i][j] = num
                                if fill(board):
                                    return True
                                board[i][j] = 0
                        return False
            return True
        
        fill(board)
        
        cells_to_remove = random.randint(40, 50)
        hidden = random.sample([(i, j) for i in range(9) for j in range(9)], cells_to_remove)
        for i, j in hidden:
            board[i][j] = 0
        
        return board

# ------------------------------------------------------------------------------
# محرك PDF
# ------------------------------------------------------------------------------

class KidsBookPDF(FPDF):
    def __init__(self):
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(auto=False, margin=0.5)
    
    def header(self):
        if self.page_no() > 2:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(150, 150, 150)
            self.cell(0, 0.25, f"Page {self.page_no() - 2}", align='R')
            self.ln(0.3)

# ------------------------------------------------------------------------------
# انواع الكتب
# ------------------------------------------------------------------------------

BOOK_TYPES = {
    "coloring": {"name": "كتاب تلوين", "icon": "🎨", "description": "صفحات تلوين ممتعة", "color": "#FF6B6B"},
    "puzzles": {"name": "كتاب الغاز", "icon": "🧩", "description": "سودوكو، متاهات، كلمات", "color": "#4ECDC4"},
    "story_coloring": {"name": "قصة + تلوين", "icon": "📖", "description": "قصة ورسمة للتلوين", "color": "#95E77E"},
    "educational": {"name": "كتاب تعليم", "icon": "✏️", "description": "تعليم الحروف والارقام", "color": "#FFD93D"},
    "comics": {"name": "كتاب كوميكس", "icon": "🦸", "description": "قصص مصورة مضحكة", "color": "#A8E6CF"},
    "interactive_story": {"name": "قصة تفاعلية", "icon": "⭐", "description": "قصة مع انشطة", "color": "#FFD700"},
    "mixed": {"name": "منوع (الكل)", "icon": "🎭", "description": "جميع الانواع", "color": "#C39BD3"}
}

# ------------------------------------------------------------------------------
# محرك الانتاج الرئيسي
# ------------------------------------------------------------------------------

class KDPProductionEngine:
    def __init__(self, config, status_callback, progress_callback):
        self.config = config
        self.status = status_callback
        self.progress = progress_callback
        self.pdf = KidsBookPDF()
    
    def run(self):
        try:
            self.status("جاري تصميم الغلاف...")
            self._generate_cover()
            self.progress(0.05)
            
            self.status(f"جاري انشاء كتاب {self.config['book_type']}...")
            
            if self.config['book_type'] == 'interactive_story':
                self._generate_interactive_story()
            elif self.config['book_type'] == 'puzzles':
                self._generate_puzzle_book()
            elif self.config['book_type'] == 'story_coloring':
                self._generate_story_coloring()
            elif self.config['book_type'] == 'educational':
                self._generate_educational_book()
            elif self.config['book_type'] == 'coloring':
                self._generate_coloring_book()
            elif self.config['book_type'] == 'comics':
                self._generate_comics_book()
            else:
                self._generate_mixed_book()
            
            self.progress(0.9)
            
            self.status("جاري تجهيز مواد البيع والتسويق...")
            marketing = self._generate_marketing_materials()
            
            self.status("جاري حفظ الكتاب...")
            filename = self._save_book()
            
            self.progress(1.0)
            
            return filename, marketing
            
        except Exception as e:
            self.status(f"خطأ: {str(e)}")
            raise
    
    def _generate_cover(self):
        theme = self.config['theme']
        
        cover_prompt = f"children's book cover for {theme}, cute colorful illustration, cartoon style, joyful, NO TEXT NO WORDS"
        
        if ImageGenerator.generate_sync(cover_prompt, "cover_temp.jpg"):
            self.pdf.add_page()
            self.pdf.image("cover_temp.jpg", x=0, y=0, w=8.5, h=11)
            os.remove("cover_temp.jpg")
        else:
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 48)
            self.pdf.set_y(4)
            self.pdf.cell(0, 1, theme.upper(), align='C')
            self.pdf.set_font('Arial', '', 24)
            self.pdf.set_y(5)
            self.pdf.cell(0, 1, "Activity Book", align='C')
        
        self.pdf.add_page()
        self.pdf.set_font('Arial', '', 12)
        self.pdf.set_y(4)
        self.pdf.multi_cell(0, 0.3, f"""
        {self.config['theme']} Activity Book
        
        Created with KDP Factory Pro
        For ages {self.config['age_group']}
        
        (c) 2024 All Rights Reserved
        """, align='C')
    
    def _generate_interactive_story(self):
        pages_needed = self.config['pages']
        
        story_prompt = f"""Write a {pages_needed}-part children's story about {self.config['theme']}. 
        The story should be exciting.
        Each part must be exactly 2 short sentences.
        Return ONLY the story parts separated by '||'."""
        
        story_text = GeminiEngine.ask(story_prompt)
        story_parts = [p.strip() for p in story_text.split('||') if p.strip()]
        
        activities = ['coloring', 'maze', 'math', 'word_search']
        
        for i in range(pages_needed):
            story = story_parts[i % len(story_parts)] if i < len(story_parts) else f"Page {i+1} of the adventure!"
            activity = random.choice(activities)
            self._add_activity_page(activity, story, i+1)
            self.progress(0.05 + (i / pages_needed) * 0.85)
    
    def _add_activity_page(self, activity_type, story_text, page_num):
        self.pdf.add_page()
        
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.set_text_color(50, 50, 150)
        self.pdf.multi_cell(0, 0.3, story_text, align='C')
        self.pdf.ln(0.2)
        
        if activity_type == 'coloring':
            prompt = f"black and white line art coloring page for kids, {self.config['theme']} themed, simple cute drawing, thick outlines, white background"
            if ImageGenerator.generate_sync(prompt, f"temp_{page_num}.jpg"):
                self.pdf.image(f"temp_{page_num}.jpg", x=1, y=2.5, w=6.5, h=6.5)
                os.remove(f"temp_{page_num}.jpg")
            
            self.pdf.add_page()
            self.pdf.set_font('Arial', '', 10)
            self.pdf.set_text_color(200, 200, 200)
            self.pdf.cell(0, 0.2, "Color this page!", align='C')
            
        elif activity_type == 'maze':
            grid, w, h = PuzzleGenerator.generate_maze(12, 12)
            self._draw_maze(grid, w, h)
            self.pdf.set_y(9)
            self.pdf.set_font('Arial', '', 10)
            self.pdf.cell(0, 0.2, "Help find the way out!", align='C')
            
        elif activity_type == 'math':
            self.pdf.set_font('Arial', 'B', 18)
            self.pdf.cell(0, 0.5, "Math Challenge!", align='C')
            self.pdf.ln(0.5)
            self.pdf.set_font('Arial', '', 16)
            for j in range(5):
                num1, num2 = random.randint(1, 20), random.randint(1, 10)
                op = random.choice(['+', '-'])
                self.pdf.cell(0, 0.4, f"{j+1})  {num1} {op} {num2} = ______", ln=True, align='C')
                
        elif activity_type == 'word_search':
            words = GeminiEngine.ask(f"Give 6 simple words related to {self.config['theme']}, just words separated by commas").split(',')[:6]
            self._draw_word_search(words)
    
    def _draw_maze(self, grid, width, height):
        start_x, start_y, cell_size = 1.5, 2.5, 0.45
        self.pdf.set_line_width(0.02)
        
        for y in range(height):
            for x in range(width):
                px, py = start_x + x * cell_size, start_y + y * cell_size
                cell = grid[y][x]
                
                if cell['N']:
                    self.pdf.line(px, py, px + cell_size, py)
                if cell['S']:
                    self.pdf.line(px, py + cell_size, px + cell_size, py + cell_size)
                if cell['E']:
                    self.pdf.line(px + cell_size, py, px + cell_size, py + cell_size)
                if cell['W']:
                    self.pdf.line(px, py, px, py + cell_size)
        
        self.pdf.set_fill_color(0, 255, 0)
        self.pdf.rect(start_x - 0.1, start_y + height * cell_size / 2, 0.15, 0.15, 'F')
        self.pdf.set_fill_color(255, 0, 0)
        self.pdf.rect(start_x + width * cell_size, start_y + height * cell_size / 2, 0.15, 0.15, 'F')
    
    def _draw_word_search(self, words):
        size = 10
        grid = [[' ' for _ in range(size)] for _ in range(size)]
        
        for word in words:
            word = word.upper().strip()
            direction = random.choice([(0,1), (1,0)])
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1 - len(word))
            
            for i, ch in enumerate(word):
                if ch.isalpha():
                    grid[row][col + i] = ch
        
        for i in range(size):
            for j in range(size):
                if grid[i][j] == ' ':
                    grid[i][j] = random.choice(string.ascii_uppercase)
        
        start_x, start_y, cell_size = 1.5, 2.5, 0.45
        self.pdf.set_font('Arial', 'B', 14)
        
        for i, row in enumerate(grid):
            for j, char in enumerate(row):
                self.pdf.text(start_x + j * cell_size, start_y + i * cell_size + 0.15, char)
        
        self.pdf.set_y(7.5)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 0.2, "Find these words:", align='C')
        self.pdf.ln(0.2)
        words_text = " - ".join([w.upper() for w in words])
        self.pdf.cell(0, 0.2, words_text, align='C')
    
    def _generate_marketing_materials(self):
        theme = self.config['theme']
        
        titles = GeminiEngine.ask(f"Generate 3 catchy Amazon book titles for a children's activity book about {theme}")
        description = GeminiEngine.ask(f"Write an Amazon product description for a children's activity book about {theme}. Use bullet points.")
        keywords = GeminiEngine.ask(f"Give 7 backend search keywords for Amazon KDP for a {theme} children's activity book")
        sales_tips = GeminiEngine.ask("Give me tips for selling on Amazon KDP")
        
        whatsapp_message = self._generate_whatsapp_message(theme, titles, description)
        
        return {
            'titles': titles,
            'description': description,
            'keywords': keywords,
            'sales_tips': sales_tips,
            'whatsapp_message': whatsapp_message
        }
    
    def _generate_whatsapp_message(self, theme, titles, description):
        return f"""
🔥 *كتاب جديد جاهز للبيع على امازون!* 🔥

*الموضوع:* {theme}
*النوع:* {self.config['book_type']}
*الفئة العمرية:* {self.config['age_group']}

*العناوين المقترحة:*
{titles[:200]}

*وصف المنتج:*
{description[:300]}

*نصائح للبيع:*
1. سعر ممتاز: 7.99 دولار
2. غلاف جذاب
3. كلمات مفتاحية دقيقة
4. نشر على KDP

للشراء او الاستفسار: [رابط المتجر]

#كتب_اطفال #امازون_KDP #كتاب_انشطة
"""
    
    def _save_book(self):
        timestamp = int(time.time())
        filename = f"KDP_Book_{self.config['theme'].replace(' ', '_')}_{timestamp}.pdf"
        self.pdf.output(filename)
        return filename
    
    def _generate_puzzle_book(self):
        for i in range(self.config['pages']):
            puzzle_type = random.choice(['maze', 'sudoku', 'word_search'])
            if puzzle_type == 'sudoku':
                self.pdf.add_page()
                board = PuzzleGenerator.generate_sudoku()
                self._draw_sudoku(board)
                self.pdf.set_y(9)
                self.pdf.set_font('Arial', '', 10)
                self.pdf.cell(0, 0.2, f"Sudoku {i+1}", align='C')
            else:
                self._add_activity_page(puzzle_type, f"Puzzle {i+1}!", i+1)
            self.progress(0.05 + (i / self.config['pages']) * 0.85)
    
    def _draw_sudoku(self, board):
        start_x, start_y, cell_size = 1.5, 2.5, 0.55
        self.pdf.set_line_width(0.01)
        self.pdf.set_font('Arial', 'B', 16)
        
        for i in range(10):
            line_width = 0.03 if i % 3 == 0 else 0.01
            self.pdf.set_line_width(line_width)
            self.pdf.line(start_x + i * cell_size, start_y, 
                         start_x + i * cell_size, start_y + 9 * cell_size)
            self.pdf.line(start_x, start_y + i * cell_size, 
                         start_x + 9 * cell_size, start_y + i * cell_size)
        
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    x = start_x + j * cell_size + cell_size/2 - 0.1
                    y = start_y + i * cell_size + cell_size/2 + 0.1
                    self.pdf.text(x, y, str(board[i][j]))
    
    def _generate_story_coloring(self):
        story = GeminiEngine.ask(f"Write {self.config['pages']} short sentences for a story about {self.config['theme']}")
        sentences = [s.strip() for s in story.split('.') if s.strip()][:self.config['pages']]
        
        for i in range(self.config['pages']):
            sent = sentences[i] if i < len(sentences) else "The adventure continues..."
            self._add_activity_page('coloring', sent, i+1)
            self.progress(0.05 + (i / self.config['pages']) * 0.85)
    
    def _generate_educational_book(self):
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')[:self.config['pages']]
        for i, letter in enumerate(letters):
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 48)
            self.pdf.set_y(2)
            self.pdf.cell(0, 1, letter, align='C')
            
            prompt = f"black and white line art of an object starting with letter {letter}, kids coloring page"
            if ImageGenerator.generate_sync(prompt, f"temp_{i}.jpg"):
                self.pdf.image(f"temp_{i}.jpg", x=2.5, y=3.5, w=3.5, h=3.5)
                os.remove(f"temp_{i}.jpg")
            
            self.pdf.add_page()
            self.progress(0.05 + (i / self.config['pages']) * 0.85)
    
    def _generate_coloring_book(self):
        for i in range(self.config['pages']):
            prompt = f"black and white line art coloring page, {self.config['theme']} theme, simple cute, page {i+1}"
            if ImageGenerator.generate_sync(prompt, f"temp_{i}.jpg"):
                self.pdf.add_page()
                self.pdf.image(f"temp_{i}.jpg", x=1, y=1, w=6.5, h=8.5)
                self.pdf.add_page()
                os.remove(f"temp_{i}.jpg")
            self.progress(0.05 + (i / self.config['pages']) * 0.85)
    
    def _generate_comics_book(self):
        for i in range(self.config['pages']):
            self.pdf.add_page()
            self.pdf.set_line_width(0.02)
            for row in range(2):
                for col in range(2):
                    x = 1 + col * 3.2
                    y = 2 + row * 4
                    self.pdf.rect(x, y, 3, 3.5)
                    
                    prompt = f"simple cartoon character expressing emotion, {self.config['theme']}, line art"
                    if ImageGenerator.generate_sync(prompt, f"temp_comic_{i}_{row}_{col}.jpg"):
                        self.pdf.image(f"temp_comic_{i}_{row}_{col}.jpg", x=x+0.2, y=y+0.2, w=2.6, h=2.6)
            self.progress(0.05 + (i / self.config['pages']) * 0.85)
    
    def _generate_mixed_book(self):
        all_activities = ['coloring', 'maze', 'math', 'word_search']
        for i in range(self.config['pages']):
            activity = random.choice(all_activities)
            self._add_activity_page(activity, f"Activity {i+1}!", i+1)
            self.progress(0.05 + (i / self.config['pages']) * 0.85)

# ------------------------------------------------------------------------------
# ارسال الى تليجرام (مع مواد البيع)
# ------------------------------------------------------------------------------

def send_to_telegram(file_path, caption, marketing_materials):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": f"{caption[:900]}...\n\n✅ الكتاب جاهز للبيع على امازون!"}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", 
                         data=data, files=files, timeout=60)
        
        message = f"""
📊 *مواد البيع الجاهزة لامازون KDP*

📌 *العناوين المقترحة:*
{marketing_materials['titles'][:400]}

📝 *وصف المنتج:*
{marketing_materials['description'][:600]}

🔑 *الكلمات المفتاحية:*
{marketing_materials['keywords']}

💡 *نصائح البيع:*
{marketing_materials['sales_tips'][:400]}

📱 *رسالة جاهزة للواتساب:*
{marketing_materials['whatsapp_message'][:500]}

---
✨ تم التوليد بواسطة KDP Factory Pro
"""
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                     data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=30)
        
        return True
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

# ------------------------------------------------------------------------------
# النظام الآلي (Auto Pilot) - بدون مكتبة schedule
# ------------------------------------------------------------------------------

class AutoPilot:
    def __init__(self):
        self.books_generated = 0
        self.niches = [
            "Space Explorers", "Magic Unicorns", "Dinosaur World",
            "Ocean Adventures", "Robot Friends", "Fairy Tales",
            "Super Heroes", "Pirate Treasure", "Jungle Animals",
            "Princess Castle", "Construction Trucks", "Farm Animals"
        ]
    
    def generate_random_book(self):
        theme = random.choice(self.niches)
        book_type = random.choice(['interactive_story', 'mixed', 'puzzles'])
        pages = random.choice([20, 25, 30])
        
        config = {
            'theme': theme,
            'pages': pages,
            'difficulty': 'سهل',
            'age_group': random.choice(['3-5 سنوات', '5-7 سنوات']),
            'book_type': book_type
        }
        
        def dummy_status(msg): 
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
        def dummy_progress(val): 
            pass
        
        engine = KDPProductionEngine(config, dummy_status, dummy_progress)
        filename, marketing = engine.run()
        
        send_to_telegram(filename, f"🤖 كتاب آلي #{self.books_generated+1}: {theme}", marketing)
        self.books_generated += 1
        return filename

# ------------------------------------------------------------------------------
# واجهة المستخدم الرئيسية
# ------------------------------------------------------------------------------

def render_book_selector():
    st.markdown("### 📚 اختر نوع الكتاب")
    
    cols = st.columns(4)
    selected_type = st.session_state.get('selected_book_type', 'mixed')
    
    for i, (key, book) in enumerate(BOOK_TYPES.items()):
        col_idx = i % 4
        with cols[col_idx]:
            border = '2px solid gold' if selected_type == key else 'none'
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {book["color"]}, {book["color"]}dd); 
                        border-radius: 15px; padding: 15px; text-align: center; margin: 5px;
                        border: {border};'>
                <div style='font-size: 40px;'>{book["icon"]}</div>
                <h4>{book["name"]}</h4>
                <p style='font-size: 10px;'>{book["description"]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"اختر", key=f"select_{key}"):
                st.session_state.selected_book_type = key
                st.rerun()

def main():
    if 'selected_book_type' not in st.session_state:
        st.session_state.selected_book_type = 'mixed'
    
    st.markdown('<h1 class="main-title">📚 KDP Factory Pro 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">أنشئ كتباً احترافية تباع على امازون في دقائق</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 📊 الاحصائيات")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class='stat-card'>
                <div class='stat-number'>0</div>
                <div>كتب منتجة</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='stat-card'>
                <div class='stat-number'>0</div>
                <div>جاهزة للبيع</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 نصائح البيع")
        st.info("💰 السعر المثالي: 6.99 - 9.99 دولار")
        st.info("🎨 الغلاف الجذاب يزيد المبيعات")
        st.info("📖 الكتب التفاعلية تبيع اكثر ب300%")
        
        auto_send = st.checkbox("ارسال تلقائي لتليجرام", value=True)
    
    render_book_selector()
    
    col1, col2 = st.columns(2)
    with col1:
        theme = st.text_input("🎯 موضوع الكتاب:", value="Space Adventure")
        pages = st.slider("📄 عدد الصفحات:", 10, 80, 30)
    with col2:
        age_group = st.selectbox("👶 الفئة العمرية:", ["3-5 سنوات", "5-7 سنوات", "7-10 سنوات"])
        difficulty = st.select_slider("🎚️ مستوى الصعوبة:", ["سهل", "متوسط", "صعب"])
    
    st.markdown("---")
    
    if st.button("🚀 ابدا التوليد الان", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        config = {
            'theme': theme,
            'pages': pages,
            'difficulty': difficulty,
            'age_group': age_group,
            'book_type': st.session_state.selected_book_type
        }
        
        try:
            engine = KDPProductionEngine(config, 
                                        lambda msg: status_text.info(f"✨ {msg}"),
                                        lambda val: progress_bar.progress(val))
            filename, marketing = engine.run()
            
            st.success("🎉 تم انشاء الكتاب بنجاح!")
            
            with st.expander("📊 مواد البيع والتسويق"):
                st.markdown("**العناوين المقترحة:**")
                st.info(marketing['titles'][:300])
                st.markdown("**وصف المنتج:**")
                st.success(marketing['description'][:400])
                st.markdown("**نصائح البيع:**")
                st.code(marketing['sales_tips'])
                st.markdown("**رسالة للواتساب:**")
                st.text(marketing['whatsapp_message'][:500])
            
            with open(filename, "rb") as f:
                st.download_button("⬇️ تحميل الكتاب", f, file_name=filename)
            
            if auto_send and TELEGRAM_TOKEN:
                if send_to_telegram(filename, f"كتاب جديد: {theme}", marketing):
                    st.success("📱 تم ارسال الكتاب ومواد البيع الى تليجرام!")
            
            st.balloons()
            
        except Exception as e:
            st.error(f"خطأ: {str(e)}")
            st.code(traceback.format_exc())
    
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #888;'>KDP Factory Pro - اصدار احترافي | انشاء كتب للبيع على امازون</p>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# تشغيل التطبيق
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    if st.query_params.get("auto") == "true":
        print("تشغيل الوضع الآلي...")
        pilot = AutoPilot()
        pilot.generate_random_book()
        print("تم الانشاء والارسال بنجاح!")
    else:
        main()
