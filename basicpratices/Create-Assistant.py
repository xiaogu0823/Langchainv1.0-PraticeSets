import os
from dotenv import load_dotenv


from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from pydantic import BaseModel, Field
import json
from datetime import datetime
from typing import Literal, List

load_dotenv()

API_KEY = os.environ.get('SILICONFLOW_API_KEY', None)
BASE_URL = os.environ.get('SILICONFLOW_BASE_URL', None)
# print(f'API_KEY:{API_KEY}')

# define pydantic output
class CopyWrittingScore(BaseModel):
    """文案评分"""
    creativity: int = Field(description="创新 1-10分")
    clearty: int = Field(description="清晰 1-10分")
    interest: int = Field(description="吸引力 1-10分")
    overall: int =Field(description="综合评分1-10分")
    comment: int = Field(description="评论 1-10分")

class CopyWrittingResult(BaseModel):
    """文案结果"""
    content: str = Field(description="文案内容")
    score: CopyWrittingScore = Field(description="质量评分")

class CopyWrittingBatch(BaseModel):
    """批量文案结果"""
    copies: List[CopyWrittingResult] = Field(description="文案列表")

class CreateAssistant:
    """文案生成器"""
    def __init__(self):
        self.qwen_model = init_chat_model(
            "Qwen/Qwen3-8B",
            model_provider="openai",
            base_url=BASE_URL,
            api_key=API_KEY,
            temperature=0.9
            # extra_body={"enable_thinking": enable_thinking},# qwen模型默认开启CoT
        )
        self.structured_model = self.qwen_model.with_structured_output(CopyWrittingBatch)

    def generate_content(self, 
                         product: str,
                         copy_type: Literal["广告","社交媒体", "邮件"],
                         style: Literal["正式", "专业", "口语"],
                         count: int = 3) -> List[CopyWrittingResult]:
        
        system_prompt = f"""你是一个专业的文案撰写专家。

            任务：为以下产品创作文案

            产品信息：{product}

            要求：
            - 文案类型{copy_type}
            - 文案风格{style}
            - 文案数量{count}
            - 文案内容不能重复，可以加入emo表情丰富内容
            - 请给每个文案评分

            输入格式：请输出{count}个文案，每个文案包含内容和评分
            """
        results = self.structured_model.invoke(system_prompt)
        return results.copies

    def export_to_file(self, copies: List[CopyWrittingResult], filename: str = None):
        """导出"""
        if filename is None:
            filename = f"copywriting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            "generated_at": datetime.now().isoformat(),
            "copies":[
                {
                    "content":c.comment,
                    "score":{
                        "eativity": c.score.creativity,
                        "clearty": c.score.clearty,
                        "interest": c.score.interest,
                        "overall": c.score.overall

                    }
                }
                for c in copies
            ]
        }
        with open(filename, 'v', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename

        # print(f"综合分析： 创意：{copy.score.creativity} | 清晰度：{copy.score.clearty} | 吸引力：{copy.score.interest} | 综合：{copy.score.overall}")
        # print(f"评价： {copy.score.comment}")

def main():
    copywritting = CreateAssistant()
    print("*" * 20)
    print(f'文案撰写（langchain 1.0）')

    product = """
        产品：编程助手
        特点：
        -实时代码补全功能
        -智能代码审查纠错
        -支持Python c++ java等编程语言
        """

    copies_file = copywritting.generate_content(product=product,copy_type="博客", style="专业",count=2) 

    for i , copy in enumerate(copies_file):
        print(f"版本{i}")
        print(f"内容:{copy.content}")
        print(f"综合分析： 创意：{copy.score.creativity} | 清晰度：{copy.score.clearty} | 吸引力：{copy.score.interest} | 综合：{copy.score.overall}")
        print(f"评价： {copy.score.comment}")

    save_tip = input(f"是否保存为本地文件(y/n)?")
    if save_tip.lower == "y":
        filename = copywritting.export_to_file(copies_file)
        print(f"已保存到{filename}")


if __name__ == "__main__":
    main()