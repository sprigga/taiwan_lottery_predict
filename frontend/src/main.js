import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import Home from './views/Home.vue'
import Lotto649 from './views/Lotto649.vue'
import SuperLotto from './views/SuperLotto.vue'
import History from './views/History.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/lotto649', component: Lotto649 },
  { path: '/super-lotto', component: SuperLotto },
  { path: '/history', component: History }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)

// 註冊所有 Element Plus 圖示
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus)
app.mount('#app')