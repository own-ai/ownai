<template>
  <div class="ainteraction-container">
    <AiSelection
      :ais="parsedAis"
      :disabled="selectionDisabled"
      :selected-ai="selectedAi"
      @select-ai="selectAi"
    />
    <KnowledgeSelection
      v-if="needsKnowledge"
      :knowledges="parsedKnowledges"
      :disabled="selectionDisabled"
      @select-knowledge="selectKnowledge"
    />
    <MessageHistory
      :greeting="selectedAi?.greeting"
      :messages="messages"
      @clear-messages="clearMessages"
    />
    <MessageInput
      v-if="selectedAi && (!needsKnowledge || selectedKnowledge)"
      :label="textInputLabel"
      @send-message="sendMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { io } from "socket.io-client";
import AiSelection from "./AiSelection.vue";
import KnowledgeSelection from "./KnowledgeSelection.vue";
import MessageHistory from "./MessageHistory.vue";
import MessageInput from "./MessageInput.vue";
import { slugify } from "@/helpers/slugify";
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

const route = useRoute();
const router = useRouter();

const selectAi = (ai: BasicAi) => {
  selectedAi.value = ai;
  router.push({ params: { ai: slugify(ai.name) } });
};
const selectKnowledge = (knowledge: BasicKnowledge) => {
  selectedKnowledge.value = knowledge;
};

const selectAiFromParams = (aiParam: string | string[]) => {
  if (!aiParam) {
    return;
  }
  if (Array.isArray(aiParam)) {
    aiParam = aiParam[0];
  }

  let ai: BasicAi | undefined;
  const aiParamAsNumber = parseInt(aiParam);
  if (Number.isInteger(aiParamAsNumber)) {
    ai = parsedAis.find((ai) => ai.id === aiParamAsNumber);
  } else {
    ai = parsedAis.find((ai) => slugify(ai.name) === aiParam);
  }

  if (ai) {
    selectAi(ai);
    clearMessages();
  }
};

onMounted(async () => {
  selectAiFromParams(route.params.ai);
});

watch(() => route.params.ai, selectAiFromParams);

const needsKnowledge = computed(
  () => !!selectedAi.value?.input_keys.includes("input_knowledge")
);
const textInputLabel = computed(
  () => selectedAi.value?.input_labels?.input_text || "Send a message"
);
const selectionDisabled = ref<boolean>(false);

const messages = ref<Message[]>([]);
const nextMessageIndex = ref(0);

const socket = io();

socket.on("token", (incoming: Token) => {
  if (messages.value.length <= incoming.messageId) {
    return;
  }
  const message = messages.value[incoming.messageId];
  messages.value[incoming.messageId] = {
    ...message,
    text: message.text + incoming.text,
  };
});

socket.on("message", (incoming: Message) => {
  if (messages.value.length <= incoming.id) {
    return;
  }
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

const clearMessages = () => {
  messages.value = [];
  nextMessageIndex.value = 0;
  selectionDisabled.value = false;
};
</script>

<style scoped>
.ainteraction-container {
  max-width: 40rem;
  margin: 0 auto;
}
</style>
