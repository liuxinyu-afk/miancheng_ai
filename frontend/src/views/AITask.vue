<template>
  <div class="page-container">
    <h2 class="page-title">AI 任务生成</h2>

    <!-- ==================== 学习模板快捷填充 ==================== -->
    <div class="card-box template-card">
      <div class="template-header">
        <el-icon :size="18"><Files /></el-icon>
        <span class="template-title">学习模板一键填充</span>
      </div>
      <div class="template-list">
        <el-button
          v-for="tpl in templates"
          :key="tpl.name"
          @click="applyTemplate(tpl)"
          plain
          size="small"
          round
        >
          {{ tpl.name }}
        </el-button>
      </div>
    </div>

    <!-- ==================== 生成表单 ==================== -->
    <div class="card-box form-card">
      <div class="form-header">
        <div class="form-header-icon">
          <el-icon :size="24"><MagicStick /></el-icon>
        </div>
        <div>
          <h3 class="form-title">智能学习计划生成器</h3>
          <p class="form-subtitle">AI自动拆分阶段任务、配套练习与验收标准，生成可直接打卡执行的学习计划</p>
        </div>
      </div>

      <!-- 表单顶部提示 -->
      <div class="form-tip">
        <span class="required-mark">*</span> 带 * 为必填项
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="gen-form"
      >
        <!-- ====== 分组1：基础目标信息 ====== -->
        <div class="form-group">
          <h4 class="group-title">🎯 基础目标信息</h4>
          <el-divider class="group-divider" />

          <el-row :gutter="20">
            <el-col :xs="24" :md="16">
              <el-form-item prop="goal">
                <template #label>📌 学习目标 <span class="required-mark">*</span></template>
                <el-input
                  v-model="form.goal"
                  type="textarea"
                  :rows="3"
                  placeholder="例如：2个月内吃透Python基础，能独立完成数据分析小项目"
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item prop="level">
                <template #label>📊 基础水平 <span class="required-mark">*</span></template>
                <el-select v-model="form.level" placeholder="请选择" style="width: 100%">
                  <el-option
                    v-for="opt in levelOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  >
                    <span style="float: left">{{ opt.label }}</span>
                    <span class="opt-desc">{{ opt.desc }}</span>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :xs="24" :md="8">
              <el-form-item>
                <template #label>📁 学习领域</template>
                <el-select v-model="form.category" placeholder="选择领域（可选）" style="width: 100%" clearable>
                  <el-option v-for="cat in categoryOptions" :key="cat" :label="cat" :value="cat" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item>
                <template #label>
                  <span class="label-with-tooltip">
                    ⚙️ 计划密度
                    <el-tooltip content="轻量化：任务少而精，适合慢节奏；高密度：任务多且紧凑，适合冲刺" placement="top">
                      <el-icon class="tooltip-icon"><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <el-select v-model="form.density" placeholder="请选择" style="width: 100%">
                  <el-option
                    v-for="opt in densityOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  >
                    <span style="float: left">{{ opt.label }}</span>
                    <span class="opt-desc">{{ opt.desc }}</span>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- ====== 分组2：时间规划 ====== -->
        <div class="form-group">
          <h4 class="group-title">⏱ 时间规划</h4>
          <el-divider class="group-divider" />

          <el-row :gutter="20">
            <el-col :xs="24" :md="8">
              <el-form-item>
                <template #label>
                  <span class="label-with-tooltip">
                    📖 学习风格
                    <el-tooltip content="理论优先：侧重概念、课件阅读&#10;实操优先：侧重练习、项目实战&#10;混合模式：理论+实操搭配" placement="top" raw-content>
                      <el-icon class="tooltip-icon"><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <el-select v-model="form.learningStyle" placeholder="请选择" style="width: 100%">
                  <el-option
                    v-for="opt in styleOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  >
                    <span style="float: left">{{ opt.label }}</span>
                    <span class="opt-desc">{{ opt.desc }}</span>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item>
                <template #label>🗓️ 目标周期 <span class="range-hint">1~180天</span></template>
                <el-input-number v-model="form.deadlineDays" :min="1" :max="180" :step="1" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item>
                <template #label>⏲️ 每日学习时长</template>
                <div class="slider-wrap">
                  <el-slider
                    v-model="form.dailyHours"
                    :min="1"
                    :max="12"
                    :marks="sliderMarks"
                    show-stops
                  />
                  <span class="slider-value">{{ form.dailyHours }}h/天</span>
                </div>
                <div class="preset-buttons">
                  <el-button
                    v-for="h in presetHours"
                    :key="h"
                    size="small"
                    :type="form.dailyHours === h ? 'primary' : 'default'"
                    @click="form.dailyHours = h"
                  >
                    {{ h }}h
                  </el-button>
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item>
            <template #label>✏️ 特别关注 / 额外要求</template>
            <el-input
              v-model="form.focusPoints"
              type="textarea"
              :rows="2"
              placeholder="例如：配套课后习题、期末考点梳理、推荐免费网课资源"
              maxlength="300"
              show-word-limit
            />
          </el-form-item>
        </div>

        <!-- 预期提示 -->
        <div class="generate-tip">
          <el-icon><InfoFilled /></el-icon>
          生成后可直接编辑任务、开启打卡跟踪
        </div>

        <div class="form-actions">
          <el-button
            type="primary"
            size="large"
            :loading="generating"
            :icon="MagicStick"
            @click="handleGenerate"
            :disabled="!formValid"
          >
            {{ generating ? 'AI 正在生成中...' : '生成学习计划' }}
          </el-button>
          <el-button size="large" :icon="DocumentCopy" @click="saveDraft">保存草稿</el-button>
          <el-button size="large" @click="resetForm">重置</el-button>
        </div>
      </el-form>
    </div>

    <!-- ==================== 生成结果 ==================== -->
    <div v-if="generating" class="card-box loading-box">
      <el-icon class="loading-icon" :size="40"><Loading /></el-icon>
      <p class="loading-text">AI 正在为你生成学习任务，请稍候...</p>
      <p class="loading-subtext">通常需要 10~30 秒，请勿离开页面</p>
    </div>

    <div v-if="!generating && generatedTasks.length" class="card-box">
      <div class="card-header">
        <h3 class="card-title">
          生成结果
          <el-tag size="small" round>共 {{ generatedTasks.length }} 个子任务</el-tag>
        </h3>
        <div class="result-actions">
          <el-button type="success" :icon="Check" :loading="saving" @click="openSaveDialog">
            保存为任务包
          </el-button>
          <el-button :icon="RefreshLeft" @click="handleGenerate">重新生成</el-button>
        </div>
      </div>

      <!-- 计划概览 -->
      <div v-if="planOverview" class="plan-overview">
        <div class="overview-header">
          <el-icon :size="20" color="#409eff"><Document /></el-icon>
          <span class="overview-title">计划概览</span>
        </div>
        <p class="overview-summary">{{ planOverview.summary }}</p>
        <div class="overview-stats">
          <div class="stat-item">
            <span class="stat-value">{{ planOverview.total_hours || 0 }}</span>
            <span class="stat-label">预计总时长(小时)</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ planOverview.estimated_days || 0 }}</span>
            <span class="stat-label">预计天数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ tasksByPhase.length }}</span>
            <span class="stat-label">学习阶段</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ generatedTasks.length }}</span>
            <span class="stat-label">子任务数</span>
          </div>
        </div>
        <div v-if="planOverview.phases && planOverview.phases.length" class="phase-tags">
          <el-tag
            v-for="(phase, idx) in planOverview.phases"
            :key="idx"
            :type="phaseTagType(idx)"
            effect="plain"
            size="small"
          >
            {{ phase }}
          </el-tag>
        </div>
      </div>

      <p class="result-tip">
        <el-icon><InfoFilled /></el-icon>
        你可以直接编辑下方任务的名称、描述和预计时长，调整满意后再保存
      </p>

      <!-- 按阶段分组的任务列表 -->
      <div class="phase-groups">
        <div
          v-for="group in tasksByPhase"
          :key="group.phase"
          class="phase-group"
        >
          <div class="phase-header">
            <span class="phase-name">{{ group.phase }}</span>
            <el-tag size="small" type="info" round>{{ group.tasks.length }} 个任务</el-tag>
          </div>
          <div class="task-list">
            <div
              class="task-item"
              v-for="task in group.tasks"
              :key="task"
            >
              <div class="task-index">{{ generatedTasks.indexOf(task) + 1 }}</div>
              <div class="task-body">
                <el-input
                  v-model="task.name"
                  class="task-name-input"
                  size="default"
                >
                  <template #prepend>任务名称</template>
                </el-input>
                <el-input
                  v-model="task.description"
                  type="textarea"
                  :rows="2"
                  class="task-desc-input"
                  placeholder="任务描述"
                />
                <!-- 学习目标 -->
                <div v-if="task.objectives && task.objectives.length" class="task-objectives">
                  <span class="objectives-label">学习目标：</span>
                  <el-tag
                    v-for="(obj, oi) in task.objectives"
                    :key="oi"
                    size="small"
                    type="success"
                    effect="plain"
                    class="objective-tag"
                  >{{ obj }}</el-tag>
                </div>
                <!-- 推荐资源 -->
                <div v-if="task.resources && task.resources.length" class="task-resources">
                  <span class="resources-label">推荐资源：</span>
                  <el-tag
                    v-for="(res, ri) in task.resources"
                    :key="ri"
                    size="small"
                    type="warning"
                    effect="plain"
                    class="resource-tag"
                  >{{ res }}</el-tag>
                </div>
                <div class="task-meta">
                  <span class="meta-label">预计时长</span>
                  <el-input-number
                    v-model="task.estimated_hours"
                    :min="0.5"
                    :max="100"
                    :step="0.5"
                    size="small"
                    controls-position="right"
                  />
                  <span class="meta-unit">小时</span>
                </div>
              </div>
              <div class="task-ops">
                <el-button
                  type="danger"
                  :icon="Delete"
                  circle
                  size="small"
                  @click="removeTask(generatedTasks.indexOf(task))"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="add-task-bar">
        <el-button :icon="Plus" plain @click="addTask">添加子任务</el-button>
      </div>
    </div>

    <!-- ==================== 我的任务包 ==================== -->
    <div class="card-box">
      <div class="card-header">
        <h3 class="card-title">
          <el-icon><Folder /></el-icon> 我的任务包
        </h3>
        <el-tag v-if="myPackages.length" size="small" round type="info">
          共 {{ myPackages.length }} 个
        </el-tag>
      </div>

      <div v-loading="pkgLoading">
        <template v-if="myPackages.length">
          <el-row :gutter="16">
            <el-col
              :xs="24"
              :sm="12"
              :md="8"
              v-for="pkg in myPackages"
              :key="pkg.id"
            >
              <div class="pkg-card" @click="goPackageDetail(pkg.id)">
                <div class="pkg-card-top">
                  <div class="pkg-card-icon">
                    <el-icon :size="22"><Document /></el-icon>
                  </div>
                  <el-tag size="small" effect="plain" type="success">
                    {{ pkg.category || '未分类' }}
                  </el-tag>
                </div>
                <h4 class="pkg-card-title">{{ pkg.title }}</h4>
                <div class="pkg-card-footer">
                  <span class="pkg-card-time">
                    <el-icon><Clock /></el-icon>
                    {{ formatDate(pkg.created_at || pkg.createdAt) }}
                  </span>
                  <el-button type="primary" link>
                    查看 <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </div>
              </div>
            </el-col>
          </el-row>
        </template>
        <el-empty v-else description="暂无任务包，快去生成第一个吧" :image-size="90" />
      </div>
    </div>

    <!-- ==================== 保存对话框 ==================== -->
    <el-dialog
      v-model="saveDialogVisible"
      title="保存任务包"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="saveFormRef"
        :model="saveForm"
        :rules="saveRules"
        label-position="top"
      >
        <el-form-item label="任务包标题" prop="title">
          <el-input v-model="saveForm.title" placeholder="请输入任务包标题" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select
            v-model="saveForm.category"
            placeholder="请选择分类"
            style="width: 100%"
            allow-create
            filterable
          >
            <el-option
              v-for="cat in categoryOptions"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-form-item>
        <div class="save-summary">
          <el-icon><InfoFilled /></el-icon>
          本次将保存 <b>{{ generatedTasks.length }}</b> 个子任务
        </div>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">确认保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  MagicStick,
  Check,
  RefreshLeft,
  Delete,
  Plus,
  InfoFilled,
  Loading,
  Folder,
  Document,
  Clock,
  ArrowRight,
  Files,
  DocumentCopy,
  QuestionFilled,
} from '@element-plus/icons-vue'
import { aiTaskApi } from '@/api'

