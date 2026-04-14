import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { resolveRouteRedirect } from './guard'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: () => import('../views/auth/LoginView.vue') },
  { path: '/dashboard', component: () => import('../views/system/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/avatars', component: () => import('../views/avatars/AvatarListView.vue'), meta: { requiresAuth: true } },
  { path: '/avatars/new', component: () => import('../views/avatars/AvatarCreateView.vue'), meta: { requiresAuth: true } },
  { path: '/avatars/:id', component: () => import('../views/avatars/AvatarDetailView.vue'), meta: { requiresAuth: true } },
  { path: '/persona', component: () => import('../views/persona/PersonaView.vue'), meta: { requiresAuth: true } },
  { path: '/avatars/:avatarId/persona', component: () => import('../views/persona/PersonaView.vue'), meta: { requiresAuth: true } },
  { path: '/agents', component: () => import('../views/agents/AgentView.vue'), meta: { requiresAuth: true } },
  { path: '/avatars/:avatarId/agents', component: () => import('../views/agents/AgentView.vue'), meta: { requiresAuth: true } },
  { path: '/tasks', component: () => import('../views/tasks/TaskView.vue'), meta: { requiresAuth: true } },
  { path: '/memories', redirect: '/memories/pending' },
  { path: '/memories/pending', component: () => import('../views/memory/MemoryView.vue'), meta: { requiresAuth: true } },
  { path: '/memories/search', component: () => import('../views/memory/MemorySearchView.vue'), meta: { requiresAuth: true } },
  { path: '/audit', component: () => import('../views/audit/AuditView.vue'), meta: { requiresAuth: true } },
  { path: '/settings', component: () => import('../views/settings/SettingsView.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', component: () => import('../views/system/NotFoundView.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  return resolveRouteRedirect(to, auth.isAuthenticated)
})

export default router
