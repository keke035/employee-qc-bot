import tools

# 测试加法
print("加法:", tools.TOOLS_MAP["calc_add"](3, 5))

# 测试次幂
print("次幂:", tools.TOOLS_MAP["calc_power"](2, 10))

# 测试天气
print("天气:", tools.TOOLS_MAP["get_weather"]("成都"))