const router = useRouter()

// ---------------- 生成表单 ----------------
const formRef = ref()
const generating = ref(false)

const form = reactive({
  goal: '',
  dailyHours: 4,
  level: 'beginner',
  category: '',
  deadlineDays: 30,
  learningStyle: 'mixed',
  focusPoints: '',
  density: 'normal',
})

const rules = {
  goal: [
    { required: true, message: '请输入学习目标', trigger: 'blur' },
    { min: 4, max: 200, message: '学习目标 4-200 个字符', trigger: 'blur' },
  ],
  level: [{ required: true, message: '请选择基础水平', trigger: 'change' }],
}

// 表单校验状态（控制生成按钮是否可点击）
const formValid = ref(false)

function checkFormValid() {
  formValid.value = !!(form.goal && form.goal.trim().length >= 4 && form.level)
}

watch(form, () => {
  checkFormValid()
}, { deep: true, immediate: true })

// 基础水平选项（4档）
const levelOptions = [
  { value: 'beginner', label: '入门', desc: '零基础或刚接触' },
  { value: 'basic', label: '基础', desc: '了解基本概念' },
  { value: 'intermediate', label: '进阶', desc: '有一定实践经验' },
  { value: 'expert', label: '熟练', desc: '能独立应用和解决问题' },
]

