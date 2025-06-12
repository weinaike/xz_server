<template>
  <div class="device-item">
    <div style="display: flex;justify-content: space-between;">
      <div style="font-weight: 700;font-size: 18px;text-align: left;color: #3d4566;">
        {{ template.agentName }}
      </div>
      <div>
        <img src="@/assets/home/delete.png" alt="" style="width: 18px;height: 18px;margin-right: 10px;"
          @click.stop="handleDelete" />
        <el-tooltip class="item" effect="dark" :content="template.systemPrompt" placement="top"
          popper-class="custom-tooltip">
          <img src="@/assets/home/info.png" alt="" style="width: 18px;height: 18px;" />
        </el-tooltip>
      </div>
    </div>
    <div class="device-name">
      语音识别模型：{{ template.asrModelId || '未设置' }}
    </div>
    <div class="device-name">
      语音合成模型：{{ template.ttsModelId || '未设置' }}
    </div>
    <div style="display: flex;gap: 10px;align-items: center;">
      <div class="settings-btn" @click="handleEdit">
        编辑模板
      </div>
      <div v-if="!isDefault" class="settings-btn" @click="handleSetDefault">
        设为默认
      </div>
      <div v-else class="settings-btn disabled-btn">
        已默认
      </div>
    </div>
    <div class="version-info">
      <div>创建时间：{{ formattedCreatedAt }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AgentTemplateItem',
  props: {
    template: { type: Object, required: true }
  },
  computed: {
    formattedCreatedAt() {
      if (!this.template.createdAt) return '未知';
      const date = new Date(this.template.createdAt);
      return date.toLocaleString();
    },
    isDefault() {
      if (this.template.isDefault === undefined || this.template.isDefault === null) {
        return false;
      }
      return this.template.isDefault === 1 || this.template.isDefault === true;
    }
  },
  methods: {
    handleDelete() {
      this.$emit('delete', this.template.id)
    },
    handleEdit() {
      this.$emit('edit', this.template)
    },
    handleSetDefault() {
      if (!this.isDefault) {
        this.$emit('set-default', this.template.id)
      }
    }
  }
}
</script>
<style scoped>
.device-item {
  width: 342px;
  border-radius: 20px;
  background: #fafcfe;
  padding: 22px;
  box-sizing: border-box;
}

.device-name {
  margin: 7px 0 10px;
  font-weight: 400;
  font-size: 11px;
  color: #3d4566;
  text-align: left;
}

.settings-btn {
  font-weight: 500;
  font-size: 12px;
  color: #5778ff;
  background: #e6ebff;
  width: auto;
  padding: 0 12px;
  height: 21px;
  line-height: 21px;
  cursor: pointer;
  border-radius: 14px;
}

.version-info {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  font-size: 12px;
  color: #979db1;
  font-weight: 400;
}

.disabled-btn {
  background: #e6e6e6;
  color: #999;
  cursor: not-allowed;
}
</style>

<style>
.custom-tooltip {
  max-width: 400px;
  word-break: break-word;
}
</style>
