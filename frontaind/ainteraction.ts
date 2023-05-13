import { createApp } from "vue";
import Ainteraction from "@/components/ainteraction/Ainteraction.vue";

const element = document.querySelector("#ainteraction");
const ais = (element as HTMLElement).dataset.ais;
const knowledges = (element as HTMLElement).dataset.knowledges;

createApp(Ainteraction, { ais, knowledges }).mount("#ainteraction");
