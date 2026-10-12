import { configDefaults, defineConfig } from "vitest/config"

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    exclude: [...configDefaults.exclude, "tests/e2e/**"],
    // Augmente le seuil d'expiration pour tolérer la latence CPU de la machine
    testTimeout: 10000,
    // Optimise la gestion des threads et l'isolation JSDOM signalée dans les rapports
    pool: 'vmThreads',
  },
})