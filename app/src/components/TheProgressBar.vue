<template>
    <div class="space-y-2">
      <div class="flex items-center justify-between text-xs">
        <span class="font-medium text-slate-600">Daily progress</span>
        <span class="tabular-nums text-slate-500">{{ Math.round(progressPercentage) }}% complete</span>
      </div>
      <div
        role="progressbar"
        aria-label="Task completion"
        aria-valuemin="0"
        aria-valuemax="100"
        :aria-valuenow="Math.round(progressPercentage)"
        class="h-2 overflow-hidden rounded-full bg-slate-200"
      >
        <div class="h-full rounded-full bg-teal-600 transition-[width] duration-500 ease-out" :style="{ width: progressPercentage + '%' }"></div>
      </div>
    </div>
</template>  
  
<script>
  export default {
    name: 'ProgressBar',
    props: {
      totalTasks: {
        type: Number,
        required: true
      },
      completedTasks: {
        type: Number,
        required: true
      }
    },
    computed: {
      progressPercentage() {
        return this.totalTasks > 0 ? (this.completedTasks / this.totalTasks) * 100 : 0;
      }
    }
  };
</script>