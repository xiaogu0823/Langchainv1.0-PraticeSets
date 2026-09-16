"""多智能体助手，功能如下：
1.search weather 
2.math
3.datetime
4.moeny change
5.search Infomation
"""
import os
from dotenv import load_dotenv


from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool


from pydantic import BaseModel, Field
import json
from datetime import datetime
from typing import Literal, List, Optional

import math

load_dotenv()

API_KEY = os.environ.get('SILICONFLOW_API_KEY', None)
BASE_URL = os.environ.get('SILICONFLOW_BASE_URL', None)

@tool
def get_weather(city: str) -> str:
    weather_db = {"北京": "多云"}
    result = weather_db.get(city)
    return result
    

@tool
def caculator(expression: str) -> str:
    try:
        safe_functions = {
            "sqrt":math.sqrt,
            "abs":abs,
            "cos":math.cos
        }
        result = eval(expression, {"__builtins__":{}}, safe_functions)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算出错： {str(e)}\n 提示：请检查表达式格式，支持sqrt, abs..."

@tool
def get_date_info(query_type: str = "current") -> str:
    """
        Args：
        keyword:关键字
        categroy:分类筛选
        """
    now = datetime.now()

    if query_type == "current":
        return now.strftime("当前时间 ： %Y年%m月%d日 %H:%M:%S")
    if query_type == "date":
        return now.strftime("今天是 ： %Y年%m月%d日")
    elif query_type == "weekday":
        weekdays = ["Monday","Tuesday","Wednesday","Thurday","Friday","Saturday","Sunday"]
        return f"今天是{weekdays[now.weekday()]}"
    else:
        return f'无法识别的查询类型{query_type}，可用选项：current、date、time、year、month、day、weekday、iso、timestamp、week_number'


@tool
def covert_currency(amount: float, from_curr: str, to_curr:str) -> str:
    """货币转换"""
    pass

@tool
def search_info(keyword: str, categroy: str = "all") -> str:
    """高级检索
        Args：
        keyword:关键字
        categroy:分类筛选
        """
    pass

class MutiFunctionAssistant:
    """高级检索器"""
    def __init__(self):
        self.qwen_model = init_chat_model(
            "Qwen/Qwen3-8B",
            model_provider="openai",
            base_url=BASE_URL,
            api_key=API_KEY,
            temperature=0.0
            # extra_body={"enable_thinking": enable_thinking},# qwen模型默认开启CoT
        )

        self.tools = [
            get_weather,
            caculator,
            get_date_info,
            covert_currency,
            search_info
        ]

        self.system_prompt="""你是一个多功能助手，可以帮助用户：
            查询天气:使用 get_weather工具
            数学计算:使用 caculator工具
            时间查询:使用 get_date_info工具
            货币转换:使用 covert_currency工具
            信息检索:使用 search_info工具

            重要提示：
            1.仔细阅读用户需求，确定使用哪个工具
            2.需要多个工具时，按顺序调用
            3.工具返回的数据请处理为容易理解的内容
            4.任务无法完成时请真实的回复用户

        """
        self.agent = create_agent(
            model=self.qwen_model,
            tools=self.tools,
            system_prompt=self.system_prompt
        )

        self.messages = []

    def chat(self, user_input: str) -> str:
        """对话接口"""
        # 用户消息
        self.messages.append({"role":"user","content":user_input})
        # 调用agent
        result = self.agent.invoke({"messages":self.messages})
        self.messages = result["messages"]
        for msg in reversed(self.messages):
            if msg.type == "ai" and msg.content:
                return msg.content

        return "抱歉， 我无法处理该请求"

    def reset(self):
        """重置对话历史"""
        self.messages

def main():
    mutilfunctionassistant = MutiFunctionAssistant()
    print("-" * 40)
    print(f'Mutil-Function（langchain 1.0）')
    print("-" * 40)
    product = """
        1.查询天气
        2.数学计算
        3.时间查询
        4.货币转换
        5.信息检索
        输入"quit" 退出，输入 "reset" 重置会话
        """
    print(product)

    while True:

        user_input = input()

        if user_input.strip().lower() == "quit":
            print("退出对话")
            break

        if user_input.strip().lower() == "reset":
            mutilfunctionassistant.reset()
            print("对话已重置")
            break

        response = mutilfunctionassistant.chat(user_input)
        print(f"AI : {response}")

 
if __name__ == "__main__":
    main()
