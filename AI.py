from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-BQ3pzHPLzQkJIgDfom0DlwXsN6278JsnI8Ac3UGL7Ol79KMe",
    base_url="https://api.moonshot.cn/v1",
)

# 定义系统提示，明确限制输出格式
system_prompt = """
你是月之暗面（Kimi）的智能客服，你负责回答用户提出的各种问题。请参考文档内容回复用户的问题。

请使用如下 JSON 格式输出你的回复：
{
    "text": "文字信息"
}

注意：
1. 只能返回 `text` 字段，不能包含 `image` 或 `url` 字段。
2. `text` 字段中只能包含文字信息。
"""

# 调用 API 生成回复
completion = client.chat.completions.create(
    model="moonshot-v1-8k",
    messages=[
        {"role": "system", "content": system_prompt},  # 明确限制输出格式
        {"role": "user", "content": "帮我写个代码，输出hello world,c语言输出"}
    ],
    temperature=0.3,
    response_format={"type": "json_object"},  # 指定输出格式为 JSON
)

# 直接打印完整的 JSON 响应
print(completion.choices[0].message.content)