<template>
  <AiSelection
    :ais="parsedAis"
    :disabled="selectionDisabled"
    @select-ai="selectAi"
  />
  <KnowledgeSelection
    v-if="needsKnowledge"
    :knowledges="parsedKnowledges"
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
import type { BasicAi } from "@/types/ainteraction/BasicAi";
import type { BasicKnowledge } from "@/types/ainteraction/BasicKnowledge";
import type { Message } from "@/types/ainteraction/Message";
import type { Token } from "@/types/ainteraction/Token";

const { ais, knowledges } = defineProps<{
  ais: string;
  knowledges: string;
}>();

const parsedAis: BasicAi[] = JSON.parse(ais);
const parsedKnowledges: BasicKnowledge[] = JSON.parse(knowledges);

const selectedAi = ref<BasicAi | null>(null);
const selectedKnowledge = ref<BasicKnowledge | null>(null);

const selectAi = (ai: BasicAi) => {
  selectedAi.value = ai;
};
const selectKnowledge = (knowledge: BasicKnowledge) => {
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
  if (!incoming.text) {
    // Workaround until https://github.com/hwchase17/langchain/pull/6211 is merged
    incoming.text = messages.value[incoming.id].text;
  }
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
    status: "done",
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

  const history = messages.value.filter((message) => message.status === "done");

  messages.value.push(userMessage, aiResponse);
  socket.emit("message", {
    message: userMessage,
    responseId: aiResponse.id,
    aiId: selectedAi.value?.id,
    knowledgeId: selectedKnowledge.value?.id,
    history,
  });
};
</script>
