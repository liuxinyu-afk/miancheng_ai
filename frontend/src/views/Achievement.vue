<template>
  <div class="achievement-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <h2>成果社区</h2>
      <el-button type="primary" :icon="EditPen" @click="openPostDialog">发布成果</el-button>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview" v-loading="statsLoading">
      <div class="stat-card stat-blue">
        <div class="stat-value">{{ stats.total_posts || 0 }}</div>
        <div class="stat-label">成果总数</div>
      </div>
      <div class="stat-card stat-red">
        <div class="stat-value">{{ stats.total_likes || 0 }}</div>
        <div class="stat-label">总点赞数</div>
      </div>
      <div class="stat-card stat-green">
        <div class="stat-value">{{ stats.total_comments || 0 }}</div>
        <div class="stat-label">总评论数</div>
      </div>
      <div class="stat-card stat-orange">
        <div class="stat-value">{{ stats.today_posts || 0 }}</div>
        <div class="stat-label">今日新发布</div>
      </div>
      <div class="stat-card stat-purple">
        <div class="stat-value">{{ stats.my_posts || 0 }}</div>
        <div class="stat-label">我的成果</div>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：帖子列表 -->
      <el-col :xs="24" :md="17">
        <el-card shadow="never" class="list-card">
          <template #header>
            <div class="card-header">
              <span>成果动态</span>
              <el-radio-group v-model="filterStatus" size="small" @change="handleFilterChange">
                <el-radio-button value="">全部</el-radio-button>
                <el-radio-button value="approved">已通过</el-radio-button>
                <el-radio-button value="pending">审核中</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <div v-loading="loading" class="post-list">
            <el-empty v-if="!loading && posts.length === 0" description="暂无成果动态" />

            <el-card
              v-for="post in posts"
              :key="post.id"
              shadow="hover"
              class="post-item"
              :data-post-id="post.id"
            >
              <div class="post-content">
                <!-- 作者信息 -->
                <div class="post-author" :class="{ 'post-author-anonymous': post.is_anonymous }" @click="goToUserProfile(post)">
                  <el-avatar :size="36" :src="post.is_anonymous ? null : getAvatarUrl(post.author_avatar)" class="post-author-avatar">
                    {{ post.is_anonymous ? '匿' : (post.author_name || `用户${post.user_id}`).charAt(0) }}
                  </el-avatar>
                  <div class="post-author-info">
                    <div class="post-author-name">
                      {{ post.is_anonymous ? '匿名用户' : (post.author_name || `用户${post.user_id}`) }}
                      <el-tag v-if="!post.is_anonymous && post.author_role === 'teacher'" type="warning" size="small" effect="dark">教师</el-tag>
                    </div>
                    <div class="post-author-time">{{ formatTime(post.created_at) }}</div>
                  </div>
                </div>

                <!-- 成果类型徽章 -->
                <div v-if="getAchievementType(post.tags)" class="achievement-type-badge">
                  <el-tag :type="achievementTypeTagType(getAchievementType(post.tags))" effect="dark" size="small" round>
                    <el-icon class="type-icon"><component :is="achievementTypeIcon(getAchievementType(post.tags))" /></el-icon>
                    {{ getAchievementType(post.tags) }}
                  </el-tag>
                </div>

                <div class="post-text">{{ post.content }}</div>

                <!-- 图片展示 -->
                <div v-if="parseImages(post.images).length" class="post-images">
                  <el-image
                    v-for="(img, idx) in parseImages(post.images)"
                    :key="idx"
                    :src="img"
                    :preview-src-list="parseImages(post.images)"
                    :initial-index="idx"
                    fit="cover"
                    class="post-image"
                    hide-on-click-modal
                    preview-teleported
                  />
                </div>

                <!-- 标签展示（排除成果类型标签） -->
                <div v-if="getExtraTags(post.tags).length" class="post-tags">
                  <el-tag
                    v-for="(tag, idx) in getExtraTags(post.tags)"
                    :key="idx"
                    size="small"
                    effect="plain"
                    class="post-tag"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>

              <div class="post-meta">
                <span class="meta-item">
                  <el-icon><Clock /></el-icon>
                  {{ formatTime(post.created_at) }}
                </span>
                <el-tag :type="auditTagType(post.audit_status)" size="small" effect="light">
                  {{ auditLabel(post.audit_status) }}
                </el-tag>
              </div>

              <div class="post-actions">
                <el-button
                  :type="postLiked(post) ? 'primary' : 'default'"
                  :icon="postLiked(post) ? StarFilled : Star"
                  size="small"
                  round
                  @click="handleLike(post)"
                >
                  {{ post.like_count || 0 }}
                </el-button>
                <el-button
                  :type="expandedPost === post.id ? 'primary' : 'default'"
                  :icon="ChatDotRound"
                  size="small"
                  round
                  @click="toggleComments(post)"
                >
                  {{ post.comment_count || 0 }} 评论
                </el-button>
                <el-button
                  v-if="post.user_id === authStore.user?.id"
                  type="danger"
                  :icon="Delete"
                  size="small"
                  text
                  @click="handleDelete(post)"
                >
                  删除
                </el-button>
              </div>

              <!-- 评论区 -->
              <div v-if="expandedPost === post.id" class="comment-section">
                <el-divider content-position="left">评论</el-divider>
                <div v-loading="commentLoading" class="comment-list">
                  <el-empty v-if="!commentLoading && comments.length === 0" description="暂无评论，快来抢沙发" :image-size="60" />
                  <div v-for="c in comments" :key="c.id" class="comment-item" :class="{ 'comment-reply-item': c.parent_id }">
                    <el-avatar :size="32" class="comment-avatar">{{ commentInitial(c) }}</el-avatar>
                    <div class="comment-body">
                      <div class="comment-top">
                        <span class="comment-user">{{ c.author_name || `用户${c.user_id}` }}</span>
                        <el-tag v-if="c.is_teacher" type="warning" size="small" effect="dark">教师点评</el-tag>
                        <span class="comment-time">{{ formatTime(c.created_at) }}</span>
                      </div>
                      <div class="comment-text" v-if="c.parent_id && getReplyTarget(c.parent_id)">
                        <span class="reply-to">回复 @{{ getReplyTarget(c.parent_id).author_name || `用户${getReplyTarget(c.parent_id).user_id}` }}：</span>{{ c.content }}
                      </div>
                      <div class="comment-text" v-else>{{ c.content }}</div>
                      <div class="comment-reply-btn" @click="setReplyTo(post, c)">回复</div>
                    </div>
                  </div>
                </div>
                <!-- 回复提示 -->
                <div v-if="replyTo" class="reply-hint">
                  <span>回复 @{{ replyTo.author_name || `用户${replyTo.user_id}` }}</span>
                  <el-button text size="small" @click="cancelReply">取消回复</el-button>
                </div>
                <div class="comment-input">
                  <el-input
                    v-model="commentText"
                    type="textarea"
                    :rows="2"
                    :placeholder="replyTo ? `回复 @${replyTo.author_name || `用户${replyTo.user_id}`}...` : '写下你的评论...'"
                    maxlength="500"
                    show-word-limit
                  />
                  <el-button type="primary" size="small" :loading="commentSubmitting" @click="submitComment(post)">
                    {{ replyTo ? '回复' : '发表评论' }}
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 分页 -->
          <div v-if="total > 0" class="pagination-wrap">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[5, 10, 20]"
              layout="total, sizes, prev, pager, next"
              background
              @current-change="fetchPosts"
              @size-change="handleSizeChange"
            />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：学习排行榜 -->
      <el-col :xs="24" :md="7">
        <el-card shadow="never" class="leaderboard-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Trophy /></el-icon>
                学习排行榜
              </span>
              <el-tag type="info" size="small" effect="plain">TOP 10</el-tag>
            </div>
          </template>

          <div v-loading="leaderboardLoading" class="leaderboard-list">
            <el-empty v-if="!leaderboardLoading && leaderboard.length === 0" description="暂无排行数据" :image-size="60" />
            <div
              v-for="item in leaderboard"
              :key="item.user_id"
              class="leaderboard-item"
              :class="{ 'leaderboard-me': item.is_me }"
              @click="goToUserProfileById(item.user_id)"
            >
              <div class="rank-badge" :class="`rank-${item.rank}`">
                {{ item.rank <= 3 ? '' : item.rank }}
              </div>
              <el-avatar :size="36" :src="getAvatarUrl(item.avatar)" class="leaderboard-avatar">
                {{ (item.nickname || 'U').charAt(0) }}
              </el-avatar>
              <div class="leaderboard-info">
                <div class="leaderboard-name">
                  {{ item.nickname || '未知用户' }}
                  <el-tag v-if="item.is_me" type="primary" size="small" effect="dark">我</el-tag>
                </div>
                <div class="leaderboard-stats">
                  <span class="lb-stat">{{ item.study_minutes }}分钟</span>
                  <span class="lb-stat-divider">·</span>
                  <span class="lb-stat">{{ item.post_count }}成果</span>
                  <span class="lb-stat-divider">·</span>
                  <span class="lb-stat">{{ item.resource_count }}资源</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 我的成果概览 -->
        <el-card shadow="never" class="my-stats-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><DataLine /></el-icon>
                我的成果
              </span>
            </div>
          </template>
          <div class="my-stats-body">
            <div class="my-stat-item">
              <div class="my-stat-value">{{ stats.my_posts || 0 }}</div>
              <div class="my-stat-label">发布成果</div>
            </div>
            <div class="my-stat-divider"></div>
            <div class="my-stat-item">
              <div class="my-stat-value">{{ stats.my_likes || 0 }}</div>
              <div class="my-stat-label">收获点赞</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 发布帖子对话框 -->
    <el-dialog v-model="postDialogVisible" title="发布成果" width="560px" :close-on-click-modal="false">
      <el-form ref="postFormRef" :model="postForm" :rules="postRules" label-position="top">
        <el-form-item label="成果类型" prop="achievement_type">
          <el-radio-group v-model="postForm.achievement_type">
            <el-radio-button value="学习打卡">
              <el-icon><Calendar /></el-icon> 学习打卡
            </el-radio-button>
            <el-radio-button value="资源分享">
              <el-icon><Share /></el-icon> 资源分享
            </el-radio-button>
            <el-radio-button value="考试通过">
              <el-icon><Select /></el-icon> 考试通过
            </el-radio-button>
            <el-radio-button value="项目完成">
              <el-icon><Finished /></el-icon> 项目完成
            </el-radio-button>
            <el-radio-button value="技能解锁">
              <el-icon><MagicStick /></el-icon> 技能解锁
            </el-radio-button>
            <el-radio-button value="读书笔记">
              <el-icon><Reading /></el-icon> 读书笔记
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="成果内容" prop="content">
          <el-input
            v-model="postForm.content"
            type="textarea"
            :rows="5"
            placeholder="分享你的学习成果，展示你的进步和收获..."
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="图片URL（多个用逗号分隔）">
          <el-input v-model="postForm.images" placeholder="https://example.com/1.png, https://example.com/2.png" />
          <div v-if="previewImages.length" class="dialog-preview">
            <el-image
              v-for="(img, idx) in previewImages"
              :key="idx"
              :src="img"
              fit="cover"
              class="preview-image"
            />
          </div>
        </el-form-item>
        <el-form-item label="附加标签">
          <el-input v-model="postForm.tags" placeholder="添加标签，逗号分隔，如：考研,Python,期末复习" />
        </el-form-item>
        <el-form-item label="匿名发布">
          <el-switch v-model="postForm.is_anonymous" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="postDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="postSubmitting" @click="submitPost">发布</el-button>
      </template>
    </el-dialog>

    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="msgDetailVisible"
      :title="msgDetail.title || '消息详情'"
      width="520px"
      :close-on-click-modal="true"
    >
      <div v-loading="msgDetailLoading" class="msg-detail-body">
        <template v-if="msgDetail.data">
          <div class="msg-detail-info">
            <el-tag :type="msgTagType(msgDetail.data.msg_type)" size="small" effect="light">
              {{ msgTypeLabel(msgDetail.data.msg_type) }}
            </el-tag>
            <span class="msg-detail-time">{{ formatTime(msgDetail.data.created_at) }}</span>
          </div>
          <div class="msg-detail-content">{{ msgDetail.data.content }}</div>
          <div v-if="msgDetail.data.sender_name" class="msg-detail-sender">
            <el-avatar :size="36" class="msg-detail-avatar">
              {{ msgDetail.data.sender_name.charAt(0) }}
            </el-avatar>
            <div class="msg-detail-sender-info">
              <div class="msg-detail-sender-name">
                {{ msgDetail.data.sender_name }}
                <el-tag
                  v-if="msgDetail.data.sender_role"
                  :type="msgDetail.data.sender_role === 'teacher' ? 'warning' : 'info'"
                  size="small"
                >
                  {{ roleLabelMap[msgDetail.data.sender_role] || msgDetail.data.sender_role }}
                </el-tag>
              </div>
            </div>
          </div>
          <div v-if="msgDetail.data.post" class="msg-detail-post">
            <div class="msg-detail-post-title">关联成果</div>
            <div class="msg-detail-post-content">{{ msgDetail.data.post.content }}</div>
            <div class="msg-detail-post-meta">
              <span>点赞 {{ msgDetail.data.post.like_count || 0 }}</span>
              <span>评论 {{ msgDetail.data.post.comment_count || 0 }}</span>
            </div>
          </div>
          <div v-if="msgDetail.data.post" class="msg-detail-footer">
            <el-button type="primary" @click="goToPost(msgDetail.data.post.id)">查看完整帖子</el-button>
          </div>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  EditPen, Clock, Star, StarFilled, ChatDotRound, Delete, Bell,
  ArrowRight, ChatLineRound, Star as StarIcon, Select, InfoFilled, Plus,
  Trophy, DataLine, Calendar, Share, Finished, MagicStick, Reading,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { achievementApi } from '@/api'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

