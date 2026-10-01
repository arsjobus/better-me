<template>
    <main class="flex min-h-screen items-center justify-center px-5 py-12">
      <section class="w-full max-w-md">
        <div class="mb-8 text-center">
          <div class="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-700 text-xl font-semibold text-white shadow-lg shadow-teal-900/15">B</div>
          <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-teal-700">A better day, one step at a time</p>
          <h1 class="font-serif text-4xl font-semibold tracking-tight text-slate-900">Welcome back</h1>
          <p class="mt-2 text-sm text-slate-500">Sign in to pick up where you left off.</p>
        </div>
        <form @submit.prevent="handleLogin" class="space-y-5 rounded-xl border border-slate-200/80 bg-white/90 p-6 shadow-xl shadow-slate-900/5 sm:p-8">
          <div class="space-y-2">
            <label for="username" class="block text-sm font-medium text-slate-700">Username</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            autocomplete="username"
            placeholder="Enter your username"
            class="w-full rounded-md border border-slate-300 bg-white px-3.5 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-teal-600 focus:ring-4 focus:ring-teal-600/10"
          />
        </div>
        <div class="space-y-2">
          <label for="password" class="block text-sm font-medium text-slate-700">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            autocomplete="current-password"
            placeholder="Enter your password"
            class="w-full rounded-md border border-slate-300 bg-white px-3.5 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-teal-600 focus:ring-4 focus:ring-teal-600/10"
          />
        </div>
        <button type="submit" :disabled="isLoading" class="w-full rounded-md bg-teal-700 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-800 focus:outline-none focus:ring-4 focus:ring-teal-700/20 disabled:cursor-wait disabled:opacity-60">
          {{ isLoading ? 'Logging in...' : 'Sign in' }}
        </button>
        <p v-if="errorMessage" role="alert" class="rounded-md bg-rose-50 px-3.5 py-3 text-sm text-rose-700">{{ errorMessage }}</p>
      </form>
      </section>
    </main>
</template>
  
<script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        username: '',
        password: '',
        isLoading: false,
        errorMessage: '',
      };
    },
    methods: {
        async handleLogin() {
            this.errorMessage = '';
            this.isLoading = true;
            try {
                const apiUrl = `${process.env.VUE_APP_API_BASE_URL}/auth/login`;
                const response = await axios.post(apiUrl, {
                    username: this.username,
                    password: this.password,
                });
                const { token } = response.data;
                this.$emit('login-success', token);
            } catch (error) {
                this.errorMessage = error.response?.data?.message || 'Login failed';
            } finally {
                this.isLoading = false;
            }
        },
    },
  }
</script>
  