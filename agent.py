# ====== 主 Agent：工具调度 + 查询改写 + 多轮循环 ======
import json
import logging
from openai import OpenAI
import setup_env
import config
import tools
import knowledge_base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("agent")

kb = knowledge_base.kb  # 项目里的知识库单例

class CustomerServiceAgent:
    def __init__(self):
        print("CLOUD KEY len:", len(config.DEEPSEEK_API_KEY or ""))
        self.client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )
        # 一次性加载知识库并建索引（网页版只在启动时做一次）
        kb.load()
        kb.build_index()
        logger.info("知识库加载并索引完成")

    # ---------- 查询改写：把用户问题改成更贴知识库措辞的检索词 ----------
    def rewrite_query(self, question):
        prompt = f"""你负责把一个用户的提问，改写成一个更适合在"员工手册"里检索的关键问句。
要求：保留原意，但尽量使用手册里可能出现的正式措辞（例如把"年假"改成"年度休假"）。
只输出改写后的问句，不要任何解释。

原始提问：{question}
改写后的检索问句："""
        r = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return r.choices[0].message.content.strip()

    # ---------- 知识库工具 ----------
    def kb_query(self, question, top_k=3):
        results = kb.search(question, top_k=top_k)
        out = []
        for i, hit in enumerate(results, 1):
            out.append(f"[片段{i} 相关度{hit['score']}]\n{hit['content']}")
        return "\n\n".join(out)

    # ---------- 让网页/命令行都能复用的“问一句答一句”接口 ----------
    def answer(self, user_input):
        system_prompt = """你是一个公司智能客服助手，能回答员工手册相关问题、做数学计算、查天气。
规则：
- 回答员工手册问题前，先用查询改写把问题变成更贴手册的措辞，再调用知识库工具。
- 只依据知识库工具返回的内容回答，知识库里找不到就明确说"手册里没有相关内容，建议咨询HR"，不要编造。
- 不要使用任何Markdown格式（不要加粗、不要列表符号），用纯文字回答。
- 闲聊可直接回复不需要调用工具。
- 回答时只回答用户当前的提问，不要复述或重复之前的对话内容"""
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}]

        greeting_words = ["你好", "您好", "hi", "hello", "谢谢", "在吗", "你是谁"]
        is_greeting = any(g in user_input.lower() for g in greeting_words)

        # 查询改写：非问候语才改写，避免问候也被拉进检索
        rewrite = user_input if is_greeting else self.rewrite_query(user_input)

        tools_schema = tools.TOOLS_SCHEMA + [{
            "type": "function",
            "function": {
                "name": "kb_query",
                "description": "在员工手册知识库中检索相关问题（应传入改写后的问句）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "检索问句"},
                    },
                    "required": ["question"],
                },
            },
        }]
        tools_map = {**tools.TOOLS_MAP, "kb_query": self.kb_query}

        for round_idx in range(config.MAX_ROUNDS):
            try:
                response = self.client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=messages,
                    tools=tools_schema,
                    temperature=0.1,
                )
            except Exception as e:
                logger.error("调用大模型失败: %s", e)
                return f"抱歉，服务暂时开小差了：{e}"

            msg = response.choices[0].message
            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    if name == "kb_query":
                        args["question"] = rewrite  # 用改写后的问句检索
                    result = tools_map[name](**args)
                    logger.info("调用工具 %s 参数=%s", name, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    })
            else:
                return msg.content

        return "抱歉，这次会话没能完成，请再试一次。"

    # ---------- 命令行入口（保留原来用法）----------
    def run(self):
        while True:
            user_input = input("你有什么问题？(输入'退出'结束)")
            if user_input == "退出":
                print("再见！")
                break
            print("AI:", self.answer(user_input))

if __name__ == "__main__":
    CustomerServiceAgent().run()