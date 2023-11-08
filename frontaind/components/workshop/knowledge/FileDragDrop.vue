<template>
  <div
    v-if="isLoading"
    class="d-flex justify-content-center align-items-center mt-5"
  >
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Uploading...</span>
    </div>
  </div>
  <div
    v-else
    class="d-flex flex-column justify-content-center align-items-center border-primary p-5"
    :class="{ 'bg-light': isDraggingOver }"
    @dragover.prevent="isDraggingOver = true"
    @dragenter.prevent="isDraggingOver = true"
    @dragleave.prevent="isDraggingOver = false"
    @drop.prevent="drop"
  >
    <template v-if="isSuccess">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="64"
        height="64"
        fill="currentColor"
        class="bi bi-check-lg text-success mb-3"
        viewBox="0 0 16 16"
      >
        <path
          d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"
        />
      </svg>
      <slot name="success"></slot>
      <button
        type="button"
        class="btn btn-primary mt-3"
        @click="isSuccess = false"
      >
        Add more
      </button>
    </template>
    <template v-else>
      <slot></slot>
      <p class="mt-4">Drop files here (txt, pdf, docx)</p>
      <p>or</p>
      <div>
        <label for="file-input" class="btn btn-primary">Select files</label>
        <input
          id="file-input"
          class="d-none"
          type="file"
          accept=".txt,.pdf,.docx"
          multiple
          @change="handleFileInput"
        />
      </div>
      <div class="alert alert-light mt-5" role="alert">
        Knowledge added here is only accessible to AIs with an
        <code>input_knowledge</code> input key in their
        <a href="/workshop/ai">aifile</a>. You can recognize these AIs by a
        yellow dot
        <span class="d-inline-block rounded-circle p-1 bg-warning"></span>
        in the AI list on the <a href="/">interaction view</a>.
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { throwOnFetchError } from "@/helpers/fetch";

const props = defineProps<{
  knowledgeId: number;
}>();
const knowledgeId = ref(props.knowledgeId);
watch(
  () => props.knowledgeId,
  (newVal) => {
    knowledgeId.value = newVal;
  }
);

const isDraggingOver = ref<boolean>(false);
const isLoading = ref<boolean>(false);
const isSuccess = ref<boolean>(false);

const drop = (event: DragEvent) => {
  isDraggingOver.value = false;
  const files = event.dataTransfer?.files;
  if (files?.length) {
    handleFiles(files);
  }
};

const handleFileInput = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files?.length) {
    handleFiles(input.files);
  }
};

const handleFiles = async (files: FileList) => {
  isLoading.value = true;
  isSuccess.value = true;
  for (const file of Array.from(files)) {
    const extension = file.name.split(".").pop();

    switch (extension) {
      case "txt":
        await uploadFile(
          file,
          `/api/knowledge/${knowledgeId.value}/document/txt`
        );
        break;
      case "pdf":
        await uploadFile(
          file,
          `/api/knowledge/${knowledgeId.value}/document/pdf`
        );
        break;
      case "docx":
        await uploadFile(
          file,
          `/api/knowledge/${knowledgeId.value}/document/docx`
        );
        break;
      default:
        isSuccess.value = false;
        alert(`The file format .${extension} is not supported yet.`);
    }
  }
  isLoading.value = false;
};

const uploadFile = async (file: File, url: string): Promise<void> => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    await throwOnFetchError(response);
  } catch (error) {
    isSuccess.value = false;
    alert(error);
  }
};
</script>

<style scoped>
.border-primary {
  border-width: 2px;
  border-style: dashed;
}
</style>