// ============ 成果类型定义 ============
const ACHIEVEMENT_TYPES = ['学习打卡', '资源分享', '考试通过', '项目完成', '技能解锁', '读书笔记']

function getAchievementType(tags) {
  if (!tags) return ''
  const tagList = String(tags).split(',').map(s => s.trim())
  return tagList.find(t => ACHIEVEMENT_TYPES.includes(t)) || ''
}

function getExtraTags(tags) {
  if (!tags) return []
  return String(tags).split(',').map(s => s.trim()).filter(t => t && !ACHIEVEMENT_TYPES.includes(t))
}

function achievementTypeTagType(type) {
  const map = {
    '学习打卡': 'primary',
    '资源分享': 'success',
    '考试通过': 'danger',
    '项目完成': 'warning',
    '技能解锁': '',
    '读书笔记': 'info',
  }
  return map[type] || 'info'
}

function achievementTypeIcon(type) {
  const map = {
    '学习打卡': 'Calendar',
    '资源分享': 'Share',
    '考试通过': 'Select',
    '项目完成': 'Finished',
    '技能解锁': 'MagicStick',
    '读书笔记': 'Reading',
  }
  return map[type] || 'InfoFilled'
}

// ============ 统计数据 ============
const statsLoading = ref(false)
const stats = ref({})

