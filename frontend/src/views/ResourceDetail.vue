<template>
  <div class="page-container">
    <!-- 顶部操作栏 -->
    <div class="detail-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回列表</el-button>
      <el-button
        v-if="authStore.isLoggedIn"
        :type="isFavorited ? 'warning' : 'default'"
        :icon="isFavorited ? StarFilled : Star"
        :loading="favLoading"
        @click="toggleFavorite"
      >
        {{ isFavorited ? '已收藏' : '收藏' }}
      </el-button>
      <el-button
        v-if="authStore.isLoggedIn"
        type="danger"
        :icon="Warning"
        @click="openReportDialog"
      >
        举报
      </el-button>
    </div>

    <!-- 详情内容 -->
    <div v-loading="loading" class="card-box">
      <el-empty
        v-if="!loading && !detail"
        description="资源不存在或已删除"
      />

      <template v-if="detail">
        <h1 class="detail-title">{{ detail.title }}</h1>

        <div class="detail-meta">
          <el-tag size="small" :type="categoryTagType(detail.category)" effect="light">
            {{ detail.category || '未分类' }}
          </el-tag>
          <el-tag size="small" :type="roleTagType(detail.publisher_role)" effect="plain">
            {{ roleLabel(detail.publisher_role) }}
          </el-tag>
          <el-tag
            v-if="detail.is_teacher_certified"
            size="small"
            type="warning"
            effect="dark"
          >
            <el-icon class="cert-icon"><Avatar /></el-icon>教师认证
          </el-tag>

          <span v-if="publisherName" class="meta-item">
            <el-icon><User /></el-icon>
            {{ publisherName }}
          </span>
          <span class="meta-item">
            <el-icon><View /></el-icon>
            {{ detail.view_count || 0 }} 浏览
          </span>
          <span class="meta-item">
            <el-icon><Clock /></el-icon>
            {{ formatTime(detail.created_at) }}
          </span>
        </div>

        <el-divider />

        <div class="detail-content" v-html="renderedContent"></div>

        <!-- 评分区域 -->
        <el-divider />
        <div class="rating-section">
          <div class="rating-summary">
            <div class="rating-score-box">
              <span class="rating-avg">{{ avgScore.toFixed(1) }}</span>
              <el-rate
                :model-value="avgScore"
                disabled
                show-score
                :score-template="`${ratingTotal} 条评分`"
              />
            </div>
            <el-button
              v-if="authStore.isLoggedIn"
              type="primary"
              :icon="Edit"
              @click="openRatingDialog"
            >
              我要评分
            </el-button>
          </div>

          <!-- 评分列表 -->
          <div class="rating-list" v-loading="ratingLoading">
            <el-empty
              v-if="!ratingLoading && ratingsList.length === 0"
              description="暂无评分"
              :image-size="80"
            />
            <div
              v-for="(item, idx) in ratingsList"
              :key="idx"
              class="rating-item"
            >
              <el-avatar :size="36" :src="item.avatar">
                {{ (item.nickname || item.username || '匿').charAt(0) }}
              </el-avatar>
              <div class="rating-item-body">
                <div class="rating-item-head">
                  <span class="rating-item-name">
                    {{ item.nickname || item.username || '匿名用户' }}
                  </span>
                  <el-rate
                    :model-value="item.score"
                    disabled
                    size="small"
                  />
                </div>
                <div v-if="item.comment" class="rating-item-comment">
                  {{ item.comment }}
                </div>
                <div class="rating-item-time">{{ formatTime(item.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- 评分对话框 -->
    <el-dialog
      v-model="ratingDialogVisible"
      title="我要评分"
      width="460px"
      :close-on-click-modal="false"
    >
      <el-form label-position="top">
        <el-form-item label="评分">
          <el-rate
            v-model="ratingForm.score"
            :max="5"
            show-text
            :texts="['很差', '较差', '一般', '较好', '很好']"
          />
        </el-form-item>
        <el-form-item label="评论">
          <el-input
            v-model="ratingForm.comment"
            type="textarea"
            :rows="4"
            maxlength="300"
            show-word-limit
            placeholder="说说你对这个资源的评价吧"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ratingDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="ratingSubmitting" @click="submitRating">
          提交评分
        </el-button>
      </template>
    </el-dialog>

    <!-- 举报对话框 -->
    <el-dialog
      v-model="reportDialogVisible"
      title="举报资源"
      width="460px"
      :close-on-click-modal="false"
    >
      <el-form label-position="top">
        <el-form-item label="举报原因" required>
          <el-select
            v-model="reportForm.reason"
            placeholder="请选择举报原因"
            style="width: 100%"
          >
            <el-option label="垃圾广告" value="垃圾广告" />
            <el-option label="内容违规" value="内容违规" />
            <el-option label="侵权抄袭" value="侵权抄袭" />
            <el-option label="信息虚假" value="信息虚假" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="详细描述">
          <el-input
            v-model="reportForm.description"
            type="textarea"
            :rows="4"
            maxlength="500"
            show-word-limit
            placeholder="请补充举报的详细情况"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="reportSubmitting" @click="submitReport">
          提交举报
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, Star, StarFilled, View, Clock, Avatar, User, Warning, Edit,
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useAuthStore } from '@/stores/auth'
import { marketApi } from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const resourceId = computed(() => route.params.id)

const loading = ref(false)
const detail = ref(null)

const favLoading = ref(false)
const isFavorited = ref(false)

// ============ 评分相关 ============
const ratingLoading = ref(false)
const ratingsList = ref([])
const avgScore = ref(0)
const ratingTotal = ref(0)

const ratingDialogVisible = ref(false)
const ratingSubmitting = ref(false)
const ratingForm = ref({
  score: 5,
  comment: '',
})

// ============ 举报相关 ============
const reportDialogVisible = ref(false)
const reportSubmitting = ref(false)
const reportForm = ref({
  reason: '',
  description: '',
})

const publisherName = computed(() => {
  if (!detail.value) return ''
  return (
    detail.value.publisher_name ||
    detail.value.publisher_nickname ||
    detail.value.author_name ||
    ''
  )
})

// 简单处理换行：先转义 HTML 特殊字符，再把 \n 转为 <br>
const renderedContent = computed(() => {
  if (!detail.value || !detail.value.content) {
    return '<p class="empty-text">暂无内容</p>'
  }
  const escaped = String(detail.value.content)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
  return escaped.replace(/\n/g, '<br>')
})

async function fetchDetail() {
  loading.value = true
  try {
    const res = await marketApi.detail(resourceId.value)
    // 兼容 { code, data } 包装与直接返回资源对象两种情况
    detail.value = res && 'code' in res ? res.data : res
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

async function fetchFavoriteStatus() {
  if (!authStore.isLoggedIn) return
  try {
    const res = await marketApi.myFavorites()
    const favs = res.data || []
    isFavorited.value = favs.some(
      (item) => String(item.id) === String(resourceId.value)
    )
  } catch (e) {
    // 忽略，不影响详情展示
  }
}

async function toggleFavorite() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录后再收藏')
    router.push('/login')
    return
  }
  favLoading.value = true
  try {
    if (isFavorited.value) {
      await marketApi.unfavorite(resourceId.value)
      isFavorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await marketApi.favorite(resourceId.value)
      isFavorited.value = true
      ElMessage.success('收藏成功')
    }
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    favLoading.value = false
  }
}

// ============ 评分功能 ============
async function fetchRatings() {
  ratingLoading.value = true
  try {
    const res = await marketApi.ratings(resourceId.value)
    // 兼容 { code, data } 包装与直接返回对象两种情况
    const data = res && 'code' in res ? res.data : res
    ratingsList.value = (data && data.ratings) || []
    avgScore.value = (data && typeof data.avg_score === 'number') ? data.avg_score : 0
    ratingTotal.value = (data && typeof data.total === 'number') ? data.total : ratingsList.value.length
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    ratingLoading.value = false
  }
}

function openRatingDialog() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录后再评分')
    router.push('/login')
    return
  }
  ratingForm.value = { score: 5, comment: '' }
  ratingDialogVisible.value = true
}

