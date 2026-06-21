import { describe, it, expect, vi } from 'vitest'
import { useFetchState } from '@/composables/useFetchState'

describe('useFetchState', () => {
  it('starts null without initial, or with the provided initial', () => {
    expect(useFetchState(() => Promise.resolve(1)).data.value).toBeNull()
    expect(useFetchState(() => Promise.resolve([1]), [] as number[]).data.value).toEqual([])
  })

  it('toggles loading around the fetch and stores the result', async () => {
    let resolve!: (v: string) => void
    const state = useFetchState(() => new Promise<string>((r) => (resolve = r)))
    const pending = state.fetch()
    expect(state.loading.value).toBe(true)
    resolve('done')
    await pending
    expect(state.loading.value).toBe(false)
    expect(state.data.value).toBe('done')
  })

  it('clears loading when the fetcher rejects and keeps prior data', async () => {
    const state = useFetchState(
      vi
        .fn<() => Promise<string>>()
        .mockResolvedValueOnce('first')
        .mockRejectedValueOnce(new Error('boom')),
    )
    await state.fetch()
    expect(state.data.value).toBe('first')
    await expect(state.fetch()).rejects.toThrow('boom')
    expect(state.loading.value).toBe(false)
    expect(state.data.value).toBe('first')
  })

  it('passes arguments through to the fetcher', async () => {
    const fetcher = vi.fn((a: string, b?: number) => Promise.resolve(`${a}:${b}`))
    const state = useFetchState(fetcher)
    await state.fetch('x', 2)
    expect(fetcher).toHaveBeenCalledWith('x', 2)
    expect(state.data.value).toBe('x:2')
  })
})
