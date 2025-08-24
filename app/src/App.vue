<template>
  <div id="app">
    <TheLogin v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
    <TaskListMorning v-else />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import TaskListMorning from './components/TaskListMorning.vue';
import TheLogin from './components/TheLogin.vue';

export default defineComponent({
  name: 'App',
  components: {
    TaskListMorning,
    TheLogin
  },
  setup() {
    const isLoggedIn = ref(false);

    // Clear the JWT token on page load
    onMounted(() => {
      localStorage.removeItem('jwtToken');
    });

    const handleLoginSuccess = (token: string) => {
      localStorage.setItem('jwtToken', token);
      isLoggedIn.value = true;
    };

    return {
      isLoggedIn,
      handleLoginSuccess
    };
  }
});
</script>

<style lang="scss" scoped>
#app {
  text-align: center;
}
</style>