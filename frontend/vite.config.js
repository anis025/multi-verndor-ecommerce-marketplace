import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync, writeFileSync } from "fs";
import { resolve } from "path";
import { fileURLToPath } from "url";

const projectRoot = fileURLToPath(new URL(".", import.meta.url));

function removeCrossorigin() {
  return {
    name: "remove-crossorigin",
    // Mutate the in-memory HTML asset before it is written to disk. This is
    // the safe, modern approach and works in both Vite 5/6 (Rollup) and
    // Vite 8 (Rolldown) without depending on file-system timing.
    generateBundle(_options, bundle) {
      const asset = bundle["index.html"];
      if (asset && asset.type === "asset" && typeof asset.source === "string") {
        asset.source = asset.source.replace(/ crossorigin/g, "");
      }
    },
    // Post-process the HTML on disk as a safety net. Tolerate a missing
    // file (e.g. when generateBundle already handled it) instead of failing
    // the build.
    writeBundle() {
      const htmlPath = resolve(projectRoot, "dist/index.html");
      try {
        let html = readFileSync(htmlPath, "utf-8");
        if (html.includes(" crossorigin")) {
          writeFileSync(htmlPath, html.replace(/ crossorigin/g, ""));
        }
      } catch (e) {
        if (e.code !== "ENOENT") throw e;
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), removeCrossorigin()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/uploads': 'http://localhost:8000',
    },
  },
});
