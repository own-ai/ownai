<template>
  <div v-if="greeting" class="card mb-2 bg-light">
    <div class="card-body">
      {{ greeting }}
    </div>
  </div>
  <div
    v-for="message in messages"
    class="card mb-2"
    :class="message.author.species === 'ai' && 'bg-light'"
    :key="message.id"
  >
    <div v-if="message.status === 'writing' && !message.text" class="card-body">
      <div
        class="progress"
        role="progressbar"
        aria-label="Progress"
        :aria-valuenow="progresses[message.id]"
        aria-valuemin="0"
        aria-valuemax="100"
      >
        <div
          class="progress-bar"
          :style="`width: ${progresses[message.id]}%`"
        ></div>
      </div>
    </div>
    <div v-else class="card-body" :class="message.status">
      <span class="d-none badge text-bg-danger error-badge me-2">Error 😩</span
      >{{ message.text }}
    </div>
  </div>
  <small v-if="messages.length" class="text-muted">
    AI responses may contain inaccurate or inappropriate information. Please
    check the content carefully before using it.
    <a href="#" @click.prevent="emit('clear-messages')">Clear all messages.</a>
  </small>
</template>

<script setup lang="ts">
import type { Message } from "@/types/ainteraction/Message";

const { greeting, messages, progresses } = defineProps<{
  greeting?: string;
  messages: Message[];
  progresses: number[];
}>();
const emit = defineEmits(["clear-messages"]);
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

.error .error-badge {
  display: inline-block !important;
}

.card-body {
  white-space: break-spaces;
}
</style>
