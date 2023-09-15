import { defineStore } from "pinia";
import { throwOnFetchError } from "@/helpers/fetch";
import type { Knowledge } from "@/types/Knowledge";

export const useKnowledgeStore = defineStore({
  id: "knowledge",

  state: () => ({
    knowledges: [] as Knowledge[],
  }),

  actions: {
    async fetchKnowledges() {
      const response = await fetch("/api/knowledge/");
      await throwOnFetchError(response);
      const data: Knowledge[] = await response.json();
      this.knowledges = data;
    },

    async createKnowledge(newKnowledge: Omit<Knowledge, "id">) {
      const response = await fetch("/api/knowledge/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newKnowledge),
      });
      await throwOnFetchError(response);
      const data: Knowledge = await response.json();
      this.knowledges.push(data);
      return data;
    },

    async updateKnowledge(updatedKnowledge: Knowledge) {
      const response = await fetch(`/api/knowledge/${updatedKnowledge.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedKnowledge),
      });
      await throwOnFetchError(response);
      const data: Knowledge = await response.json();
      const index = this.knowledges.findIndex(
        (knowledge) => knowledge.id === updatedKnowledge.id
      );
      if (index !== -1) {
        this.knowledges[index] = data;
      }
      return data;
    },

    async deleteKnowledge(knowledgeId: number) {
      const response = await fetch(`/api/knowledge/${knowledgeId}`, {
        method: "DELETE",
      });
      await throwOnFetchError(response);
      this.knowledges = this.knowledges.filter(
        (knowledge) => knowledge.id !== knowledgeId
      );
    },
  },
});
