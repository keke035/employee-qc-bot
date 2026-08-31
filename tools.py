# ====== 业务工具：算数 + 天气 ======
import requests

def calc_add(a, b):
    return a + b

def calc_power(a, b):
    return a ** b

def get_weather(city):
    """根据城市名查询实时温度"""
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "zh"},
            timeout=10,
        ).json()
        result = geo["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather = requests.get(url, timeout=10).json()
        temp = weather["current_weather"]["temperature"]
        return f"{city}当前温度是{temp}摄氏度"
    except Exception as e:
        return f"查询天气失败：{e}"

# 工具名 -> 真实函数 的映射（后面 Agent 用）
TOOLS_MAP = {
    "calc_add": calc_add,
    "calc_power": calc_power,
    "get_weather": get_weather,
}

# 工具描述（给模型的"员工花名册"）
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calc_add",
            "description": "计算两个数字的加法",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个加数"},
                    "b": {"type": "number", "description": "第二个加数"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_power",
            "description": "计算a的b次幂",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "底数"},
                    "b": {"type": "number", "description": "指数"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "根据城市名查询当地当前天气温度",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如 北京"},
                },
                "required": ["city"],
            },
        },
    },
]