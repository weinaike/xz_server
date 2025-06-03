<template>
  <div class="welcome">
    <!-- 公共头部 -->
    <HeaderBar :templates="templates" @search="handleSearch" @search-reset="handleSearchReset" />
    <el-main style="padding: 20px;display: flex;flex-direction: column;">
      <div>
        <!-- 内容 -->
        <div class="add-device">
          <div class="add-device-bg">
            <div class="hellow-text" style="margin-top: 30px;">
              你好，小智
            </div>
            <div class="hellow-text">
              让我们度过
              <div style="display: inline-block;color: #5778FF;">
                美好的一天！
              </div>
            </div>
            <div class="hi-hint">
              Hello, Let's have a wonderful day!
            </div>
            <div class="add-device-btn">
              <div class="left-add" @click="showAddDialog">
                添加模板
              </div>
              <div style="width: 23px;height: 13px;background: #5778ff;margin-left: -10px;" />
              <div class="right-add">
                <i class="el-icon-right" @click="showAddDialog" style="font-size: 20px;color: #fff;" />
              </div>
            </div>
          </div>
        </div>
        <div class="device-list-container">
          <template v-if="isLoading">
            <div v-for="i in skeletonCount" :key="'skeleton-' + i" class="skeleton-item">
              <div class="skeleton-image"></div>
              <div class="skeleton-content">
                <div class="skeleton-line"></div>
                <div class="skeleton-line-short"></div>
              </div>
            </div>
          </template>

          <template v-else>
            <AgentTemplateItem v-for="(item, index) in templates" :key="index" :template="item" @edit="handleEditTemplate" @delete="handleDeleteTemplate" />
          </template>
        </div>
      </div>
      <AddAgentTemplateDialog :visible.sync="addDeviceDialogVisible" @confirm="handleAddTemplate" />
      <EditAgentTemplateDialog
        :visible.sync="editDialogVisible"
        :templateData="editTemplateData"
        @confirm="handleEditDialogConfirm"
        @cancel="handleEditDialogCancel"
      />
    </el-main>
    <el-footer>
      <version-footer />
    </el-footer>
  </div>
</template>

<script>
import Api from '@/apis/api';
import AddAgentTemplateDialog from '@/components/AddAgentTemplateDialog.vue';
import AgentTemplateItem from '@/components/AgentTemplateItem.vue';
import EditAgentTemplateDialog from '@/components/EditAgentTemplateDialog.vue';
import HeaderBar from '@/components/HeaderBar.vue';
import VersionFooter from '@/components/VersionFooter.vue';

export default {
  name: 'HomePage',
  components: { AgentTemplateItem, AddAgentTemplateDialog, EditAgentTemplateDialog, HeaderBar, VersionFooter },
  data() {
    return {
      addDeviceDialogVisible: false,
      editDialogVisible: false,
      editTemplateData: null,
      templates: [],
      originalTemplates: [],
      isSearching: false,
      searchRegex: null,
      isLoading: true,
      skeletonCount: localStorage.getItem('skeletonCount') || 8
    }
  },

  mounted() {
    this.fetchAgentTemplateList();
  },

  methods: {
    showAddDialog() {
      this.addDeviceDialogVisible = true
    },
    handleEditTemplate(template) {
      this.editTemplateData = { ...template };
      this.editDialogVisible = true;
    },
    handleEditDialogConfirm(updatedData) {
      if (!this.editTemplateData || !this.editTemplateData.id) return;
      Api.agent.updateAgentTemplate(this.editTemplateData.id, updatedData, (res) => {
        if (res.data.code === 0) {
          this.$message.success({ message: '修改成功', showClose: true });
          this.fetchAgentTemplateList();
          this.editDialogVisible = false;
        } else {
          this.$message.error({ message: res.data.msg || '修改失败', showClose: true });
        }
      });
    },
    handleEditDialogCancel() {
      this.editDialogVisible = false;
      this.editTemplateData = null;
    },
    handleAddTemplate(res) {
      this.fetchAgentTemplateList();
      this.addDeviceDialogVisible = false;
    },
    handleSearch(regex) {
      this.isSearching = true;
      this.searchRegex = regex;
      this.applySearchFilter();
    },
    handleSearchReset() {
      this.isSearching = false;
      this.searchRegex = null;
      this.templates = [...this.originalTemplates];
    },
    applySearchFilter() {
      if (!this.isSearching || !this.searchRegex) {
        this.templates = [...this.originalTemplates];
        return;
      }
      this.templates = this.originalTemplates.filter(template => {
        return this.searchRegex.test(template.agentName);
      });
    },
    // 搜索更新模板列表
    handleSearchResult(filteredList) {
      this.templates = filteredList;
    },
    // 获取模板列表
    fetchAgentTemplateList() {
      this.isLoading = true;
      Api.agent.getAgentTemplate(({ data }) => {
        if (data?.data) {
          this.originalTemplates = data.data.map(item => ({
            ...item,
            agentId: item.id // 保持兼容性
          }));
          this.skeletonCount = Math.min(
            Math.max(this.originalTemplates.length, 3),
            10
          );
          this.handleSearchReset();
        }
        this.isLoading = false;
      }, (error) => {
        console.error('Failed to fetch agent template list:', error);
        this.isLoading = false;
      });
    },
    // 删除智能体模板
    handleDeleteTemplate(templateId) {
      this.$confirm('确定要删除该智能体模板吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        Api.agent.deleteAgentTemplate(templateId, (res) => {
          if (res.data.code === 0) {
            this.$message.success({
              message: '删除成功',
              showClose: true
            });
            this.fetchAgentTemplateList();
          } else {
            this.$message.error({
              message: res.data.msg || '删除失败',
              showClose: true
            });
          }
        });
      }).catch(() => { });
    },
  }
}
</script>

