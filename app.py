
# ====== 员工手册智能客服 · 网页界面 ======
import streamlit as st

# 页面基础配置
st.set_page_config(page_title="员工手册智能客服", page_icon="📖")
st.title("📖 员工手册智能客服")
st.caption("回答员工手册相关问题 · 支持数学计算 · 支持天气查询")

# ====== 启动 Agent（只初始化一次）======
from agent import CustomerServiceAgent

@st.cache_resource
def build_agent():
    return CustomerServiceAgent()

agent = build_agent()

# ====== 会话状态：存历史对话 ======
if "history" not in st.session_state:
    st.session_state.history = []

# ====== 输入区 ======
with st.container():
    user_input = st.chat_input("请输入你的问题，例如：年假怎么算？")

# ====== 处理输入 ======
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("思考中..."):
            try:
                reply = agent.answer(user_input)
            except Exception as e:
                reply = f"抱歉，服务出了点问题：{e}"
        st.markdown(reply)

    st.session_state.history.append(("user", user_input))
    st.session_state.history.append(("assistant", reply))

# ====== 展示历史记录 ======
last_seen = {
    "user": len(st.session_state.history),
}

for rolex, text in st.session_state.history:
    if rolex == "user":
        with st.chat_message("user"):
            st.markdown(text)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(text)