<template>
  <div class="img-wrapper">
    <img ref="image_img_field" :src="'data:image/png;base64,' + props.value" class="border-0" />
    <div class="change-img-btn" @click="openFilePicker" title="Change">
      <font-awesome-icon :icon="['fas', 'upload']" />
    </div>
    <input class="form-control" type="file" ref="image_file_field" @change="updateImage" />
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/stores'
import { ref, type Ref } from 'vue'

const props = defineProps<{
  value?: string
  enforced_format?: string
  enforced_dimensions?: { width: number; height: number }
}>()

const emit = defineEmits<{
  change: [data: string]
}>()
const image_file_field: Ref<HTMLInputElement | null> = ref(null)
const image_img_field: Ref<HTMLImageElement | null> = ref(null)

const storeApp = useAppStore()

function openFilePicker() {
  if (image_file_field.value !== null) image_file_field.value.click()
}

const imageDimensions = (dataUrl: string) =>
  new Promise((resolve, reject) => {
    const img = new Image()

    // the following handler will fire after a successful loading of the image
    img.onload = () => {
      const { naturalWidth: width, naturalHeight: height } = img
      resolve({ width, height })
    }

    // and this handler will fire if there was an error with the image (like if it's not really an image or a corrupted one)
    img.onerror = () => {
      reject('failed to load image')
    }

    img.src = dataUrl
  })

function updateImage(event: Event) {
  if (event.target === null) return

  const target = event.target as HTMLInputElement
  if (target.files === null) return

  const file = target.files[0]
  const reader = new FileReader()
  if (!file) {
    console.error('updateImage failed without file')
    return
  }
  console.debug('file', file)

  reader.onload = async () => {
    console.log('onload')

    let error_message = 'Image must be '
    if (props.enforced_dimensions) {
      error_message += `a ${props.enforced_dimensions.width}x${props.enforced_dimensions.height}px `
    }
    if (props.enforced_format) {
      error_message += `${props.enforced_format.toUpperCase()} `
    }
    error_message += 'Image'

    if (reader.result instanceof ArrayBuffer) {
      storeApp.alertsError(`${error_message} (no result)`)
      return
    }
    let result: string = reader.result!

    let [prefix, bytes] = result.split(',', 2)
    let mimetype = prefix.replace(RegExp('^data:(.+);base64$'), '$1')
    if (props.enforced_format && mimetype != `image/${props.enforced_format}`) {
      console.error(error_message, mimetype)
      storeApp.alertsError(`${error_message} (not ${mimetype})`)
      return
    }

    if (props.enforced_dimensions) {
      // load on DOM to get dimensions
      const dimensions = { width: 0, height: 0 }
      await imageDimensions(result)
        .then(function (dim: any) {
          ;(dimensions.width = dim.width), (dimensions.height = dim.height)
        })
        .catch(function (error: string) {
          console.error('Image could not be loaded as image', error)
          storeApp.alertsError(`${error_message} (failed to load)`)
        })

      if (!dimensions.width || !dimensions.height) {
        console.log('failed to load', dimensions)
        return
      }

      if (dimensions.width != 48 || dimensions.height != 48) {
        console.error('Image dimensions are incorrect', dimensions)
        storeApp.alertsError(`${error_message} (not ${dimensions.width}x${dimensions.height}px)`)
        return
      }
    }

    if (image_img_field.value) image_img_field.value.src = 'data:image/png;base64,' + bytes

    emit('change', bytes)
  }
  reader.readAsDataURL(file)
}
</script>

<style type="text/css">
.img-wrapper {
  position: relative;
  box-sizing: content-box;
  border: 1px solid #333;
  overflow: hidden;
  /*width: 100%;
    height: 100%;*/
}
img {
  height: 100%;
}
div.change-img-btn {
  position: absolute;
  top: 0;
  /*    height: 1.5em;*/
  width: 100%;
  background-color: rgba(0, 0, 0, 0.4);
  color: white;
  cursor: pointer;
  text-align: center;
}
input[type='file'] {
  display: none;
}
</style>
