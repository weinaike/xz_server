import time
import numpy as np
import torch
import opuslib_next
import onnxruntime as ort
from transformers import WhisperFeatureExtractor
from config.logger import setup_logging
from core.providers.vad.base import VADProviderBase

TAG = __name__
logger = setup_logging()


class VADProvider(VADProviderBase):
    def __init__(self, config):
        logger.bind(tag=TAG).info("SileroVAD", config)
        self.model, _ = torch.hub.load(
            repo_or_dir=config["model_dir"],
            source="local",
            model="silero_vad",
            force_reload=False,
        )

        self.decoder = opuslib_next.Decoder(16000, 1)

        # 处理空字符串的情况
        threshold = config.get("threshold", "0.5")
        min_silence_duration_ms = config.get("min_silence_duration_ms", "1000")

        self.vad_threshold = float(threshold) if threshold else 0.5
        self.silence_threshold_ms = (
            int(min_silence_duration_ms) if min_silence_duration_ms else 1000
        )

        # Smart-turn 模型集成
        use_smart_turn = config.get("use_smart_turn", "False")
        # 处理字符串转布尔值
        self.use_smart_turn = use_smart_turn.lower() in ('true')
        
        self.smart_turn_session = None
        self.feature_extractor = None
        smart_turn_threshold = config.get("smart_turn_threshold", "0.5")
        # 确保转换为float类型
        self.smart_turn_threshold = float(smart_turn_threshold) if smart_turn_threshold else 0.5
        
        # 控制是否使用短音频模式（5秒音频+3秒零填充）
        enable_short = config.get("enable_short", "True")
        # 处理字符串转布尔值
        self.enable_short = enable_short.lower() in ('true', '1', 'yes')        
        
        if self.use_smart_turn:
            smart_turn_model_path = config.get("smart_turn_model_path", "models/smart-turn/smart-turn-v3.0.onnx")
            try:
                # 初始化ONNX模型
                so = ort.SessionOptions()
                so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                so.inter_op_num_threads = 1
                so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                self.smart_turn_session = ort.InferenceSession(smart_turn_model_path, sess_options=so)
                
                # 初始化Whisper特征提取器
                self.feature_extractor = WhisperFeatureExtractor(chunk_length=8)
                
                logger.bind(tag=TAG).info(f"Smart-turn model loaded from {smart_turn_model_path}")
            except Exception as e:
                logger.bind(tag=TAG).error(f"Failed to load smart-turn model: {e}")
                self.use_smart_turn = False

    def _truncate_audio_to_last_n_seconds(self, audio_array, n_seconds=8, sample_rate=16000):
        """
        截取音频到最后n秒或填充零到n秒
        
        Args:
            audio_array: 输入音频数组
            n_seconds: 总时长（秒），默认8秒
            sample_rate: 采样率，默认16000
            
        Returns:
            处理后的音频数组，长度为 n_seconds * sample_rate
        """
        max_samples = n_seconds * sample_rate
        
        if self.enable_short:
            # 新策略：最后5秒信号 + 尾部填充零
            signal_seconds = 5
            signal_samples = signal_seconds * sample_rate
            padding_samples = max_samples - signal_samples
            
            # 获取最后signal_seconds秒的音频（如果音频少于signal_seconds秒，则全部使用）
            if len(audio_array) > signal_samples:
                signal_part = audio_array[-signal_samples:]
            else:
                # 如果音频短于signal_seconds，在开头填充零
                signal_part = np.pad(audio_array, (signal_samples - len(audio_array), 0), 
                                    mode='constant', constant_values=0)
            
            # 添加尾部填充零
            zeros_padding = np.zeros(padding_samples, dtype=audio_array.dtype)
            return np.concatenate([signal_part, zeros_padding])
        else:
            # 原始策略：截取到最后n秒或在开头填充零
            if len(audio_array) > max_samples:
                return audio_array[-max_samples:]
            elif len(audio_array) < max_samples:
                # 在开头填充零
                padding = max_samples - len(audio_array)
                return np.pad(audio_array, (padding, 0), mode='constant', constant_values=0)
            return audio_array

    def _predict_endpoint(self, audio_array):
        """
        预测音频段是否完整（轮次结束）或不完整
        
        Args:
            audio_array: 包含16kHz采样率音频样本的Numpy数组
            
        Returns:
            字典包含预测结果：
            - prediction: 1表示完整，0表示不完整
            - probability: 完成概率（sigmoid输出）
        """
        if not self.use_smart_turn or self.smart_turn_session is None:
            return {"prediction": 1, "probability": 1.0}
        
        try:
            # 截取到8秒（保留结尾）或填充到8秒
            audio_array = self._truncate_audio_to_last_n_seconds(audio_array, n_seconds=8)
            
            # 使用Whisper的特征提取器处理音频
            inputs = self.feature_extractor(
                audio_array,
                sampling_rate=16000,
                return_tensors="np",
                padding="max_length",
                max_length=8 * 16000,
                truncation=True,
                do_normalize=True,
            )
            
            # 提取特征并确保ONNX的正确形状
            input_features = inputs.input_features.squeeze(0).astype(np.float32)
            input_features = np.expand_dims(input_features, axis=0)  # 添加批次维度
            
            # 运行ONNX推理
            outputs = self.smart_turn_session.run(None, {"input_features": input_features})
            
            # 提取概率（ONNX模型返回sigmoid概率）
            probability = outputs[0][0].item()
            
            # 做出预测（1表示完整，0表示不完整）
            prediction = 1 if probability > self.smart_turn_threshold else 0
            
            return {
                "prediction": prediction,
                "probability": probability,
            }
        except Exception as e:
            logger.bind(tag=TAG).error(f"Smart-turn prediction error: {e}")
            # 出错时默认认为已完成
            return {"prediction": 1, "probability": 1.0}

    def is_vad(self, conn, opus_packet):
        try:            
            pcm_frame = self.decoder.decode(opus_packet, 960)
            conn.client_audio_buffer.extend(pcm_frame)  # 将新数据加入缓冲区

            # 初始化smart-turn的PCM缓冲区（如果不存在）
            if not hasattr(conn, 'smart_turn_audio_buffer'):
                conn.smart_turn_audio_buffer = np.array([], dtype=np.float32)

            # 处理缓冲区中的完整帧（每次处理512采样点）
            client_have_voice = False
            while len(conn.client_audio_buffer) >= 512 * 2:
                # 提取前512个采样点（1024字节）
                chunk = conn.client_audio_buffer[: 512 * 2]
                conn.client_audio_buffer = conn.client_audio_buffer[512 * 2 :]

                # 转换为模型需要的张量格式（一次转换，两处使用）
                audio_int16 = np.frombuffer(chunk, dtype=np.int16)
                audio_float32 = audio_int16.astype(np.float32) / 32768.0
                audio_tensor = torch.from_numpy(audio_float32)
                
                # 同步积累到smart-turn缓冲区（优化：复用已转换的float32数据）
                if self.use_smart_turn:
                    conn.smart_turn_audio_buffer = np.concatenate([conn.smart_turn_audio_buffer, audio_float32])
                    
                    # 限制缓冲区大小，最多保留10秒的音频（预留余量）
                    max_samples = 10 * 16000
                    if len(conn.smart_turn_audio_buffer) > max_samples:
                        conn.smart_turn_audio_buffer = conn.smart_turn_audio_buffer[-max_samples:]

                # 检测语音活动
                with torch.no_grad():
                    speech_prob = self.model(audio_tensor, 16000).item()
                client_have_voice = speech_prob >= self.vad_threshold

                # 如果之前有声音，但本次没有声音，且与上次有声音的时间差已经超过了静默阈值，则进行双重判断
                if conn.client_have_voice and not client_have_voice and conn.client_have_voice_last_time > 0:
                    stop_duration = (
                        time.time() * 1000 - conn.client_have_voice_last_time
                    )
                    if stop_duration >= self.silence_threshold_ms:
                        # Silero VAD检测到静默，现在用smart-turn模型进行二次确认
                        smart_turn_confirmed = True
                        if self.use_smart_turn and len(conn.smart_turn_audio_buffer) >= 16000:
                            result = self._predict_endpoint(conn.smart_turn_audio_buffer)
                            smart_turn_confirmed = result["prediction"] == 1
                            logger.bind(tag=TAG).debug(
                                f"Smart-turn prediction: {result['prediction']}, "
                                f"probability: {result['probability']:.4f}"
                            )
                        
                        # 只有当smart-turn模型也确认对话结束时，才设置client_voice_stop
                        if smart_turn_confirmed:
                            conn.client_voice_stop = True
                            logger.bind(tag=TAG).info("Voice stop confirmed by both Silero VAD and Smart-turn model")
                            # 清空smart-turn缓冲区
                            if self.use_smart_turn:
                                conn.smart_turn_audio_buffer = np.array([], dtype=np.float32)
                        else:
                            logger.bind(tag=TAG).info("Voice stop detected by Silero VAD but rejected by Smart-turn model")
                            conn.client_have_voice_last_time = time.time() * 1000
                
                if client_have_voice:
                    conn.client_have_voice = True
                    conn.client_have_voice_last_time = time.time() * 1000

            return client_have_voice
        except opuslib_next.OpusError as e:
            logger.bind(tag=TAG).info(f"解码错误: {e}")
        except Exception as e:
            logger.bind(tag=TAG).error(f"Error processing audio packet: {e}")
