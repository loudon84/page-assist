import { createContext, ReactNode, useContext } from "react"
import { useOctopSession } from "./useOctopSession"

type SessionValue = ReturnType<typeof useOctopSession>

const Ctx = createContext<SessionValue | null>(null)

export const OctopSessionProvider = ({ children }: { children: ReactNode }) => {
  const value = useOctopSession()
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export const useOctopSessionContext = () => {
  const value = useContext(Ctx)
  if (!value) {
    throw new Error("OctopSessionProvider missing")
  }
  return value
}
