import { OctopApiError } from "./errors"
import type { ClientCapabilities } from "./types"

export type EnterpriseConfig = {
  enabled: boolean
  base_url: string
  client_id: string
  source: "managed" | "user" | "disabled"
  allow_insecure_dev: boolean
}

export type ResolvedConfig = EnterpriseConfig & {
  epoch: number
}

const USER_KEY = "octop.enterprise.config"
const EPOCH_KEY = "octop.enterprise.epoch"

const CORE_FEATURES = [
  "catalog_v1",
  "independent_threads",
  "history_v1",
  "chat_ws_v1",
  "uploads_v1",
  "revocable_sessions",
  "runtime_revision_v1"
] as const

const emptyConfig = (): EnterpriseConfig => ({
  enabled: false,
  base_url: "",
  client_id: "",
  source: "disabled",
  allow_insecure_dev: false
})

const readLocal = async <T>(key: string): Promise<T | undefined> => {
  const bag = await chrome.storage.local.get(key)
  return bag[key] as T | undefined
}

const readManaged = async <T>(key: string): Promise<T | undefined> => {
  if (!chrome.storage.managed) {
    return undefined
  }
  try {
    const bag = await chrome.storage.managed.get(key)
    return bag[key] as T | undefined
  } catch {
    return undefined
  }
}

export const loadEnterpriseConfig = async (): Promise<ResolvedConfig> => {
  const managed = await readManaged<Partial<EnterpriseConfig>>("octopEnterprise")
  const user = (await readLocal<EnterpriseConfig>(USER_KEY)) || emptyConfig()
  const epoch = (await readLocal<number>(EPOCH_KEY)) || 0
  if (managed && ("enabled" in managed || "base_url" in managed || "client_id" in managed)) {
    return {
      enabled: Boolean(managed.enabled),
      base_url: String(managed.base_url || ""),
      client_id: String(managed.client_id || ""),
      source: "managed",
      allow_insecure_dev: false,
      epoch
    }
  }
  if (!user.enabled) {
    return { ...emptyConfig(), epoch }
  }
  return { ...user, source: "user", epoch }
}

export const saveEnterpriseConfig = async (
  next: EnterpriseConfig
): Promise<ResolvedConfig> => {
  const current = await loadEnterpriseConfig()
  const same =
    current.base_url === next.base_url &&
    current.client_id === next.client_id &&
    current.enabled === next.enabled
  const epoch = same ? current.epoch : current.epoch + 1
  await chrome.storage.local.set({ [USER_KEY]: next, [EPOCH_KEY]: epoch })
  return loadEnterpriseConfig()
}

export const bumpEpoch = async (): Promise<number> => {
  const current = await loadEnterpriseConfig()
  const epoch = current.epoch + 1
  await chrome.storage.local.set({ [EPOCH_KEY]: epoch })
  return epoch
}

export const canonicalOrigin = (raw: string): string => {
  let parsed: URL
  try {
    parsed = new URL(raw)
  } catch {
    throw new OctopApiError("CONFIG_INVALID", "base_url is not a valid URL")
  }
  if (parsed.username || parsed.password) {
    throw new OctopApiError("CONFIG_INVALID", "base_url must not contain userinfo")
  }
  if (parsed.search || parsed.hash) {
    throw new OctopApiError("CONFIG_INVALID", "base_url must not contain query or fragment")
  }
  if (parsed.pathname && parsed.pathname !== "/") {
    throw new OctopApiError("CONFIG_INVALID", "base_url must be origin form")
  }
  const host = parsed.hostname.toLowerCase()
  const port =
    parsed.port && parsed.port !== "443" && parsed.port !== "80"
      ? `:${parsed.port}`
      : ""
  return `${parsed.protocol}//${host}${port}`
}

export const assertSecureEndpoint = (
  config: EnterpriseConfig,
  isDevBuild: boolean
): string => {
  if (!config.enabled) {
    throw new OctopApiError("CLIENT_MODULE_DISABLED", "enterprise is disabled")
  }
  const origin = canonicalOrigin(config.base_url)
  const parsed = new URL(origin)
  if (parsed.protocol !== "https:") {
    if (!(isDevBuild && config.allow_insecure_dev)) {
      throw new OctopApiError("INSECURE_ENDPOINT", "HTTPS is required")
    }
  }
  if (!config.client_id) {
    throw new OctopApiError("CONFIG_INVALID", "client_id is required")
  }
  return origin
}

export const assertCompatible = (caps: ClientCapabilities): void => {
  if (caps.protocol.major !== 1) {
    throw new OctopApiError("PROTOCOL_INCOMPATIBLE", "protocol major must be 1")
  }
  if ((caps.protocol.minor ?? 0) < 1) {
    throw new OctopApiError("PROTOCOL_INCOMPATIBLE", "protocol minor must be >= 1")
  }
  for (const key of CORE_FEATURES) {
    if (!caps.features[key]) {
      throw new OctopApiError(
        "CAPABILITY_UNAVAILABLE",
        `missing core capability ${key}`
      )
    }
  }
  if (!caps.build.ready) {
    throw new OctopApiError("CLIENT_MODULE_UNAVAILABLE", "module not ready")
  }
}

export const isEnterpriseBrowser = (): boolean => {
  if (import.meta.env.BROWSER === "firefox") {
    return false
  }
  if (chrome?.extension?.inIncognitoContext) {
    return false
  }
  return true
}
