from ..base import MemoryProviderBase, logger
import time
import json
import os
import yaml
from config.config_loader import get_project_dir
from config.manage_api_client import save_mem_local_short


short_term_memory_prompt = """
# 时空记忆编织者

## 核心使命
构建可生长的动态记忆网络，在有限空间内保留关键信息的同时，智能维护信息演变轨迹
根据对话记录，总结user的重要信息，以便在未来的对话中提供更个性化的服务

## 记忆法则
### 1. 三维度记忆评估（每次更新必执行）
| 维度       | 评估标准                  | 权重分 |
|------------|---------------------------|--------|
| 时效性     | 信息新鲜度（按对话轮次） | 40%    |
| 情感强度   | 含💖标记/重复提及次数     | 35%    |
| 关联密度   | 与其他信息的连接数量      | 25%    |

### 2. 动态更新机制
**名字变更处理示例：**
原始记忆："曾用名": ["张三"], "现用名": "张三丰"
触发条件：当检测到「我叫X」「称呼我Y」等命名信号时
操作流程：
1. 将旧名移入"曾用名"列表
2. 记录命名时间轴："2024-02-15 14:32:启用张三丰"
3. 在记忆立方追加：「从张三到张三丰的身份蜕变」

### 3. 空间优化策略
- **信息压缩术**：用符号体系提升密度
  - ✅"张三丰[北/软工/🐱]"
  - ❌"北京软件工程师，养猫"
- **淘汰预警**：当总字数≥900时触发
  1. 删除权重分<60且3轮未提及的信息
  2. 合并相似条目（保留时间戳最近的）

## 记忆结构
输出格式必须为可解析的json字符串，不需要解释、注释和说明，保存记忆时仅从对话提取信息，不要混入示例内容
```json
{
  "时空档案": {
    "身份图谱": {
      "现用名": "",
      "特征标记": [] 
    },
    "记忆立方": [
      {
        "事件": "入职新公司",
        "时间戳": "2024-03-20",
        "情感值": 0.9,
        "关联项": ["下午茶"],
        "保鲜期": 30 
      }
    ]
  },
  "关系网络": {
    "高频话题": {"职场": 12},
    "暗线联系": [""]
  },
  "待响应": {
    "紧急事项": ["需立即处理的任务"], 
    "潜在关怀": ["可主动提供的帮助"]
  },
  "高光语录": [
    "最打动人心的瞬间，强烈的情感表达，user的原话"
  ]
}
```
"""

short_term_memory_prompt_only_content = """

你是一个经验丰富的记忆总结者，擅长将对话内容进行总结摘要，遵循以下规则：
1、总结user的重要信息，以便在未来的对话中提供更个性化的服务
2、不要重复总结，不要遗忘之前记忆，不要压缩用户的历史记忆
3、用户操控的设备音量、播放音乐、天气、退出、不想对话等和用户本身无关的内容，这些信息不需要加入到总结中
4、不要把设备操控的成果结果和失败结果加入到总结中，也不要把用户的一些废话加入到总结中
5、不要为了总结而总结，如果用户的聊天没有意义，请返回原来的历史记录也是可以的
7、不要包含代码、xml，不需要解释、注释和说明，保存记忆时仅从对话提取信息，不要混入示例内容
8、为记忆设置权重和衰减机制。频繁提及的核心兴趣（如恐龙）权重高、保质期长；一时兴起的提及（如“今天我喜欢橙色”）权重低、保质期短。系统应能自动淡出不再被提及的旧记忆。

以下是一份记忆模板，基于该模板总结与更新记忆。
**模板中`（如xxx）`这类描述，只是一个示例， 不能直接作为记忆内容。 真是的记忆内容必须来源于对话。未提及相关内容可以留空。**
···
# 记忆模板
## 核心身份和档案
- 昵称：xx
- 年龄阶段：xx （如4-5岁）
- 性格特点：xx (如 活泼、好奇、情绪来得快去得也快)

## 重要人际关系网络
- 宠物昵称：xx (如 毛毛)
- 家人关系：xx （如 爸爸、妈妈、奶奶 ......)
- 好朋友：xx (如陆珂、秋月......）
- 玩偶/幻想的朋友：xx （如hellokitty, 彩虹公主......）

## 核心兴趣和热情（按照热度排序）（根据实际对话内容提取， 不要主动添加）
|兴趣|提及喜欢次数|最新提及时间|
|奥特曼|5次|2025-10-10|
|画画|1次|2024-1-5|
|工程车|3次|2025-10-5|
**提及次数， 每次对话总结只能+1， 多次对话总结，可持续叠加**
**兴趣类型相同，表述差异可合并， 提及次数也合并**
**当前最爱， 持续热爱，一般喜欢，可以更具表格中提及次数排序提炼**
**记忆冲突处理， 如果原来标记为喜欢，但是本次会话现在提及不喜欢，则需要将提及次数-1.**

1.【当前最爱】
    - xx(如奥特曼 提及次数5次， 最喜欢迪迦奥特曼，喜欢模仿发射光线的动作。（上次对话提到迪迦打败了怪兽贝利亚））

2.【持续热爱】
    - xx (如 工程车 提及次数3次，特别是挖掘机，喜欢模仿“轰隆隆”的声音。）

3.【一般喜欢】
    - xx （如 画画 提及次数 1次：喜欢画城堡和火箭。）
    - xx （如 唱歌 提及次数 2次：会唱《小星星》和《两只老虎》。）

## 重要的经历和成就， 以及最近的`项目`
- xx (学会了骑自行车：2025-6-5）
- xx (学会了拍气球：2025-10-5）
- xx（正在学骑自行车：2025-11-2）

## 情感模式与舒适物
- 开心时：会说“太棒了！”，笑声很大。
- 受挫时（如积木倒塌）：会小声说“讨厌”，需要鼓励。
- 有效的安慰方式：提议“我们数到10，再试一次好不好？”通常有效。
- 已知担忧：害怕打雷。解释为“云朵在吵架”似乎能接受。

## 认知与发展笔记
- 数字能力：xx(能熟练数1-20，在29到30时会卡住，需要提示。)
- 语言能力：xx(如 孩子的语言xxx、词汇量增加了xxx、句子长度xxx）
- 提问特点：xx (如最近爱问“为什么”类问题（如“为什么天会黑？”）。)
- 注意力：xx （如对感兴趣的话题能持续10-20轮对话，喜欢快节奏的对话轮换。）
- 诗歌能力：xx（如 孩子唐诗会背xxx)
- 唱歌能力：xx (如 会唱xxx)

## 互动小贴士（为AI提供的快速参考）
- 喜欢的互动模式：xxx()
- 高效开场白：xx（如， “今天和毛毛有什么新冒险吗？”、“奥特曼先生最近好吗？”）【根据最近的最爱和项目进行调整】
- 增强 engagement 的方法：立即进入角色扮演（如“船长，请下达指令！”），使用夸张的音效。【根据最近的最爱和项目进行调整】
- 避免的话题：暂无。
- 上次对话亮点：他主动创造了“用彩虹桥修复飞船”的情节，非常有想象力，及时给予了赞扬。

···
"""


