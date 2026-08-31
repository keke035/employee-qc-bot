# ====== 知识库模块：读取文档 -> 切分 -> 向量化 -> 检索 ======
import os
import shutil
import tempfile
import setup_env   # ① 先设环境变量
import config      # ② 再读配置常量

import numpy as np
from sentence_transformers import SentenceTransformer

def build_model_dir(source_dir="models", parts_dir="models_parts"):
    """把仓库里的模型（小文件或分片）组装到可写临时目录，供加载。
    兼容：本地有完整 models/，或云端只有 models_parts/ 分片。"""
    base = os.environ.get("TMPDIR") or tempfile.gettempdir()
    out = os.path.join(base, "rag_model")
    weights = os.path.join(out, "model.safetensors")
    if os.path.isfile(weights):
        return out

    os.makedirs(out, exist_ok=True)

    # 1) 拷贝模型小文件
    if os.path.isdir(source_dir):
        for name in os.listdir(source_dir):
            src = os.path.join(source_dir, name)
            dst = os.path.join(out, name)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        # 2) 有完整权重就复制；否则拼分片
        full = os.path.join(source_dir, "model.safetensors")
        if os.path.isfile(full):
            shutil.copy2(full, weights)
        elif os.path.isdir(parts_dir):
            parts = sorted(
                (f for f in os.listdir(parts_dir)
                 if f.startswith("part_") and f.endswith(".bin")),
                key=lambda f: int("".join(c for c in f if c.isdigit())),
            )
            with open(weights, "wb") as w:
                for name in parts:
                    with open(os.path.join(parts_dir, name), "rb") as r:
                        shutil.copyfileobj(r, w)
    return out

class KnowledgeBase:
    def __init__(self):
        model_dir = build_model_dir()
        self.embedding_model = SentenceTransformer(model_dir)
        self.chunks = []
        self.chunk_embeddings = None

    def load(self, file_path=None):
        path = file_path or config.KNOWLEDGE_FILE
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        self.chunks = self._chunk_text(text)
        print(f"[知识库] 已加载 {path}，切分成 {len(self.chunks)} 块")

    def _chunk_text(self, text, chunk_size=None, overlap=None):
        chunk_size = chunk_size or config.CHUNK_SIZE
        overlap = overlap or config.CHUNK_OVERLAP
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start += chunk_size - overlap
        return chunks

    def build_index(self):
        self.chunk_embeddings = self.embedding_model.encode(self.chunks)

    def search(self, query, top_k=3):
        q_emb = self.embedding_model.encode(query)
        scores = np.dot(self.chunk_embeddings, q_emb) / (
            np.linalg.norm(self.chunk_embeddings, axis=1) * np.linalg.norm(q_emb)
        )
        idx = scores.argsort()[-top_k:][::-1]
        results = []
        for i in idx:
            results.append({"score": round(float(scores[i]), 4),
                            "content": self.chunks[i]})
        return results

    def query(self, question, top_k=3):
        hits = self.search(question, top_k)
        return "\n\n".join(h["content"] for h in hits)

kb = KnowledgeBase()