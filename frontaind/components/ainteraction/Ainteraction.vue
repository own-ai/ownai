<template>
  <MessageHistory :messages="messages" />
  <MessageInput @send-message="sendMessage" />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { io } from 'socket.io-client';
import MessageHistory from './MessageHistory.vue';
import MessageInput from './MessageInput.vue';
import type { Message } from '@/types/ainteraction/Message';
import type { Token } from '@/types/ainteraction/Token';

const messages = ref<Message[]>([]);
const nextMessageIndex = ref(0);

const socket = io();

socket.on('token', (incoming: Token) => {
  const message = messages.value[incoming.messageId];
  messages.value[incoming.messageId] = {
    ...message,
    text: message.text + incoming.text,
  };
});

socket.on('message', (incoming: Message) => {
  messages.value[incoming.id] = incoming;
});

const sendMessage = (text: string) => {
  const userMessage: Message = {
    id: nextMessageIndex.value++,
    author: {
      species: 'human',
    },
    date: new Date(),
    text,
  };

  const aiResponse: Message = {
    id: nextMessageIndex.value++,
    author: {
      species: 'ai',
    },
    date: new Date(),
    text: '',
    status: 'writing',
  };

  messages.value.push(userMessage, aiResponse);
  socket.emit('message', { message: userMessage, responseId: aiResponse.id });
};
</script>
