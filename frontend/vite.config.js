// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  css: {
    postcss: "./postcss.config.cjs", // 명시적으로 PostCSS 설정 경로 지정
  },
});