const categoryOptions = [
  '编程开发', '设计创意', '语言学习', '考试认证', '职业发展', '考研考公', '兴趣爱好', '其他',
]

// 学习风格选项（3种 + 悬浮说明）
const styleOptions = [
  { value: 'theory', label: '理论优先', desc: '侧重概念、课件阅读' },
  { value: 'practice', label: '实操优先', desc: '侧重练习、项目实战' },
  { value: 'mixed', label: '混合模式', desc: '理论+实操搭配' },
]

// 计划密度选项
const densityOptions = [
  { value: 'light', label: '轻量化', desc: '任务少而精，适合慢节奏' },
  { value: 'normal', label: '标准', desc: '均衡的任务量' },
  { value: 'intensive', label: '高密度', desc: '任务紧凑，适合冲刺' },
]

// 每日时长快捷预设
const presetHours = [1, 2, 4, 6]

const sliderMarks = {
  1: '1h',
  4: '4h',
  8: '8h',
  12: '12h',
}

// 学习模板
const templates = [
  {
    name: '考研备考',
    goal: '系统备考研究生入学考试，覆盖政治、英语、数学/专业课三大科目',
    level: 'intermediate',
    category: '考研考公',
    deadlineDays: 120,
    dailyHours: 6,
    learningStyle: 'theory',
    focusPoints: '历年真题解析、高频考点梳理、冲刺模拟卷',
    density: 'intensive',
  },
  {
    name: '编程入门',
    goal: '从零开始学习Python编程，能独立完成数据分析小项目',
    level: 'beginner',
    category: '编程开发',
    deadlineDays: 60,
    dailyHours: 2,
    learningStyle: 'mixed',
    focusPoints: '配套课后习题、推荐免费网课资源、实战项目练习',
    density: 'normal',
  },
  {
    name: '考证学习',
    goal: '备考计算机等级考试/职业资格证，掌握核心知识点并通过考试',
    level: 'basic',
    category: '考试认证',
    deadlineDays: 45,
    dailyHours: 3,
    learningStyle: 'theory',
    focusPoints: '考试大纲梳理、模拟题练习、重点笔记整理',
    density: 'normal',
  },
  {
    name: '技能提升',
    goal: '深入学习前端开发技术栈，掌握Vue3全家桶并完成实战项目',
    level: 'intermediate',
    category: '编程开发',
    deadlineDays: 90,
    dailyHours: 4,
    learningStyle: 'practice',
    focusPoints: '项目实战、面试常考点、最新技术趋势',
    density: 'normal',
  },
]