async function submitRating() {
  if (!ratingForm.value.score || ratingForm.value.score < 1) {
    ElMessage.warning('请选择评分')
    return
  }
  ratingSubmitting.value = true
  try {
    await marketApi.rate(resourceId.value, {
      score: ratingForm.value.score,
      comment: ratingForm.value.comment,
    })
    ElMessage.success('评分成功')
    ratingDialogVisible.value = false
    fetchRatings()
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    ratingSubmitting.value = false
  }
}

// ============ 举报功能 ============
function openReportDialog() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录后再举报')
    router.push('/login')
    return
  }
  reportForm.value = { reason: '', description: '' }
  reportDialogVisible.value = true
}

async function submitReport() {
  if (!reportForm.value.reason) {
    ElMessage.warning('请选择举报原因')
    return
  }
  reportSubmitting.value = true
  try {
    await marketApi.report(resourceId.value, {
      reason: reportForm.value.reason,
      description: reportForm.value.description,
    })
    ElMessage.success('举报已提交，我们会尽快处理')
    reportDialogVisible.value = false
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    reportSubmitting.value = false
  }
}

function goBack() {
  router.push('/market')
}

// ============ 工具函数 ============
function formatTime(t) {
  if (!t) return ''
  const d = dayjs(t)
  return d.isValid() ? d.format('YYYY-MM-DD HH:mm') : t
}

function roleLabel(role) {
  const map = { student: '学生', teacher: '教师', admin: '管理员', auditor: '审核员' }
  return map[role] || (role ? role : '匿名用户')
}

function roleTagType(role) {
  const map = { teacher: 'warning', admin: 'danger', auditor: 'info', student: '' }
  return map[role] ?? 'info'
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

onMounted(() => {
  fetchDetail()
  fetchFavoriteStatus()
  fetchRatings()
})
</script>

<style scoped>
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  line-height: 1.4;
}

.detail-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  color: #909399;
  font-size: 13px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.cert-icon {
  margin-right: 2px;
  vertical-align: -2px;
}

.detail-content {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
  word-break: break-word;
  min-height: 120px;
}

.detail-content :deep(.empty-text) {
  color: #c0c4cc;
  text-align: center;
}

/* 评分区域 */
.rating-section {
  margin-top: 8px;
}

.rating-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.rating-score-box {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rating-avg {
  font-size: 28px;
  font-weight: 600;
  color: #ff9900;
  line-height: 1;
}

.rating-list {
  margin-top: 8px;
}

.rating-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.rating-item:last-child {
  border-bottom: none;
}

.rating-item-body {
  flex: 1;
  min-width: 0;
}

.rating-item-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.rating-item-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.rating-item-comment {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 4px 0;
  word-break: break-word;
}

.rating-item-time {
  font-size: 12px;
  color: #c0c4cc;
}
</style>
