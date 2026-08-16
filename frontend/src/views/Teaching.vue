<template>
  <div class="teaching-page">
    <div class="page-header">
      <h2>教学管理</h2>
      <p class="page-desc">教师专属功能：查看教学资源数据、学生互动统计、发布教学公告</p>
    </div>

    <!-- 数据概览 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-card-blue">
          <div class="stat-icon">📚</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.resourceCount }}</div>
            <div class="stat-label">已发布资源</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-card-green">
          <div class="stat-icon">👁️</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalViews }}</div>
            <div class="stat-label">总浏览量</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-card-orange">
          <div class="stat-icon">🏆</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.postCount }}</div>
            <div class="stat-label">成果动态</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-card-purple">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.studentCount }}</div>
            <div class="stat-label">互动学生数</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 功能区 -->
    <el-row :gutter="20">
      <!-- 左侧：我的资源数据 -->
      <el-col :xs="24" :md="16">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span>📊 我的资源数据</span>
              <el-button text @click="goToMarket">前往资源集市</el-button>
            </div>
          </template>
          <div v-loading="loading" class="resource-list">
            <el-empty v-if="!loading && resources.length === 0" description="暂无发布的资源" :image-size="80" />
            <div
              v-for="item in resources"
              :key="item.id"
              class="resource-item"
              @click="goToResource(item.id)"
            >
              <div class="resource-main">
                <span class="resource-title">{{ item.title }}</span>
                <el-tag size="small" :type="categoryTagType(item.category)" effect="light">
                  {{ item.category || '未分类' }}
                </el-tag>
                <el-tag v-if="item.audit_status === 'approved'" size="small" type="success" effect="plain">已通过</el-tag>
                <el-tag v-else-if="item.audit_status === 'pending'" size="small" type="warning" effect="plain">审核中</el-tag>
              </div>
              <div class="resource-meta">
                <span>👁️ {{ item.view_count || 0 }} 浏览</span>
                <span>📅 {{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 最近互动的学生 -->
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span>💬 最近互动的学生</span>
            </div>
          </template>
          <div v-loading="loading" class="student-list">
            <el-empty v-if="!loading && students.length === 0" description="暂无学生互动" :image-size="80" />
            <div
              v-for="student in students"
              :key="student.id"
              class="student-item"
              @click="goToProfile(student.id)"
            >
              <el-avatar :size="40" :src="getAvatarUrl(student.avatar)">
                {{ (student.nickname || 'U').charAt(0) }}
              </el-avatar>
              <div class="student-info">
                <div class="student-name">{{ student.nickname || '未知用户' }}</div>
                <div class="student-action">{{ student.action }}</div>
              </div>
              <div class="student-time">{{ formatDate(student.created_at) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：快捷操作 -->
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span>⚡ 快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <div class="quick-action-item" @click="goToPublishResource">
              <div class="quick-action-icon">📎</div>
              <div class="quick-action-text">
                <div class="quick-action-title">发布教学资源</div>
                <div class="quick-action-desc">上传课件、习题等</div>
              </div>
            </div>
            <div class="quick-action-item" @click="goToAchievement">
              <div class="quick-action-icon">🏆</div>
              <div class="quick-action-text">
                <div class="quick-action-title">发布成果动态</div>
                <div class="quick-action-desc">分享教学心得</div>
              </div>
            </div>
            <div class="quick-action-item" @click="goToStudyRoom">
              <div class="quick-action-icon">🏠</div>
              <div class="quick-action-text">
                <div class="quick-action-title">创建自习房间</div>
                <div class="quick-action-desc">带领学生一起学习</div>
              </div>
            </div>
            <div class="quick-action-item" @click="goToAITask">
              <div class="quick-action-icon">🤖</div>
              <div class="quick-action-text">
                <div class="quick-action-title">生成学习计划</div>
                <div class="quick-action-desc">为学生定制计划</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 教师认证状态 -->
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span>🎓 教师认证</span>
            </div>
          </template>
          <div class="cert-status">
            <el-tag :type="certTagType" size="default" effect="light" round>{{ certLabel }}</el-tag>
            <p class="cert-desc">
              <span v-if="certStatus === 'approved'">已通过教师实名认证，发布的资源将显示"教师认证"标识</span>
              <span v-else-if="certStatus === 'pending'">认证审核中，请耐心等待</span>
              <span v-else>完成教师认证后，资源将显示认证标识，更容易被学生发现</span>
            </p>
            <el-button v-if="certStatus !== 'approved' && certStatus !== 'pending'" type="primary" plain @click="goToProfile">
              前往认证
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { marketApi, achievementApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const resources = ref([])
const students = ref([])

const stats = computed(() => ({
  resourceCount: resources.value.length,
  totalViews: resources.value.reduce((sum, r) => sum + (r.view_count || 0), 0),
  postCount: students.value.filter(s => s.action?.includes('成果')).length,
  studentCount: new Set(students.value.map(s => s.id)).size,
}))

const certStatus = computed(() => authStore.user?.cert_status || 'none')
const certLabel = computed(() => {
  const map = { pending: '审核中', approved: '已认证', rejected: '未通过', none: '未认证' }
  return map[certStatus.value] || '未认证'
})
const certTagType = computed(() => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger', none: 'info' }
  return map[certStatus.value] || 'info'
})

function categoryTagType(category) {
  const map = { '考研': 'danger', '考证': 'warning', '专业课': 'success', '技能学习': 'primary', '其他': 'info' }
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
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function goToMarket() { router.push('/market') }
function goToResource(id) { router.push(`/market/${id}`) }
function goToAchievement() { router.push('/achievement') }
function goToStudyRoom() { router.push('/study-room') }
function goToAITask() { router.push('/ai-task') }
function goToProfile() { router.push('/profile') }
function goToPublishResource() { router.push('/market') }

async function loadData() {
  loading.value = true
  try {
    // 获取教师发布的资源
    const res = await marketApi.myResources?.() || marketApi.list({ publisher_id: authStore.user?.id })
    if (res.data) {
      resources.value = Array.isArray(res.data) ? res.data : (res.data.items || res.data.list || [])
    }
  } catch (e) {
    // 静默处理
  }

  try {
    // 获取教师发布的成果帖（作为学生互动的来源）
    const res = await achievementApi.posts()
    if (res.data) {
      const myPosts = res.data.filter(p => p.user_id === authStore.user?.id)
      students.value = myPosts.slice(0, 10).map(p => ({
        id: p.user_id,
        nickname: p.author_name,
        avatar: p.author_avatar,
        action: `发布了成果动态`,
        created_at: p.created_at,
      }))
    }
  } catch (e) {
    // 静默处理
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.teaching-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 6px 0;
  font-size: 22px;
  color: #303133;
}

.page-desc {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

/* 统计卡片 */
.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.stat-card-blue { background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%); }
.stat-card-green { background: linear-gradient(135deg, #f0f9eb 0%, #f5fbeb 100%); }
.stat-card-orange { background: linear-gradient(135deg, #fdf6ec 0%, #fefaf3 100%); }
.stat-card-purple { background: linear-gradient(135deg, #f5f3ff 0%, #faf8ff 100%); }

.stat-icon {
  font-size: 32px;
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
  margin-top: 2px;
}

/* 通用卡片 */
.section-card {
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
  border: none;
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  font-size: 15px;
}

/* 资源列表 */
.resource-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
}

.resource-item:hover {
  background: #f5f3ff;
  border-color: #d3c5f5;
}

.resource-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.resource-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

/* 学生列表 */
.student-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.student-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.2s;
}

.student-item:hover {
  background: #f0f9ff;
}

.student-info {
  flex: 1;
  min-width: 0;
}

.student-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.student-action {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.student-time {
  font-size: 12px;
  color: #c0c4cc;
  flex-shrink: 0;
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-action-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 10px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-action-item:hover {
  background: #f5f3ff;
  border-color: #d3c5f5;
  transform: translateX(4px);
}

.quick-action-icon {
  font-size: 24px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 10px;
  flex-shrink: 0;
}

.quick-action-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.quick-action-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* 认证状态 */
.cert-status {
  text-align: center;
  padding: 10px 0;
}

.cert-desc {
  font-size: 13px;
  color: #909399;
  margin: 12px 0;
  line-height: 1.6;
}
</style>
