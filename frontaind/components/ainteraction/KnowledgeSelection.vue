<template>
  <div class="d-flex align-items-center justify-content-center gap-2 mb-4">
    <div class="col-sm-2 col-lg-1 d-flex justify-content-end">
      <span class="badge rounded-pill text-bg-warning">Knowledge</span>
    </div>
    <div v-if="!knowledgeDefinitions.length" class="flex-grow-1">
      <strong
        >This AI accesses knowledge. Please set up knowledge first.</strong
      >
    </div>
    <div v-else-if="disabled" class="flex-grow-1">
      <strong>{{ selectedKnowledge?.name }}</strong>
    </div>
    <div v-else class="dropdown flex-grow-1">
      <button
        class="btn btn-light border dropdown-toggle d-block w-100 text-start"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        {{ selectedKnowledge ? selectedKnowledge.name : "Select Knowledge" }}
      </button>
      <ul class="dropdown-menu w-100">
        <li
          v-for="knowledgeDefinition in knowledgeDefinitions"
          :key="knowledgeDefinition.id"
        >
          <a
            class="dropdown-item d-flex align-items-center gap-2 py-2"
            @click="selectKnowledge(knowledgeDefinition)"
          >
            {{ knowledgeDefinition.name }}
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { KnowledgeDefinition } from "@/types/ainteraction/KnowledgeDefinition";

const { knowledgeDefinitions, disabled } = defineProps<{
  knowledgeDefinitions: KnowledgeDefinition[];
  disabled: boolean;
}>();

const emit = defineEmits(["select-knowledge"]);
const selectedKnowledge = ref<KnowledgeDefinition | null>(null);

const selectKnowledge = (knowledgeDefinition: KnowledgeDefinition) => {
  emit("select-knowledge", knowledgeDefinition);
  selectedKnowledge.value = knowledgeDefinition;
};

if (knowledgeDefinitions.length) {
  selectKnowledge(knowledgeDefinitions[0]);
}
</script>

<style scoped>
.dropdown-toggle,
.dropdown-item {
  white-space: normal;
}
</style>
