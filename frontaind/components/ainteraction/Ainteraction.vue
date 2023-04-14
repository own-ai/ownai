<script setup lang="ts">
import { ref } from 'vue';

const count = ref(0);
</script>

<template>
  <div class="card">
    <button type="button" class="btn btn-primary" @click="count++">
      count is {{ count }}
    </button>
  </div>
</template>

<style scoped>
.card {
  padding: 2rem;
}
</style>
