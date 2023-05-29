<template>
  <div
    class="actionbar d-flex flex-grow-0 flex-shrink-0 align-items-center justify-content-between border-bottom"
  >
    <button
      class="btn btn-outline-primary d-lg-none mx-2"
      type="button"
      aria-controls="offcanvasResponsive"
      @click="offcanvas.toggle()"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        fill="currentColor"
        class="bi bi-list"
        viewBox="0 0 16 16"
      >
        <path
          fill-rule="evenodd"
          d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"
        />
      </svg>
      <span class="ms-1">
        <slot name="offcanvas-toggle-label"></slot>
      </span>
    </button>
    <slot name="actionbar"></slot>
  </div>
  <div class="d-flex flex-nowrap h-100">
    <div
      ref="offcanvasRef"
      class="offcanvas-lg offcanvas-start h-100"
      tabindex="-1"
      id="offcanvasResponsive"
    >
      <div class="offcanvas-header">
        <slot name="offcanvas-header"></slot>
        <button
          type="button"
          class="btn-close"
          aria-label="Close"
          @click="offcanvas.hide()"
        ></button>
      </div>
      <div class="offcanvas-body p-0 border-top h-100 overflow-auto">
        <div
          class="d-flex flex-column align-items-stretch flex-shrink-0 bg-body-tertiary overflow-auto w-100"
        >
          <div class="list-group list-group-flush border-bottom scrollarea">
            <a
              v-for="item in items"
              :key="item.id"
              class="list-group-item list-group-item-action py-3 lh-sm"
              :class="item.id === selectedItemId ? 'active' : null"
              href="#"
              :aria-current="item.id === selectedItemId"
              @click.prevent="selectItem(item)"
            >
              <div
                class="d-flex w-100 align-items-center justify-content-between"
              >
                <strong class="me-1 list-group-item-title" :title="item.name">{{
                  item.name
                }}</strong>
                <div class="dropdown">
                  <button
                    class="btn dropdown-toggle"
                    :class="
                      item.id === selectedItemId ? 'btn-primary' : 'btn-light'
                    "
                    type="button"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                    @click.stop="() => {}"
                  ></button>
                  <ul class="dropdown-menu shadow m-0">
                    <slot name="list-item-dropdown-items" :item="item"></slot>
                  </ul>
                </div>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
    <div class="vr"></div>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Offcanvas } from "bootstrap";
import type { IdName } from "@/types/IdName";

const { items, selectedItemId } = defineProps<{
  items: IdName[];
  selectedItemId?: number | null;
}>();

const emit = defineEmits(["select-item"]);

const offcanvasRef = ref();
let offcanvas: Offcanvas;

onMounted(() => {
  offcanvas = new Offcanvas(offcanvasRef.value);
});

const selectItem = (item: IdName) => {
  emit("select-item", item);
  offcanvas.hide();
};
</script>

<style>
#workshop {
  font-size: 0.875rem;
}
</style>

<style scoped>
.actionbar {
  height: 3rem;
}

.actionbar + div {
  min-height: 0;
}

@media (min-width: 992px) {
  .offcanvas-lg {
    width: 350px;
    flex-shrink: 0;
  }

  .offcanvas-body {
    border-top: 0 !important;
  }
}

.list-group-item-title {
  line-height: 1.2em;
  max-height: 2.4em; /* 1.2em * 2 lines */
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-overflow: ellipsis;
}

.list-group .dropdown-toggle:not(:hover):not(:active) {
  transition: none;
  background-color: transparent;
  border-color: transparent;
}
</style>
