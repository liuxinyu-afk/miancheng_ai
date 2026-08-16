<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '210px'" class="sidebar">
      <div class="logo">
        <span v-if="!isCollapse">绵城AI学习集市</span>
        <span v-else>AI</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <el-menu-item :index="route.fullPath" class="menu-item-relative">
            <el-icon><component :is="route.meta.icon" /></el-icon>
            <span>{{ route.meta.title }}</span>
            <el-badge v-if="route.path === 'messages' && totalUnread > 0" :value="totalUnread" :max="99" class="menu-badge" />
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle !== '首页'">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 消息通知 -->
          <el-popover
            v-model:visible="notifyVisible"
            placement="bottom-end"
            :width="380"
            trigger="click"
            popper-class="notify-popover"
          >
            <template #reference>
              <el-badge :value="totalUnread" :hidden="totalUnread === 0" class="message-badge">
                <el-icon :size="20" class="bell-icon"><Bell /></el-icon>
              </el-badge>
            </template>

            <!-- 通知面板 -->
            <div class="notify-panel">
              <div class="notify-header">
                <span class="notify-title">消息通知</span>
                <div class="notify-header-actions">
                  <el-tooltip :content="dndMode ? '免打扰已开启，关闭后恢复提醒' : '开启免打扰，专注自习'" placement="top">
                    <el-switch
                      v-model="dndMode"
                      size="small"
                      inline-prompt
                      active-text="免打扰"
                      inactive-text="提醒"
                      @change="toggleDnd"
                      class="dnd-switch"
                    />
                  </el-tooltip>
                  <el-button v-if="totalUnread > 0" size="small" text type="primary" @click="handleClearNotifications">一键清除提示</el-button>
                </div>
              </div>

              <div v-if="dndMode" class="dnd-banner">
                <el-icon><Mute /></el-icon>
                <span>免打扰模式已开启，消息提醒已关闭</span>
              </div>

              <div class="notify-body" v-loading="notifyLoading">
                <el-empty v-if="!notifyLoading && notifyList.length === 0 && friendReqList.length === 0" description="暂无消息" :image-size="40" />
                <!-- 好友请求 -->
                <div v-for="req in friendReqList" :key="'req_' + req.id" class="notify-item notify-item-friend" @click="goMessages">
                  <el-avatar :size="36" :style="{ background: '#67c23a' }">{{ (req.nickname || 'U').charAt(0) }}</el-avatar>
                  <div class="notify-content">
                    <div class="notify-text"><b>{{ req.nickname }}</b> 请求添加你为好友</div>
                    <div class="notify-time">{{ formatNotifyTime(req.created_at) }}</div>
                  </div>
                  <el-tag type="warning" size="small">待处理</el-tag>
                </div>
                <!-- 成果社区消息 -->
                <div v-for="msg in notifyList" :key="'msg_' + msg.id" class="notify-item" :class="{ 'notify-unread': !msg.is_read }" @click="handleClickNotify(msg)">
                  <el-avatar :size="36" :style="{ background: notifyColor(msg.type) }">{{ notifyIcon(msg.type) }}</el-avatar>
                  <div class="notify-content">
                    <div class="notify-text">{{ msg.content }}</div>
                    <div class="notify-time">{{ formatNotifyTime(msg.created_at) }}</div>
                  </div>
                  <span v-if="!msg.is_read" class="unread-dot"></span>
                </div>
              </div>

              <div class="notify-footer">
                <el-button size="small" type="primary" plain @click="goMessages">查看全部私信</el-button>
              </div>
            </div>
          </el-popover>

          <!-- 用户下拉 -->
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="authStore.user?.avatar || ''">
                {{ authStore.nickname?.charAt(0) }}
              </el-avatar>
              <span class="username">{{ authStore.nickname }}</span>
              <el-tag size="small" :type="roleTagType">{{ roleLabel }}</el-tag>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="feedback" divided>问题反馈</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 问题反馈对话框 -->
    <el-dialog v-model="feedbackVisible" title="问题反馈" width="560px" :close-on-click-modal="false">
      <el-tabs v-model="feedbackTab">
        <!-- 提交反馈 -->
        <el-tab-pane label="提交反馈" name="create">
          <el-form ref="feedbackFormRef" :model="feedbackForm" :rules="feedbackRules" label-position="top">
            <el-form-item label="问题类型" prop="category">
              <el-radio-group v-model="feedbackForm.category">
                <el-radio value="bug">系统Bug</el-radio>
                <el-radio value="suggestion">功能建议</el-radio>
                <el-radio value="account">账号问题</el-radio>
                <el-radio value="other">其他问题</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="问题标题" prop="title">
              <el-input v-model="feedbackForm.title" placeholder="简要描述遇到的问题" maxlength="100" show-word-limit />
            </el-form-item>
            <el-form-item label="详细描述" prop="content">
              <el-input
                v-model="feedbackForm.content"
                type="textarea"
                :rows="5"
                placeholder="请详细描述问题发生的场景、操作步骤和期望结果，方便管理员定位问题"
                maxlength="1000"
                show-word-limit
              />
            </el-form-item>
            <el-form-item label="联系方式（选填）">
              <el-input v-model="feedbackForm.contact" placeholder="邮箱或手机号，方便管理员联系你" maxlength="100" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 我的反馈 -->
        <el-tab-pane label="我的反馈" name="history">
          <div v-loading="feedbackHistoryLoading" class="feedback-history">
            <el-empty v-if="!feedbackHistoryLoading && feedbackHistory.length === 0" description="暂无反馈记录" :image-size="60" />
            <div v-for="fb in feedbackHistory" :key="fb.id" class="feedback-history-item">
              <div class="fb-item-header">
                <el-tag :type="fbCategoryTagType(fb.category)" size="small">{{ fb.category_label }}</el-tag>
                <el-tag :type="fbStatusTagType(fb.status)" size="small" effect="light">{{ fb.status_label }}</el-tag>
                <span class="fb-item-time">{{ formatNotifyTime(fb.created_at) }}</span>
              </div>
              <div class="fb-item-title">{{ fb.title }}</div>
              <div class="fb-item-content">{{ fb.content }}</div>
              <div v-if="fb.reply" class="fb-item-reply">
                <div class="fb-reply-label">管理员回复：</div>
                <div class="fb-reply-text">{{ fb.reply }}</div>
                <div class="fb-reply-time" v-if="fb.replied_at">{{ formatNotifyTime(fb.replied_at) }}</div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="feedbackVisible = false">关闭</el-button>
        <el-button v-if="feedbackTab === 'create'" type="primary" :loading="feedbackSubmitting" @click="submitFeedback">提交反馈</el-button>
        <el-button v-if="feedbackTab === 'history'" :icon="Refresh" @click="fetchMyFeedbacks">刷新</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell, Mute, Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { achievementApi, friendApi, feedbackApi } from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapse = ref(false)
