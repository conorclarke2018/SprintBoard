import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Mantine is a large library; one ~600 kB bundle is fine for this app.
    chunkSizeWarningLimit: 800,
  },
  server: {
    // In development, forward API calls to FastAPI so there is no CORS setup.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
