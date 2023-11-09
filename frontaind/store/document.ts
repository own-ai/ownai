import { defineStore } from "pinia";
import { throwOnFetchError } from "@/helpers/fetch";
import type { Document } from "@/types/Document";

export const useDocumentStore = (knowledgeId: number) =>
  defineStore({
    id: `document-${knowledgeId}`,

    state: () => ({
      documentPages: {} as Record<number, Document[]>,
      totalDocuments: 0,
      currentPage: 1,
      itemsPerPage: 10,
      knowledgeId,
    }),

    getters: {
      currentDocuments(): Document[] {
        return this.documentPages[this.currentPage] || [];
      },
      totalPages(): number {
        return Math.ceil(this.totalDocuments / this.itemsPerPage);
      },
    },

    actions: {
      async fetchDocumentsForPage(page: number) {
        const offset = (page - 1) * this.itemsPerPage;
        const limit = this.itemsPerPage;

        if (this.documentPages[page]) {
          return;
        }

        const response = await fetch(
          `/api/knowledge/${knowledgeId}/document?offset=${offset}&limit=${limit}`,
        );
        await throwOnFetchError(response);

        const data = await response.json();
        this.documentPages[page] = data.items;
        this.totalDocuments = data.total;
      },

      async goToPage(page: number) {
        this.currentPage = page;
        await this.fetchDocumentsForPage(page);
      },

      async deleteDocument(documentId: string) {
        const response = await fetch(
          `/api/knowledge/${knowledgeId}/document/${documentId}`,
          {
            method: "DELETE",
          },
        );
        await throwOnFetchError(response);
        this.documentPages[this.currentPage] = this.documentPages[
          this.currentPage
        ].filter((document) => document.id !== documentId);
      },
    },
  });
