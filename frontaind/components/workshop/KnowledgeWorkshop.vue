<template>
  <Workshop
    :items="knowledgeStore.knowledges"
    :selected-item-id="selectedKnowledgeId"
    @select-item="selectKnowledge"
  >
    <template v-slot:offcanvas-toggle-label>Select Knowledge</template>
    <template v-slot:offcanvas-header>
      <button type="button" class="btn btn-outline-primary" @click="create">
        Create
      </button>
    </template>
    <template v-slot:actionbar>
      <button
        type="button"
        class="btn btn-outline-primary mx-2 d-none d-lg-block"
        @click="create"
      >
        Create
      </button>
    </template>
    <template v-slot:list-item-dropdown-items="props">
      <li>
        <a
          class="dropdown-item"
          href="#"
          @click.prevent.stop="rename(props.item.id)"
        >
          Rename
        </a>
      </li>
      <li>
        <a
          class="dropdown-item dropdown-item-danger"
          href="#"
          @click.prevent.stop="deleteKnowledge(props.item.id)"
        >
          Delete
        </a>
      </li>
    </template>
    <FileDragDrop
      v-if="selectedKnowledgeId"
      :knowledge-id="selectedKnowledgeId"
    >
      <h4>Add knowledge to {{ selectedKnowledge?.name }}</h4>
      <template v-slot:success
        ><h4>Successfully added to {{ selectedKnowledge?.name }}</h4></template
      >
    </FileDragDrop>
  </Workshop>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter, onBeforeRouteUpdate } from "vue-router";
import { useKnowledgeStore } from "@/store/knowledge";
import Workshop from "./Workshop.vue";
import FileDragDrop from "./knowledge/FileDragDrop.vue";
import type { IdName } from "@/types/IdName";

const knowledgeStore = useKnowledgeStore();

const route = useRoute();
const router = useRouter();

const selectedKnowledgeId = ref<number | null>();
const selectedKnowledge = computed(() =>
  knowledgeStore.knowledges.find(
    (knowledge) => knowledge.id === selectedKnowledgeId.value
  )
);

const selectKnowledge = (knowledge: IdName) => {
  selectedKnowledgeId.value = knowledge.id;
  router.push({ params: { id: knowledge.id } });
};

const create = async () => {
  const name = prompt("Name of the new knowledge collection");
  if (!name) {
    return;
  }
  try {
    await knowledgeStore.createKnowledge({
      name,
      embeddings: "huggingface",
      chunk_size: 500,
    });
  } catch (error) {
    alert(error);
  }
};

const rename = async (knowledgeId: number) => {
  const knowledge = knowledgeStore.knowledges.find(
    (knowledge) => knowledge.id === knowledgeId
  );
  const name = prompt("New name of the knowledge collection", knowledge?.name);
  if (!name) {
    return;
  }
  try {
    await knowledgeStore.updateKnowledge({ ...knowledge!, name });
  } catch (error) {
    alert(error);
  }
};

const deleteKnowledge = async (knowledgeId: number) => {
  const knowledge = knowledgeStore.knowledges.find(
    (knowledge) => knowledge.id === knowledgeId
  );
  if (!confirm(`Really delete knowledge collection "${knowledge?.name}"?`)) {
    return;
  }
  try {
    await knowledgeStore.deleteKnowledge(knowledgeId);
    if (knowledgeId === selectedKnowledgeId.value) {
      selectedKnowledgeId.value = null;
    }
  } catch (error) {
    alert(error);
  }
};

onMounted(async () => {
  await knowledgeStore.fetchKnowledges();

  const paramId = route.params.id;
  if (typeof paramId === "string" && !isNaN(parseInt(paramId))) {
    selectedKnowledgeId.value = parseInt(paramId);
  } else if (knowledgeStore.knowledges?.length) {
    selectedKnowledgeId.value = knowledgeStore.knowledges[0].id;
    router.push({ params: { id: knowledgeStore.knowledges[0].id } });
  }
});

onBeforeRouteUpdate((to, from) => {
  if (to.params.id !== from.params.id) {
    if (typeof to.params.id === "string" && !isNaN(parseInt(to.params.id))) {
      const id = parseInt(to.params.id);
      if (selectedKnowledgeId.value !== id) {
        selectedKnowledgeId.value = id;
      }
    }
  }
});
</script>
