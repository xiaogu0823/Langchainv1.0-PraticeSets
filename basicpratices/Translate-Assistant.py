import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, content

load_dotenv()

API_KEY = os.environ.get('SILICONFLOW_API_KEY', None)
BASE_URL = os.environ.get('SILICONFLOW_BASE_URL', None)
# print(f'API_KEY:{API_KEY}')

class TranslaterAssistant():
    def __init__(self):
        self.qwen_model = init_chat_model(
            "Qwen/Qwen3-8B",
            model_provider="openai",
            base_url=BASE_URL,
            api_key=API_KEY,
            # extra_body={"enable_thinking": enable_thinking},# qwen模型默认开启CoT
        )

    def translator_func(self, text:str, taret_lang:str = "中文", style:str = "正式"):
        system_prompt = f"""你是一个高效、精准的机器辅助翻译助手。
            任务：
            1.自动检测输入文本的语言
            2.翻译为{taret_lang}
            3.使用{style}
            4.如果有专业术语。翻译后需要标注原文
            限制与要求：
            1. 零废话：直接输出翻译结果，不要包含“以下是翻译内容”等前缀。
            2. 一致性：保持术语统一，不引入同义词替换。

            输入格式：
            【原文】：
            【译文】：
            【术语解析】：
            """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=text)
        ]

        # response = self.qwen_model.invoke(messages)
        return self.qwen_model.stream(messages)

def main():
    translator = TranslaterAssistant()
    print(f'智能翻译助手（langchain 1.0）')

    while True:
        print("\n")
        user_input=input("请输入需要翻译内容：")
        if user_input.strip().lower() == "exit":
            print("退出对话")
            break

        user_lang=input("请输入目标语言：")
        user_style=input("请输入翻译风格（口语/正式）：")
        translate_result = translator.translator_func(user_input,user_lang,user_style)
        for chunk in translate_result:
            print(chunk.content, end="", flush=True)

if __name__ == "__main__":
    main()