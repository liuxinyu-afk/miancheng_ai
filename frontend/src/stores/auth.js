import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => user.value?.role || '')
  const nickname = computed(() => user.value?.nickname || '')
  const isAdmin = computed(() => role.value === 'admin')
  const isAuditor = computed(() => role.value === 'auditor' || role.value === 'admin')
  const isTeacher = computed(() => role.value === 'teacher')

  async function login(loginData) {
    const res = await authApi.login(loginData)
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    return res
  }

  async function fetchMe() {
    const res = await authApi.getMe()
    user.value = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
    return res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token, user, isLoggedIn, role, nickname,
    isAdmin, isAuditor, isTeacher,
    login, fetchMe, logout,
  }
})
