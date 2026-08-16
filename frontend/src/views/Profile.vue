<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人中心</h2>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：用户信息卡片 -->
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="profile-card">
          <div class="profile-avatar">
            <!-- 头像圆形底色容器 -->
            <div class="avatar-container">
              <div class="avatar-wrapper" @click="triggerFileInput">
                <el-avatar :size="100" :src="getAvatarUrl(user.avatar)">
                  {{ (user.nickname || 'U').charAt(0) }}
                </el-avatar>
                <div class="avatar-overlay">
                  <el-icon><Camera /></el-icon>
                  <span>换头像</span>
                </div>
              </div>
            </div>
            <h3 class="profile-name">{{ user.nickname || '未设置' }}</h3>
            <!-- 优化审核员角色标签配色 -->
            <el-tag :type="roleTagType" effect="dark" size="default" round>{{ roleLabel }}</el-tag>

            <!-- 审核员专属快捷入口 -->
            <div v-if="authStore.role === 'auditor'" class="auditor-shortcut">
              <el-button type="primary" @click="goToAuditCenter" round>
                <el-icon><Checked /></el-icon>
                前往审核中心
              </el-button>
            </div>
          </div>

          <!-- 隐藏的文件选择（仅相册选择，移除拍照） -->
          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            style="display:none"
            @change="handleAvatarChange"
          />

          <el-divider />

          <!-- 账号信息：标签+值对齐排版 -->
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">账号</span>
              <span class="info-value">{{ user.username || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">角色</span>
              <span class="info-value">{{ roleLabel }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">认证状态</span>
              <span class="info-value">
                <el-tag :type="certTagType" size="small" effect="light" round>{{ certLabel }}</el-tag>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">注册时间</span>
              <span class="info-value">{{ formatTime(user.created_at) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：编辑 & 认证 & 安全 -->
      <el-col :xs="24" :md="16">
        <!-- 编辑资料 -->
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span>✏️ 编辑资料</span>
            </div>
          </template>
          <el-form ref="profileFormRef" :model="profileForm" :rules="profileRules" label-width="90px">
            <!-- 昵称：仅学生和教师可改，管理员和审核员不可改 -->
            <el-form-item v-if="canEditNickname" label="昵称" prop="nickname">
              <el-input v-model="profileForm.nickname" placeholder="请输入昵称" maxlength="30" show-word-limit />
            </el-form-item>
            <el-form-item v-else label="昵称">
              <el-input :value="user.nickname" disabled />
              <div class="field-hint">管理员/审核员昵称不可修改</div>
            </el-form-item>

            <!-- 头像选择（PC端仅保留从相册选择） -->
            <el-form-item label="头像">
              <div class="avatar-edit-area">
                <el-avatar :size="64" :src="getAvatarUrl(user.avatar)">
                  {{ (user.nickname || 'U').charAt(0) }}
                </el-avatar>
                <div class="avatar-buttons">
                  <el-button @click="triggerFileInput">
                    <el-icon><Picture /></el-icon>
                    从相册选择
                  </el-button>
                </div>
              </div>
            </el-form-item>

            <el-form-item v-if="canEditNickname">
              <el-button type="primary" :loading="profileSubmitting" @click="submitProfile">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 教师认证 -->
        <el-card v-if="authStore.isTeacher" shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span>🧑 教师实名认证</span>
              <el-tag :type="certTagType" size="small" effect="light" round>{{ certLabel }}</el-tag>
            </div>
          </template>

          <el-alert
            v-if="user.cert_status === 'pending'"
            title="您的认证申请正在审核中，请耐心等待。"
            type="warning"
            :closable="false"
            show-icon
            class="cert-alert"
          />
          <el-alert
            v-else-if="user.cert_status === 'approved'"
            title="您已完成教师实名认证。"
            type="success"
            :closable="false"
            show-icon
            class="cert-alert"
          />
          <el-alert
            v-else-if="user.cert_status === 'rejected'"
            :title="`认证未通过：${user.cert_reason || '请重新提交申请'}`"
            type="error"
            :closable="false"
            show-icon
            class="cert-alert"
          />

          <el-form
            v-if="user.cert_status !== 'approved' && user.cert_status !== 'pending'"
            ref="certFormRef"
            :model="certForm"
            :rules="certRules"
            label-width="100px"
          >
            <el-form-item label="真实姓名" prop="real_name">
              <el-input v-model="certForm.real_name" placeholder="请输入真实姓名" maxlength="20" />
            </el-form-item>
            <el-form-item label="教职工号" prop="employee_id">
              <el-input v-model="certForm.employee_id" placeholder="请输入教职工号" maxlength="30" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="certSubmitting" @click="submitCert">提交认证</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 账号安全 -->
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span>🔒 账号安全</span>
            </div>
          </template>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">账号状态</span>
              <span class="info-value">
                <el-tag
                  :type="user.status === 'disabled' ? 'danger' : 'success'"
                  size="small"
                  effect="light"
                  round
                >
                  {{ user.status === 'disabled' ? '已禁用' : '正常' }}
                </el-tag>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">最后登录</span>
              <span class="info-value">{{ formatTime(user.last_login_at) || '暂未记录登录信息' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">密码安全</span>
              <span class="info-value">
                <el-button type="primary" text @click="openPasswordDialog">修改密码</el-button>
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 头像预览裁剪对话框 -->
    <el-dialog v-model="avatarDialogVisible" title="预览头像" width="400px" :close-on-click-modal="false">
      <div class="avatar-preview">
        <img :src="avatarTempUrl" alt="头像预览" class="preview-img" />
      </div>
      <template #footer>
        <el-button @click="cancelAvatarUpload">取消</el-button>
        <el-button type="primary" :loading="avatarUploading" @click="confirmAvatarUpload">确认上传</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="440px" :close-on-click-modal="false">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-position="top">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码（至少6位）" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordSubmitting" @click="submitPasswordChange">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Camera, Picture, Checked } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user || {})

const roleLabel = computed(() => {
  const map = { student: '学生', teacher: '教师', auditor: '审核员', admin: '管理员' }
  return map[authStore.role] || '未知'
})

// 优化审核员角色标签配色：取消刺眼红色，改用 primary
const roleTagType = computed(() => {
  const map = { student: 'success', teacher: 'warning', auditor: 'primary', admin: '' }
  return map[authStore.role] || 'info'
})

// 管理员和审核员不能改昵称
const canEditNickname = computed(() => {
  return authStore.role === 'student' || authStore.role === 'teacher'
})

const certLabel = computed(() => {
  const map = { pending: '审核中', approved: '已认证', rejected: '未通过', none: '未认证' }
  return map[user.value.cert_status] || '未认证'
})

const certTagType = computed(() => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger', none: 'info' }
  return map[user.value.cert_status] || 'info'
})

// 前往审核中心
function goToAuditCenter() {
  router.push('/audit')
}

// ============ 头像上传 ============
const fileInputRef = ref()
const avatarDialogVisible = ref(false)
const avatarUploading = ref(false)
const avatarTempUrl = ref('')
const avatarFile = ref(null)

function getAvatarUrl(avatar) {
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  const base = import.meta.env.VITE_API_BASE_URL.replace('/api', '')
  return base + avatar
}

function triggerFileInput() {
  fileInputRef.value.click()
}

function handleAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }

  avatarFile.value = file
  avatarTempUrl.value = URL.createObjectURL(file)
  avatarDialogVisible.value = true

  e.target.value = ''
}

function cancelAvatarUpload() {
  avatarDialogVisible.value = false
  avatarFile.value = null
  avatarTempUrl.value = ''
}

async function confirmAvatarUpload() {
  if (!avatarFile.value) return
  avatarUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', avatarFile.value)
    const res = await authApi.uploadAvatar(formData)
    await authApi.updateMe({ avatar: res.data.avatar })
    await authStore.fetchMe()
    ElMessage.success('头像更新成功')
    avatarDialogVisible.value = false
    avatarFile.value = null
    avatarTempUrl.value = ''
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    avatarUploading.value = false
  }
}

// ============ 编辑资料 ============
const profileFormRef = ref()
const profileSubmitting = ref(false)
const profileForm = reactive({ nickname: '', avatar: '' })
const originalNickname = ref('')
const profileRules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
}

