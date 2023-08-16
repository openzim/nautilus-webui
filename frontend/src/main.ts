import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faPlus,
  faMinus,
  faXmark,
  faTrash,
  faFilePen,
  faAngleDown,
  faCheck,
  faSort,
  faFile,
} from '@fortawesome/free-solid-svg-icons'

/* add icons to the library */
library.add(faPlus, faMinus, faXmark, faTrash, faFilePen, faAngleDown, faCheck, faSort, faFile)

import App from './App.vue'
import router from './router'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)

app.mount('#app')
