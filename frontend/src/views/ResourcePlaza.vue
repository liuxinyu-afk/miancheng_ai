<template>
  <div class="plaza-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <h2>交流广场</h2>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="fetchList">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">发布帖子</el-button>
      </div>
    </div>

    <div class="plaza-container">
      <!-- 左侧：帖子列表 -->
      <div class="plaza-list-panel">
        <!-- 筛选栏 -->
        <div class="filter-bar">
          <el-input
            v-model="keyword"
            placeholder="搜索标题或内容"
            :prefix-icon="Search"
            clearable
            size="small"
            style="width: 220px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
          <el-radio-group v-model="selectedCategory" size="small" @change="handleSearch">
            <el-radio-button label="全部">全部</el-radio-button>
            <el-radio-button label="考研">考研</el-radio-button>
            <el-radio-button label="编程">编程</el-radio-button>
            <el-radio-button label="英语">英语</el-radio-button>
            <el-radio-button label="论文">论文</el-radio-button>
            <el-radio-button label="职业">职业</el-radio-button>
            <el-radio-button label="其他">其他</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 帖子列表 -->
        <div class="request-list" v-loading="loading">
          <el-empty v-if="!loading && list.length === 0" description="暂无帖子，快来发布一个吧" :image-size="60" />
          <el-card
            v-for="item in list"
            :key="item.id"
            shadow="hover"
            class="request-card"
            :class="{ active: activeRequest?.id === item.id }"
            @click="selectRequest(item)"
          >
            <div class="request-card-header">
              <span class="request-title">{{ item.title }}</span>
              <el-tag :type="statusTagType(item.status)" size="small" effect="plain">
                {{ statusLabel(item.status) }}
              </el-tag>
            </div>
            <div class="request-card-content">{{ item.content }}</div>
            <!-- 缩略图 -->
            <div class="request-card-images" v-if="item.images && item.images.length">
              <el-image
                v-for="(img, idx) in item.images.slice(0, 3)"
                :key="idx"
                :src="img"
                fit="cover"
                class="card-thumb"
                :preview-src-list="item.images"
                :preview-teleported="true"
                @click.stop
              />
              <span v-if="item.images.length > 3" class="more-images">+{{ item.images.length - 3 }}</span>
            </div>
            <div class="request-card-footer">
              <div class="request-author">
                <el-avatar :size="20" :style="{ background: categoryColor(item.category) }">
                  {{ (item.author_name || 'U').charAt(0) }}
                </el-avatar>
                <span class="author-name">{{ item.author_name }}</span>
                <el-tag size="small" :type="roleTagType(item.author_role)" effect="plain">{{ roleLabel(item.author_role) }}</el-tag>
              </div>
              <div class="request-meta">
                <span><el-icon><ChatLineRound /></el-icon> {{ item.reply_count }}</span>
                <span><el-icon><View /></el-icon> {{ item.view_count }}</span>
                <span class="time">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrap" v-if="total > pageSize">
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
            small
            @current-change="fetchList"
          />
        </div>
      </div>

      <!-- 右侧：详情 + 回复 -->
      <div class="plaza-detail-panel">
        <template v-if="activeRequest">
          <!-- 帖子详情 -->
          <div class="detail-header">
            <h3>{{ activeRequest.title }}</h3>
            <div class="detail-meta">
              <el-tag :type="statusTagType(activeRequest.status)" size="small">{{ statusLabel(activeRequest.status) }}</el-tag>
              <el-tag type="info" size="small" effect="plain">{{ activeRequest.category }}</el-tag>
              <span class="detail-time">{{ formatTime(activeRequest.created_at) }}</span>
            </div>
          </div>

          <div class="detail-author">
            <el-avatar :size="32" :style="{ background: categoryColor(activeRequest.category) }">
              {{ (activeRequest.author_name || 'U').charAt(0) }}
            </el-avatar>
            <div class="author-info">
              <span class="author-name">{{ activeRequest.author_name }}</span>
              <el-tag size="small" :type="roleTagType(activeRequest.author_role)" effect="plain">{{ roleLabel(activeRequest.author_role) }}</el-tag>
            </div>
            <div class="author-actions" v-if="activeRequest.is_owner">
              <el-select v-model="activeRequest.status" size="small" style="width: 100px" @change="handleStatusChange">
                <el-option label="待解决" value="open" />
                <el-option label="已解决" value="solved" />
                <el-option label="已关闭" value="closed" />
              </el-select>
              <el-button size="small" type="danger" text :icon="Delete" @click="handleDelete">删除</el-button>
            </div>
          </div>

          <div class="detail-content">{{ activeRequest.content }}</div>

          <!-- 详情图片 -->
          <div class="detail-images" v-if="activeRequest.images && activeRequest.images.length">
            <el-image
              v-for="(img, idx) in activeRequest.images"
              :key="idx"
              :src="img"
              fit="cover"
              class="detail-img"
              :preview-src-list="activeRequest.images"
              :initial-index="idx"
              :preview-teleported="true"
            />
          </div>

          <div class="detail-tags" v-if="activeRequest.tags">
            <el-tag v-for="tag in activeRequest.tags.split(',').filter(t => t.trim())" :key="tag" size="small" effect="plain">
              #{{ tag.trim() }}
            </el-tag>
          </div>

          <el-divider />

          <!-- 回复区 -->
          <div class="replies-section">
            <div class="replies-header">
              <span>回复 ({{ replies.length }})</span>
              <el-button v-if="activeRequest.status !== 'closed'" type="primary" size="small" :icon="Plus" @click="openReplyDialog">
                回复/分享资料
              </el-button>
            </div>

            <div class="replies-list" v-loading="repliesLoading">
              <el-empty v-if="!repliesLoading && replies.length === 0" description="暂无回复，快来分享吧" :image-size="40" />
              <div v-for="reply in replies" :key="reply.id" class="reply-item" :class="{ 'reply-accepted': reply.is_accepted }">
                <div class="reply-header">
                  <el-avatar :size="28" :style="{ background: '#409eff' }">{{ (reply.author_name || 'U').charAt(0) }}</el-avatar>
                  <span class="reply-author">{{ reply.author_name }}</span>
                  <el-tag size="small" :type="roleTagType(reply.author_role)" effect="plain">{{ roleLabel(reply.author_role) }}</el-tag>
                  <el-tag v-if="reply.is_accepted" type="success" size="small" effect="dark">已采纳</el-tag>
                  <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
                </div>
                <div class="reply-content">{{ reply.content }}</div>
                <!-- 回复图片 -->
                <div class="reply-images" v-if="reply.images && reply.images.length">
                  <el-image
                    v-for="(img, idx) in reply.images"
                    :key="idx"
                    :src="img"
                    fit="cover"
                    class="reply-img"
                    :preview-src-list="reply.images"
                    :initial-index="idx"
                    :preview-teleported="true"
                  />
                </div>
                <div class="reply-link" v-if="reply.resource_link">
                  <el-link :href="reply.resource_link" target="_blank" type="primary" :icon="Link">
                    {{ reply.resource_link }}
                  </el-link>
                </div>
                <div class="reply-actions">
                  <el-button
                    v-if="activeRequest.is_owner && !reply.is_accepted && activeRequest.status === 'open'"
                    size="small"
                    type="success"
                    text
                    @click="handleAccept(reply)"
                  >采纳</el-button>
                  <el-button
                    v-if="reply.is_owner || isAdmin"
                    size="small"
                    type="danger"
                    text
                    @click="handleDeleteReply(reply)"
                  >删除</el-button>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- 空状态 -->
        <div v-else class="detail-empty">
          <el-icon :size="60" color="#dcdfe6"><ChatLineSquare /></el-icon>
          <p>点击左侧帖子查看详情</p>
        </div>
      </div>
    </div>

    <!-- 发布帖子对话框 -->
    <el-dialog v-model="createDialogVisible" title="发布帖子" width="600px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="createForm.title" placeholder="如：求一份考研政治复习资料" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="createForm.category" style="width: 100%">
            <el-option label="考研" value="考研" />
            <el-option label="编程" value="编程" />
            <el-option label="英语" value="英语" />
            <el-option label="论文" value="论文" />
            <el-option label="职业" value="职业" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-input v-model="createForm.tags" placeholder="多个标签用逗号分隔，如：高数,线代,真题" />
        </el-form-item>
        <el-form-item label="详细描述" prop="content">
          <el-input
            v-model="createForm.content"
            type="textarea"
            :rows="5"
            placeholder="详细描述你的需求，越具体越容易得到帮助"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="图片">
          <el-upload
            v-model:file-list="createFileList"
            action="#"
            list-type="picture-card"
            :auto-upload="true"
            :http-request="handleUploadImage"
            :before-upload="beforeUpload"
            accept="image/jpeg,image/png,image/gif,image/webp"
            :limit="6"
            :on-exceed="() => ElMessage.warning('最多上传6张图片')"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持 JPG/PNG/GIF/WEBP，单张不超过5MB，最多6张</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="createLoading">发布</el-button>
      </template>
    </el-dialog>

    <!-- 回复对话框 -->
    <el-dialog v-model="replyDialogVisible" title="回复/分享资料" width="560px">
      <el-form ref="replyFormRef" :model="replyForm" :rules="replyRules" label-width="80px">
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="replyForm.content"
            type="textarea"
            :rows="4"
            placeholder="描述你要分享的资料或回复内容"
          />
        </el-form-item>
        <el-form-item label="资料链接" prop="resource_link">
          <el-input v-model="replyForm.resource_link" placeholder="粘贴网盘链接或网址（选填）" />
        </el-form-item>
        <el-form-item label="图片">
          <el-upload
            v-model:file-list="replyFileList"
            action="#"
            list-type="picture-card"
            :auto-upload="true"
            :http-request="handleUploadImageReply"
            :before-upload="beforeUpload"
            accept="image/jpeg,image/png,image/gif,image/webp"
            :limit="6"
            :on-exceed="() => ElMessage.warning('最多上传6张图片')"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">可上传截图或资料预览图</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleReply" :loading="replyLoading">发送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, ChatLineRound, ChatLineSquare, View, Delete, Link,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { plazaApi } from '@/api'

