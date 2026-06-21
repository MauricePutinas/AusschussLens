import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Backend-Ziel fuer den Dev-Proxy; per Env ueberschreibbar (Default Port 8000).
const target = process.env.VITE_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: Number(process.env.PORT) || 5173,
    proxy: {
      '/api': target,
      '/uploads': target,
    },
  },
})
