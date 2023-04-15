<template>
  <div
    v-for="message in messages"
    class="card mb-2"
    :class="message.author.species === 'ai' && 'bg-light'"
    :key="message.id"
  >
    <div class="card-body">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import type { Message } from '@/types/ainteraction/Message';

const { messages } = defineProps<{
  messages: Message[];
}>();
</script>
