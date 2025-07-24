import re
import os
from PyPDF2 import PdfReader
from docx import Document
import streamlit as st

# Hàm trích xuất văn bản từ file PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = []
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text.append(page.extract_text())
    return ''.join(text)

# Làm sạch văn bản cho Word
def clean_text_for_word(text):
    cleaned_text = re.sub(r'[\x00-\x1F\x7F]', '', text)  # Remove non-printable characters
    cleaned_text = cleaned_text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").strip()
    return cleaned_text

# Hàm chia văn bản thành các chương (dựa trên "Chương I", "Chương II", ...)
def split_into_chapters(text):
    chapters = re.split(r'(Chương\s+[IVXLCDM]+)', text)
    chapters = [chapter.strip() for chapter in chapters if chapter.strip()]
    
    chapter_list = []
    for i in range(0, len(chapters), 2):
        if i+1 < len(chapters):
            chapter_list.append(chapters[i] + "\n" + chapters[i+1])
        else:
            chapter_list.append(chapters[i])
    
    return chapter_list

# Hàm chia văn bản thành các điều (dựa trên "Điều 1", "Điều 2", ...)
def split_into_articles(text):
    articles = re.split(r'(Điều\s+\d+)', text)
    articles = [article.strip() for article in articles if article.strip()]
    
    article_list = []
    for i in range(0, len(articles), 2):
        if i+1 < len(articles):
            article_list.append(articles[i] + "\n" + articles[i+1])
        else:
            article_list.append(articles[i])
    
    return article_list

# Hàm lưu các chương hoặc điều vào file Word
def save_parts_as_word(parts, part_type):
    output_files = []
    for i, part in enumerate(parts):
        doc = Document()
        doc.add_paragraph(part)
        output_path = f"{part_type}_{i+1}.docx"
        doc.save(output_path)
        output_files.append(output_path)
    return output_files

# Hàm chính để xử lý PDF
def process_pdf(pdf_file, split_type):
    text = extract_text_from_pdf(pdf_file)
    cleaned_text = clean_text_for_word(text)
    
    if split_type == "Chương":
        parts = split_into_chapters(cleaned_text)
    elif split_type == "Điều":
        parts = split_into_articles(cleaned_text)
    
    output_files = save_parts_as_word(parts, split_type)
    return output_files

# Streamlit UI
st.title("Chia PDF thành các chương hoặc điều và tải về")
st.markdown("Tải lên file PDF và hệ thống sẽ xử lý để chia thành các chương hoặc điều và xuất thành các file Word.")

# Tải lên file PDF
uploaded_file = st.file_uploader("Chọn file PDF", type=["pdf"])

# Chọn loại tách (Chương hoặc Điều)
split_type = st.selectbox("Chọn cách tách văn bản:", ["Chương", "Điều"])

if uploaded_file is not None:
    # Hiển thị file đã tải lên
    st.write("Đang xử lý file:", uploaded_file.name)

    # Xử lý PDF và lưu các chương hoặc điều thành các file Word
    output_files = process_pdf(uploaded_file, split_type)

    # Tạo liên kết để tải các file về
    st.markdown("### Các phần đã được tạo. Tải về các file Word dưới đây:")
    for i, file in enumerate(output_files):
        with open(file, "rb") as f:
            st.download_button(
                label=f"Tải {split_type} {i+1}",
                data=f,
                file_name=os.path.basename(file),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # Xoá các file sau khi tải về
    for file in output_files:
        os.remove(file)