const authStore = useAuthStore()

const isAdmin = computed(() => authStore.role === 'admin')

// 列表
const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const keyword = ref('')
const selectedCategory = ref('全部')

// 详情
const activeRequest = ref(null)
const replies = ref([])
const repliesLoading = ref(false)

// 发布帖子
const createDialogVisible = ref(false)
const createLoading = ref(false)
const createFormRef = ref()
const createForm = ref({ title: '', content: '', category: '其他', tags: '', images: '' })
const createRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}
const createFileList = ref([])
const createImageUrls = ref([])

// 回复
const replyDialogVisible = ref(false)
const replyLoading = ref(false)
const replyFormRef = ref()
const replyForm = ref({ content: '', resource_link: '', images: '' })
const replyRules = {
  content: [{ required: true, message: '请输入回复内容', trigger: 'blur' }],
}
const replyFileList = ref([])
const replyImageUrls = ref([])

// ==================== 工具函数 ====================
function formatTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
  if (diff < 604800) return Math.floor(diff / 86400) + '天前'
  return d.toLocaleDateString()
}

function statusLabel(status) {
  return { open: '待解决', solved: '已解决', closed: '已关闭' }[status] || status
}

function statusTagType(status) {
  return { open: 'warning', solved: 'success', closed: 'info' }[status] || 'info'
}

