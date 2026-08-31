
# ====== 统一设置环境变量：本地与云端按需分流 ======
import os

# 判断是否线上（Streamlit Cloud）
IS_CLOUD = os.getenv("STREAMLIT_SERVER_ADDRESS") is not None

if IS_CLOUD:
    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
else:
    HF_CACHE = r"C:\Users\86156\Downloads\hf_cache"
    os.environ["HF_HOME"] = HF_CACHE
    os.environ["HF_HUB_CACHE"] = os.path.join(HF_CACHE, "hub")
    os.environ["HF_HUB_OFFLINE"] = "1"
    # force redeploy
