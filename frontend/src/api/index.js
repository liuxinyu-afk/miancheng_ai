import request from '@/utils/request'

// ==================== 认证管理 ====================
export const authApi = {
  register: (data) => request.post('/auth/register', data),
  login: (data) => request.post('/auth/login', data),
  getMe: () => request.get('/auth/me'),
  updateMe: (data) => request.put('/auth/me', data),
  changePassword: (data) => request.post('/auth/change-password', data),
  teacherCert: (data) => request.post('/auth/teacher-cert', data),
  uploadAvatar: (formData) => request.post('/auth/upload-avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  uploadFile: (formData) => request.post('/auth/upload-cert', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

// ==================== AI 任务生成 ====================
export const aiTaskApi = {
  generate: (data) => request.post('/ai-task/generate', data),
  save: (data) => request.post('/ai-task/save', data),
  myPackages: () => request.get('/ai-task/my-packages'),
  packageDetail: (id) => request.get(`/ai-task/packages/${id}`),
  deletePackage: (id) => request.delete(`/ai-task/packages/${id}`),
}

// ==================== AI 智能问答 ====================
export const aiChatApi = {
  ask: (data) => request.post('/ai-chat/ask', data),
  askWithImage: (formData) => request.post('/ai-chat/ask-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  }),
}

// ==================== 资源集市 ====================
export const marketApi = {
  publish: (data) => request.post('/market/publish', data),
  list: (params) => request.get('/market/list', { params }),
  myPublishments: () => request.get('/market/my-publishments'),
  myFavorites: () => request.get('/market/my-favorites'),
  detail: (id) => request.get(`/market/${id}`),
  favorite: (id) => request.post(`/market/${id}/favorite`),
  unfavorite: (id) => request.delete(`/market/${id}/favorite`),
  // 评分
  rate: (id, data) => request.post(`/market/${id}/rate`, data),
  ratings: (id, params) => request.get(`/market/${id}/ratings`, { params }),
  // 举报
  report: (id, data) => request.post(`/market/${id}/report`, data),
}

// ==================== 学习中心 ====================
export const studyApi = {
  checkin: (data) => request.post('/study/checkin', data),
  todayCheckin: () => request.get('/study/checkin/today'),
  checkinHistory: (params) => request.get('/study/checkin/history', { params }),
  createNote: (data) => request.post('/study/notes', data),
  myNotes: () => request.get('/study/notes'),
  updateNote: (id, data) => request.put(`/study/notes/${id}`, data),
  deleteNote: (id) => request.delete(`/study/notes/${id}`),
  progress: (packageId) => request.get(`/study/progress/${packageId}`),
}

// ==================== 成果社区 ====================
export const achievementApi = {
  createPost: (data) => request.post('/achievement/posts', data),
  posts: (params) => request.get('/achievement/posts', { params }),
  postDetail: (id) => request.get(`/achievement/posts/${id}`),
  myPosts: () => request.get('/achievement/my-posts'),
  deletePost: (id) => request.delete(`/achievement/posts/${id}`),
  like: (id) => request.post(`/achievement/posts/${id}/like`),
  comments: (id) => request.get(`/achievement/posts/${id}/comments`),
  addComment: (id, data) => request.post(`/achievement/posts/${id}/comments`, data),
  messages: () => request.get('/achievement/messages', { silent: true }),
  messageDetail: (id) => request.get(`/achievement/messages/${id}/detail`),
  readMessage: (id) => request.put(`/achievement/messages/${id}/read`),
  clearNotifications: () => request.put('/achievement/messages/read-all'),
  leaderboard: () => request.get('/achievement/leaderboard', { silent: true }),
  stats: () => request.get('/achievement/stats', { silent: true }),
}

// ==================== 结伴自习 ====================
export const studyRoomApi = {
  create: (data) => request.post('/study-room/create', data),
  list: (params) => request.get('/study-room/list', { params }),
  myRooms: () => request.get('/study-room/my-rooms'),
  join: (id) => request.post(`/study-room/${id}/join`),
  leave: (id) => request.post(`/study-room/${id}/leave`),
  start: (id) => request.post(`/study-room/${id}/start`),
  stop: (id, data) => request.post(`/study-room/${id}/stop`, data),
  members: (id) => request.get(`/study-room/${id}/members`),
  // 群聊消息（支持分区 zone: chat/study/all）
  messages: (id, params) => request.get(`/study-room/${id}/messages`, { params }),
  sendMessage: (id, data) => request.post(`/study-room/${id}/messages`, data),
  // 房间统计
  stats: (id) => request.get(`/study-room/${id}/stats`),
  // 结构化打卡
  checkin: (id, data) => request.post(`/study-room/${id}/checkin`, data),
  checkins: (id, params) => request.get(`/study-room/${id}/checkins`, { params }),
  // 房间公告
  updateAnnouncement: (id, data) => request.put(`/study-room/${id}/announcement`, data),
  // 我的打卡档案
  myCheckins: () => request.get('/study-room/my-checkins'),
  // 管理功能
  kickMember: (roomId, userId) => request.delete(`/study-room/${roomId}/members/${userId}`),
  closeRoom: (roomId) => request.put(`/study-room/${roomId}/close`),
  adminAll: () => request.get('/study-room/admin/all'),
  // V8 新增：审核功能
  pendingMembers: (roomId) => request.get(`/study-room/${roomId}/pending`),
  approveMember: (roomId, userId) => request.post(`/study-room/${roomId}/approve/${userId}`),
  rejectMember: (roomId, userId) => request.post(`/study-room/${roomId}/reject/${userId}`),
}

// ==================== 审核管理 ====================
export const auditApi = {
  pending: (params) => request.get('/audit/pending', { params }),
  pendingDetail: (type, id) => request.get(`/audit/pending/${type}/${id}`),
  review: (data) => request.post('/audit/review', data),
  history: (params) => request.get('/audit/history', { params }),
}

// ==================== 系统管理 ====================
export const adminApi = {
  dashboard: () => request.get('/admin/dashboard'),
  users: (params) => request.get('/admin/users', { params }),
  updateStatus: (id, data) => request.put(`/admin/users/${id}/status`, data),
  certRequests: () => request.get('/admin/cert-requests'),
  reviewCert: (id, data) => request.put(`/admin/cert-requests/${id}`, data),
  createAuditor: (data) => request.post('/admin/auditors', data),
  resourceStats: () => request.get('/admin/stats/resources'),
  taskStats: () => request.get('/admin/stats/tasks'),
  // V8 新增
  trends: () => request.get('/admin/trends'),
  reports: (params) => request.get('/admin/reports', { params }),
  handleReport: (id, data) => request.put(`/admin/reports/${id}`, data),
}

// ==================== 勋章系统 ====================
export const badgeApi = {
  my: () => request.get('/badges/my'),
  userBadges: (userId) => request.get(`/badges/user/${userId}`),
}

// ==================== 学习计划（学生专属）====================
export const studyPlanApi = {
  create: (data) => request.post('/study-plan/', data),
  list: (params) => request.get('/study-plan/', { params }),
  update: (id, data) => request.put(`/study-plan/${id}`, data),
  delete: (id) => request.delete(`/study-plan/${id}`),
}

// ==================== 公开统计 ====================
export const statsApi = {
  overview: () => request.get('/stats/overview', { silent: true }),
}

// ==================== 私信 ====================
export const messageApi = {
  searchUsers: (keyword) => request.get('/message/users', { params: { keyword } }),
  send: (data) => request.post('/message/send', data),
  conversations: () => request.get('/message/conversations', { silent: true }),
  messages: (userId) => request.get(`/message/conversation/${userId}`, { silent: true }),
  unreadCount: () => request.get('/message/unread-count', { silent: true }),
}

// ==================== 好友 ====================
export const friendApi = {
  search: (keyword) => request.get('/friend/search', { params: { keyword } }),
  sendRequest: (data) => request.post('/friend/request', data),
  requests: () => request.get('/friend/requests', { silent: true }),
  accept: (friendshipId) => request.post(`/friend/${friendshipId}/accept`),
  reject: (friendshipId) => request.post(`/friend/${friendshipId}/reject`),
  list: () => request.get('/friend/list', { silent: true }),
  status: (userId) => request.get(`/friend/status/${userId}`),
  remove: (userId) => request.delete(`/friend/${userId}`),
}

// ==================== 用户主页 ====================
export const userApi = {
  profile: (userId) => request.get(`/user/profile/${userId}`),
  recommend: () => request.get('/user/recommend'),
  userResources: (userId, params) => request.get(`/user/${userId}/resources`, { params }),
  userPosts: (userId, params) => request.get(`/user/${userId}/posts`, { params }),
}

// ==================== 交流广场 ====================
export const plazaApi = {
  list: (params) => request.get('/resource-plaza/list', { params }),
  create: (data) => request.post('/resource-plaza/create', data),
  detail: (id) => request.get(`/resource-plaza/${id}`),
  updateStatus: (id, status) => request.put(`/resource-plaza/${id}/status?status=${status}`),
  delete: (id) => request.delete(`/resource-plaza/${id}`),
  replies: (id) => request.get(`/resource-plaza/${id}/replies`),
  createReply: (id, data) => request.post(`/resource-plaza/${id}/replies`, data),
  acceptReply: (requestId, replyId) => request.put(`/resource-plaza/${requestId}/replies/${replyId}/accept`),
  deleteReply: (requestId, replyId) => request.delete(`/resource-plaza/${requestId}/replies/${replyId}`),
  myRequests: () => request.get('/resource-plaza/my/requests'),
  uploadImage: (formData) => request.post('/resource-plaza/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
}

// ==================== 问题反馈 ====================
export const feedbackApi = {
  create: (data) => request.post('/feedback/create', data),
  my: (params) => request.get('/feedback/my', { params }),
  // 管理员接口
  list: (params) => request.get('/feedback/list', { params }),
  stats: () => request.get('/feedback/stats'),
  reply: (id, data) => request.put(`/feedback/${id}/reply`, data),
  updateStatus: (id, status) => request.put(`/feedback/${id}/status?status=${status}`),
}
