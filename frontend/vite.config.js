import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:18000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Element Plus 独立拆分（减少主包 ~300KB gzipped）
          'element-plus': ['element-plus'],
          // Vue 生态独立拆分
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
        },
      },
    },
  },
})
