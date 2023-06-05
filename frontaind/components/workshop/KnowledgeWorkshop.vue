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
    <template v-slot:list-empty>
      No knowledge set up yet.
      <a href="#" @click.prevent="create">Create knowledge</a>
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
    <div
      v-else
      class="d-flex h-100 w-100 align-items-center justify-content-center"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="48"
        height="48"
        fill="currentColor"
        class="bi bi-lightbulb"
        viewBox="0 0 16 16"
      >
        <path
          d="M2 6a6 6 0 1 1 10.174 4.31c-.203.196-.359.4-.453.619l-.762 1.769A.5.5 0 0 1 10.5 13a.5.5 0 0 1 0 1 .5.5 0 0 1 0 1l-.224.447a1 1 0 0 1-.894.553H6.618a1 1 0 0 1-.894-.553L5.5 15a.5.5 0 0 1 0-1 .5.5 0 0 1 0-1 .5.5 0 0 1-.46-.302l-.761-1.77a1.964 1.964 0 0 0-.453-.618A5.984 5.984 0 0 1 2 6zm6-5a5 5 0 0 0-3.479 8.592c.263.254.514.564.676.941L5.83 12h4.342l.632-1.467c.162-.377.413-.687.676-.941A5 5 0 0 0 8 1z"
        />
      </svg>
    </div>
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
