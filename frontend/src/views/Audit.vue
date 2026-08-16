<template>
  <div class="audit-page">
    <div class="page-header">
      <h2>审核中心</h2>
      <el-tag type="warning" effect="plain">审核员：{{ authStore.nickname }}</el-tag>
    </div>

    <el-card shadow="never">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 待审核 -->
        <el-tab-pane label="待审核" name="pending">
          <div class="filter-bar">
            <el-radio-group v-model="filterType" @change="handlePendingFilter">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="resource">资源</el-radio-button>
              <el-radio-button value="achievement">成果</el-radio-button>
              <el-radio-button value="task_package">任务包</el-radio-button>
            </el-radio-group>
            <el-button :icon="Refresh" @click="fetchPending">刷新</el-button>
          </div>

          <el-table v-loading="pendingLoading" :data="pendingList" stripe>
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="typeTagType(row.type)" size="small">{{ typeLabel(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="内容预览" min-width="280">
              <template #default="{ row }">
                <div class="preview-text">{{ row.preview || row.title || row.content || row.summary || '—' }}</div>
              </template>
            </el-table-column>
            <el-table-column label="提交人" width="120">
              <template #default="{ row }">
                {{ row.username || row.nickname || ('用户' + row.user_id) }}
              </template>
            </el-table-column>
            <el-table-column label="提交时间" width="170">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" :icon="View" @click="openDetail(row)">查看详情</el-button>
                <el-button type="success" size="small" @click="openReview(row, 'approve')">通过</el-button>
                <el-button type="danger" size="small" @click="openReview(row, 'reject')">驳回</el-button>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无待审核内容" />
            </template>
          </el-table>

          <div v-if="pendingTotal > 0" class="pagination-wrap">
            <el-pagination
              v-model:current-page="pendingPage"
              v-model:page-size="pendingPageSize"
              :total="pendingTotal"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              background
              @current-change="fetchPending"
              @size-change="handlePendingSizeChange"
            />
          </div>
        </el-tab-pane>

        <!-- 审核历史 -->
        <el-tab-pane label="审核历史" name="history">
          <div class="filter-bar">
            <el-radio-group v-model="historyType" @change="handleHistoryFilter">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="resource">资源</el-radio-button>
              <el-radio-button value="achievement">成果</el-radio-button>
              <el-radio-button value="task_package">任务包</el-radio-button>
            </el-radio-group>
            <el-button :icon="Refresh" @click="fetchHistory">刷新</el-button>
          </div>

          <el-table v-loading="historyLoading" :data="historyList" stripe>
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="typeTagType(row.type)" size="small">{{ typeLabel(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="内容预览" min-width="240">
              <template #default="{ row }">
                <div class="preview-text">{{ row.preview || row.title || row.content || row.summary || '—' }}</div>
              </template>
            </el-table-column>
            <el-table-column label="提交人" width="120">
              <template #default="{ row }">
                {{ row.username || row.nickname || ('用户' + row.user_id) }}
              </template>
            </el-table-column>
            <el-table-column label="审核结果" width="120">
              <template #default="{ row }">
                <el-tag :type="resultTagType(row.action || row.result)" size="small">
                  {{ resultLabel(row.action || row.result) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="审核理由" min-width="160">
              <template #default="{ row }">
                <span class="preview-text">{{ row.reason || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="审核时间" width="170">
              <template #default="{ row }">{{ formatTime(row.reviewed_at || row.created_at) }}</template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无审核历史" />
            </template>
          </el-table>

          <div v-if="historyTotal > 0" class="pagination-wrap">
            <el-pagination
              v-model:current-page="historyPage"
              v-model:page-size="historyPageSize"
              :total="historyTotal"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              background
              @current-change="fetchHistory"
              @size-change="handleHistorySizeChange"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="审核详情" width="640px">
      <div v-loading="detailLoading" class="detail-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="类型">
            <el-tag :type="typeTagType(currentDetail.type)" size="small">{{ typeLabel(currentDetail.type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标题">{{ currentDetail.title || '—' }}</el-descriptions-item>
          <el-descriptions-item label="提交人">
            {{ currentDetail.username || currentDetail.nickname || ('用户' + currentDetail.user_id) }}
            <el-tag v-if="currentDetail.role" :type="currentDetail.role === 'teacher' ? 'warning' : 'success'" size="small" effect="plain" style="margin-left: 8px">
              {{ { student: '学生', teacher: '教师', auditor: '审核员', admin: '管理员' }[currentDetail.role] || currentDetail.role }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ formatTime(currentDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="描述/内容">
            <div class="detail-text">{{ currentDetail.description || currentDetail.content || currentDetail.summary || '—' }}</div>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentDetail.images" label="图片">
            <div class="detail-images">
              <el-image
                v-for="(img, idx) in parseImages(currentDetail.images)"
                :key="idx"
                :src="img"
                :preview-src-list="parseImages(currentDetail.images)"
                fit="cover"
                class="detail-image"
                preview-teleported
              />
            </div>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentDetail.extra" label="附加信息">
            <pre class="detail-extra">{{ formatJson(currentDetail.extra) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="success" @click="openReview(currentRow, 'approve')">通过</el-button>
        <el-button type="danger" @click="openReview(currentRow, 'reject')">驳回</el-button>
      </template>
    </el-dialog>

    <!-- 审核操作对话框 -->
    <el-dialog v-model="reviewDialogVisible" :title="reviewAction === 'approve' ? '通过审核' : '驳回审核'" width="440px" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item v-if="reviewAction === 'reject'" label="驳回理由" required>
          <el-input v-model="reviewForm.reason" type="textarea" :rows="4" placeholder="请填写驳回理由" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item v-else label="审核备注">
          <el-input v-model="reviewForm.reason" type="textarea" :rows="3" placeholder="可选填写备注" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button
          :type="reviewAction === 'approve' ? 'success' : 'danger'"
          :loading="reviewSubmitting"
          @click="submitReview"
        >
          确认{{ reviewAction === 'approve' ? '通过' : '驳回' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { View, Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { auditApi } from '@/api'

const authStore = useAuthStore()

const activeTab = ref('pending')

function handleTabChange() {
  if (activeTab.value === 'pending') fetchPending()
  else fetchHistory()
}

// ============ 待审核 ============
const pendingLoading = ref(false)
const pendingList = ref([])
const pendingTotal = ref(0)
const pendingPage = ref(1)
const pendingPageSize = ref(10)
const filterType = ref('')

async function fetchPending() {
  pendingLoading.value = true
  try {
    const params = { page: pendingPage.value, page_size: pendingPageSize.value }
    if (filterType.value) params.content_type = filterType.value
    const res = await auditApi.pending(params)
    pendingList.value = res.data || []
    pendingTotal.value = res.total || 0
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    pendingLoading.value = false
  }
}

function handlePendingFilter() {
  pendingPage.value = 1
  fetchPending()
}

function handlePendingSizeChange() {
  pendingPage.value = 1
  fetchPending()
}

// ============ 审核历史 ============
const historyLoading = ref(false)
const historyList = ref([])
const historyTotal = ref(0)
const historyPage = ref(1)
const historyPageSize = ref(10)
const historyType = ref('')

async function fetchHistory() {
  historyLoading.value = true
  try {
    const params = { page: historyPage.value, page_size: historyPageSize.value }
    if (historyType.value) params.content_type = historyType.value
    const res = await auditApi.history(params)
    historyList.value = res.data || []
    historyTotal.value = res.total || 0
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    historyLoading.value = false
  }
}

function handleHistoryFilter() {
  historyPage.value = 1
  fetchHistory()
}

function handleHistorySizeChange() {
  historyPage.value = 1
  fetchHistory()
}

// ============ 详情 ============
const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const currentRow = ref(null)
const currentDetail = ref({})

async function openDetail(row) {
  currentRow.value = row
  currentDetail.value = { ...row }
  detailDialogVisible.value = true
  detailLoading.value = true
  try {
    const res = await auditApi.pendingDetail(row.type, row.id)
    currentDetail.value = { ...row, ...(res.data || res) }
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    detailLoading.value = false
  }
}

// ============ 审核操作 ============
const reviewDialogVisible = ref(false)
const reviewSubmitting = ref(false)
const reviewAction = ref('approve')
const reviewForm = reactive({ reason: '' })

function openReview(row, action) {
  if (!row) return
  currentRow.value = row
  reviewAction.value = action
  reviewForm.reason = ''
  reviewDialogVisible.value = true
}

async function submitReview() {
  if (reviewAction.value === 'reject' && !reviewForm.reason.trim()) {
    ElMessage.warning('请填写驳回理由')
    return
  }
  reviewSubmitting.value = true
  try {
    await auditApi.review({
      type: currentRow.value.type,
      id: currentRow.value.id,
      action: reviewAction.value,
      reason: reviewForm.reason,
      reject_reason: reviewForm.reason,
    })
    ElMessage.success(reviewAction.value === 'approve' ? '已通过审核' : '已驳回')
    reviewDialogVisible.value = false
    detailDialogVisible.value = false
    fetchPending()
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    reviewSubmitting.value = false
  }
}

// ============ 工具函数 ============
function typeLabel(type) {
  const map = { resource: '资源', achievement: '成果', task_package: '任务包' }
  return map[type] || type || '未知'
}

function typeTagType(type) {
  const map = { resource: '', achievement: 'success', task_package: 'warning' }
  return map[type] || 'info'
}

function resultLabel(action) {
  const map = { approve: '通过', approved: '通过', reject: '驳回', rejected: '驳回' }
  return map[action] || action || '—'
}

function resultTagType(action) {
  return action === 'approve' || action === 'approved' ? 'success' : 'danger'
}

function parseImages(images) {
  if (!images) return []
  if (Array.isArray(images)) return images.filter(Boolean)
  return String(images).split(',').map((s) => s.trim()).filter(Boolean)
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

function formatJson(obj) {
  if (!obj) return ''
  if (typeof obj === 'string') return obj
  try {
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return String(obj)
  }
}

onMounted(() => {
  fetchPending()
})
</script>

<style scoped>
.audit-page {
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

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.preview-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.detail-content {
  min-height: 100px;
}

.detail-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  color: #303133;
}

.detail-images {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  cursor: pointer;
}

.detail-extra {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow: auto;
  margin: 0;
}
</style>
