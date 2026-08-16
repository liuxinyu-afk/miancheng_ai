<template>
  <div class="study-plan-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">
          <el-icon class="title-icon"><Notebook /></el-icon>
          学习计划
        </h2>
        <p class="page-subtitle">制定专属学习计划，坚持每日打卡，稳步达成目标</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">创建计划</el-button>
    </div>

    <!-- 统计概览 -->
    <el-row :gutter="16" class="stat-row" v-if="plans.length > 0">
      <el-col :xs="8" :sm="8">
        <el-card shadow="never" class="stat-card stat-active">
          <div class="stat-value">{{ statusCount('active') }}</div>
          <div class="stat-label">进行中</div>
        </el-card>
      </el-col>
      <el-col :xs="8" :sm="8">
        <el-card shadow="never" class="stat-card stat-completed">
          <div class="stat-value">{{ statusCount('completed') }}</div>
          <div class="stat-label">已完成</div>
        </el-card>
      </el-col>
      <el-col :xs="8" :sm="8">
        <el-card shadow="never" class="stat-card stat-abandoned">
          <div class="stat-value">{{ statusCount('abandoned') }}</div>
          <div class="stat-label">已放弃</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 计划列表 -->
    <div v-loading="loading" class="plan-list">
      <el-empty
        v-if="!loading && plans.length === 0"
        description="还没有学习计划，快去创建一个吧"
        :image-size="120"
      >
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">立即创建</el-button>
      </el-empty>

      <el-row :gutter="16">
        <el-col
          v-for="plan in plans"
          :key="plan.id"
          :xs="24"
          :sm="12"
          :lg="8"
        >
          <el-card shadow="hover" class="plan-card">
            <!-- 卡片头部 -->
            <div class="plan-top">
              <span class="plan-title">{{ plan.title }}</span>
              <el-tag
                :type="statusTagType(plan.status)"
                size="small"
                effect="light"
              >
                {{ statusLabel(plan.status) }}
              </el-tag>
            </div>

            <!-- 学科标签 -->
            <div class="plan-subject">
              <el-tag type="info" size="small" effect="plain">
                {{ plan.subject || '未分类' }}
              </el-tag>
            </div>

            <!-- 进度条 -->
            <div class="plan-progress">
              <div class="progress-info">
                <span>学习进度</span>
                <span class="progress-percent">{{ plan.progress || 0 }}%</span>
              </div>
              <el-progress
                :percentage="plan.progress || 0"
                :color="progressColor(plan.status)"
                :stroke-width="10"
                :show-text="false"
              />
            </div>

            <!-- 元信息 -->
            <div class="plan-meta">
              <div class="meta-row">
                <el-icon><Calendar /></el-icon>
                <span class="meta-label">起止日期</span>
                <span class="meta-value">{{ formatDate(plan.start_date) }} ~ {{ formatDate(plan.end_date) }}</span>
              </div>
              <div class="meta-row">
                <el-icon><AlarmClock /></el-icon>
                <span class="meta-label">每日目标</span>
                <span class="meta-value">{{ plan.daily_goal_minutes || 0 }} 分钟</span>
              </div>
              <div class="meta-row">
                <el-icon><Clock /></el-icon>
                <span class="meta-label">创建时间</span>
                <span class="meta-value">{{ formatDateTime(plan.created_at) }}</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="plan-actions">
              <el-button
                size="small"
                type="primary"
                plain
                :icon="Refresh"
                :disabled="plan.status !== 'active'"
                @click="openProgressDialog(plan)"
              >
                更新进度
              </el-button>
              <el-button
                size="small"
                type="success"
                plain
                :icon="CircleCheck"
                :disabled="plan.status === 'completed'"
                @click="handleComplete(plan)"
              >
                标记完成
              </el-button>
              <el-button
                size="small"
                type="danger"
                plain
                :icon="Delete"
                @click="handleDelete(plan)"
              >
                删除
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 创建计划对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建学习计划"
      width="580px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="计划标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="请输入计划标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="学科" prop="subject">
          <el-input
            v-model="form.subject"
            placeholder="例如：数学、英语、物理"
            maxlength="50"
          />
        </el-form-item>
        <el-form-item label="每日目标（分钟）" prop="daily_goal_minutes">
          <el-input-number
            v-model="form.daily_goal_minutes"
            :min="1"
            :max="1440"
            :step="10"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="选择开始日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker
                v-model="form.end_date"
                type="date"
                placeholder="选择结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitCreate">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 更新进度对话框 -->
    <el-dialog
      v-model="progressDialogVisible"
      title="更新进度"
      width="460px"
      :close-on-click-modal="false"
    >
      <div class="progress-dialog-body">
        <div class="dialog-plan-name">{{ currentPlan?.title }}</div>
        <el-slider
          v-model="progressValue"
          :min="0"
          :max="100"
          :step="1"
          show-input
          :input-size="small"
        />
        <div class="dialog-progress-preview">
          <el-progress
            :percentage="progressValue"
            :stroke-width="14"
            :color="progressColor(currentPlan?.status)"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="progressDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="progressSubmitting" @click="submitProgress">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Notebook, Plus, Calendar, AlarmClock, Clock, Refresh, CircleCheck, Delete,
} from '@element-plus/icons-vue'
import { studyPlanApi } from '@/api'

// ============ 计划列表 ============
const loading = ref(false)
const plans = ref([])

