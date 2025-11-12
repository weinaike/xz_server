from abc import ABC, abstractmethod
from typing import Any, Generator, Optional, Tuple, TYPE_CHECKING

from config.logger import setup_logging

if TYPE_CHECKING:
    from core.connection import ConnectionHandler

TAG = __name__
logger = setup_logging()

class LLMProviderBase(ABC):
    def __init__(self, config):
        self.conn: Optional["ConnectionHandler"] = None
    @abstractmethod
    def response(self, session_id, dialogue) -> Generator[str, None, None]:
        """LLM response generator"""
        ...

    def response_no_stream(self, system_prompt, user_prompt, **kwargs):
        try:
            # 构造对话格式
            dialogue = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            result = ""
            for part in self.response("", dialogue, **kwargs):
                result += part
            return result

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in Ollama response generation: {e}")
            return "【LLM服务响应异常】"
    
    def response_with_functions(
        self, session_id, dialogue, functions=None
    ) -> Generator[Tuple[str, Optional[Any]], None, None]:
        """
        Default implementation for function calling (streaming)
        This should be overridden by providers that support function calls

        Returns: generator that yields either text tokens or a special function call token
        """
        # For providers that don't support functions, just return regular response
        for token in self.response(session_id, dialogue):
            yield token, None

    def set_connection(self, conn: "ConnectionHandler"):
        self.conn = conn