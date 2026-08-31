# ====== 员工手册智能客服 · 网页界面 ======
import streamlit as st

st.set_page_config(page_title="员工手册智能客服", page_icon="📖")
st.title("📖 员工手册智能客服")
st.caption("回答员工手册相关问题 · 支持数学计算 · 支持天气查询")

# ====== 懒加载：不在这里初始化 Agent，避免冷启动加载模型 ======
@st.cache_resource
def build_agent():
    from agent import CustomerServiceAgent
    return CustomerServiceAgent()

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.chat_input("请输入你的问题，例如：年假怎么算？")

if user_input:
    # 第一次问答时才加载模型
    agent = build_agent()

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

for role, text in st.session_state.history:
    if role == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(text)
    else:
        with st.chat_message("user"):
            st.markdown(text)