function applyTemplate(tpl) {
  form.goal = tpl.goal
  form.level = tpl.level
  form.category = tpl.category
  form.deadlineDays = tpl.deadlineDays
  form.dailyHours = tpl.dailyHours
  form.learningStyle = tpl.learningStyle
  form.focusPoints = tpl.focusPoints
  form.density = tpl.density
  ElMessage.success(`已填充「${tpl.name}」模板，可根据需要调整`)
  checkFormValid()
}

// ---------------- 草稿保存/恢复 ----------------
const DRAFT_KEY = 'aitask_draft'

function saveDraft() {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify({
      goal: form.goal,
      level: form.level,
      category: form.category,
      deadlineDays: form.deadlineDays,
      dailyHours: form.dailyHours,
      learningStyle: form.learningStyle,
      focusPoints: form.focusPoints,
      density: form.density,
      savedAt: Date.now(),
    }))
    ElMessage.success('草稿已保存，下次进入页面将自动恢复')
  } catch (e) {
    ElMessage.error('草稿保存失败')
  }
}

function loadDraft() {
  try {
    const raw = localStorage.getItem(DRAFT_KEY)
    if (!raw) return
    const draft = JSON.parse(raw)
    if (draft.goal) form.goal = draft.goal
    if (draft.level) form.level = draft.level
    if (draft.category !== undefined) form.category = draft.category
    if (draft.deadlineDays) form.deadlineDays = draft.deadlineDays
    if (draft.dailyHours) form.dailyHours = draft.dailyHours
    if (draft.learningStyle) form.learningStyle = draft.learningStyle
    if (draft.focusPoints !== undefined) form.focusPoints = draft.focusPoints
    if (draft.density) form.density = draft.density
  } catch (e) {
    // 静默处理
  }
}

