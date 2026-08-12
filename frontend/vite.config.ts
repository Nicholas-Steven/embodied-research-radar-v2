import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages project site: https://nicholas-steven.github.io/embodied-research-radar-v2/
const BASE = "/embodied-research-radar-v2/";

export default defineConfig({
  plugins: [react()],
  base: BASE,
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
