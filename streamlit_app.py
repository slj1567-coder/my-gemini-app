import streamlit as st
import google.generativeai as genai

# 設定網頁標題
st.title("我的 AI 助手 🤖")

# 從 Streamlit Secrets 獲取 API Key
api_key = st.secrets["GEMINI_API_KEY"]

# 設定 Gemini 模型
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 初始化聊天歷史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史訊息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 接收使用者輸入
if prompt := st.chat_input("輸入你想問的問題..."):
    # 顯示使用者訊息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 呼叫 Gemini API
    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.markdown(response.text)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
