import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import time

# --- إعداد الصفحة والواجهة ---
st.set_page_config(page_title="KDP Book Generator", page_icon="📚", layout="centered")
st.title("🚀 KDP Activity Book Generator")
st.markdown("##### Made by Erwin Smith") # حقوق المطور كما طلبت
st.divider()

# --- إعداد مفتاح Gemini ---
# في بيئة الإنتاج (Render)، يجب وضع المفتاح في Secrets، لكن هنا للتجربة سنأخذه كإدخال
API_KEY = st.text_input("Enter your Gemini API Key:", type="password")

# --- واجهة المستخدم (المدخلات) ---
col1, col2 = st.columns(2)
with col1:
    book_type = st.selectbox("Book Type (نوع الكتاب):", ["Coloring Book", "Mazes", "Spot the Difference"])
    book_style = st.selectbox("Style/Theme (الثيم):", ["Space Adventures", "Cute Ocean", "Robots", "Dinosaurs"])
with col2:
    target_audience = st.selectbox("Age Group:", ["Ages 4-8", "Ages 8-12"])
    # قللنا العدد للتجربة فقط حتى لا ينتهي وقت السيرفر، يمكنك زيادته لاحقاً
    num_pages = st.number_input("Number of Pages (للنسخة التجريبية):", min_value=1, max_value=5, value=2)

book_title = st.text_input("Book Title (العنوان):", f"{book_style} {book_type} for Kids")

# --- زر بدء التوليد ---
if st.button("🪄 Generate Book", use_container_width=True):
    if not API_KEY:
        st.error("Please enter your Gemini API Key first!")
        st.stop()

    # 1. تهيئة Gemini
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    with st.spinner("🧠 Gemini is designing the pages (Writing Prompts)..."):
        # إعطاء أوامر لغيميني لتوليد أوامر الصور باللغة الإنجليزية
        system_prompt = f"""
        You are an expert KDP activity book designer. The target audience is Western/English speaking.
        Create a list of exactly {num_pages} highly detailed image generation prompts for a {book_type}.
        The theme is {book_style} and the target age is {target_audience}.
        Rules for the prompts:
        - Must be in English.
        - Must include: "thick black outlines, pure white background, coloring book style, simple flat vector, no shading".
        - Only output the prompts, one per line. No introductions, no numbers.
        """
        response = model.generate_content(system_prompt)
        prompts = response.text.strip().split('\n')
        # تنظيف القائمة من أي أسطر فارغة
        prompts = [p.strip() for p in prompts if p.strip()]

    st.success(f"✅ Generated {len(prompts)} prompts successfully!")

    # 2. توليد الصور وتجميعها في PDF
    with st.spinner("🎨 Generating Images and compiling PDF... This may take a minute."):
        pdf = FPDF(unit="in", format=(8.5, 11)) # مقاس أمازون KDP
        pdf.set_auto_page_break(0)
        
        # صفحة العنوان
        pdf.add_page()
        pdf.set_font("Arial", "B", 24)
        pdf.cell(0, 5, book_title, align="C")
        
        image_files = []

        # المرور على كل برومبت وتوليد صورته
        for i, prompt in enumerate(prompts):
            if i >= num_pages: break # ضمان عدم تجاوز العدد
            st.text(f"Generating image {i+1}...")
            
            # نستخدم pollinations لتوليد الصور مجاناً عبر الـ URL
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&nologo=true"
            img_response = requests.get(image_url)
            
            if img_response.status_code == 200:
                img_path = f"temp_img_{i}.jpg"
                with open(img_path, "wb") as f:
                    f.write(img_response.content)
                image_files.append(img_path)
                
                # إضافة الصورة للـ PDF (على الوجه الأيمن)
                pdf.add_page()
                # نترك هامش 0.5 بوصة من كل جهة
                pdf.image(img_path, x=0.5, y=0.5, w=7.5, h=7.5) 
                
                # إضافة صفحة فارغة خلفها (لمنع تسرب الألوان)
                pdf.add_page()
            
            # استراحة قصيرة لتجنب حظر الـ API
            time.sleep(1)

        # حفظ ملف الـ PDF النهائي
        pdf_filename = "KDP_Book_Ready.pdf"
        pdf.output(pdf_filename)

    # 3. تنظيف الملفات المؤقتة
    for img in image_files:
        if os.path.exists(img):
            os.remove(img)

    st.success("🎉 Book is Ready!")
    
    # 4. زر تحميل الـ PDF
    with open(pdf_filename, "rb") as pdf_file:
        st.download_button(
            label="⬇️ Download PDF Book",
            data=pdf_file,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True
        )
