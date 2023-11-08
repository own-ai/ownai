<template>
  <div
    v-if="isLoading"
    class="d-flex justify-content-center align-items-center mt-5"
  >
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
  <div v-else-if="store.currentDocuments.length">
    <svg xmlns="http://www.w3.org/2000/svg" class="d-none">
      <symbol id="trash" viewBox="0 0 16 16">
        <path
          d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6Z"
        />
        <path
          d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1ZM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118ZM2.5 3h11V2h-11v1Z"
        />
      </symbol>
    </svg>
    <table class="table">
      <tbody>
        <tr v-for="document in store.currentDocuments" :key="document.id">
          <td>{{ document.text }}</td>
          <td>
            <button
              type="button"
              class="btn btn-light"
              @click="deleteDocument(document.id)"
            >
              <svg width="16" height="16">
                <use href="#trash"></use>
              </svg>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <nav>
      <ul class="pagination flex-wrap">
        <li class="page-item mt-2">
          <a
            class="page-link"
            :class="{ disabled: !hasPrevious }"
            href="#"
            aria-label="Previous"
            @click.prevent="store.goToPage(store.currentPage - 1)"
          >
            <span aria-hidden="true">&laquo;</span>
          </a>
        </li>
        <li
          class="page-item mt-2"
          v-for="page in store.totalPages"
          :key="page"
          :class="{ active: page === store.currentPage }"
        >
          <a class="page-link" href="#" @click.prevent="store.goToPage(page)">{{
            page
          }}</a>
        </li>
        <li class="page-item mt-2">
          <a
            class="page-link"
            :class="{ disabled: !hasNext }"
            href="#"
            aria-label="Next"
            @click.prevent="store.goToPage(store.currentPage + 1)"
          >
            <span aria-hidden="true">&raquo;</span>
          </a>
        </li>
      </ul>
    </nav>
  </div>
  <div v-else>
    <p class="my-4">
      Nothing there yet. Please add something to this knowledge first.
    </p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref, watch } from "vue";
import { useDocumentStore } from "@/store/document";

const props = defineProps<{
  knowledgeId: number;
}>();

const store = ref(useDocumentStore(props.knowledgeId)());
const isLoading = ref(true);

const load = async () => {
  isLoading.value = true;
  await store.value.fetchDocumentsForPage(store.value.currentPage);
  isLoading.value = false;
};

onMounted(load);

watch(
  () => props.knowledgeId,
  (newVal) => {
    store.value = useDocumentStore(newVal)();
    load();
  }
);

const deleteDocument = async (documentId: string) => {
  await store.value.deleteDocument(documentId);
  await store.value.fetchDocumentsForPage(store.value.currentPage);
};

const hasPrevious = computed(() => store.value.currentPage > 1);
const hasNext = computed(
  () => store.value.currentPage < store.value.totalPages
);
</script>
