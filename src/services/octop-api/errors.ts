export class OctopApiError extends Error {
  code: string
  retryable: boolean
  requestId: string
  details: Record<string, unknown>
  status?: number

  constructor(
    code: string,
    message: string,
    options?: {
      retryable?: boolean
      requestId?: string
      details?: Record<string, unknown>
      status?: number
    }
  ) {
    super(message)
    this.name = "OctopApiError"
    this.code = code
    this.retryable = options?.retryable ?? false
    this.requestId = options?.requestId ?? crypto.randomUUID()
    this.details = options?.details ?? {}
    this.status = options?.status
  }
}

export const parseErrorBody = (status: number, body: unknown): OctopApiError => {
  const record = body as { error?: Record<string, unknown> } | null
  const error = record?.error
  if (error && typeof error.code === "string") {
    return new OctopApiError(error.code, String(error.message || "request failed"), {
      retryable: Boolean(error.retryable),
      requestId: String(error.request_id || crypto.randomUUID()),
      details: (error.details as Record<string, unknown>) || {},
      status
    })
  }
  return new OctopApiError("NETWORK_UNAVAILABLE", "unexpected response", {
    retryable: status >= 500,
    status
  })
}
