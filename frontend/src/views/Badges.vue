<template>
  <div class="badges-page">
    <!-- 顶部信息栏 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">
          <el-icon class="title-icon"><Trophy /></el-icon>
          我的勋章
        </h2>
        <p class="page-subtitle" v-if="authStore.nickname">
          {{ authStore.nickname }} 的勋章墙
        </p>
      </div>
      <div class="header-right">
        <el-tag type="warning" effect="dark" size="large" round>
          已获得 {{ earnedCount }} / 总共 {{ totalCount }} 枚勋章
        </el-tag>
      </div>
    </div>

    <!-- 总进度条 -->
    <el-card shadow="never" class="progress-card" v-if="totalCount > 0">
      <div class="overall-progress">
        <span class="progress-label">勋章收集进度</span>
        <el-progress
          :percentage="overallPercent"
          :stroke-width="14"
          :color="progressColors"
          :format="(p) => `${p}%`"
        />
      </div>
    </el-card>

    <!-- 勋章内容 -->
    <div v-loading="loading" class="badges-content">
      <el-empty
        v-if="!loading && badges.length === 0"
        description="暂无勋章数据"
        :image-size="120"
      />

      <template v-else>
        <div
          v-for="cat in categoryList"
          :key="cat.key"
          class="category-section"
        >
          <template v-if="groupedBadges[cat.key] && groupedBadges[cat.key].length">
            <div class="category-header">
              <span class="category-icon">{{ cat.icon }}</span>
              <span class="category-title">{{ cat.label }}</span>
              <el-tag size="small" type="info" effect="plain">
                {{ earnedInCategory(cat.key) }} / {{ groupedBadges[cat.key].length }}
              </el-tag>
            </div>

            <el-row :gutter="16">
              <el-col
                v-for="badge in groupedBadges[cat.key]"
                :key="badge.id"
                :xs="12"
                :sm="8"
                :md="6"
                :lg="4"
              >
                <el-card
                  shadow="hover"
                  class="badge-card"
                  :class="{ earned: badge.earned, unearned: !badge.earned }"
                >
                  <div class="badge-icon-wrap">
                    <span class="badge-icon">{{ badge.icon || '🏅' }}</span>
                    <span v-if="badge.earned" class="badge-check">
                      <el-icon><Select /></el-icon>
                    </span>
                  </div>
                  <div class="badge-name">{{ badge.name }}</div>
                  <div class="badge-desc">{{ badge.description }}</div>

                  <div class="badge-footer">
                    <el-tag
                      v-if="badge.earned"
                      type="success"
                      size="small"
                      effect="dark"
                    >
                      已获得
                    </el-tag>
                    <el-tag
                      v-else
                      type="info"
                      size="small"
                      effect="plain"
                    >
                      未获得
                    </el-tag>
                  </div>

                  <div
                    v-if="!badge.earned && badge.condition_type"
                    class="badge-condition"
                  >
                    达成条件：{{ conditionText(badge) }}
                  </div>
                  <div
                    v-else-if="badge.earned"
                    class="badge-condition badge-condition-earned"
                  >
                    {{ badge.description }}
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Trophy, Select } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { badgeApi } from '@/api'

const authStore = useAuthStore()

// ============ 分类配置 ============
const categoryList = [
  { key: 'study', label: '学习类', icon: '📚' },
  { key: 'checkin', label: '打卡类', icon: '📅' },
  { key: 'social', label: '社交类', icon: '💬' },
  { key: 'contribution', label: '贡献类', icon: '🤝' },
  { key: 'special', label: '特殊类', icon: '🏆' },
  { key: 'milestone', label: '里程碑', icon: '🎯' },
]

// ============ 数据状态 ============
const loading = ref(false)
const badges = ref([])
const newlyAwarded = ref([])

// 已获得 / 总数
const earnedCount = computed(() => badges.value.filter((b) => b.earned).length)
const totalCount = computed(() => badges.value.length)
const overallPercent = computed(() =>
  totalCount.value === 0
    ? 0
    : Math.round((earnedCount.value / totalCount.value) * 100)
)

const progressColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#409eff', percentage: 60 },
  { color: '#67c23a', percentage: 80 },
  { color: '#67c23a', percentage: 100 },
]

// 按分类分组
const groupedBadges = computed(() => {
  const groups = {}
  for (const cat of categoryList) groups[cat.key] = []
  for (const b of badges.value) {
    const key = b.category
    if (!groups[key]) groups[key] = []
    groups[key].push(b)
  }
  return groups
})

