<template>
  <div class="profile-page">
    <!-- 返回按钮 - 固定在顶部 -->
    <div class="back-bar-fixed">
      <el-button :icon="ArrowLeft" type="primary" plain size="large" @click="goBack" class="back-btn-fixed">
        返回上一页
      </el-button>
      <span class="back-bar-title">用户主页</span>
    </div>

    <!-- 用户信息头部卡片 -->
    <el-card shadow="never" class="profile-header-card" v-loading="profileLoading">
      <div class="profile-header">
        <div class="profile-header-left">
          <el-avatar :size="92" :src="getAvatarUrl(profile.avatar)" class="profile-avatar">
            {{ (profile.nickname || 'U').charAt(0) }}
          </el-avatar>
          <div class="profile-info">
            <div class="profile-name-row">
              <h2 class="profile-nickname">{{ profile.nickname || '未知用户' }}</h2>
              <el-tag :type="roleTagType(profile.role)" effect="dark" size="default">
                {{ roleLabel(profile.role) }}
              </el-tag>
              <el-tag v-if="profile.is_teacher_certified" type="warning" effect="dark" size="small">
                <el-icon class="cert-icon"><Avatar /></el-icon>教师认证
              </el-tag>
            </div>
            <div class="profile-meta">
              <span class="meta-stat">
                <el-icon><Calendar /></el-icon>
                加入于 {{ formatDate(profile.created_at) }}
              </span>
              <span class="meta-divider">|</span>
              <span class="meta-stat">
                <el-icon><Timer /></el-icon>
                累计学习 {{ profile.study_minutes || 0 }} 分钟
              </span>
              <span class="meta-divider">|</span>
              <span class="meta-stat">
                <el-icon><Files /></el-icon>
                {{ profile.resource_count || 0 }} 个资源
              </span>
              <span class="meta-divider">|</span>
              <span class="meta-stat">
                <el-icon><Document /></el-icon>
                {{ profile.post_count || 0 }} 条动态
              </span>
            </div>
          </div>
        </div>

        <div class="profile-header-right">
          <!-- 自己的主页 -->
          <el-button v-if="isSelf" type="primary" plain :icon="Edit" @click="goEditProfile">
            编辑资料
          </el-button>

          <!-- 非好友 -->
          <el-button
            v-else-if="friendStatus === 'none'"
            type="primary"
            :icon="Plus"
            :loading="actionLoading"
            @click="handleAddFriend"
          >
            添加好友
          </el-button>

          <!-- 已发送请求，等待对方同意 -->
          <el-button v-else-if="friendStatus === 'pending_sent'" type="warning" plain disabled>
            等待验证
          </el-button>

          <!-- 对方已发请求 -->
          <el-button v-else-if="friendStatus === 'pending_received'" type="warning" :icon="Bell" disabled>
            待处理请求
          </el-button>

          <!-- 已是好友 -->
          <template v-else-if="friendStatus === 'friend'">
            <el-tag type="success" effect="light" size="large" class="friend-tag">已是好友</el-tag>
            <el-button type="primary" plain :icon="ChatLineRound" @click="goMessage">发私信</el-button>
            <el-button type="danger" text :icon="Delete" @click="handleRemoveFriend">删除好友</el-button>
          </template>
        </div>
      </div>
    </el-card>

    <!-- 标签页内容 -->
    <el-card shadow="never" class="content-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 发布的资源 -->
        <el-tab-pane label="发布的资源" name="resources">
          <div v-loading="resourceLoading" class="tab-content">
            <el-empty v-if="!resourceLoading && resources.length === 0" description="暂无发布的资源" />
            <div v-else class="resource-list">
              <div
                v-for="item in resources"
                :key="item.id"
                class="resource-item"
                @click="goResourceDetail(item.id)"
              >
                <div class="resource-item-main">
                  <span class="resource-item-title">{{ item.title }}</span>
                  <el-tag size="small" :type="categoryTagType(item.category)" effect="light">
                    {{ item.category || '未分类' }}
                  </el-tag>
                </div>
                <div class="resource-item-meta">
                  <span class="meta-item">
                    <el-icon><View /></el-icon>
                    {{ item.view_count || 0 }} 浏览
                  </span>
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    {{ formatDate(item.created_at) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <!-- 分页 -->
          <div v-if="resourceTotal > 0" class="pagination-wrap">
            <el-pagination
              v-model:current-page="resourcePage"
              v-model:page-size="resourcePageSize"
              :total="resourceTotal"
              :page-sizes="[5, 10, 20]"
              layout="total, prev, pager, next"
              background
              small
              @current-change="fetchResources"
            />
          </div>
        </el-tab-pane>

        <!-- 成果动态 -->
        <el-tab-pane label="成果动态" name="posts">
          <div v-loading="postLoading" class="tab-content">
            <el-empty v-if="!postLoading && posts.length === 0" description="暂无成果动态" />
            <div v-else class="post-list">
              <el-card
                v-for="post in posts"
                :key="post.id"
                shadow="hover"
                class="post-item"
              >
                <div class="post-content">{{ post.content }}</div>
                <div class="post-meta">
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    {{ formatDate(post.created_at) }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Star /></el-icon>
                    {{ post.like_count || 0 }} 点赞
                  </span>
                </div>
              </el-card>
            </div>
          </div>
          <!-- 分页 -->
          <div v-if="postTotal > 0" class="pagination-wrap">
            <el-pagination
              v-model:current-page="postPage"
              v-model:page-size="postPageSize"
              :total="postTotal"
              :page-sizes="[5, 10, 20]"
              layout="total, prev, pager, next"
              background
              small
              @current-change="fetchPosts"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 推荐好友 -->
    <el-card shadow="never" class="recommend-card">
      <template #header>
        <div class="card-header">
          <span>
            <el-icon><UserFilled /></el-icon>
            推荐好友
          </span>
        </div>
      </template>
      <div v-loading="recommendLoading" class="recommend-list">
        <el-empty v-if="!recommendLoading && recommends.length === 0" description="暂无推荐" :image-size="60" />
        <div
          v-for="user in recommends"
          :key="user.id"
          class="recommend-item"
          @click="goUserProfile(user.id)"
        >
          <el-avatar :size="48" :src="getAvatarUrl(user.avatar)" class="recommend-avatar">
            {{ (user.nickname || 'U').charAt(0) }}
          </el-avatar>
          <div class="recommend-info">
            <span class="recommend-name">{{ user.nickname || '未知用户' }}</span>
            <el-tag :type="roleTagType(user.role)" size="small" effect="plain">
              {{ roleLabel(user.role) }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Bell, ChatLineRound, Delete, Edit, Calendar, Timer,
  Files, Document, View, Clock, Star, UserFilled, Avatar, ArrowLeft,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { userApi, friendApi } from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 返回上一页：优先返回历史记录，无有效历史时回到成果社区
function goBack() {
  // window.history.state.back 由 Vue Router 设置，表示有可返回的上一页
  if (window.history.state && window.history.state.back) {
    router.go(-1)
  } else {
    router.push('/achievement')
  }
}

// ============ 角色与工具函数 ============
const roleLabelMap = {
  student: '学生',
  teacher: '教师',
  auditor: '审核员',
  admin: '管理员',
}

function roleLabel(role) {
  return roleLabelMap[role] || '未知'
}

function roleTagType(role) {
  const map = { student: 'success', teacher: 'warning', auditor: 'primary', admin: '' }
  return map[role] || 'info'
}

function categoryTagType(category) {
  const map = {
    '考研': 'danger',
    '考证': 'warning',
    '专业课': 'success',
    '技能学习': 'primary',
    '其他': 'info',
  }
  return map[category] || 'info'
}

function getAvatarUrl(avatar) {
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  const base = import.meta.env.VITE_API_BASE_URL.replace('/api', '')
  return base + avatar
}

function formatDate(t) {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function pad(n) {
  return String(n).padStart(2, '0')
}

// ============ 用户资料 ============
const profileLoading = ref(false)
const profile = ref({})
const friendStatus = ref('none')
const actionLoading = ref(false)

const isSelf = computed(() => {
  const uid = Number(route.params.userId)
  return authStore.user?.id && uid === authStore.user.id
})

async function fetchProfile() {
  profileLoading.value = true
  try {
    console.log('[UserProfile] fetchProfile for userId:', route.params.userId)
    const res = await userApi.profile(route.params.userId)
    const data = res.data || {}
    console.log('[UserProfile] API response data:', data)
    // 后端返回 { basic_info: {...}, resource_count, post_count, total_study_minutes, friend_status, ... }
    // 展平到 profile 上，使模板可直接访问 profile.nickname 等
    const bi = data.basic_info || {}
    profile.value = {
      id: bi.id,
      nickname: bi.nickname,
      username: bi.username,
      avatar: bi.avatar,
      role: bi.role,
      created_at: bi.created_at,
      cert_status: bi.cert_status,
      is_teacher_certified: bi.is_teacher_certified,
      resource_count: data.resource_count || 0,
      post_count: data.post_count || 0,
      study_minutes: data.total_study_minutes || 0,
    }
    console.log('[UserProfile] profile set:', profile.value)
    // 如果接口返回了好友状态，直接使用
    if (data.friend_status && data.friend_status !== 'self') {
      friendStatus.value = data.friend_status
    }
  } catch (e) {
    console.error('[UserProfile] fetchProfile error:', e)
    // 错误已由拦截器处理
  } finally {
    profileLoading.value = false
  }
}

async function fetchFriendStatus() {
  if (isSelf.value) {
    friendStatus.value = 'none'
    return
  }
  try {
    const res = await friendApi.status(route.params.userId)
    if (res.data) {
      friendStatus.value = res.data.status || 'none'
    }
  } catch (e) {
    // 静默处理
  }
}

// ============ 好友操作 ============
async function handleAddFriend() {
  actionLoading.value = true
  try {
    await friendApi.sendRequest({ receiver_id: Number(route.params.userId) })
    ElMessage.success('好友请求已发送')
    friendStatus.value = 'pending_sent'
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    actionLoading.value = false
  }
}

async function handleRemoveFriend() {
  try {
    await ElMessageBox.confirm('确定要删除该好友吗？', '提示', { type: 'warning' })
    await friendApi.remove(route.params.userId)
    ElMessage.success('已删除好友')
    friendStatus.value = 'none'
  } catch (e) {
    // 取消或错误
  }
}

function goMessage() {
  router.push('/messages')
}

function goEditProfile() {
  router.push('/profile')
}

// ============ 标签页 ============
const activeTab = ref('resources')
const loadedTabs = ref({ resources: false, posts: false })

const resourceLoading = ref(false)
const resources = ref([])
const resourceTotal = ref(0)
const resourcePage = ref(1)
const resourcePageSize = ref(10)

const postLoading = ref(false)
const posts = ref([])
const postTotal = ref(0)
const postPage = ref(1)
const postPageSize = ref(10)

function handleTabChange(tabName) {
  if (tabName === 'resources' && !loadedTabs.value.resources) {
    fetchResources()
  } else if (tabName === 'posts' && !loadedTabs.value.posts) {
    fetchPosts()
  }
}

async function fetchResources() {
  resourceLoading.value = true
  try {
    const res = await userApi.userResources(route.params.userId, {
      page: resourcePage.value,
      page_size: resourcePageSize.value,
    })
    resources.value = res.data || []
    resourceTotal.value = res.total || 0
    loadedTabs.value.resources = true
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    resourceLoading.value = false
  }
}

async function fetchPosts() {
  postLoading.value = true
  try {
    const res = await userApi.userPosts(route.params.userId, {
      page: postPage.value,
      page_size: postPageSize.value,
    })
    posts.value = res.data || []
    postTotal.value = res.total || 0
    loadedTabs.value.posts = true
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    postLoading.value = false
  }
}

function goResourceDetail(id) {
  router.push('/market/' + id)
}

// ============ 推荐好友 ============
const recommendLoading = ref(false)
const recommends = ref([])

async function fetchRecommends() {
  recommendLoading.value = true
  try {
    const res = await userApi.recommend()
    recommends.value = res.data || []
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    recommendLoading.value = false
  }
}

function goUserProfile(userId) {
  router.push('/user/' + userId)
}

// ============ 初始化 & 路由监听 ============
async function loadProfileData() {
  await Promise.allSettled([fetchProfile(), fetchFriendStatus()])
  // 重置标签页状态并加载默认 tab
  loadedTabs.value = { resources: false, posts: false }
  resourcePage.value = 1
  postPage.value = 1
  resources.value = []
  posts.value = []
  resourceTotal.value = 0
  postTotal.value = 0
  activeTab.value = 'resources'
  fetchResources()
}

onMounted(() => {
  // 强制确保路由参数存在且有效
  const uid = route.params.userId
  console.log('[UserProfile] onMounted, userId from route:', uid, 'current user:', authStore.user?.id)
  if (!uid) {
    console.warn('[UserProfile] No userId in route, redirecting to /achievement')
    router.replace('/achievement')
    return
  }
  loadProfileData()
  fetchRecommends()
})

// 监听 userId 变化（从推荐好友跳转时复用同一组件）
watch(
  () => route.params.userId,
  (newId) => {
    if (newId) {
      friendStatus.value = 'none'
      loadProfileData()
    }
  }
)
</script>

<style scoped>
.profile-page {
  padding: 20px;
}

/* ---------- 返回按钮 - 固定顶部 ---------- */
.back-bar-fixed {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border-radius: 8px;
  margin-bottom: 16px;
}
.back-btn-fixed {
  font-weight: 600;
}
.back-bar-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* ---------- 头部卡片 ---------- */
.profile-header-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%);
  border: none;
  box-shadow: 0 2px 12px rgba(102, 89, 167, 0.08);
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.profile-header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.profile-avatar {
  background: #6c5ce7;
  color: #fff;
  font-size: 32px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.profile-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.profile-nickname {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.cert-icon {
  margin-right: 2px;
  vertical-align: -2px;
}

.profile-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  color: #606266;
  font-size: 13px;
}

.meta-stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.meta-divider {
  color: #dcdfe6;
}

.profile-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.friend-tag {
  font-weight: 600;
}

/* ---------- 内容卡片 ---------- */
.content-card {
  margin-bottom: 20px;
}

.tab-content {
  min-height: 240px;
}

/* ---------- 资源列表 ---------- */
.resource-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
}

.resource-item:hover {
  background: #f5f3ff;
  border-color: #d3c5f5;
  transform: translateX(2px);
}

.resource-item-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.resource-item-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-item-meta {
  display: flex;
  align-items: center;
  gap: 18px;
  color: #909399;
  font-size: 13px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* ---------- 成果动态列表 ---------- */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-item {
  margin-bottom: 0;
}

.post-content {
  font-size: 15px;
  line-height: 1.7;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 18px;
  color: #909399;
  font-size: 13px;
  padding-top: 10px;
  border-top: 1px dashed #ebeef5;
}

/* ---------- 分页 ---------- */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

/* ---------- 推荐好友 ---------- */
.recommend-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  font-weight: 600;
}

.card-header span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.recommend-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
  min-height: 60px;
}

.recommend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: #fafafa;
  border-radius: 10px;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
}

.recommend-item:hover {
  background: #f5f3ff;
  border-color: #d3c5f5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 92, 231, 0.1);
}

.recommend-avatar {
  background: #6c5ce7;
  color: #fff;
  flex-shrink: 0;
}

.recommend-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.recommend-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---------- 响应式 ---------- */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-header-right {
    width: 100%;
    flex-wrap: wrap;
  }

  .profile-meta {
    gap: 6px;
  }

  .meta-divider {
    display: none;
  }
}
</style>