const unreadCount = ref(0)
const friendRequestCount = ref(0)
let msgTimer = null

// 通知面板
const notifyVisible = ref(false)
const notifyLoading = ref(false)
const notifyList = ref([])
const friendReqList = ref([])

// 免打扰模式（从 localStorage 读取，跨页面保持）
const dndMode = ref(localStorage.getItem('dnd_mode') === 'true')

const totalUnread = computed(() => {
  if (dndMode.value) return 0  // 免打扰时不显示红点
  return unreadCount.value + friendRequestCount.value
})

// 获取当前用户的菜单路由
const menuRoutes = computed(() => {
  const mainRoute = router.options.routes.find((r) => r.path === '/')
  if (!mainRoute?.children) return []
  return mainRoute.children
    .filter((r) => !r.meta?.hidden)
    .filter((r) => {
      // 所有角色都可以使用私信和好友功能
      const roles = r.meta?.roles
      if (!roles) return true
      return roles.includes(authStore.role)
    })
    .map((r) => ({
      ...r,
      fullPath: '/' + r.path,
    }))
})

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title || '')

const roleLabel = computed(() => {
  const map = { student: '学生', teacher: '教师', auditor: '审核员', admin: '管理员' }
  return map[authStore.role] || ''
})

const roleTagType = computed(() => {
  const map = { student: 'success', teacher: 'warning', auditor: 'primary', admin: '' }
  return map[authStore.role] || 'info'
})

async function handleCommand(command) {
  if (command === 'logout') {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'feedback') {
    openFeedbackDialog()
  }
}

// ============ 问题反馈 ============
const feedbackVisible = ref(false)
const feedbackTab = ref('create')
const feedbackSubmitting = ref(false)
const feedbackFormRef = ref()
const feedbackForm = reactive({
  category: 'bug',
  title: '',
  content: '',
  contact: '',
})
const feedbackRules = {
  category: [{ required: true, message: '请选择问题类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入问题标题', trigger: 'blur' }],
  content: [{ required: true, message: '请描述问题详情', trigger: 'blur' }],
}

// 反馈历史
const feedbackHistoryLoading = ref(false)
const feedbackHistory = ref([])

function openFeedbackDialog() {
  feedbackForm.category = 'bug'
  feedbackForm.title = ''
  feedbackForm.content = ''
  feedbackForm.contact = ''
  feedbackTab.value = 'create'
  feedbackVisible.value = true
}

async function submitFeedback() {
  await feedbackFormRef.value.validate(async (valid) => {
    if (!valid) return
    feedbackSubmitting.value = true
    try {
      await feedbackApi.create({
        title: feedbackForm.title,
        content: feedbackForm.content,
        category: feedbackForm.category,
        contact: feedbackForm.contact || undefined,
      })
      ElMessage.success('反馈已提交，管理员将尽快处理')
      feedbackForm.title = ''
      feedbackForm.content = ''
      feedbackForm.contact = ''
      feedbackTab.value = 'history'
      fetchMyFeedbacks()
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      feedbackSubmitting.value = false
    }
  })
}

