import { getAuthBroker } from "./auth-broker"
import {
  assertCompatible,
  assertSecureEndpoint,
  bumpEpoch,
  isEnterpriseBrowser,
  loadEnterpriseConfig
} from "./config"
import { OctopApiError } from "./errors"
import { clientFetch, expectJson } from "./http"
import type {
  ApprovalInstructions,
  ApprovalReceipt,
  AttachmentRef,
  ClientCapabilities,
  ClientSession,
  ConversationConnection,
  ExpertPage,
  HistoryPage,
  OctopApi,
  RemoteThread,
  ThreadPage
} from "./types"
import { openConversation } from "./websocket"

const TOKEN_KEY = "octop.client.token"
const SESSION_KEY = "octop.client.session"

const pkceVerifier = (): string => {
  const bytes = crypto.getRandomValues(new Uint8Array(32))
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "")
}

const pkceChallenge = async (verifier: string): Promise<string> => {
  const data = new TextEncoder().encode(verifier)
  const digest = await crypto.subtle.digest("SHA-256", data)
  const bytes = new Uint8Array(digest)
  let binary = ""
  bytes.forEach((b) => {
    binary += String.fromCharCode(b)
  })
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "")
}

const originAndClient = async () => {
  if (!isEnterpriseBrowser()) {
    throw new OctopApiError("CLIENT_MODULE_DISABLED", "enterprise is not available in this browser")
  }
  const config = await loadEnterpriseConfig()
  const origin = assertSecureEndpoint(config, import.meta.env.MODE !== "production")
  return { origin, config }
}

const authHeader = async (): Promise<Record<string, string>> => {
  const token = await getAuthBroker().sessionGet(TOKEN_KEY)
  if (!token) {
    throw new OctopApiError("AUTH_REQUIRED", "not signed in")
  }
  return { Authorization: `Bearer ${token}` }
}

