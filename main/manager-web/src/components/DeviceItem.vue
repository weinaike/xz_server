<template>
  <div class="device-item">
    <div style="display: flex;justify-content: space-between;">
      <div style="font-weight: 700;font-size: 18px;text-align: left;color: #3d4566;">
        {{ device.agentName }}
      </div>
      <div>
        <img src="@/assets/home/delete.png" alt="" style="width: 18px;height: 18px;margin-right: 10px;"
          @click.stop="handleDelete" />
        <el-tooltip class="item" effect="dark" :content="device.systemPrompt" placement="top"
          popper-class="custom-tooltip">
          <img src="@/assets/home/info.png" alt="" style="width: 18px;height: 18px;" />
        </el-tooltip>
      </div>
    </div>
    <div class="device-name">
      设备型号：{{ device.ttsModelName }}
    </div>
    <div class="device-name">
      音色模型：{{ device.ttsVoiceName }}
    </div>
    <div style="display: flex;gap: 10px;align-items: center;">
      <div class="settings-btn" @click="handleConfigure">
        配置角色
      </div>

      <div v-if="showUpdateBtn"  class="settings-btn" @click="handleUpdateFromTemplate">
        更新模板
      </div>
      <div class="settings-btn" @click="handleDeviceManage">
        设备管理({{ device.deviceCount }})
      </div>
      <div class="settings-btn" @click="handleChatHistory"
        :class="{ 'disabled-btn': device.memModelId === 'Memory_nomem' }">
        <el-tooltip v-if="device.memModelId === 'Memory_nomem'" content="请先在“配置角色”界面开启记忆" placement="top">
          <span>聊天记录</span>
        </el-tooltip>
        <span v-else>聊天记录</span>
      </div>
    </div>
    <div class="version-info">
      <div>最近对话：{{ formattedLastConnectedTime }}</div>
    </div>
  </div>
</template>

<script>
import Api from '@/apis/module/agent';
export default {
  name: 'DeviceItem',
  props: {
    device: { type: Object, required: true }
  },
  data() {
    return { switchValue: false, templateVersionRemote: null };
  },
  computed: {
    formattedLastConnectedTime() {
      if (!this.device.lastConnectedAt) return '暂未对话';

      const lastTime = new Date(this.device.lastConnectedAt);
      const now = new Date();
      const diffMinutes = Math.floor((now - lastTime) / (1000 * 60));

      if (diffMinutes <= 1) {
        return '刚刚';
      } else if (diffMinutes < 60) {
        return `${diffMinutes}分钟前`;
      } else if (diffMinutes < 24 * 60) {
        const hours = Math.floor(diffMinutes / 60);
        const minutes = diffMinutes % 60;
        return `${hours}小时${minutes > 0 ? minutes + '分钟' : ''}前`;
      } else {
        return this.device.lastConnectedAt;
      }
    },
    showUpdateBtn() {
      // 只有当模板ID和本地版本号都存在且远端版本号更高时显示
      return (
        this.device.agentTemplateId &&
        this.device.templateVersion !== undefined &&
        this.templateVersionRemote !== null &&
        this.templateVersionRemote > this.device.templateVersion
      );
    }
  },
  watch: {
    'device.agentTemplateId': {
      immediate: true,
      handler(val) {
        if (val) {
          Api.getAgentTemplateById(val, (res) => {
            if (res.data && res.data.data) {
              this.templateVersionRemote = res.data.data.version;
            } else {
              this.templateVersionRemote = null;
            }
          });
        } else {
          this.templateVersionRemote = null;
        }
      }
    }
  },
  methods: {
    handleDelete() {
      this.$emit('delete', this.device.agentId)
    },
    handleConfigure() {
      this.$router.push({ path: '/role-config', query: { agentId: this.device.agentId } });
    },
    handleDeviceManage() {
      this.$router.push({ path: '/device-management', query: { agentId: this.device.agentId } });
    },
    handleChatHistory() {
      if (this.device.memModelId === 'Memory_nomem') {
        return
      }
      this.$emit('chat-history', { agentId: this.device.agentId, agentName: this.device.agentName })
    },
    handleUpdateFromTemplate() {
      this.$confirm('智能体更新至最新模板内容？此操作会覆盖当前配置。', '更新模板确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 拉取模板内容并更新智能体
        Api.getAgentTemplateById(this.device.agentTemplateId, (res) => {
          if (res.data && res.data.data) {
            const tpl = res.data.data;
            const updateData = {
              agentName: tpl.agentName,
              asrModelId: tpl.asrModelId,
              vadModelId: tpl.vadModelId,
              llmModelId: tpl.llmModelId,
              ttsModelId: tpl.ttsModelId,
              ttsVoiceId: tpl.ttsVoiceId,
              memModelId: tpl.memModelId,
              intentModelId: tpl.intentModelId,
              chatHistoryConf: tpl.chatHistoryConf,
              systemPrompt: tpl.systemPrompt,
              summaryMemory: tpl.summaryMemory,
              langCode: tpl.langCode,
              language: tpl.language,
              agentTemplateId: tpl.id,
              templateVersion: tpl.version
            };
            Api.updateAgentConfig(this.device.agentId, updateData, (updateRes) => {
              if (updateRes.data && updateRes.data.code === 0) {
                this.$message.success('已同步到最新模板');
                this.$emit('updated');
              } else {
                this.$message.error(updateRes.data.msg || '更新失败');
              }
            });
          } else {
            this.$message.error('获取模板信息失败');
          }
        });
      }).catch(() => {});
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