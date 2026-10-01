<template>
  <main class="mx-auto w-full max-w-3xl px-5 py-10 sm:py-14">
    <header class="mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
      <div>
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-teal-700">Your daily reset</p>
        <h1 class="font-serif text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">Make room for what matters.</h1>
        <p class="mt-2 text-sm text-slate-500">Small, consistent steps add up.</p>
      </div>
      <div class="inline-flex w-fit items-center gap-2 rounded-full border border-teal-200 bg-white/80 px-4 py-2 text-sm shadow-sm">
        <span class="font-semibold text-teal-800">{{ completedTasks }}</span>
        <span class="text-slate-500">of {{ totalTasks }} complete</span>
      </div>
    </header>

    <section class="overflow-hidden rounded-xl border border-slate-200/80 bg-white shadow-xl shadow-slate-900/5">
      <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4 sm:px-6">
        <h2 class="text-sm font-semibold text-slate-800">Today's tasks</h2>
        <span class="text-xs font-medium text-slate-400">{{ totalTasks }} {{ totalTasks === 1 ? 'task' : 'tasks' }}</span>
      </div>
      <ul class="max-h-[52vh] divide-y divide-slate-100 overflow-y-auto">
        <li
          v-for="(task, index) in tasks"
          :key="index"
          class="group flex items-center justify-between gap-3 px-5 py-4 transition-colors hover:bg-slate-50 sm:px-6"
          :class="{ 'bg-teal-50/40': task.completed }"
        >
          <div class="flex min-w-0 items-start gap-3">
            <input
              :id="task.id.toString()"
              type="checkbox"
              :checked="task.completed"
              @change="toggleTaskCompletion(index)"
              class="mt-0.5 h-5 w-5 shrink-0 cursor-pointer rounded border-slate-300 accent-teal-700 focus:ring-teal-600"
            />
            <label
              :for="task.id.toString()"
              class="min-w-0 cursor-pointer break-words text-sm leading-6 text-slate-700"
              :class="{ 'text-slate-400 line-through': task.completed }"
            >{{ task.title }}</label>
          </div>
          <button
            @click="confirmAndRemoveTask(index)"
            aria-label="Remove task"
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-lg leading-none text-slate-400 transition hover:bg-rose-50 hover:text-rose-600 focus:outline-none focus:ring-2 focus:ring-rose-500/30 sm:opacity-0 sm:group-hover:opacity-100 sm:focus:opacity-100"
          >
            x
          </button>
        </li>
        <li v-if="!tasks.length" class="px-6 py-12 text-center">
          <p class="font-serif text-lg text-slate-700">A fresh start.</p>
          <p class="mt-1 text-sm text-slate-500">Add one small task to get moving.</p>
        </li>
      </ul>

      <div class="border-t border-slate-100 bg-slate-50/70 px-5 py-5 sm:px-6">
        <TheProgressBar :totalTasks="totalTasks" :completedTasks="completedTasks" />
        <div class="mt-5 flex flex-col gap-3 sm:flex-row">
          <input
            v-model="newTask"
            type="text"
            placeholder="What would you like to get done?"
            @keyup.enter="addTask"
            class="min-w-0 flex-1 rounded-md border border-slate-300 bg-white px-3.5 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-teal-600 focus:ring-4 focus:ring-teal-600/10"
          />
          <button @click="addTask" class="inline-flex items-center justify-center gap-2 rounded-md bg-teal-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-800 focus:outline-none focus:ring-4 focus:ring-teal-700/20">
            <span aria-hidden="true" class="text-lg font-normal leading-none">+</span>
            Add task
          </button>
        </div>
      </div>
    </section>

    <div class="flex justify-end pt-4">
      <button @click="resetAllTasks" class="rounded-md px-3 py-2 text-sm font-medium text-slate-500 transition hover:bg-white/70 hover:text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400/30">
        Reset all tasks
      </button>
    </div>
  </main>
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
