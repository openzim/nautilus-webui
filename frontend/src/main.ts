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
  faUpload,
  faFile,
  faFileArrowDown,
  faFileExcel
} from '@fortawesome/free-solid-svg-icons'
import { faCircleXmark as farCircleXmark, faCopy } from '@fortawesome/free-regular-svg-icons'

/* add icons to the library */
library.add(
  faPlus,
  faMinus,
  faXmark,
  faTrash,
  faFilePen,
  faAngleDown,
  faCheck,
  faSort,
  faUpload,
  faFile,
  faFileArrowDown,
  farCircleXmark,
  faFileExcel,
  faCopy
)

import App from './App.vue'
import router from './router'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)

app.mount('#app')