function categoryColor(category) {
  const map = { '考研': '#f56c6c', '编程': '#409eff', '英语': '#67c23a', '论文': '#e6a23c', '职业': '#909399', '其他': '#b37feb' }
  return map[category] || '#909399'
}

function roleLabel(role) {
  return { student: '学生', teacher: '教师', auditor: '审核员', admin: '管理员' }[role] || role
}

function roleTagType(role) {
  return { student: 'success', teacher: 'warning', auditor: 'primary', admin: '' }[role] || 'info'
}

// ==================== 图片上传 ====================
function beforeUpload(file) {
  const isImage = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  if (!isImage) {
    ElMessage.error('仅支持 JPG/PNG/GIF/WEBP 格式')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过5MB')
    return false
  }
  return true
}

async function handleUploadImage({ file, onSuccess, onError }) {
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await plazaApi.uploadImage(formData)
    if (res.data?.url) {
      createImageUrls.value.push(res.data.url)
      onSuccess?.(res)
    }
  } catch (e) {
    ElMessage.error('图片上传失败')
    onError?.(e)
  }
}

async function handleUploadImageReply({ file, onSuccess, onError }) {
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await plazaApi.uploadImage(formData)
    if (res.data?.url) {
      replyImageUrls.value.push(res.data.url)
      onSuccess?.(res)
    }
  } catch (e) {
    ElMessage.error('图片上传失败')
    onError?.(e)
  }
}

// ==================== 列表 ====================
async function fetchList() {
  loading.value = true
  try {
    const res = await plazaApi.list({
      keyword: keyword.value || undefined,
      category: selectedCategory.value !== '全部' ? selectedCategory.value : undefined,
      page: page.value,
      page_size: pageSize,
    })
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (e) { /* handled */ } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchList()
}

// ==================== 详情 ====================
async function selectRequest(item) {
  activeRequest.value = item
  await fetchDetail(item.id)
  await fetchReplies(item.id)
}

async function fetchDetail(id) {
  try {
    const res = await plazaApi.detail(id)
    if (res.data) {
      activeRequest.value = res.data
    }
  } catch (e) { /* ignore */ }
}

async function fetchReplies(id) {
  repliesLoading.value = true
  try {
    const res = await plazaApi.replies(id)
    replies.value = res.data || []
  } catch (e) { /* ignore */ } finally {
    repliesLoading.value = false
  }
}

// ==================== 发布帖子 ====================
function openCreateDialog() {
  createForm.value = { title: '', content: '', category: '其他', tags: '', images: '' }
  createFileList.value = []
  createImageUrls.value = []
  createDialogVisible.value = true
}

async function handleCreate() {
  try {
    await createFormRef.value.validate()
    createLoading.value = true
    const images = createImageUrls.value.join(',')
    const res = await plazaApi.create({ ...createForm.value, images })
    ElMessage.success('发布成功')
    createDialogVisible.value = false
    fetchList()
    if (res.data) {
      selectRequest(res.data)
    }
  } catch (e) {
    if (e?.message) ElMessage.error(e.message)
  } finally {
    createLoading.value = false
  }
}

// ==================== 状态管理 ====================
async function handleStatusChange(status) {
  try {
    await plazaApi.updateStatus(activeRequest.value.id, status)
    ElMessage.success('状态已更新')
    fetchList()
  } catch (e) { /* ignore */ }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定删除这条帖子吗？', '提示', { type: 'warning' })
    await plazaApi.delete(activeRequest.value.id)
    ElMessage.success('已删除')
    activeRequest.value = null
    replies.value = []
    fetchList()
  } catch (e) { /* cancel */ }
}