def extract_json_data(json_code):
    start = json_code.find("```json")
    # 从start开始找到下一个```结束
    end = json_code.find("```", start + 1)
    # print("start:", start, "end:", end)
    if start == -1 or end == -1:
        try:
            jsonData = json.loads(json_code)
            return json_code
        except Exception as e:
            print("Error:", e)
        return ""
    jsonData = json_code[start + 7 : end]
    return jsonData


TAG = __name__


class MemoryProvider(MemoryProviderBase):
    def __init__(self, config, summary_memory):
        super().__init__(config)
        self.short_memory = ""
        self.save_to_file = True
        self.memory_path = get_project_dir() + "data/.memory.yaml"
        self.load_memory(summary_memory)

    def init_memory(
        self, role_id, llm, summary_memory=None, save_to_file=True, **kwargs
    ):
        super().init_memory(role_id, llm, **kwargs)
        self.save_to_file = save_to_file
        self.load_memory(summary_memory)

    def load_memory(self, summary_memory):
        # api获取到总结记忆后直接返回
        if summary_memory or not self.save_to_file:
            self.short_memory = summary_memory
            return

        all_memory = {}
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r", encoding="utf-8") as f:
                all_memory = yaml.safe_load(f) or {}
        if self.role_id in all_memory:
            self.short_memory = all_memory[self.role_id]

    def save_memory_to_file(self):
        all_memory = {}
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r", encoding="utf-8") as f:
                all_memory = yaml.safe_load(f) or {}
        all_memory[self.role_id] = self.short_memory
        with open(self.memory_path, "w", encoding="utf-8") as f:
            yaml.dump(all_memory, f, allow_unicode=True)

    async def save_memory(self, msgs):
        # 打印使用的模型信息
        model_info = getattr(self.llm, "model_name", str(self.llm.__class__.__name__))
        logger.bind(tag=TAG).debug(f"使用记忆保存模型: {model_info}")
        if self.llm is None:
            logger.bind(tag=TAG).error("LLM is not set for memory provider")
            return None

        if len(msgs) < 2:
            return None

        msgStr = ""
        for msg in msgs:
            if msg.role == "user":
                msgStr += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                msgStr += f"Assistant: {msg.content}\n"
        if self.short_memory and len(self.short_memory) > 0:
            msgStr += "历史记忆：\n"
            msgStr += self.short_memory

        # 当前时间
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msgStr += f"当前时间：{time_str}"

        if self.save_to_file:
            result = self.llm.response_no_stream(
                short_term_memory_prompt,
                msgStr,
                max_tokens=4096,
                temperature=0.2,
            )
            json_str = extract_json_data(result)
            try:
                json.loads(json_str)  # 检查json格式是否正确
                self.short_memory = json_str
                self.save_memory_to_file()
            except Exception as e:
                print("Error:", e)
        else:
            result = self.llm.response_no_stream(
                short_term_memory_prompt_only_content,
                msgStr,
                max_tokens=4096,
                temperature=0.2,
            )
            save_mem_local_short(self.role_id, result)
        logger.bind(tag=TAG).info(f"Save memory successful - Role: {self.role_id}")

        return self.short_memory

    async def query_memory(self, query: str) -> str:
        return self.short_memory