async function fetchStats() {
  statsLoading.value = true
  try {
    const res = await achievementApi.stats()
    stats.value = res.data || {}
  } catch (e) {
    // 静默处理
  } finally {
    statsLoading.value = false
  }
}

// ============ 学习排行榜 ============
const leaderboardLoading = ref(false)
const leaderboard = ref([])

async function fetchLeaderboard() {
  leaderboardLoading.value = true
  try {
    const res = await achievementApi.leaderboard()
    leaderboard.value = res.data || []
  } catch (e) {
    // 静默处理
  } finally {
    leaderboardLoading.value = false
  }
}

// ============ 帖子列表 ============
const loading = ref(false)
const posts = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filterStatus = ref('')
const likedMap = ref({})

async function fetchPosts() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterStatus.value) params.audit_status = filterStatus.value
    const res = await achievementApi.posts(params)
    posts.value = res.data || []
    total.value = res.total || 0
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  page.value = 1
  fetchPosts()
}

function handleSizeChange() {
  page.value = 1
  fetchPosts()
}

// ============ 点赞 ============
function postLiked(post) {
  return likedMap.value[post.id] || post.liked || false
}

async function handleLike(post) {
  try {
    const res = await achievementApi.like(post.id)
    const liked = res.data?.liked ?? !postLiked(post)
    const count = res.data?.like_count
    likedMap.value[post.id] = liked
    if (typeof count === 'number') {
      post.like_count = count
    } else {
      post.like_count = (post.like_count || 0) + (liked ? 1 : -1)
    }
  } catch (e) {
    // 错误已由拦截器处理
  }
}

