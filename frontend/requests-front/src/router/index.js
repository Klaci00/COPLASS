import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashBoardView from '../views/DashBoardView.vue'
import AccessRightRequestPost from '../views/AccessRightRequestPost.vue'
import RegisterView from '../views/RegisterView.vue'
import MessagesView from '../views/MessagesView.vue'
import AccessRightRequestList from '../views/AccessRightRequestList.vue'
import NewEmployeesListView from '../views/NewEmployeesListView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashBoardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/access-right-requests',
      name: 'access-right-requests',
      component: AccessRightRequestPost,
      meta: { requiresAuth: true }
    },
    {
      path: '/messages',
      name: 'messages',
      component: MessagesView,
      meta: { requiresAuth: true }
    },
    {
    path: '/access-right-requests/list',
    name: 'access-right-requests-list',
    component: AccessRightRequestList,
    meta: { requiresAuth: true }
},
    {
    path: '/new-employees',
    name: 'new-employees',
    component: NewEmployeesListView,
    meta: { requiresAuth: true }
}
  ]
})

// ✅ Navigation guard — protects all routes with requiresAuth: true
router.beforeEach((to) => {
  const isLoggedIn = !!localStorage.getItem('token')
  if (to.meta.requiresAuth && !isLoggedIn) {
    return { name: 'login' }
  }
  if ((to.name === 'login' || to.name === 'register') && isLoggedIn) {
    return { name: 'dashboard' }
  }
})

export default router