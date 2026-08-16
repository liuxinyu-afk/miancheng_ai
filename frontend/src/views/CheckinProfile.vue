<template>
  <div class="checkin-profile-page">
    <div class="page-header">
      <h2>我的打卡档案</h2>
      <el-button :icon="Refresh" @click="fetchData">刷新</el-button>
    </div>

    <div v-loading="loading">
      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :xs="12" :sm="8" :md="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value">{{ data.total_checkins || 0 }}</div>
            <div class="stat-label">累计打卡</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value">{{ data.total_minutes || 0 }}</div>
            <div class="stat-label">累计学习(分钟)</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value">{{ weekTotalMinutes }}</div>
            <div class="stat-label">本周学习(分钟)</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value">{{ avgPerDay }}</div>
            <div class="stat-label">日均学习(分钟)</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 本周柱状图 -->
      <el-card shadow="never" class="chart-card">
        <template #header>本周学习时长</template>
        <div class="week-chart">
          <div v-for="(val, i) in (data.week_minutes || [0,0,0,0,0,0,0])" :key="i" class="week-bar-col">
            <div class="week-bar-val">{{ val }}</div>
            <div class="week-bar" :style="{ height: barHeight(val) + 'px' }"></div>
            <div class="week-bar-label">{{ weekLabels[i] }}</div>
          </div>
        </div>
      </el-card>

      <!-- 打卡记录列表 -->
      <el-card shadow="never" class="records-card">
        <template #header>打卡记录</template>
        <el-empty v-if="!loading && (data.checkins || []).length === 0" description="还没有打卡记录" />
        <div class="records-list">
          <div v-for="c in (data.checkins || [])" :key="c.id" class="record-card">
            <div class="record-header">
              <span class="record-room">{{ c.room_name }}</span>
              <span class="record-time">{{ formatTime(c.created_at) }}</span>
              <el-tag v-if="c.study_minutes > 0" type="success" size="small" effect="plain">{{ c.study_minutes }}分钟</el-tag>
            </div>
            <div class="record-body">
              <div v-if="c.completed" class="record-field"><span class="record-label">✅ 完成</span><span>{{ c.completed }}</span></div>
              <div v-if="c.incomplete" class="record-field"><span class="record-label">❌ 未完成</span><span>{{ c.incomplete }}</span></div>
              <div v-if="c.tomorrow_plan" class="record-field"><span class="record-label">🎯 明日</span><span>{{ c.tomorrow_plan }}</span></div>
              <div v-if="c.mood" class="record-field"><span class="record-label">💭 碎碎念</span><span>{{ c.mood }}</span></div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { studyRoomApi } from '@/api'

const loading = ref(false)
const data = ref({ checkins: [], total_checkins: 0, total_minutes: 0, week_minutes: [0,0,0,0,0,0,0] })
const weekLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const weekTotalMinutes = computed(() => (data.value.week_minutes || []).reduce((a, b) => a + b, 0))
const avgPerDay = computed(() => {
  const total = data.value.total_minutes || 0
  const count = (data.value.checkins || []).length
  return count > 0 ? Math.round(total / Math.max(1, Math.ceil(count / 7))) : 0
})

function barHeight(val) {
  const max = Math.max(...(data.value.week_minutes || [1]), 1)
  return Math.max(4, (val / max) * 120)
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

async function fetchData() {
  loading.value = true
  try {
    const res = await studyRoomApi.myCheckins()
    data.value = res.data || { checkins: [], total_checkins: 0, total_minutes: 0, week_minutes: [0,0,0,0,0,0,0] }
  } catch (e) { /* handled */ } finally {
    loading.value = false
  }
}

onMounted(() => { fetchData() })
</script>

<style scoped>
.checkin-profile-page { padding: 20px; max-width: 900px; margin: 0 auto; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 20px; color: #303133; }

.stats-row { margin-bottom: 16px; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-card :deep(.el-card__body) { padding: 20px; }
.stat-value { font-size: 28px; font-weight: 700; color: #409eff; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }

.chart-card { margin-bottom: 16px; }
.week-chart { display: flex; justify-content: space-around; align-items: flex-end; height: 180px; padding: 20px 10px 0; }
.week-bar-col { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.week-bar-val { font-size: 12px; color: #67c23a; font-weight: 600; }
.week-bar { width: 40px; background: linear-gradient(180deg, #67c23a 0%, #95d475 100%); border-radius: 4px 4px 0 0; transition: height 0.3s; }
.week-bar-label { font-size: 12px; color: #909399; }

.records-card { }
.records-list { display: flex; flex-direction: column; gap: 12px; }
.record-card { background: #f9fafc; border-radius: 8px; padding: 14px 16px; }
.record-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.record-room { font-size: 14px; font-weight: 600; color: #303133; }
.record-time { font-size: 12px; color: #c0c4cc; flex: 1; }
.record-body { display: flex; flex-direction: column; gap: 6px; }
.record-field { display: flex; gap: 8px; font-size: 13px; }
.record-label { color: #909399; width: 70px; flex-shrink: 0; }
</style>
