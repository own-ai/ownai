import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import Ainteraction from "@/components/ainteraction/Ainteraction.vue";
import AinteractionApp from "@/components/ainteraction/AinteractionApp.vue";

const element = document.querySelector("#ainteraction");
const ais = (element as HTMLElement).dataset.ais;
const knowledges = (element as HTMLElement).dataset.knowledges;
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/:ai?", component: Ainteraction, props: { ais, knowledges } },
  ],
});

const app = createApp(AinteractionApp);
app.use(router);
app.mount("#ainteraction");
