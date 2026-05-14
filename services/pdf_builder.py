# services/pdf_builder.py
from fpdf import FPDF
import os
from datetime import datetime

class ModernKDPBook(FPDF):
    """قاعدة الكتاب الرقمي مع دعم كامل للغة العربية (RTL) وتنسيق احترافي"""
    
    def __init__(self, title="KDP Book"):
        # مقاس أمازون القياسي 8.5 * 11 بوصة
        super().__init__(unit="in", format=(8.5, 11))
        self.set_auto_page_break(auto=False)
        self.set_margins(0.5, 0.5, 0.5)
        self.book_title = title
        
        # تحميل الخطوط العربية (تأكد من وجود الملفات في هذا المسار)
        self.font_dir = os.path.join(os.getcwd(), "assets", "fonts")
        self._load_arabic_fonts()

    def _load_arabic_fonts(self):
        """تحميل الخطوط وتفعيل دعم تشكيل الحروف العربية"""
        regular_font = os.path.join(self.font_dir, "Cairo-Regular.ttf")
        bold_font = os.path.join(self.font_dir, "Cairo-Bold.ttf")
        
        # إذا كانت الخطوط موجودة، نضيفها. إذا لم تكن، نستخدم الافتراضي (سيسبب مشاكل بالعربية)
        if os.path.exists(regular_font):
            self.add_font("Cairo", style="", fname=regular_font)
            self.add_font("Cairo", style="B", fname=bold_font)
            self.set_font("Cairo", size=14)
        else:
            self.set_font("Helvetica", size=14)
            print("⚠️ تحذير: لم يتم العثور على خطوط عربية في مجلد assets/fonts/")

    def add_cover(self, image_path: str, title: str):
        """إضافة صفحة غلاف احترافية تملأ الشاشة (Bleed)"""
        self.add_page()
        if os.path.exists(image_path):
            # جعل الصورة تغطي كامل مقاس الصفحة
            self.image(image_path, x=0, y=0, w=8.5, h=11)
        else:
            # غلاف طوارئ في حال فشل توليد الصورة
            self.set_fill_color(30, 30, 40)
            self.rect(0, 0, 8.5, 11, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font("Cairo", "B", 36)
            # استخدام align='C' مع text_shaping لضمان ترتيب الكلمات الصحيح
            self.set_xy(0, 4)
            self.multi_cell(w=8.5, h=0.6, text=title, align="C", text_direction="RTL")
            self.set_text_color(0, 0, 0) # إعادة اللون للأسود للصفحات القادمة

    def add_copyright_page(self, author_name="DevMate Factory"):
        """صفحة حقوق نشر KDP القياسية"""
        self.add_page()
        self.set_font("Cairo", "", 10)
        self.set_xy(1, 9)
        year = datetime.now().year
        copyright_text = f"© {year} {author_name}. جميع الحقوق محفوظة.\nلا يجوز نسخ أو إعادة إنتاج أي جزء من هذا الكتاب."
        self.multi_cell(w=6.5, h=0.3, text=copyright_text, align="C", text_direction="RTL")

    def add_coloring_page(self, image_path: str, item_name: str):
        """صفحة تلوين قياسية لأمازون (صورة في المنتصف مع إطار)"""
        self.add_page()
        
        # عنوان خفيف أعلى الصفحة
        self.set_font("Cairo", "B", 18)
        self.set_xy(0, 0.8)
        self.cell(w=8.5, h=0.5, text=item_name, align="C", text_direction="RTL")
        
        # إطار الصورة (يفضله KDP لكي لا تخرج الألوان)
        self.set_line_width(0.02)
        self.set_draw_color(150, 150, 150)
        self.rect(0.75, 1.5, 7.0, 8.0)
        
        if os.path.exists(image_path):
            self.image(image_path, x=1.0, y=1.75, w=6.5, h=7.5)
        else:
            self.set_font("Cairo", "B", 24)
            self.set_xy(0, 5)
            self.cell(w=8.5, h=1, text="⚠️ تعذر تحميل الصورة", align="C", text_direction="RTL")
            
        # إضافة صفحة فارغة خلفية (مهم جداً في كتب التلوين لكي لا يتسرب الحبر للرسمة التالية)
        self.add_page()

