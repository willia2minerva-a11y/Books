# services/factory_pipeline.py
import os
import asyncio
import time
from sqlalchemy.orm import Session
from core.models import Product
from services.ai_engine import ai_engine
from services.image_generator import image_generator
from services.pdf_builder import ModernKDPBook

class ProductionPipeline:
    """المدير التنفيذي للمصنع: يدير سير العمل من الفكرة إلى الكتاب الجاهز"""
    
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def _get_drawing_items(self, theme: str, count: int) -> list:
        """طلب قائمة بالعناصر التي يجب رسمها من الذكاء الاصطناعي"""
        prompt = f"""
        Return a valid JSON object containing exactly {count} simple, cute items related to the theme '{theme}'.
        Format: {{"items": ["item1", "item2", ...]}}
        """
        # نستخدم دالة _generate_json التي بنيناها مسبقاً
        result = ai_engine._generate_json(prompt, {"items": [f"{theme} concept {i}" for i in range(count)]})
        return result.get("items", [])[:count]

    async def run_coloring_book_pipeline(self, db: Session, theme: str, pages: int):
        """خط إنتاج كتاب التلوين (غير متزامن بالكامل)"""
        
        # 1. تسجيل بدء العمل في قاعدة البيانات
        db_product = Product(
            niche=theme, 
            product_type="كتاب تلوين", 
            status="⚙️ جاري التصنيع..."
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        try:
            timestamp = int(time.time())
            
            # 2. توليد الغلاف والأفكار
            items_to_draw = await self._get_drawing_items(theme, pages)
            
            # تجهيز مهام توليد الصور لمحرك الـ Async
            image_tasks = []
            cover_filename = f"cover_{timestamp}.jpg"
            image_tasks.append((theme, cover_filename, "cover"))
            
            for i, item in enumerate(items_to_draw):
                filename = f"page_{timestamp}_{i}.jpg"
                image_tasks.append((item, filename, "coloring"))
                
            # 3. تشغيل المصنع الصاروخي (جلب كل الصور في نفس الوقت)
            db_product.status = "🎨 جاري توليد الصور..."
            db.commit()
            image_results = await image_generator.generate_batch(image_tasks)
            
            # 4. بناء الـ PDF
            db_product.status = "📖 جاري تجميع الكتاب..."
            db.commit()
            
            book = ModernKDPBook(title=theme)
            
            # إضافة الغلاف إذا تم توليده بنجاح
            cover_path = os.path.join(image_generator.temp_dir, cover_filename)
            book.add_cover(cover_path, theme)
            book.add_copyright_page()
            
            # إضافة صفحات التلوين
            for i, item in enumerate(items_to_draw):
                filename = f"page_{timestamp}_{i}.jpg"
                img_path = os.path.join(image_generator.temp_dir, filename)
                # إذا نجح توليد الصورة، نضيفها
                if image_results.get(filename):
                    book.add_coloring_page(img_path, item)
                    
            # حفظ الملف النهائي
            pdf_filename = f"KDP_{theme.replace(' ', '_')}_{timestamp}.pdf"
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            book.output(pdf_path)
            
            # 5. هندسة التسويق
            db_product.status = "📊 جاري إعداد خطة النشر..."
            db.commit()
            marketing = ai_engine.generate_marketing(theme)
            
            # 6. التحديث النهائي لقاعدة البيانات
            db_product.seo_title = marketing.get("seo_title", "")
            db_product.keywords = marketing.get("keywords", "")
            db_product.description = marketing.get("description", "")
            db_product.tiktok_script = marketing.get("tiktok_script", "")
            db_product.file_path = pdf_path
            db_product.status = "✅ مكتمل"
            db.commit()
            
            return db_product

        except Exception as e:
            db_product.status = f"❌ فشل: {str(e)[:50]}"
            db.commit()
            raise e

pipeline = ProductionPipeline()
