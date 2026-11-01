import { OctopApiError } from "./errors"
import type {
  CancelReceipt,
  ContextSnapshot,
  ConversationConnection,
  OctopEvent,
  SubmissionReceipt
} from "./types"

const KNOWN_EVENTS = new Set([
  "submission.accepted",
  "turn.started",
  "turn.resumed",
  "message.delta",
  "reasoning.summary",
  "tool.call",
  "tool.result",
  "approval.required",
  "usage",
  "turn.ended",
  "thread.status",
  "error",
  "pong",
  "subscribe.ok"
])

type Pending = {
  resolve: (value: unknown) => void
  reject: (error: unknown) => void
}

const PING_INTERVAL_MS = 20_000
const PONG_TIMEOUT_MS = 40_000

export const openConversation = (wsUrl: string): ConversationConnection => {
  let socket: WebSocket | null = null
  let closed = false
  let seqSeen = 0
  let gapDetected = false
  const pending = new Map<string, Pending>()
  const queue: OctopEvent[] = []
  let notify: (() => void) | null = null
  let reconnectAttempt = 0
  let pingTimer: ReturnType<typeof setInterval> | null = null
  let pongTimer: ReturnType<typeof setTimeout> | null = null

  const flush = () => {
    if (notify) {
      const n = notify
      notify = null
      n()
    }
  }

  const pushError = (data: Record<string, unknown>, code: string, message: string) => {
    queue.push({
      v: 1,
      connection_id: String(data.connection_id || ""),
      seq: Number(data.seq || 0),
      type: "error",
      thread_id: (data.thread_id as string) || null,
      turn_id: (data.turn_id as string) || null,
      client_request_id: (data.client_request_id as string) || null,
      payload: { code, message }
    })
    flush()
  }

  const clearHeartbeat = () => {
    if (pingTimer) {
      clearInterval(pingTimer)
      pingTimer = null
    }
    if (pongTimer) {
      clearTimeout(pongTimer)
      pongTimer = null
    }
  }

  const startHeartbeat = () => {
    clearHeartbeat()
    pingTimer = setInterval(() => {
      if (!socket || socket.readyState !== WebSocket.OPEN || closed) {
        return
      }
      try {
        send("ping", null, { nonce: crypto.randomUUID().replace(/-/g, "").slice(0, 32) })
        if (pongTimer) {
          clearTimeout(pongTimer)
        }
        pongTimer = setTimeout(() => {
          pushError({}, "TIMEOUT", "no pong within 40s")
          socket?.close()
        }, PONG_TIMEOUT_MS)
      } catch {
        // socket closed concurrently; onclose handles reconnect
      }
    }, PING_INTERVAL_MS)
  }

  const connect = () => {
    socket = new WebSocket(wsUrl)
    socket.onopen = () => {
      startHeartbeat()
    }
    socket.onmessage = (event) => {
      const data = JSON.parse(String(event.data)) as Record<string, unknown>
      if (data.request_id && pending.has(String(data.request_id)) && data.status) {
        pending.get(String(data.request_id))?.resolve(data)
        pending.delete(String(data.request_id))
      }
      if (data.type === "subscribe.ok" && data.request_id) {
        pending.get(String(data.request_id))?.resolve(data)
        pending.delete(String(data.request_id))
        return
      }
      if (data.type === "pong") {
        if (pongTimer) {
          clearTimeout(pongTimer)
          pongTimer = null
        }
        return
      }
      if (typeof data.seq === "number") {
        const seq = data.seq as number
        if (seq !== seqSeen + 1 && seqSeen !== 0 && !gapDetected) {
          gapDetected = true
          pushError(data, "RESULT_UNKNOWN", "event gap")
        }
        seqSeen = seq
      }
      if (typeof data.type === "string" && data.type !== "subscribe.ok") {
        if (!KNOWN_EVENTS.has(data.type) && data.optional !== true) {
          queue.push({
            v: 1,
            connection_id: String(data.connection_id || ""),
            seq: Number(data.seq || 0),
            type: "error",
            thread_id: (data.thread_id as string) || null,
            turn_id: (data.turn_id as string) || null,
            client_request_id: (data.client_request_id as string) || null,
            payload: { code: "PROTOCOL_INCOMPATIBLE", message: "unknown event" }
          })
          flush()
          return
        }
        queue.push(data as OctopEvent)
        flush()
      }
    }
    socket.onclose = () => {
      clearHeartbeat()
      if (closed) {
        return
      }
      if (reconnectAttempt >= 5) {
        return
      }
      const delay = [1000, 2000, 4000, 8000, 16000][reconnectAttempt]
      reconnectAttempt += 1
      setTimeout(connect, delay)
    }
  }
  connect()

  const send = (type: string, threadId: string | null, payload: Record<string, unknown>) => {
    const request_id = crypto.randomUUID()
    const frame = {
      v: 1,
      type,
      request_id,
      thread_id: threadId,
      payload
    }
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      throw new OctopApiError("NETWORK_UNAVAILABLE", "websocket not open")
    }
    socket.send(JSON.stringify(frame))
    return request_id
  }

  const wait = (requestId: string) =>
    new Promise((resolve, reject) => {
      pending.set(requestId, { resolve, reject })
    })

  const connection: ConversationConnection = {
    async subscribe(threadId) {
      const id = send("subscribe", threadId, {})
      await wait(id)
    },
    async sendTurn(input) {
      const contextPayload = input.context
        ? {
            source_url: input.context.url,
            title: input.context.title,
            captured_at: input.context.captured_at,
            text: input.context.text
          }
        : null
      const id = send("user_turn", input.threadId, {
        question: input.question,
        context: contextPayload,
        upload_ids: input.uploadIds
      })
      const receipt = (await wait(id)) as SubmissionReceipt
      return receipt
    },
    async cancelTurn(input) {
      const id = send("cancel", input.threadId, { expected_turn_id: input.turnId })
      return (await wait(id)) as CancelReceipt
    },
    events: {
      async *[Symbol.asyncIterator]() {
        while (!closed) {
          if (queue.length) {
            yield queue.shift() as OctopEvent
            continue
          }
          await new Promise<void>((resolve) => {
            notify = resolve
          })
        }
      }
    },
    close() {
      closed = true
      clearHeartbeat()
      socket?.close()
    }
  }
  return connection
}

export type { ContextSnapshot }