function fillProfileForm() {
  profileForm.nickname = user.value.nickname || ''
  profileForm.avatar = user.value.avatar || ''
  originalNickname.value = user.value.nickname || ''
}

async function submitProfile() {
  await profileFormRef.value.validate(async (valid) => {
    if (!valid) return
    // 未修改内容拦截提示
    if (profileForm.nickname === originalNickname.value) {
      ElMessage.info('昵称未修改，无需保存')
      return
    }
    profileSubmitting.value = true
    try {
      await authApi.updateMe({ nickname: profileForm.nickname })
      await authStore.fetchMe()
      originalNickname.value = profileForm.nickname
      ElMessage.success('资料保存成功')
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      profileSubmitting.value = false
    }
  })
}

// ============ 教师认证 ============
const certFormRef = ref()
const certSubmitting = ref(false)
const certForm = reactive({ real_name: '', employee_id: '' })
const certRules = {
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  employee_id: [{ required: true, message: '请输入教职工号', trigger: 'blur' }],
}

async function submitCert() {
  await certFormRef.value.validate(async (valid) => {
    if (!valid) return
    certSubmitting.value = true
    try {
      await authApi.teacherCert({ ...certForm })
      await authStore.fetchMe()
      ElMessage.success('认证申请已提交，请等待审核')
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      certSubmitting.value = false
    }
  })
}

