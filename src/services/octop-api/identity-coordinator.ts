import { getAuthBroker } from "./auth-broker"
import { bumpEpoch, loadEnterpriseConfig, saveEnterpriseConfig, type EnterpriseConfig } from "./config"
import { deletePartition } from "@/db/octop"

export type IdentitySnapshot = {
  origin: string
  instanceId: string
  subject: string
  epoch: number
  partition: string
}

type CoordinatorState = {
  snapshot: IdentitySnapshot | NoneSnapshot
  writeChain: Promise<void>
}

type NoneSnapshot = {
  origin: ""
  instanceId: ""
  subject: ""
  epoch: number
  partition: ""
}

const TOKEN_KEY = "octop.client.token"
const SESSION_KEY = "octop.client.session"

const empty = (epoch: number): NoneSnapshot => ({
  origin: "",
  instanceId: "",
  subject: "",
  epoch,
  partition: ""
})

const state: CoordinatorState = {
  snapshot: empty(0),
  writeChain: Promise.resolve()
}

const trustedSender = (sender: { id?: string; url?: string } | undefined): boolean => {
  if (!sender?.id || sender.id !== chrome.runtime.id) {
    return false
  }
  const url = sender.url || ""
  return url.startsWith(`chrome-extension://${chrome.runtime.id}/`) || url.startsWith(`edge-extension://${chrome.runtime.id}/`)
}

const serialize = async (work: () => Promise<void>): Promise<void> => {
  const next = state.writeChain.then(work, work)
  state.writeChain = next.catch(() => undefined)
  await next
}

export const publishIdentity = async (snapshot: IdentitySnapshot): Promise<void> => {
  await serialize(async () => {
    if (snapshot.epoch < state.snapshot.epoch) {
      return
    }
    state.snapshot = snapshot
    await chrome.storage.session?.set?.({ "octop.identity": snapshot })
  })
}

export const clearIdentity = async (reason: string): Promise<{ locked: boolean; code: string }> => {
  let locked = true
  let code = "LOGOUT_UNCONFIRMED"
  await serialize(async () => {
    const epoch = await bumpEpoch()
    const previous = state.snapshot
    state.snapshot = empty(epoch)
    const broker = getAuthBroker()
    try {
      await broker.sessionRemove(TOKEN_KEY)
      await broker.sessionRemove(SESSION_KEY)
    } catch {
      locked = true
      code = "STORAGE_CLEANUP_REQUIRED"
    }
    try {
      if (previous.partition) {
        await deletePartition(previous.partition)
      }
    } catch {
      locked = true
      code = "STORAGE_CLEANUP_REQUIRED"
    }
    if (code !== "STORAGE_CLEANUP_REQUIRED") {
      code = reason
      locked = reason === "LOGOUT_UNCONFIRMED"
    }
  })
  return { locked, code }
}

export const switchHub = async (next: EnterpriseConfig): Promise<void> => {
  await serialize(async () => {
    await clearIdentity("HUB_SWITCH")
    await saveEnterpriseConfig(next)
  })
}

export const currentIdentity = (): IdentitySnapshot | NoneSnapshot => state.snapshot

export const installIdentityCoordinator = (): void => {
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (!trustedSender(sender)) {
      sendResponse({ ok: false, code: "FORBIDDEN" })
      return false
    }
    const type = message?.type
    if (type === "octop.identity.get") {
      sendResponse({ ok: true, snapshot: state.snapshot })
      return false
    }
    if (type === "octop.identity.publish") {
      void publishIdentity(message.snapshot).then(() => sendResponse({ ok: true }))
      return true
    }
    if (type === "octop.identity.clear") {
      void clearIdentity(message.reason || "LOGOUT_UNCONFIRMED").then((result) => sendResponse({ ok: true, ...result }))
      return true
    }
    return false
  })
}
