from abc import ABC, abstractmethod
from typing import Optional


class VADProviderBase(ABC):
    @abstractmethod
    def is_vad(self, conn, opus_packet) -> bool:
        """检测音频数据中的语音活动"""
        pass
