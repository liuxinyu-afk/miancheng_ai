<template>
  <div class="messages-page">
    <div class="page-header">
      <h2>私信 & 好友</h2>
      <el-button type="primary" :icon="Search" @click="openAddFriendDialog">添加好友</el-button>
    </div>

    <div class="chat-container">
      <!-- 左侧：标签切换面板 -->
      <div class="conv-panel">
        <el-tabs v-model="activeTab" class="conv-tabs">
          <!-- 好友列表 -->
          <el-tab-pane label="好友" name="friends">
            <template #label>
              <span>好友</span>
              <el-badge v-if="friends.length" :value="friends.length" type="info" class="tab-badge" />
            </template>
            <div class="conv-list" v-loading="friendsLoading">
              <el-empty v-if="!friendsLoading && friends.length === 0" description="暂无好友，去添加吧" :image-size="60" />
              <div
                v-for="f in friends"
                :key="f.id"
                class="conv-item"
                :class="{ active: activeUserId === f.id }"
                @click="selectFriend(f.id)"
              >
                <el-avatar :size="44" class="conv-avatar">{{ f.nickname?.charAt(0) }}</el-avatar>
                <div class="conv-info">
                  <div class="conv-top-row">
                    <span class="conv-name">{{ f.nickname }}</span>
                    <el-tag size="small" :type="roleTagType(f.role)" effect="plain">{{ roleLabel(f.role) }}</el-tag>
                  </div>
                  <div class="conv-bottom-row">
                    <span class="conv-last-msg">@{{ f.username }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 会话列表 -->
          <el-tab-pane label="会话" name="conversations">
            <template #label>
              <span>会话</span>
              <el-badge v-if="totalUnread > 0" :value="totalUnread" type="danger" class="tab-badge" />
            </template>
            <div class="conv-list" v-loading="convLoading">
              <el-empty v-if="!convLoading && conversations.length === 0" description="暂无会话" :image-size="60" />
              <div
                v-for="conv in conversations"
                :key="conv.id"
                class="conv-item"
                :class="{ active: activeUserId === conv.other_user.id }"
                @click="selectConversation(conv.other_user.id)"
              >
                <el-avatar :size="44" class="conv-avatar">{{ conv.other_user.nickname?.charAt(0) }}</el-avatar>
                <div class="conv-info">
                  <div class="conv-top-row">
                    <span class="conv-name">{{ conv.other_user.nickname }}</span>
                    <el-tag size="small" :type="roleTagType(conv.other_user.role)" effect="plain">{{ roleLabel(conv.other_user.role) }}</el-tag>
                  </div>
                  <div class="conv-bottom-row">
                    <span class="conv-last-msg">{{ conv.last_message || '暂无消息' }}</span>
                    <span class="conv-time" v-if="conv.last_message_at">{{ formatTime(conv.last_message_at) }}</span>
                  </div>
                </div>
                <div class="conv-badge" v-if="conv.unread_count > 0">{{ conv.unread_count }}</div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 好友请求 -->
          <el-tab-pane label="请求" name="requests">
            <template #label>
              <span>请求</span>
              <el-badge v-if="friendRequests.length > 0" :value="friendRequests.length" type="danger" class="tab-badge" />
            </template>
            <div class="conv-list" v-loading="requestsLoading">
              <el-empty v-if="!requestsLoading && friendRequests.length === 0" description="暂无好友请求" :image-size="60" />
              <div v-for="req in friendRequests" :key="req.id" class="conv-item request-item">
                <el-avatar :size="44" class="conv-avatar" @click="goToProfile(req.user?.id)">{{ req.user?.nickname?.charAt(0) }}</el-avatar>
                <div class="conv-info">
                  <div class="conv-top-row">
                    <span class="conv-name" @click="goToProfile(req.user?.id)" style="cursor: pointer">{{ req.user?.nickname }}</span>
                    <el-tag size="small" :type="roleTagType(req.user?.role)" effect="plain">{{ roleLabel(req.user?.role) }}</el-tag>
                  </div>
                  <div class="conv-bottom-row">
                    <span class="conv-last-msg">请求添加你为好友</span>
                    <span class="conv-time" v-if="req.created_at">{{ formatTime(req.created_at) }}</span>
                  </div>
                </div>
                <div class="request-actions">
                  <el-button type="primary" size="small" @click="acceptRequest(req.id)">同意</el-button>
                  <el-button size="small" @click="rejectRequest(req.id)">拒绝</el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 推荐好友 -->
          <el-tab-pane label="推荐" name="recommend">
            <template #label>
              <span>推荐</span>
              <el-icon style="margin-left: 4px; font-size: 12px"><Star /></el-icon>
            </template>
            <div class="conv-list" v-loading="recommendLoading">
              <el-empty v-if="!recommendLoading && recommendUsers.length === 0" description="暂无推荐" :image-size="60" />
              <div v-for="user in recommendUsers" :key="user.id" class="conv-item recommend-item">
                <el-avatar :size="44" class="conv-avatar" @click="goToProfile(user.id)" style="cursor: pointer">{{ user.nickname?.charAt(0) }}</el-avatar>
                <div class="conv-info">
                  <div class="conv-top-row">
                    <span class="conv-name" @click="goToProfile(user.id)" style="cursor: pointer">{{ user.nickname }}</span>
                    <el-tag size="small" :type="roleTagType(user.role)" effect="plain">{{ roleLabel(user.role) }}</el-tag>
                  </div>
                  <div class="conv-bottom-row">
                    <span class="conv-last-msg">{{ user.resource_count || 0 }} 个资源 · {{ user.achievement_count || 0 }} 条动态</span>
                  </div>
                </div>
                <el-button
                  v-if="user.friend_status !== 'pending_sent'"
                  type="primary"
                  size="small"
                  plain
                  @click="addRecommendFriend(user)"
                >加好友</el-button>
                <el-tag v-else type="warning" size="small">待同意</el-tag>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 右侧：聊天窗口 -->
      <div class="chat-panel">
        <template v-if="activeUserId">
          <div class="chat-header">
            <div class="chat-header-user">
              <el-avatar :size="36" class="chat-header-avatar">{{ activeUserInfo?.nickname?.charAt(0) }}</el-avatar>
              <div>
                <div class="chat-header-name">{{ activeUserInfo?.nickname }}</div>
                <div class="chat-header-role">
                  <el-tag size="small" :type="roleTagType(activeUserInfo?.role)" effect="plain">{{ roleLabel(activeUserInfo?.role) }}</el-tag>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-messages" ref="chatMessagesRef" v-loading="msgLoading">
            <div v-for="msg in chatMessages" :key="msg.id" class="msg-row" :class="{ 'msg-mine': msg.sender_id === authStore.user?.id }">
              <div class="msg-bubble">
                <div class="msg-text">{{ msg.content }}</div>
                <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
              </div>
            </div>
            <el-empty v-if="!msgLoading && chatMessages.length === 0" description="开始你的第一次对话吧" :image-size="60" />
          </div>

          <div class="chat-input-area">
            <el-input v-model="inputText" type="textarea" :rows="2" placeholder="输入消息..." maxlength="2000" @keydown.enter.exact.prevent="sendMessage" />
            <el-button type="primary" :loading="sending" @click="sendMessage" :disabled="!inputText.trim()">发送</el-button>
          </div>
        </template>

        <div v-else class="chat-placeholder">
          <el-icon :size="60" color="#dcdfe6"><ChatLineRound /></el-icon>
          <p>选择好友或会话开始聊天</p>
        </div>
      </div>
    </div>

    <!-- 添加好友对话框 -->
    <el-dialog v-model="addFriendDialogVisible" title="添加好友" width="480px">
      <el-input v-model="searchKeyword" placeholder="搜索用户名或昵称..." :prefix-icon="Search" clearable @input="handleSearch" style="margin-bottom: 16px" />
      <div class="user-search-list" v-loading="searchLoading">
        <el-empty v-if="!searchLoading && searchResults.length === 0 && searchKeyword" description="未找到用户" :image-size="60" />
        <el-empty v-if="!searchLoading && searchResults.length === 0 && !searchKeyword" description="输入关键词搜索用户" :image-size="60" />
        <div v-for="user in searchResults" :key="user.id" class="user-search-item">
          <el-avatar :size="36" class="user-search-avatar" @click="goToProfile(user.id)" style="cursor: pointer">{{ user.nickname?.charAt(0) }}</el-avatar>
          <div class="user-search-info">
            <div class="user-search-name" @click="goToProfile(user.id)" style="cursor: pointer">{{ user.nickname }}</div>
            <div class="user-search-meta">
              <el-tag size="small" :type="roleTagType(user.role)" effect="plain">{{ roleLabel(user.role) }}</el-tag>
              <span class="user-search-username">@{{ user.username }}</span>
            </div>
          </div>
          <!-- 根据好友状态显示不同按钮 -->
          <el-button v-if="user.friend_status === 'none'" type="primary" size="small" plain @click="sendFriendRequest(user)">加好友</el-button>
          <el-tag v-else-if="user.friend_status === 'friend'" type="success" size="small">已好友</el-tag>
          <el-tag v-else-if="user.friend_status === 'pending_sent'" type="warning" size="small">待对方同意</el-tag>
          <el-tag v-else-if="user.friend_status === 'pending_received'" type="danger" size="small">对方已申请</el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, ChatLineRound, Star } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { messageApi, friendApi, userApi } from '@/api'