// ==================== 回复 ====================
function openReplyDialog() {
  replyForm.value = { content: '', resource_link: '', images: '' }
  replyFileList.value = []
  replyImageUrls.value = []
  replyDialogVisible.value = true
}

async function handleReply() {
  try {
    await replyFormRef.value.validate()
    replyLoading.value = true
    const images = replyImageUrls.value.join(',')
    await plazaApi.createReply(activeRequest.value.id, { ...replyForm.value, images })
    ElMessage.success('回复成功')
    replyDialogVisible.value = false
    await fetchReplies(activeRequest.value.id)
    fetchList()
  } catch (e) {
    if (e?.message) ElMessage.error(e.message)
  } finally {
    replyLoading.value = false
  }
}

async function handleAccept(reply) {
  try {
    await ElMessageBox.confirm('确定采纳这条回复吗？', '采纳回复', { type: 'success' })
    await plazaApi.acceptReply(activeRequest.value.id, reply.id)
    ElMessage.success('已采纳')
    activeRequest.value.status = 'solved'
    await fetchReplies(activeRequest.value.id)
    fetchList()
  } catch (e) { /* cancel */ }
}

async function handleDeleteReply(reply) {
  try {
    await ElMessageBox.confirm('确定删除这条回复吗？', '提示', { type: 'warning' })
    await plazaApi.deleteReply(activeRequest.value.id, reply.id)
    ElMessage.success('已删除')
    await fetchReplies(activeRequest.value.id)
    fetchList()
  } catch (e) { /* cancel */ }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.plaza-page {
  height: 100%;
  display: flex;
  flex-direction: column;
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
}

.header-actions {
  display: flex;
  gap: 8px;
}

.plaza-container {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

/* 左侧列表 */
.plaza-list-panel {
  width: 420px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.request-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.request-card {
  cursor: pointer;
  transition: all 0.2s;
}

.request-card:hover {
  border-color: #c6e2ff;
}

.request-card.active {
  border-color: #409eff;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.2);
}

.request-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.request-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 8px;
}

.request-card-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
}

.request-card-images {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  align-items: center;
}

.card-thumb {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.more-images {
  font-size: 13px;
  color: #909399;
  margin-left: 4px;
}

.request-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.request-author {
  display: flex;
  align-items: center;
  gap: 4px;
}

.author-name {
  font-size: 12px;
  color: #606266;
}

.request-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.request-meta span {
  display: flex;
  align-items: center;
  gap: 2px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}

/* 右侧详情 */
.plaza-detail-panel {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
}

.detail-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #c0c4cc;
}

.detail-header h3 {
  margin: 0 0 8px;
  font-size: 18px;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-time {
  font-size: 12px;
  color: #909399;
}

.detail-author {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.author-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.detail-content {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  padding: 12px;
  background: #f9fafc;
  border-radius: 8px;
}

.detail-images {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.detail-img {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.detail-tags {
  display: flex;
  gap: 6px;
  margin-top: 12px;
  flex-wrap: wrap;
}

/* 回复区 */
.replies-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
}

.replies-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reply-item {
  padding: 12px;
  border-radius: 8px;
  background: #f9fafc;
  border: 1px solid #ebeef5;
  transition: all 0.2s;
}

.reply-item:hover {
  border-color: #d9ecff;
}

.reply-accepted {
  background: #f0f9eb;
  border-color: #b3e19d;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.reply-author {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.reply-time {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.reply-content {
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
}

.reply-images {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.reply-img {
  width: 100px;
  height: 100px;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.reply-link {
  margin-top: 8px;
}

.reply-link .el-link {
  font-size: 13px;
  word-break: break-all;
}

.reply-actions {
  display: flex;
  gap: 4px;
  margin-top: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
