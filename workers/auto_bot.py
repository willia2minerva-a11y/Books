# workers/auto_bot.py
import asyncio
import os
import sys
from datetime import datetime

# إضافة مسار المشروع الجذري لكي يتعرف بايثون على مجلدات core و services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.blocking import BlockingScheduler
from core.database import SessionLocal, Base, engine
from services.factory_pipeline import pipeline
from services.ai_engine import ai_engine
from services.telegram_ops import telegram_dispatcher

# التأكد من إنشاء قاعدة البيانات والجداول قبل بدء البوت
Base.metadata.create_all(bind=engine)

async def async_job():
    """المهمة غير المتزامنة التي تقوم بكل العمل"""
    db = SessionLocal()
    try:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🤖 البوت استيقظ! جاري البحث عن نيش مربح...")
        
        # 1. اصطياد نيش عشوائي
        theme = ai_engine.generate_niche()
        print(f"🎯 النيش المستهدف: {theme}")
        
        # 2. تشغيل المصنع
        product = await pipeline.run_coloring_book_pipeline(db, theme, pages=20)
        
        # 3. الشحن والتوصيل (تيليجرام)
        print("📦 جاري إرسال الحزمة إلى تيليجرام...")
        success = await telegram_dispatcher.send_launch_package(product)
        
        if success:
            product.telegram_status = "✅ تم الإرسال"
            print("🚀 تم الإرسال بنجاح!")
        else:
            product.telegram_status = "❌ فشل الإرسال"
            print("⚠️ فشل الإرسال لتيليجرام. (تأكد من الـ Token والـ Chat ID)")
            
        db.commit()
            
    except Exception as e:
        print(f"❌ حدث خطأ في البوت: {e}")
    finally:
        db.close()

def scheduled_job():
    """غلاف (Wrapper) لتشغيل الدالة غير المتزامنة داخل المجدول"""
    asyncio.run(async_job())

if __name__ == "__main__":
    # تشغيل المهمة فوراً عند بدء السكربت للتجربة
    scheduled_job() 
    
    # إعداد المجدول ليعمل كل X دقيقة (مثلاً كل 60 دقيقة)
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_job, 'interval', minutes=60)
    
    print("\n🟢 عامل الخلفية يعمل الآن. في وضع الانتظار للجدول الزمني...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🔴 تم إيقاف البوت.")

