/// <reference types="vitest" />
import { resolve } from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      // The planner plus one static landing page per Step-1 wedge (/for/<wedge>/).
      input: {
        main: resolve(import.meta.dirname, "index.html"),
        "travellers-abroad": resolve(import.meta.dirname, "for/travellers-abroad/index.html"),
        "tour-operators": resolve(import.meta.dirname, "for/tour-operators/index.html"),
        "heritage-stories": resolve(import.meta.dirname, "for/heritage-stories/index.html"),
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts"
  }
});
