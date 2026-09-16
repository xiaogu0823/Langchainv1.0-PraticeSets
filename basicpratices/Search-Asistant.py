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

load_dotenv()

API_KEY = os.environ.get('SILICONFLOW_API_KEY', None)
BASE_URL = os.environ.get('SILICONFLOW_BASE_URL', None)

class SearchAssistant:
    """高级检索器"""
    def __init__(self):
        self.qwen_model = init_chat_model(
            "Qwen/Qwen3-8B",
            model_provider="openai",
            base_url=BASE_URL,
            api_key=API_KEY,
            temperature=0.9
            # extra_body={"enable_thinking": enable_thinking},# qwen模型默认开启CoT
        )



class SearchParams(BaseModel):
    """检索参数"""
    keyward: str = Field(description="关键字检索")
    max_results: int = Field(default=5, description="检索结果最大限制")
    categroy: Optional[str] = Field(description="分类筛选")


@tool
def advanced_search(param: SearchParams) -> str:
    results = f"搜索 ‘{param.keyward}’"
    if param.categroy:
        results += f"在分类 ‘{param.categroy}’"
    results += f"返回前 {param.max_results}结果"

    return results

@tool
def get_product_info(self, product_id: str) -> str:
    """获取产品详情"""
    products = {
        "p01":{
            "name":"iphone",
            "price":"5000",
            "version":"pro"
        },
        "p05":{
            "name":"vivo plus 7",
            "price":"4000",
            "rating":"x70"
        },
        "p001":{
            "name":"xiaomi",
            "price":"5889",
            "rating":"pro"
        },
    }

    product = products.get(product_id, {"error": "产品不存在"})
    return json.dump(product, ensure_ascii=False)

import asyncio

@tool
async def fetch_data_async(url: str) -> str:
    """异步获取网络数据
    Args:
        url: 目标url
    """
    # 模拟虚拟请求
    await asyncio.sleep(1)
    return f"从 {url}中获取的数据"

serch_model = SearchAssistant()
agent = create_agent(
    model=serch_model,
    tools=tool,
)
# 使用异步 agent
result = await agent.ainvoke(