# AI 智能客服 Agent

一个基于大模型 + Function Calling + RAG 的智能客服 Agent，
能回答员工手册问题、做数学计算、查天气，并具备抗幻觉能力。

## 功能特性
- 多轮对话：基于 OpenAI 兼容 API（DeepSeek），支持函数调用循环
- 工具调用（Function Calling）：
  - 数学计算（加减乘除、幂运算）
  - 天气查询（对接外部天气接口）
  - 知识库检索（RAG）
- 检索增强生成（RAG）：
  - 文档切分（chunk + overlap）
  - 向量化（Sentence-BERT 多语言模型）
  - 余弦相似度检索，返回 Top-K 相关片段
  - 查询改写：把口语提问改写为贴近文档的说法，提升命中率
- 抗幻觉：只依据知识库返回内容回答，找不到就明确说明，不编造

## 技术栈
- Python 3 / DeepSeek API（OpenAI 兼容）
- sentence-transformers（向量检索）
- numpy（余弦相似度计算）

## 项目结构

| 文件 | 作用 |
|------|------|
| main.py | 统一入口 |
| agent.py | 主 Agent：工具调度 + 查询改写 + 多轮循环 |
| tools.py | 工具定义（计算 / 天气） |
| knowledge_base.py | RAG：加载、切分、向量化、检索 |
| config.py | 全局配置（纯常量） |
| setup_env.py | 环境变量设置 |
| data/员工手册.txt | 知识库文档源 |
## 快速开始
1. 安装依赖：`pip install openai sentence-transformers numpy python-dotenv`
2. 配置 `DEEPSEEK_API_KEY` 环境变量
3. 运行：`python main.py`

## 运行示例
> 问：工作满 3 年有几天年假？

>AI回答： 根据员工手册的规定，员工进入公司实际工作满一年至三年（含第三年）的，方可享有3日年度休假之福利。从第四年以后，服务期每满一年加1日假期，但年度休假累计最多不超过15日。 所以工作满3年，享有3日年度休假。
## 遇到的难点与解决
| 难点 | 现象 | 解决 |
|------|------|------|
| 循环导入 | `AttributeError: partially initialized module 'config' has no attribute` | 把环境变量设置抽到独立的 `setup_env.py`，`config.py` 只留纯常量 |
| 环境变量混乱 | HF 缓存拉取失败、连接超时 | 统一在 `setup_env.py` 设置 `HF_HOME` / `HF_ENDPOINT` / 离线模式 |
| 检索分数偏低 | 口语「年假」0.45 分 vs 「年度休假」0.66 分 | 加查询改写，把用户提问改写为贴合文档的说法再检索 |
| 多轮串台 | 上一轮对话影响当前回答 | 每轮从 `system + 当前问题` 重新构造 `messages` |
| 模型幻觉 | 知识库没有也硬编答案 | 只依据工具返回内容回答，找不到就明确说「建议咨询HR」 |
| API 调用崩溃 | 网络抖动直接抛异常退出 | 大模型调用加 `try/except` 兜底 |