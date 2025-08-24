<template>
    <BaseTaskList ref="baseTaskList">
      <template #header>
        <h1>Extended Task List</h1>
      </template>
      <template #footer>
        <button @click="performAdditionalAction">Perform Action</button>
      </template>
    </BaseTaskList>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  import BaseTaskList from './BaseTaskList.vue';
  
  export default defineComponent({
    name: "TaskListMorning",
    components: {
      BaseTaskList
    },
    methods: {
      performAdditionalAction() {
        console.log("Additional action performed!");
      }
    },
  });
  </script>
  
  <style scoped>
 
  </style>
  