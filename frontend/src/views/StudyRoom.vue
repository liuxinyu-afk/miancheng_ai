<template>
  <div class="study-room-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <h2>结伴自习</h2>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="fetchRooms">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">创建房间</el-button>
      </div>
    </div>

    <!-- 自习中状态条 -->
    <el-card v-if="myStudyRoom" shadow="never" class="active-study-bar">
      <div class="active-study-info">
        <el-tag type="success" effect="dark" size="small">自习中</el-tag>
        <span class="active-study-name">{{ myStudyRoom.name }}</span>
        <span class="active-study-time">已学习 {{ studyElapsedText }}</span>
      </div>
      <el-button type="danger" size="small" :icon="VideoPause" @click="handleStopStudy">结束自习</el-button>
    </el-card>

    <div class="room-container">
      <!-- 左侧：房间列表 -->
      <div class="room-list-panel">
        <!-- 分类筛选 -->
        <div class="category-filter">
          <el-radio-group v-model="selectedCategory" size="small" @change="fetchRooms">
            <el-radio-button label="全部">全部</el-radio-button>
            <el-radio-button label="考研">考研</el-radio-button>
            <el-radio-button label="编程">编程</el-radio-button>
            <el-radio-button label="英语考试">英语</el-radio-button>
            <el-radio-button label="职业发展">职业</el-radio-button>
            <el-radio-button label="其他">其他</el-radio-button>
          </el-radio-group>
        </div>

        <div class="room-list-header">
          <el-input
            v-model="keyword"
            placeholder="搜索房间名称/标签/简介"
            :prefix-icon="Search"
            clearable
            size="small"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
        </div>

        <div class="room-list" v-loading="loading">
          <el-empty v-if="!loading && rooms.length === 0" description="暂无房间，快去创建一个吧" :image-size="50" />
          <div
            v-for="room in rooms"
            :key="room.id"
            class="room-item"
            :class="{ active: activeRoom?.id === room.id }"
            @click="selectRoom(room)"
          >
            <div class="room-item-avatar" :style="{ background: categoryColor(room.category) }">
              <el-icon :size="20"><User /></el-icon>
            </div>
            <div class="room-item-info">
              <div class="room-item-top">
                <span class="room-item-name">
                  <el-icon v-if="room.is_private" color="#e6a23c" size="12"><Lock /></el-icon>
                  {{ room.name }}
                </span>
                <span class="room-item-time" v-if="room.last_message_at">{{ formatTime(room.last_message_at) }}</span>
              </div>
              <!-- 标签行 -->
              <div class="room-item-tags" v-if="room.tags">
                <el-tag
                  v-for="tag in parseTags(room.tags)"
                  :key="tag"
                  size="small"
                  effect="plain"
                  class="room-tag"
                >#{{ tag }}</el-tag>
              </div>
              <!-- 简介行 -->
              <div class="room-item-desc" v-if="room.description">{{ room.description }}</div>
              <!-- 底部信息 -->
              <div class="room-item-bottom">
                <span class="room-item-meta">
                  <el-icon size="11"><Timer /></el-icon>
                  {{ formatTarget(room.daily_target_minutes) }}
                </span>
                <span class="room-item-meta studying" v-if="room.studying_count > 0">
                  <span class="dot-studying"></span>{{ room.studying_count }}人学习中
                </span>
                <span class="room-item-count">{{ room.current_members || 0 }}/{{ room.max_members || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：房间内容 -->
      <div class="chat-panel">
        <template v-if="activeRoom">
          <!-- 聊天头部 -->
          <div class="chat-header">
            <div class="chat-header-left">
              <h3>
                <el-icon v-if="activeRoom.is_private" color="#e6a23c" size="16"><Lock /></el-icon>
                {{ activeRoom.name }}
              </h3>
              <el-tag v-if="activeRoom.category" size="small" effect="plain" :color="categoryColor(activeRoom.category)" style="border: none; color: #fff;">{{ activeRoom.category }}</el-tag>
              <span class="chat-header-meta">{{ activeRoom.current_members || 0 }}人</span>
              <el-tag v-if="activeRoom.can_manage" size="small" type="danger" effect="plain">管理</el-tag>
            </div>
            <div class="chat-header-right">
              <el-button v-if="canManageRoom" size="small" :icon="Checked" type="warning" plain @click="openPendingDialog">
                审核
                <el-badge v-if="activeRoom.pending_count > 0" :value="activeRoom.pending_count" class="pending-badge" />
              </el-button>
              <el-button size="small" :icon="User" @click="openMembersDialog">成员</el-button>
              <el-button v-if="canEditAnnouncement" size="small" :icon="Edit" @click="openAnnouncementDialog">公告</el-button>
              <el-button v-if="activeRoom.is_member && !activeRoom.can_manage" size="small" type="warning" plain @click="handleLeave">离开</el-button>
              <el-button v-if="activeRoom.can_manage" size="small" type="danger" plain :icon="CircleClose" @click="handleCloseRoom">关闭</el-button>
            </div>
          </div>

          <!-- 房间公告 -->
          <div v-if="activeRoom.announcement" class="room-announcement-bar">
            <el-icon color="#e6a23c"><Bell /></el-icon>
            <span>{{ activeRoom.announcement }}</span>
          </div>

          <!-- 房间统计条 -->
          <div class="room-stats-bar">
            <span class="stat-item">
              <el-icon size="12"><User /></el-icon>
              今日在线 {{ roomStats.studying_count || 0 }}/{{ roomStats.total_members || 0 }}人
            </span>
            <span class="stat-item">
              <el-icon size="12"><Timer /></el-icon>
              今日总计 {{ roomStats.today_total_minutes || 0 }}分钟
            </span>
            <span class="stat-item" v-if="roomStats.daily_target_minutes > 0">
              <el-icon size="12"><Aim /></el-icon>
              每日目标 {{ roomStats.daily_target_minutes }}分钟
            </span>
            <span class="stat-item">
              <el-icon size="12"><Calendar /></el-icon>
              今日打卡 {{ roomStats.today_checkins || 0 }}人
            </span>
          </div>

          <!-- 未加入提示 -->
          <div v-if="!activeRoom.is_member && !activeRoom.can_manage && activeRoom.member_status !== 'pending'" class="join-prompt">
            <el-icon :size="40" color="#909399"><Lock /></el-icon>
            <p>你还没有加入这个房间，加入需房主或管理员审核</p>
            <el-button type="primary" @click="handleJoin(activeRoom)">申请加入</el-button>
          </div>

          <!-- 待审核提示 -->
          <div v-else-if="activeRoom.member_status === 'pending'" class="join-prompt">
            <el-icon :size="40" color="#e6a23c"><Clock /></el-icon>
            <p>您的加入申请正在等待审核，请耐心等待</p>
            <el-button type="warning" plain @click="handleCancelJoin(activeRoom)">取消申请</el-button>
          </div>

          <!-- 管理员未加入 -->
          <div v-else-if="!activeRoom.is_member && activeRoom.can_manage" class="join-prompt">
            <el-icon :size="40" color="#409eff"><Setting /></el-icon>
            <p>管理员/审核员进入即拥有群管理权限</p>
            <el-button type="primary" @click="handleJoin(activeRoom)">进入管理</el-button>
          </div>

          <!-- 已加入：分区切换 -->
          <template v-else>
            <div class="zone-tabs">
              <div class="zone-tab" :class="{ active: activeZone === 'chat' }" @click="switchZone('chat')">
                <el-icon><ChatLineRound /></el-icon> 闲聊茶水间
              </div>
              <div class="zone-tab" :class="{ active: activeZone === 'study' }" @click="switchZone('study')">
                <el-icon><Reading /></el-icon> 自习打卡区
              </div>
            </div>

            <!-- ===== 闲聊区 ===== -->
            <template v-if="activeZone === 'chat'">
              <div class="chat-messages" ref="chatMessagesRef" v-loading="msgLoading">
                <div v-for="msg in chatMessages" :key="msg.id" class="msg-row" :class="{ 'msg-mine': msg.sender_id === authStore.user?.id, 'msg-system': msg.is_system }">
                  <template v-if="msg.is_system">
                    <div class="msg-system-text">{{ msg.content.replace('【系统消息】', '') }}</div>
                  </template>
                  <template v-else>
                    <el-avatar :size="36" class="msg-avatar" :style="{ background: avatarColor(msg.sender_id) }">{{ msg.sender_name?.charAt(0) }}</el-avatar>
                    <div class="msg-content-wrap">
                      <div class="msg-sender">
                        {{ msg.sender_name }}
                        <el-tag size="small" :type="roleTagType(msg.sender_role)" effect="plain" class="msg-role-tag">{{ roleLabel(msg.sender_role) }}</el-tag>
                      </div>
                      <div class="msg-bubble">{{ msg.content }}</div>
                      <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
                    </div>
                  </template>
                </div>
                <el-empty v-if="!msgLoading && chatMessages.length === 0" description="还没有消息，发一条试试吧" :image-size="60" />
              </div>
              <div class="chat-input-area">
                <el-input v-model="inputText" type="textarea" :rows="2" placeholder="输入消息，按 Ctrl+Enter 发送..." maxlength="2000" @keydown.enter.ctrl="sendMessage" resize="none" />
                <el-button type="primary" :loading="sending" :disabled="!inputText.trim()" @click="sendMessage">发送</el-button>
              </div>
            </template>

            <!-- ===== 自习区 ===== -->
            <template v-if="activeZone === 'study'">
              <div class="study-zone" v-loading="checkinLoading">
                <!-- 自习计时器 -->
                <div class="timer-card">
                  <div class="timer-left">
                    <div v-if="isStudyingInActive" class="timer-display">
                      <span class="timer-number">{{ studyElapsedText }}</span>
                      <el-tag type="success" effect="dark" size="small">自习中</el-tag>
                    </div>
                    <div v-else class="timer-display">
                      <span class="timer-number">{{ myTodayMinutes }}分钟</span>
                      <span class="timer-label">今日已学</span>
                    </div>
                  </div>
                  <div class="timer-right">
                    <el-button v-if="!isStudyingInActive" type="success" :icon="VideoPlay" @click="handleStartStudy">开始自习</el-button>
                    <el-button v-if="isStudyingInActive" type="danger" :icon="VideoPause" @click="handleStopStudy">结束自习</el-button>
                    <el-button type="primary" plain :icon="EditPen" @click="openCheckinDialog">今日打卡</el-button>
                  </div>
                </div>

                <!-- 打卡记录列表 -->
                <div class="checkin-list-header">
                  <span>打卡记录</span>
                  <el-button text size="small" :icon="Refresh" @click="fetchCheckins">刷新</el-button>
                </div>
                <div class="checkin-list">
                  <el-empty v-if="!checkinLoading && checkins.length === 0" description="还没有人打卡，快来第一个打卡吧" :image-size="60" />
                  <div v-for="c in checkins" :key="c.id" class="checkin-card">
                    <div class="checkin-card-header">
                      <el-avatar :size="32" :style="{ background: avatarColor(c.user_id) }">{{ c.nickname?.charAt(0) }}</el-avatar>
                      <div class="checkin-user-info">
                        <span class="checkin-user-name">{{ c.nickname }}</span>
                        <el-tag size="small" :type="roleTagType(c.role)" effect="plain">{{ roleLabel(c.role) }}</el-tag>
                        <span class="checkin-time">{{ formatTime(c.created_at) }}</span>
                      </div>
                      <el-tag v-if="c.study_minutes > 0" type="success" size="small" effect="plain">学习{{ c.study_minutes }}分钟</el-tag>
                    </div>
                    <div class="checkin-card-body">
                      <div v-if="c.completed" class="checkin-field"><span class="checkin-label">✅ 完成</span><span class="checkin-value">{{ c.completed }}</span></div>
                      <div v-if="c.incomplete" class="checkin-field"><span class="checkin-label">❌ 未完成</span><span class="checkin-value">{{ c.incomplete }}</span></div>
                      <div v-if="c.tomorrow_plan" class="checkin-field"><span class="checkin-label">🎯 明日</span><span class="checkin-value">{{ c.tomorrow_plan }}</span></div>
                      <div v-if="c.mood" class="checkin-field"><span class="checkin-label">💭 碎碎念</span><span class="checkin-value">{{ c.mood }}</span></div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </template>
        </template>

        <div v-else class="chat-placeholder">
          <el-icon :size="60" color="#dcdfe6"><ChatLineRound /></el-icon>
          <p>选择一个房间开始交流</p>
        </div>
      </div>
    </div>

    <!-- 创建房间对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建自习房间" width="520px" :close-on-click-modal="false">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="110px">
        <el-form-item label="房间名称" prop="name">
          <el-input v-model="createForm.name" placeholder="如：考研英语冲刺自习室" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="房间分类" prop="category">
          <el-select v-model="createForm.category" placeholder="选择分类" style="width: 100%">
            <el-option label="考研" value="考研" />
            <el-option label="编程" value="编程" />
            <el-option label="英语考试" value="英语考试" />
            <el-option label="职业发展" value="职业发展" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="房间标签" prop="tags">
          <el-input v-model="createForm.tags" placeholder="逗号分隔，如：考研,Python,每日目标8h,禁闲聊" maxlength="255" />
          <div class="form-tip">用逗号分隔，方便别人快速了解房间主题</div>
        </el-form-item>
        <el-form-item label="房间简介" prop="description">
          <el-input v-model="createForm.description" type="textarea" :rows="2" placeholder="如：考研冲刺自习室｜禁闲聊，每日目标7h，考研公共课搭子" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="每日目标" prop="daily_target_minutes">
          <el-input-number v-model="createForm.daily_target_minutes" :min="0" :max="960" :step="30" />
          <span class="form-tip-inline">分钟（0=不限）</span>
        </el-form-item>
        <el-form-item label="目标时长" prop="target_minutes">
          <el-input-number v-model="createForm.target_minutes" :min="10" :max="600" :step="10" />
          <span class="form-tip-inline">分钟</span>
        </el-form-item>
        <el-form-item label="最大人数" prop="max_members">
          <el-input-number v-model="createForm.max_members" :min="2" :max="50" />
        </el-form-item>
        <el-form-item label="是否私密">
          <el-switch v-model="createForm.is_private" :active-value="1" :inactive-value="0" active-text="私密（需申请）" inactive-text="公开（直接加入）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createSubmitting" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 打卡对话框 -->
    <el-dialog v-model="checkinDialogVisible" title="今日打卡" width="520px" :close-on-click-modal="false">
      <el-form :model="checkinForm" label-width="90px">
        <el-form-item label="今日完成">
          <el-input v-model="checkinForm.completed" type="textarea" :rows="3" placeholder="今天完成了哪些学习任务？" />
        </el-form-item>
        <el-form-item label="未完成">
          <el-input v-model="checkinForm.incomplete" type="textarea" :rows="2" placeholder="哪些任务没做完？（选填）" />
        </el-form-item>
        <el-form-item label="明日计划">
          <el-input v-model="checkinForm.tomorrow_plan" type="textarea" :rows="2" placeholder="明天打算学什么？" />
        </el-form-item>
        <el-form-item label="碎碎念">
          <el-input v-model="checkinForm.mood" type="textarea" :rows="2" placeholder="今天的状态、心情（选填）" />
        </el-form-item>
        <el-form-item label="学习时长">
          <el-input-number v-model="checkinForm.study_minutes" :min="0" :max="960" :step="15" />
          <span class="form-tip-inline">分钟</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="checkinDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="checkinSubmitting" @click="submitCheckin">提交打卡</el-button>
      </template>
    </el-dialog>

    <!-- 公告对话框 -->
    <el-dialog v-model="announcementDialogVisible" title="设置房间公告" width="520px">
      <el-input v-model="announcementText" type="textarea" :rows="5" placeholder="输入房间公告，如：禁止晒分数、禁止广告、打卡模板等" maxlength="2000" show-word-limit />
      <template #footer>
        <el-button @click="announcementDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="announcementSubmitting" @click="submitAnnouncement">保存</el-button>
      </template>
    </el-dialog>

    <!-- 成员列表对话框 -->
    <el-dialog v-model="membersDialogVisible" :title="'房间成员 (' + members.length + ')'" width="480px">
      <div v-loading="membersLoading" class="members-list">
        <el-empty v-if="!membersLoading && members.length === 0" description="暂无成员" :image-size="50" />
        <div v-for="m in members" :key="m.user_id" class="member-item">
          <el-avatar :size="40" :style="{ background: avatarColor(m.user_id) }">{{ (m.nickname || 'U').charAt(0) }}</el-avatar>
          <div class="member-info">
            <div class="member-name-row">
              <span class="member-name">{{ m.nickname }}</span>
              <el-tag v-if="m.is_owner" type="warning" size="small">群主</el-tag>
              <el-tag size="small" :type="roleTagType(m.role)" effect="plain">{{ roleLabel(m.role) }}</el-tag>
            </div>
            <div class="member-meta">
              <span v-if="m.is_studying" class="studying-badge">● 自习中</span>
              <span class="study-minutes">今日{{ m.today_minutes || 0 }}min / 累计{{ m.study_minutes || 0 }}min</span>
            </div>
          </div>
          <el-button v-if="canKickMember(m)" size="small" type="danger" text @click="handleKick(m)">踢出</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 待审核成员对话框 -->
    <el-dialog v-model="pendingDialogVisible" title="加入申请审核" width="480px">
      <div v-loading="pendingLoading" class="members-list">
        <el-empty v-if="!pendingLoading && pendingMembers.length === 0" description="暂无待审核申请" :image-size="50" />
        <div v-for="m in pendingMembers" :key="m.user_id" class="member-item">
          <el-avatar :size="40" :style="{ background: avatarColor(m.user_id) }">{{ (m.nickname || 'U').charAt(0) }}</el-avatar>
          <div class="member-info">
            <div class="member-name-row">
              <span class="member-name">{{ m.nickname }}</span>
              <el-tag size="small" :type="roleTagType(m.role)" effect="plain">{{ roleLabel(m.role) }}</el-tag>
            </div>
            <div class="member-meta">
              <span class="study-minutes">申请时间: {{ formatTime(m.joined_at) }}</span>
            </div>
          </div>
          <div class="pending-actions">
            <el-button size="small" type="success" @click="handleApprove(m)">通过</el-button>
            <el-button size="small" type="danger" plain @click="handleReject(m)">拒绝</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, User, Lock, CircleClose, ChatLineRound,
  VideoPlay, VideoPause, Setting, Timer, Reading, Edit, EditPen,
  Bell, Aim, Calendar, Checked, Clock,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { studyRoomApi } from '@/api'

const authStore = useAuthStore()
const isAdminRole = computed(() => ['admin', 'auditor'].includes(authStore.role))

// ============ 房间列表 ============
const loading = ref(false)
const rooms = ref([])
const keyword = ref('')
const selectedCategory = ref('全部')

async function fetchRooms() {
  loading.value = true
  try {
    const params = { page: 1, page_size: 50 }
    if (keyword.value) params.keyword = keyword.value
    if (selectedCategory.value && selectedCategory.value !== '全部') params.category = selectedCategory.value
    const res = await studyRoomApi.list(params)
    rooms.value = res.data || []
    if (activeRoom.value) {
      const updated = rooms.value.find((r) => r.id === activeRoom.value.id)
      if (updated) {
        updated.can_manage = activeRoom.value.can_manage
        activeRoom.value = { ...activeRoom.value, ...updated }
      }
    }
  } catch (e) { /* handled */ } finally {
    loading.value = false
  }
}

function handleSearch() { fetchRooms() }

// ============ 自习计时 ============
const myStudyRoomId = ref(null)
const myStudyStartTime = ref(null)
const myTodayMinutes = ref(0)
let studyTimer = null

const myStudyRoom = computed(() => {
  if (!myStudyRoomId.value) return null
  return rooms.value.find((r) => r.id === myStudyRoomId.value) || activeRoom.value
})

const isStudyingInActive = computed(() => activeRoom.value && myStudyRoomId.value === activeRoom.value.id)

const studyElapsedText = computed(() => {
  if (!myStudyStartTime.value) return '0分钟'
  const elapsed = Math.floor((Date.now() - myStudyStartTime.value) / 60000)
  if (elapsed < 1) return '不到1分钟'
  if (elapsed < 60) return elapsed + '分钟'
  const h = Math.floor(elapsed / 60)
  const m = elapsed % 60
  return m > 0 ? `${h}小时${m}分钟` : `${h}小时`
})

async function handleStartStudy() {
  if (!activeRoom.value) return
  try {
    await studyRoomApi.start(activeRoom.value.id)
    myStudyRoomId.value = activeRoom.value.id
    myStudyStartTime.value = Date.now()
    ElMessage.success('开始自习，加油！')
    startStudyTimer()
    fetchRoomStats()
  } catch (e) { /* handled */ }
}

async function handleStopStudy() {
  if (!myStudyRoomId.value) return
  const elapsed = myStudyStartTime.value ? Math.floor((Date.now() - myStudyStartTime.value) / 60000) : 0
  const totalMinutes = Math.max(1, elapsed)
  try {
    const res = await studyRoomApi.stop(myStudyRoomId.value, { study_minutes: totalMinutes })
    ElMessage.success(`已结束自习，本次学习 ${totalMinutes} 分钟`)
    myTodayMinutes.value = res.data?.today_minutes || (myTodayMinutes.value + totalMinutes)
    myStudyRoomId.value = null
    myStudyStartTime.value = null
    stopStudyTimer()
    fetchRoomStats()
  } catch (e) { /* handled */ }
}

function startStudyTimer() {
  stopStudyTimer()
  studyTimer = setInterval(() => {}, 60000)
}
function stopStudyTimer() {
  if (studyTimer) { clearInterval(studyTimer); studyTimer = null }
}

// ============ 群聊 ============
const activeRoom = ref(null)
const activeZone = ref('chat')
const chatMessages = ref([])
const chatMessagesRef = ref(null)
const msgLoading = ref(false)
const inputText = ref('')
const sending = ref(false)
let pollTimer = null

const roomStats = ref({})
const canEditAnnouncement = computed(() => {
  if (!activeRoom.value) return false
  return activeRoom.value.can_manage || activeRoom.value.creator_id === authStore.user?.id
})

const canManageRoom = computed(() => {
  if (!activeRoom.value) return false
  return activeRoom.value.can_manage || activeRoom.value.creator_id === authStore.user?.id
})

async function selectRoom(room) {
  activeRoom.value = room
  activeZone.value = 'chat'
  myTodayMinutes.value = 0
  if (room.is_member || room.can_manage) {
    await Promise.all([fetchMessages(room.id), fetchRoomStats(), fetchMyStudyInfo(room.id)])
    startPolling(room.id)
  } else {
    chatMessages.value = []
    stopPolling()
  }
}

function switchZone(zone) {
  activeZone.value = zone
  if (zone === 'study') {
    fetchCheckins()
  }
}

async function fetchRoomStats() {
  if (!activeRoom.value) return
  try {
    const res = await studyRoomApi.stats(activeRoom.value.id)
    roomStats.value = res.data || {}
  } catch (e) { /* silent */ }
}

async function fetchMyStudyInfo(roomId) {
  try {
    const res = await studyRoomApi.members(roomId)
    const me = (res.data || []).find((m) => m.user_id === authStore.user?.id)
    if (me) {
      myTodayMinutes.value = me.today_minutes || 0
      if (me.is_studying) {
        myStudyRoomId.value = roomId
        myStudyStartTime.value = Date.now()
        startStudyTimer()
      }
    }
  } catch (e) { /* silent */ }
}

async function fetchMessages(roomId) {
  if (activeRoom.value?.id !== roomId) return
  msgLoading.value = true
  try {
    const res = await studyRoomApi.messages(roomId, { limit: 50, zone: 'chat' })
    chatMessages.value = res.data || []
    await nextTick()
    scrollToBottom()
  } catch (e) { /* handled */ } finally {
    msgLoading.value = false
  }
}

function startPolling(roomId) {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (activeRoom.value?.id !== roomId) { stopPolling(); return }
    try {
      const res = await studyRoomApi.messages(roomId, { limit: 50, zone: 'chat' })
      const newMsgs = res.data || []
      if (newMsgs.length !== chatMessages.value.length) {
        const wasNearBottom = isNearBottom()
        chatMessages.value = newMsgs
        if (wasNearBottom) { await nextTick(); scrollToBottom() }
      }
    } catch (e) { /* silent */ }
  }, 3000)
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

function isNearBottom() {
  if (!chatMessagesRef.value) return true
  const el = chatMessagesRef.value
  return el.scrollHeight - el.scrollTop - el.clientHeight < 100
}

function scrollToBottom() {
  if (chatMessagesRef.value) chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
}

async function sendMessage() {
  if (!inputText.value.trim() || !activeRoom.value) return
  sending.value = true
  try {
    await studyRoomApi.sendMessage(activeRoom.value.id, { content: inputText.value.trim(), zone: 'chat' })
    inputText.value = ''
    await fetchMessages(activeRoom.value.id)
  } catch (e) { /* handled */ } finally {
    sending.value = false
  }
}

// ============ 加入/离开 ============
async function handleJoin(room) {
  try {
    const res = await studyRoomApi.join(room.id)
    ElMessage.success(res.message || (isAdminRole.value ? '已进入管理' : '申请已提交'))
    if (isAdminRole.value) {
      room.is_member = true
      room.member_status = 'active'
      await fetchMessages(room.id)
      await fetchRoomStats()
      await fetchMyStudyInfo(room.id)
      startPolling(room.id)
    } else {
      room.member_status = 'pending'
    }
    fetchRooms()
  } catch (e) { /* handled */ }
}

async function handleCancelJoin(room) {
  try {
    await ElMessageBox.confirm('确定取消加入申请吗？', '提示', { type: 'warning' })
    await studyRoomApi.leave(room.id)
    ElMessage.success('已取消申请')
    room.member_status = null
    fetchRooms()
  } catch (e) { /* cancel */ }
}

async function handleLeave() {
  if (!activeRoom.value) return
  try {
    await ElMessageBox.confirm('确定离开这个房间吗？', '提示', { type: 'warning' })
    if (myStudyRoomId.value === activeRoom.value.id) await handleStopStudy()
    await studyRoomApi.leave(activeRoom.value.id)
    ElMessage.success('已离开房间')
    activeRoom.value.is_member = false
    chatMessages.value = []
    stopPolling()
    fetchRooms()
  } catch (e) { /* cancel */ }
}

// ============ 创建房间 ============
const createDialogVisible = ref(false)
const createSubmitting = ref(false)
const createFormRef = ref()
const createForm = reactive({
  name: '', target_minutes: 120, max_members: 10, is_private: 0,
  tags: '', description: '', category: '其他', daily_target_minutes: 0,
})
const createRules = {
  name: [{ required: true, message: '请输入房间名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

function openCreateDialog() {
  Object.assign(createForm, { name: '', target_minutes: 120, max_members: 10, is_private: 0, tags: '', description: '', category: '其他', daily_target_minutes: 0 })
  createDialogVisible.value = true
}

async function submitCreate() {
  await createFormRef.value.validate(async (valid) => {
    if (!valid) return
    createSubmitting.value = true
    try {
      await studyRoomApi.create({ ...createForm })
      ElMessage.success('房间创建成功')
      createDialogVisible.value = false
      fetchRooms()
    } catch (e) { /* handled */ } finally {
      createSubmitting.value = false
    }
  })
}

// ============ 打卡 ============
const checkinDialogVisible = ref(false)
const checkinSubmitting = ref(false)
const checkinLoading = ref(false)
const checkins = ref([])
const checkinForm = reactive({ completed: '', incomplete: '', tomorrow_plan: '', mood: '', study_minutes: 0 })

function openCheckinDialog() {
  Object.assign(checkinForm, { completed: '', incomplete: '', tomorrow_plan: '', mood: '', study_minutes: myTodayMinutes.value })
  checkinDialogVisible.value = true
}

async function fetchCheckins() {
  if (!activeRoom.value) return
  checkinLoading.value = true
  try {
    const res = await studyRoomApi.checkins(activeRoom.value.id, { page: 1, page_size: 20 })
    checkins.value = res.data || []
  } catch (e) { /* handled */ } finally {
    checkinLoading.value = false
  }
}

async function submitCheckin() {
  if (!checkinForm.completed && !checkinForm.tomorrow_plan && !checkinForm.mood) {
    ElMessage.warning('请至少填写一项打卡内容')
    return
  }
  checkinSubmitting.value = true
  try {
    await studyRoomApi.checkin(activeRoom.value.id, { ...checkinForm })
    ElMessage.success('打卡成功！')
    checkinDialogVisible.value = false
    await fetchCheckins()
    await fetchRoomStats()
  } catch (e) { /* handled */ } finally {
    checkinSubmitting.value = false
  }
}

// ============ 公告 ============
const announcementDialogVisible = ref(false)
const announcementText = ref('')
const announcementSubmitting = ref(false)

function openAnnouncementDialog() {
  announcementText.value = activeRoom.value?.announcement || ''
  announcementDialogVisible.value = true
}

async function submitAnnouncement() {
  announcementSubmitting.value = true
  try {
    await studyRoomApi.updateAnnouncement(activeRoom.value.id, { announcement: announcementText.value })
    ElMessage.success('公告已更新')
    activeRoom.value.announcement = announcementText.value
    announcementDialogVisible.value = false
  } catch (e) { /* handled */ } finally {
    announcementSubmitting.value = false
  }
}

// ============ 成员管理 ============
const membersDialogVisible = ref(false)
const membersLoading = ref(false)
const members = ref([])

async function openMembersDialog() {
  if (!activeRoom.value) return
  membersDialogVisible.value = true
  membersLoading.value = true
  members.value = []
  try {
    const res = await studyRoomApi.members(activeRoom.value.id)
    members.value = res.data || []
  } catch (e) { /* handled */ } finally {
    membersLoading.value = false
  }
}

function canKickMember(m) {
  if (m.user_id === authStore.user?.id) return false
  if (m.is_owner) return false  // 不能踢群主
  if (isAdminRole.value) return true
  if (activeRoom.value?.creator_id === authStore.user?.id) return true
  return false
}

async function handleKick(member) {
  try {
    await ElMessageBox.confirm(`确定将「${member.nickname}」移出房间吗？被移出的成员将无法再次加入。`, '踢出成员', { type: 'warning' })
    await studyRoomApi.kickMember(activeRoom.value.id, member.user_id)
    ElMessage.success(`已将 ${member.nickname} 移出房间`)
    members.value = members.value.filter((m) => m.user_id !== member.user_id)
    fetchRooms()
    fetchRoomStats()
  } catch (e) { /* cancel */ }
}

// ============ 待审核管理 ============
const pendingDialogVisible = ref(false)
const pendingLoading = ref(false)
const pendingMembers = ref([])

async function openPendingDialog() {
  if (!activeRoom.value) return
  pendingDialogVisible.value = true
  pendingLoading.value = true
  pendingMembers.value = []
  try {
    const res = await studyRoomApi.pendingMembers(activeRoom.value.id)
    pendingMembers.value = res.data || []
  } catch (e) { /* handled */ } finally {
    pendingLoading.value = false
  }
}

async function handleApprove(member) {
  try {
    await studyRoomApi.approveMember(activeRoom.value.id, member.user_id)
    ElMessage.success(`已通过 ${member.nickname} 的加入申请`)
    pendingMembers.value = pendingMembers.value.filter((m) => m.user_id !== member.user_id)
    activeRoom.value.pending_count = Math.max(0, (activeRoom.value.pending_count || 0) - 1)
    fetchRooms()
    fetchRoomStats()
  } catch (e) { /* handled */ }
}

async function handleReject(member) {
  try {
    await ElMessageBox.confirm(`确定拒绝「${member.nickname}」的加入申请吗？`, '拒绝申请', { type: 'warning' })
    await studyRoomApi.rejectMember(activeRoom.value.id, member.user_id)
    ElMessage.success(`已拒绝 ${member.nickname} 的加入申请`)
    pendingMembers.value = pendingMembers.value.filter((m) => m.user_id !== member.user_id)
    activeRoom.value.pending_count = Math.max(0, (activeRoom.value.pending_count || 0) - 1)
    fetchRooms()
  } catch (e) { /* cancel */ }
}

async function handleCloseRoom() {
  try {
    await ElMessageBox.confirm(`确定关闭房间「${activeRoom.value.name}」吗？`, '关闭房间', { type: 'warning' })
    await studyRoomApi.closeRoom(activeRoom.value.id)
    ElMessage.success('房间已关闭')
    activeRoom.value = null
    stopPolling()
    fetchRooms()
  } catch (e) { /* cancel */ }
}

// ============ 工具函数 ============
function roleLabel(role) {
  const map = { student: '学生', teacher: '教师', auditor: '审核员', admin: '管理员' }
  return map[role] || '用户'
}

function roleTagType(role) {
  const map = { student: 'success', teacher: 'warning', auditor: 'danger', admin: '' }
  return map[role] || 'info'
}

const avatarColors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#6c5ce7', '#00b894', '#fd79a8']
function avatarColor(userId) { return avatarColors[userId % avatarColors.length] }

function parseTags(tags) {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean).slice(0, 4)
}

function formatTarget(minutes) {
  if (!minutes || minutes === 0) return '不限'
  if (minutes >= 60) {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    return m > 0 ? `目标${h}h${m}m` : `目标${h}h`
  }
  return `目标${minutes}m`
}

const categoryColors = {
  '考研': '#f56c6c', '编程': '#409eff', '英语考试': '#67c23a',
  '职业发展': '#e6a23c', '其他': '#909399',
}
function categoryColor(cat) { return categoryColors[cat] || '#909399' }

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '时前'
  if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
  return (d.getMonth() + 1) + '/' + d.getDate()
}

onMounted(() => { fetchRooms() })
onUnmounted(() => { stopPolling(); stopStudyTimer() })
</script>

<style scoped>
.study-room-page {
  padding: 20px;
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
}
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.page-header h2 { margin: 0; font-size: 20px; color: #303133; }
.header-actions { display: flex; gap: 8px; }

/* 自习状态条 */
.active-study-bar { margin-bottom: 12px; }
.active-study-bar :deep(.el-card__body) { display: flex; align-items: center; justify-content: space-between; padding: 10px 20px; }
.active-study-info { display: flex; align-items: center; gap: 12px; }
.active-study-name { font-size: 15px; font-weight: 600; color: #303133; }
.active-study-time { font-size: 13px; color: #67c23a; }

/* 主容器 */
.room-container { flex: 1; display: flex; gap: 16px; overflow: hidden; }

/* 左侧列表 */
.room-list-panel {
  width: 340px; flex-shrink: 0; background: #fff; border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); display: flex; flex-direction: column; overflow: hidden;
}
.category-filter { padding: 10px 10px 6px; border-bottom: 1px solid #f0f0f0; }
.category-filter :deep(.el-radio-button__inner) { padding: 6px 10px; font-size: 12px; }
.room-list-header { padding: 10px; border-bottom: 1px solid #ebeef5; }
.room-list { flex: 1; overflow-y: auto; padding: 6px; }

.room-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px; border-radius: 8px; cursor: pointer; transition: background 0.2s; margin-bottom: 4px; }
.room-item:hover { background: #f5f7fa; }
.room-item.active { background: #ecf5ff; }
.room-item-avatar { width: 44px; height: 44px; border-radius: 10px; color: #fff; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.room-item-info { flex: 1; min-width: 0; }
.room-item-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.room-item-name { font-size: 14px; font-weight: 600; color: #303133; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: flex; align-items: center; gap: 4px; }
.room-item-time { font-size: 11px; color: #c0c4cc; flex-shrink: 0; margin-left: 8px; }
.room-item-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; }
.room-tag { font-size: 11px !important; height: 20px !important; padding: 0 6px !important; line-height: 18px !important; }
.room-item-desc { font-size: 12px; color: #909399; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.room-item-bottom { display: flex; align-items: center; gap: 10px; }
.room-item-meta { font-size: 11px; color: #909399; display: flex; align-items: center; gap: 2px; }
.studying { color: #67c23a; display: flex; align-items: center; gap: 4px; }
.dot-studying { width: 6px; height: 6px; border-radius: 50%; background: #67c23a; display: inline-block; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
.room-item-count { font-size: 11px; color: #c0c4cc; margin-left: auto; }

/* 审核按钮徽标 */
.pending-badge { margin-left: 4px; }
.pending-badge :deep(.el-badge__content) { font-size: 10px; height: 16px; line-height: 16px; padding: 0 4px; }
.pending-actions { display: flex; gap: 6px; flex-shrink: 0; }

/* 右侧聊天 */
.chat-panel { flex: 1; background: #fff; border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); display: flex; flex-direction: column; overflow: hidden; }
.chat-header { padding: 12px 20px; border-bottom: 1px solid #ebeef5; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
.chat-header-left { display: flex; align-items: center; gap: 10px; }
.chat-header-left h3 { margin: 0; font-size: 17px; color: #303133; display: flex; align-items: center; gap: 4px; }
.chat-header-meta { font-size: 13px; color: #909399; }
.chat-header-right { display: flex; gap: 8px; flex-wrap: wrap; }

/* 公告条 */
.room-announcement-bar { padding: 8px 20px; background: #fdf6ec; border-bottom: 1px solid #faecd8; display: flex; align-items: center; gap: 8px; font-size: 13px; color: #e6a23c; flex-shrink: 0; }

/* 统计条 */
.room-stats-bar { padding: 8px 20px; background: #f0f9eb; border-bottom: 1px solid #e1f3d8; display: flex; gap: 20px; font-size: 12px; color: #67c23a; flex-shrink: 0; flex-wrap: wrap; }
.stat-item { display: flex; align-items: center; gap: 4px; }

/* 分区标签 */
.zone-tabs { display: flex; border-bottom: 1px solid #ebeef5; flex-shrink: 0; }
.zone-tab { flex: 1; padding: 12px; text-align: center; cursor: pointer; font-size: 14px; color: #909399; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 6px; border-bottom: 2px solid transparent; }
.zone-tab:hover { color: #409eff; }
.zone-tab.active { color: #409eff; border-bottom-color: #409eff; font-weight: 600; }

/* 未加入提示 */
.join-prompt { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; color: #909399; }
.join-prompt p { margin: 0; font-size: 15px; }

/* 消息区 */
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; background: #f5f7fa; }
.msg-row { display: flex; gap: 10px; margin-bottom: 16px; }
.msg-mine { flex-direction: row-reverse; }
.msg-system { justify-content: center; }
.msg-system-text { font-size: 12px; color: #909399; background: rgba(0,0,0,0.05); padding: 4px 12px; border-radius: 10px; }
.msg-avatar { color: #fff; flex-shrink: 0; }
.msg-content-wrap { max-width: 65%; }
.msg-mine .msg-content-wrap { display: flex; flex-direction: column; align-items: flex-end; }
.msg-sender { font-size: 12px; color: #909399; margin-bottom: 4px; display: flex; align-items: center; gap: 4px; }
.msg-role-tag { transform: scale(0.85); }
.msg-bubble { padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.6; word-break: break-word; background: #fff; color: #303133; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.msg-mine .msg-bubble { background: #409eff; color: #fff; }
.msg-time { font-size: 11px; color: #c0c4cc; margin-top: 4px; }
.msg-mine .msg-time { text-align: right; }

/* 输入区 */
.chat-input-area { padding: 12px 20px; border-top: 1px solid #ebeef5; display: flex; gap: 12px; align-items: flex-end; flex-shrink: 0; }
.chat-input-area .el-input { flex: 1; }

/* 自习区 */
.study-zone { flex: 1; overflow-y: auto; padding: 20px; background: #f5f7fa; }
.timer-card { background: #fff; border-radius: 12px; padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.timer-left { display: flex; flex-direction: column; gap: 4px; }
.timer-display { display: flex; align-items: baseline; gap: 8px; }
.timer-number { font-size: 28px; font-weight: 700; color: #303133; }
.timer-label { font-size: 13px; color: #909399; }
.timer-right { display: flex; gap: 8px; }

/* 打卡记录 */
.checkin-list-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; font-size: 15px; font-weight: 600; color: #303133; }
.checkin-list { display: flex; flex-direction: column; gap: 12px; }
.checkin-card { background: #fff; border-radius: 10px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.checkin-card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.checkin-user-info { flex: 1; display: flex; align-items: center; gap: 6px; }
.checkin-user-name { font-size: 14px; font-weight: 600; color: #303133; }
.checkin-time { font-size: 12px; color: #c0c4cc; }
.checkin-card-body { display: flex; flex-direction: column; gap: 8px; }
.checkin-field { display: flex; gap: 8px; font-size: 13px; }
.checkin-label { color: #909399; flex-shrink: 0; width: 70px; }
.checkin-value { color: #303133; flex: 1; white-space: pre-wrap; }

/* 占位 */
.chat-placeholder { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #909399; }
.chat-placeholder p { margin-top: 16px; font-size: 14px; }

/* 成员列表 */
.members-list { min-height: 120px; max-height: 420px; overflow-y: auto; }
.member-item { display: flex; align-items: center; gap: 12px; padding: 10px 4px; border-bottom: 1px dashed #f0f0f0; }
.member-item:last-child { border-bottom: none; }
.member-info { flex: 1; }
.member-name-row { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.member-name { font-size: 14px; font-weight: 500; color: #303133; }
.member-meta { display: flex; align-items: center; gap: 10px; font-size: 12px; color: #909399; }
.studying-badge { color: #67c23a; font-weight: 500; }
.study-minutes { color: #c0c4cc; }

.form-tip { font-size: 12px; color: #909399; margin-top: 4px; }
.form-tip-inline { margin-left: 8px; color: #909399; font-size: 13px; }

@media (max-width: 768px) {
  .room-container { flex-direction: column; }
  .room-list-panel { width: 100%; height: 280px; }
  .room-stats-bar { gap: 10px; }
  .timer-card { flex-direction: column; gap: 12px; }
}
</style>