<style scoped>
.welcome {
  min-width: 900px;
  min-height: 506px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(145deg, #e6eeff, #eff0ff);
  background-size: cover;
  /* 确保背景图像覆盖整个元素 */
  background-position: center;
  /* 从顶部中心对齐 */
  -webkit-background-size: cover;
  /* 兼容老版本WebKit浏览器 */
  -o-background-size: cover;
  /* 兼容老版本Opera浏览器 */
}

.add-device {
  height: 195px;
  border-radius: 15px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(269.62deg,
      #e0e6fd 0%,
      #cce7ff 49.69%,
      #d3d3fe 100%);
}

.add-device-bg {
  width: 100%;
  height: 100%;
  text-align: left;
  background-image: url("@/assets/home/main-top-bg.png");
  overflow: hidden;
  background-size: cover;
  /* 确保背景图像覆盖整个元素 */
  background-position: center;
  /* 从顶部中心对齐 */
  -webkit-background-size: cover;
  /* 兼容老版本WebKit浏览器 */
  -o-background-size: cover;
  box-sizing: border-box;

  /* 兼容老版本Opera浏览器 */
  .hellow-text {
    margin-left: 75px;
    color: #3d4566;
    font-size: 33px;
    font-weight: 700;
    letter-spacing: 0;
  }

  .hi-hint {
    font-weight: 400;
    font-size: 12px;
    text-align: left;
    color: #818cae;
    margin-left: 75px;
    margin-top: 5px;
  }
}

.add-device-btn {
  display: flex;
  align-items: center;
  margin-left: 75px;
  margin-top: 15px;
  cursor: pointer;

  .left-add {
    width: 105px;
    height: 34px;
    border-radius: 17px;
    background: #5778ff;
    color: #fff;
    font-size: 14px;
    font-weight: 500;
    text-align: center;
    line-height: 34px;
  }

  .right-add {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #5778ff;
    margin-left: -6px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

.device-list-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 30px;
  padding: 30px 0;
}

/* 在 DeviceItem.vue 的样式中 */
.device-item {
  margin: 0 !important;
  /* 避免冲突 */
  width: auto !important;
}

.footer {
  font-size: 12px;
  font-weight: 400;
  margin-top: auto;
  padding-top: 30px;
  color: #979db1;
  text-align: center;
  /* 居中显示 */
}

/* 骨架屏动画 */
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.skeleton-item {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  height: 120px;
  position: relative;
  overflow: hidden;
  margin-bottom: 20px;
}

.skeleton-image {
  width: 80px;
  height: 80px;
  background: #f0f2f5;
  border-radius: 4px;
  float: left;
  position: relative;
  overflow: hidden;
}

.skeleton-content {
  margin-left: 100px;
}

.skeleton-line {
  height: 16px;
  background: #f0f2f5;
  border-radius: 4px;
  margin-bottom: 12px;
  width: 70%;
  position: relative;
  overflow: hidden;
}

.skeleton-line-short {
  height: 12px;
  background: #f0f2f5;
  border-radius: 4px;
  width: 50%;
}

.skeleton-item::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg,
      rgba(255, 255, 255, 0),
      rgba(255, 255, 255, 0.3),
      rgba(255, 255, 255, 0));
  animation: shimmer 1.5s infinite;
}
</style>