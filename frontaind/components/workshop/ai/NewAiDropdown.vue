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
      <li><hr class="dropdown-divider" /></li>
      <li>
        <a
          href="http://aifiles.ownai.org/?aifileversion=1"
          target="_blank"
          rel="noopener noreferrer"
          class="dropdown-item d-flex gap-2"
        >
          Find Examples
          <div class="text-secondary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="12"
              height="12"
              fill="currentColor"
              class="bi bi-box-arrow-up-right align-baseline"
              viewBox="0 0 16 16"
            >
              <path
                fill-rule="evenodd"
                d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"
              />
              <path
                fill-rule="evenodd"
                d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"
              />
            </svg>
          </div>
        </a>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits(["load", "create"]);
</script>
