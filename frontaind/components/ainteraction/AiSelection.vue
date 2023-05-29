<template>
  <div
    class="d-flex align-items-center justify-content-center gap-2"
    :class="needsKnowledge ? 'mb-2' : 'mb-4'"
  >
    <div
      :class="
        needsKnowledge ? 'col-sm-2 col-lg-1 d-flex justify-content-end' : ''
      "
    >
      <span class="badge rounded-pill text-bg-primary">AI</span>
    </div>
    <div v-if="!aiDefinitions.length" class="flex-grow-1">
      <strong>No AI found. Please set up an AI first.</strong>
    </div>
    <div v-else-if="disabled" class="flex-grow-1">
      <strong>{{ selectedAi?.name }}</strong>
    </div>
    <div v-else class="dropdown flex-grow-1">
      <button
        class="btn btn-light border dropdown-toggle d-block w-100 text-start"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        {{ selectedAi ? selectedAi.name : "Select AI" }}
      </button>
      <ul class="dropdown-menu w-100 m-0">
        <li v-for="aiDefinition in aiDefinitions" :key="aiDefinition.id">
          <a
            class="dropdown-item d-flex align-items-center gap-2 py-2"
            @click="selectAi(aiDefinition)"
          >
            <span
              class="d-inline-block rounded-circle p-1"
              :class="getAiColor(aiDefinition)"
              :title="getAiCapabilitiesHint(aiDefinition)"
            ></span>
            {{ aiDefinition.name }}
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type { AiDefinition } from "@/types/ainteraction/AiDefinition";

const { aiDefinitions, disabled } = defineProps<{
  aiDefinitions: AiDefinition[];
  disabled: boolean;
}>();

const emit = defineEmits(["select-ai"]);
const selectedAi = ref<AiDefinition | null>(null);

const selectAi = (aiDefinition: AiDefinition) => {
  emit("select-ai", aiDefinition);
  selectedAi.value = aiDefinition;
};

const usesKnowledge = (aiDefinition: AiDefinition) => {
  return aiDefinition.input_keys.includes("input_knowledge");
};

const needsKnowledge = computed(
  () => !!selectedAi.value && usesKnowledge(selectedAi.value)
);

const getAiColor = (aiDefinition: AiDefinition) => {
  if (usesKnowledge(aiDefinition)) {
    return "bg-warning";
  }
  return "bg-secondary";
};

const getAiCapabilitiesHint = (aiDefinition: AiDefinition) => {
  if (usesKnowledge(aiDefinition)) {
    return "Understands text input and can access additional knowledge.";
  }
  return "Understands text input.";
};

if (aiDefinitions.length) {
  selectAi(aiDefinitions[0]);
}
</script>

<style scoped>
.dropdown-toggle,
.dropdown-item {
  white-space: normal;
}
</style>
