# app.py
import streamlit as st
import asyncio
import os
import traceback
from core.database import SessionLocal, engine, Base
from core.models import Product, SystemLog
from services.ai_engine import ai_engine
from services.factory_pipeline import pipeline
from services.telegram_ops import telegram_dispatcher

# إنشاء الجداول إذا لم تكن موجودة
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# إعداد الصفحة
st.set_page_config(page_title="مصنع المحتوى V32.4", page_icon="🏭", layout="centered")

# ==========================================
# 1. حقنة CSS لجعل الموقع عربياً بالكامل (RTL)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    /* فرض الاتجاه من اليمين لليسار على كل شيء */
    html, body, [class*="st-"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    /* عكس اتجاه القوائم والأزرار لتبدو طبيعية بالعربية */
    .stTabs [data-baseweb="tab-list"] { justify-content: flex-start; flex-direction: row-reverse; }
    .stTabs [data-baseweb="tab"] { font-family: 'Cairo', sans-serif; font-weight: bold; }
    
    /* تنسيق العناوين والبطاقات */
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
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        border-right: 5px solid #FF416C;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF416C, #FF4B2B);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255,65,108,0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الواجهة الرئيسية والتطبيقات
# ==========================================
def main():
    st.markdown('<h1 class="main-title">🏭 مصنع المحتوى الرقمي V32.4</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#666;">المهندس: DevMate | معمارية Async + DB</p>', unsafe_allow_html=True)
    
    # التحقق من تيليجرام
    if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
        st.warning("⚠️ تنبيه: مفاتيح تيليجرام غير موجودة في متغيرات البيئة. سيتم الإنتاج ولكن لن يتم الإرسال.")

    tabs = st.tabs(["📝 الموجه المفتوح", "🚀 المصنع السريع", "🔍 محلل النيش", "🤖 الأتمتة والسجل"])
    
    db = next(get_db())

    # ========== تبويب الموجه المفتوح ==========
    with tabs[0]:
        st.markdown("""
        <div class="info-card">
            <h3>📝 طور الموجه المفتوح (الذكي)</h3>
            <p>اكتب وصفاً حراً، وسيقوم المحرك الذكي بتحليله وتصنيعه فوراً.</p>
        </div>
        """, unsafe_allow_html=True)
        
        open_prompt = st.text_area("✍️ ماذا تريد أن نصنع اليوم؟", height=100, placeholder="مثال: اصنع لي كتاب تلوين عن ديناصورات في الفضاء للأطفال بـ 15 صفحة")
        
        if st.button("✨ تحليل وتصنيع", key="open_prompt_btn", use_container_width=True):
            if len(open_prompt) > 5:
                with st.spinner("🧠 جاري تحليل طلبك..."):
                    parsed_data = ai_engine.parse_open_prompt(open_prompt)
                    st.success(f"✅ تم الفهم! النيش: {parsed_data['theme']} | الصفحات: {parsed_data['pages']}")
                    
                    # استدعاء المصنع
                    run_factory_ui(db, parsed_data['theme'], parsed_data['pages'], parsed_data['mode'])
            else:
                st.error("الرجاء إدخال وصف أطول.")

    # ========== تبويب المصنع السريع ==========
    with tabs[1]:
        st.markdown('<div class="info-card">⚡ اختر الإعدادات وسيتم التصنيع فوراً.</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            theme_input = st.text_input("🎯 فكرة النيش:")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True) # للمحاذاة
            if st.button("💡 اقترح نيش"):
                theme_input = ai_engine.generate_niche()
                st.info(f"اقتراح: {theme_input}")

        pages_input = st.number_input("📄 عدد الصفحات:", min_value=10, max_value=50, value=20)
        mode_input = st.selectbox("📦 نوع الكتاب:", ["تلوين للأطفال", "قصص مصورة", "ألغاز ونشاطات", "مخططات ودفاتر"])
        
        if st.button("🚀 ابدأ التصنيع", key="quick_factory_btn", use_container_width=True):
            if theme_input:
                run_factory_ui(db, theme_input, int(pages_input), mode_input)
            else:
                st.error("الرجاء إدخال فكرة النيش.")

    # ========== تبويب محلل النيش ==========
    with tabs[2]:
        st.markdown('<div class="info-card">🔍 حلل قوة النيش قبل تصنيعه.</div>', unsafe_allow_html=True)
        niche_to_analyze = st.text_input("💡 أدخل الفكرة لتحليلها:")
        if st.button("📊 تحليل السوق"):
            if niche_to_analyze:
                with st.spinner("جاري دراسة السوق والكلمات المفتاحية..."):
                    marketing = ai_engine.generate_marketing(niche_to_analyze)
                    st.json(marketing) # عرض الـ JSON بشكل أنيق
            else:
                st.error("أدخل الفكرة أولاً.")

    # ========== تبويب الأتمتة والسجل ==========
    with tabs[3]:
        st.markdown('<div class="info-card">🤖 سجل المصنع وحالة الإرسال لتيليجرام.</div>', unsafe_allow_html=True)
        
        products = db.query(Product).order_by(Product.id.desc()).limit(10).all()
        if not products:
            st.info("لم يتم تصنيع أي منتج بعد.")
            
        for p in products:
            with st.expander(f"📦 {p.niche} | 📅 {p.created_at.strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"**حالة التصنيع:** `{p.status}`")
                st.write(f"**حالة تيليجرام:** `{p.telegram_status}`")
                st.write(f"**مسار الملف:** `{p.file_path}`")
                if p.seo_title:
                    st.write(f"**SEO Title:** {p.seo_title}")

def run_factory_ui(db, theme, pages, mode):
    """دالة مساعدة لتشغيل المصنع من الواجهة وعرض التقدم"""
    progress_bar = st.progress(0, text="🚀 جاري تسخين المحركات...")
    status_text = st.empty()
    
    try:
        # تشغيل خط الإنتاج غير المتزامن
        status_text.info("🎨 جاري توليد الصور وبناء الكتاب (قد يستغرق 30-60 ثانية)...")
        progress_bar.progress(40)
        
        # ملاحظة: حالياً المصنع يدعم "كتب التلوين". سنضيف البقية لاحقاً.
        product = asyncio.run(pipeline.run_coloring_book_pipeline(db, theme, pages))
        
        progress_bar.progress(80, text="📦 جاري الإرسال إلى تيليجرام...")
        status_text.info("إرسال الحزمة لتيليجرام...")
        
        # الإرسال لتيليجرام
        success = asyncio.run(telegram_dispatcher.send_launch_package(product))
        
        if success:
            product.telegram_status = "✅ تم الإرسال"
            st.success("🎉 تم تصنيع الكتاب وإرساله لتيليجرام بنجاح!")
        else:
            product.telegram_status = "❌ فشل الإرسال"
            st.error("⚠️ تم تصنيع الكتاب، لكن فشل إرساله لتيليجرام. (تأكد من إعدادات البوت والإنترنت).")
            
        db.commit()
        progress_bar.progress(100, text="✅ اكتملت العملية.")
        
        # توفير زر تحميل مباشر من الواجهة
        if product.file_path and os.path.exists(product.file_path):
            with open(product.file_path, "rb") as f:
                st.download_button("📥 تحميل الكتاب يدوياً", data=f, file_name=os.path.basename(product.file_path), mime="application/pdf")

    except Exception as e:
        progress_bar.empty()
        st.error(f"❌ حدث خطأ داخلي: {str(e)}")
        with st.expander("تفاصيل الخطأ للمطور"):
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
