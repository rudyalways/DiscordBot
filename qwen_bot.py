import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-0e9e036bc5ac479b89f2fabd7e3df4b7", # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 通过 messages 数组实现上下文管理
messages = [
    {'role': 'user', 'content': '你是一个直播平台运营，想要引导抖音的主播到你的平台去直播。请给一个开场白。回答需要像在对话聊天一样。不要太长，只要回答聊天内容。'}
]

completion = client.chat.completions.create(
    model="deepseek-r1-distill-qwen-32b",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
    messages=messages
)

print("="*20+"第一轮对话"+"="*20)
# 通过reasoning_content字段打印思考过程
print("="*20+"思考过程"+"="*20)
print(completion.choices[0].message.reasoning_content)
# 通过content字段打印最终答案
print("="*20+"最终答案"+"="*20)
print(completion.choices[0].message.content)

messages.append({'role': 'assistant', 'content': completion.choices[0].message.content})
messages.append({'role': 'user', 'content': '你们平台有什么优势呢?'})
print("="*20+"第二轮对话"+"="*20)
completion = client.chat.completions.create(
    model="deepseek-r1",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
    messages=messages
)
# 通过reasoning_content字段打印思考过程
print("="*20+"思考过程"+"="*20)
print(completion.choices[0].message.reasoning_content)
# 通过content字段打印最终答案
print("="*20+"最终答案"+"="*20)
print(completion.choices[0].message.content)