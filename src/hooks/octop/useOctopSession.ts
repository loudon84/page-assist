import { useCallback, useEffect, useState } from "react"
import { deletePartition } from "@/db/octop"
import {
  isEnterpriseBrowser,
  loadEnterpriseConfig,
  octopApi
} from "@/services/octop-api"
import { OctopApiError } from "@/services/octop-api/errors"
import type { AuthUiState, ClientSession } from "@/services/octop-api/types"

export const useOctopSession = () => {
  const [authState, setAuthState] = useState<AuthUiState>("DISABLED")
  const [session, setSession] = useState<ClientSession | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      if (!isEnterpriseBrowser()) {
        setAuthState("DISABLED")
        setSession(null)
        return
      }
      const config = await loadEnterpriseConfig()
      if (!config.enabled) {
        setAuthState("DISABLED")
        setSession(null)
        return
      }
      await octopApi.getCapabilities()
      try {
        const current = await octopApi.getSession()
        setSession(current)
        setAuthState("AUTHENTICATED")
      } catch (err) {
        if (err instanceof OctopApiError && err.code === "SESSION_EXPIRED") {
          setAuthState("EXPIRED")
          setSession(null)
          return
        }
        setAuthState("SIGNED_OUT")
        setSession(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "unavailable")
      setAuthState("SIGNED_OUT")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const login = async () => {
    setAuthState("AUTHENTICATING")
    setError(null)
    try {
      const next = await octopApi.login()
      setSession(next)
      setAuthState("AUTHENTICATED")
    } catch (err) {
      setError(err instanceof Error ? err.message : "login failed")
      setAuthState("SIGNED_OUT")
    }
  }

  const logout = async () => {
    const result = await octopApi.logout()
    if (session) {
      try {
        await deletePartition(session.sid)
      } catch {
        setError("STORAGE_CLEANUP_REQUIRED")
        return result
      }
    }
    setSession(null)
    setAuthState("SIGNED_OUT")
    return result
  }

  return { authState, session, error, loading, login, logout, refresh }
}
