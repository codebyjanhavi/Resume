import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Configure Vite with the React plugin for frontend development and builds.
export default defineConfig({
  plugins: [react()],
})
