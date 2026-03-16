<script setup>
import { ref } from "vue"

const file = ref(null)
const uploading = ref(false)

function handleFileChange(event) {
  file.value = event.target.files[0]
}

async function uploadPhoto() {
  if (!file.value) return

  const formData = new FormData()
  formData.append("file", file.value)

  uploading.value = true

  try {
      await fetch("http://localhost:8000/photos/upload-test", {
        method: "POST",
        body: formData
      })

      alert("Upload complete!")
  } catch (error) {
      console.error(error)
      alert("Error uploading photo.")
  }
  uploading.value = false
}
</script>

<template>
  <div>
    <h1>Upload Photo</h1>

    <input
      type="file"
      @change="handleFileChange"
    />

    <button 
        @click="uploadPhoto"
        :disabled="uploading"
    >
      Upload
    </button>
  </div>
</template>