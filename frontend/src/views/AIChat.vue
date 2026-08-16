<template>
  <div class="chat-page">
    <div class="chat-header-bar">
      <div class="chat-header-left">
        <div class="chat-header-icon">
          <el-icon :size="24"><ChatLineRound /></el-icon>
        </div>
        <div>
          <h2>AI 智能问答</h2>
          <p>有问题随时问，AI 学习助手为你解答</p>
        </div>
      </div>
      <el-button :icon="Delete" @click="clearHistory" text>清空记录</el-button>
    </div>

    <!-- 消息区域 -->
    <div class="chat-messages-area" ref="messagesRef">
      <!-- 欢迎语 -->
      <div v-if="messages.length === 0" class="welcome-section">
        <div class="welcome-icon">
          <el-icon :size="48"><ChatLineRound /></el-icon>
        </div>
        <h3>你好，{{ authStore.nickname }}！</h3>
        <p>我是绵城AI学习助手，可以帮你解答学习中的各种问题</p>
        <div class="quick-questions">
          <div class="quick-label">试试问我：</div>
          <div class="quick-tags">
            <el-tag
              v-for="q in quickQuestions"
              :key="q"
              class="quick-tag"
              effect="plain"
              @click="useQuickQuestion(q)"
            >{{ q }}</el-tag>
          </div>
        </div>
        <div class="feature-tips">
          <div class="feature-tip" @click="triggerImageUpload">
            <el-icon><Camera /></el-icon>
            <span>拍照解答</span>
          </div>
          <div class="feature-tip" @click="toggleVoice">
            <el-icon><Microphone /></el-icon>
            <span>语音输入</span>
          </div>
        </div>
      </div>

      <!-- 对话消息 -->
      <div v-for="(msg, idx) in messages" :key="idx" class="msg-block" :class="msg.role">
        <div class="msg-avatar">
          <el-avatar :size="36" :class="msg.role === 'user' ? 'avatar-user' : 'avatar-ai'">
            <el-icon v-if="msg.role === 'ai'"><ChatLineRound /></el-icon>
            <span v-else>{{ authStore.nickname?.charAt(0) }}</span>
          </el-avatar>
        </div>
        <div class="msg-content">
          <div class="msg-role">{{ msg.role === 'user' ? '我' : 'AI 助手' }}</div>
          <!-- 图片消息 -->
          <div v-if="msg.image" class="msg-image-wrap">
            <el-image :src="msg.image" :preview-src-list="[msg.image]" fit="cover" class="msg-image" preview-teleported />
            <div v-if="msg.content" class="msg-text" v-html="renderMarkdown(msg.content)"></div>
          </div>
          <!-- 纯文本消息 -->
          <div v-else class="msg-text" v-html="renderMarkdown(msg.content)"></div>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="msg-block ai">
        <div class="msg-avatar">
          <el-avatar :size="36" class="avatar-ai">
            <el-icon><ChatLineRound /></el-icon>
          </el-avatar>
        </div>
        <div class="msg-content">
          <div class="msg-role">AI 助手</div>
          <div class="msg-loading">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
            正在思考中...
          </div>
        </div>
      </div>
    </div>

    <!-- 图片预览区 -->
    <div v-if="pendingImage" class="image-preview-bar">
      <div class="image-preview-item">
        <img :src="pendingImage" class="preview-thumb" />
        <el-button :icon="Close" circle size="small" class="remove-image-btn" @click="removePendingImage" />
      </div>
      <span class="preview-hint">已选择图片，点击发送让 AI 识别解答</span>
    </div>

    <!-- 语音状态提示 -->
    <div v-if="voiceListening" class="voice-status-bar">
      <div class="voice-pulse"></div>
      <span>正在聆听... {{ voiceText || '请说话' }}</span>
      <el-button size="small" type="danger" @click="stopVoice">停止</el-button>
    </div>

    <!-- 输入区 -->
    <div class="chat-input-bar">
      <div class="input-actions">
        <el-tooltip content="拍照/上传图片" placement="top">
          <el-button :icon="Camera" circle @click="triggerImageUpload" :disabled="loading" />
        </el-tooltip>
        <el-tooltip :content="voiceListening ? '停止录音' : '语音输入'" placement="top">
          <el-button
            :icon="Microphone"
            circle
            :type="voiceListening ? 'danger' : 'default'"
            @click="toggleVoice"
            :disabled="!voiceSupported || loading"
          />
        </el-tooltip>
      </div>
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        :placeholder="voiceListening ? '正在聆听...' : '输入你的问题，按回车发送...'"
        maxlength="1000"
        @keydown.enter.exact.prevent="sendQuestion"
      />
      <el-button
        type="primary"
        :loading="loading"
        :disabled="!canSend"
        @click="sendQuestion"
        :icon="Position"
      >
        发送
      </el-button>
    </div>

    <!-- 隐藏的文件选择器 -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      capture="environment"
      style="display: none"
      @change="handleImageSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatLineRound, Position, Delete, Camera, Microphone, Close } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { aiChatApi } from '@/api'

const authStore = useAuthStore()

