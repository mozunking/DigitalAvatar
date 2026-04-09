/**
 * Composable for unified async state management: loading, error, empty.
 *
 * Usage:
 *   const { loading, error, empty, run, retry } = useAsyncState<Task[]>()
 *   await run(() => taskApi.list())
 */
import { ref, computed } from 'vue'

export function useAsyncState<T>(initialValue?: T) {
  const data = ref<T | undefined>(initialValue) as { value: T | undefined }
  const loading = ref(false)
  const error = ref<string | null>(null)

  const empty = computed(() => !loading.value && !error.value && (!data.value || (Array.isArray(data.value) && data.value.length === 0)))

  const run = async (fn: () => Promise<T>) => {
    loading.value = true
    error.value = null
    try {
      data.value = await fn()
      return data.value
    } catch (e: any) {
      error.value = e?.response?.data?.error?.message || e?.message || 'Unknown error'
      throw e
    } finally {
      loading.value = false
    }
  }

  const retry = (fn: () => Promise<T>) => run(fn)

  const clearError = () => {
    error.value = null
  }

  return { data, loading, error, empty, run, retry, clearError }
}
