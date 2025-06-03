<template>
  <el-dialog :visible="visible" @close="handleClose" width="60%" center :title="'添加智能体模板'">
    <AgentTemplateForm v-model="form" />
    <div style="display: flex; margin: 15px 15px; gap: 7px;">
      <div class="dialog-btn" @click="confirm">保存</div>
      <div class="dialog-btn" style="background: #e6ebff; border: 1px solid #adbdff; color: #5778ff;" @click="cancel">取消</div>
    </div>
  </el-dialog>
</template>

<script>
import Api from '@/apis/api';
import AgentTemplateForm from './AgentTemplateForm.vue';

export default {
  name: 'AddAgentTemplateDialog',
  components: { AgentTemplateForm },
  props: {
    visible: { type: Boolean, required: true }
  },
  data() {
    return {
      form: {
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
        language: ''
      }
    }
  },
  methods: {
    confirm() {
      Api.agent.createAgentTemplate(this.form, (res) => {
        if (res.data.code === 0) {
          this.$message.success({ message: '添加成功', showClose: true });
          this.$emit('confirm', res);
          this.$emit('update:visible', false);
          this.resetForm();
        } else {
          this.$message.error(res.data.msg || '添加失败');
        }
      });
    },
    cancel() {
      this.$emit('update:visible', false);
      this.resetForm();
    },
    handleClose() {
      this.$emit('update:visible', false);
      this.resetForm();
    },
    resetForm() {
      this.form = {
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
        language: ''
      };
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

::v-deep .el-dialog {
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

::v-deep .el-dialog__headerbtn {
  display: none;
}

::v-deep .el-dialog__body {
  padding: 4px 6px;
}

::v-deep .el-dialog__header {
  padding: 10px;
}

/* 解决 el-input textarea rows 无效问题，确保 rows 属性生效 */
::v-deep .el-textarea__inner {
  height: auto !important;
  min-height: unset !important;
  max-height: unset !important;
  resize: vertical;
}

</style>
