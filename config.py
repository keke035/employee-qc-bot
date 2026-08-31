
# ====== 全局配置 ======
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# 云端用 Streamlit secrets 兜底（本地没有 streamlit 也安全）
try:
    import streamlit as st
    _has_streamlit = True
except Exception:
    _has_streamlit = False

def _get_secret(key):
    """优先系统环境变量，其次 Streamlit secrets（云端部署用）"""
    val = os.getenv(key)
    if val:
        return val
    if _has_streamlit:
        try:
            return st.secrets.get(key)
        except Exception:
            return None
    return None

# ---- 大模型 API ----
DEEPSEEK_API_KEY = _get_secret("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-chat"

# ---- Embedding ----
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# ---- 知识库路径（正斜杠，Linux/Windows 通用）----
KNOWLEDGE_FILE = "data/员工手册.txt"

# ---- Agent 运行参数 ----
MAX_ROUNDS = 10

# ---- 切分参数 ----
CHUNK_SIZE = 700
CHUNK_OVERLAP = 50
