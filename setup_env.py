
# ====== 环境准备：让 embedding 模型在本地/云端都能加载 ======
import os
import tempfile

# 优先用系统/项目缓存；云端无缓存时也能回退到系统临时目录
cache_base = os.environ.get("HF_HOME") or os.path.join(
    tempfile.gettempdir(), "hf_cache"
)
os.environ["HF_HOME"] = cache_base
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# 注意：云端不自带 HuggingFace 缓存，若 still 连不上 hf 会崩，

# 因此模型需提前分片打包进仓库，由 indexer 组装后加载。
os.environ["HF_HUB_OFFLINE"] = "1"
