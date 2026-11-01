import { Button } from "antd"
import { Link, Outlet, useNavigate } from "react-router-dom"
import { useOctopSessionContext } from "@/hooks/octop/OctopSessionContext"

export const EnterpriseShell = () => {
  const { session, logout, authState } = useOctopSessionContext()
  const navigate = useNavigate()
  return (
    <div className="min-h-screen bg-white dark:bg-[#1a1a1a]">
      <div className="h-12 border-b dark:border-gray-700 px-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/" className="text-sm text-gray-500">
            Local chat
          </Link>
          <Link to="/enterprise/experts" className="text-sm font-medium dark:text-white">
            Experts
          </Link>
        </div>
        <div className="flex items-center gap-2 text-sm">
          {session ? <span className="text-gray-500">{session.display_name}</span> : null}
          {authState === "AUTHENTICATED" ? (
            <Button
              size="small"
              onClick={async () => {
                await logout()
                navigate("/enterprise/login")
              }}>
              Sign out
            </Button>
          ) : null}
        </div>
      </div>
      <Outlet />
    </div>
  )
}
