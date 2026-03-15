<script setup>
import { ref, onMounted } from 'vue'

const photos = ref([])
const loading = ref(true)

onMounted(async () => {
  const res = await fetch('http://localhost:8000/photos')
  const data = await res.json()

  photos.value = data.items
  loading.value = false
})
</script>

<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold mb-6">Orbit Gallery</h1>

    <div v-if="loading">
      Loading photos...
    </div>

    <div v-else class="grid grid-cols-3 gap-4">
      <div
        v-for="photo in photos"
        :key="photo.id"
        class="border rounded p-2"
      >
        <img
          :src="photo.thumbnail_url"
          class="w-full"
        />

        <p class="mt-2 text-sm">
          {{ photo.title }}
        </p>
      </div>
    </div>
  </div>
</template>