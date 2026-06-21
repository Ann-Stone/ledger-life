import { mergeConfig } from 'vite'
import { defineConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
      include: ['src/**/__tests__/**/*.spec.ts'],
      // Force element-plus auto-injected CSS through Vite's transform pipeline,
      // otherwise jsdom tries to resolve .css with the native ESM loader.
      server: {
        deps: {
          inline: ['element-plus'],
        },
      },
    },
  }),
)
