import { createApp } from 'vue'
import App from './App.vue'
import './styles/global.css'

const app = createApp(App)

app.directive('blur-on-click', {
  mounted(el: HTMLElement) {
    el.addEventListener('click', () => el.blur())
  },
})

app.mount('#app')