const api: OctopApi = {
  async getCapabilities(signal) {
    const { origin } = await originAndClient()
    const response = await clientFetch(`${origin}/api/client/v1/capabilities`, {
      method: "GET",
      signal
    })
    const caps = await expectJson<ClientCapabilities>(response)
    assertCompatible(caps)
    return caps
  },
  async login(signal) {
    const { origin, config } = await originAndClient()
    await api.getCapabilities(signal)
    const broker = getAuthBroker()
    const redirectUri = broker.getRedirectURL("octop")
    const verifier = pkceVerifier()
    const state = pkceVerifier()
    const challenge = await pkceChallenge(verifier)
    const txRes = await clientFetch(
      `${origin}/api/client/v1/auth/transactions`,
      {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          client_id: config.client_id,
          redirect_uri: redirectUri,
          state,
          code_challenge: challenge,
          method: "S256"
        }),
        signal
      },
      { retries: false }
    )
    const tx = await expectJson<{ authorization_url: string }>(txRes)
    let redirected: string
    try {
      redirected = await broker.launchWebAuthFlow({
        url: tx.authorization_url,
        interactive: true
      })
    } catch {
      throw new OctopApiError("AUTH_CANCELLED", "login cancelled")
    }
    const url = new URL(redirected)
    const returnedState = url.searchParams.get("state")
    const code = url.searchParams.get("code")
    if (returnedState !== state) {
      throw new OctopApiError("AUTH_STATE_MISMATCH", "state mismatch")
    }
    if (!code) {
      throw new OctopApiError("AUTH_CODE_INVALID", "missing code")
    }
    const exRes = await clientFetch(
      `${origin}/api/client/v1/auth/exchange`,
      {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          client_id: config.client_id,
          redirect_uri: redirectUri,
          code,
          code_verifier: verifier
        }),
        signal
      },
      { retries: false }
    )
    const exchanged = await expectJson<{
      access_token: string
      token_type: string
      session: ClientSession
    }>(exRes)
    if (exchanged.token_type !== "Bearer" || exchanged.access_token.startsWith("eyJ")) {
      throw new OctopApiError("AUTH_CODE_INVALID", "token is not a client token")
    }
    await broker.sessionSet(TOKEN_KEY, exchanged.access_token)
    await broker.sessionSet(SESSION_KEY, JSON.stringify(exchanged.session))
    return exchanged.session
  },
  async getSession(signal) {
    const { origin } = await originAndClient()
    const response = await clientFetch(`${origin}/api/client/v1/session`, {
      method: "GET",
      headers: await authHeader(),
      signal
    })
    const session = await expectJson<ClientSession>(response)
    await getAuthBroker().sessionSet(SESSION_KEY, JSON.stringify(session))
    return session
  },
  async logout() {
    const broker = getAuthBroker()
    const token = await broker.sessionGet(TOKEN_KEY)
    let serverRevoked = false
    if (token) {
      try {
        const { origin } = await originAndClient()
        const response = await clientFetch(
          `${origin}/api/client/v1/session`,
          {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` }
          },
          { retries: false }
        )
        serverRevoked = response.status === 204
      } catch {
        serverRevoked = false
      }
    }
    try {
      await broker.sessionRemove(TOKEN_KEY)
      await broker.sessionRemove(SESSION_KEY)
    } catch {
      throw new OctopApiError("STORAGE_CLEANUP_REQUIRED", "local session cleanup failed")
    }
    await bumpEpoch()
    return { localCleared: true as const, serverRevoked }
  },
  async listExperts(input, signal) {
    const { origin } = await originAndClient()
    const params = new URLSearchParams()
    if (input.q) params.set("q", input.q)
    if (input.source) params.set("source", input.source)
    if (input.cursor) params.set("cursor", input.cursor)
    const response = await clientFetch(
      `${origin}/api/client/v1/experts?${params.toString()}`,
      { method: "GET", headers: await authHeader(), signal }
    )
    return expectJson<ExpertPage>(response)
  },
  async listThreads(expertKey, cursor, signal) {
    const { origin } = await originAndClient()
    const qs = cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""
    const response = await clientFetch(
      `${origin}/api/client/v1/experts/${encodeURIComponent(expertKey)}/threads${qs}`,
      { method: "GET", headers: await authHeader(), signal }
    )
    return expectJson<ThreadPage>(response)
  },
  async createThread(input, signal) {
    const { origin } = await originAndClient()
    const response = await clientFetch(
      `${origin}/api/client/v1/experts/${encodeURIComponent(input.expertKey)}/threads`,
      {
        method: "POST",
        headers: {
          ...(await authHeader()),
          "content-type": "application/json",
          "Idempotency-Key": input.requestId
        },
        body: "{}",
        signal
      },
      { retries: false }
    )
    return expectJson<RemoteThread>(response)
  },
  async getHistory(input, signal) {
    const { origin } = await originAndClient()
    const qs = input.cursor ? `?cursor=${encodeURIComponent(input.cursor)}` : ""
    const response = await clientFetch(
      `${origin}/api/client/v1/experts/${encodeURIComponent(input.expertKey)}/threads/${encodeURIComponent(input.threadId)}/history${qs}`,
      { method: "GET", headers: await authHeader(), signal }
    )
    return expectJson<HistoryPage>(response)
  },
  async uploadAttachment(input, signal) {
    const { origin } = await originAndClient()
    const bytes = new Uint8Array(await input.file.arrayBuffer())
    const digest = await crypto.subtle.digest("SHA-256", bytes)
    const sha = [...new Uint8Array(digest)]
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")
    const form = new FormData()
    form.append("file", input.file)
    form.append("sha256", sha)
    const response = await clientFetch(
      `${origin}/api/client/v1/experts/${encodeURIComponent(input.expertKey)}/threads/${encodeURIComponent(input.threadId)}/uploads`,
      {
        method: "POST",
        headers: {
          ...(await authHeader()),
          "Idempotency-Key": input.requestId
        },
        body: form,
        signal
      },
      { retries: false }
    )
    return expectJson<AttachmentRef>(response)
  },
  connect(input): ConversationConnection {
    const controller = input.signal
    let connection: ConversationConnection | null = null
    const starter = (async () => {
      const { origin } = await originAndClient()
      const response = await clientFetch(
        `${origin}/api/client/v1/ws-tickets`,
        {
          method: "POST",
          headers: {
            ...(await authHeader()),
            "content-type": "application/json"
          },
          body: JSON.stringify({ expertKey: input.expertKey }),
          signal: controller
        },
        { retries: false }
      )
      const ticket = await expectJson<{ ws_url: string }>(response)
      connection = openConversation(ticket.ws_url)
      return connection
    })()
    const wrap: ConversationConnection = {
      async subscribe(threadId) {
        const real = connection || (await starter)
        return real.subscribe(threadId)
      },
      async sendTurn(payload) {
        const real = connection || (await starter)
        return real.sendTurn(payload)
      },
      async cancelTurn(payload) {
        const real = connection || (await starter)
        return real.cancelTurn(payload)
      },
      events: {
        async *[Symbol.asyncIterator]() {
          const real = connection || (await starter)
          yield* real.events
        }
      },
      close() {
        connection?.close()
      }
    }
    return wrap
  },
  async resolveApproval(input, signal) {
    const { origin } = await originAndClient()
    const response = await clientFetch(
      `${origin}/api/client/v1/experts/${encodeURIComponent(input.expertKey)}/threads/${encodeURIComponent(input.threadId)}/approvals`,
      {
        method: "POST",
        headers: {
          ...(await authHeader()),
          "content-type": "application/json"
        },
        body: JSON.stringify({
          pending_id: input.pendingId,
          decision_id: input.decisionId,
          decisions: input.decisions
        }),
        signal
      },
      { retries: false }
    )
    return expectJson<ApprovalReceipt>(response)
  },
  async getApprovalInstructions(input, signal) {
    const { origin } = await originAndClient()
    const response = await clientFetch(
      `${origin}/api/client/v1/experts/${encodeURIComponent(input.expertKey)}/threads/${encodeURIComponent(input.threadId)}/approval-instructions?pending_id=${encodeURIComponent(input.pendingId)}`,
      { method: "GET", headers: await authHeader(), signal }
    )
    return expectJson<ApprovalInstructions>(response)
  }
}

export const octopApi = api
export type { OctopApi, ConversationConnection } from "./types"
export { OctopApiError } from "./errors"
export {
  loadEnterpriseConfig,
  saveEnterpriseConfig,
  isEnterpriseBrowser
} from "./config"
export { getAuthBroker, setAuthBroker } from "./auth-broker"
