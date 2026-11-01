import { OctopApiError, parseErrorBody } from "./errors"

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const RETRY_STATUSES = new Set([502, 503, 504])

export const clientFetch = async (
  url: string,
  init: RequestInit,
  options?: { retries?: boolean }
): Promise<Response> => {
  const retries = options?.retries ?? init.method === "GET" || !init.method
  const maxAttempts = retries ? 3 : 1
  let lastError: unknown
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 10000)
    try {
      const response = await fetch(url, {
        ...init,
        signal: init.signal ?? controller.signal
      })
      clearTimeout(timer)
      if (retries && RETRY_STATUSES.has(response.status) && attempt < maxAttempts - 1) {
        await sleep(1000 * (attempt + 1))
        continue
      }
      if (response.status === 429) {
        const retryAfter = Number(response.headers.get("Retry-After") || "1")
        if (retries && attempt < maxAttempts - 1) {
          await sleep(Math.min(Math.max(retryAfter, 1), 60) * 1000)
          continue
        }
      }
      return response
    } catch (error) {
      clearTimeout(timer)
      lastError = error
      if (!retries || attempt >= maxAttempts - 1) {
        throw new OctopApiError("NETWORK_UNAVAILABLE", "network failure", {
          retryable: true
        })
      }
      await sleep(1000 * (attempt + 1))
    }
  }
  throw lastError instanceof OctopApiError
    ? lastError
    : new OctopApiError("NETWORK_UNAVAILABLE", "network failure", { retryable: true })
}

export const readJson = async (response: Response): Promise<unknown> => {
  const text = await response.text()
  if (!text) {
    return null
  }
  try {
    return JSON.parse(text)
  } catch {
    throw new OctopApiError("PROTOCOL_INCOMPATIBLE", "response is not json", {
      status: response.status
    })
  }
}

export const expectJson = async <T>(response: Response): Promise<T> => {
  const body = await readJson(response)
  if (!response.ok) {
    throw parseErrorBody(response.status, body)
  }
  return body as T
}