const authStore = useAuthStore()
const router = useRouter()

// ============ 标签页 ============
const activeTab = ref('friends')

// ============ 好友列表 ============
const friendsLoading = ref(false)
const friends = ref([])

async function fetchFriends() {
  friendsLoading.value = true
  try {
    const res = await friendApi.list()
    friends.value = res.data || []
  } catch (e) {} finally {
    friendsLoading.value = false
  }
}

// ============ 会话列表 ============
const convLoading = ref(false)
const conversations = ref([])
const totalUnread = computed(() => conversations.value.reduce((sum, c) => sum + (c.unread_count || 0), 0))

async function fetchConversations() {
  convLoading.value = true
  try {
    const res = await messageApi.conversations()
    conversations.value = res.data || []
  } catch (e) {} finally {
    convLoading.value = false
  }
}

// ============ 好友请求 ============
const requestsLoading = ref(false)
const friendRequests = ref([])

async function fetchFriendRequests() {
  requestsLoading.value = true
  try {
    const res = await friendApi.requests()
    friendRequests.value = res.data || []
  } catch (e) {} finally {
    requestsLoading.value = false
  }
}

async function acceptRequest(friendshipId) {
  try {
    await friendApi.accept(friendshipId)
    ElMessage.success('已同意好友请求')
    await fetchFriendRequests()
    await fetchFriends()
  } catch (e) {}
}