// ============ 修改密码 ============
const passwordDialogVisible = ref(false)
const passwordSubmitting = ref(false)
const passwordFormRef = ref()
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度 6-100 位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

function openPasswordDialog() {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordDialogVisible.value = true
}

async function submitPasswordChange() {
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    passwordSubmitting.value = true
    try {
      await authApi.changePassword({
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password,
      })
      ElMessage.success('密码修改成功')
      passwordDialogVisible.value = false
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      passwordSubmitting.value = false
    }
  })
}

// ============ 工具函数 ============
function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function pad(n) {
  return String(n).padStart(2, '0')
}

onMounted(async () => {
  fillProfileForm()
  try {
    await authStore.fetchMe()
    fillProfileForm()
  } catch (e) {
    // 静默处理
  }
})
</script>

<style scoped>
.profile-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

/* ---------- 统一卡片样式 ---------- */
.profile-card,
.section-card {
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
  border: none;
}

.profile-card {
  text-align: center;
}

/* ---------- 头像区域 ---------- */
.profile-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px 0;
}

/* 头像圆形底色 */
.avatar-container {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f7ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
  width: 100px;
  height: 100px;
}

.avatar-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-size: 12px;
  padding: 4px 0;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.profile-name {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

/* ---------- 审核员快捷入口 ---------- */
.auditor-shortcut {
  margin-top: 8px;
  width: 100%;
  display: flex;
  justify-content: center;
}

/* ---------- 信息标签+值对齐排版 ---------- */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 0 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  color: #909399;
  font-size: 13px;
  flex-shrink: 0;
  min-width: 70px;
}

.info-value {
  color: #303133;
  font-weight: 500;
  font-size: 14px;
  word-break: break-all;
}

/* ---------- 板块标题 ---------- */
.section-card {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  font-size: 15px;
}

/* ---------- 编辑资料区域 ---------- */
.avatar-edit-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 昵称限制提示：浅灰色，输入框下方 */
.field-hint {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
  line-height: 1.5;
}

.cert-alert {
  margin-bottom: 16px;
}

/* ---------- 头像预览 ---------- */
.avatar-preview {
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-img {
  max-width: 300px;
  max-height: 300px;
  border-radius: 50%;
  object-fit: cover;
}

/* ---------- 响应式 ---------- */
@media (max-width: 768px) {
  .info-label {
    min-width: 60px;
  }
}
</style>
