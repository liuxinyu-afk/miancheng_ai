<template>
  <div class="task-detail-page">
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" text @click="goBack">返回</el-button>
        <h2>任务包详情</h2>
      </div>
      <el-button type="danger" :icon="Delete" @click="handleDelete">删除任务包</el-button>
    </div>

    <div v-loading="loading">
      <!-- 任务包信息 -->
      <el-card shadow="never" class="info-card">
        <template #header>
          <div class="card-header">
            <span>{{ pkg.title || '加载中...' }}</span>
            <el-tag :type="auditTagType" effect="light">{{ auditLabel }}</el-tag>
          </div>
        </template>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="分类">
            <el-tag size="small">{{ pkg.category || '未分类' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="每日时长">{{ pkg.daily_minutes || 0 }} 分钟</el-descriptions-item>
          <el-descriptions-item label="难度">
            <el-rate :model-value="pkg.difficulty || 0" disabled />
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="3">{{ formatTime(pkg.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="3">
            <div class="desc-text">{{ pkg.description || '暂无描述' }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 学习进度 -->
      <el-card shadow="never" class="progress-card">
        <template #header>
          <div class="card-header">
            <span>学习进度</span>
            <el-button size="small" :icon="Refresh" @click="fetchProgress">刷新</el-button>
          </div>
        </template>

        <div v-loading="progressLoading" class="progress-content">
          <el-empty v-if="!progressLoading && !hasProgress" description="暂无学习记录" :image-size="60" />
          <div v-else class="progress-grid">
            <div class="progress-item">
              <div class="progress-value">{{ progress.completed || 0 }}</div>
              <div class="progress-label">已完成任务</div>
            </div>
            <div class="progress-item">
              <div class="progress-value">{{ progress.total || (pkg.tasks?.length || 0) }}</div>
              <div class="progress-label">总任务数</div>
            </div>
            <div class="progress-item">
              <div class="progress-value">{{ progress.total_minutes || 0 }}</div>
              <div class="progress-label">累计时长(分)</div>
            </div>
            <div class="progress-bar-wrap">
              <div class="progress-bar-label">
                总体进度：{{ progressPercent }}%
              </div>
              <el-progress :percentage="progressPercent" :stroke-width="20" :text-inside="true" status="success" />
            </div>
          </div>
        </div>
      </el-card>

      <!-- 子任务列表 -->
      <el-card shadow="never" class="tasks-card">
        <template #header>
          <div class="card-header">
            <span>子任务列表</span>
            <el-tag type="info" size="small">共 {{ pkg.tasks?.length || 0 }} 个任务</el-tag>
          </div>
        </template>

        <el-empty v-if="!loading && (!pkg.tasks || pkg.tasks.length === 0)" description="暂无子任务" />

        <div class="task-list">
          <div
            v-for="(task, idx) in pkg.tasks"
            :key="task.id"
            class="task-item"
          >
            <div class="task-index">{{ task.sort || idx + 1 }}</div>
            <div class="task-main">
              <div class="task-title">
                {{ task.name }}
                <el-tag v-if="isTaskDone(task)" type="success" size="small" effect="dark">已完成</el-tag>
              </div>
              <div class="task-desc">{{ task.description || '暂无描述' }}</div>
              <div class="task-meta">
                <el-tag type="info" size="small" effect="plain">
                  预计 {{ task.estimated_minutes || 0 }} 分钟
                </el-tag>
              </div>
            </div>
            <div class="task-action">
              <el-button
                v-if="!isTaskDone(task)"
                type="primary"
                size="small"
                :icon="Check"
                :loading="checkinTaskId === task.id"
                @click="handleCheckin(task)"
              >
                打卡
              </el-button>
              <el-tag v-else type="success"><el-icon><CircleCheck /></el-icon> 已打卡</el-tag>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 打卡对话框 -->
    <el-dialog v-model="checkinDialogVisible" title="任务打卡" width="440px" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="任务">
          <span class="checkin-task-name">{{ checkinTask?.name }}</span>
        </el-form-item>
        <el-form-item label="实际学习时长（分钟）">
          <el-input-number v-model="checkinForm.actual_minutes" :min="1" :max="600" :step="5" />
        </el-form-item>
        <el-form-item label="学习笔记（选填）">
          <el-input v-model="checkinForm.note" type="textarea" :rows="3" placeholder="记录本次学习心得" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="checkinDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="checkinSubmitting" @click="submitCheckin">确认打卡</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Delete, Refresh, Check, CircleCheck } from '@element-plus/icons-vue'
import { aiTaskApi, studyApi } from '@/api'

const route = useRoute()
const router = useRouter()

const packageId = computed(() => route.params.id)

const loading = ref(false)
const pkg = ref({})

// ============ 任务包详情 ============
async function fetchDetail() {
  loading.value = true
  try {
    const res = await aiTaskApi.packageDetail(packageId.value)
    pkg.value = res.data || res || {}
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

// ============ 学习进度 ============
const progressLoading = ref(false)
const progress = ref({})
const hasProgress = computed(() => Object.keys(progress.value).length > 0)

const progressPercent = computed(() => {
  const total = progress.value.total || pkg.value.tasks?.length || 0
  const completed = progress.value.completed || 0
  if (total <= 0) return 0
  return Math.min(100, Math.round((completed / total) * 100))
})

async function fetchProgress() {
  progressLoading.value = true
  try {
    const res = await studyApi.progress(packageId.value)
    progress.value = res.data || res || {}
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    progressLoading.value = false
  }
}

// 已完成任务集合（用于标记）
const doneTaskIds = ref(new Set())

function isTaskDone(task) {
  return doneTaskIds.value.has(task.id)
}

function syncDoneTasks() {
  const ids = new Set()
  // 优先从进度接口返回的已完成任务列表
  const doneList = progress.value.completed_tasks || progress.value.done_tasks || []
  if (Array.isArray(doneList)) {
    doneList.forEach((t) => {
      const id = typeof t === 'object' ? t.id : t
      if (id) ids.add(id)
    })
  }
  doneTaskIds.value = ids
}

// ============ 打卡 ============
const checkinDialogVisible = ref(false)
const checkinSubmitting = ref(false)
const checkinTaskId = ref(null)
const checkinTask = ref(null)
const checkinForm = reactive({ actual_minutes: 30, note: '' })

function handleCheckin(task) {
  checkinTask.value = task
  checkinTaskId.value = task.id
  checkinForm.actual_minutes = task.estimated_minutes || 30
  checkinForm.note = ''
  checkinDialogVisible.value = true
}

async function submitCheckin() {
  checkinSubmitting.value = true
  try {
    await studyApi.checkin({
      package_id: Number(packageId.value),
      task_id: checkinTask.value.id,
      actual_minutes: checkinForm.actual_minutes,
      note: checkinForm.note,
    })
    ElMessage.success('打卡成功')
    checkinDialogVisible.value = false
    doneTaskIds.value = new Set([...doneTaskIds.value, checkinTask.value.id])
    fetchProgress()
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    checkinSubmitting.value = false
    checkinTaskId.value = null
  }
}

// ============ 删除任务包 ============
async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定删除该任务包吗？删除后无法恢复。', '危险操作', {
      type: 'error',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
    })
    await aiTaskApi.deletePackage(packageId.value)
    ElMessage.success('任务包已删除')
    router.push('/ai-task')
  } catch (e) {
    // 取消或错误
  }
}

// ============ 工具函数 ============
const auditLabel = computed(() => {
  const map = { approved: '已通过', pending: '审核中', rejected: '已驳回' }
  return map[pkg.value.audit_status] || pkg.value.audit_status || '未知'
})

const auditTagType = computed(() => {
  const map = { approved: 'success', pending: 'warning', rejected: 'danger' }
  return map[pkg.value.audit_status] || 'info'
})

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function pad(n) {
  return String(n).padStart(2, '0')
}

function goBack() {
  router.back()
}

onMounted(async () => {
  await fetchDetail()
  await fetchProgress()
  syncDoneTasks()
})
</script>

<style scoped>
.task-detail-page {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.info-card,
.progress-card,
.tasks-card {
  margin-bottom: 16px;
}

.desc-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
  color: #303133;
}

.progress-content {
  min-height: 100px;
}

.progress-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr) 2fr;
  gap: 16px;
  align-items: center;
}

.progress-item {
  text-align: center;
  padding: 16px 8px;
  background: #f5f7fa;
  border-radius: 8px;
}

.progress-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
}

.progress-label {
  font-size: 13px;
  color: #909399;
  margin-top: 6px;
}

.progress-bar-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: box-shadow 0.2s;
}

.task-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.task-index {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ecf5ff;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.task-main {
  flex: 1;
}

.task-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-desc {
  font-size: 13px;
  color: #909399;
  margin: 6px 0;
  line-height: 1.5;
}

.task-meta {
  display: flex;
  gap: 8px;
}

.task-action {
  flex-shrink: 0;
}

.checkin-task-name {
  font-weight: 600;
  color: #303133;
}

@media (max-width: 768px) {
  .progress-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .progress-bar-wrap {
    grid-column: 1 / -1;
  }
}
</style>
