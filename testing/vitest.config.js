import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    root: path.resolve(__dirname, '../frontend'),
    // Le decimos a Vitest EXACTAMENTE dónde buscar tu archivo de pruebas
    include: ['../testing/test_frontend.js'], 
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../frontend/src')
    }
  }
})