// ============ 删除帖子 ============
async function handleDelete(post) {
  try {
    await ElMessageBox.confirm('确定删除这条成果吗？', '提示', { type: 'warning' })
    await achievementApi.deletePost(post.id)
    ElMessage.success('删除成功')
    fetchPosts()
    fetchStats()
  } catch (e) {
    // 取消或错误
  }
}

// ============ 评论 ============
const expandedPost = ref(null)
const commentLoading = ref(false)
const comments = ref([])
const commentText = ref('')
const commentSubmitting = ref(false)
const replyTo = ref(null)

function setReplyTo(post, comment) {
  replyTo.value = comment
  commentText.value = ''
}

function cancelReply() {
  replyTo.value = null
}

function getReplyTarget(parentId) {
  return comments.value.find((c) => c.id === parentId)
}

async function toggleComments(post) {
  if (expandedPost.value === post.id) {
    expandedPost.value = null
    return
  }
  expandedPost.value = post.id
  commentText.value = ''
  replyTo.value = null
  await fetchComments(post.id)
}

async function fetchComments(postId) {
  commentLoading.value = true
  try {
    const res = await achievementApi.comments(postId)
    comments.value = res.data || []
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    commentLoading.value = false
  }
}

async function submitComment(post) {
  if (!commentText.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  commentSubmitting.value = true
  try {
    const payload = { content: commentText.value }
    if (replyTo.value) {
      payload.parent_id = replyTo.value.id
    }
    const res = await achievementApi.addComment(post.id, payload)
    comments.value.push(res.data)
    post.comment_count = (post.comment_count || 0) + 1
    commentText.value = ''
    const wasReply = !!replyTo.value
    replyTo.value = null
    ElMessage.success(wasReply ? '回复成功' : '评论成功')
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    commentSubmitting.value = false
  }
}

function commentInitial(c) {
  return c.is_teacher ? '师' : String(c.user_id || '').charAt(0) || 'U'
}

// ============ 发布帖子 ============
const postDialogVisible = ref(false)
const postSubmitting = ref(false)
const postFormRef = ref()
const postForm = reactive({ achievement_type: '学习打卡', content: '', images: '', tags: '', is_anonymous: false })
const postRules = {
  achievement_type: [{ required: true, message: '请选择成果类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入成果内容', trigger: 'blur' }],
}

const previewImages = computed(() => parseImages(postForm.images))

function openPostDialog() {
  postForm.achievement_type = '学习打卡'
  postForm.content = ''
  postForm.images = ''
  postForm.tags = ''
  postForm.is_anonymous = false
  postDialogVisible.value = true
}

async function submitPost() {
  await postFormRef.value.validate(async (valid) => {
    if (!valid) return
    postSubmitting.value = true
    try {
      // 将成果类型作为第一个标签
      const allTags = [postForm.achievement_type, postForm.tags].filter(Boolean).join(',')
      await achievementApi.createPost({
        content: postForm.content,
        images: postForm.images,
        tags: allTags,
        is_anonymous: postForm.is_anonymous,
      })
      ElMessage.success('发布成功，等待审核')
      postDialogVisible.value = false
      page.value = 1
      fetchPosts()
      fetchStats()
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      postSubmitting.value = false
    }
  })
}

// ============ 消息通知（保留接口，但不在页面展示） ============
const msgDetailVisible = ref(false)
const msgDetailLoading = ref(false)
const msgDetail = reactive({ title: '', data: null })

const roleLabelMap = {
  student: '学生',
  teacher: '教师',
  auditor: '审核员',
  admin: '管理员',
}

function msgTagType(type) {
  const map = { comment: '', like: 'danger', audit: 'success', system: 'info' }
  return map[type] || 'info'
}

function msgTypeLabel(type) {
  const map = { comment: '评论通知', like: '点赞通知', audit: '审核通知', system: '系统通知' }
  return map[type] || '通知'
}

function goToPost(postId) {
  msgDetailVisible.value = false
  fetchPosts().then(() => {
    nextTick(() => {
      const el = document.querySelector(`[data-post-id="${postId}"]`)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        el.classList.add('highlight-post')
        setTimeout(() => el.classList.remove('highlight-post'), 2000)
      }
    })
  })
}

