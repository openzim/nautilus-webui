<template>
  <div class="container help">
    <div class="row justify-content-md-center">
      <h1 v-if="showTitle">Frequently Asked Questions</h1>
      <ul class="list-group list-group-flush">
        <li class="list-group-item" v-for="(item, index) in faqs" :key="item.title">
          <div class="d-grid">
            <button
              type="button"
              class="btn px-0"
              data-bs-toggle="collapse"
              :data-bs-target="'#collapse' + index"
              aria-expanded="false"
              :aria-controls="'collapse' + index"
              @click="toggleCollapse(index)"
            >
              <div class="container px-0">
                <div class="row align-items-start justify-content-start">
                  <div class="col-md-auto">{{ item.title }}</div>
                  <div class="col" />
                  <div class="col-md-auto">
                    <font-awesome-icon v-if="!item.toggle" :icon="['fas', 'plus']" />
                    <font-awesome-icon v-else :icon="['fas', 'minus']" />
                  </div>
                </div>
              </div>
            </button>
          </div>
          <div
            class="collapse mt-3 text-secondary"
            :id="'collapse' + index"
            v-html="item.content"
          ></div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { humanifyFileSize } from '@/constants'
import { useAppStore } from '@/stores/stores'
defineProps({showTitle: Boolean})
const storeApp = useAppStore()
const faqs = ref([
  {
    title: 'What is a Zim file',
    content: `<p>The Zim file format stores website content for
    <a href="https://en.wikipedia.org/wiki/Online_and_offline">offline</a>
    usage. It assembles the normal constituent of a website into a single archive, and compresses it so as to make it easier to save, share, and store.</p>`,
    toggle: false
  },
  {
    title: 'How do I read my Zim files?',
    content: `<p>
    You will need a Zim file reader. This usually means
    <a href="https://kiwix.org/">Kiwix</a>,
    which is available on
    <a href="https://www.kiwix.org/en/download/">desktop computers, mobile devices, and more.</a>
    Currently only Kiwix-serve and Kiwix-Android can read all Zimit-generated files.
    If using Kiwix-Desktop for Microsoft Windows and GNU/Linux, then you will need to configure it as a Kiwix-serve instance in the settings.
    We expect most platforms to be upgraded by the end of 2021.
    </p>`,
    toggle: false
  },
  {
    title: 'Why can not I create a Zim file of any size?',
    content: `<p>
      Due to the nature of the tool, we cannot allow it to create files of arbitrary size. 
      This could be detrimental to our infrastructure. 
      We currently enforce a limit: ${humanifyFileSize(storeApp.constants.env.NAUTILUS_PROJECT_QUOTA)} files.
      </p>`,
    toggle: false
  },
  {
    title: 'I can not create a Zim file',
    content: `<p>
      If you have any problems creating a Zim file, please reflect them on
      <a href="https://github.com/openzim/nautilus-webui/issues">Github</a>.
      </p>`,
    toggle: false
  }
])
function toggleCollapse(index: number) {
  faqs.value[index].toggle = !faqs.value[index].toggle
}
</script>

<style scoped>
.help {
  width: 50em;
}

.help:deep(a) {
  color: var(--main-color);
}
</style>
<style scoped>
.help {
  width: 50em;
}

.help:deep(a) {
  color: var(--main-color);
}
</style>
