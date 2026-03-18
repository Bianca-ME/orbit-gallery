<script setup>
import { ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const photos = ref([])
const loading = ref(true)

const isLoggedIn = computed(() => {
  if (process.client) return !!localStorage.getItem("token")
  return false
})

function logout() {
  localStorage.removeItem("token")
  router.push("/login")
}

onMounted(async () => {
  const res = await fetch("http://localhost:8000/photos")
  const data = await res.json()
  photos.value = data.items
  loading.value = false
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
        <p>{{ photo.owner_email }}</p>
        <div>
          <span v-for="tag in photo.tags" :key="tag">{{ tag }} </span>
        </div>
      </div>
    </div>
  </div>
</template>