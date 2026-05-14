# core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# استخدام SQLite محلياً. إذا تم وضع رابط قاعدة بيانات في المتغيرات البيئية سيستخدمه فوراً
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./factory_data.sqlite")

# إعداد محرك قاعدة البيانات
# check_same_thread=False ضروري جداً لـ SQLite مع Streamlit
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# مصنع الجلسات للتخاطب مع قاعدة البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# الفئة الأساسية التي سترث منها كل جداولنا
Base = declarative_base()

def get_db():
    """دالة مساعدة لفتح وإغلاق الاتصال بقاعدة البيانات بأمان"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

