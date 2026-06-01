import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
  },
  {
    path: '/subjects',
    name: 'SubjectList',
    component: () => import('@/views/SubjectList.vue'),
  },
  {
    path: '/subjects/:bangumiId',
    name: 'SubjectDetail',
    component: () => import('@/views/SubjectDetail.vue'),
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/Search.vue'),
  },
  {
    path: '/records',
    name: 'MyRecords',
    component: () => import('@/views/MyRecords.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