// ---------------- 生成结果 ----------------
const generatedTasks = ref([])
const planOverview = ref(null)

// 按阶段分组任务
const tasksByPhase = computed(() => {
  const groups = {}
  const phaseOrder = []
  for (const task of generatedTasks.value) {
    const phase = task.phase || '学习任务'
    if (!groups[phase]) {
      groups[phase] = []
      phaseOrder.push(phase)
    }
    groups[phase].push(task)
  }
  return phaseOrder.map((phase) => ({ phase, tasks: groups[phase] }))
})

async function handleGenerate() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    generating.value = true
    generatedTasks.value = []
    planOverview.value = null
    try {
      const res = await aiTaskApi.generate({
        goal: form.goal,
        daily_hours: form.dailyHours,
        level: form.level,
        category: form.category || undefined,
        deadline_days: form.deadlineDays || undefined,
        learning_style: form.learningStyle || undefined,
        focus_points: form.focusPoints || undefined,
        density: form.density || undefined,
      })
      if (res.code === 200) {
        const data = res.data || {}
        // 兼容新旧格式
        const tasks = data.tasks || (Array.isArray(data) ? data : [])
        planOverview.value = data.overview || null
        generatedTasks.value = tasks.map((t, i) => ({
          name: t.name || `任务 ${i + 1}`,
          description: t.description || '',
          estimated_hours: Number(t.estimated_hours) || 1,
          phase: t.phase || '学习任务',
          objectives: t.objectives || [],
          resources: t.resources || [],
        }))
        if (!generatedTasks.value.length) {
          ElMessage.warning('AI 未生成有效任务，请调整目标后重试')
        } else {
          ElMessage.success(`成功生成 ${generatedTasks.value.length} 个子任务`)
        }
      }
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      generating.value = false
    }
  })
}

