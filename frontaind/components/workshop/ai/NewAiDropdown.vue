<template>
  <div class="dropdown">
    <button
      class="btn btn-outline-primary dropdown-toggle"
      type="button"
      data-bs-toggle="dropdown"
      aria-expanded="false"
    >
      New AI
    </button>
    <ul class="dropdown-menu shadow">
      <li>
        <a class="dropdown-item" href="#" @click.prevent="emit('load')">
          Load Aifile
        </a>
      </li>
      <li>
        <a class="dropdown-item" href="#" @click.prevent="emit('create')">
          Create Empty
        </a>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits(["load", "create"]);
</script>
