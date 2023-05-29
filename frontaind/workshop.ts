import { createApp } from "vue";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";
import AiWorkshop from "@/components/workshop/AiWorkshop.vue";
import KnowledgeWorkshop from "@/components/workshop/KnowledgeWorkshop.vue";
import WorkshopApp from "@/components/workshop/WorkshopApp.vue";

const pinia = createPinia();
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/workshop", redirect: "/workshop/ai" },
    { path: "/workshop/ai/:id?", component: AiWorkshop },
    { path: "/workshop/knowledge/:id?", component: KnowledgeWorkshop },
  ],
});

const app = createApp(WorkshopApp);
app.use(pinia);
app.use(router);
app.mount("#workshop");