function resetForm() {
  formRef.value?.resetFields()
  form.dailyHours = 4
  form.density = 'normal'
  form.focusPoints = ''
  form.category = ''
  generatedTasks.value = []
  planOverview.value = null
  // 清除草稿
  localStorage.removeItem(DRAFT_KEY)
  checkFormValid()
}

function addTask() {
  generatedTasks.value.push({
    name: '新任务',
    description: '',
    estimated_hours: 1,
    phase: '学习任务',
    objectives: [],
    resources: [],
  })
}

function removeTask(index) {
  generatedTasks.value.splice(index, 1)
}

// ---------------- 保存 ----------------
const saveDialogVisible = ref(false)
const saving = ref(false)
const saveFormRef = ref()

const saveForm = reactive({
  title: '',
  category: '',
})

const saveRules = {
  title: [
    { required: true, message: '请输入任务包标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题 2-50 个字符', trigger: 'blur' },
  ],
  category: [{ required: true, message: '请选择或输入分类', trigger: 'change' }],
}

function openSaveDialog() {
  if (!generatedTasks.value.length) {
    ElMessage.warning('请先生成任务')
    return
  }
  // 预填标题：取学习目标前 20 字
  saveForm.title = form.goal.length > 20 ? form.goal.slice(0, 20) + '...' : form.goal
  saveForm.category = ''
  saveDialogVisible.value = true
}

async function handleSave() {
  await saveFormRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const res = await aiTaskApi.save({
        title: saveForm.title,
        category: saveForm.category,
        goal: form.goal,
        level: form.level,
        daily_hours: form.dailyHours,
        tasks: generatedTasks.value.map((t) => ({
          name: t.name,
          description: t.description,
          estimated_hours: t.estimated_hours,
        })),
      })
      if (res.code === 200) {
        ElMessage.success('任务包保存成功')
        saveDialogVisible.value = false
        generatedTasks.value = []
        // 刷新任务包列表
        loadMyPackages()
        // 跳转到详情页
        if (res.data?.id) {
          router.push(`/ai-task/${res.data.id}`)
        }
      }
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      saving.value = false
    }
  })
}

// ---------------- 我的任务包 ----------------
const myPackages = ref([])
const pkgLoading = ref(false)

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

function goPackageDetail(id) {
  router.push(`/ai-task/${id}`)
}

