import { Button } from "antd"
import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useOctopSessionContext } from "@/hooks/octop/OctopSessionContext"
import { StateBanner } from "./StateBanner"

export const LoginPage = () => {
  const { authState, login, error, loading } = useOctopSessionContext()
  const navigate = useNavigate()

  useEffect(() => {
    if (authState === "AUTHENTICATED") {
      navigate("/enterprise/experts", { replace: true })
    }
  }, [authState, navigate])

  return (
    <div className="mx-auto max-w-md p-6 space-y-4">
      <h1 className="text-xl font-semibold dark:text-white">Enterprise login</h1>
      {authState === "EXPIRED" ? (
        <StateBanner marker="expired" message="Your enterprise session expired. Sign in again." />
      ) : (
        <StateBanner marker="signed_out" message="Sign in with your organization account." />
      )}
      {error ? <StateBanner marker="error" message={error} /> : null}
      <Button
        type="primary"
        size="large"
        loading={loading || authState === "AUTHENTICATING"}
        onClick={() => void login()}>
        Continue with Octop
      </Button>
    </div>
  )
}