async function rejectRequest(friendshipId) {
  try {
    await friendApi.reject(friendshipId)
    ElMessage.success('已拒绝好友请求')
    await fetchFriendRequests()
  } catch (e) {}
}

// ============ 消息记录 ============
const msgLoading = ref(false)
const chatMessages = ref([])
const chatMessagesRef = ref(null)
const activeUserId = ref(null)

const activeUserInfo = computed(() => {
  if (!activeUserId.value) return null
  const conv = conversations.value.find((c) => c.other_user.id === activeUserId.value)
  if (conv) return conv.other_user
  const friend = friends.value.find((f) => f.id === activeUserId.value)
  return friend || null
})

async function selectConversation(userId) {
  activeUserId.value = userId
  await fetchMessages(userId)
}

async function selectFriend(friendId) {
  activeUserId.value = friendId
  await fetchMessages(friendId)
}

async function fetchMessages(userId) {
  msgLoading.value = true
  try {
    const res = await messageApi.messages(userId)
    if (res.data) {
      chatMessages.value = res.data.messages || []
      const conv = conversations.value.find((c) => c.other_user.id === userId)
      if (conv) conv.unread_count = 0
    }
    await nextTick()
    scrollToBottom()
  } catch (e) {} finally {
    msgLoading.value = false
  }
}

function scrollToBottom() {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

// ============ 发送消息 ============
const inputText = ref('')
const sending = ref(false)

async function sendMessage() {
  if (!inputText.value.trim() || !activeUserId.value) return
  sending.value = true
  try {
    await messageApi.send({ receiver_id: activeUserId.value, content: inputText.value.trim() })
    inputText.value = ''
    await fetchMessages(activeUserId.value)
    await fetchConversations()
  } catch (e) {} finally {
    sending.value = false
  }
}

// ============ 添加好友搜索 ============
const addFriendDialogVisible = ref(false)
const searchKeyword = ref('')
const searchLoading = ref(false)
const searchResults = ref([])
let searchTimer = null

function openAddFriendDialog() {
  searchKeyword.value = ''
  searchResults.value = []
  addFriendDialogVisible.value = true
}

function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }
  searchTimer = setTimeout(async () => {
    searchLoading.value = true
    try {
      const res = await friendApi.search(searchKeyword.value.trim())
      searchResults.value = res.data || []
    } catch (e) {} finally {
      searchLoading.value = false
    }
  }, 300)
}

