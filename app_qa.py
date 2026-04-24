# --- 强制修复 Protobuf 版本冲突 ---
import subprocess
import sys
import streamlit as st
# 如果 protobuf 版本高于 4.0，强制降级到 3.20.3
# subprocess.check_call([sys.executable, "-m", "pip", "install", "protobuf==3.20.3"])

# st.write(f"当前 Python 版本: {sys.version}")
# st.write(f"Python 可执行文件路径: {sys.executable}")
# # ----------------------------------

import time
from rag import RagService
import streamlit as st
import config_data as config

# 标题
# 标题
st.title("生命语言组学问答系统")
st.divider()            # 分隔符

# 初始化消息历史
if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "你好，有什么可以帮助你？"}]

if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

# 显示完整的对话历史
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 在页面最下方提供用户输入栏
prompt = st.chat_input()

if prompt:
    # 在页面输出用户的提问
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    ai_res_list = []
    with st.spinner("AI思考中..."):
        res_stream = st.session_state["rag"].chain.stream({"input": prompt}, config.session_config)
        
        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(res_stream, ai_res_list))
        st.session_state["message"].append({"role": "assistant", "content": "".join(ai_res_list)})
        st.rerun()