const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const messagesRef = ref(null)
const fileInputRef = ref(null)
const pendingImage = ref(null)
const pendingImageFile = ref(null)

const quickQuestions = [
  '如何高效学习编程？',
  'Vue3 和 React 有什么区别？',
  '考研政治怎么复习？',
  '推荐一些 Python 学习资源',
  '如何提高英语口语？',
]

// ============ 语音识别 ============
const voiceListening = ref(false)
const voiceText = ref('')
const voiceSupported = ref(false)
let recognition = null
let intentionalStop = false  // 标记是否用户主动停止
let restartTimer = null

onMounted(() => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (SR && window.isSecureContext) {
    voiceSupported.value = true
    recognition = new SR()
    recognition.lang = 'zh-CN'
    recognition.continuous = true
    recognition.interimResults = true

    recognition.onresult = (event) => {
      let finalText = ''
      let interimText = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalText += transcript
        } else {
          interimText += transcript
        }
      }
      voiceText.value = interimText
      if (finalText) {
        inputText.value += finalText
      }
    }

    recognition.onerror = (event) => {
      // 'no-speech' 和 'aborted' 是正常情况，不需要停止
      // 'network' 错误时也尝试重启
      const restartableErrors = ['no-speech', 'aborted', 'network']
      const fatalErrors = ['not-allowed', 'service-not-allowed', 'audio-capture']

      if (fatalErrors.includes(event.error)) {
        if (voiceListening.value) {
          ElMessage.error('语音识别不可用: ' + event.error + '，请检查麦克风权限')
        }
        intentionalStop = true
        voiceListening.value = false
        return
      }

      // 可恢复的错误不设置 intentionalStop，让 onend 自动重启
      if (!restartableErrors.includes(event.error) && voiceListening.value) {
        console.warn('语音识别错误:', event.error)
      }
    }

    recognition.onend = () => {
      // 清除之前的重启定时器
      if (restartTimer) {
        clearTimeout(restartTimer)
        restartTimer = null
      }

      // 如果用户没有主动停止，自动重启（加延迟避免立即重启失败）
      if (!intentionalStop && voiceListening.value) {
        restartTimer = setTimeout(() => {
          if (!intentionalStop && voiceListening.value) {
            try {
              recognition.start()
            } catch (e) {
              // 如果 start 失败（可能已经在运行），再试一次
              try {
                recognition.stop()
                setTimeout(() => {
                  if (!intentionalStop && voiceListening.value) {
                    recognition.start()
                  }
                }, 200)
              } catch (e2) {
                voiceListening.value = false
              }
            }
          }
        }, 300)
      }
    }
  }
})

onUnmounted(() => {
  intentionalStop = true
  if (restartTimer) {
    clearTimeout(restartTimer)
    restartTimer = null
  }
  if (recognition && voiceListening.value) {
    recognition.stop()
  }
})

function toggleVoice() {
  if (!voiceSupported.value) {
    ElMessage.warning('当前浏览器不支持语音识别，请使用 Chrome 或 Edge 浏览器')
    return
  }
  // 检查安全上下文（语音 API 需要 localhost 或 HTTPS）
  if (!window.isSecureContext) {
    ElMessage.warning('语音识别需要 HTTPS 环境或使用 localhost 访问，当前地址可能不支持')
    return
  }
  if (voiceListening.value) {
    stopVoice()
  } else {
    startVoice()
  }
}

function startVoice() {
  if (!recognition) return
  intentionalStop = false
  try {
    recognition.start()
    voiceListening.value = true
    voiceText.value = ''
  } catch (e) {
    // 可能是重复启动，先停止再启动
    try {
      recognition.stop()
      setTimeout(() => {
        try {
          recognition.start()
          voiceListening.value = true
          voiceText.value = ''
        } catch (e2) {
          // 仍然失败，放弃
        }
      }, 200)
    } catch (e2) {
      // 忽略
    }
  }
}

function stopVoice() {
  intentionalStop = true
  if (restartTimer) {
    clearTimeout(restartTimer)
    restartTimer = null
  }
  voiceListening.value = false
  if (recognition) {
    try {
      recognition.stop()
    } catch (e) {
      // 忽略
    }
  }
}

// ============ 图片上传 ============
function triggerImageUpload() {
  fileInputRef.value?.click()
}

function handleImageSelect(event) {
  const file = event.target.files?.[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过 10MB')
    return
  }

  pendingImageFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    pendingImage.value = e.target.result
  }
  reader.readAsDataURL(file)

  // 清空 input 以便重复选择同一文件
  event.target.value = ''
}

function removePendingImage() {
  pendingImage.value = null
  pendingImageFile.value = null
}

// ============ 发送 ============
const canSend = computed(() => {
  return inputText.value.trim() || pendingImage.value
})

function useQuickQuestion(q) {
  inputText.value = q
  sendQuestion()
}

