import { configDefaults, defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    exclude: [...configDefaults.exclude, "tests/e2e/**"],
    testTimeout: 10000,
    
    // CORRECTION 1 : Utiliser 'threads' au lieu de 'vmThreads' pour éviter le bug ESM du module vm de Node
    pool: 'threads',
    
    // CORRECTION 2 : Syntaxe correcte Vitest 5 pour l'inlining des dépendances
    deps: {
      inline: [
        "react-router",
        "react-router-dom"
      ]
    }
  },
})