async function fetchMyFeedbacks() {
  feedbackHistoryLoading.value = true
  try {
    const res = await feedbackApi.my({ page: 1, page_size: 20 })
    feedbackHistory.value = res.data || []
  } catch (e) {
    // 静默处理
  } finally {
    feedbackHistoryLoading.value = false
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

function goMessages() {
  notifyVisible.value = false
  router.push('/messages')
}

async function fetchMessages() {
  if (!authStore.isLoggedIn) return
  try {
    const [msgRes, friendRes] = await Promise.allSettled([
      achievementApi.messages(),
      friendApi.requests(),
    ])
    if (msgRes.status === 'fulfilled') {
      const msgs = msgRes.value.data || []
      notifyList.value = msgs.slice(0, 20)
      unreadCount.value = msgs.filter((m) => !m.is_read).length
    }
    if (friendRes.status === 'fulfilled') {
      const reqs = friendRes.value.data || []
      friendReqList.value = reqs
      friendRequestCount.value = reqs.length
    }
  } catch (e) {
    // 静默处理
  }
}

// 通知面板打开时刷新数据
function onNotifyShow() {
  fetchMessages()
}

// 通知图标颜色
function notifyColor(type) {
  const map = { like: '#f56c6c', comment: '#409eff', reply: '#409eff', system: '#909399' }
  return map[type] || '#909399'
}

// 通知图标文字
function notifyIcon(type) {
  const map = { like: '赞', comment: '评', reply: '回', system: '系' }
  return map[type] || '消'
}

// 格式化时间
function formatNotifyTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
  if (diff < 604800) return Math.floor(diff / 86400) + '天前'
  return d.toLocaleDateString()
}

// 点击通知项
async function handleClickNotify(msg) {
  if (!msg.is_read) {
    try {
      await achievementApi.readMessage(msg.id)
      msg.is_read = 1
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (e) { /* ignore */ }
  }
  notifyVisible.value = false
  if (msg.post_id) {
    router.push(`/achievement?post=${msg.post_id}`)
  } else {
    router.push('/messages')
  }
}

// 免打扰开关
function toggleDnd(val) {
  localStorage.setItem('dnd_mode', String(val))
  if (val) {
    ElMessage.success('已开启免打扰模式，安心自习吧')
  } else {
    ElMessage.success('已关闭免打扰，恢复消息提醒')
  }
}

// 一键清除消息提示（标记已读，消息本身不删除）
async function handleClearNotifications() {
  try {
    await achievementApi.clearNotifications()
    notifyList.value.forEach((m) => { m.is_read = 1 })
    unreadCount.value = 0
    ElMessage.success('已清除所有消息提示')
  } catch (e) { /* ignore */ }
}

onMounted(() => {
  fetchMessages()
  msgTimer = setInterval(fetchMessages, 30000)
})

onUnmounted(() => {
  if (msgTimer) clearInterval(msgTimer)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  border-bottom: 1px solid #3d4d5f;
}

.el-menu {
  border-right: none;
}

.menu-item-relative {
  position: relative;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #5a5e66;
}

.collapse-btn:hover {
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.message-badge {
  cursor: pointer;
}

.bell-icon {
  cursor: pointer;
  color: #5a5e66;
  transition: color 0.2s;
}

.bell-icon:hover {
  color: #409eff;
}

/* 通知面板样式 */
.notify-panel {
  margin: -12px;
}

.notify-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

.notify-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.notify-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dnd-switch {
  --el-switch-on-color: #909399;
  --el-switch-off-color: #409eff;
}

.dnd-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #fdf6ec;
  color: #e6a23c;
  font-size: 12px;
  border-bottom: 1px solid #faecd8;
}

.notify-body {
  max-height: 360px;
  overflow-y: auto;
  padding: 4px 0;
}

.notify-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.notify-item:hover {
  background: #f5f7fa;
}

.notify-unread {
  background: #ecf5ff;
}

.notify-unread:hover {
  background: #d9ecff;
}

.notify-content {
  flex: 1;
  min-width: 0;
}

.notify-text {
  font-size: 13px;
  color: #303133;
  line-height: 1.5;
  word-break: break-word;
}

.notify-time {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f56c6c;
  flex-shrink: 0;
  margin-top: 6px;
}

.notify-footer {
  padding: 8px 16px;
  border-top: 1px solid #ebeef5;
  text-align: center;
}

.menu-badge {
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
}

.menu-badge :deep(.el-badge__content) {
  font-size: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #303133;
}

.main-content {
  background: #f5f7fa;
  overflow-y: auto;
}

/* ---------- 问题反馈 ---------- */
.feedback-history {
  max-height: 400px;
  overflow-y: auto;
}

.feedback-history-item {
  padding: 14px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  margin-bottom: 12px;
}

.fb-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.fb-item-time {
  font-size: 12px;
  color: #c0c4cc;
  margin-left: auto;
}

.fb-item-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.fb-item-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.fb-item-reply {
  margin-top: 10px;
  padding: 10px 12px;
  background: #ecf5ff;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.fb-reply-label {
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 4px;
}

.fb-reply-text {
  font-size: 13px;
  color: #303133;
  line-height: 1.6;
}

.fb-reply-time {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}
</style>
