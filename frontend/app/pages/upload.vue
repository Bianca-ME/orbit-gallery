<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const file = ref(null)
const title = ref("")
const tags = ref("")
const uploading = ref(false)

onMounted(() => {
  if (!localStorage.getItem("token")) {
    router.push("/login")
  }
})

function handleFileChange(event) {
  file.value = event.target.files[0]
  if (file.value && !title.value) {
    title.value = file.value.name.replace(/\.[^.]+$/, "")
  }
}

async function uploadPhoto() {
  if (!file.value) return alert("Please select a file first.")
  if (!title.value) return alert("Please add a title.")

  const token = localStorage.getItem("token")
  if (!token) return router.push("/login")

  const formData = new FormData()
  formData.append("file", file.value)

  uploading.value = true

  try {
    const res = await fetch("http://localhost:8000/photos/upload-test", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    })

    if (!res.ok) throw new Error("Upload failed")

    const data = await res.json()

    const tagList = tags.value
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean)

    await fetch(`http://localhost:8000/photos/${data.id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
    },
      body: JSON.stringify({ title: title.value, tags: tagList }),
    })

    router.push("/")
  } catch (error) {
    console.error(error)
    alert("Error uploading photo.")
  }

  uploading.value = false
}
</script>

<template>
  <div>
    <NuxtLink to="/">← Back to Gallery</NuxtLink>

    <h1>Upload Photo</h1>

    <div>
      <label>File</label>
      <input type="file" accept="image/*" @change="handleFileChange" />
    </div>

    <div>
      <label>Title</label>
      <input v-model="title" type="text" placeholder="e.g. Amazon Deforestation 2024" />
    </div>

    <div>
      <label>Tags (comma separated)</label>
      <input v-model="tags" type="text" placeholder="e.g. forest, brazil, 2024" />
    </div>

    <button @click="uploadPhoto" :disabled="uploading">
      {{ uploading ? "Uploading..." : "Upload" }}
    </button>
  </div>
</template>