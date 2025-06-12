<template>
  <el-dialog :visible="visible" @close="handleClose" width="60%" center :title="'编辑智能体模板'">
    <AgentTemplateForm v-model="form" ref="agentForm" :isEdit="true" />
    <div style="display: flex; margin: 15px 15px; gap: 7px;">
      <div class="dialog-btn" @click="confirm">保存</div>
      <div class="dialog-btn" style="background: #e6ebff; border: 1px solid #adbdff; color: #5778ff;" @click="cancel">取消</div>
    </div>
  </el-dialog>
</template>

<script>
import AgentTemplateForm from './AgentTemplateForm.vue';

export default {
  name: 'EditAgentTemplateDialog',
  components: { AgentTemplateForm },
  props: {
    visible: { type: Boolean, required: true },
    templateData: { type: Object, default: null }
  },
  data() {
    return {
      form: this.templateData ? { ...this.templateData } : {
        agentName: '',
        vadModelId: '',        
        asrModelId: '',
        intentModelId: '',
        llmModelId: '',
        memModelId: '',        
        ttsModelId: '',
        ttsVoiceId: '',
        chatHistoryConf: 0,
        systemPrompt: '',
        langCode: '',
        language: '',
        version: '100'
      }
    }
  },
  watch: {
    templateData: {
      immediate: true,
      handler(val) {
        if (val) {
          // 编辑时，version 默认显示原值+1
          this.form = { ...val, version: (parseInt(val.version || 100, 10) + 1).toString() };
        }
      }
    }
  },
  methods: {
    confirm() {
      this.$refs.agentForm.$refs.formRef.validate((valid) => {
        if (!valid) return;
        this.$emit('confirm', { ...this.form });
      });
    },
    cancel() {
      this.$emit('cancel');
    },
    handleClose() {
      this.$emit('cancel');
    }
  }
}
</script>

<style scoped>
.dialog-btn {
  cursor: pointer;
  flex: 1;
  border-radius: 23px;
  background: #5778ff;
  height: 40px;
  font-weight: 500;
  font-size: 12px;
  color: #fff;
  line-height: 40px;
  text-align: center;
}

/* 解决 el-input textarea rows 无效问题，确保 rows 属性生效 */
::v-deep .el-textarea__inner {
  height: auto !important;
  min-height: unset !important;
  max-height: unset !important;
  resize: vertical;
}
</style>
