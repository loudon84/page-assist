export type ExpertSourceKind = "local" | "bridge_personal" | "bridge_shared"
export type ExpertAvailability = "available" | "offline" | "forbidden" | "unsupported"
export type ApprovalMode = "in_client" | "external_instructions" | "none"
export type CatalogSource = "all" | "local" | "remote"

export type ClientCapabilities = {
  protocol: { major: number; minor: number }
  build: {
    module_version: string
    host_api_version: number
    host_build_id: string
    ready: boolean
  }
  instance_id: string
  auth: { mode: "hosted_pkce"; session_ttl_seconds: number }
  features: {
    catalog_v1: boolean
    independent_threads: boolean
    history_v1: boolean
    chat_ws_v1: boolean
    uploads_v1: boolean
    revocable_sessions: boolean
  }
  limits: {
    question_utf8_bytes: number
    context_utf8_bytes: number
    turn_json_bytes: number
    file_bytes: number
    files_per_turn: number
    files_total_bytes: number
  }
}

export type ClientSession = {
  sid: string
  instance_id: string
  tenant_id: string
  subject: string
  display_name: string
  expires_at: string
  client_id: string
  scopes: string[]
}

export type Expert = {
  expertKey: string
  name: string
  description: string
  avatar: { kind: "emoji" | "asset" | "none"; value: string }
  kind: "expert"
  source: { kind: ExpertSourceKind; label: string }
  availability: ExpertAvailability
  unavailable_reason: string | null
  capabilities: {
    create_thread: boolean
    chat: boolean
    attachments: boolean
    approval_in_client: boolean
    approval_mode: ApprovalMode
  }
}

export type ExpertPage = { items: Expert[]; next_cursor: string | null }

export type RuntimeState = {
  state: "idle" | "running" | "awaiting_approval" | "interrupted"
  turn_id: string | null
  pending_id: string | null
  last_outcome: string | null
}

export type RemoteThread = {
  thread_id: string
  expertKey: string
  channel_type: "page_assist"
  title: string
  created_at: string
  updated_at: string
  runtime: RuntimeState
}

export type ThreadPage = { items: RemoteThread[]; next_cursor: string | null }

export type HistoryPart = {
  kind: "text" | "tool_call" | "tool_result" | "attachment" | "reasoning_summary"
  data: Record<string, unknown>
}

export type HistoryMessage = {
  message_id: string
  order: number
  role: "user" | "assistant" | "tool" | "system"
  parts: HistoryPart[]
  created_at: string
  client_request_id: string | null
}

export type HistoryPage = {
  thread_id: string
  items: HistoryMessage[]
  next_cursor: string | null
  history_revision: string
  runtime: RuntimeState
}

export type AttachmentRef = {
  upload_id: string
  thread_id: string
  expertKey: string
  filename: string
  media_type: string
  bytes: number
  sha256: string
  expires_at: string
  state: "ready" | "attached" | "expired"
}

export type ContextSnapshot = {
  snapshot_id: string
  tab_id: number
  url: string
  title: string
  captured_at: string
  text: string
  utf8_bytes: number
  truncated: boolean
  sha256: string
}

export type ApprovalDecision =
  | { item_id: string; type: "approve" }
  | { item_id: string; type: "reject"; reason: string }
  | { item_id: string; type: "respond"; answers: Record<string, string | boolean> }

export type ApprovalReceipt = { decision_id: string; status: "accepted" }

export type ApprovalInstructions = {
  pending_id: string
  source_label: string
  entry_url: string
  instructions: string
}

export type ApprovalPending = {
  pending_id: string
  items: Array<{
    item_id: string
    kind: "tool" | "question"
    title: string
    detail: string
    allowed_decisions: string[]
    fields: Array<{
      key: string
      label: string
      type: "text" | "boolean" | "select"
      required: boolean
      options: string[]
    }>
  }>
  mode: "in_client" | "external_instructions"
}

export type SubmissionReceipt = {
  request_id: string
  thread_id: string
  turn_id: string
  status: "accepted"
}

export type CancelReceipt = {
  request_id: string
  thread_id: string
  turn_id: string
  status: "requested" | "already_terminal"
}

export type OctopEventType =
  | "submission.accepted"
  | "turn.started"
  | "turn.resumed"
  | "message.delta"
  | "reasoning.summary"
  | "tool.call"
  | "tool.result"
  | "approval.required"
  | "usage"
  | "turn.ended"
  | "thread.status"
  | "error"
  | "pong"
  | "subscribe.ok"

export type OctopEvent = {
  v: 1
  connection_id: string
  seq: number
  type: OctopEventType | string
  thread_id: string | null
  turn_id: string | null
  client_request_id: string | null
  payload: Record<string, unknown>
  optional?: boolean
}

export type ConversationConnection = {
  subscribe(threadId: string): Promise<void>
  sendTurn(input: {
    threadId: string
    clientRequestId: string
    question: string
    context: ContextSnapshot | null
    uploadIds: string[]
  }): Promise<SubmissionReceipt>
  cancelTurn(input: { threadId: string; turnId: string }): Promise<CancelReceipt>
  events: AsyncIterable<OctopEvent>
  close(): void
}

export type OctopApi = {
  getCapabilities(signal?: AbortSignal): Promise<ClientCapabilities>
  login(signal?: AbortSignal): Promise<ClientSession>
  getSession(signal?: AbortSignal): Promise<ClientSession>
  logout(): Promise<{ localCleared: true; serverRevoked: boolean }>
  listExperts(
    input: { q?: string; source?: CatalogSource; cursor?: string },
    signal?: AbortSignal
  ): Promise<ExpertPage>
  listThreads(
    expertKey: string,
    cursor?: string,
    signal?: AbortSignal
  ): Promise<ThreadPage>
  createThread(
    input: { expertKey: string; requestId: string },
    signal?: AbortSignal
  ): Promise<RemoteThread>
  getHistory(
    input: { expertKey: string; threadId: string; cursor?: string },
    signal?: AbortSignal
  ): Promise<HistoryPage>
  uploadAttachment(
    input: {
      expertKey: string
      threadId: string
      requestId: string
      file: File
    },
    signal?: AbortSignal
  ): Promise<AttachmentRef>
  connect(input: { expertKey: string; signal?: AbortSignal }): ConversationConnection
  resolveApproval(
    input: {
      expertKey: string
      threadId: string
      pendingId: string
      decisionId: string
      decisions: ApprovalDecision[]
    },
    signal?: AbortSignal
  ): Promise<ApprovalReceipt>
  getApprovalInstructions(
    input: { expertKey: string; threadId: string; pendingId: string },
    signal?: AbortSignal
  ): Promise<ApprovalInstructions>
}

export type ConversationUiState =
  | "EMPTY"
  | "CREATING"
  | "IDLE"
  | "UPLOADING"
  | "SUBMITTING"
  | "RUNNING"
  | "AWAITING_APPROVAL"
  | "CANCELLING"
  | "UNKNOWN"
  | "RECONCILING"

export type AuthUiState =
  | "DISABLED"
  | "SIGNED_OUT"
  | "AUTHENTICATING"
  | "AUTHENTICATED"
  | "EXPIRED"