async function fetchPlans() {
  loading.value = true
  try {
    const res = await studyPlanApi.list()
    // 兼容数组直接返回与 { data: [...] } 包装两种结构
    const list = Array.isArray(res) ? res : (res.data || [])
    plans.value = list
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

function statusCount(status) {
  return plans.value.filter((p) => p.status === status).length
}

// ============ 状态映射 ============
function statusLabel(status) {
  const map = {
    active: '进行中',
    completed: '已完成',
    abandoned: '已放弃',
  }
  return map[status] || status || '未知'
}

function statusTagType(status) {
  const map = {
    active: 'success',   // 绿色
    completed: 'primary', // 蓝色
    abandoned: 'info',    // 灰色
  }
  return map[status] || 'info'
}

function progressColor(status) {
  const map = {
    active: '#67c23a',
    completed: '#409eff',
    abandoned: '#909399',
  }
  return map[status] || '#409eff'
}

// ============ 创建计划 ============
const createDialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref()
const form = reactive({
  title: '',
  subject: '',
  daily_goal_minutes: 30,
  start_date: '',
  end_date: '',
})

const rules = {
  title: [{ required: true, message: '请输入计划标题', trigger: 'blur' }],
  subject: [{ required: true, message: '请输入学科', trigger: 'blur' }],
  daily_goal_minutes: [
    { required: true, message: '请输入每日目标分钟数', trigger: 'blur' },
  ],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' },
    {
      validator: (rule, value, callback) => {
        if (value && form.start_date && new Date(value) < new Date(form.start_date)) {
          callback(new Error('结束日期不能早于开始日期'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

function openCreateDialog() {
  form.title = ''
  form.subject = ''
  form.daily_goal_minutes = 30
  form.start_date = ''
  form.end_date = ''
  createDialogVisible.value = true
}

async function submitCreate() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await studyPlanApi.create({
        title: form.title,
        subject: form.subject,
        daily_goal_minutes: form.daily_goal_minutes,
        start_date: form.start_date,
        end_date: form.end_date,
      })
      ElMessage.success('计划创建成功')
      createDialogVisible.value = false
      fetchPlans()
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      submitting.value = false
    }
  })
}

// ============ 更新进度 ============
const progressDialogVisible = ref(false)
const progressSubmitting = ref(false)
const progressValue = ref(0)
const currentPlan = ref(null)

function openProgressDialog(plan) {
  currentPlan.value = plan
  progressValue.value = plan.progress || 0
  progressDialogVisible.value = true
}

async function submitProgress() {
  if (!currentPlan.value) return
  progressSubmitting.value = true
  try {
    const payload = { progress: progressValue.value }
    // 进度达到 100 时自动置为已完成
    if (progressValue.value >= 100) {
      payload.status = 'completed'
    }
    await studyPlanApi.update(currentPlan.value.id, payload)
    ElMessage.success('进度已更新')
    progressDialogVisible.value = false
    fetchPlans()
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    progressSubmitting.value = false
  }
}

// ============ 标记完成 ============
async function handleComplete(plan) {
  try {
    await ElMessageBox.confirm(
      `确定将计划「${plan.title}」标记为已完成吗？`,
      '提示',
      { type: 'warning' }
    )
    await studyPlanApi.update(plan.id, { status: 'completed', progress: 100 })
    ElMessage.success('已标记为完成')
    fetchPlans()
  } catch (e) {
    // 取消或错误
  }
}

// ============ 删除计划 ============
async function handleDelete(plan) {
  try {
    await ElMessageBox.confirm(
      `确定删除计划「${plan.title}」吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning' }
    )
    await studyPlanApi.delete(plan.id)
    ElMessage.success('删除成功')
    fetchPlans()
  } catch (e) {
    // 取消或错误
  }
}

// ============ 工具函数 ============
function pad(n) {
  return String(n).padStart(2, '0')
}

function formatDate(t) {
  if (!t) return '未设置'
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function formatDateTime(t) {
  if (!t) return '-'
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

onMounted(() => {
  fetchPlans()
})
</script>

<style scoped>
.study-plan-page {
  padding: 20px;
}

/* ---------- 顶部操作栏 ---------- */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
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
  color: #409eff;
  font-size: 24px;
}

.page-subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

/* ---------- 统计概览 ---------- */
.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  text-align: center;
  padding: 8px 0;
  border: none;
}

.stat-card.stat-active {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
}

.stat-card.stat-completed {
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
}

.stat-card.stat-abandoned {
  background: linear-gradient(135deg, #f4f4f5 0%, #e9e9eb 100%);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #606266;
  margin-top: 4px;
}

/* ---------- 计划列表 ---------- */
.plan-list {
  min-height: 200px;
}

.plan-card {
  margin-bottom: 16px;
  border-radius: 14px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.plan-card:hover {
  transform: translateY(-3px);
}

.plan-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.plan-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.plan-subject {
  margin-bottom: 14px;
}

.plan-progress {
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.progress-percent {
  font-weight: 600;
  color: #409eff;
}

/* ---------- 元信息 ---------- */
.plan-meta {
  padding: 12px;
  background: #f7f8fa;
  border-radius: 8px;
  margin-bottom: 14px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  padding: 3px 0;
}

.meta-row .el-icon {
  color: #909399;
  flex-shrink: 0;
}

.meta-label {
  color: #909399;
  flex-shrink: 0;
}

.meta-value {
  color: #303133;
  font-weight: 500;
}

/* ---------- 操作按钮 ---------- */
.plan-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.plan-actions .el-button {
  flex: 1;
  min-width: 0;
}

/* ---------- 更新进度对话框 ---------- */
.progress-dialog-body {
  padding: 8px 4px;
}

.dialog-plan-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  text-align: center;
}

.dialog-progress-preview {
  margin-top: 20px;
}
</style>
