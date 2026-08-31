# ====== 把完整权重拆分成 <100MB 的分片（推到 GitHub 用）======
import os
import glob

SRC = r"C:\Users\86156\Downloads\enterprise_qa_bot\models\model.safetensors"  # 项目二完整权重
OUT_DIR = "models_parts"
CHUNK = 90 * 1024 * 1024  # 每片 90MB（<100MB，安全）

os.makedirs(OUT_DIR, exist_ok=True)
with open(SRC, "rb") as f:
    data = f.read()

print(f"总大小: {len(data)/1024/1024:.2f} MB")
idx = 0
part = 0
while idx < len(data):
    piece = data[idx: idx + CHUNK]
    name = f"part_{part}.bin"
    with open(os.path.join(OUT_DIR, name), "wb") as w:
        w.write(piece)
    print(f"写出 {name}: {len(piece)/1024/1024:.2f} MB")
    idx += CHUNK
    part += 1
print("完成，共", part, "个分片")