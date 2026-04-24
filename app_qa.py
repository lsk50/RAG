# --- 强制修复 Protobuf 版本冲突 ---
import subprocess
import sys
import streamlit as st
import json
import os
# 如果 protobuf 版本高于 4.0，强制降级到 3.20.3
# subprocess.check_call([sys.executable, "-m", "pip", "install", "protobuf==3.20.3"])

# st.write(f"当前 Python 版本: {sys.version}")
# st.write(f"Python 可执行文件路径: {sys.executable}")
# # ----------------------------------

import time
from rag import RagService
import config_data as config

# 定义会话存储文件路径
SESSION_STORAGE_FILE = "./chat_history/session_storage.json"

# 确保存储目录存在
os.makedirs(os.path.dirname(SESSION_STORAGE_FILE), exist_ok=True)

# 加载会话状态

def load_session():
    if os.path.exists(SESSION_STORAGE_FILE):
        try:
            with open(SESSION_STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"加载会话失败: {e}")
            return [{"role": "assistant", "content": "你好，有什么可以帮助你？"}]
    return [{"role": "assistant", "content": "你好，有什么可以帮助你？"}]

# 保存会话状态

def save_session(messages):
    try:
        with open(SESSION_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"保存会话失败: {e}")

# 标题
st.title("生命语言组学问答系统")
st.divider()            # 分隔符

# 初始化会话状态，从文件加载历史记录
if "message" not in st.session_state:
    st.session_state["message"] = load_session()

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
        # yield

        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(res_stream, ai_res_list))
        st.session_state["message"].append({"role": "assistant", "content": "".join(ai_res_list)})
        
        # 保存会话状态到文件
        save_session(st.session_state["message"])
        
        # 强制刷新页面以显示更新后的会话状态
        st.rerun()

