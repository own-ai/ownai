<template>
  <div class="w-100">
    <ul class="nav nav-tabs ps-2">
      <li class="nav-item" v-for="(tab, index) in tabs" :key="tab">
        <a
          class="nav-link"
          :class="{ active: currentTab === index }"
          href="#"
          @click.prevent="selectTab(index)"
        >
          {{ tab }}
        </a>
      </li>
    </ul>
    <div class="tab-content m-3">
      <slot :name="`tab${currentTab}`"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const { tabs } = defineProps<{ tabs: string[] }>();
const currentTab = ref(0);

const selectTab = (index: number) => {
  currentTab.value = index;
};
</script>
