<template>
  <MessageHistory :messages="messages" />
  <MessageInput @send-message="sendMessage" />
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import MessageHistory from './MessageHistory.vue';
import MessageInput from './MessageInput.vue';
import type { Message } from '@/types/ainteraction/Message';

const messages = reactive<Message[]>([]);
const nextMessageId = ref(1);

const sendMessage = async (text: string) => {
  messages.push({
    id: nextMessageId.value++,
    author: {
      species: 'human',
    },
    date: new Date(),
    text,
  });
  messages.push({
    id: nextMessageId.value++,
    author: {
      species: 'ai',
    },
    date: new Date(),
    text: '42',
  });
};
</script>
