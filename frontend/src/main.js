import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { TrendCharts, DataAnalysis, Money, Calendar } from '@element-plus/icons-vue'

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

// 只註冊實際使用的圖示
app.component('TrendCharts', TrendCharts)
app.component('DataAnalysis', DataAnalysis)
app.component('Money', Money)
app.component('Calendar', Calendar)

app.use(router)
app.use(ElementPlus)
app.mount('#app')