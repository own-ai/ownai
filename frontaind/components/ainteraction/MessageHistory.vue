<template>
  <div
    v-for="message in messages"
    class="card mb-2"
    :class="message.author.species === 'ai' && 'bg-light'"
    :key="message.id"
  >
    <div
      class="card-body"
      :class="message.status === 'writing' && 'writing'"
    >
      {{ message.text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '@/types/ainteraction/Message';

const { messages } = defineProps<{
  messages: Message[];
}>();
</script>

<style scoped>
@keyframes blink-animation {
  to {
    visibility: hidden;
  }
}

.writing::after {
  content: "";
  width: 1ch;
  height: 1em;
  background: var(--ownai-primary);
  display: inline-block;
  animation: blink-animation 1s steps(3, start) infinite;
}

.card-body {
  white-space: break-spaces;
}
</style>
