import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { ElLoading } from 'element-plus'
import router from './router'
import App from './App.vue'
import { i18n } from './i18n'
import './assets/main.css'

if (import.meta.env.VITE_USE_MOCK === 'true') {
  const { startMockWorker } = await import('./api/mock')
  await startMockWorker()
}

const app = createApp(App)
app.use(createPinia())
app.use(i18n)
app.use(router)
app.directive('loading', ElLoading.directive)
app.mount('#app')
