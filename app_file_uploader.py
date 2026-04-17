"""
1
基于Streamlit完成WEB网页上传服务

pip install streamlit

Streamlit：当WEB页面元素发生变化，则代码重新执行一遍
"""
import time
from docx import Document
import streamlit as st
from knowledge_base import KnowledgeBaseService

# 添加网页标题
st.title("生命语言组学问答系统")

# file_uploader
uploader_file = st.file_uploader(
    "请上传TXT文件",
    type=['txt', 'docx'],
    accept_multiple_files=False,    # False表示仅接受一个文件的上传
)

# session_state就是一个字典
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()


if uploader_file is not None:
    # 提取文件的信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024    # KB

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | 大小：{file_size:.2f} KB")

    # 判断文件类型，docx还是txt
    # get_value -> bytes -> decode('utf-8')
    file_content = ''
    if uploader_file.type == "text/plain":
        text = uploader_file.getvalue().decode("utf-8")
        file_content = text
    elif uploader_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # 如果是docx文档，处理docx文件
        doc = Document(uploader_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        file_content = '\n'.join(full_text)

    with st.spinner("载入知识库中..."):       # 在spinner内的代码执行过程中，会有一个转圈动画
        time.sleep(1)
        result = st.session_state["service"].upload_by_str(file_content, file_name)
        st.write(result)




