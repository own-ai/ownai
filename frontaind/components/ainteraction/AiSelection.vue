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
    <div v-if="!ais.length" class="flex-grow-1">
      <strong
        >No AI found. Please
        <a href="/workshop/ai">set up an AI</a> first.</strong
      >
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
        <li v-for="ai in ais" :key="ai.id">
          <a
            class="dropdown-item d-flex align-items-center gap-2 py-2"
            @click="selectAi(ai)"
          >
            <span
              class="d-inline-block rounded-circle p-1"
              :class="getAiColor(ai)"
              :title="getAiCapabilitiesHint(ai)"
            ></span>
            {{ ai.name }}
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type { BasicAi } from "@/types/ainteraction/BasicAi";

const { ais, disabled } = defineProps<{
  ais: BasicAi[];
  disabled: boolean;
}>();

const emit = defineEmits(["select-ai"]);
const selectedAi = ref<BasicAi | null>(null);

const selectAi = (ai: BasicAi) => {
  emit("select-ai", ai);
  selectedAi.value = ai;
};

const usesKnowledge = (ai: BasicAi) => {
  return ai.input_keys.includes("input_knowledge");
};

const needsKnowledge = computed(
  () => !!selectedAi.value && usesKnowledge(selectedAi.value)
);

const getAiColor = (ai: BasicAi) => {
  if (usesKnowledge(ai)) {
    return "bg-warning";
  }
  return "bg-secondary";
};

const getAiCapabilitiesHint = (ai: BasicAi) => {
  if (usesKnowledge(ai)) {
    return "Understands text input and can access additional knowledge.";
  }
  return "Understands text input.";
};

if (ais.length) {
  selectAi(ais[0]);
}
</script>

<style scoped>
.dropdown-toggle,
.dropdown-item {
  white-space: normal;
}
</style>
