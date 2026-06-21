import { ref, type Ref } from 'vue'

export interface FetchState<T, A extends unknown[]> {
  data: Ref<T>
  loading: Ref<boolean>
  fetch: (...args: A) => Promise<void>
}

/**
 * Loading-wrapped async fetch state for Pinia stores.
 *
 * Wraps the repeated `loading = true / try { data = await api() } finally`
 * block. Per-action pre-logic (e.g. year anchoring) belongs inside the
 * fetcher closure. Deliberately minimal — no abort/error/retry features.
 *
 * Without `initial`, `data` starts as `null` (nullable report objects);
 * pass `initial` (e.g. `[]`) to keep a non-nullable list type.
 */
export function useFetchState<T, A extends unknown[]>(
  fetcher: (...args: A) => Promise<T>,
): FetchState<T | null, A>
export function useFetchState<T, A extends unknown[]>(
  fetcher: (...args: A) => Promise<T>,
  initial: T,
): FetchState<T, A>
export function useFetchState<T, A extends unknown[]>(
  fetcher: (...args: A) => Promise<T>,
  initial?: T,
): FetchState<T | null, A> {
  const data = ref(initial ?? null) as Ref<T | null>
  const loading = ref(false)

  async function fetch(...args: A): Promise<void> {
    loading.value = true
    try {
      data.value = await fetcher(...args)
    } finally {
      loading.value = false
    }
  }

  return { data, loading, fetch }
}
