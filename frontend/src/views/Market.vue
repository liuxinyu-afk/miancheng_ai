<template>
  <div class="page-container">
    <h2 class="page-title">资源集市</h2>

    <!-- 搜索栏 -->
    <div class="card-box search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索资源标题 / 关键词"
        clearable
        :prefix-icon="Search"
        style="width: 280px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-select
        v-model="category"
        placeholder="选择分类"
        clearable
        style="width: 160px"
        @change="handleSearch"
      >
        <el-option
          v-for="opt in categoryOptions"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
        />
      </el-select>
      <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      <el-button :icon="RefreshLeft" @click="handleReset">重置</el-button>
      <el-button
        type="success"
        :icon="EditPen"
        class="publish-btn"
        @click="openPublishDialog"
      >
        发布资源
      </el-button>
    </div>

    <!-- 资源列表 -->
    <div v-loading="loading" class="resource-list">
      <el-empty
        v-if="!loading && list.length === 0"
        description="暂无资源，快去发布第一个吧"
      />
      <el-row :gutter="16">
        <el-col
          v-for="item in list"
          :key="item.id"
          :xs="24"
          :sm="12"
          :lg="8"
        >
          <el-card shadow="hover" class="resource-card" @click="goDetail(item.id)">
            <div class="card-top">
              <span class="card-title">{{ item.title }}</span>
              <el-tag size="small" :type="categoryTagType(item.category)" effect="light">
                {{ item.category || '未分类' }}
              </el-tag>
            </div>

            <div class="card-tags">
              <el-tag
                size="small"
                :type="roleTagType(item.publisher_role)"
                effect="plain"
              >
                {{ roleLabel(item.publisher_role) }}
              </el-tag>
              <el-tag
                v-if="item.is_teacher_certified"
                size="small"
                type="warning"
                effect="dark"
              >
                <el-icon class="cert-icon"><Avatar /></el-icon>教师认证
              </el-tag>
            </div>

            <div class="card-footer">
              <span class="meta-item">
                <el-icon><View /></el-icon>
                {{ item.view_count || 0 }} 浏览
              </span>
              <span class="meta-item">
                <el-icon><Clock /></el-icon>
                {{ formatTime(item.created_at) }}
              </span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination-wrap">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[9, 12, 24]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="fetchList"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 发布资源对话框 -->
    <el-dialog
      v-model="publishDialogVisible"
      title="发布资源"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="publishFormRef"
        :model="publishForm"
        :rules="publishRules"
        label-position="top"
      >
        <el-form-item label="资源标题" prop="title">
          <el-input
            v-model="publishForm.title"
            placeholder="请输入资源标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="资源分类" prop="category">
          <el-select
            v-model="publishForm.category"
            placeholder="请选择分类"
            style="width: 100%"
          >
            <el-option
              v-for="opt in categoryOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="资源内容" prop="content">
          <el-input
            v-model="publishForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入资源内容描述..."
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="附件URL">
          <el-input
            v-model="publishForm.attachment_url"
            placeholder="https://example.com/file.pdf"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="publishDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="publishSubmitting"
          @click="submitPublish"
        >
          发布
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search, RefreshLeft, EditPen, View, Clock, Avatar,
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useAuthStore } from '@/stores/auth'
import { marketApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

// 分类选项
const categoryOptions = [
  { value: '考研', label: '考研' },
  { value: '考证', label: '考证' },
  { value: '专业课', label: '专业课' },
  { value: '技能学习', label: '技能学习' },
  { value: '其他', label: '其他' },
]

// ============ 列表查询 ============
const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(9)
const keyword = ref('')
const category = ref('')

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    if (category.value) params.category = category.value
    const res = await marketApi.list(params)
    list.value = res.data || []
    total.value = res.total || 0
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchList()
}

function handleReset() {
  keyword.value = ''
  category.value = ''
  page.value = 1
  fetchList()
}

function handleSizeChange() {
  page.value = 1
  fetchList()
}

function goDetail(id) {
  router.push('/market/' + id)
}

// ============ 发布资源 ============
const publishDialogVisible = ref(false)
const publishSubmitting = ref(false)
const publishFormRef = ref()
const publishForm = reactive({
  title: '',
  category: '',
  content: '',
  attachment_url: '',
})
const publishRules = {
  title: [{ required: true, message: '请输入资源标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择资源分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入资源内容', trigger: 'blur' }],
}

function openPublishDialog() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录后再发布资源')
    router.push('/login')
    return
  }
  publishForm.title = ''
  publishForm.category = ''
  publishForm.content = ''
  publishForm.attachment_url = ''
  publishDialogVisible.value = true
}

async function submitPublish() {
  await publishFormRef.value.validate(async (valid) => {
    if (!valid) return
    publishSubmitting.value = true
    try {
      await marketApi.publish({
        title: publishForm.title,
        category: publishForm.category,
        content: publishForm.content,
        attachment_url: publishForm.attachment_url,
      })
      ElMessage.success('资源发布成功')
      publishDialogVisible.value = false
      page.value = 1
      fetchList()
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      publishSubmitting.value = false
    }
  })
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
  fetchList()
})
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-bar .publish-btn {
  margin-left: auto;
}

.resource-list {
  min-height: 300px;
}

.resource-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.resource-card:hover {
  transform: translateY(-2px);
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.cert-icon {
  margin-right: 2px;
  vertical-align: -2px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px dashed #ebeef5;
  color: #909399;
  font-size: 13px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
