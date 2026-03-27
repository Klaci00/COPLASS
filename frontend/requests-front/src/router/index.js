import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashBoardView from '../views/DashboardView.vue' 
import AccessRightRequestPost from '../views/AccessRightRequestPost.vue'
import RegisterView from '../views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashBoardView
    },
    {
      path: '/access-right-requests',
      name: 'access-right-requests',
      component: AccessRightRequestPost
    },
    {
      path: '/register_employee',
      name: 'register_employee',
      component: RegisterView
    }
    // ... your other routes
  ]
})

export default router