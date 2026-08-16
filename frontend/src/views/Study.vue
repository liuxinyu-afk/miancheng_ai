<template>
  <div class="page-container">
    <h2 class="page-title">学习中心</h2>

    <el-row :gutter="20">
      <!-- 左侧：今日打卡 + 打卡历史 -->
      <el-col :xs="24" :md="14">
        <!-- 今日打卡 -->
        <div class="card-box">
          <div class="section-header">
            <span class="section-title">
              <el-icon><Calendar /></el-icon> 今日打卡
            </span>
            <el-tag type="success" size="small">今日 {{ todayList.length }} 条</el-tag>
          </div>

          <div v-loading="todayLoading" class="timeline-wrap">
            <el-empty
              v-if="!todayLoading && todayList.length === 0"
              description="今天还没有打卡记录"
              :image-size="60"
            />
            <el-timeline v-else>
              <el-timeline-item
                v-for="item in todayList"
                :key="item.id"
                :timestamp="formatTime(item.check_time)"
                placement="top"
                :type="statusTagType(item.status)"
              >
                <div class="timeline-content">
                  <el-tag :type="statusTagType(item.status)" size="small" effect="light">
                    {{ statusLabel(item.status) }}
                  </el-tag>
                  <span v-if="item.task_id" class="timeline-task">
                    任务 #{{ item.task_id }}
                  </span>
                  <div v-if="item.remark" class="timeline-remark">
                    {{ item.remark }}
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>

        <!-- 打卡历史 -->
        <div class="card-box">
          <div class="section-header">
            <span class="section-title">
              <el-icon><Clock /></el-icon> 打卡历史
            </span>
          </div>

          <el-table
            v-loading="historyLoading"
            :data="historyList"
            stripe
            style="width: 100%"
          >
            <el-table-column label="任务ID" width="110">
              <template #default="{ row }">
                {{ row.task_id ? '#' + row.task_id : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)" size="small" effect="light">
                  {{ statusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="备注" min-width="180" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.remark || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="打卡时间" width="170">
              <template #default="{ row }">
                {{ formatTime(row.check_time) }}
              </template>
            </el-table-column>
          </el-table>

          <div v-if="historyTotal > 0" class="pagination-wrap">
            <el-pagination
              v-model:current-page="historyPage"
              v-model:page-size="historyPageSize"
              :total="historyTotal"
              :page-sizes="[5, 10, 20]"
              layout="total, sizes, prev, pager, next"
              background
              @current-change="fetchHistory"
              @size-change="handleHistorySizeChange"
            />
          </div>
        </div>
      </el-col>

      <!-- 右侧：学习笔记 -->
      <el-col :xs="24" :md="10">
        <div class="card-box">
          <div class="section-header">
            <span class="section-title">
              <el-icon><Notebook /></el-icon> 学习笔记
            </span>
            <el-button
              type="primary"
              size="small"
              :icon="Plus"
              @click="openNoteDialog()"
            >
              新建笔记
            </el-button>
          </div>

          <div v-loading="notesLoading" class="note-list">
            <el-empty
              v-if="!notesLoading && notes.length === 0"
              description="还没有学习笔记"
              :image-size="60"
            />
            <el-card
              v-for="note in notes"
              :key="note.id"
              shadow="hover"
              class="note-card"
              @click="openNoteDetail(note)"
            >
              <div class="note-top">
                <span class="note-title">{{ note.title }}</span>
                <el-tag
                  :type="note.is_public ? 'success' : 'info'"
                  size="small"
                  effect="plain"
                >
                  {{ note.is_public ? '公开' : '私密' }}
                </el-tag>
              </div>

              <div class="note-content">{{ note.content }}</div>

              <div class="note-meta" @click.stop>
                <span>{{ formatTime(note.updated_at || note.created_at) }}</span>
                <div class="note-actions">
                  <el-button
                    type="primary"
                    size="small"
                    text
                    :icon="View"
                    @click.stop="openNoteDetail(note)"
                  >
                    查看
                  </el-button>
                  <el-button
                    type="warning"
                    size="small"
                    text
                    :icon="Edit"
                    @click.stop="openNoteDialog(note)"
                  >
                    编辑
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    text
                    :icon="Delete"
                    @click.stop="handleDeleteNote(note)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 笔记对话框 -->
    <el-dialog
      v-model="noteDialogVisible"
      :title="noteEditingId ? '编辑笔记' : '新建笔记'"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="noteFormRef"
        :model="noteForm"
        :rules="noteRules"
        label-position="top"
      >
        <el-form-item label="笔记标题" prop="title">
          <el-input
            v-model="noteForm.title"
            placeholder="请输入笔记标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="笔记内容" prop="content">
          <el-input
            v-model="noteForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入笔记内容..."
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="是否公开">
          <el-switch
            v-model="noteForm.is_public"
            active-text="公开"
            inactive-text="私密"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="noteSubmitting"
          @click="submitNote"
        >
          {{ noteEditingId ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 笔记详情对话框 -->
    <el-dialog
      v-model="noteDetailVisible"
      :title="noteDetail.title || '笔记详情'"
      width="640px"
    >
      <div class="note-detail-body">
        <div class="note-detail-meta">
          <el-tag :type="noteDetail.is_public ? 'success' : 'info'" size="small" effect="plain">
            {{ noteDetail.is_public ? '公开' : '私密' }}
          </el-tag>
          <span class="note-detail-time">{{ formatTime(noteDetail.updated_at || noteDetail.created_at) }}</span>
        </div>
        <div class="note-detail-content">{{ noteDetail.content || '暂无内容' }}</div>
      </div>
      <template #footer>
        <el-button @click="noteDetailVisible = false">关闭</el-button>
        <el-button type="warning" :icon="Edit" @click="noteDetailVisible = false; openNoteDialog(noteDetail)">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Calendar, Clock, Notebook, Plus, Edit, Delete, View,
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useAuthStore } from '@/stores/auth'
import { studyApi } from '@/api'

const authStore = useAuthStore()

// ============ 今日打卡 ============
const todayLoading = ref(false)
const todayList = ref([])

async function fetchToday() {
  todayLoading.value = true
  try {
    const res = await studyApi.todayCheckin()
    todayList.value = res.data || []
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    todayLoading.value = false
  }
}

// ============ 打卡历史 ============
const historyLoading = ref(false)
const historyList = ref([])
const historyTotal = ref(0)
const historyPage = ref(1)
const historyPageSize = ref(10)

async function fetchHistory() {
  historyLoading.value = true
  try {
    const res = await studyApi.checkinHistory({
      page: historyPage.value,
      page_size: historyPageSize.value,
    })
    historyList.value = res.data || []
    historyTotal.value = res.total || 0
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    historyLoading.value = false
  }
}

function handleHistorySizeChange() {
  historyPage.value = 1
  fetchHistory()
}

// ============ 学习笔记 ============
const notesLoading = ref(false)
const notes = ref([])

async function fetchNotes() {
  notesLoading.value = true
  try {
    const res = await studyApi.myNotes()
    notes.value = res.data || []
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    notesLoading.value = false
  }
}

const noteDialogVisible = ref(false)
const noteSubmitting = ref(false)
const noteFormRef = ref()
const noteEditingId = ref(null)
const noteForm = reactive({
  title: '',
  content: '',
  is_public: false,
})
const noteRules = {
  title: [{ required: true, message: '请输入笔记标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入笔记内容', trigger: 'blur' }],
}

// 笔记详情
const noteDetailVisible = ref(false)
const noteDetail = ref({})

function openNoteDetail(note) {
  noteDetail.value = { ...note }
  noteDetailVisible.value = true
}

function openNoteDialog(note) {
  if (note) {
    noteEditingId.value = note.id
    noteForm.title = note.title
    noteForm.content = note.content
    noteForm.is_public = !!note.is_public
  } else {
    noteEditingId.value = null
    noteForm.title = ''
    noteForm.content = ''
    noteForm.is_public = false
  }
  noteDialogVisible.value = true
}

async function submitNote() {
  await noteFormRef.value.validate(async (valid) => {
    if (!valid) return
    noteSubmitting.value = true
    try {
      if (noteEditingId.value) {
        await studyApi.updateNote(noteEditingId.value, {
          title: noteForm.title,
          content: noteForm.content,
          is_public: noteForm.is_public,
        })
        ElMessage.success('笔记已更新')
      } else {
        await studyApi.createNote({
          title: noteForm.title,
          content: noteForm.content,
          is_public: noteForm.is_public,
        })
        ElMessage.success('笔记已创建')
      }
      noteDialogVisible.value = false
      fetchNotes()
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      noteSubmitting.value = false
    }
  })
}

async function handleDeleteNote(note) {
  try {
    await ElMessageBox.confirm(
      `确定删除笔记「${note.title}」吗？`,
      '提示',
      { type: 'warning' }
    )
    await studyApi.deleteNote(note.id)
    ElMessage.success('删除成功')
    fetchNotes()
  } catch (e) {
    // 取消或错误
  }
}

// ============ 工具函数 ============
function formatTime(t) {
  if (!t) return ''
  const d = dayjs(t)
  return d.isValid() ? d.format('YYYY-MM-DD HH:mm') : t
}

function statusLabel(status) {
  const map = {
    completed: '已完成',
    done: '已完成',
    pending: '进行中',
    in_progress: '进行中',
    missed: '已错过',
  }
  return map[status] || (status ? status : '未知')
}

function statusTagType(status) {
  const map = {
    completed: 'success',
    done: 'success',
    pending: 'warning',
    in_progress: 'warning',
    missed: 'danger',
  }
  return map[status] || 'info'
}

onMounted(() => {
  fetchToday()
  fetchHistory()
  fetchNotes()
})
</script>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.timeline-wrap {
  min-height: 120px;
}

.timeline-content {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.timeline-task {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.timeline-remark {
  width: 100%;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-top: 4px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.note-list {
  min-height: 200px;
}

.note-card {
  margin-bottom: 12px;
}

.note-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.note-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.note-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 10px;
}

.note-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #c0c4cc;
}

.note-actions {
  display: flex;
  gap: 4px;
}

/* 笔记详情 */
.note-detail-body {
  min-height: 200px;
}

.note-detail-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.note-detail-time {
  font-size: 13px;
  color: #909399;
}

.note-detail-content {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  padding: 16px;
  background: #f9fafc;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  min-height: 120px;
}

.note-card {
  cursor: pointer;
  transition: all 0.2s;
}

.note-card:hover {
  border-color: #c6e2ff;
}
</style>