async function sendQuestion() {
  if (!canSend.value || loading.value) return

  loading.value = true
  const question = inputText.value.trim() || '请解答图片中的问题'

  if (pendingImage.value) {
    // 图片问答
    messages.value.push({
      role: 'user',
      content: question,
      image: pendingImage.value,
    })

    const imageData = pendingImage.value
    const imageFile = pendingImageFile.value
    inputText.value = ''
    removePendingImage()

    await nextTick()
    scrollToBottom()

    try {
      const formData = new FormData()
      formData.append('image', imageFile)
      formData.append('question', question)
      const res = await aiChatApi.askWithImage(formData)
      if (res.data) {
        messages.value.push({ role: 'ai', content: res.data.answer })
      }
    } catch (e) {
      messages.value.push({
        role: 'ai',
        content: '抱歉，图片识别出了一些问题，请稍后再试。',
      })
    } finally {
      loading.value = false
      await nextTick()
      scrollToBottom()
    }
  } else {
    // 文字问答
    messages.value.push({ role: 'user', content: question })
    inputText.value = ''

    await nextTick()
    scrollToBottom()

    try {
      const res = await aiChatApi.ask({ question })
      if (res.data) {
        messages.value.push({ role: 'ai', content: res.data.answer })
      }
    } catch (e) {
      messages.value.push({
        role: 'ai',
        content: '抱歉，出了一些问题，请稍后再试。',
      })
    } finally {
      loading.value = false
      await nextTick()
      scrollToBottom()
    }
  }
}

function clearHistory() {
  messages.value = []
}

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

// 简单 Markdown 渲染
function renderMarkdown(text) {
  if (!text) return ''
  let html = text
  // 代码块
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre class="md-code"><code>$2</code></pre>')
  // 行内代码
  html = html.replace(/`([^`]+)`/g, '<code class="md-inline-code">$1</code>')
  // 加粗
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  // 标题
  html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>')
  // 列表
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
  html = html.replace(/^[-*] (.+)$/gm, '<li>$1</li>')
  // 换行
  html = html.replace(/\n/g, '<br>')
  // 修复嵌套
  html = html.replace(/<li>(.*?)<\/li>(<br>)?(?=<li>|$)/g, '<li>$1</li>')
  return html
}
</script>

<style scoped>
.chat-page {
  padding: 20px;
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  max-width: 900px;
  margin: 0 auto;
}

.chat-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.chat-header-icon {
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

.chat-header-bar h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.chat-header-bar p {
  margin: 2px 0 0;
  font-size: 13px;
  color: #909399;
}

/* ---------- 消息区 ---------- */
.chat-messages-area {
  flex: 1;
  overflow-y: auto;
  background: #f5f7fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 8px;
}

/* ---------- 欢迎语 ---------- */
.welcome-section {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.welcome-section h3 {
  font-size: 22px;
  color: #303133;
  margin-bottom: 8px;
}

.welcome-section p {
  color: #909399;
  font-size: 14px;
  margin-bottom: 24px;
}

.quick-questions {
  max-width: 500px;
  margin: 0 auto;
}

.quick-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.quick-tag {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.quick-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.feature-tips {
  display: flex;
  gap: 24px;
  justify-content: center;
  margin-top: 28px;
}

.feature-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  font-size: 13px;
  color: #606266;
}

.feature-tip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
  color: #667eea;
}

/* ---------- 消息块 ---------- */
.msg-block {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.msg-block.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
}

.avatar-user {
  background: #409eff;
  color: #fff;
}

.avatar-ai {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.msg-content {
  max-width: 75%;
}

.msg-role {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.msg-block.user .msg-role {
  text-align: right;
}

.msg-text {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
}

.msg-block.ai .msg-text {
  background: #fff;
  color: #303133;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.msg-block.user .msg-text {
  background: #409eff;
  color: #fff;
}

.msg-text :deep(.md-code) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 13px;
  margin: 8px 0;
}

.msg-text :deep(.md-inline-code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.msg-block.user .msg-text :deep(.md-inline-code) {
  background: rgba(255, 255, 255, 0.2);
}

.msg-text :deep(h2),
.msg-text :deep(h3),
.msg-text :deep(h4) {
  margin: 8px 0 4px;
}

.msg-text :deep(li) {
  margin: 4px 0;
}

/* ---------- 图片消息 ---------- */
.msg-image-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.msg-image {
  max-width: 280px;
  max-height: 280px;
  border-radius: 12px;
  border: 2px solid #e4e7ed;
}

/* ---------- 加载中 ---------- */
.msg-loading {
  padding: 12px 16px;
  background: #fff;
  border-radius: 12px;
  font-size: 14px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c0c4cc;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* ---------- 图片预览栏 ---------- */
.image-preview-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f0f2f5;
  border-radius: 8px;
  margin-bottom: 8px;
}

.image-preview-item {
  position: relative;
  flex-shrink: 0;
}

.preview-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
}

.remove-image-btn {
  position: absolute;
  top: -6px;
  right: -6px;
}

.preview-hint {
  font-size: 13px;
  color: #909399;
}

/* ---------- 语音状态栏 ---------- */
.voice-status-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: #fef0f0;
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #f56c6c;
}

.voice-pulse {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #f56c6c;
  animation: pulse 1.2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 0.4; }
  100% { transform: scale(0.8); opacity: 0.8; }
}

/* ---------- 输入区 ---------- */
.chat-input-bar {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.chat-input-bar .el-input {
  flex: 1;
}
</style>
