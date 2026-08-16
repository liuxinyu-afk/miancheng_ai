import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'HomeFilled' },
      },
      {
        path: 'ai-task',
        name: 'AITask',
        component: () => import('@/views/AITask.vue'),
        meta: { title: 'AI任务生成', icon: 'MagicStick' },
      },
      {
        path: 'ai-chat',
        name: 'AIChat',
        component: () => import('@/views/AIChat.vue'),
        meta: { title: 'AI问答', icon: 'ChatLineRound' },
      },
      {
        path: 'ai-task/:id',
        name: 'TaskPackageDetail',
        component: () => import('@/views/TaskPackageDetail.vue'),
        meta: { title: '任务包详情', hidden: true },
      },
      {
        path: 'market',
        name: 'Market',
        component: () => import('@/views/Market.vue'),
        meta: { title: '资源集市', icon: 'Goods' },
      },
      {
        path: 'market/:id',
        name: 'ResourceDetail',
        component: () => import('@/views/ResourceDetail.vue'),
        meta: { title: '资源详情', hidden: true },
      },
      {
        path: 'study',
        name: 'Study',
        component: () => import('@/views/Study.vue'),
        meta: { title: '学习中心', icon: 'Reading', roles: ['student', 'teacher', 'admin'] },
      },
      {
        path: 'achievement',
        name: 'Achievement',
        component: () => import('@/views/Achievement.vue'),
        meta: { title: '成果社区', icon: 'Trophy' },
      },
      {
        path: 'study-room',
        name: 'StudyRoom',
        component: () => import('@/views/StudyRoom.vue'),
        meta: { title: '结伴自习', icon: 'User' },
      },
      {
        path: 'messages',
        name: 'Messages',
        component: () => import('@/views/Messages.vue'),
        meta: { title: '私信', icon: 'ChatLineRound', roles: ['student', 'teacher', 'auditor'] },
      },
      {
        path: 'audit',
        name: 'Audit',
        component: () => import('@/views/Audit.vue'),
        meta: { title: '审核中心', icon: 'Checked', roles: ['auditor', 'admin'] },
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('@/views/Admin.vue'),
        meta: { title: '系统管理', icon: 'Setting', roles: ['admin'] },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心', hidden: true },
      },
      {
        path: 'user/:userId',
        name: 'UserProfile',
        component: () => import('@/views/UserProfile.vue'),
        meta: { title: '用户主页', hidden: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '首页'} - 绵城AI学习集市`
  const authStore = useAuthStore()

  if (to.path === '/login') {
    if (authStore.isLoggedIn) {
      next('/dashboard')
    } else {
      next()
    }
    return
  }

  if (!authStore.isLoggedIn) {
    next('/login')
    return
  }

  // 角色权限检查
  const requiredRoles = to.meta.roles
  if (requiredRoles && !requiredRoles.includes(authStore.role)) {
    next('/dashboard')
    return
  }

  next()
})

export default router
