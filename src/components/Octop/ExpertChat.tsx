import { useEffect, useMemo, useRef, useState } from "react"
import { Button, Input, Upload } from "antd"
import { useNavigate, useParams } from "react-router-dom"
import { octopApi } from "@/services/octop-api"
import type {
  ApprovalPending,
  ConversationUiState,
  HistoryMessage,
  OctopEvent,
  OctopEventType
} from "@/services/octop-api/types"
import { isBusyState, DEFAULT_QUESTION } from "@/hooks/octop/state"
import { usePageSnapshot } from "@/hooks/octop/usePageSnapshot"
import { StateBanner } from "./StateBanner"

const SafeMarkdown = ({ text }: { text: string }) => {
  const cleaned = text.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, "")
  return <div className="whitespace-pre-wrap break-words text-sm dark:text-gray-100">{cleaned}</div>
}

export const ExpertChat = ({ mode }: { mode: "new" | "thread" }) => {
  const { expertKey = "", threadId: routeThreadId } = useParams()
  const navigate = useNavigate()
  const decodedKey = decodeURIComponent(expertKey)
  const [threadId, setThreadId] = useState(routeThreadId || "")
  const [messages, setMessages] = useState<HistoryMessage[]>([])
  const [draft, setDraft] = useState("")
  const [files, setFiles] = useState<File[]>([])
  const [state, setState] = useState<ConversationUiState>(mode === "new" ? "EMPTY" : "IDLE")
  const [pending, setPending] = useState<ApprovalPending | null>(null)
  const [externalHelp, setExternalHelp] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [turnId, setTurnId] = useState<string | null>(null)
  const [streamText, setStreamText] = useState("")
  const streamBuf = useRef("")
  const streamFlushTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const { snapshot, error: snapError, add, remove } = usePageSnapshot()
  const busy = isBusyState(state)

  const scheduleStreamFlush = () => {
    if (streamFlushTimer.current) {
      return
    }
    streamFlushTimer.current = setTimeout(() => {
      streamFlushTimer.current = null
      setStreamText(streamBuf.current)
    }, 100)
  }

  const reconcile = async () => {
    setState("RECONCILING")
    await connection.subscribe(threadId)
    const history = await octopApi.getHistory({ expertKey: decodedKey, threadId })
    setMessages((prev) => {
      const byId = new Map(prev.map((m) => [m.message_id, m]))
      for (const msg of history.items) {
        byId.set(msg.message_id, msg)
      }
      return [...byId.values()]
    })
    setState("IDLE")
  }

  const connection = useMemo(() => octopApi.connect({ expertKey: decodedKey }), [decodedKey])

  useEffect(() => {
    let cancelled = false
    const run = async () => {
      if (!threadId) {
        return
      }
      const history = await octopApi.getHistory({ expertKey: decodedKey, threadId })
      if (!cancelled) {
        setMessages(history.items)
        setState("IDLE")
      }
      await connection.subscribe(threadId)
      for await (const event of connection.events) {
        if (cancelled) break
        applyEvent(event)
      }
    }
    void run().catch((err) => setError(err instanceof Error ? err.message : "stream failed"))
    return () => {
      cancelled = true
      if (streamFlushTimer.current) {
        clearTimeout(streamFlushTimer.current)
        streamFlushTimer.current = null
      }
      connection.close()
    }
  }, [connection, decodedKey, threadId])

  const applyEvent = (event: OctopEvent) => {
    const type = event.type as OctopEventType
    switch (type) {
      case "message.delta": {
        streamBuf.current += String(event.payload.text || "")
        scheduleStreamFlush()
        break
      }
      case "turn.started":
      case "turn.resumed":
        setState("RUNNING")
        break
      case "approval.required":
        setPending(event.payload as ApprovalPending)
        setState("AWAITING_APPROVAL")
        break
      case "turn.ended":
        setState("IDLE")
        streamBuf.current = ""
        setStreamText("")
        void octopApi
          .getHistory({ expertKey: decodedKey, threadId })
          .then((page) => setMessages(page.items))
        break
      case "submission.accepted":
      case "subscribe.ok":
      case "pong":
        break
      case "reasoning.summary":
      case "tool.call":
      case "tool.result":
      case "usage":
      case "thread.status":
        break
      case "error":
        if (event.payload.code === "RESULT_UNKNOWN") {
          void reconcile().catch(() => setState("UNKNOWN"))
        } else {
          setError(String(event.payload.message || event.payload.code || "error"))
        }
        break
      default: {
        const exhaustive: never = type
        throw new Error(`unhandled event type: ${String(exhaustive)}`)
      }
    }
  }

  const send = async () => {
    if (busy) return
    let currentThread = threadId
    try {
      if (!currentThread) {
        setState("CREATING")
        const created = await octopApi.createThread({
          expertKey: decodedKey,
          requestId: crypto.randomUUID()
        })
        currentThread = created.thread_id
        setThreadId(currentThread)
        navigate(`/enterprise/experts/${encodeURIComponent(decodedKey)}/threads/${currentThread}`, {
          replace: true
        })
      }
      const uploadIds: string[] = []
      if (files.length) {
        setState("UPLOADING")
        for (const file of files) {
          const uploaded = await octopApi.uploadAttachment({
            expertKey: decodedKey,
            threadId: currentThread,
            requestId: crypto.randomUUID(),
            file
          })
          uploadIds.push(uploaded.upload_id)
        }
      }
      const question = draft.trim() || (snapshot || files.length ? DEFAULT_QUESTION : "")
      if (!question) {
        setError("INPUT_EMPTY")
        setState("IDLE")
        return
      }
      setState("SUBMITTING")
      const receipt = await connection.sendTurn({
        threadId: currentThread,
        clientRequestId: crypto.randomUUID(),
        question,
        context: snapshot,
        uploadIds
      })
      setTurnId(receipt.turn_id)
      setDraft("")
      setFiles([])
      setState("RUNNING")
    } catch (err) {
      setError(err instanceof Error ? err.message : "send failed")
      setState("UNKNOWN")
    }
  }

  const cancel = async () => {
    if (!threadId || !turnId) return
    setState("CANCELLING")
    try {
      await connection.cancelTurn({ threadId, turnId })
    } catch {
      setState("UNKNOWN")
    }
  }

  return (
    <div className="flex flex-col h-full min-h-[70vh] p-4 gap-3">
      <div className="flex items-center gap-2">
        <Button onClick={() => navigate("/enterprise/experts")}>Back</Button>
        <div className="text-sm text-gray-500">Expert session</div>
      </div>
      {error ? <StateBanner marker="error" message={error} /> : null}
      {state === "UNKNOWN" ? (
        <StateBanner marker="unknown" message="Result unknown. Reconnect to verify. Do not resend automatically." />
      ) : null}
      {snapError ? <StateBanner marker="error" message={snapError} /> : null}
      <div className="flex-1 overflow-y-auto space-y-3">
        {messages.map((msg) => (
          <div key={msg.message_id} className="rounded-lg p-3 bg-gray-50 dark:bg-[#111]">
            <div className="text-xs uppercase text-gray-400">{msg.role}</div>
            {msg.parts.map((part, idx) => (
              <SafeMarkdown key={idx} text={String((part.data as { text?: string }).text || part.kind)} />
            ))}
          </div>
        ))}
        {streamText ? <SafeMarkdown text={streamText} /> : null}
        {pending ? (
          <div className="border rounded-lg p-3">
            <div className="font-medium">Approval required</div>
            {pending.mode === "in_client" ? (
              <div className="flex gap-2 mt-2">
                <Button
                  type="primary"
                  onClick={() => {
                    void octopApi.resolveApproval({
                      expertKey: decodedKey,
                      threadId,
                      pendingId: pending.pending_id,
                      decisionId: crypto.randomUUID(),
                      decisions: pending.items.map((item) => ({ item_id: item.item_id, type: "approve" }))
                    })
                    setPending(null)
                  }}>
                  Approve
                </Button>
                <Button
                  onClick={() => {
                    void octopApi.resolveApproval({
                      expertKey: decodedKey,
                      threadId,
                      pendingId: pending.pending_id,
                      decisionId: crypto.randomUUID(),
                      decisions: pending.items.map((item) => ({
                        item_id: item.item_id,
                        type: "reject",
                        reason: ""
                      }))
                    })
                    setPending(null)
                  }}>
                  Reject
                </Button>
              </div>
            ) : (
              <Button
                onClick={async () => {
                  const help = await octopApi.getApprovalInstructions({
                    expertKey: decodedKey,
                    threadId,
                    pendingId: pending.pending_id
                  })
                  setExternalHelp(help.instructions)
                }}>
                Show instructions
              </Button>
            )}
            {externalHelp ? <StateBanner marker="approval_external" message={externalHelp} /> : null}
          </div>
        ) : null}
      </div>
      {snapshot ? (
        <div className="text-xs border rounded p-2">
          Page: {snapshot.title} ({snapshot.url}) {snapshot.truncated ? "(truncated)" : ""}
          <Button size="small" className="ml-2" onClick={remove}>
            Remove
          </Button>
        </div>
      ) : null}
      <div className="flex gap-2 items-end">
        <Input.TextArea
          value={draft}
          disabled={busy}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Message"
          autoSize={{ minRows: 2, maxRows: 6 }}
        />
        <div className="flex flex-col gap-2">
          <Button onClick={() => void add()}>Add current page</Button>
          <Upload
            beforeUpload={(file) => {
              setFiles((prev) => [...prev, file].slice(0, 5))
              return false
            }}
            fileList={files.map((file, i) => ({ uid: String(i), name: file.name }))}
            onRemove={(item) => {
              setFiles((prev) => prev.filter((file) => file.name !== item.name))
            }}
          />
          <Button type="primary" disabled={busy} onClick={() => void send()}>
            Send
          </Button>
          <Button disabled={!busy} onClick={() => void cancel()}>
            Stop
          </Button>
        </div>
      </div>
    </div>
  )
}
