<template>
  <div class="d-flex align-items-center justify-content-center gap-2 mb-4">
    <div class="col-sm-2 col-lg-1 d-flex justify-content-end">
      <span class="badge rounded-pill text-bg-warning">Knowledge</span>
    </div>
    <div v-if="!knowledges.length" class="flex-grow-1">
      <strong
        >This AI accesses knowledge. Please
        <a href="/workshop/knowledge">set up knowledge</a> first.</strong
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
      <ul class="dropdown-menu w-100 m-0">
        <li v-for="knowledge in knowledges" :key="knowledge.id">
          <a
            class="dropdown-item d-flex align-items-center gap-2 py-2"
            @click="selectKnowledge(knowledge)"
          >
            {{ knowledge.name }}
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { BasicKnowledge } from "@/types/ainteraction/BasicKnowledge";

const { knowledges, disabled } = defineProps<{
  knowledges: BasicKnowledge[];
  disabled: boolean;
}>();

const emit = defineEmits(["select-knowledge"]);
const selectedKnowledge = ref<BasicKnowledge | null>(null);

const selectKnowledge = (knowledge: BasicKnowledge) => {
  emit("select-knowledge", knowledge);
  selectedKnowledge.value = knowledge;
};

if (knowledges.length) {
  selectKnowledge(knowledges[0]);
}
</script>

<style scoped>
.dropdown-toggle,
.dropdown-item {
  white-space: normal;
}
</style>