function earnedInCategory(catKey) {
  const list = groupedBadges.value[catKey] || []
  return list.filter((b) => b.earned).length
}

// 达成条件文案
function conditionText(badge) {
  const type = badge.condition_type || ''
  const val = badge.condition_value
  if (val === undefined || val === null || val === '') return ''

  const typeLabels = {
    study_minutes: `累计学习满${Math.floor(val / 60)}小时`,
    checkin_count: `累计打卡满${val}次`,
    friend_count: `添加满${val}个好友`,
    like_received: `收到满${val}个点赞`,
    resource_count: `发布满${val}个资源`,
    post_count: `发布满${val}个成果帖子`,
    room_count: `创建满${val}个自习房间`,
    register_days: `注册满${val}天`,
    note_count: `创建满${val}篇学习笔记`,
    task_count: `创建满${val}个学习任务包`,
    ai_task_count: `生成满${val}个AI任务`,
    message_sent: `发送满${val}条私信`,
    room_message_count: `在自习室发送满${val}条消息`,
    room_join_count: `加入满${val}个自习房间`,
    comment_count: `发表满${val}条评论`,
    public_note_count: `公开满${val}篇学习笔记`,
  }

  return typeLabels[type] || `${type} ${val}`
}

// ============ 获取勋章 ============
async function fetchBadges() {
  loading.value = true
  try {
    const res = await badgeApi.my()
    // 兼容 { badges, newly_awarded } 与 { data: { badges, newly_awarded } } 两种返回结构
    const payload = res && res.data ? res.data : res
    badges.value = payload.badges || []
    newlyAwarded.value = payload.newly_awarded || []
    notifyNewlyAwarded(newlyAwarded.value)
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

// 新获得的勋章通知
function notifyNewlyAwarded(list) {
  if (!list || !list.length) return
  list.forEach((badge, idx) => {
    setTimeout(() => {
      ElMessage({
        message: `恭喜获得新勋章：${badge.icon || ''} ${badge.name}`,
        type: 'success',
        duration: 3500,
        showClose: true,
      })
    }, idx * 600)
  })
}

onMounted(() => {
  fetchBadges()
})
</script>

<style scoped>
.badges-page {
  padding: 20px;
}

/* ---------- 顶部信息栏 ---------- */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #303133;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  color: #e6a23c;
  font-size: 24px;
}

.page-subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.header-right {
  display: flex;
  align-items: center;
}

/* ---------- 总进度卡 ---------- */
.progress-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.overall-progress {
  display: flex;
  align-items: center;
  gap: 16px;
}

.progress-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  white-space: nowrap;
}

.overall-progress .el-progress {
  flex: 1;
}

/* ---------- 分类区块 ---------- */
.badges-content {
  min-height: 200px;
}

.category-section {
  margin-bottom: 28px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.category-icon {
  font-size: 20px;
  line-height: 1;
}

.category-title {
  font-size: 17px;
  font-weight: 600;
  color: #303133;
}

/* ---------- 勋章卡片 ---------- */
.badge-card {
  margin-bottom: 16px;
  border-radius: 14px;
  text-align: center;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  overflow: hidden;
}

.badge-card:hover {
  transform: translateY(-4px);
}

.badge-card.earned {
  border-color: #f0d27a;
  background: linear-gradient(160deg, #fffbf0 0%, #fff7e6 100%);
}

.badge-card.unearned {
  filter: grayscale(1);
  opacity: 0.55;
  background: #fafafa;
}

.badge-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 84px;
  margin-bottom: 8px;
}

.badge-icon {
  font-size: 56px;
  line-height: 1;
}

.badge-card.earned .badge-icon-wrap::before {
  content: '';
  position: absolute;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(230, 162, 60, 0.25) 0%, rgba(230, 162, 60, 0) 70%);
}

.badge-check {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #67c23a;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.badge-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badge-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  min-height: 36px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 10px;
}

.badge-footer {
  margin-bottom: 6px;
}

.badge-condition {
  font-size: 12px;
  color: #c0c4cc;
  line-height: 1.4;
  padding-top: 6px;
  border-top: 1px dashed #ebeef5;
}

.badge-condition-earned {
  color: #e6a23c;
  border-top-color: #f5dab1;
}
</style>
