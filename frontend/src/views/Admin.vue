<template>
  <div class="admin-page">
    <div class="page-header">
      <h2>系统管理</h2>
      <el-button :icon="Refresh" @click="initData">刷新数据</el-button>
    </div>

    <!-- 数据看板 -->
    <el-row :gutter="16" class="dashboard-row">
      <el-col :xs="12" :sm="6" v-for="card in statCards" :key="card.key">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-inner">
            <el-icon :size="36" :color="card.color"><component :is="card.icon" /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户管理 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div class="header-filters">
            <el-select v-model="userRole" placeholder="全部角色" clearable style="width: 130px" @change="handleUserSearch">
              <el-option label="学生" value="student" />
              <el-option label="教师" value="teacher" />
              <el-option label="审核员" value="auditor" />
              <el-option label="管理员" value="admin" />
            </el-select>
            <el-input
              v-model="userKeyword"
              placeholder="搜索用户名/昵称"
              :prefix-icon="Search"
              clearable
              style="width: 220px"
              @keyup.enter="handleUserSearch"
              @clear="handleUserSearch"
            />
          </div>
        </div>
      </template>

      <el-table v-loading="userLoading" :data="userList" stripe>
        <el-table-column label="ID" prop="id" width="70" />
        <el-table-column label="用户名" prop="username" width="130" />
        <el-table-column label="昵称" prop="nickname" min-width="120" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="认证状态" width="110">
          <template #default="{ row }">
            <el-tag :type="certTagType(row.cert_status)" size="small" effect="light">
              {{ certLabel(row.cert_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'disabled' ? 'danger' : 'success'" size="small">
              {{ row.status === 'disabled' ? '已禁用' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              :type="row.status === 'disabled' ? 'success' : 'warning'"
              size="small"
              text
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 'disabled' ? '启用' : '禁用' }}
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无用户" />
        </template>
      </el-table>

      <div v-if="userTotal > 0" class="pagination-wrap">
        <el-pagination
          v-model:current-page="userPage"
          v-model:page-size="userPageSize"
          :total="userTotal"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="fetchUsers"
          @size-change="handleUserSizeChange"
        />
      </div>
    </el-card>

    <el-row :gutter="16">
      <!-- 教师认证审核 -->
      <el-col :xs="24" :lg="14">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="card-header">
              <span>教师认证审核</span>
              <el-button size="small" :icon="Refresh" @click="fetchCertRequests">刷新</el-button>
            </div>
          </template>

          <el-table v-loading="certLoading" :data="certList" stripe>
            <el-table-column label="用户名" prop="username" width="120" />
            <el-table-column label="真实姓名" prop="real_name" min-width="100" />
            <el-table-column label="教职工号" prop="employee_id" min-width="110" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="certTagType(row.cert_status)" size="small" effect="light">
                  {{ certLabel(row.cert_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <template v-if="row.cert_status === 'pending'">
                  <el-button type="success" size="small" text @click="handleReviewCert(row, 'approve')">通过</el-button>
                  <el-button type="danger" size="small" text @click="handleReviewCert(row, 'reject')">驳回</el-button>
                </template>
                <span v-else class="text-muted">已处理</span>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无认证申请" />
            </template>
          </el-table>
        </el-card>
      </el-col>

      <!-- 创建审核员 -->
      <el-col :xs="24" :lg="10">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="card-header">
              <span>创建审核员</span>
              <el-button size="small" type="primary" :icon="Plus" @click="openAuditorDialog">新建</el-button>
            </div>
          </template>
          <div class="auditor-tip">
            <el-alert
              title="审核员可访问审核中心，对资源、成果、任务包进行审核。"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
          <el-button type="primary" plain style="width: 100%" :icon="Plus" @click="openAuditorDialog">
            创建审核员账号
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 资源统计 -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="section-card">
          <template #header>
            <span>资源统计</span>
          </template>
          <div v-loading="resourceStatsLoading" class="stats-box">
            <el-empty v-if="!resourceStatsLoading && !resourceStats" description="暂无数据" :image-size="60" />
            <template v-else-if="resourceStats">
              <div class="stats-highlight">
                <div class="stats-highlight-value">{{ resourceStats.total || 0 }}</div>
                <div class="stats-highlight-label">资源总数</div>
              </div>
              <div v-if="resourceStats.by_category && Object.keys(resourceStats.by_category).length" class="stats-category-list">
                <div class="stats-sub-title">按分类分布</div>
                <div
                  v-for="(count, category) in resourceStats.by_category"
                  :key="category"
                  class="stats-category-row"
                >
                  <span class="stats-category-name">{{ category || '未分类' }}</span>
                  <div class="stats-category-bar-wrap">
                    <div
                      class="stats-category-bar"
                      :style="{ width: ((count / resourceStats.total) * 100) + '%' }"
                    ></div>
                  </div>
                  <span class="stats-category-count">{{ count }}</span>
                </div>
              </div>
            </template>
          </div>
        </el-card>
      </el-col>

      <!-- 任务统计 -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="section-card">
          <template #header>
            <span>任务统计</span>
          </template>
          <div v-loading="taskStatsLoading" class="stats-box">
            <el-empty v-if="!taskStatsLoading && !taskStats" description="暂无数据" :image-size="60" />
            <template v-else-if="taskStats">
              <div class="stats-highlight">
                <div class="stats-highlight-value">{{ taskStats.total || 0 }}</div>
                <div class="stats-highlight-label">任务包总数</div>
              </div>
              <div v-if="taskStats.by_category && Object.keys(taskStats.by_category).length" class="stats-category-list">
                <div class="stats-sub-title">按分类分布</div>
                <div
                  v-for="(count, category) in taskStats.by_category"
                  :key="category"
                  class="stats-category-row"
                >
                  <span class="stats-category-name">{{ category || '未分类' }}</span>
                  <div class="stats-category-bar-wrap">
                    <div
                      class="stats-category-bar stats-bar-orange"
                      :style="{ width: ((count / taskStats.total) * 100) + '%' }"
                    ></div>
                  </div>
                  <span class="stats-category-count">{{ count }}</span>
                </div>
              </div>
              <div v-if="taskStats.source" class="stats-source-list">
                <div class="stats-sub-title">来源分布</div>
                <div class="stats-source-row">
                  <span class="stats-source-name">AI 生成</span>
                  <span class="stats-source-count">{{ taskStats.source.ai_generated || 0 }}</span>
                  <span class="stats-source-ratio">{{ ((taskStats.source.ai_generated_ratio || 0) * 100).toFixed(1) }}%</span>
                </div>
                <div class="stats-source-row">
                  <span class="stats-source-name">用户发布</span>
                  <span class="stats-source-count">{{ taskStats.source.user_published || 0 }}</span>
                  <span class="stats-source-ratio">{{ ((taskStats.source.user_published_ratio || 0) * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 问题反馈管理 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <span>
            问题反馈管理
            <el-tag v-if="feedbackStats.pending > 0" type="danger" size="small" class="fb-pending-badge">{{ feedbackStats.pending }} 待处理</el-tag>
          </span>
          <div class="header-filters">
            <el-select v-model="fbFilterStatus" placeholder="全部状态" clearable style="width: 120px" @change="handleFbSearch">
              <el-option label="待处理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已解决" value="resolved" />
              <el-option label="已关闭" value="closed" />
            </el-select>
            <el-select v-model="fbFilterCategory" placeholder="全部分类" clearable style="width: 120px" @change="handleFbSearch">
              <el-option label="系统Bug" value="bug" />
              <el-option label="功能建议" value="suggestion" />
              <el-option label="账号问题" value="account" />
              <el-option label="其他问题" value="other" />
            </el-select>
            <el-button size="small" :icon="Refresh" @click="fetchFeedbacks">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="fbLoading" :data="fbList" stripe>
        <el-table-column label="ID" prop="id" width="70" />
        <el-table-column label="提交用户" min-width="120">
          <template #default="{ row }">
            <span>{{ row.user_nickname }}</span>
            <el-tag :type="roleTagType(row.user_role)" size="small" effect="plain" style="margin-left: 4px">{{ roleLabel(row.user_role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="fbCategoryTagType(row.category)" size="small">{{ row.category_label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标题" prop="title" min-width="150" show-overflow-tooltip />
        <el-table-column label="内容" prop="content" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="fbStatusTagType(row.status)" size="small" effect="light">{{ row.status_label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提交时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="openFbReplyDialog(row)">回复</el-button>
            <el-dropdown trigger="click" @command="(cmd) => handleFbStatusChange(row, cmd)">
              <el-button type="warning" size="small" text>状态</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="pending">待处理</el-dropdown-item>
                  <el-dropdown-item command="processing">处理中</el-dropdown-item>
                  <el-dropdown-item command="resolved">已解决</el-dropdown-item>
                  <el-dropdown-item command="closed">已关闭</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无反馈" />
        </template>
      </el-table>

      <div v-if="fbTotal > 0" class="pagination-wrap">
        <el-pagination
          v-model:current-page="fbPage"
          v-model:page-size="fbPageSize"
          :total="fbTotal"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="fetchFeedbacks"
          @size-change="handleFbSizeChange"
        />
      </div>
    </el-card>

    <!-- 创建审核员对话框 -->
    <el-dialog v-model="auditorDialogVisible" title="创建审核员" width="440px" :close-on-click-modal="false">
      <el-form ref="auditorFormRef" :model="auditorForm" :rules="auditorRules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="auditorForm.username" placeholder="登录账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="auditorForm.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="auditorForm.nickname" placeholder="显示昵称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="auditorDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="auditorSubmitting" @click="submitAuditor">创建</el-button>
      </template>
    </el-dialog>

    <!-- 认证驳回理由对话框 -->
    <el-dialog v-model="certRejectDialogVisible" title="驳回认证" width="420px" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="驳回理由" required>
          <el-input v-model="certRejectReason" type="textarea" :rows="4" placeholder="请填写驳回理由" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="certRejectDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="certReviewSubmitting" @click="submitCertReview">确认驳回</el-button>
      </template>
    </el-dialog>

    <!-- 反馈回复对话框 -->
    <el-dialog v-model="fbReplyDialogVisible" title="回复反馈" width="520px" :close-on-click-modal="false">
      <div v-if="currentFb" class="fb-reply-dialog-body">
        <div class="fb-reply-dialog-info">
          <el-tag :type="fbCategoryTagType(currentFb.category)" size="small">{{ currentFb.category_label }}</el-tag>
          <el-tag :type="fbStatusTagType(currentFb.status)" size="small" effect="light">{{ currentFb.status_label }}</el-tag>
          <span class="fb-reply-dialog-user">提交人：{{ currentFb.user_nickname }}（{{ roleLabel(currentFb.user_role) }}）</span>
          <span class="fb-reply-dialog-time">{{ formatTime(currentFb.created_at) }}</span>
        </div>
        <div class="fb-reply-dialog-title">{{ currentFb.title }}</div>
        <div class="fb-reply-dialog-content">{{ currentFb.content }}</div>
        <div v-if="currentFb.contact" class="fb-reply-dialog-contact">联系方式：{{ currentFb.contact }}</div>
        <el-divider />
        <el-form label-position="top">
          <el-form-item label="回复内容" required>
            <el-input v-model="fbReplyText" type="textarea" :rows="4" placeholder="请输入回复内容" maxlength="500" show-word-limit />
          </el-form-item>
          <el-form-item label="处理状态">
            <el-radio-group v-model="fbReplyStatus">
              <el-radio value="processing">处理中</el-radio>
              <el-radio value="resolved">已解决</el-radio>
              <el-radio value="closed">已关闭</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="fbReplyDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="fbReplySubmitting" @click="submitFbReply">提交回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, Plus, User, Goods, Files, Reading } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { adminApi, feedbackApi } from '@/api'

const authStore = useAuthStore()

// ============ 数据看板 ============
const dashboard = ref({})
const dashboardLoading = ref(false)

const statCards = computed(() => [
  { key: 'users', label: '用户总数', value: dashboard.value.user_count ?? 0, icon: User, color: '#409eff' },
  { key: 'resources', label: '资源总数', value: dashboard.value.resource_count ?? 0, icon: Goods, color: '#67c23a' },
  { key: 'tasks', label: '任务包数', value: dashboard.value.task_count ?? 0, icon: Files, color: '#e6a23c' },
  { key: 'checkins', label: '打卡总数', value: dashboard.value.checkin_count ?? 0, icon: Reading, color: '#f56c6c' },
])

async function fetchDashboard() {
  dashboardLoading.value = true
  try {
    const res = await adminApi.dashboard()
    const d = res.data || res || {}
    // 后端返回 total_users / total_resources / total_tasks / total_achievements / pending_total
    // 前端使用 user_count / resource_count / task_count / checkin_count
    dashboard.value = {
      user_count: d.total_users ?? d.user_count ?? 0,
      resource_count: d.total_resources ?? d.resource_count ?? 0,
      task_count: d.total_tasks ?? d.task_count ?? 0,
      checkin_count: d.checkin_count ?? 0,
      post_count: d.total_achievements ?? d.post_count ?? 0,
      pending_count: d.pending_total ?? d.pending_count ?? 0,
    }
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    dashboardLoading.value = false
  }
}

// ============ 用户管理 ============
const userLoading = ref(false)
const userList = ref([])
const userTotal = ref(0)
const userPage = ref(1)
const userPageSize = ref(10)
const userRole = ref('')
const userKeyword = ref('')

async function fetchUsers() {
  userLoading.value = true
  try {
    const params = { page: userPage.value, page_size: userPageSize.value }
    if (userRole.value) params.role = userRole.value
    if (userKeyword.value) params.keyword = userKeyword.value
    const res = await adminApi.users(params)
    userList.value = res.data || []
    userTotal.value = res.total || 0
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    userLoading.value = false
  }
}

function handleUserSearch() {
  userPage.value = 1
  fetchUsers()
}

function handleUserSizeChange() {
  userPage.value = 1
  fetchUsers()
}

async function handleToggleStatus(row) {
  const nextStatus = row.status === 'disabled' ? 'active' : 'disabled'
  const action = nextStatus === 'disabled' ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定${action}用户「${row.username}」吗？`, '提示', { type: 'warning' })
    await adminApi.updateStatus(row.id, { status: nextStatus })
    ElMessage.success(`${action}成功`)
    fetchUsers()
  } catch (e) {
    // 取消或错误
  }
}

// ============ 教师认证审核 ============
const certLoading = ref(false)
const certList = ref([])

async function fetchCertRequests() {
  certLoading.value = true
  try {
    const res = await adminApi.certRequests()
    certList.value = res.data || []
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    certLoading.value = false
  }
}

let currentCertRow = null
const certRejectDialogVisible = ref(false)
const certRejectReason = ref('')
const certReviewSubmitting = ref(false)

async function handleReviewCert(row, action) {
  currentCertRow = row
  if (action === 'approve') {
    try {
      await ElMessageBox.confirm(`确定通过「${row.username}」的教师认证吗？`, '提示', { type: 'success' })
      await adminApi.reviewCert(row.id, { action: 'approve' })
      ElMessage.success('已通过认证')
      fetchCertRequests()
    } catch (e) {
      // 取消或错误
    }
  } else {
    certRejectReason.value = ''
    certRejectDialogVisible.value = true
  }
}

async function submitCertReview() {
  if (!certRejectReason.value.trim()) {
    ElMessage.warning('请填写驳回理由')
    return
  }
  certReviewSubmitting.value = true
  try {
    await adminApi.reviewCert(currentCertRow.id, { action: 'reject', reason: certRejectReason.value })
    ElMessage.success('已驳回认证')
    certRejectDialogVisible.value = false
    fetchCertRequests()
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    certReviewSubmitting.value = false
  }
}

// ============ 创建审核员 ============
const auditorDialogVisible = ref(false)
const auditorSubmitting = ref(false)
const auditorFormRef = ref()
const auditorForm = reactive({ username: '', password: '', nickname: '' })
const auditorRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '3-50个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '至少6位', trigger: 'blur' },
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
}

function openAuditorDialog() {
  auditorForm.username = ''
  auditorForm.password = ''
  auditorForm.nickname = ''
  auditorDialogVisible.value = true
}

async function submitAuditor() {
  await auditorFormRef.value.validate(async (valid) => {
    if (!valid) return
    auditorSubmitting.value = true
    try {
      await adminApi.createAuditor({ ...auditorForm })
      ElMessage.success('审核员创建成功')
      auditorDialogVisible.value = false
      fetchUsers()
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      auditorSubmitting.value = false
    }
  })
}

// ============ 资源 / 任务统计 ============
const resourceStatsLoading = ref(false)
const resourceStats = ref(null)
const taskStatsLoading = ref(false)
const taskStats = ref(null)

async function fetchResourceStats() {
  resourceStatsLoading.value = true
  try {
    const res = await adminApi.resourceStats()
    resourceStats.value = res.data || null
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    resourceStatsLoading.value = false
  }
}

async function fetchTaskStats() {
  taskStatsLoading.value = true
  try {
    const res = await adminApi.taskStats()
    taskStats.value = res.data || null
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    taskStatsLoading.value = false
  }
}

// ============ 问题反馈管理 ============
const fbLoading = ref(false)
const fbList = ref([])
const fbTotal = ref(0)
const fbPage = ref(1)
const fbPageSize = ref(10)
const fbFilterStatus = ref('')
const fbFilterCategory = ref('')
const feedbackStats = ref({ total: 0, pending: 0, processing: 0, resolved: 0, closed: 0 })

const fbReplyDialogVisible = ref(false)
const currentFb = ref(null)
const fbReplyText = ref('')
const fbReplyStatus = ref('resolved')
const fbReplySubmitting = ref(false)

async function fetchFeedbacks() {
  fbLoading.value = true
  try {
    const params = { page: fbPage.value, page_size: fbPageSize.value }
    if (fbFilterStatus.value) params.status = fbFilterStatus.value
    if (fbFilterCategory.value) params.category = fbFilterCategory.value
    const res = await feedbackApi.list(params)
    fbList.value = res.data || []
    fbTotal.value = res.total || 0
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    fbLoading.value = false
  }
}

async function fetchFeedbackStats() {
  try {
    const res = await feedbackApi.stats()
    feedbackStats.value = res.data || { total: 0, pending: 0, processing: 0, resolved: 0, closed: 0 }
  } catch (e) {
    // 静默处理
  }
}

function handleFbSearch() {
  fbPage.value = 1
  fetchFeedbacks()
}

function handleFbSizeChange() {
  fbPage.value = 1
  fetchFeedbacks()
}

function openFbReplyDialog(row) {
  currentFb.value = row
  fbReplyText.value = row.reply || ''
  fbReplyStatus.value = row.status === 'pending' ? 'processing' : (row.status === 'resolved' ? 'resolved' : 'resolved')
  fbReplyDialogVisible.value = true
}

async function submitFbReply() {
  if (!fbReplyText.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  fbReplySubmitting.value = true
  try {
    await feedbackApi.reply(currentFb.value.id, {
      reply: fbReplyText.value,
      status: fbReplyStatus.value,
    })
    ElMessage.success('回复成功')
    fbReplyDialogVisible.value = false
    fetchFeedbacks()
    fetchFeedbackStats()
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    fbReplySubmitting.value = false
  }
}

async function handleFbStatusChange(row, newStatus) {
  try {
    await feedbackApi.updateStatus(row.id, newStatus)
    ElMessage.success('状态已更新')
    fetchFeedbacks()
    fetchFeedbackStats()
  } catch (e) {
    // 错误已由拦截器处理
  }
}

function fbCategoryTagType(category) {
  const map = { bug: 'danger', suggestion: 'warning', account: 'primary', other: 'info' }
  return map[category] || 'info'
}

function fbStatusTagType(status) {
  const map = { pending: 'warning', processing: 'primary', resolved: 'success', closed: 'info' }
  return map[status] || 'info'
}

// ============ 工具函数 ============
function roleLabel(role) {
  const map = { student: '学生', teacher: '教师', auditor: '审核员', admin: '管理员' }
  return map[role] || role || '未知'
}

function roleTagType(role) {
  const map = { student: 'success', teacher: 'warning', auditor: 'danger', admin: '' }
  return map[role] || 'info'
}

function certLabel(status) {
  const map = { pending: '待审核', approved: '已认证', rejected: '未通过', none: '未认证' }
  return map[status] || status || '未认证'
}

function certTagType(status) {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger', none: 'info' }
  return map[status] || 'info'
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function pad(n) {
  return String(n).padStart(2, '0')
}

function initData() {
  fetchDashboard()
  fetchUsers()
  fetchCertRequests()
  fetchResourceStats()
  fetchTaskStats()
  fetchFeedbacks()
  fetchFeedbackStats()
}

onMounted(() => {
  initData()
})
</script>

<style scoped>
.admin-page {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.dashboard-row {
  margin-bottom: 16px;
}

.stat-card {
  margin-bottom: 16px;
}

.stat-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.section-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.header-filters {
  display: flex;
  gap: 8px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.text-muted {
  color: #c0c4cc;
  font-size: 13px;
}

.auditor-tip {
  margin-bottom: 16px;
}

.stats-box {
  min-height: 120px;
}

.stats-highlight {
  text-align: center;
  padding: 20px 0;
  margin-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.stats-highlight-value {
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
  line-height: 1.2;
}

.stats-highlight-label {
  font-size: 14px;
  color: #909399;
  margin-top: 6px;
}

.stats-sub-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
}

.stats-category-list {
  margin-bottom: 16px;
}

.stats-category-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
}

.stats-category-name {
  font-size: 13px;
  color: #303133;
  width: 70px;
  flex-shrink: 0;
}

.stats-category-bar-wrap {
  flex: 1;
  height: 18px;
  background: #f0f2f5;
  border-radius: 9px;
  overflow: hidden;
}

.stats-category-bar {
  height: 100%;
  background: #67c23a;
  border-radius: 9px;
  transition: width 0.3s;
  min-width: 4px;
}

.stats-bar-orange {
  background: #e6a23c;
}

.stats-category-count {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  width: 32px;
  text-align: right;
  flex-shrink: 0;
}

.stats-source-list {
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}

.stats-source-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
}

.stats-source-name {
  font-size: 13px;
  color: #303133;
  flex: 1;
}

.stats-source-count {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.stats-source-ratio {
  font-size: 12px;
  color: #909399;
  width: 48px;
  text-align: right;
}

/* ---------- 反馈管理 ---------- */
.fb-pending-badge {
  margin-left: 8px;
}

.fb-reply-dialog-body {
  padding: 0 4px;
}

.fb-reply-dialog-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.fb-reply-dialog-user {
  font-size: 13px;
  color: #606266;
}

.fb-reply-dialog-time {
  font-size: 12px;
  color: #c0c4cc;
  margin-left: auto;
}

.fb-reply-dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.fb-reply-dialog-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
}

.fb-reply-dialog-contact {
  margin-top: 8px;
  font-size: 13px;
  color: #e6a23c;
}
</style>
