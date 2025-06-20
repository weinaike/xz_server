<template>
  <div class="welcome">
    <!-- 公共头部 -->
    <HeaderBar :devices="devices" @search="handleSearch" @search-reset="handleSearchReset" />
    <el-main style="padding: 20px;display: flex;flex-direction: column;">
      <div>
        <!-- 首页内容 -->
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
                添加智能体
              </div>
              <div style="width: 23px;height: 13px;background: #5778ff;margin-left: -10px;" />
              <div class="right-add">
                <i class="el-icon-right" @click="showAddDialog" style="font-size: 20px;color: #fff;" />
              </div>
            </div>
          </div>
        </div>
        
        <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="agent-tabs">
          
          <el-tab-pane label="我的智能体" name="my">
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
                <DeviceItem v-for="(item, index) in devices" :key="index" :device="item" @configure="goToRoleConfig"
                  @deviceManage="handleDeviceManage" @delete="handleDeleteAgent" @chat-history="handleShowChatHistory" />
              </template>
            </div>
          </el-tab-pane>
          <!-- 所有智能体 -->
          <el-tab-pane v-if="isSuperAdmin" label="所有智能体" name="all">
            <div class="device-list-container" style="display: block; padding: 0;">
              <template v-if="isLoadingAll">
                <div v-for="i in skeletonCount" :key="'skeleton-all-' + i" class="skeleton-item">
                  <div class="skeleton-image"></div>
                  <div class="skeleton-content">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line-short"></div>
                  </div>
                </div>
              </template>
              <template v-else>
                <!-- el-table展示所有智能体 -->
                <el-table :data="allDevices" style="width: 100%" border>
                  <el-table-column prop="userId" label="用户ID" min-width="120" />
                  <el-table-column prop="agentName" label="智能体名" min-width="150" />
                  <el-table-column prop="agentTemplateId" label="智能体模板ID" min-width="180" />
                  <el-table-column prop="templateVersion" label="智能体模板版本" min-width="120" />
                  <el-table-column label="操作" min-width="140">
                    <template slot-scope="scope">
                      <el-button
                        size="mini"
                        type="primary"
                        :disabled="!isTemplateUpdateAvailable(scope.row)"
                        @click="handleUpdateTemplate(scope.row)"
                      >
                        更新模板
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <!-- 底部分页 -->
                <div class="pagination-container" v-if="totalCount > 0">
                  <el-pagination
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                    :current-page="currentPage"
                    :page-sizes="[10, 20, 50, 100]"
                    :page-size="pageSize"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="totalCount">
                  </el-pagination>
                </div>
              </template>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <AddWisdomBodyDialog :visible.sync="addDeviceDialogVisible" @confirm="handleWisdomBodyAdded" />
    </el-main>
    <el-footer>
      <version-footer />
    </el-footer>
    <chat-history-dialog :visible.sync="showChatHistory" :agent-id="currentAgentId" :agent-name="currentAgentName" />
  </div>

</template>

<script>
import Api from '@/apis/api';
import AddWisdomBodyDialog from '@/components/AddWisdomBodyDialog.vue';
import ChatHistoryDialog from '@/components/ChatHistoryDialog.vue';
import DeviceItem from '@/components/DeviceItem.vue';
import HeaderBar from '@/components/HeaderBar.vue';
import VersionFooter from '@/components/VersionFooter.vue';
import { mapGetters } from 'vuex';

