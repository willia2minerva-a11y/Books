# app.py
import streamlit as st
import asyncio
from core.database import SessionLocal, engine, Base
from core.models import Product
from services.factory_pipeline import pipeline
from services.telegram_ops import telegram_dispatcher

# ضمان إنشاء الجداول
Base.metadata.create_all(bind=engine)

st.set_page_config(page_title="لوحة تحكم المصنع", page_icon="🏭", layout="wide")

# تصميم بسيط باستخدام CSS
st.markdown("""
<style>
    * { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .status-badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def main():
    st.title("🏭 مصنع الأصول الرقمية (DevMate Edition)")
    
    db = get_db()
    
    # الشريط الجانبي (التحكم اليدوي)
    with st.sidebar:
        st.header("⚙️ الإدارة اليدوية")
        st.info("💡 يمكنك إجبار المصنع على إنتاج كتاب محدد فوراً.")
        
        theme = st.text_input("اكتب النيش:", placeholder="مثال: قطط في الفضاء")
        pages = st.number_input("عدد الصفحات:", min_value=10, max_value=50, value=20)
        
        if st.button("🚀 بدء التصنيع اليدوي", use_container_width=True):
            if theme:
                with st.spinner("الصواريخ تعمل... جاري تصنيع الكتاب في الخلفية 🚀"):
                    # استدعاء المصنع غير المتزامن
                    product = asyncio.run(pipeline.run_coloring_book_pipeline(db, theme, int(pages)))
                    asyncio.run(telegram_dispatcher.send_launch_package(product))
                st.success("✅ تمت العملية بنجاح!")
                st.rerun() # تحديث الصفحة لإظهار المنتج الجديد
            else:
                st.error("الرجاء كتابة النيش أولاً.")

    # لوحة عرض الإنتاج
    st.header("📊 سجل الإنتاج الآلي واليدوي")
    
    # جلب آخر 20 منتج من قاعدة البيانات
    products = db.query(Product).order_by(Product.id.desc()).limit(20).all()
    
    if not products:
        st.info("📭 قاعدة البيانات فارغة. البوت الآلي نائم، أو يمكنك إضافة منتج يدوياً.")
        
    for p in products:
        with st.expander(f"📦 {p.niche} | النوع: {p.product_type} | التاريخ: {p.created_at.strftime('%Y-%m-%d %H:%M')}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**العنوان المحسن (SEO):** `{p.seo_title}`")
                st.markdown(f"**الكلمات المفتاحية:** {p.keywords}")
                st.markdown(f"**مسار الملف:** `{p.file_path}`")
            with col2:
                st.markdown(f"**حالة المصنع:** `{p.status}`")
                st.markdown(f"**حالة تيليجرام:** `{p.telegram_status}`")
            
            st.markdown("---")
            st.markdown("**سكريبت تيك توك:**")
            st.info(p.tiktok_script)

if __name__ == "__main__":
    main()

