import config
import knowledge_base

# 使用项目里的单例
kb = knowledge_base.kb
kb.load()
kb.build_index()

print("检索测试：年度休假怎么算")
for hit in kb.search("年度休假怎么算", top_k=2):
    print(" 分:", hit["score"], "| 内容:", hit["content"][:50], "...")