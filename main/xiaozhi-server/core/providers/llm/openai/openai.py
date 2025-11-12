from typing import Dict, Iterable, List, Optional

import openai
from openai import NOT_GIVEN
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletionToolParam
from config.logger import setup_logging
from core.utils.util import check_model_key
from core.providers.llm.base import LLMProviderBase

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    PARAMS = {
        "max_tokens": (500, int),
        "temperature": (0.7, lambda v: round(float(v), 1)),
        "top_p": (1.0, lambda v: round(float(v), 1)),
        "frequency_penalty": (0, lambda v: round(float(v), 1)),
    }
    def __init__(self, config):
        super().__init__(config)
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        if "base_url" in config:
            self.base_url = config.get("base_url")
        else:
            self.base_url = config.get("url")

        self.max_tokens = 500
        self.temperature = 0.7
        self.top_p = 1.0
        self.frequency_penalty = 0.0
        for name, (default, cast) in self.PARAMS.items():
            value = config.get(name)
            try:
                setattr(self, name, cast(value) if value not in (None, "") else default)
            except (TypeError, ValueError):
                setattr(self, name, default)

        logger.debug(
            f"意图识别参数初始化: {self.temperature}, {self.max_tokens}, {self.top_p}, {self.frequency_penalty}")

        check_model_key("LLM", self.api_key)
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
    @staticmethod
    def normalize_dialogue(dialogue):
        """自动修复 dialogue 中缺失 content 的消息"""
        for msg in dialogue:
            if "role" in msg and "content" not in msg:
                msg["content"] = ""
        return dialogue
    def response(self, session_id, dialogue, **kwargs):
        try:
            logger.bind(tag=TAG).debug(f"messages for openai:\n {dialogue}")
            dialogue = self.normalize_dialogue(dialogue)
            
            # 构建额外参数，用于禁用思考功能
            extra_body = kwargs.get("extra_body", {})
            if "thinking" not in extra_body:
                extra_body["thinking"] = {"type": "disabled"}
            
            responses = self.client.chat.completions.create(
                model=self.model_name,
                messages=dialogue,
                stream=True,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                frequency_penalty=kwargs.get("frequency_penalty", self.frequency_penalty),
                extra_body=extra_body,
            )

            is_active = True
            reasoning_parts = []  # 收集推理内容
            for chunk in responses:
                # logger.bind(tag=TAG).debug(f"Received chunk: {chunk}")
                
                if self.conn and self.conn.client_abort:
                    logger.bind(tag=TAG).info(f"Client aborted the connection, stopping streaming.")
                    responses.close()
                    break
                try:
                    # 检查是否存在有效的choice且content不为空
                    choice = chunk.choices[0] if getattr(chunk, "choices", None) else None
                    if not choice:
                        continue
                    
                    delta = choice.delta
                    finish_reason = getattr(choice, "finish_reason", None)
                    
                    content = ""
                    reasoning_content = ""
                    if delta:
                        delta_content = getattr(delta, "content", None)
                        delta_reasoning = getattr(delta, "reasoning_content", None)
                        if delta_content:
                            content = delta_content
                        if delta_reasoning:
                            reasoning_content = delta_reasoning
                            reasoning_parts.append(reasoning_content)
                    
                    # 检查是否完成并输出完整推理日志
                    if finish_reason == "stop" and reasoning_parts:
                        full_reasoning = "".join(reasoning_parts)
                        logger.bind(tag=TAG).info(f"完整推理过程: {full_reasoning}")
                        reasoning_parts = []  # 清空收集的内容
                        
                except IndexError:
                    content = ""
                if content:
                    # 处理标签跨多个chunk的情况
                    if "<think>" in content:
                        is_active = False
                        content = content.split("<think>")[0]
                    if "</think>" in content:
                        is_active = True
                        content = content.split("</think>")[-1]
                    if is_active:
                        yield content

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in response generation: {e}")
            yield f"不好意思，没听清楚，请你再说一遍！"

    def response_with_functions(
        self,
        session_id,
        dialogue,
        functions = None,
    ):
        try:
            logger.bind(tag=TAG).debug(f"messages for openai:\n: {dialogue}, \n functions: {functions}")
            tools = functions if functions else NOT_GIVEN
            dialogue = self.normalize_dialogue(dialogue)
            
            # 禁用思考功能
            extra_body = {"thinking": {"type": "disabled"}}
            
            stream = self.client.chat.completions.create(
                model=self.model_name, messages=dialogue, stream=True, tools=tools,
                extra_body=extra_body
            )

            reasoning_parts = []  # 收集推理内容
            for chunk in stream:
                # 检查是否存在有效的choice且content不为空
                if self.conn and self.conn.client_abort:
                    logger.bind(tag=TAG).info(f"Client aborted the connection, stopping function call streaming.")
                    stream.close()
                    break
                if getattr(chunk, "choices", None):
                    choice = chunk.choices[0]
                    delta = choice.delta
                    finish_reason = getattr(choice, "finish_reason", None)
                    
                    content = getattr(delta, "content", "") or ""
                    reasoning_content = getattr(delta, "reasoning_content", None)
                    if reasoning_content:
                        reasoning_parts.append(reasoning_content)
                    
                    # 检查是否完成并输出完整推理日志
                    if finish_reason == "stop" and reasoning_parts:
                        full_reasoning = "".join(reasoning_parts)
                        logger.bind(tag=TAG).info(f"完整推理过程: {full_reasoning}")
                        reasoning_parts = []  # 清空收集的内容
                    
                    tool_calls = getattr(delta, "tool_calls", None)
                    yield content, tool_calls
                # 存在 CompletionUsage 消息时，生成 Token 消耗 log
                elif isinstance(getattr(chunk, 'usage', None), CompletionUsage):
                    usage_info = getattr(chunk, 'usage', None)
                    logger.bind(tag=TAG).info(
                        f"Token 消耗：输入 {getattr(usage_info, 'prompt_tokens', '未知')}，" 
                        f"输出 {getattr(usage_info, 'completion_tokens', '未知')}，"
                        f"共计 {getattr(usage_info, 'total_tokens', '未知')}"
                    )

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in function call streaming: {e}")
            yield f"不好意思，没听清楚，请你再说一遍！", None
