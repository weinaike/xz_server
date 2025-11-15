from ..base import IntentProviderBase
from typing import List, Dict
from core.connection import ConnectionHandler
from config.logger import setup_logging
import re
import json

import time

TAG = __name__
logger = setup_logging()


class IntentProvider(IntentProviderBase):
    def __init__(self, config):
        super().__init__(config)
        self.llm = None
        self.history_count = 4  # 默认使用最近4条对话记录
        self.disabled = True  # 是否启用纠正功能

    async def detect_intent(self, conn:ConnectionHandler, dialogue_history: List[Dict], text: str) -> str:
        if self.disabled:
            return  json.dumps({"function_call": {"name": "continue_chat","true_content": text}},ensure_ascii=False)
        if not self.llm:
            raise ValueError("LLM provider not set")
    
        system_prompt = '''
你是一个文字处理助手， 请分析用户的最后一句话，判断用户意图。
1. 用户输入的文字（来源于语音识别），因为语音识别过程中，可能存在同音字、发音不准、环境噪音等问题导致识别不准。需要根据上下文，尽量纠正这些错误
2. 请仅返回纠正后的内容， 不要包含任何其他文字

以json格式化输出。数据格式要求：
{
  "function_call": {
    "name": "continue_chat",
    "true_content":"(纠正后的内容)"
  }
}
"用户: 我喜欢西蓝花\n"
'返回: {"function_call": {"name": "continue_chat", "true_content":"我喜欢西兰花"}}\n'

'''

        # 构建用户对话历史的提示
        msgStr = ""

        # 获取最近的对话历史
        start_idx = max(0, len(dialogue_history) - self.history_count)
        for i in range(start_idx, len(dialogue_history)):
            msgStr += f"{dialogue_history[i].role}: {dialogue_history[i].content}\n"

        msgStr += f"User: {text}\n"
        user_prompt = f"current dialogue:\n{msgStr} + \nUser's latest input: {text} + \n格式化输出用户的真实像表达的内容是什么？（ 注意仅纠正文字，不要添加内容。）" 

        start_time = time.time()
        intent = self.llm.response_no_stream(
            system_prompt=system_prompt, user_prompt=user_prompt
        )
        logger.bind(tag=TAG).info(
            f"LLM纠正耗时: {(time.time() - start_time):.4f}秒"
        )

        # 清理和解析响应
        intent = intent.strip()
        # 尝试提取JSON部分
        match = re.search(r"\{.*\}", intent, re.DOTALL)
        if match:
            intent = match.group(0)

        # 尝试解析为JSON
        try:
            intent_data = json.loads(intent)
            # 如果包含function_call，则格式化为适合处理的格式
            function = intent_data.get("function_call")
            name = function.get("name") 
            true_content = function.get("true_content")
            # 字段完整， 则返回意图， 如果一次
            return intent
        except:
            # 如果解析失败，默认返回继续聊天意图
            return json.dumps({"function_call": {"name": "continue_chat","true_content": text}},ensure_ascii=False)