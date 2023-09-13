<template>
  <form
    @submit.prevent="sendMessage"
    class="d-flex my-4 align-items-sm-start flex-column flex-sm-row gap-2"
  >
    <textarea
      class="form-control"
      v-model="messageInput"
      :placeholder="label"
      required
      @keydown="checkForSubmit"
    ></textarea>
    <button type="submit" class="btn btn-primary" title="Send">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        fill="currentColor"
        class="bi bi-send"
        viewBox="0 0 16 16"
      >
        <path
          d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576 6.636 10.07Zm6.787-8.201L1.591 6.602l4.339 2.76 7.494-7.493Z"
        />
      </svg>
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref } from "vue";

const { label } = defineProps<{
  label: string;
}>();

const messageInput = ref("");
const emit = defineEmits(["send-message"]);

const sendMessage = () => {
  emit("send-message", messageInput.value);
  messageInput.value = "";
};

const checkForSubmit = (event: KeyboardEvent) => {
  if ((event.shiftKey || event.ctrlKey) && event.code === "Enter") {
    sendMessage();
  }
};
</script>
