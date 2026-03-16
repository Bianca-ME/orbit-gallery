<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const email = ref("")
const password = ref("")
const error = ref("")
const loading = ref(false)

async function login() {
  error.value = ""
  loading.value = true

  try {
    // Backend expects form data (OAuth2 standard), not JSON
    const formData = new URLSearchParams()
    formData.append("username", email.value)  // FastAPI OAuth2 calls it "username"
    formData.append("password", password.value)

    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    })

    const data = await res.json()

    if (!res.ok) {
      error.value = data.detail || "Login failed."
      return
    }

    // Save the token to localStorage
    localStorage.setItem("token", data.access_token)

    // Go to gallery
    router.push("/")
  } catch (e) {
    error.value = "Something went wrong. Is the backend running?"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-950 text-white flex items-center justify-center">
    <div class="w-full max-w-sm bg-gray-900 border border-gray-800 rounded-2xl p-8">

      <h1 class="text-2xl font-bold mb-1">Welcome back</h1>
      <p class="text-gray-400 text-sm mb-8">Sign in to Orbit Gallery</p>

      <!-- Error -->
      <div v-if="error" class="bg-red-900 border border-red-700 text-red-300 text-sm rounded-lg px-4 py-3 mb-6">
        {{ error }}
      </div>

      <!-- Email -->
      <div class="mb-4">
        <label class="block text-sm text-gray-400 mb-1">Email</label>
        <input
          v-model="email"
          type="email"
          placeholder="you@example.com"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
        />
      </div>

      <!-- Password -->
      <div class="mb-8">
        <label class="block text-sm text-gray-400 mb-1">Password</label>
        <input
          v-model="password"
          type="password"
          placeholder="••••••••"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
        />
      </div>

      <!-- Submit -->
      <button
        @click="login"
        :disabled="loading"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white font-semibold py-3 rounded-lg transition"
      >
        {{ loading ? "Signing in..." : "Sign in" }}
      </button>

      <p class="text-center text-sm text-gray-500 mt-6">
        No account yet?
        <NuxtLink to="/register" class="text-blue-400 hover:underline">Create one</NuxtLink>
      </p>

    </div>
  </div>
</template>