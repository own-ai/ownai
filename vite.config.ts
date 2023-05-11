import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { glob } from "glob";
import path from "path";

export default defineConfig({
  root: path.resolve(__dirname, "frontaind"),
  build: {
    outDir: "../backaind/static",
    emptyOutDir: true,
    rollupOptions: {
      input: glob.sync("frontaind/*.ts"),
      output: {
        entryFileNames: "ownai-[name].js",
        assetFileNames: "ownai-[name].css",
      },
    },
  },
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "frontaind"),
    },
  },
  optimizeDeps: {
    disabled: true,
  },
});
