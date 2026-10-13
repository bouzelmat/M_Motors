import { configDefaults, defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"

export default defineConfig({
  // Ajout du plugin React pour assurer une compilation JSX cohérente dans les tests
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    exclude: [...configDefaults.exclude, "tests/e2e/**"],
    
    // Augmente le seuil d'expiration pour tolérer la latence CPU de la machine
    testTimeout: 10000,
    
    // Optimise la gestion des threads et l'isolation JSDOM
    pool: 'vmThreads',
    
    // ==========================================
    // CORRECTION DE L'ERREUR ESM / COMMONJS
    // ==========================================
    // Force Vitest à transformer ces paquets via Vite au lieu de les 
    // laisser natifs à Node.js, ce qui évite l'erreur ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING
    deps: {
      inline: [
        "react-router",
        "react-router-dom"
      ]
    }
    // ==========================================
  },
})