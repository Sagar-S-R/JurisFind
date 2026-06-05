import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    proxy: {
      // All /api/* requests from localhost:5173 are forwarded to the FastAPI backend.
      // This makes them same-origin, which fixes:
      //   1. CORS errors when fetch()-ing PDFs as blobs in the viewer modal.
      //   2. Chrome ignoring the `download` attr on cross-origin <a> links.
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