function formatDate(str) {
  if (!str) return '未知时间'
  const d = new Date(str)
  if (isNaN(d.getTime())) return str
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function phaseTagType(idx) {
  const types = ['', 'success', 'warning', 'danger', 'info']
  return types[idx % types.length]
}

onMounted(() => {
  // 恢复草稿
  loadDraft()
  checkFormValid()
  loadMyPackages()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #303133;
}

/* ---------- 通用卡片 ---------- */
.card-box {
  background: #fff;
  border-radius: 12px;
  padding: 22px;
  margin-bottom: 20px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

/* ---------- 模板快捷填充 ---------- */
.template-card {
  background: linear-gradient(135deg, #f0f5ff 0%, #f6f8ff 100%);
  padding: 16px 22px;
}

.template-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #409eff;
  font-weight: 600;
  font-size: 14px;
}

.template-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* ---------- 生成表单 ---------- */
.form-card {
  background: linear-gradient(135deg, #ffffff 0%, #f6f8ff 100%);
}

.form-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.form-header-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  flex-shrink: 0;
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.form-subtitle {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* ---------- 表单提示 ---------- */
.form-tip {
  font-size: 13px;
  color: #606266;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 8px 14px;
  margin-bottom: 20px;
}

.required-mark {
  color: #f56c6c;
  font-weight: 600;
}

/* ---------- 表单分组 ---------- */
.form-group {
  margin-bottom: 8px;
}

.group-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.group-divider {
  margin: 0 0 18px 0;
}

/* ---------- 标签 tooltip ---------- */
.label-with-tooltip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.tooltip-icon {
  font-size: 14px;
  color: #c0c4cc;
  cursor: help;
}

.tooltip-icon:hover {
  color: #909399;
}

/* ---------- 范围提示 ---------- */
.range-hint {
  font-size: 12px;
  color: #909399;
  font-weight: 400;
  margin-left: 4px;
}

/* ---------- 下拉选项描述 ---------- */
.opt-desc {
  float: right;
  color: #909399;
  font-size: 12px;
}

/* ---------- 滑块 ---------- */
.slider-wrap {
  display: flex;
  align-items: center;
  gap: 20px;
  width: 100%;
}

.slider-wrap :deep(.el-slider) {
  flex: 1;
}

.slider-value {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
  white-space: nowrap;
  min-width: 70px;
  text-align: right;
}

/* ---------- 快捷预设按钮 ---------- */
.preset-buttons {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

/* ---------- 预期提示 ---------- */
.generate-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #67c23a;
  background: #f0f9eb;
  padding: 10px 14px;
  border-radius: 8px;
  margin-top: 8px;
  margin-bottom: 16px;
}

/* ---------- 操作按钮 ---------- */
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

/* ---------- 加载态 ---------- */
.loading-box {
  text-align: center;
  padding: 50px 20px;
}

.loading-icon {
  color: #409eff;
  animation: rotate 1.2s linear infinite;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 16px;
  color: #606266;
  font-size: 14px;
}

.loading-subtext {
  margin-top: 6px;
  color: #c0c4cc;
  font-size: 12px;
}

/* ---------- 结果列表 ---------- */
.result-actions {
  display: flex;
  gap: 10px;
}

.result-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 18px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.task-item {
  display: flex;
  gap: 14px;
  padding: 16px;
  border-radius: 10px;
  background: #f9fafc;
  border: 1px solid #ebeef5;
  transition: border-color 0.2s;
}

.task-item:hover {
  border-color: #c6e2ff;
}

.task-index {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.task-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-name-input :deep(.el-input-group__prepend) {
  background: #ecf5ff;
  color: #409eff;
  font-size: 12px;
  padding: 0 10px;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  font-size: 13px;
  color: #606266;
}

.meta-unit {
  font-size: 13px;
  color: #909399;
}

.task-ops {
  display: flex;
  align-items: flex-start;
}

.add-task-bar {
  margin-top: 16px;
  text-align: center;
}

/* ---------- 任务包卡片 ---------- */
.pkg-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 18px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
}

.pkg-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-color: #c6e2ff;
}

.pkg-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.pkg-card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #ecf5ff;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pkg-card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  line-height: 1.5;
  /* 两行省略 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pkg-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px dashed #ebeef5;
  padding-top: 10px;
}

.pkg-card-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

/* ---------- 保存对话框 ---------- */
.save-summary {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
  background: #f5f7fa;
  padding: 10px 14px;
  border-radius: 6px;
}

.save-summary b {
  color: #409eff;
}

/* ---------- 计划概览 ---------- */
.plan-overview {
  background: linear-gradient(135deg, #f0f5ff 0%, #f6f8ff 100%);
  border: 1px solid #d9e2ff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 18px;
}

.overview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.overview-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.overview-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 16px;
}

.overview-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.phase-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* ---------- 阶段分组 ---------- */
.phase-groups {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.phase-group {
  border-left: 3px solid #409eff;
  padding-left: 16px;
}

.phase-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.phase-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

/* ---------- 任务目标与资源 ---------- */
.task-objectives,
.task-resources {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.objectives-label,
.resources-label {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
  line-height: 24px;
}

.objective-tag,
.resource-tag {
  margin-bottom: 2px;
}
</style>
