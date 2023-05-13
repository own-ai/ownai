<template>
  <AiSelection
    :ai-definitions="aiDefinitions"
    :disabled="selectionDisabled"
    @select-ai="selectAi"
  />
  <KnowledgeSelection
    v-if="needsKnowledge"
    :knowledge-definitions="knowledgeDefinitions"
    :disabled="selectionDisabled"
    @select-knowledge="selectKnowledge"
  />
  <MessageHistory :messages="messages" />
  <MessageInput
    v-if="selectedAi && (!needsKnowledge || selectedKnowledge)"
    @send-message="sendMessage"
  />
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { io } from "socket.io-client";
import AiSelection from "./AiSelection.vue";
import KnowledgeSelection from "./KnowledgeSelection.vue";
import MessageHistory from "./MessageHistory.vue";
import MessageInput from "./MessageInput.vue";
import type { AiDefinition } from "@/types/ainteraction/AiDefinition";
import type { KnowledgeDefinition } from "@/types/ainteraction/KnowledgeDefinition";
import type { Message } from "@/types/ainteraction/Message";
import type { Token } from "@/types/ainteraction/Token";

const { ais, knowledges } = defineProps<{
  ais: string;
  knowledges: string;
}>();

const aiDefinitions: AiDefinition[] = JSON.parse(ais);
const knowledgeDefinitions: KnowledgeDefinition[] = JSON.parse(knowledges);

const selectedAi = ref<AiDefinition | null>(null);
const selectedKnowledge = ref<KnowledgeDefinition | null>(null);

const selectAi = (ai: AiDefinition) => {
  selectedAi.value = ai;
};
const selectKnowledge = (knowledge: KnowledgeDefinition) => {
  selectedKnowledge.value = knowledge;
};

const needsKnowledge = computed(
  () => !!selectedAi.value?.input_keys.includes("input_knowledge")
);
const selectionDisabled = ref<boolean>(false);

const messages = ref<Message[]>([]);
const nextMessageIndex = ref(0);

const socket = io();

socket.on("token", (incoming: Token) => {
  const message = messages.value[incoming.messageId];
  messages.value[incoming.messageId] = {
    ...message,
    text: message.text + incoming.text,
  };
});

socket.on("message", (incoming: Message) => {
  messages.value[incoming.id] = incoming;
});

const sendMessage = (text: string) => {
  selectionDisabled.value = true;
  const userMessage: Message = {
    id: nextMessageIndex.value++,
    author: {
      species: "human",
    },
    date: new Date(),
    text,
  };

  const aiResponse: Message = {
    id: nextMessageIndex.value++,
    author: {
      species: "ai",
    },
    date: new Date(),
    text: "",
    status: "writing",
  };

  messages.value.push(userMessage, aiResponse);
  socket.emit("message", {
    message: userMessage,
    responseId: aiResponse.id,
    aiId: selectedAi.value?.id,
    knowledgeId: selectedKnowledge.value?.id,
  });
};
</script>
