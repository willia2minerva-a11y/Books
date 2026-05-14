# core/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    niche = Column(String(255), nullable=False)           # اسم النيش (مثال: قطط نينجا)
    product_type = Column(String(100), nullable=False)    # نوع المنتج (كتاب تلوين، بطاقات...)
    status = Column(String(50), default="⏳ قيد الانتظار") # حالة الإنتاج
    
    # معلومات التسويق
    seo_title = Column(String(255), nullable=True)
    keywords = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    tiktok_script = Column(Text, nullable=True)
    
    # مسار الملف و التوقيت
    file_path = Column(String(500), nullable=True)
    telegram_status = Column(String(100), default="لم يُرسل")
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(50), nullable=False) # INFO, ERROR, WARNING
    message = Column(Text, nullable=False)
    source = Column(String(100), nullable=False) # مصدر الخطأ (AI, PDF, Telegram)
    created_at = Column(DateTime, default=datetime.utcnow)

