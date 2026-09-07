import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Standard Vite + React config. Nothing project-specific is needed here —
// the frontend talks to the Flask backend over plain fetch() calls at
// runtime (see API_BASE_URL in src/App.jsx), not through a Vite proxy.
export default defineConfig({
  plugins: [react()],
})
