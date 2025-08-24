<template>
    <div role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80">
        <div :style="{ width: progressPercentage + '%' }"></div>
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
  
<style scoped>
    .progress-bar-container {
        background-color: #f0f0f0; /* Background color similar to Windows 7 */
        border: 1px solid #b0b0b0; /* Border color */
        border-radius: 3px; /* Rounded corners */
        position: relative; /* Position for progress bar */
        height: 24px; /* Height of the progress bar container */
        margin-bottom: 10px; /* Spacing between progress bar and other elements */
    }

    .progress-bar {
        background-color: #0078d7; /* Progress bar color (Windows blue) */
        height: 100%; /* Fill the height of the container */
        border-radius: 3px; /* Rounded corners */
        transition: width 0.3s ease; /* Smooth transition for width change */
    }

    .progress-text {
        position: absolute; /* Absolute position for centering text */
        top: 2px; /* Center the text vertically */
        left: 50%; /* Center the text horizontally */
        transform: translateX(-50%); /* Adjust for text width */
        color: #333; /* Text color */
        font-size: 14px; /* Text size */
    }
</style>