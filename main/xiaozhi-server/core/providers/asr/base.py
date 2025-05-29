from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
import opuslib_next
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class ASRProviderBase(ABC):
    def __init__(self):
        self.audio_format = "opus"

    @abstractmethod
    def save_audio_to_file(self, pcm_data: List[bytes], session_id: str) -> str:
        """PCM数据保存为WAV文件"""
        pass

    @abstractmethod
    async def speech_to_text(
        self, opus_data: List[bytes], session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """将语音数据转换为文本"""
        pass

    def set_audio_format(self, format: str) -> None:
        """设置音频格式"""
        self.audio_format = format

    @staticmethod
    def decode_opus(opus_data: List[bytes]) -> bytes:
        """将Opus音频数据解码为PCM数据"""
        try:
            decoder = opuslib_next.Decoder(16000, 1)  # 16kHz, 单声道
            pcm_data = []
            buffer_size = 960  # 每次处理960个采样点

            for opus_packet in opus_data:
                try:
                    # 使用较小的缓冲区大小进行处理
                    pcm_frame = decoder.decode(opus_packet, buffer_size)
                    if pcm_frame:
                        pcm_data.append(pcm_frame)
                except opuslib_next.OpusError as e:
                    logger.bind(tag=TAG).warning(f"Opus解码错误，跳过当前数据包: {e}")
                    continue
                except Exception as e:
                    logger.bind(tag=TAG).error(f"音频处理错误: {e}", exc_info=True)
                    continue

            return pcm_data
        except Exception as e:
            logger.bind(tag=TAG).error(f"音频解码过程发生错误: {e}", exc_info=True)
            return []
