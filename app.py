import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="KDP Auto-Author", page_icon="🚀", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2980b9; color: white; }
    </style>
    """, unsafe_allow_html=True)


st.title("🌌 Outer Space KDP Generator")
st.info("تم التطوير بواسطة: Erwin Smith")

# --- جلب مفتاح API من إعدادات Render ---
# سيقوم الموقع بالبحث عن متغير اسمه GEMINI_API_KEY في إعدادات Render
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ لم يتم العثور على مفتاح API في إعدادات السيرفر. يرجى إدخاله يدوياً مؤقتاً:")
    api_key = st.text_input("Gemini API Key:", type="password")

# --- مدخلات المستخدم ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("نوع النشاط:", ["Coloring Pages", "Mazes", "Spot the Difference"])
        pages_count = st.slider("عدد صفحات الأنشطة:", 5, 20, 10)
    with col2:
        theme = st.text_input("الثيم (Theme):", "Cute Outer Space")
        age_group = st.selectbox("الفئة العمرية:", ["4-8 years", "8-12 years"])

book_title = st.text_input("عنوان الكتاب:", f"{theme} {category} for Kids")

# --- منطق التوليد ---
if st.button("🚀 ابدأ صناعة الكتاب"):
    if not api_key:
        st.error("خطأ: مفتاح API مفقود!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("🧠 غيميني يقوم بتصميم أوامر الصور..."):
                prompt_task = f"""Generate {pages_count} unique image prompts for a children's {category} book. 
                Theme: {theme}. Audience: {age_group}. 
                Style: Bold black outlines, coloring book style, white background, no shading, flat vector.
                Return ONLY the prompts, one per line."""
                
                response = model.generate_content(prompt_task)
                prompts_list = [p.strip() for p in response.text.split('\n') if p.strip()]

            # إنشاء ملف PDF بمقاس 8.5x11 بوصة
            pdf = FPDF(unit="in", format=(8.5, 11))
            pdf.set_auto_page_break(0)
            
            # صفحة العنوان
            pdf.add_page()
            pdf.set_font("Arial", "B", 24)
            pdf.cell(0, 5, book_title, align="C")
            
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, p in enumerate(prompts_list):
                status_text.text(f"جاري توليد الصفحة {i+1} من {len(prompts_list)}...")
                
                # استخدام pollinations لتوليد الصور
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true&seed={i}"
                img_data = requests.get(img_url).content
                
                with open(f"temp_{i}.jpg", "wb") as f:
                    f.write(img_data)
                
                # إضافة صفحة النشاط
                pdf.add_page()
                pdf.image(f"temp_{i}.jpg", x=0.5, y=0.5, w=7.5)
                
                # إضافة صفحة فارغة خلفها (قاعدة التلوين)
                pdf.add_page()
                
                os.remove(f"temp_{i}.jpg")
                progress_bar.progress((i + 1) / len(prompts_list))

            output_file = "KDP_Space_Adventure.pdf"
            pdf.output(output_file)
            
            st.success("✅ تم بنجاح! كتابك جاهز للتحميل.")
            with open(output_file, "rb") as f:
                st.download_button("⬇️ تحميل الكتاب (PDF)", f, file_name=output_file)

        except Exception as e:
            st.error(f"حدث خطأ تقني: {e}")
