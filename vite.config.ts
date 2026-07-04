import { resolve } from 'node:path';
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    outDir: 'dist',
    assetsDir: 'compiled',
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'index.html'),
        dashboard: resolve(__dirname, 'dashboard.html'),
        staffDashboard: resolve(__dirname, 'staff-dashboard.html'),
        adminDashboard: resolve(__dirname, 'admin-dashboard.html'),
      },
    },
  }
})
