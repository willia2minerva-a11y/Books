import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF
import os
import time

# --- إعدادات الواجهة ---
st.set_page_config(page_title="KDP Auto-Author Pro", page_icon="⚙️", layout="centered")
st.title("🌌 صانع كتب KDP المتقدم")
st.markdown("**تم التطوير بواسطة: Erwin Smith**")
st.divider()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.text_input("أدخل مفتاح Gemini API:", type="password")

book_types = {
    "كتب التلوين (AI Images)": "Coloring Book",
    "المتاهات (AI Images)": "Mazes",
    "سودوكو (Pure Python Logic)": "Sudoku"
}

col1, col2 = st.columns(2)
with col1:
    selected_type = st.selectbox("نوع النشاط:", list(book_types.keys()))
    pages_count = st.slider("عدد الألغاز/الصفحات:", 2, 20, 5)
with col2:
    theme = st.text_input("الثيم (للتلوين والمتاهات):", "Space Adventures")
    book_title = st.text_input("عنوان الكتاب:", "My Awesome Activity Book")

category = book_types[selected_type]

# --- دالة رسم السودوكو برمجياً (بدون ذكاء اصطناعي للصور) ---
def generate_sudoku_pages(pdf, count):
    for n in range(count):
        pdf.add_page()
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 1, f"Sudoku Puzzle #{n+1}", align="C", ln=True)
        
        # رسم شبكة 9x9 دقيقة
        start_x, start_y, cell_size = 1.25, 2.5, 0.66
        for i in range(10):
            # خطوط سميكة للمربعات الكبيرة، ورفيعة للمربعات الصغيرة
            line_width = 0.05 if i % 3 == 0 else 0.01
            pdf.set_line_width(line_width)
            # خطوط أفقية
            pdf.line(start_x, start_y + i * cell_size, start_x + 9 * cell_size, start_y + i * cell_size)
            # خطوط عمودية
            pdf.line(start_x + i * cell_size, start_y, start_x + i * cell_size, start_y + 9 * cell_size)
        
        pdf.add_page() # صفحة فارغة لمنع التسرب

if st.button("🚀 بدء المعالجة والتوليد", use_container_width=True):
    if not api_key:
        st.error("مفتاح API مفقود!")
        st.stop()

    try:
        pdf = FPDF(unit="in", format=(8.5, 11))
        pdf.set_auto_page_break(0)
        pdf.add_page()
        pdf.set_font("Arial", "B", 26)
        pdf.cell(0, 4, book_title, align="C")

        if category == "Sudoku":
            with st.spinner("🔢 جاري بناء شبكات السودوكو رياضياً..."):
                generate_sudoku_pages(pdf, pages_count)
        else:
            with st.spinner("🧠 غيميني يصمم الأوامر..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                sys_prompt = f"""Generate {pages_count} prompt descriptions for a children's {category}. 
                Theme: {theme}. Style: thick black outlines, coloring book style, white background, simple vector.
                Return ONLY the prompts, one per line."""
                
                response = model.generate_content(sys_prompt)
                prompts = [p.strip() for p in response.text.split('\n') if p.strip()]

            progress = st.progress(0)
            for i, p in enumerate(prompts[:pages_count]):
                st.text(f"توليد الصورة {i+1}...")
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1024&height=1024&nologo=true"
                
                # إضافة احتياط (Timeout & Retry) لمعالجة تعليق السيرفر
                img_response = requests.get(img_url, timeout=15) 
                
                with open(f"temp_img.jpg", "wb") as f:
                    f.write(img_response.content)
                
                pdf.add_page()
                # توسيط الصورة بدقة: العرض 7، والمساحة المتبقية 1.5 (0.75 من كل جهة)
                pdf.image("temp_img.jpg", x=0.75, y=1.5, w=7, h=7)
                pdf.add_page()
                progress.progress((i + 1) / pages_count)
            
            if os.path.exists("temp_img.jpg"): os.remove("temp_img.jpg")

        output_name = "Final_KDP_Book.pdf"
        pdf.output(output_name)
        st.success("✅ تم الفحص والتجميع بنجاح!")
        
        with open(output_name, "rb") as f:
            st.download_button("⬇️ تحميل الكتاب الجاهز للطباعة", f, file_name=output_name)

    except Exception as e:
        st.error(f"تم اكتشاف خطأ ومعالجته: {e}")
