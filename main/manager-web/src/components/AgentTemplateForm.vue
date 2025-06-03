<template>
  <el-form :model="form" ref="formRef" label-width="120px" :rules="rules">
    <div class="form-grid">
      <div class="form-column">
        <el-form-item label="模板名称" prop="agentName" required>
          <el-input v-model="form.agentName" maxlength="20" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="角色设定参数" prop="systemPrompt" required>
          <el-input type="textarea" v-model="form.systemPrompt" rows="8" maxlength="2000" show-word-limit placeholder="请输入角色设定参数" />
        </el-form-item>
        <el-form-item label="聊天记录配置" prop="chatHistoryConf" required>
          <el-radio-group v-model="form.chatHistoryConf">
            <el-radio :label="0">不记录</el-radio>
            <el-radio :label="1">仅文本</el-radio>
            <el-radio :label="2">文本和语音</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="语言编码" prop="langCode" required>
          <el-input v-model="form.langCode" maxlength="10" placeholder="如 zh_CN/zh_HK/en_US/ja_JP等" />
        </el-form-item>
        <el-form-item label="交互语种" prop="language" required>
          <el-input v-model="form.language" maxlength="10" placeholder="如 中文" />
        </el-form-item>
      </div>
      <div class="form-column">
        <el-form-item label="语音活动检测" prop="vadModelId" required>
          <el-select v-model="form.vadModelId" filterable placeholder="请选择VAD模型">
            <el-option v-for="item in modelOptions.VAD" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="语音识别模型" prop="asrModelId" required>
          <el-select v-model="form.asrModelId" filterable placeholder="请选择ASR模型">
            <el-option v-for="item in modelOptions.ASR" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="意图模型" prop="intentModelId" required>
          <el-select v-model="form.intentModelId" filterable placeholder="请选择意图模型">
            <el-option v-for="item in modelOptions.Intent" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>                
        <el-form-item label="大语言模型" prop="llmModelId" required>
          <el-select v-model="form.llmModelId" filterable placeholder="请选择LLM模型">
            <el-option v-for="item in modelOptions.LLM" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="记忆模型" prop="memModelId" required>
          <el-select v-model="form.memModelId" filterable placeholder="请选择记忆模型">
            <el-option v-for="item in modelOptions.Memory" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>        
        <el-form-item label="语音合成模型" prop="ttsModelId" required>
          <el-select v-model="form.ttsModelId" filterable placeholder="请选择TTS模型" @change="fetchVoiceOptions">
            <el-option v-for="item in modelOptions.TTS" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="音色标识" prop="ttsVoiceId" required>
          <el-select v-model="form.ttsVoiceId" filterable placeholder="请选择音色">
            <el-option v-for="item in voiceOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </div>
    </div>
  </el-form>   
</template>

<script>
import Api from '@/apis/api';

export default {
  name: 'AgentTemplateForm',
  props: {
    value: { type: Object, required: true }
  },
  data() {
    return {
      modelOptions: {
        VAD: [], ASR: [], Intent: [], LLM: [], Memory: [], TTS: []
      },
      voiceOptions: [],
      rules: {
        agentName: [
          { required: true, message: '请输入模板名称', trigger: 'blur' }
        ],
        vadModelId: [
          { required: true, message: '请选择语音活动检测模型', trigger: 'change' }
        ],
        asrModelId: [
          { required: true, message: '请选择语音识别模型', trigger: 'change' }
        ],
        intentModelId: [
          { required: true, message: '请选择意图模型', trigger: 'change' }
        ],
        llmModelId: [
          { required: true, message: '请选择大语言模型', trigger: 'change' }
        ],
        memModelId: [
          { required: true, message: '请选择记忆模型', trigger: 'change' }
        ],
        ttsModelId: [
          { required: true, message: '请选择语音合成模型', trigger: 'change' }
        ],
        ttsVoiceId: [
          { required: true, message: '请选择音色', trigger: 'change' }
        ],
        chatHistoryConf: [
          { required: true, message: '请选择聊天记录配置', trigger: 'change' }
        ],
        systemPrompt: [
          { required: true, message: '请输入角色设定参数', trigger: 'blur' }
        ],
        langCode: [
          { required: true, message: '请输入语言编码', trigger: 'blur' }
        ],
        language: [
          { required: true, message: '请输入交互语种', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    form: {
      get() { return this.value },
      set(val) { this.$emit('input', val) }
    }
  },
  watch: {
    'form.ttsModelId': {
      handler(newVal) {
        if (newVal) this.fetchVoiceOptions(newVal);
      },
      immediate: true
    }
  },
  mounted() {
    this.fetchModelOptions();
    if (this.form.ttsModelId) {
      this.fetchVoiceOptions(this.form.ttsModelId);
    }
  },
  methods: {
    fetchModelOptions() {
      const types = [
        { type: 'VAD', key: 'VAD' },
        { type: 'ASR', key: 'ASR' },
        { type: 'LLM', key: 'LLM' },
        { type: 'TTS', key: 'TTS' },
        { type: 'Memory', key: 'Memory' },
        { type: 'Intent', key: 'Intent' }
      ];
      types.forEach(({ type, key }) => {
        Api.model.getModelNames(type, '', ({ data }) => {
          if (data.code === 0) {
            this.$set(this.modelOptions, key, data.data.map(item => ({ value: item.id, label: item.modelName })));
          }
        });
      });
    },
    fetchVoiceOptions(modelId) {
      if (!modelId) {
        this.voiceOptions = [];
        return;
      }
      Api.model.getModelVoices(modelId, '', ({ data }) => {
        if (data.code === 0 && data.data) {
          this.voiceOptions = data.data.map(voice => ({ value: voice.id, label: voice.name }));
        } else {
          this.voiceOptions = [];
        }
      });
    },
    validate() {
      return this.$refs.formRef.validate();
    }
  }
}
</script>

<style scoped>

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.form-column {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

</style>
