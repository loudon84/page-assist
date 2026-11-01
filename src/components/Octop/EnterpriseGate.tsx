import { ReactNode } from "react"
import { Navigate, useLocation } from "react-router-dom"
import { isEnterpriseBrowser } from "@/services/octop-api"
import { useOctopSessionContext } from "@/hooks/octop/OctopSessionContext"
import { StateBanner } from "./StateBanner"
import { PageAssistLoader } from "@/components/Common/PageAssistLoader"

export const EnterpriseGate = ({ children }: { children: ReactNode }) => {
  const { authState, loading, error } = useOctopSessionContext()
  const location = useLocation()

  if (!isEnterpriseBrowser()) {
    return <Navigate to="/" replace />
  }
  if (loading) {
    return <PageAssistLoader />
  }
  if (authState === "DISABLED") {
    return (
      <div className="p-6">
        <StateBanner marker="unconfigured" message="Enterprise is disabled. Enable it in Settings." />
      </div>
    )
  }
  if (authState === "SIGNED_OUT" || authState === "EXPIRED") {
    if (location.pathname !== "/enterprise/login") {
      return <Navigate to="/enterprise/login" replace />
    }
  }
  if (error && authState !== "AUTHENTICATED") {
    return (
      <div className="p-6">
        <StateBanner marker="error" message={error} />
        {children}
      </div>
    )
  }
  return <>{children}</>
}