// ============ 工具函数 ============
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

function auditLabel(status) {
  const map = { approved: '已通过', pending: '审核中', rejected: '已驳回' }
  return map[status] || status || '未知'
}

function auditTagType(status) {
  const map = { approved: 'success', pending: 'warning', rejected: 'danger' }
  return map[status] || 'info'
}

// ============ 用户主页跳转 ============
function getAvatarUrl(avatar) {
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  const base = import.meta.env.VITE_API_BASE_URL.replace('/api', '')
  return base + avatar
}

function goToUserProfile(post) {
  if (!post.user_id || post.is_anonymous) {
    console.warn('[Achievement] Cannot navigate: user_id missing or anonymous', post)
    return
  }
  // 始终跳转到用户主页，即使是自己的帖子也展示主页内容
  console.log('[Achievement] Navigating to user profile:', `/user/${post.user_id}`, 'post user_id:', post.user_id, 'current user:', authStore.user?.id)
  router.push(`/user/${post.user_id}`)
}

function goToUserProfileById(userId) {
  if (!userId) return
  router.push(`/user/${userId}`)
}

onMounted(() => {
  fetchPosts()
  fetchStats()
  fetchLeaderboard()
})
</script>

<style scoped>
.achievement-page {
  padding: 20px;
}

/* ---------- 统计概览 ---------- */
.stats-overview {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 120px;
  padding: 16px 20px;
  border-radius: 10px;
  text-align: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-blue { background: linear-gradient(135deg, #ecf5ff, #d9ecff); }
.stat-red { background: linear-gradient(135deg, #fef0f0, #fde2e2); }
.stat-green { background: linear-gradient(135deg, #f0f9eb, #e1f3d8); }
.stat-orange { background: linear-gradient(135deg, #fdf6ec, #faecd8); }
.stat-purple { background: linear-gradient(135deg, #f4f4f5, #e9e9eb); }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-blue .stat-value { color: #409eff; }
.stat-red .stat-value { color: #f56c6c; }
.stat-green .stat-value { color: #67c23a; }
.stat-orange .stat-value { color: #e6a23c; }
.stat-purple .stat-value { color: #6c5ce7; }

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* ---------- 帖子作者 ---------- */
.post-author {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.post-author:hover {
  background: #f5f7fa;
}

.post-author-avatar {
  background: #409eff;
  color: #fff;
  flex-shrink: 0;
}

.post-author-info {
  flex: 1;
}

.post-author-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.post-author-time {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* ---------- 成果类型徽章 ---------- */
.achievement-type-badge {
  margin-bottom: 10px;
}

.type-icon {
  margin-right: 2px;
  vertical-align: -2px;
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

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.card-header span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.list-card,
.leaderboard-card,
.my-stats-card {
  margin-bottom: 16px;
}

.post-list {
  min-height: 200px;
}

.post-item {
  margin-bottom: 16px;
}

.post-content {
  margin-bottom: 12px;
}

.post-text {
  font-size: 15px;
  line-height: 1.7;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
}

.post-images {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.post-image {
  width: 120px;
  height: 120px;
  border-radius: 6px;
  cursor: pointer;
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.post-tag {
  margin: 0;
}

.post-author-anonymous {
  cursor: default;
}

.post-author-anonymous:hover {
  background: transparent;
}

.post-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #909399;
  font-size: 13px;
  padding: 8px 0;
  border-top: 1px dashed #ebeef5;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-section {
  margin-top: 8px;
}

.comment-list {
  min-height: 40px;
}

.comment-item {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px dashed #f0f0f0;
}

.comment-avatar {
  background: #409eff;
  color: #fff;
  flex-shrink: 0;
}

.comment-body {
  flex: 1;
}

.comment-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.comment-user {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.comment-time {
  font-size: 12px;
  color: #c0c4cc;
  margin-left: auto;
}

.comment-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.comment-reply-item {
  margin-left: 42px;
}

.reply-to {
  color: #409eff;
  font-weight: 600;
}

.comment-reply-btn {
  font-size: 12px;
  color: #909399;
  cursor: pointer;
  margin-top: 4px;
  display: inline-block;
  transition: color 0.2s;
}

.comment-reply-btn:hover {
  color: #409eff;
}

.reply-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: #ecf5ff;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #409eff;
}

.comment-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
  align-items: flex-end;
}

.comment-input .el-input {
  width: 100%;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

/* ---------- 学习排行榜 ---------- */
.leaderboard-list {
  min-height: 120px;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}

.leaderboard-item:hover {
  background: #f5f7fa;
}

.leaderboard-me {
  background: #ecf5ff;
}

.leaderboard-me:hover {
  background: #d9ecff;
}

.rank-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #909399;
  background: #f0f0f0;
  flex-shrink: 0;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffb700);
  color: #fff;
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #a8a8a8);
  color: #fff;
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #b8722d);
  color: #fff;
}

.leaderboard-avatar {
  background: #6c5ce7;
  color: #fff;
  flex-shrink: 0;
}

.leaderboard-info {
  flex: 1;
  min-width: 0;
}

.leaderboard-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.leaderboard-stats {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.lb-stat {
  display: inline;
}

.lb-stat-divider {
  margin: 0 4px;
  color: #dcdfe6;
}

/* ---------- 我的成果概览 ---------- */
.my-stats-body {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 8px 0;
}

.my-stat-item {
  text-align: center;
}

.my-stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #409eff;
}

.my-stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.my-stat-divider {
  width: 1px;
  height: 40px;
  background: #ebeef5;
}

/* ---------- 消息详情对话框 ---------- */
.msg-detail-body {
  min-height: 120px;
}

.msg-detail-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.msg-detail-time {
  font-size: 12px;
  color: #c0c4cc;
}

.msg-detail-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.7;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.msg-detail-sender {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.msg-detail-avatar {
  background: #409eff;
  color: #fff;
  flex-shrink: 0;
}

.msg-detail-sender-info {
  flex: 1;
}

.msg-detail-sender-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.msg-detail-post {
  padding: 14px;
  background: #f9fafc;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-top: 16px;
}

.msg-detail-post-title {
  font-size: 12px;
  font-weight: 600;
  color: #909399;
  margin-bottom: 8px;
}

.msg-detail-post-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  margin-bottom: 10px;
  max-height: 120px;
  overflow-y: auto;
}

.msg-detail-post-meta {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.msg-detail-footer {
  margin-top: 20px;
  text-align: center;
}

.highlight-post {
  animation: highlight-flash 2s ease;
}

@keyframes highlight-flash {
  0%, 100% { box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06); }
  25%, 75% { box-shadow: 0 0 0 3px #409eff; }
}

.dialog-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.preview-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
}
</style>