export default {
  name: 'HomePage',
  components: { DeviceItem, AddWisdomBodyDialog, HeaderBar, VersionFooter, ChatHistoryDialog },
  data() {
    return {
      addDeviceDialogVisible: false,
      devices: [],
      originalDevices: [],
      isSearching: false,
      searchRegex: null,
      isLoading: true,
      skeletonCount: localStorage.getItem('skeletonCount') || 8,
      showChatHistory: false,
      currentAgentId: '',
      currentAgentName: '',
      // 管理员相关数据
      activeTab: 'my',
      allDevices: [],
      isLoadingAll: true,
      // 分页相关
      currentPage: 1,
      pageSize: 20,
      totalCount: 0,
      agentTemplates: [] // 所有模板信息
    }
  },

  computed: {
    ...mapGetters(['getIsSuperAdmin']),
    isSuperAdmin() {
      return this.getIsSuperAdmin;
    }
  },

  mounted() {
    this.fetchAgentList();
    if (this.isSuperAdmin) {
      this.fetchAllAgentList();
      this.fetchAgentTemplates();
    }
  },

  methods: {
    showAddDialog() {
      this.addDeviceDialogVisible = true
    },
    goToRoleConfig() {
      // 点击配置角色后跳转到角色配置页
      this.$router.push('/role-config')
    },
    handleWisdomBodyAdded(res) {
      this.fetchAgentList();
      this.addDeviceDialogVisible = false;
    },
    handleDeviceManage() {
      this.$router.push('/device-management');
    },
    handleSearch(regex) {
      this.isSearching = true;
      this.searchRegex = regex;
      this.applySearchFilter();
    },
    handleSearchReset() {
      this.isSearching = false;
      this.searchRegex = null;
      this.devices = [...this.originalDevices];
    },
    applySearchFilter() {
      if (!this.isSearching || !this.searchRegex) {
        this.devices = [...this.originalDevices];
        return;
      }

      this.devices = this.originalDevices.filter(device => {
        return this.searchRegex.test(device.agentName);
      });
    },
    // 搜索更新智能体列表
    handleSearchResult(filteredList) {
      this.devices = filteredList; // 更新设备列表
    },
    // 获取智能体列表
    fetchAgentList() {
      this.isLoading = true;
      Api.agent.getAgentList(({ data }) => {
        if (data?.data) {
          this.originalDevices = data.data.map(item => ({
            ...item,
            agentId: item.id
          }));

          // 动态设置骨架屏数量（可选）
          this.skeletonCount = Math.min(
            Math.max(this.originalDevices.length, 3), // 最少3个
            10 // 最多10个
          );

          this.handleSearchReset();
        }
        this.isLoading = false;
      }, (error) => {
        console.error('Failed to fetch agent list:', error);
        this.isLoading = false;
      });
    },
    // 获取所有智能体列表（管理员）
    fetchAllAgentList() {
      this.isLoadingAll = true;
      const params = {
        page: this.currentPage,
        limit: this.pageSize
      };
      
      Api.agent.getAdminAgentList(params, ({ data }) => {
        if (data?.data) {
          this.allDevices = data.data.list || [];
          this.totalCount = data.data.total || 0;
        }
        this.isLoadingAll = false;
      }, (error) => {
        console.error('Failed to fetch all agent list:', error);
        this.isLoadingAll = false;
      });
    },
    // 获取模板列表
    fetchAgentTemplates() {
      Api.agent.getAgentTemplate(({ data }) => {
        if (data?.data) {
          this.agentTemplates = data.data;
        }
      });
    },
    isTemplateUpdateAvailable(row) {
      const tpl = this.agentTemplates.find(t => t.id === row.agentTemplateId);
      return tpl && tpl.version > row.templateVersion;
    },
    handleUpdateTemplate(row) {
      const tpl = this.agentTemplates.find(t => t.id === row.agentTemplateId);
      if (!tpl) {
        this.$message.error('未找到对应模板');
        return;
      }

      // 构造更新数据，只用模板最新字段覆盖智能体
      const updateData = {
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
      Api.agent.updateAgentConfig(row.id, updateData, (res) => {
        if (res.data.code === 0) {
          this.$message.success('模板已更新');
          this.fetchAllAgentList();
        } else {
          this.$message.error(res.data.msg || '更新失败');
        }
      });
    },
    // 标签页切换
    handleTabClick(tab) {
      this.activeTab = tab.name;
      if (tab.name === 'all' && this.allDevices.length === 0) {
        this.fetchAllAgentList();
      }
    },
    // 分页大小改变
    handleSizeChange(size) {
      this.pageSize = size;
      this.currentPage = 1;
      this.fetchAllAgentList();
    },
    // 当前页改变
    handleCurrentChange(page) {
      this.currentPage = page;
      this.fetchAllAgentList();
    },
    // 删除智能体
    handleDeleteAgent(agentId) {
      this.$confirm('确定要删除该智能体吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        Api.agent.deleteAgent(agentId, (res) => {
          if (res.data.code === 0) {
            this.$message.success({
              message: '删除成功',
              showClose: true
            });
            this.fetchAgentList(); // 刷新列表
          } else {
            this.$message.error({
              message: res.data.msg || '删除失败',
              showClose: true
            });
          }
        });
      }).catch(() => { });
    },
    handleShowChatHistory({ agentId, agentName }) {
      this.currentAgentId = agentId;
      this.currentAgentName = agentName;
      this.showChatHistory = true;
    }
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

/* 管理员标签页样式 */
.admin-tabs {
  margin-top: 30px;
}

.agent-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.agent-tabs::v-deep .el-tabs__header {
  margin-bottom: 20px;
}

.agent-tabs::v-deep .el-tabs__nav-wrap::after {
  background-color: #f0f2f5;
}

.agent-tabs::v-deep .el-tabs__item {
  font-size: 16px;
  font-weight: 500;
  color: #818cae;
}

.agent-tabs::v-deep .el-tabs__item.is-active {
  color: #5778ff;
}

.agent-tabs::v-deep .el-tabs__active-bar {
  background-color: #5778ff;
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.pagination-top {
  margin-bottom: 30px;
}

.pagination-container::v-deep .el-pagination {
  color: #818cae;
}

.pagination-container::v-deep .el-pagination .el-pager li {
  background-color: #fff;
  border: 1px solid #e4e6ef;
  color: #818cae;
}

.pagination-container::v-deep .el-pagination .el-pager li.active {
  background-color: #5778ff;
  color: #fff;
  border-color: #5778ff;
}

.pagination-container::v-deep .el-pagination .btn-prev,
.pagination-container::v-deep .el-pagination .btn-next {
  background-color: #fff;
  border: 1px solid #e4e6ef;
  color: #818cae;
}

.pagination-container::v-deep .el-pagination .btn-prev:hover,
.pagination-container::v-deep .el-pagination .btn-next:hover {
  color: #5778ff;
}

/* 在所有智能体标签页中，使用不同的布局 */
.admin-tabs .el-tab-pane[id="pane-all"] .device-list-container {
  display: block;
  grid-template-columns: none;
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