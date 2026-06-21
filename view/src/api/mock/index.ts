import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)

export async function startMockWorker() {
  // vite.config.ts sets `base: '/networth/'`, so the deployed worker URL
  // must be `/networth/mockServiceWorker.js`. Hard-coding `/` 404s on prod.
  await worker.start({
    serviceWorker: { url: import.meta.env.BASE_URL + 'mockServiceWorker.js' },
    onUnhandledRequest: 'bypass',
  })
}
