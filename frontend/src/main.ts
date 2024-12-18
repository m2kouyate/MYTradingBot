import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
// import router from './router'
import { router } from './router'
import { setupValidation } from './utils/validation'
import './style.css'

setupValidation()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')