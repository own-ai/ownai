import { defineStore } from "pinia";
import { throwOnFetchError } from "@/helpers/fetch";
import type { Ai } from "@/types/Ai";

export const useAiStore = defineStore({
  id: "ai",

  state: () => ({
    ais: [] as Ai[],
  }),

  actions: {
    async fetchAis() {
      const response = await fetch("/api/ai/");
      await throwOnFetchError(response);
      const data: Ai[] = await response.json();
      this.ais = data;
    },

    async createAi(newAi: Omit<Ai, "id">) {
      const response = await fetch("/api/ai/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newAi),
      });
      await throwOnFetchError(response);
      const data: Ai = await response.json();
      this.ais.push(data);
      return data;
    },

    async updateAi(updatedAi: Ai) {
      const response = await fetch(`/api/ai/${updatedAi.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedAi),
      });
      await throwOnFetchError(response);
      const data: Ai = await response.json();
      const index = this.ais.findIndex((ai) => ai.id === updatedAi.id);
      if (index !== -1) {
        this.ais[index] = data;
      }
      return data;
    },

    async deleteAi(aiId: number) {
      const response = await fetch(`/api/ai/${aiId}`, {
        method: "DELETE",
      });
      await throwOnFetchError(response);
      this.ais = this.ais.filter((ai) => ai.id !== aiId);
    },
  },
});