async function sendFriendRequest(user) {
  try {
    await friendApi.sendRequest({ receiver_id: user.id })
    ElMessage.success(`已向 ${user.nickname} 发送好友请求`)
    user.friend_status = 'pending_sent'
  } catch (e) {}
}

// ============ 推荐好友 ============
const recommendLoading = ref(false)
const recommendUsers = ref([])

async function fetchRecommend() {
  recommendLoading.value = true
  try {
    const res = await userApi.recommend()
    recommendUsers.value = res.data || []
  } catch (e) {} finally {
    recommendLoading.value = false
  }
}

async function addRecommendFriend(user) {
  try {
    await friendApi.sendRequest({ receiver_id: user.id })
    ElMessage.success(`已向 ${user.nickname} 发送好友请求`)
    user.friend_status = 'pending_sent'
  } catch (e) {}
}

// ============ 跳转用户主页 ============
function goToProfile(userId) {
  router.push(`/user/${userId}`)
}

// ============ 工具函数 ============
function roleLabel(role) {
  const map = { student: '学生', teacher: '教师', auditor: '审核员', admin: '管理员' }
  return map[role] || '用户'
}

function roleTagType(role) {
  const map = { student: 'success', teacher: 'warning', auditor: 'danger', admin: '' }
  return map[role] || 'info'
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

onMounted(() => {
  fetchFriends()
  fetchConversations()
  fetchFriendRequests()
  fetchRecommend()
})
</script>

<style scoped>
.messages-page {
  padding: 20px;
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
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

.chat-container {
  flex: 1;
  display: flex;
  gap: 16px;
  overflow: hidden;
}

/* ---------- 左侧面板 ---------- */
.conv-panel {
  width: 340px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.conv-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.conv-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 12px;
}

.conv-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

.conv-tabs :deep(.el-tab-pane) {
  height: 100%;
}

.tab-badge {
  margin-left: 4px;
}

.conv-list {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
  position: relative;
}

.conv-item:hover {
  background: #f5f7fa;
}

.conv-item.active {
  background: #ecf5ff;
}

.conv-avatar {
  background: #409eff;
  color: #fff;
  flex-shrink: 0;
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-top-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.conv-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conv-bottom-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.conv-last-msg {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.conv-time {
  font-size: 11px;
  color: #c0c4cc;
  flex-shrink: 0;
}

.conv-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #f56c6c;
  color: #fff;
  font-size: 11px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}

.request-item {
  cursor: default;
}

.request-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

/* ---------- 聊天窗口 ---------- */
.chat-panel {
  flex: 1;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}

.chat-header-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-header-avatar {
  background: #67c23a;
  color: #fff;
}

.chat-header-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chat-header-role {
  margin-top: 2px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
}

.msg-row {
  display: flex;
  margin-bottom: 12px;
}

.msg-mine {
  justify-content: flex-end;
}

.msg-bubble {
  max-width: 60%;
  padding: 10px 14px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.msg-mine .msg-bubble {
  background: #409eff;
  color: #fff;
}

.msg-text {
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.msg-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
  text-align: right;
}

.msg-mine .msg-time {
  color: rgba(255, 255, 255, 0.7);
}

.chat-input-area {
  padding: 12px 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-shrink: 0;
}

.chat-input-area .el-input {
  flex: 1;
}

.chat-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.chat-placeholder p {
  margin-top: 16px;
  font-size: 14px;
}

/* ---------- 搜索用户列表 ---------- */
.user-search-list {
  max-height: 360px;
  overflow-y: auto;
}

.user-search-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-search-item:hover {
  background: #f5f7fa;
}

.user-search-avatar {
  background: #409eff;
  color: #fff;
  flex-shrink: 0;
}

.user-search-info {
  flex: 1;
}

.user-search-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.user-search-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}

.user-search-username {
  font-size: 12px;
  color: #c0c4cc;
}
</style>
