import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    open: true,
    allowedHosts: ['5173-i5rd7yb40dyiyhjy5foyd-f093ec88.manus.computer', '5174-i5rd7yb40dyiyhjy5foyd-f093ec88.manus.computer', '5175-i5rd7yb40dyiyhjy5foyd-f093ec88.manus.computer']
  }
})
