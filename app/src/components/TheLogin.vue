<template>
    <div class="login-container">
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Username </label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            placeholder="Enter your username"
          />
        </div>
        <div class="form-group">
          <label for="password">Password </label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="Enter your password"
          />
        </div>
        <button type="submit" :disabled="isLoading">
          {{ isLoading ? 'Logging in...' : 'Login' }}
        </button>
        <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
      </form>
    </div>
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
  };
</script>
  
<style scoped>
  .login-container {
    max-width: 400px;
    margin: auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: #f9f9f9;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  .error {
    color: red;
    margin-top: 10px;
  }
</style>
  