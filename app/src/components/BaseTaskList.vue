<template>
  <div class="window active checklist">
    <div class="title-bar">
      <div class="title-bar-text">To-Do List</div>
      <div class="title-bar-controls">
        <button aria-label="Minimize"></button>
        <button aria-label="Maximize"></button>
        <button aria-label="Close"></button>
      </div>
    </div>
    <div class="window-body has-space">
      <ul class="has-scrollbar" style="height: 70vh; overflow: auto">
        <li 
          v-for="(task, index) in tasks" 
          :key="index" 
          :class="{ 'completed': task.completed, 'field-row': true, }" 
        >
          <div>
            <input
              :id="task.id.toString()"
              type="checkbox"
              :checked="task.completed"
              @change="toggleTaskCompletion(index)"
              class="checkbox"
            />
            <label :for="task.id.toString()" class="task-title" :class="{ 'line-through': task.completed }">{{ task.title }}</label>
          </div>
          <button @click="confirmAndRemoveTask(index)" class="remove-button">
            ✖
          </button>
        </li>
      </ul>
      <TheProgressBar :totalTasks="totalTasks" :completedTasks="completedTasks"></TheProgressBar>
      <div class="new-task field-row">
        <input
          v-model="newTask"
          type="text"
          placeholder="Add a new task"
          @keyup.enter="addTask"
          class="new-task-input"
        />
        <button @click="addTask" class="add-button">
          Add
        </button>
      </div>
      <div>
        <button @click="resetAllTasks" class="reset-button">
          Reset All Tasks
        </button>
      </div>
    </div>
  </div>
</template>
  
<script lang="ts">
import { defineComponent } from 'vue';
import TheProgressBar from './TheProgressBar.vue';

interface Task {
  id: number;
  title: string;
  completed: boolean;
}

export default defineComponent({
  name: "BaseTaskList",
  components: {
    TheProgressBar
  },
  data() {
    return {
      tasks: [] as Task[],
      newTask: "",
    };
  },
  computed: {
    totalTasks(): number {
      return this.tasks.length;
    },
    completedTasks(): number {
      return this.tasks.filter(task => task.completed).length;
    }
  },
  mounted() {
    this.loadTasks();
  },
  methods: {
    getAuthHeaders() {
      const token = localStorage.getItem('jwtToken');
      return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      };
    },
    async loadTasks() {
      try {
        const apiUrl = `${process.env.VUE_APP_API_BASE_URL}/tasks`;
        const response = await fetch(apiUrl, {
          headers: this.getAuthHeaders(),
        });
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        this.tasks = data.tasks;
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    },
    async addTask() {
      if (this.newTask.trim()) {
        const newTask = { title: this.newTask, completed: false, last_updated: Date.now(), next_timeout: this.getNextTimeout() };
        try {
          const apiUrl = `${process.env.VUE_APP_API_BASE_URL}/tasks`;
          const response = await fetch(apiUrl, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(newTask),
          });
          if (!response.ok) throw new Error('Network response was not ok');
          const data = await response.json();
          this.tasks.push(data.task);
          this.newTask = ""; // Reset the input field
        } catch (error) {
          console.error('Error adding task:', error);
        }
      }
    },
    getNextTimeout() {
      const currentDate = new Date();
      const tomorrow = new Date(currentDate);
      tomorrow.setDate(currentDate.getDate() + 1);
      tomorrow.setHours(8, 0, 0, 0);
      return tomorrow.getTime();
    },
    async resetAllTasks() {
      const confirmed = confirm("Are you sure you want to reset all tasks to incomplete?");
      if (!confirmed) return;
      try {
        const apiUrl = `${process.env.VUE_APP_API_BASE_URL}/tasks`;
        await Promise.all(
          this.tasks.map(async (task) => {
            task.completed = false;
            await fetch(`${apiUrl}/${task.id}`, {
              method: 'PUT',
              headers: this.getAuthHeaders(),
              body: JSON.stringify({ completed: false, last_updated: Date.now(), next_timeout: this.getNextTimeout() }),
            });
          })
        );
      } catch (error) {
        console.error('Error resetting tasks:', error);
      }
    },
    async toggleTaskCompletion(index: number) {
      const task = this.tasks[index];
      task.completed = !task.completed;
      try {
        const apiUrl = `${process.env.VUE_APP_API_BASE_URL}/tasks`;
        await fetch(`${apiUrl}/${task.id}`, {
          method: 'PUT',
          headers: this.getAuthHeaders(),
          body: JSON.stringify({ completed: task.completed, last_updated: Date.now(), next_timeout: this.getNextTimeout() }),
        });
      } catch (error) {
        console.error('Error updating task completion:', error);
      }
    },
    confirmAndRemoveTask(index: number) {
      const confirmed = confirm("Are you sure you want to delete this task?");
      if (confirmed) {
        const task = this.tasks[index];
        const apiUrl = `${process.env.VUE_APP_API_BASE_URL}/tasks`;
        fetch(`${apiUrl}/${task.id}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders(), // Include the token in the delete request
        }).then(() => {
          this.tasks.splice(index, 1); // Remove the task from the local array
        }).catch(error => {
          console.error('Error deleting task:', error);
        });
      }
    },
  },
});
</script>

<style scoped>
  .window {
    margin: 10px;
  }

  .field-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px;
    border-bottom: 1px solid #ccc;
    margin: 0 !important;
  }

  .checkbox {
    cursor: pointer;
  }

  .checklist ul {
    padding: 0;
  }

  .line-through {
    text-decoration: line-through;
  }

  .reset-button {
    margin-top: 20px;
    margin-bottom: 14px;
  }
</style>
