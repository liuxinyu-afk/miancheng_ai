<template>
  <div class="page-container">
    <!-- ==================== 管理员仪表盘 ==================== -->
    <template v-if="authStore.isAdmin">
      <h2 class="page-title">系统概览</h2>

      <!-- 统计卡片 -->
      <div class="stat-grid">
        <div
          class="stat-card stat-card-clickable"
          v-for="card in statCards"
          :key="card.key"
          :style="{ '--theme': card.color }"
          @click="handleStatClick(card.key)"
        >
          <div class="stat-icon">
            <el-icon :size="34"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
          <el-icon class="stat-arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- 图表区 -->
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <div class="card-box">
            <div class="card-header">
              <h3 class="card-title">用户角色分布</h3>
            </div>
            <v-chart class="chart" :option="pieOption" autoresize />
          </div>
        </el-col>
        <el-col :xs="24" :md="12">
          <div class="card-box">
            <div class="card-header">
              <h3 class="card-title">业务数据概览</h3>
            </div>
            <v-chart class="chart" :option="barOption" autoresize />
          </div>
        </el-col>
      </el-row>

      <!-- 7天趋势图 -->
      <div class="card-box">
        <div class="card-header">
          <h3 class="card-title">近7天数据趋势</h3>
        </div>
        <v-chart class="chart" :option="trendOption" autoresize />
      </div>

      <!-- 待办提醒 -->
      <div class="card-box">
        <div class="card-header">
          <h3 class="card-title">待办事项</h3>
        </div>
        <div class="todo-grid">
          <div class="todo-item todo-warn" @click="router.push('/audit')">
            <div class="todo-num">{{ stats.pending_count || 0 }}</div>
            <div class="todo-text">待审核内容</div>
            <el-button type="primary" link>去处理 <el-icon><ArrowRight /></el-icon></el-button>
          </div>
          <div class="todo-item todo-info" @click="router.push('/admin')">
            <div class="todo-num">{{ stats.user_count || 0 }}</div>
            <div class="todo-text">注册用户</div>
            <el-button type="primary" link>用户管理 <el-icon><ArrowRight /></el-icon></el-button>
          </div>
          <div class="todo-item todo-success" @click="router.push('/market')">
            <div class="todo-num">{{ stats.resource_count || 0 }}</div>
            <div class="todo-text">资源总数</div>
            <el-button type="primary" link>查看集市 <el-icon><ArrowRight /></el-icon></el-button>
          </div>
        </div>
      </div>
    </template>

    <!-- ==================== 学生 / 教师仪表盘 ==================== -->
    <template v-else>
      <!-- 欢迎卡片 -->
      <div class="welcome-card">
        <div class="welcome-bg"></div>
        <div class="welcome-content">
          <h1>{{ greeting }}，{{ authStore.nickname }}</h1>
          <p>欢迎回到绵城AI学习集市，让 AI 助力你的个人成长之旅</p>
          <div class="welcome-tags">
            <el-tag effect="dark" round>{{ roleLabel }}</el-tag>
            <el-tag effect="dark" round type="success">{{ todayStr }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <h3 class="section-title">
        <el-icon><Star /></el-icon> 快捷入口
      </h3>
      <el-row :gutter="20" class="quick-row">
        <el-col :xs="12" :sm="6" v-for="entry in quickEntries" :key="entry.path">
          <div class="quick-card" @click="router.push(entry.path)">
            <div class="quick-icon" :style="{ background: entry.color }">
              <el-icon :size="30"><component :is="entry.icon" /></el-icon>
            </div>
            <div class="quick-title">{{ entry.title }}</div>
            <div class="quick-desc">{{ entry.desc }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 我的统计 -->
      <h3 class="section-title">
        <el-icon><DataAnalysis /></el-icon> 我的数据
      </h3>
      <el-row :gutter="20" class="mini-row">
        <el-col :xs="12" :sm="6" v-for="stat in personalStats" :key="stat.label">
          <div
            class="mini-stat-card mini-stat-clickable"
            @click="handleStatClick(stat.key)"
          >
            <div class="mini-stat-icon" :style="{ color: stat.color }">
              <el-icon :size="28"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="mini-stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
            <div class="mini-stat-label">{{ stat.label }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 我的任务包预览 -->
      <div class="card-box">
        <div class="card-header">
          <h3 class="card-title">我的任务包</h3>
          <el-button type="primary" link @click="router.push('/ai-task')">
            生成新任务 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div v-loading="pkgLoading">
          <template v-if="myPackages.length">
            <div
              class="pkg-preview-item"
              v-for="pkg in myPackages.slice(0, 4)"
              :key="pkg.id"
              @click="router.push(`/ai-task/${pkg.id}`)"
            >
              <div class="pkg-preview-left">
                <el-icon class="pkg-icon" :size="20"><Document /></el-icon>
                <div>
                  <div class="pkg-preview-title">{{ pkg.title }}</div>
                  <div class="pkg-preview-meta">
                    <el-tag size="small" effect="plain">{{ pkg.category || '未分类' }}</el-tag>
                  </div>
                </div>
              </div>
              <el-icon class="pkg-arrow"><ArrowRight /></el-icon>
            </div>
          </template>
          <el-empty v-else description="还没有任务包，快去生成一个吧" :image-size="80" />
        </div>
      </div>
    </template>

    <!-- ==================== 详情抽屉 ==================== -->
    <el-drawer
      v-model="detailDrawer.visible"
      :title="detailDrawer.title"
      size="45%"
      direction="rtl"
    >
      <div v-loading="detailDrawer.loading">
        <!-- 注册用户详情 -->
        <template v-if="detailDrawer.type === 'user'">
          <div class="detail-section">
            <h4 class="detail-section-title">角色分布</h4>
            <div class="detail-role-grid">
              <div
                class="detail-role-item"
                v-for="item in roleDistribution"
                :key="item.name"
              >
                <div class="detail-role-name">{{ item.name }}</div>
                <div class="detail-role-count">{{ item.value }} 人</div>
              </div>
            </div>
          </div>
          <div class="detail-section" v-if="authStore.isAdmin">
            <h4 class="detail-section-title">已认证教师</h4>
            <div class="detail-info-row">
              <span class="detail-info-label">通过实名认证</span>
              <span class="detail-info-value">{{ stats.certified_teachers || 0 }} 人</span>
            </div>
          </div>
          <div class="detail-footer">
            <el-button type="primary" @click="router.push('/admin'); detailDrawer.visible = false">
              前往用户管理
            </el-button>
          </div>
        </template>

        <!-- 资源总数详情 -->
        <template v-if="detailDrawer.type === 'resource'">
          <div class="detail-section" v-if="authStore.isAdmin && detailData.resourceStats">
            <h4 class="detail-section-title">按分类统计</h4>
            <div
              class="detail-category-item"
              v-for="(count, category) in detailData.resourceStats.by_category"
              :key="category"
            >
              <span>{{ category || '未分类' }}</span>
              <span>{{ count }} 个</span>
            </div>
            <div v-if="!detailData.resourceStats || Object.keys(detailData.resourceStats.by_category).length === 0"
                 class="detail-empty">
              暂无资源数据
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-info-row">
              <span class="detail-info-label">资源总数</span>
              <span class="detail-info-value">{{ stats.resource_count || 0 }} 个</span>
            </div>
          </div>
          <div class="detail-footer">
            <el-button type="primary" @click="router.push('/market'); detailDrawer.visible = false">
              前往资源集市
            </el-button>
          </div>
        </template>

        <!-- 任务包数详情 -->
        <template v-if="detailDrawer.type === 'task'">
          <div class="detail-section" v-if="authStore.isAdmin && detailData.taskStats">
            <h4 class="detail-section-title">按分类统计</h4>
            <div
              class="detail-category-item"
              v-for="(count, category) in detailData.taskStats.by_category"
              :key="category"
            >
              <span>{{ category || '未分类' }}</span>
              <span>{{ count }} 个</span>
            </div>
            <div v-if="!detailData.taskStats || Object.keys(detailData.taskStats.by_category).length === 0"
                 class="detail-empty">
              暂无任务包数据
            </div>
          </div>
          <div class="detail-section" v-if="authStore.isAdmin && detailData.taskStats">
            <h4 class="detail-section-title">来源分布</h4>
            <div class="detail-info-row">
              <span class="detail-info-label">AI 生成</span>
              <span class="detail-info-value">{{ detailData.taskStats.source.ai_generated }} 个</span>
            </div>
            <div class="detail-info-row">
              <span class="detail-info-label">用户发布</span>
              <span class="detail-info-value">{{ detailData.taskStats.source.user_published }} 个</span>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-info-row">
              <span class="detail-info-label">任务包总数</span>
              <span class="detail-info-value">{{ stats.task_count || 0 }} 个</span>
            </div>
          </div>
          <div class="detail-footer">
            <el-button type="primary" @click="router.push('/ai-task'); detailDrawer.visible = false">
              前往任务生成
            </el-button>
          </div>
        </template>

        <!-- 社区帖子详情 -->
        <template v-if="detailDrawer.type === 'post'">
          <div class="detail-section">
            <div class="detail-info-row">
              <span class="detail-info-label">帖子总数</span>
              <span class="detail-info-value">{{ stats.post_count || 0 }} 篇</span>
            </div>
          </div>
          <div class="detail-section" v-if="detailData.recentPosts && detailData.recentPosts.length">
            <h4 class="detail-section-title">最新帖子</h4>
            <div
              class="detail-post-item"
              v-for="post in detailData.recentPosts"
              :key="post.id"
              @click="router.push(`/achievement`); detailDrawer.visible = false"
            >
              <div class="detail-post-title">{{ post.title }}</div>
              <div class="detail-post-meta">
                <span>{{ post.author_name || '匿名' }}</span>
                <span>{{ post.created_at?.slice(0, 10) }}</span>
              </div>
            </div>
          </div>
          <div class="detail-footer">
            <el-button type="primary" @click="router.push('/achievement'); detailDrawer.visible = false">
              前往成果社区
            </el-button>
          </div>
        </template>

        <!-- 待审核详情 -->
        <template v-if="detailDrawer.type === 'pending'">
          <div class="detail-section">
            <h4 class="detail-section-title">待审核分类</h4>
            <div class="detail-info-row">
              <span class="detail-info-label">资源审核</span>
              <span class="detail-info-value">{{ stats.pending_breakdown?.resource || 0 }} 项</span>
            </div>
            <div class="detail-info-row">
              <span class="detail-info-label">成果帖子审核</span>
              <span class="detail-info-value">{{ stats.pending_breakdown?.achievement || 0 }} 项</span>
            </div>
            <div class="detail-info-row">
              <span class="detail-info-label">任务包审核</span>
              <span class="detail-info-value">{{ stats.pending_breakdown?.task_package || 0 }} 项</span>
            </div>
            <div class="detail-info-row total-row">
              <span class="detail-info-label">合计</span>
              <span class="detail-info-value">{{ stats.pending_count || 0 }} 项</span>
            </div>
          </div>
          <div class="detail-footer">
            <el-button type="primary" @click="router.push('/audit'); detailDrawer.visible = false">
              前往审核中心
            </el-button>
          </div>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { useAuthStore } from '@/stores/auth'
import { adminApi, aiTaskApi, statsApi, achievementApi } from '@/api'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const router = useRouter()
const authStore = useAuthStore()

// ---------------- 数据 ----------------
const stats = reactive({
  user_count: 0,
  role_distribution: {},
  resource_count: 0,
  task_count: 0,
  post_count: 0,
  pending_count: 0,
  certified_teachers: 0,
  pending_breakdown: { resource: 0, achievement: 0, task_package: 0 },
})

const myPackages = ref([])
const pkgLoading = ref(false)
const trendData = ref({ dates: [], users: [], resources: [], achievements: [], tasks: [] })

// 详情抽屉
const detailDrawer = reactive({
  visible: false,
  title: '',
  type: '',
  loading: false,
})

// 详情数据
const detailData = reactive({
  resourceStats: null,
  taskStats: null,
  recentPosts: [],
})

// ---------------- 计算属性 ----------------
const roleLabel = computed(() => {
  const map = { student: '学生', teacher: '教师', auditor: '审核员', admin: '管理员' }
  return map[authStore.role] || '用户'
})

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '凌晨好'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const todayStr = computed(() => {
  const d = new Date()
  const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${d.getMonth() + 1}月${d.getDate()}日 ${week[d.getDay()]}`
})

const statCards = computed(() => [
  { key: 'user', label: '注册用户', value: stats.user_count, icon: 'User', color: '#409eff' },
  { key: 'resource', label: '资源总数', value: stats.resource_count, icon: 'Files', color: '#67c23a' },
  { key: 'task', label: '任务包数', value: stats.task_count, icon: 'List', color: '#e6a23c' },
  { key: 'post', label: '社区帖子', value: stats.post_count, icon: 'ChatDotRound', color: '#f56c6c' },
  { key: 'pending', label: '待审核', value: stats.pending_count, icon: 'Bell', color: '#909399' },
])

const roleNameMap = {
  student: '学生',
  teacher: '教师',
  auditor: '审核员',
  admin: '管理员',
}

const roleDistribution = computed(() => {
  const raw = stats.role_distribution
  if (!raw) return []
  if (Array.isArray(raw)) {
    return raw.map((item) => ({
      name: roleNameMap[item.name] || item.name,
      value: Number(item.value) || 0,
    }))
  }
  // 对象形式 { student: 10, teacher: 5, ... }
  return Object.entries(raw).map(([key, value]) => ({
    name: roleNameMap[key] || key,
    value: Number(value) || 0,
  }))
})

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { bottom: 0, left: 'center' },
  color: ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399'],
  series: [
    {
      name: '角色分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2,
      },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 16, fontWeight: 'bold' },
      },
      data: roleDistribution.value.length
        ? roleDistribution.value
        : [{ name: '暂无数据', value: 1 }],
    },
  ],
}))

const barOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: ['资源', '任务包', '帖子', '待审核'],
    axisTick: { alignWithLabel: true },
  },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      type: 'bar',
      barWidth: '40%',
      data: [
        { value: stats.resource_count, itemStyle: { color: '#67c23a' } },
        { value: stats.task_count, itemStyle: { color: '#e6a23c' } },
        { value: stats.post_count, itemStyle: { color: '#f56c6c' } },
        { value: stats.pending_count, itemStyle: { color: '#909399' } },
      ],
    },
  ],
}))

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['注册用户', '资源发布', '成果帖子', '任务包'], bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
  xAxis: { type: 'category', data: trendData.value.dates || [], boundaryGap: false },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    { name: '注册用户', type: 'line', data: trendData.value.users || [], smooth: true, itemStyle: { color: '#409eff' } },
    { name: '资源发布', type: 'line', data: trendData.value.resources || [], smooth: true, itemStyle: { color: '#67c23a' } },
    { name: '成果帖子', type: 'line', data: trendData.value.achievements || [], smooth: true, itemStyle: { color: '#f56c6c' } },
    { name: '任务包', type: 'line', data: trendData.value.tasks || [], smooth: true, itemStyle: { color: '#e6a23c' } },
  ],
}))

const quickEntries = [
  {
    path: '/ai-task',
    title: 'AI任务生成',
    desc: '智能生成学习计划',
    icon: 'MagicStick',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  {
    path: '/market',
    title: '资源集市',
    desc: '发现优质学习资源',
    icon: 'Goods',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  },
  {
    path: '/study',
    title: '学习中心',
    desc: '打卡笔记进度管理',
    icon: 'Reading',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  },
  {
    path: '/achievement',
    title: '成果社区',
    desc: '分享交流学习成果',
    icon: 'Trophy',
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  },
]

const personalStats = computed(() => [
  { key: 'task', label: '我的任务包', value: myPackages.value.length, icon: 'List', color: '#409eff' },
  { key: 'resource', label: '社区资源', value: stats.resource_count, icon: 'Files', color: '#67c23a' },
  { key: 'post', label: '社区帖子', value: stats.post_count, icon: 'ChatDotRound', color: '#f56c6c' },
  { key: 'user', label: '社区成员', value: stats.user_count, icon: 'User', color: '#e6a23c' },
])

// ---------------- 详情抽屉处理 ----------------
const drawerTitleMap = {
  user: '注册用户详情',
  resource: '资源总数详情',
  task: '任务包详情',
  post: '社区帖子详情',
  pending: '待审核详情',
}

async function handleStatClick(key) {
  detailDrawer.type = key
  detailDrawer.title = drawerTitleMap[key] || '详情'
  detailDrawer.visible = true
  detailDrawer.loading = true

  // 重置详情数据
  detailData.resourceStats = null
  detailData.taskStats = null
  detailData.recentPosts = []

  try {
    if (key === 'resource' && authStore.isAdmin) {
      const res = await adminApi.resourceStats()
      if (res.code === 200 && res.data) {
        detailData.resourceStats = res.data
      }
    } else if (key === 'task' && authStore.isAdmin) {
      const res = await adminApi.taskStats()
      if (res.code === 200 && res.data) {
        detailData.taskStats = res.data
      }
    } else if (key === 'post') {
      const res = await achievementApi.posts({ page: 1, page_size: 5 })
      if (res.code === 200 && res.data) {
        // 兼容分页/非分页返回
        detailData.recentPosts = Array.isArray(res.data) ? res.data : (res.data.list || res.data.records || [])
      }
    }
  } catch (e) {
    // 静默处理
  } finally {
    detailDrawer.loading = false
  }
}

// ---------------- 数据加载 ----------------
async function loadAdminData() {
  try {
    const res = await adminApi.dashboard()
    if (res.code === 200 && res.data) {
      // 正确映射后端字段到前端字段
      stats.user_count = res.data.total_users ?? 0
      stats.resource_count = res.data.total_resources ?? 0
      stats.task_count = res.data.total_tasks ?? 0
      stats.post_count = res.data.total_achievements ?? 0
      stats.pending_count = res.data.pending_total ?? 0
      stats.role_distribution = res.data.role_counts || {}
      stats.certified_teachers = res.data.certified_teachers ?? 0
      stats.pending_breakdown = res.data.pending_breakdown || { resource: 0, achievement: 0, task_package: 0 }
    }
  } catch (e) {
    ElMessage.error('获取系统数据失败')
  }
}

async function loadMyPackages() {
  pkgLoading.value = true
  try {
    const res = await aiTaskApi.myPackages()
    if (res.code === 200) {
      myPackages.value = res.data || []
    }
  } catch (e) {
    // 静默处理
  } finally {
    pkgLoading.value = false
  }
}

// 学生/教师：通过公开统计接口获取概览数据
async function loadOverview() {
  try {
    const res = await statsApi.overview()
    if (res.code === 200 && res.data) {
      stats.user_count = res.data.user_count ?? 0
      stats.resource_count = res.data.resource_count ?? 0
      stats.task_count = res.data.task_count ?? 0
      stats.post_count = res.data.post_count ?? 0
      stats.role_distribution = res.data.role_distribution || {}
    }
  } catch (e) {
    // 静默处理
  }
}

async function loadTrends() {
  try {
    const res = await adminApi.trends()
    if (res.code === 200 && res.data) {
      trendData.value = res.data
    }
  } catch (e) { /* silent */ }
}

onMounted(async () => {
  if (authStore.isAdmin) {
    await loadAdminData()
    await loadTrends()
  } else {
    // 并行加载
    await Promise.all([loadOverview(), loadMyPackages()])
  }
  await nextTick()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

/* ---------- 管理员统计卡片 ---------- */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fff;
  border-radius: 10px;
  padding: 22px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border-left: 4px solid var(--theme);
  transition: transform 0.25s, box-shadow 0.25s;
}

.stat-card-clickable {
  cursor: pointer;
  position: relative;
}

.stat-card-clickable:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.stat-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #c0c4cc;
  transition: transform 0.25s;
}

.stat-card-clickable:hover .stat-arrow {
  transform: translateY(-50%) translateX(4px);
  color: var(--theme);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: var(--theme);
  flex-shrink: 0;
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

/* ---------- 通用卡片 ---------- */
.card-box {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.chart {
  height: 320px;
  width: 100%;
}

/* ---------- 待办网格 ---------- */
.todo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.todo-item {
  border-radius: 10px;
  padding: 20px;
  cursor: pointer;
  transition: transform 0.25s;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.todo-item:hover {
  transform: translateY(-3px);
}

.todo-warn {
  background: linear-gradient(135deg, #fff4e6 0%, #ffe4c4 100%);
}

.todo-info {
  background: linear-gradient(135deg, #e6f0ff 0%, #cce0ff 100%);
}

.todo-success {
  background: linear-gradient(135deg, #e6f9ec 0%, #c3f0d4 100%);
}

.todo-num {
  font-size: 30px;
  font-weight: 700;
  color: #303133;
}

.todo-text {
  font-size: 14px;
  color: #606266;
}

/* ---------- 欢迎卡片 ---------- */
.welcome-card {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 24px;
  color: #fff;
}

.welcome-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.welcome-bg::after {
  content: '';
  position: absolute;
  right: -40px;
  top: -40px;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
}

.welcome-bg::before {
  content: '';
  position: absolute;
  right: 80px;
  bottom: -60px;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.welcome-content {
  position: relative;
  z-index: 1;
  padding: 36px 32px;
}

.welcome-content h1 {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 10px;
}

.welcome-content p {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 16px;
}

.welcome-tags {
  display: flex;
  gap: 10px;
}

/* ---------- 区块标题 ---------- */
.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 17px;
  font-weight: 600;
  color: #303133;
  margin: 8px 0 16px;
}

/* ---------- 快捷入口 ---------- */
.quick-row {
  margin-bottom: 24px;
}

.quick-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px 20px;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.25s, box-shadow 0.25s;
  margin-bottom: 16px;
}

.quick-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
}

.quick-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin: 0 auto 14px;
}

.quick-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.quick-desc {
  font-size: 12px;
  color: #909399;
}

/* ---------- 我的统计 ---------- */
.mini-row {
  margin-bottom: 24px;
}

.mini-stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
}

.mini-stat-clickable {
  cursor: pointer;
  transition: transform 0.25s, box-shadow 0.25s;
}

.mini-stat-clickable:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.mini-stat-icon {
  margin-bottom: 8px;
}

.mini-stat-value {
  font-size: 26px;
  font-weight: 700;
  line-height: 1.2;
}

.mini-stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* ---------- 任务包预览 ---------- */
.pkg-preview-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.pkg-preview-item:hover {
  background: #f5f7fa;
}

.pkg-preview-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pkg-icon {
  color: #409eff;
}

.pkg-preview-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
}

.pkg-arrow {
  color: #c0c4cc;
}

/* ---------- 详情抽屉样式 ---------- */
.detail-section {
  margin-bottom: 24px;
}

.detail-section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.detail-role-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-role-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.detail-role-name {
  font-size: 14px;
  color: #606266;
  margin-bottom: 6px;
}

.detail-role-count {
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
}

.detail-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-info-row.total-row {
  border-bottom: none;
  border-top: 2px solid #ebeef5;
  margin-top: 8px;
  padding-top: 14px;
}

.detail-info-row.total-row .detail-info-value {
  font-size: 18px;
  font-weight: 700;
  color: #f56c6c;
}

.detail-info-label {
  font-size: 14px;
  color: #606266;
}

.detail-info-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.detail-category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-category-item:last-child {
  border-bottom: none;
}

.detail-post-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 8px;
}

.detail-post-item:hover {
  background: #f5f7fa;
}

.detail-post-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
}

.detail-post-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.detail-empty {
  text-align: center;
  color: #909399;
  padding: 20px;
  font-size: 14px;
}

.detail-footer {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
