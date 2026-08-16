<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>绵城AI学习集市</h1>
        <p>个人成长学习平台 · AI驱动的智能学习管家</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs" stretch>
        <!-- 登录 -->
        <el-tab-pane label="登录" name="login">
          <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-position="top" size="large">
            <el-form-item label="账号" prop="username">
              <el-input v-model="loginForm.username" placeholder="请输入用户名" :prefix-icon="User" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
            </el-form-item>
            <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleLogin">
              登 录
            </el-button>
          </el-form>

          <div class="quick-login">
            <p class="quick-title">快速登录（密码均为 123456）</p>
            <div class="quick-buttons">
              <el-button size="small" @click="quickLogin('admin')">管理员</el-button>
              <el-button size="small" @click="quickLogin('auditor01')">审核员</el-button>
              <el-button size="small" @click="quickLogin('teacher01')">教师</el-button>
              <el-button size="small" @click="quickLogin('student01')">学生</el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 注册 -->
        <el-tab-pane label="注册" name="register">
          <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-position="top" size="large">
            <el-form-item label="账号" prop="username">
              <el-input v-model="registerForm.username" placeholder="3-50个字符" :prefix-icon="User" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="registerForm.password" type="password" placeholder="至少6位" :prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="registerForm.nickname" placeholder="给自己起个昵称" :prefix-icon="EditPen" />
            </el-form-item>
            <el-form-item label="真实姓名" prop="real_name">
              <el-input v-model="registerForm.real_name" placeholder="请输入真实姓名" />
            </el-form-item>
            <el-form-item label="角色" prop="role">
              <el-radio-group v-model="registerForm.role" @change="onRoleChange">
                <el-radio value="student">学生</el-radio>
                <el-radio value="teacher">教师</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 学生：学号 + 学生证 -->
            <template v-if="registerForm.role === 'student'">
              <el-form-item label="学号" prop="student_no">
                <el-input v-model="registerForm.student_no" placeholder="请输入学号" />
              </el-form-item>
              <el-form-item label="学生证照片" prop="cert_image">
                <el-upload
                  :show-file-list="false"
                  :before-upload="handleCertUpload"
                  accept="image/*"
                >
                  <el-button type="primary" plain :loading="certUploading">
                    <el-icon><Upload /></el-icon> 上传学生证
                  </el-button>
                </el-upload>
                <el-image
                  v-if="registerForm.cert_image"
                  :src="registerForm.cert_image"
                  fit="cover"
                  class="cert-preview"
                />
              </el-form-item>
            </template>

            <!-- 教师：教职工号 + 教师资格证/就职证明 -->
            <template v-if="registerForm.role === 'teacher'">
              <el-form-item label="教职工号" prop="teacher_no">
                <el-input v-model="registerForm.teacher_no" placeholder="请输入教职工号" />
              </el-form-item>
              <el-form-item label="教师资格证 / 就职证明" prop="cert_image">
                <el-upload
                  :show-file-list="false"
                  :before-upload="handleCertUpload"
                  accept="image/*"
                >
                  <el-button type="primary" plain :loading="certUploading">
                    <el-icon><Upload /></el-icon> 上传资格证明
                  </el-button>
                </el-upload>
                <el-image
                  v-if="registerForm.cert_image"
                  :src="registerForm.cert_image"
                  fit="cover"
                  class="cert-preview"
                />
                <p class="cert-tip">支持上传教师资格证或就职证明，审核通过后可发布资料</p>
              </el-form-item>
            </template>

            <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleRegister">
              注 册
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, EditPen, Upload } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')
const loading = ref(false)
const certUploading = ref(false)
const loginFormRef = ref()
const registerFormRef = ref()

const loginForm = reactive({
  username: '',
  password: '',
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const registerForm = reactive({
  username: '',
  password: '',
  nickname: '',
  real_name: '',
  role: 'student',
  student_no: '',
  teacher_no: '',
  cert_image: '',
})

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '3-50个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '至少6位', trigger: 'blur' },
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  student_no: [{
    validator: (rule, value, callback) => {
      if (registerForm.role === 'student' && !value) {
        callback(new Error('请输入学号'))
      } else {
        callback()
      }
    },
    trigger: 'blur',
  }],
  teacher_no: [{
    validator: (rule, value, callback) => {
      if (registerForm.role === 'teacher' && !value) {
        callback(new Error('请输入教职工号'))
      } else {
        callback()
      }
    },
    trigger: 'blur',
  }],
  cert_image: [{
    validator: (rule, value, callback) => {
      if (!value) {
        callback(new Error('请上传资格证明图片'))
      } else {
        callback()
      }
    },
    trigger: 'change',
  }],
}

function onRoleChange() {
  registerForm.student_no = ''
  registerForm.teacher_no = ''
}

async function handleCertUpload(file) {
  certUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await authApi.uploadFile(formData)
    if (res.data?.url) {
      registerForm.cert_image = res.data.url
      ElMessage.success('上传成功')
    } else {
      ElMessage.error('上传失败')
    }
  } catch (e) {
    ElMessage.error('上传失败：' + (e.message || '未知错误'))
  } finally {
    certUploading.value = false
  }
  return false
}

async function handleLogin() {
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await authStore.login(loginForm)
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      loading.value = false
    }
  })
}

function quickLogin(username) {
  loginForm.username = username
  loginForm.password = '123456'
  handleLogin()
}

async function handleRegister() {
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const payload = {
        username: registerForm.username,
        password: registerForm.password,
        nickname: registerForm.nickname,
        role: registerForm.role,
        real_name: registerForm.real_name,
        cert_image: registerForm.cert_image,
      }
      if (registerForm.role === 'student') {
        payload.student_no = registerForm.student_no
      } else {
        payload.teacher_no = registerForm.teacher_no
      }
      const res = await authApi.register(payload)
      ElMessage.success(res.message || '注册成功，请登录')
      // 自动填充登录表单
      loginForm.username = registerForm.username
      loginForm.password = registerForm.password
      activeTab.value = 'login'
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 460px;
  background: #fff;
  border-radius: 12px;
  padding: 40px 36px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  max-height: 90vh;
  overflow-y: auto;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 26px;
  color: #303133;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: #909399;
}

.login-tabs {
  margin-top: 10px;
}

.quick-login {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px dashed #e4e7ed;
  text-align: center;
}

.quick-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
}

.quick-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.cert-preview {
  width: 100%;
  max-height: 200px;
  margin-top: 10px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.cert-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  line-height: 1.5;
}
</style>
