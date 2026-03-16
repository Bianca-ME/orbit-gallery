<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const email = ref("")
const password = ref("")
const error = ref("")
const loading = ref(false)

async function register() {
  error.value = ""
  loading.value = true

  try {
    const res = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email.value, password: password.value }),
    })

    const data = await res.json()

    if (!res.ok) {
      error.value = data.detail || "Registration failed."
      return
    }

    // Registration worked — go to login
    router.push("/login")
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

      <h1 class="text-2xl font-bold mb-1">Create account</h1>
      <p class="text-gray-400 text-sm mb-8">Join Orbit Gallery</p>

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
        @click="register"
        :disabled="loading"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white font-semibold py-3 rounded-lg transition"
      >
        {{ loading ? "Creating account..." : "Create account" }}
      </button>

      <p class="text-center text-sm text-gray-500 mt-6">
        Already have an account?
        <NuxtLink to="/login" class="text-blue-400 hover:underline">Sign in</NuxtLink>
      </p>

    </div>
  </div>
</template>