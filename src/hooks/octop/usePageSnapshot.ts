import { useState } from "react"
import { OctopApiError } from "@/services/octop-api/errors"
import type { ContextSnapshot } from "@/services/octop-api/types"

const CODEPOINT_MAX = 20000
const BYTE_MAX = 65536

const sha256Text = async (text: string): Promise<string> => {
  const bytes = new TextEncoder().encode(text)
  const digest = await crypto.subtle.digest("SHA-256", bytes)
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("")
}

const redactUrl = (raw: string): string => {
  const url = new URL(raw)
  url.username = ""
  url.password = ""
  url.search = ""
  url.hash = ""
  return url.toString()
}

const truncate = (text: string): { text: string; truncated: boolean; bytes: number } => {
  let next = text
  let truncated = false
  if ([...next].length > CODEPOINT_MAX) {
    next = [...next].slice(0, CODEPOINT_MAX).join("")
    truncated = true
  }
  let bytes = new TextEncoder().encode(next)
  while (bytes.length > BYTE_MAX) {
    next = [...next].slice(0, [...next].length - 1).join("")
    truncated = true
    bytes = new TextEncoder().encode(next)
  }
  return { text: next, truncated, bytes: bytes.length }
}

export const captureCurrentPage = async (): Promise<ContextSnapshot> => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
  if (!tab?.id || !tab.url) {
    throw new OctopApiError("CONTEXT_CAPTURE_DENIED", "no active tab")
  }
  if (tab.url.startsWith("chrome://") || tab.url.startsWith("file://") || tab.url.startsWith("edge://")) {
    throw new OctopApiError("CONTEXT_CAPTURE_DENIED", "this page cannot be captured")
  }
  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      const hidden = Array.from(document.querySelectorAll("input[type=password], [hidden]"))
      hidden.forEach((el) => el.setAttribute("data-pa-skip", "1"))
      return {
        title: document.title || "",
        text: document.body?.innerText || ""
      }
    }
  })
  const payload = results[0]?.result
  if (!payload) {
    throw new OctopApiError("CONTEXT_CAPTURE_DENIED", "capture returned empty")
  }
  const clipped = truncate(payload.text)
  const url = redactUrl(tab.url)
  const text = clipped.text
  return {
    snapshot_id: crypto.randomUUID(),
    tab_id: tab.id,
    url,
    title: [...payload.title].slice(0, 512).join(""),
    captured_at: new Date().toISOString(),
    text,
    utf8_bytes: clipped.bytes,
    truncated: clipped.truncated,
    sha256: await sha256Text(text)
  }
}

export const usePageSnapshot = () => {
  const [snapshot, setSnapshot] = useState<ContextSnapshot | null>(null)
  const [error, setError] = useState<string | null>(null)
  const add = async () => {
    setError(null)
    try {
      setSnapshot(await captureCurrentPage())
    } catch (err) {
      setError(err instanceof Error ? err.message : "capture failed")
      setSnapshot(null)
    }
  }
  const remove = () => setSnapshot(null)
  return { snapshot, error, add, remove }
}
