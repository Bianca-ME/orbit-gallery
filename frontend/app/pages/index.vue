<script setup>
import { ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const photos = ref([])
const loading = ref(true)
const currentUserEmail = ref(null)  

const isLoggedIn = computed(() => {
  if (process.client) return !!localStorage.getItem("token")
  return false
})

function logout() {
  localStorage.removeItem("token")
  currentUserEmail.value = null
  router.push("/login")
}

async function deletePhoto(photoId) {
  const token = localStorage.getItem("token")
  if (!token) return

  const confirmed = confirm("Delete this photo?")
  if (!confirmed) return

  await fetch(`http://localhost:8000/photos/${photoId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  // Remove from local list without reloading the page
  photos.value = photos.value.filter((p) => p.id !== photoId)
}

onMounted(async () => {
  const res = await fetch("http://localhost:8000/photos")
  const data = await res.json()
  photos.value = data.items
  loading.value = false

  // Decode the token to get current user email
  const token = localStorage.getItem("token")
  if (token) {
    const payload = JSON.parse(atob(token.split(".")[1]))
    currentUserEmail.value = payload.sub
  }
})
</script>

<template>
  <div>
    <header>
      <h1>ORBIT GALLERY</h1>
      <div>
        <NuxtLink to="/upload">+ Upload</NuxtLink>
        <button v-if="isLoggedIn" @click="logout">Sign out</button>
        <NuxtLink v-else to="/login">Sign in</NuxtLink>
      </div>
    </header>

    <div v-if="loading">Loading images...</div>

    <div v-else-if="photos.length === 0">
      <p>No images yet.</p>
      <NuxtLink to="/upload">Upload your first satellite image</NuxtLink>
    </div>

    <div v-else>
      <div v-for="photo in photos" :key="photo.id">
        <img :src="photo.thumbnail_url" :alt="photo.title" />
        <p>{{ photo.title }}</p>
        <p>Posted by {{ photo.owner_email }}</p>
        <div>
          <span v-for="tag in photo.tags" :key="tag">Tags: {{ tag }} </span>
        </div>
        <button
          v-if="currentUserEmail === photo.owner_email"
          @click="deletePhoto(photo.id)"
        >
          Delete
        </button>
      </div>
    </div>
  </div>
</template>